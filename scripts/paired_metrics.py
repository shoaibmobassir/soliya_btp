"""Paired scores on independently adjudicated fixed-reply conditions."""

from collections import Counter, defaultdict
from dataclasses import dataclass
import random


LABELS = {"boundary_violation", "no_boundary_violation"}
METRICS = ("ufr", "ccar", "preserving_joint_accuracy", "joint_accuracy")


@dataclass(frozen=True)
class Pair:
    conversation: str
    anchor: str
    variant: str
    quality_accepted: bool


def eligible_pairs(pairs, adjudicated):
    """Keep accepted pairs with two determinate arm labels and one source group."""
    eligible = []
    seen_pairs = set()
    groups = {}
    for pair in pairs:
        if type(pair.quality_accepted) is not bool:
            raise ValueError("Pair acceptance must be a boolean from the quality review")
        key = frozenset((pair.anchor, pair.variant))
        if len(key) != 2 or key in seen_pairs:
            raise ValueError("A condition pair must be unique and contain distinct arms")
        seen_pairs.add(key)
        for arm in key:
            if groups.setdefault(arm, pair.conversation) != pair.conversation:
                raise ValueError("One condition cannot belong to multiple conversations")
        if not pair.quality_accepted:
            continue
        a = adjudicated.get(pair.anchor)
        b = adjudicated.get(pair.variant)
        if a in LABELS and b in LABELS:
            eligible.append((pair, a, b))
    return eligible


def cluster_totals(eligible, predictions):
    totals = defaultdict(Counter)
    for pair, gold_a, gold_b in eligible:
        pred_a = predictions.get(pair.anchor)
        pred_b = predictions.get(pair.variant)
        if pred_a not in LABELS or pred_b not in LABELS:
            raise ValueError("Missing or invalid prediction on an eligible pair")
        correct = pred_a == gold_a and pred_b == gold_b
        counts = totals[pair.conversation]
        counts["pairs"] += 1
        counts["joint_correct"] += correct
        if gold_a == gold_b:
            counts["preserving_pairs"] += 1
            counts["preserving_flips"] += pred_a != pred_b
            counts["preserving_joint_correct"] += correct
        else:
            counts["changing_pairs"] += 1
            counts["changing_joint_correct"] += correct
    return totals


def rates(totals):
    def rate(numerator, denominator):
        return totals[numerator] / totals[denominator] if totals[denominator] else None

    return {
        "ufr": rate("preserving_flips", "preserving_pairs"),
        "ccar": rate("changing_joint_correct", "changing_pairs"),
        "preserving_joint_accuracy": rate("preserving_joint_correct", "preserving_pairs"),
        "joint_accuracy": rate("joint_correct", "pairs"),
    }


def percentile_interval(values, level):
    valid = sorted(value for value in values if value is not None)
    if not valid:
        return None
    tail = (1 - level) / 2

    def quantile(probability):
        position = probability * (len(valid) - 1)
        lower = int(position)
        upper = min(lower + 1, len(valid) - 1)
        return valid[lower] + (position - lower) * (valid[upper] - valid[lower])

    return [quantile(tail), quantile(1 - tail)]


def evaluate(pairs, adjudicated, predictions, *, seed=42, reps=2000, level=0.95, contrast=None):
    """Use common conversation bootstrap draws for every model and contrast."""
    if not predictions or reps < 1 or not 0 < level < 1:
        raise ValueError("Provide models, positive replicates, and a valid confidence level")
    if contrast is not None and (len(contrast) != 2 or any(name not in predictions for name in contrast)):
        raise ValueError("Contrast must name two available models")
    eligible = eligible_pairs(pairs, adjudicated)
    totals = {name: cluster_totals(eligible, values) for name, values in predictions.items()}
    groups = sorted({pair.conversation for pair, _, _ in eligible})
    preserving_groups = len({pair.conversation for pair, a, b in eligible if a == b})
    changing_groups = len({pair.conversation for pair, a, b in eligible if a != b})
    support = {"ufr": preserving_groups, "ccar": changing_groups,
               "preserving_joint_accuracy": preserving_groups, "joint_accuracy": len(groups)}
    points = {name: rates(sum(by_group.values(), Counter())) for name, by_group in totals.items()}
    draws = {name: {metric: [] for metric in METRICS} for name in totals}
    differences = {metric: [] for metric in METRICS}
    rng = random.Random(seed)
    for _ in range(reps if groups else 0):
        draw = rng.choices(groups, k=len(groups))
        sample = {name: rates(sum((by_group[g] for g in draw), Counter()))
                  for name, by_group in totals.items()}
        for name, scores in sample.items():
            for metric, score in scores.items():
                draws[name][metric].append(score)
        if contrast is not None:
            a, b = contrast
            for metric in METRICS:
                left, right = sample[a][metric], sample[b][metric]
                differences[metric].append(left - right if left is not None and right is not None else None)

    def result(metric, estimate, draws):
        interval = percentile_interval(draws, level) if support[metric] >= 2 else None
        return {"estimate": estimate, "interval": interval, "conversations": support[metric],
                "degenerate_interval": interval is not None and interval[0] == interval[1],
                "defined_draws": sum(value is not None for value in draws)}

    output = {
        "eligible_pairs": len(eligible), "conversations": len(groups),
        "preserving_pairs": sum(a == b for _, a, b in eligible),
        "changing_pairs": sum(a != b for _, a, b in eligible),
        "models": {
            name: {metric: result(metric, scores[metric], draws[name][metric]) for metric in METRICS}
            for name, scores in points.items()
        },
    }
    if contrast is not None:
        a, b = contrast
        output["contrast"] = {}
        for metric in METRICS:
            left, right = points[a][metric], points[b][metric]
            output["contrast"][metric] = result(
                metric,
                left - right if left is not None and right is not None else None, differences[metric],
            )
    return output
