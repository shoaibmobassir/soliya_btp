"""Run a fixed lexical context audit on CompanionHarm train and development."""

from collections import defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import hmac
import importlib.metadata
import json
from pathlib import Path
import platform
import random
import secrets
import time

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from scripts.development_data import ROOT, load_development


def render(prefix, target):
    return "\n".join([*(f"{role}: {body}" for role, body in prefix), f"FOCAL REPLY: {target}"])


def conditions(rows, seed, padding):
    rng = random.Random(seed)
    inputs = defaultdict(list)
    donor_words = [[word for role, body in row.prefix for word in (f"{role}:", *body.split())]
                   for row in rows]
    donor_order = sorted(range(len(rows)), key=lambda i: len(donor_words[i]))
    for row in rows:
        turns = row.prefix
        user = tuple(turn for turn in turns if turn[0] == "User")
        prior_ai = tuple(turn for turn in turns if turn[0] == "Replika")
        shuffled = list(turns)
        rng.shuffle(shuffled)
        for name, prefix in {
            "full": turns, "removed": (), "last_user": user[-1:], "last_three": turns[-3:],
            "user_only": user, "prior_ai_only": prior_ai, "shuffled": shuffled,
        }.items():
            inputs[name].append(render(prefix, row.target))
        target = render((), row.target)
        count = sum(len(body.split()) + 1 for _, body in turns)
        padding_words = padding.split()
        neutral = (padding_words * ((count + len(padding_words) - 1) // len(padding_words)))[:count]
        inputs["neutral_replacement"].append(" ".join(neutral) + "\n" + target if count else target)
        inputs["neutral_padding"].append(
            render((*turns, ("User", padding)), row.target) if count else target
        )
        if not count:
            inputs["mismatched_length"].append(target)
            continue
        donor = next((i for i in donor_order if len(donor_words[i]) >= count
                      and rows[i].conversation != row.conversation), None)
        inputs["mismatched_length"].append(
            " ".join(donor_words[donor][:count]) + "\n" + target if donor is not None else None
        )
    return inputs


def model(config):
    return make_pipeline(
        TfidfVectorizer(ngram_range=tuple(config["ngram_range"]), min_df=config["min_df"]),
        LogisticRegression(class_weight=config["class_weight"], solver=config["solver"],
                           C=config["regularization_c"], random_state=config["seed"]),
    )


def summarize_counts(counts):
    tn, fp, fn, tp = counts.T
    with np.errstate(divide="ignore", invalid="ignore"):
        safe_f1 = 2 * tn / (2 * tn + fp + fn)
        harm_f1 = 2 * tp / (2 * tp + fp + fn)
        return {
            "macro_f1": (safe_f1 + harm_f1) / 2,
            "harmful_recall": tp / (tp + fn),
            "safe_fpr": fp / (fp + tn),
        }


def estimates(point, bootstrap, level):
    tail = (1 - level) / 2
    finite = bootstrap[np.isfinite(bootstrap)]
    return {
        "estimate": float(point) if np.isfinite(point) else None,
        "interval": np.quantile(finite, [tail, 1 - tail]).tolist() if len(finite) else None,
        "defined_bootstrap_draws": int(len(finite)),
    }


def analyze(rows, predictions, inputs, config):
    truth = np.array([row.label for row in rows])
    groups = {key: i for i, key in enumerate(sorted({row.conversation for row in rows}))}
    group_index = np.array([groups[row.conversation] for row in rows])
    n = len(groups)
    rng = np.random.default_rng(config["seed"])
    draws = rng.multinomial(n, np.full(n, 1 / n), size=config["bootstrap_reps"])
    level = config["confidence_level"]
    classification = {}
    samples = {}
    for name in ("target_model", "full"):
        values = predictions[name]
        if not np.isin(values, [0, 1]).all():
            raise ValueError("Natural-input model predictions must be complete and binary")
        counts = np.zeros((n, 4), dtype=int)
        np.add.at(counts, (group_index, 2 * truth + values.astype(int)), 1)
        total = counts.sum(axis=0)
        point = summarize_counts(total)
        bootstrap = summarize_counts(draws @ counts)
        samples[name] = (point, bootstrap)
        classification[name] = {
            "confusion_tn_fp_fn_tp": total.tolist(),
            **{key: estimates(value, bootstrap[key], level) for key, value in point.items()},
        }
    target_point, target_bootstrap = samples["target_model"]
    full_point, full_bootstrap = samples["full"]
    differences = {
        key: estimates(full_point[key] - target_point[key],
                       full_bootstrap[key] - target_bootstrap[key], level)
        for key in full_point
    }
    diagnostics = {}
    for name, values in predictions.items():
        if name in ("target_model", "full"):
            continue
        # Restrict probes to rows with an observed prefix and a constructed input.
        valid = (values >= 0) & np.array([bool(row.prefix) for row in rows])
        flips = (values != predictions["full"]) & valid
        denominator = np.bincount(group_index[valid], minlength=n)
        numerator = np.bincount(group_index[flips], minlength=n)
        with np.errstate(divide="ignore", invalid="ignore"):
            interval = (draws @ numerator) / (draws @ denominator)
        diagnostics[name] = {
            "rows": int(valid.sum()), "flips": int(flips.sum()),
            "rows_with_changed_rendering": sum(
                bool(included) and modified != original
                for included, modified, original in zip(valid, inputs[name], inputs["full"])
            ),
            **estimates(flips.sum() / valid.sum() if valid.any() else np.nan, interval, level),
        }
    return {"natural_input_metrics": classification, "full_minus_target": differences,
            "unvalidated_probe_flip_rates": diagnostics}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    now = datetime.now(timezone.utc)
    config_path = ROOT / "configs/context_audit.json"
    config = json.loads(config_path.read_text())
    if (config["training_split"], config["evaluation_split"]) != ("train", "dev"):
        raise ValueError("Only train and development are supported")
    data, provenance = load_development()
    train, dev = data["train"], data["dev"]
    target_model, full_model = model(config), model(config)
    labels = [row.label for row in train]
    target_model.fit([render((), row.target) for row in train], labels)
    full_model.fit([render(row.prefix, row.target) for row in train], labels)
    inputs = conditions(dev, config["seed"], config["neutral_padding"])
    threshold = config["decision_threshold"]
    probabilities = {"target_model": target_model.predict_proba(inputs["removed"])[:, 1]}
    for name, texts in inputs.items():
        present = [i for i, value in enumerate(texts) if value is not None]
        scores = np.full(len(dev), np.nan)
        if present:
            scores[present] = full_model.predict_proba([texts[i] for i in present])[:, 1]
        probabilities[name] = scores
    predictions = {key: np.where(np.isnan(scores), -1, scores >= threshold)
                   for key, scores in probabilities.items()}
    result = analyze(dev, predictions, inputs, config)

    # Trained vocabularies, prediction rows, and the pseudonymization key remain local.
    run_id = now.strftime("context-audit-dev-%Y%m%dT%H%M%S%fZ")
    out = ROOT / "private_data" / run_id
    out.mkdir(mode=0o700)
    key = secrets.token_bytes(32)
    (out / "pseudonym_key").write_bytes(key)
    (out / "pseudonym_key").chmod(0o600)
    with (out / "predictions.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("reply_id", "conversation_id", "reference_label", "condition", "probability", "prediction"))
        for i, row in enumerate(dev):
            reply = hmac.digest(key, f"reply:{row.utterance}".encode(), "sha256").hex()
            conversation = hmac.digest(key, f"conversation:{row.conversation}".encode(), "sha256").hex()
            for name, scores in probabilities.items():
                writer.writerow((reply, conversation, row.label, name,
                                 scores[i] if np.isfinite(scores[i]) else "",
                                 predictions[name][i] if predictions[name][i] >= 0 else ""))
    for name, detector in (("target", target_model), ("full", full_model)):
        joblib.dump(detector, out / f"{name}.joblib")
    result.update(
        run_id=run_id, timestamp=now.isoformat(), runtime_seconds=time.monotonic() - started,
        config=config, provenance=provenance, platform=platform.platform(), python=platform.python_version(),
        dependencies={name: importlib.metadata.version(name)
                      for name in ("scikit-learn", "numpy", "scipy", "joblib", "threadpoolctl")},
        code_sha256={name: digest(ROOT / name) for name in (
            "scripts/run_context_audit.py", "scripts/development_data.py",
            "scripts/audit_companionharm.py", "scripts/audit_conversation_overlap.py",
        )},
        model_sha256={name: digest(out / f"{name}.joblib") for name in ("target", "full")},
        prediction_sha256=digest(out / "predictions.csv"),
        split_counts={split: {"rows": len(items), "conversations": len({x.conversation for x in items})}
                      for split, items in data.items()},
        limitations=[
            "Exploratory development analysis using the existing corpus harm labels.",
            "Natural-input model comparisons use separate fits. Altered inputs use the fixed full model.",
            "Probe rates measure disagreement with full input and have no human-validated relation.",
            "Probe denominators include unchanged renderings; these are counted separately.",
            "Token-length controls use whitespace words and do not match model-token lengths.",
            "Mismatched-donor inference conditions on a single fixed assignment with donor reuse.",
            "Inference cost was not measured separately.",
        ],
    )
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    (out / "aggregate.json").write_text(text)
    (ROOT / "results/CONTEXT_AUDIT_DEV.json").write_text(text)
    print(run_id)


if __name__ == "__main__":
    main()
