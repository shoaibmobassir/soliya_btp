"""Build the hosted practice site using an explicit public asset list."""

from pathlib import Path

preview = Path(__file__).resolve().parent
source = preview.parent / "pilot_review"
dist = preview / "dist"
dist.mkdir(exist_ok=True)
html = (source / "index.html").read_text()
html = html.replace("__PILOT_ROLE__", "reviewer")
html = html.replace('<script src="/app.js"', '<script src="/practice.js" defer></script>\n  <script src="/app.js"')
html = html.replace("Pilot Review · Context Evidence", "Conversation Review Practice")
(dist / "index.html").write_text(html)
for name in ("app.js", "style.css", "harm_guide.json"):
    (dist / name).write_bytes((source / name).read_bytes())
for name in ("practice.js", "cases.json"):
    (dist / name).write_bytes((preview / name).read_bytes())
