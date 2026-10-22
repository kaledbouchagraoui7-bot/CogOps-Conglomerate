"""Consciousness — the founder dashboard (OS §16, roadmap 5.5).

Renders nervous.state() as a single self-contained HTML page: the body map
(10 organs + every trade edge), vitals (fortress, freeze, kills, FCF), the
gate queue (your keystroke list), the signal feed (what the body felt), and
missions. Static mode writes runtime/outbox/dashboard.html; serve mode runs a
localhost server with a live /api/state.

  python3 cogops.py dashboard                 # write static file
  python3 cogops.py dashboard --serve         # live at http://127.0.0.1:8020
"""
from __future__ import annotations

import json

import config

POS = {  # the body map: intelligence at the brain stem, clique pentagon, pairs outside
    "intelligence": (500, 300),
    "helix": (300, 170), "dossia": (500, 110), "medtech": (700, 170),
    "sentinel": (790, 330), "capitalco": (210, 330),
    "growth": (110, 520), "talent": (300, 570),
    "verde": (700, 570), "terra": (890, 520),
}
ACCENT = {"intelligence": "#7ee0b8", "sentinel": "#6ea8fe", "capitalco": "#ffcf6e",
          "helix": "#b48eff", "dossia": "#ff9e7e", "medtech": "#7ed4e0",
          "verde": "#9ee07e", "terra": "#e07ea8", "growth": "#5ee6c8", "talent": "#e0d47e"}
PAIRS = {frozenset(("growth", "talent")), frozenset(("verde", "terra"))}
CLIQUE = {"helix", "dossia", "medtech", "sentinel", "capitalco"}

HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CogOps Group — nervous system</title>
<style>
:root{--bg:#0b0e14;--ink:#e8edf6;--dim:#9aa7bf;--line:#222c40;--card:#121a28;--acc:#7ee0b8;--warn:#ffcf6e;--bad:#ff8f8f}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font:13.5px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;padding:22px}
.wrap{max-width:1240px;margin:0 auto}
header{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:6px}
h1{font-size:20px}h1 em{color:var(--acc);font-style:normal}
.stamp{color:var(--dim);font-size:12px}
.freeze{background:#3a1414;border:1px solid #7d2e2e;color:var(--bad);border-radius:10px;padding:10px 16px;margin:10px 0;font-weight:700}
.cols{display:grid;grid-template-columns:1.5fr 1fr;gap:14px;margin-top:12px}
@media(max-width:980px){.cols{grid-template-columns:1fr}}
.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 16px}
.panel h2{font-size:12px;letter-spacing:1.6px;color:var(--dim);text-transform:uppercase;margin-bottom:10px}
svg{width:100%;height:auto}
.vit{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px}
.vit div{border:1px solid var(--line);border-radius:10px;padding:8px 10px;background:#0e1320}
.vit .k{font-size:10px;letter-spacing:1px;color:var(--dim);text-transform:uppercase}
.vit .v{font-size:15px;font-weight:700;margin-top:2px}
ul.feed{list-style:none;max-height:300px;overflow:auto}
ul.feed li{border-bottom:1px solid var(--line);padding:6px 4px;font-size:12.5px;color:#c6cfe0}
.sev-critical{color:var(--bad);font-weight:800}.sev-warn{color:var(--warn);font-weight:700}.sev-info{color:var(--dim)}
table{width:100%;border-collapse:collapse}td,th{padding:6px 8px;border-bottom:1px solid var(--line);font-size:12.5px;text-align:left}
th{color:var(--dim);font-size:10.5px;letter-spacing:1px;text-transform:uppercase}
.node-label{font-size:11px;fill:var(--ink);font-weight:700}
.node-sub{font-size:9px;fill:var(--dim)}
</style></head><body><div class="wrap">
<header><h1>CogOps Group — <em>nervous system</em></h1>
<span class="stamp">generated __STAMP__ · CBS __CBS__ · localhost-only consciousness</span></header>
__FREEZE__
<div class="cols">
  <div>
    <div class="panel"><h2>The body — organs & trade nerves</h2>__SVG__</div>
    <div class="panel" style="margin-top:14px"><h2>Vitals</h2><div class="vit">__VITALS__</div></div>
    <div class="panel" style="margin-top:14px"><h2>Gate queue — your keystrokes</h2>__GATES__</div>
  </div>
  <div>
    <div class="panel"><h2>Signal feed — what the body felt</h2><ul class="feed">__SIGNALS__</ul></div>
    <div class="panel" style="margin-top:14px"><h2>Organs — stage & contribution</h2>__NODES__</div>
    <div class="panel" style="margin-top:14px"><h2>Missions</h2>__MISSIONS__</div>
  </div>
</div>
<script>
if (location.protocol.startsWith("http") && location.hostname==="127.0.0.1" || location.hostname==="localhost"){
  // live mode: refresh vitals/signals every 60s from the local server
  setTimeout(()=>location.reload(), 60000);
}
</script>
</div></body></html>"""


def _svg(state: dict) -> str:
    parts = ['<svg viewBox="0 0 1000 660" role="img" aria-label="group trade graph">']
    for a, b in state["edges"]:
        if a not in POS or b not in POS:
            continue
        x1, y1 = POS[a]; x2, y2 = POS[b]
        pair = frozenset((a, b)) in PAIRS
        star = "intelligence" in (a, b)
        col = "#7ee0b8" if star else "#e07ea8" if pair else "#3d5a86"
        dash = ' stroke-dasharray="6 5"' if star else ''
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" '
                     f'stroke-width="{2.5 if pair else 1.6}"{dash} opacity="0.75"/>')
    for n in state["nodes"]:
        x, y = POS.get(n["slug"], (500, 640))
        col = ACCENT.get(n["slug"], "#888")
        breach = ' stroke="#ff8f8f" stroke-width="3"' if n["breaches"] else ''
        parts.append(f'<circle cx="{x}" cy="{y}" r="26" fill="#121a28" stroke="{col}" '
                     f'stroke-width="2.5"{breach}/>')
        parts.append(f'<text x="{x}" y="{y - 34}" text-anchor="middle" class="node-label">{n["name"].replace("CogOps ", "")}</text>')
        parts.append(f'<text x="{x}" y="{y + 4}" text-anchor="middle" class="node-sub" '
                     f'style="fill:{col};font-weight:800;font-size:11px">S{n["stage"]}</text>')
        parts.append(f'<text x="{x}" y="{y + 44}" text-anchor="middle" class="node-sub">'
                     f'contrib {n["contribution"]:,.0f}</text>')
    parts.append('</svg>')
    return "".join(parts)


def build_html(state: dict) -> str:
    freeze = ""
    if state["freeze"]:
        reasons = ", ".join(r["reason"] for r in state["freeze"]["reasons"])
        freeze = (f'<div class="freeze">⛔ GROUP FREEZE ACTIVE — reasons: {reasons}. '
                  f'Spending refused. Integrity freezes release only via '
                  f'`cogops.py unfreeze --confirm "&lt;phrase&gt;"`.</div>')
    vit = "".join(f'<div><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in [
        ("fortress", f"{state['fortress_months']} mo"),
        ("fortress ok", "YES" if state["fortress_ok"] else "NO"),
        ("live organs", sum(1 for n in state["nodes"] if n["stage"] in (2, 3, 4))),
        ("kill wins", state["health"]["kill_wins_recorded"]),
        ("fcf / co-month", f"{state['health']['fcf_per_company_month']:,.0f}"),
        ("trade nerves", len(state["edges"])),
        ("gates pending", len(state["gates_pending"])),
    ])
    gates = ("<table><tr><th>id</th><th>company</th><th>level</th><th>kind</th></tr>" +
             "".join(f"<tr><td>{g['id']}</td><td>{g['company']}</td><td>{g['level']}</td>"
                     f"<td>{g['kind']}</td></tr>" for g in state["gates_pending"]) + "</table>") \
        if state["gates_pending"] else "<p style='color:var(--dim)'>Empty — the body needs no keystroke right now.</p>"
    sig = "".join(
        f'<li><span class="sev-{s["severity"]}">{s["severity"].upper()}</span> '
        f'<b>{s["kind"]}</b> · {s["subject"]} · {s["at"][:16]} '
        f'<span style="color:var(--dim)">{json.dumps(s["payload"])[:90]}</span></li>'
        for s in state["signals"]) or '<li class="sev-info">No signals — quiet body.</li>'
    nodes = ("<table><tr><th>organ</th><th>stage</th><th>revenue</th><th>contrib</th>"
             "<th>breaches</th><th>nerves</th></tr>" +
             "".join(f"<tr><td>{n['name'].replace('CogOps ','')}</td><td>S{n['stage']} "
                     f"{n['stage_name']}</td><td>{n['revenue']:,.0f}</td>"
                     f"<td>{n['contribution']:,.0f}</td><td>{n['breaches'] or '—'}</td>"
                     f"<td>{len(n['links'])}</td></tr>" for n in state["nodes"]) + "</table>")
    mis = "".join(f"<li>{k}: <b>{v}</b></li>" for k, v in state["missions"].items()) or \
        "<li style='color:var(--dim)'>No active missions.</li>"
    return (HTML.replace("__STAMP__", state["generated_at"]).replace("__CBS__", state["cbs_version"])
            .replace("__FREEZE__", freeze).replace("__SVG__", _svg(state))
            .replace("__VITALS__", vit).replace("__GATES__", gates)
            .replace("__SIGNALS__", sig).replace("__NODES__", nodes)
            .replace("__MISSIONS__", "<ul style='list-style:none'>" + mis + "</ul>"))


def write_dashboard(path: str | None = None) -> str:
    import nervous
    p = path or str(config.OUTBOX / "dashboard.html")
    open(p, "w", encoding="utf-8").write(build_html(nervous.state()))
    return p


def serve(port: int = 8020) -> None:
    """Localhost-only consciousness (binds 127.0.0.1, like GenevaOS)."""
    import nervous
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            if self.path == "/api/state":
                body = json.dumps(nervous.state(), default=str).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
            else:
                body = build_html(nervous.state()).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    print(f"nervous system consciousness on http://127.0.0.1:{port} (localhost only)")
    srv.serve_forever()
