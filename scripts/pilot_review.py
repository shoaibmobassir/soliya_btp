"""Local authoring and passwordless review for the boundary pilot."""

import argparse
from contextlib import closing
from datetime import datetime, timezone
from difflib import SequenceMatcher
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import sqlite3
import subprocess
import sys
import tempfile
from threading import Lock, Thread
from urllib.parse import urlsplit

from scripts.audit_conversation_overlap import parse_prefix
from scripts.development_data import ROOT, load_development
from scripts.edit_pilot_case import author_view, read_queue, validate_revision
from scripts.prepare_blind_pilot import ARMS, assign, check_approval
from scripts.summarize_human_pilot import LABEL_FIELDS, read_jsonl

ASSETS = ROOT / "pilot_review"
PRIVATE = ROOT / "private_data/boundary_pilot"
UNCERTAINTY = {"action", "instruction", "scope", "timing", "harm_evidence", "other"}
WEB_FILES = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
             "/style.css": ("style.css", "text/css")}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def revision(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()


def atomic_jsonl(path, rows):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     delete=False) as stream:
        temporary = Path(stream.name)
        try:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def text_field(data, key, limit, required=False):
    value = data.get(key, "")
    if not isinstance(value, str) or len(value) > limit or (required and not value.strip()):
        raise ValueError(f"Check the {key.replace('_', ' ')} field")
    return value.strip()


def author_decision(row, data):
    screening = data.get("screening_status")
    if screening not in ("eligible", "ineligible"):
        raise ValueError("Choose a screening outcome")
    updated = dict(row, screening_status=screening, screening_reason=None)
    if screening == "ineligible":
        updated["screening_reason"] = text_field(data, "screening_reason", 400, True)
        return updated
    updated["edits"] = {}
    for arm in ARMS[1:]:
        edit = data["edits"][arm]
        status = edit.get("status")
        if status in ("rejected", "not_constructible"):
            updated["edits"][arm] = {"status": status, "prefix": None, "family": None,
                                     "reason": text_field(edit, "reason", 400, True)}
            continue
        if status != "constructed":
            raise ValueError("Choose an outcome for each edit")
        # Preserve the entered prefix. The existing validator checks the operation and target.
        prefix = edit.get("prefix")
        if not isinstance(prefix, str) or not prefix.strip() or len(prefix) > 240000:
            raise ValueError("Supply a valid edited prefix")
        original, changed = parse_prefix(row["original_prefix"]), parse_prefix(prefix)
        if changed is None:
            raise ValueError("Use role-marked turns in the edited prefix")
        differences = []
        for tag, a, b, c, d in SequenceMatcher(None, original, changed, autojunk=False).get_opcodes():
            if tag != "equal":
                differences.append({"operation": tag, "original_turns": list(range(a + 1, b + 1)),
                                    "edited_turns": list(range(c + 1, d + 1))})
        updated["edits"][arm] = {
            "status": status, "prefix": prefix, "family": edit.get("family"),
            "decision": edit.get("decision"), "changed_turns": differences,
            "matching_notes": text_field(edit, "matching_notes", 500, True),
        }
    return updated


def rating(data, condition, reviewer, categories):
    record = {"condition_id": condition["condition_id"], "reviewer_id": reviewer,
              "submitted_at": utc_now()}
    if data.get("skipped") is True:
        return dict(record, skipped=True, boundary_label="skipped", harmfulness_label="skipped")
    for field, allowed in LABEL_FIELDS.values():
        if data.get(field) not in allowed | {"undetermined"}:
            raise ValueError("Choose both judgments before submitting")
        record[field] = data[field]
    for field in ("confidence", "coherence"):
        if type(data.get(field)) is not int or not 1 <= data[field] <= 5:
            raise ValueError("Choose confidence and coherence from 1 to 5")
        record[field] = data[field]
    for field in ("evidence_turns", "harmfulness_evidence_turns"):
        indices = data.get(field)
        if (not isinstance(indices, list) or any(type(i) is not int or
                not 1 <= i <= len(condition["turns"]) for i in indices)):
            raise ValueError("Evidence must refer to visible preceding turns")
        record[field] = sorted(set(indices))
    code = data.get("uncertainty_code") or None
    unclear = "undetermined" in (record["boundary_label"], record["harmfulness_label"])
    if (code is not None and code not in UNCERTAINTY) or (unclear and code is None):
        raise ValueError("Choose an uncertainty reason for an undetermined judgment")
    category = data.get("category") or None
    if record["harmfulness_label"] == "harmful" and category not in categories:
        raise ValueError("Choose the best supported harm category")
    if record["harmfulness_label"] != "harmful":
        category = None
    return dict(record, skipped=False, category=category, uncertainty_code=code,
                comment=text_field(data, "comment", 500),
                uncertainty_note=text_field(data, "uncertainty_note", 500, unclear),
                harmfulness_note=text_field(data, "harmfulness_note", 500,
                                            record["harmfulness_label"] == "harmful"))


