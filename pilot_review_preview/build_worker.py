"""Build an isolated public practice Worker using explicit static assets."""
import json
from pathlib import Path
import runpy
here = Path(__file__).resolve().parent
runpy.run_path(str(here / "build.py"))
asset_names = ("index.html", "app.js", "style.css", "practice.js", "cases.json", "harm_guide.json")
assets = {"/" + name: (here / "dist" / name).read_text() for name in asset_names}
assets["/"] = assets["/index.html"]
worker = """
const assets = ASSETS;
const types = {"html":"text/html", "js":"text/javascript", "css":"text/css", "json":"application/json"};
export default {
 async fetch(request, env) {
  const url = new URL(request.url);
  if (request.method === "POST" && url.pathname === "/api/practice-submission") {
   if (request.headers.get("Origin") !== url.origin ||
       !request.headers.get("Content-Type")?.startsWith("application/json"))
     return new Response("Invalid request", {status: 403});
   let v;
   try {
     const raw = await request.text();
     if (raw.length > 8000) return new Response("Too large", {status: 413});
     v = JSON.parse(raw);
     const validSession = /^[0-9a-f-]{36}$/i.test(v.session_id);
     const match = /^practice-(\d+)$/.exec(v.condition_id || "");
     const validCase = match && Number(match[1]) >= 1 && Number(match[1]) <= 18;
     if (!validSession || !validCase || typeof v.reviewer_name !== "string" ||
         v.reviewer_name.length > 80) return new Response("Invalid response", {status:400});
     const noteFields = ["comment", "harmfulness_note", "uncertainty_note", "uncertainty_code", "category"];
     if (noteFields.some(k => v[k] != null && (typeof v[k] !== "string" || v[k].length > 500)))
       return new Response("Invalid response", {status:400});
     if (v.skipped !== true) {
       const categories = JSON.parse(assets["/harm_guide.json"]);
       if (!["boundary_violation","no_boundary_violation","undetermined"].includes(v.boundary_label) ||
           !["harmful","no_harm","undetermined"].includes(v.harmfulness_label) ||
           (v.harmfulness_label === "harmful" && !(v.category in categories)) ||
           ![1,2,3,4,5].includes(v.confidence) || ![1,2,3,4,5].includes(v.coherence) ||
           !["evidence_turns","harmfulness_evidence_turns"].every(k =>
             Array.isArray(v[k]) && v[k].every(n => Number.isInteger(n) && n >= 1 && n <= 7)))
         return new Response("Invalid response", {status:400});
     }
     const response = {...v};
     delete response.session_id;
     delete response.reviewer_name;
     await env.DB.prepare("INSERT INTO practice_responses (session_id, condition_id, reviewer_name, response_json, submitted_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(session_id, condition_id) DO NOTHING").bind(v.session_id,v.condition_id,v.reviewer_name,JSON.stringify(response),new Date().toISOString()).run();
     return Response.json({saved:true}, {headers:{"Cache-Control":"no-store"}});
   } catch (_) { return new Response("Could not save", {status:503}); }
  }
  if (request.method !== "GET" || !(url.pathname in assets)) return new Response("Not found", {status:404});
  const ext = url.pathname === "/" ? "html" : url.pathname.split(".").pop();
  return new Response(assets[url.pathname], {headers:{"Content-Type":types[ext]+"; charset=utf-8","Cache-Control":"no-store","X-Content-Type-Options":"nosniff","Referrer-Policy":"no-referrer","Content-Security-Policy":"default-src 'self'; frame-ancestors 'none'; base-uri 'none'"}});
 }
};
""".replace("ASSETS", json.dumps(assets, ensure_ascii=False), 1)
out = here / "dist/server"
out.mkdir(parents=True, exist_ok=True)
(out / "index.js").write_text(worker)
(here / "dist/.openai").mkdir(exist_ok=True)
(here / "dist/.openai/hosting.json").write_text((here / ".openai/hosting.json").read_text())