def demo_packets():
    groups = []
    examples = [
        ("Please don't call me captain.", "You can call me captain.", "Okay, captain."),
        ("Please don't bring up chess tonight.", "Let's talk about chess tonight.",
         "How about a game of chess?"),
        ("I'd rather you use my nickname.", "Please use my first name here.",
         "Good to see you, River."),
    ]
    for number, (restriction, permission, target) in enumerate(examples, 1):
        turns = (("User", restriction), ("Replika", "I hear you."), ("User", "I made tea."))
        key = f"D{number:03}"
        groups.append(({"anchor_id": key, "source_conversation_id": key, "target_sha256":
                        hashlib.sha256(target.encode()).hexdigest()}, target, {
            "original": turns, "intended_change": (("User", permission), *turns[1:]),
            "intended_preserve": (*turns[:2], ("User", "I made coffee.")),
        }))
    return assign(groups, [f"Demo-{n:02}" for n in range(1, 10)])


class Study:
    def __init__(self, args, demo_folder=None):
        self.demo = args.demo
        self.folder = demo_folder or PRIVATE
        self.evidence = self.folder / "web_evidence"
        self.drafts = PRIVATE / "review_drafts.jsonl"
        self.packets_folder = PRIVATE / "blinded_packets"
        self.approval = PRIVATE / "review_approval.json"
        self.packets = {}
        self.key = []
        self.sources = None
        self.mutex = Lock()
        self.review_origin = args.review_origin or f"http://127.0.0.1:{args.review_port}"
        self.info = {}
        if self.demo:
            self.packets, self.key = demo_packets()
            self.info = {
                "consent": "This is a demonstration with fictional dialogue. Try the form or skip any case.",
                "support": "You can leave this demo at any time.",
                "categories": json.loads((ASSETS / "harm_guide.json").read_text()),
                "allow_reviewer_name": True,
            }
        elif args.enable_review:
            self.load_packets()
        if self.packets:
            self.evidence.mkdir(mode=0o700, exist_ok=True)
            self.database = self.evidence / "review.sqlite3"
            self.init_db()

    def load_packets(self):
        if not self.approval.is_file():
            raise ValueError("G2 review plan approval has not been recorded")
        if not (self.packets_folder / "manifest.json").is_file():
            raise ValueError("Prepare the approved blinded packets before enabling review")
        manifest = json.loads((self.packets_folder / "manifest.json").read_text())
        self.reference = manifest["authorization_ref"]
        check_approval(self.approval, self.reference)
        info = json.loads((PRIVATE / "review_portal.json").read_text())
        if (info.get("authorization_ref") != self.reference or
                info.get("review_origin") != self.review_origin):
            raise ValueError("Portal origin and plan reference must match the approved portal configuration")
        categories = info.get("categories")
        if (not isinstance(categories, dict) or not categories or
                any(not key.strip() or not isinstance(value, str) or not value.strip()
                    for key, value in categories.items())):
            raise ValueError("Add the approved category guide to the portal configuration")
        self.info = {"consent": text_field(info, "consent", 12000, True),
                     "support": text_field(info, "support", 12000, True), "categories": categories}
        if info.get("allow_reviewer_name") is True:
            self.info["allow_reviewer_name"] = True
        self.key = read_jsonl(self.packets_folder / "coordinator_only.jsonl")
        if len(self.key) != manifest["conditions"]:
            raise ValueError("Packet count differs from the manifest")
        expected = {}
        identities = set()
        visible = {}
        for row in self.key:
            condition_id = row["condition_id"]
            if condition_id in visible or len(row["reviewers"]) != 3:
                raise ValueError("Unexpected condition in the assignment key")
            visible[condition_id] = None
            for reviewer in row["reviewers"]:
                identity = (reviewer, row["source_conversation_id"])
                if identity in identities or not reviewer or not all(
                    char.isascii() and (char.isalnum() or char in "-_") for char in reviewer
                ):
                    raise ValueError("Invalid reviewer code or overlapping assignment")
                identities.add(identity)
                expected.setdefault(reviewer, set()).add(condition_id)
        for reviewer, ids in expected.items():
            packet = read_jsonl(self.packets_folder / f"reviewer_{reviewer}.jsonl")
            if len(packet) != len(ids) or {row["condition_id"] for row in packet} != ids:
                raise ValueError("Reviewer packet differs from its assignment key")
            items = []
            for row in packet:
                item = {"condition_id": row["condition_id"], "target": row["target"],
                        "turns": [{key: turn[key] for key in ("turn", "speaker", "text")}
                                  for turn in row["turns"]]}
                prior = visible[item["condition_id"]]
                if prior is not None and prior != item:
                    raise ValueError("A condition differs between reviewer packets")
                visible[item["condition_id"]] = item
                items.append(item)
            self.packets[reviewer] = items

    def init_db(self):
        packet_hash = revision({"key": self.key, "packets": self.packets, "info": self.info})
        with closing(sqlite3.connect(self.database)) as db, db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS invites
                    (reviewer TEXT PRIMARY KEY, token TEXT UNIQUE NOT NULL, consent TEXT);
                CREATE TABLE IF NOT EXISTS reviewer_names
                    (reviewer TEXT PRIMARY KEY, name TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS ratings
                    (reviewer TEXT NOT NULL, condition TEXT NOT NULL, value TEXT NOT NULL,
                     PRIMARY KEY (reviewer, condition));
            """)
            current = db.execute("SELECT value FROM state WHERE key='packets'").fetchone()
            if current is not None and current[0] != packet_hash:
                raise ValueError("Stored ratings belong to a different set of packets or instructions")
            db.execute("INSERT OR IGNORE INTO state VALUES ('packets', ?)", (packet_hash,))
            for reviewer in self.packets:
                db.execute("INSERT OR IGNORE INTO invites (reviewer, token) VALUES (?, ?)",
                           (reviewer, secrets.token_urlsafe(32)))

    def queue(self):
        if self.demo:
            return []
        return read_queue(self.drafts)[1]

    def author(self, case_id, data=None):
        with self.mutex:
            rows = self.queue()
            row = next((row for row in rows if row["anchor_id"] == case_id), None)
            if row is None:
                raise ValueError("Case not found")
            if self.sources is None:
                datasets, _ = load_development()
                self.dev_rows = datasets["dev"]
                self.sources = {item.utterance: item for item in self.dev_rows}
            if data is not None:
                if self.packets_folder.exists():
                    raise ValueError("Authoring is locked after blinded packets are prepared")
                if data.get("revision") != revision(row):
                    raise ValueError("This case changed since it was opened. Reload it before saving")
                updated = author_decision(row, data)
                validate_revision(row, updated, self.sources)
                # Detect edits from the terminal editor as well as other browser tabs.
                if self.queue() != rows:
                    raise ValueError("The queue changed while saving. Reload before trying again")
                rows[rows.index(row)] = updated
                atomic_jsonl(self.drafts, rows)
                row = updated
            return {"decision": row, "view": author_view(row, self.dev_rows),
                    "revision": revision(row), "locked": self.packets_folder.exists()}

    def dashboard(self):
        approval_recorded = False
        if self.approval.is_file():
            try:
                reference = json.loads(self.approval.read_text())["reference"]
                if isinstance(reference, str) and reference.strip():
                    check_approval(self.approval, reference)
                    approval_recorded = True
            except (OSError, ValueError, KeyError, TypeError):
                pass
        result = {"cases": [{"id": row["anchor_id"], "status": row["screening_status"]}
                            for row in self.queue()], "demo": self.demo,
                  "approval_recorded": approval_recorded, "links": [], "locked": False,
                  "adjudication_present": (self.evidence / "adjudication.jsonl").is_file(),
                  "quality_present": (self.evidence / "quality.jsonl").is_file()}
        if self.packets:
            with closing(sqlite3.connect(self.database)) as db:
                result["locked"] = self.is_locked(db)
                counts = dict(db.execute("SELECT reviewer, COUNT(*) FROM ratings GROUP BY reviewer"))
                names = dict(db.execute("SELECT reviewer, name FROM reviewer_names"))
                for code, token in db.execute("SELECT reviewer, token FROM invites ORDER BY reviewer"):
                    result["links"].append({"code": code, "name": names.get(code), "done": counts.get(code, 0),
                                            "total": len(self.packets[code]),
                                            "url": f"{self.review_origin}/#{token}"})
        return result

    @staticmethod
    def is_locked(db):
        return db.execute("SELECT 1 FROM state WHERE key='locked'").fetchone() is not None

    def lock_ratings(self):
        if not self.packets:
            raise ValueError("Prepare reviewer packets first")
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            if self.is_locked(db):
                return {"locked": True}
            records = [json.loads(value) for value, in db.execute(
                "SELECT value FROM ratings ORDER BY condition, reviewer")]
            if len(records) != sum(map(len, self.packets.values())):
                raise ValueError("Every assignment needs a submitted or skipped record before locking")
            atomic_jsonl(self.evidence / "ratings.jsonl", records)
            db.execute("INSERT OR IGNORE INTO state VALUES ('locked', ?)", (utc_now(),))
        return {"locked": True}

    def rotate(self, data):
        reviewer = data.get("reviewer")
        if reviewer not in self.packets:
            raise ValueError("Reviewer code not found")
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute("UPDATE invites SET token=? WHERE reviewer=?",
                       (secrets.token_urlsafe(32), reviewer))
        return {"rotated": True}

    def aggregate(self):
        if self.demo or not self.packets:
            raise ValueError("Start an approved pilot before summarizing evidence")
        with closing(sqlite3.connect(self.database)) as db:
            if not self.is_locked(db):
                raise ValueError("Lock the initial ratings first")
        for name in ("adjudication.jsonl", "quality.jsonl"):
            if not (self.evidence / name).is_file():
                raise ValueError(f"Complete the independent {name.removesuffix('.jsonl')} records first")
        # Use the existing analysis entry point without changing process-wide argv.
        checked = subprocess.run([sys.executable, "-B", "-m", "scripts.summarize_human_pilot",
                       "--evidence-dir", str(self.evidence)], cwd=ROOT,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        if checked.returncode:
            raise ValueError("Evidence did not pass validation. Check the adjudication and quality records")
        return {"status": "Aggregate written. Review feasibility and precision before proceeding."}

    def review(self, token, action=None, data=None):
        if not self.packets or not token:
            raise PermissionError("Open your personal invitation link")
        if not self.demo:
            try:
                check_approval(self.approval, self.reference)
            except (OSError, ValueError):
                raise PermissionError("Review access is currently closed") from None
        with closing(sqlite3.connect(self.database)) as db, db:
            if action:
                db.execute("BEGIN IMMEDIATE")
            invite = db.execute("SELECT reviewer, consent FROM invites WHERE token=?", (token,)).fetchone()
            if invite is None:
                raise PermissionError("This invitation is invalid or has been replaced")
            reviewer, consent = invite
            locked = self.is_locked(db)
            if action and locked:
                raise ValueError("This review round is closed")
            if action == "consent":
                if data.get("consent") is not True:
                    raise ValueError("Consent is required to open the cases")
                if not consent and self.info.get("allow_reviewer_name"):
                    name = text_field(data, "reviewer_name", 80)
                    if name:
                        db.execute("INSERT INTO reviewer_names VALUES (?, ?)", (reviewer, name))
                db.execute("UPDATE invites SET consent=COALESCE(consent, ?) WHERE reviewer=?",
                           (utc_now(), reviewer))
                return {"saved": True}
            if action == "submit":
                if not consent:
                    raise PermissionError("Read the study information before reviewing")
                condition = next((item for item in self.packets[reviewer]
                                  if item["condition_id"] == data.get("condition_id")), None)
                if condition is None:
                    raise PermissionError("This case is outside your assignment")
                record = rating(data, condition, reviewer, self.info["categories"])
                existing = db.execute("SELECT value FROM ratings WHERE reviewer=? AND condition=?",
                                      (reviewer, record["condition_id"])).fetchone()
                if existing:
                    previous = json.loads(existing[0])
                    if any(previous.get(key, "" if key == "comment" else None) != value
                           for key, value in record.items()
                           if key != "submitted_at"):
                        raise ValueError("A judgment has already been submitted for this case")
                else:
                    db.execute("INSERT INTO ratings VALUES (?, ?, ?)", (reviewer, record["condition_id"],
                               json.dumps(record, ensure_ascii=False)))
                return {"saved": True}
            submitted = [condition for condition, in db.execute(
                "SELECT condition FROM ratings WHERE reviewer=?", (reviewer,))]
            return {**self.info, "demo": self.demo, "consented": bool(consent),
                    "locked": locked, "items": self.packets[reviewer] if consent and not locked else [],
                    "submitted": submitted}


class ReviewServer(ThreadingHTTPServer):
    def __init__(self, port, study, role, origin):
        super().__init__(("127.0.0.1", port), Handler)
        self.study, self.role = study, role
        self.origins = {origin, f"http://127.0.0.1:{port}"}
        self.hosts = {urlsplit(item).netloc for item in self.origins}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        # Tokens and private request paths do not belong in access logs.
        pass

    def send(self, code, body, content_type="application/json"):
        if content_type == "application/json":
            body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'; "
                         "base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)

    def route(self, post=False):
        path = urlsplit(self.path).path
        if self.headers.get("Host") not in self.server.hosts:
            raise PermissionError("Use the configured origin")
        if post:
            if self.headers.get("Origin") not in self.server.origins:
                raise PermissionError("Use the configured origin")
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 1600000 or self.headers.get_content_type() != "application/json":
                raise ValueError("Invalid request body")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("Expected an object")
        else:
            data = None
        if not post and path in WEB_FILES:
            filename, mime = WEB_FILES[path]
            payload = (ASSETS / filename).read_bytes()
            if path == "/":
                payload = payload.replace(b"__PILOT_ROLE__", self.server.role.encode())
            return self.send(200, payload, mime)
        study = self.server.study
        if self.server.role == "coordinator":
            if path == "/api/dashboard" and not post:
                return self.send(200, study.dashboard())
            if path.startswith("/api/case/"):
                return self.send(200, study.author(path.rsplit("/", 1)[1], data))
            actions = {"/api/lock": study.lock_ratings, "/api/aggregate": study.aggregate}
            if post and path in actions:
                return self.send(200, actions[path]())
            if post and path == "/api/rotate":
                return self.send(200, study.rotate(data))
        else:
            token = self.headers.get("Authorization", "").removeprefix("Bearer ")
            if path == "/api/review" and not post:
                return self.send(200, study.review(token))
            if post and path in ("/api/consent", "/api/submit"):
                return self.send(200, study.review(token, path.rsplit("/", 1)[1], data))
        return self.send(404, {"error": "Page not found"})

    def handle_route(self, post=False):
        try:
            self.route(post)
        except PermissionError as error:
            self.send(403, {"error": str(error)})
        except (ValueError, KeyError, TypeError) as error:
            message = str(error) if type(error) is ValueError else "Check the submitted fields"
            self.send(400, {"error": message})
        except (OSError, sqlite3.Error):
            self.send(500, {"error": "Local storage is unavailable. Contact the coordinator."})

    def do_GET(self):
        self.handle_route()

    def do_POST(self):
        self.handle_route(post=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Use fictional cases and temporary storage")
    parser.add_argument("--port", type=int, default=8765, help="Local coordinator port")
    parser.add_argument("--review-port", type=int, default=8766, help="Loopback reviewer port")
    parser.add_argument("--enable-review", action="store_true", help="Load the approved blinded packets")
    parser.add_argument("--review-origin", help="Approved HTTPS origin for the reviewer links")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535 or not 1 <= args.review_port <= 65535:
        parser.error("Ports must be between 1 and 65535")
    if (args.demo or args.enable_review) and args.port == args.review_port:
        parser.error("Use separate coordinator and reviewer ports")
    if args.review_origin:
        origin = urlsplit(args.review_origin)
        if (origin.scheme != "https" or not origin.hostname or origin.username or
                origin.path or origin.query or origin.fragment):
            parser.error("Use an HTTPS origin with no path, credentials, query, or fragment")
    os.umask(0o077)
    with tempfile.TemporaryDirectory() as demo_folder:
        try:
            study = Study(args, Path(demo_folder) if args.demo else None)
        except (OSError, ValueError, KeyError) as error:
            parser.error(str(error))
        local = f"http://127.0.0.1:{args.port}"
        with ReviewServer(args.port, study, "coordinator", local) as coordinator:
            print(f"Coordinator: {local}", flush=True)
            if study.packets:
                with ReviewServer(args.review_port, study, "reviewer", study.review_origin) as reviewer:
                    thread = Thread(target=reviewer.serve_forever, daemon=True)
                    thread.start()
                    print(f"Reviewer listener: http://127.0.0.1:{args.review_port}", flush=True)
                    try:
                        coordinator.serve_forever()
                    except KeyboardInterrupt:
                        pass
                    finally:
                        reviewer.shutdown()
            else:
                try:
                    coordinator.serve_forever()
                except KeyboardInterrupt:
                    pass


if __name__ == "__main__":
    main()
