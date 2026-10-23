"""build_vault.py — generate the founder-only vault site (vault/site/public).

Regroups the whole engagement: full path structure, the AI/OS architecture,
decision records, company roster with live URLs, analyst rounds, action kit.
Password-gated at the edge (functions/_middleware.ts); URL is unlisted.
Run: python3 vault/build_vault.py   then deploy with wrangler (see SECRETS.md).
"""
from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # repo root
OUT = Path(__file__).resolve().parent / "site" / "public"
EXCLUDE = {".git", "__pycache__", "runtime", "node_modules", ".venv"}

CSS = """
:root{--bg:#0a0d12;--ink:#e8edf6;--dim:#93a1b8;--acc:#7ee0b8;--acc2:#6ea8fe;--warn:#ffcf6e;--line:#1e2836;--card:#101722}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 ui-sans-serif,system-ui,Segoe UI,Roboto,sans-serif}
header{border-bottom:1px solid var(--line);padding:18px 28px;display:flex;gap:18px;align-items:baseline;flex-wrap:wrap}
header a{color:var(--dim);text-decoration:none}header a.on,header a:hover{color:var(--acc)}
header .t{color:var(--ink);font-weight:700;letter-spacing:.4px}
main{max-width:1060px;margin:0 auto;padding:28px}
h1{font-size:26px;margin:6px 0 4px}h2{font-size:19px;margin:26px 0 8px;color:var(--acc)}h3{font-size:15.5px;margin:18px 0 6px}
p{color:var(--dim)}li{color:var(--dim);margin:3px 0}.k{color:var(--ink)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:10px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
pre{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;overflow:auto;color:#cfe3d8;font-size:12.5px;line-height:1.5}
.pill{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:2px 10px;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--acc2)}
.pill.d{color:var(--warn);border-color:var(--warn)}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:10px 0}
td,th{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;font-size:13.5px;color:var(--dim)}th{color:var(--ink)}
a{color:var(--acc2)}code{color:var(--acc);background:#0e1520;padding:1px 5px;border-radius:6px}
img{max-width:100%;border:1px solid var(--line);border-radius:14px}
.warn{color:var(--warn)}
"""

NAV = [("index", "Overview"), ("tree", "Path structure"), ("ai", "AI & OS"),
       ("decisions", "Decisions"), ("companies", "Companies"),
       ("analysis", "Analyst"), ("actions", "Action kit")]


def page(title: str, body: str) -> str:
    nav = "".join(f'<a href="{k}.html" class="{"on" if k == title else ""}">{v}</a>'
                  if False else f'<a href="{k}.html">{v}</a>' for k, v in NAV)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex,nofollow">'
            f'<title>Vault · {title}</title><style>{CSS}</style></head><body>'
            f'<header><span class="t">COGOPS VAULT</span>{nav}'
            f'<span style="margin-left:auto" class="pill">founder-only</span></header>'
            f'<main>{body}</main></body></html>')


def md(s: str) -> str:
    out, in_pre = [], False
    for line in html.escape(s).splitlines():
        if line.startswith("```"):
            in_pre = not in_pre
            out.append("<pre>" if in_pre else "</pre>")
            continue
        if in_pre:
            out.append(line)
            continue
        line = re.sub(r"\*\*(.+?)\*\*", r"<b class='k'>\1</b>", line)
        line = re.sub(r"`([^`]+)`", r"<code>\1</code>", line)
        line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', line)
        if line.startswith("### "):
            out.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("> "):
            out.append(f"<p style='border-left:3px solid var(--warn);padding-left:10px'>{line[2:]}</p>")
        elif line.startswith("- "):
            out.append(f"<li>{line[2:]}</li>")
        elif re.match(r"^\d+\. ", line):
            out.append(f"<li>{line}</li>")
        elif line.strip():
            out.append(f"<p>{line}</p>")
    return "".join(out)


def tree() -> str:
    lines = []
    base = ROOT

    def walk(d: Path, prefix: str):
        entries = sorted([p for p in d.iterdir()
                          if p.name not in EXCLUDE and not p.name.endswith(".pyc")],
                         key=lambda p: (p.is_file(), p.name.lower()))
        for i, p in enumerate(entries):
            last = i == len(entries) - 1
            mark = "└── " if last else "├── "
            if p.is_dir():
                lines.append(f"{prefix}{mark}{p.name}/")
                walk(p, prefix + ("    " if last else "│   "))
            else:
                lines.append(f"{prefix}{mark}{p.name}")
    lines.append("CogOps-Conglomerate/")
    walk(base, "")
    return html.escape("\n".join(lines))


# ---------------------------------------------------------------- visual tree
COMPANIES = ["growth", "talent", "helix", "dossia", "medtech", "sentinel",
             "capitalco", "verde", "terra", "intelligence"]


def _accent(slug: str) -> str:
    try:
        m = re.search(r'--acc:\s*(#[0-9a-fA-F]{3,8})',
                      (ROOT / slug / "site" / "public" / "index.html").read_text(encoding="utf-8"))
        return m.group(1) if m else "#7ee0b8"
    except OSError:
        return "#7ee0b8"


ACC = {s: _accent(s) for s in COMPANIES}
ACC["group"] = _accent("group")

CAT = {"cogops-os": "#4ade80", "tools": "#22d3ee", "structure": "#f87171",
       "legal": "#f87171", "holding": "#f87171", "analysis": "#60a5fa",
       "brand": "#fbbf24", "vault": "#fbbf24"}


def tree_data() -> dict:
    """Nested JSON tree with per-node colors (category / company accent)."""
    def color(parts):
        top = parts[0] if parts else ""
        if len(parts) >= 2 and top in ACC and parts[1] == "site":
            return "#a78bfa"
        if top in ACC:
            return ACC[top]
        if top == "cogops-os" and len(parts) >= 3 and parts[1] == "companies":
            return ACC.get(Path(parts[2]).stem, "#4ade80")
        return CAT.get(top, "#94a3b8")

    def walk(d: Path, parts):
        kids = []
        entries = sorted(
            [p for p in d.iterdir()
             if p.name not in EXCLUDE and not p.name.endswith(".pyc")
             and not (p.is_dir() and p.name == "functions"
                      and parts and parts[-1] == "public")],
            key=lambda p: (p.is_file(), p.name.lower()))
        for p in entries:
            pp = parts + [p.name]
            if p.is_dir():
                kids.append({"n": p.name, "d": 1, "c": color(pp), "k": walk(p, pp)})
            else:
                kids.append({"n": p.name, "d": 0, "c": color(pp)})
        return kids

    return {"n": ROOT.name + "/", "d": 1, "c": "#e8edf6", "k": walk(ROOT, [])}


def _count(node):
    if not node.get("d"):
        return 0, 1
    df = ff = 0
    for k in node.get("k", []):
        a, b = _count(k)
        df += a
        ff += b
    return df + 1, ff


GRAPH_HOVER = """<script>
if(!window.__rg){window.__rg=1;
document.addEventListener('mouseover',function(ev){
  var g=ev.target.closest&&ev.target.closest('g.nd');
  document.querySelectorAll('svg line.e').forEach(function(l){l.classList.remove('hi');});
  if(!g)return; var s=g.dataset.s;
  document.querySelectorAll('svg line.e').forEach(function(l){
    if(l.dataset.a===s||l.dataset.b===s)l.classList.add('hi');});
});}
</script>"""


def rel_graph() -> str:
    """SVG relationship graph: holding hub + 10 companies, star/clique/pair edges."""
    order = ["intelligence", "growth", "talent", "helix", "dossia", "medtech",
             "sentinel", "capitalco", "verde", "terra"]
    cx, cy, rx, ry = 450, 330, 330, 225
    pos = {}
    for i, s in enumerate(order):
        a = math.radians(-90 + i * 36)
        pos[s] = (cx + rx * math.cos(a), cy + ry * math.sin(a))
    e = []
    for s in order:
        x, y = pos[s]
        e.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="#26334a" stroke-width="1"/>')
    for s in order:
        if s == "intelligence":
            continue
        x1, y1 = pos["intelligence"]
        x2, y2 = pos[s]
        e.append(f'<line class="e" data-a="intelligence" data-b="{s}" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#7ee0b8" stroke-width="1.5" stroke-dasharray="5 5" opacity=".5"/>')
    k5 = ["helix", "dossia", "medtech", "sentinel", "capitalco"]
    for i in range(len(k5)):
        for j in range(i + 1, len(k5)):
            a, b = k5[i], k5[j]
            x1, y1 = pos[a]
            x2, y2 = pos[b]
            e.append(f'<line class="e" data-a="{a}" data-b="{b}" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#6ea8fe" stroke-width="1.8" opacity=".45"/>')
    for a, b in [("growth", "talent"), ("verde", "terra")]:
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        e.append(f'<line class="e" data-a="{a}" data-b="{b}" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#ffcf6e" stroke-width="2.4" opacity=".7"/>')
    g = []
    for s in order:
        x, y = pos[s]
        r = 30 if s == "intelligence" else 23
        nm = "Capital" if s == "capitalco" else s.title()
        url = f"https://cogops-{'capital' if s == 'capitalco' else s}.pages.dev"
        g.append(f'<a href="{url}" target="_blank" rel="noopener"><g class="nd" data-s="{s}">'
                 f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r + 6}" fill="{ACC[s]}" opacity=".14"/>'
                 f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{ACC[s]}"/>'
                 f'<text x="{x:.0f}" y="{y + 4:.0f}" text-anchor="middle" font-size="10.5" font-weight="800" fill="#0a0d12">{nm[:2].upper()}</text>'
                 f'<text x="{x:.0f}" y="{y + r + 17:.0f}" text-anchor="middle" font-size="11.5" fill="#c6d2e4">{nm}</text></g></a>')
    hub = (f'<g class="nd" data-s="group"><circle cx="{cx}" cy="{cy}" r="42" fill="#101722" stroke="#7ee0b8" stroke-width="2"/>'
           f'<text x="{cx}" y="{cy - 3}" text-anchor="middle" font-size="10.5" font-weight="800" fill="#7ee0b8">HOLDING</text>'
           f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" font-size="9" fill="#93a1b8">CogOps Group</text></g>')
    legend = ('<g font-size="11" fill="#93a1b8">'
              '<line x1="40" y1="628" x2="78" y2="628" stroke="#7ee0b8" stroke-width="1.5" stroke-dasharray="5 5"/>'
              '<text x="86" y="632">star — Intelligence ↔ all (the multiplier)</text>'
              '<line x1="350" y1="628" x2="388" y2="628" stroke="#6ea8fe" stroke-width="1.8"/>'
              '<text x="396" y="632">clique K5 — deep-domain internal market</text>'
              '<line x1="660" y1="628" x2="698" y2="628" stroke="#ffcf6e" stroke-width="2.4"/>'
              '<text x="706" y="632">pairs — shared pipelines</text></g>')
    return ('<style>svg line.e{transition:opacity .15s,stroke-width .15s}svg line.e.hi{opacity:1!important;stroke-width:3.2}'
            'svg g.nd{cursor:pointer}svg g.nd:hover circle{filter:brightness(1.2)}</style>'
            '<svg viewBox="0 0 900 655" style="width:100%;height:auto;background:#0b1017;border:1px solid var(--line);border-radius:14px" '
            'role="img" aria-label="CogOps relationship graph: holding hub, ten companies, star/clique/pair links">'
            + "".join(e) + hub + "".join(g) + legend + '</svg>' + GRAPH_HOVER)


TREE_CSS = """
.vt,.vkids{list-style:none;margin:0;padding:0}
.vkids{margin-left:20px;border-left:1px dashed var(--line);padding-left:10px}
.vrow{display:flex;align-items:center;gap:8px;padding:3px 8px;border-radius:8px;cursor:pointer;color:var(--dim);font:13px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace}
.vrow:hover,.vrow:focus{background:#111a26;color:var(--ink);outline:none}
.vcar{width:12px;flex:none;color:var(--acc);font-size:11px}
.vdot{width:8px;height:8px;border-radius:50%;flex:none}
.vdir{color:var(--ink);font-weight:600}
.vic{margin-left:auto;opacity:.45}
.vcnt{margin-left:auto;font-size:11px;opacity:.5}
li.hit>.vrow .vname{background:rgba(255,207,110,.16);color:var(--warn);border-radius:4px}
.vctl{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}
.vctl input{flex:1;min-width:220px;background:var(--card);border:1px solid var(--line);color:var(--ink);border-radius:10px;padding:9px 13px;font:inherit}
.vctl input:focus{border-color:var(--acc)}
.vctl button{background:var(--card);border:1px solid var(--line);color:var(--dim);border-radius:10px;padding:9px 15px;cursor:pointer;font:inherit}
.vctl button:hover{color:var(--acc);border-color:var(--acc)}
.vchips{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
.vchip{border:1px solid var(--line);border-radius:99px;padding:3px 12px;font-size:12px;color:var(--dim)}
.vchip b{color:var(--ink)}
.vleg{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--dim);margin:4px 0 12px}
.vleg span{display:inline-flex;align-items:center;gap:6px}
.vleg i{width:10px;height:10px;border-radius:3px;display:inline-block}
#vtree{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 10px;max-height:70vh;overflow:auto}
details.raw summary{cursor:pointer;color:var(--acc2);margin:18px 0 8px}
"""

TREE_JS = """
(function(){
var DATA = __DATA__;
var host = document.getElementById('vtree');
var OPEN_DEPTH = 1;
var FIC = {py:'\\u25C6',md:'\\u25A4',html:'\\u25C8',js:'\\u2B22',json:'\\u2B21',toml:'\\u2B2C',ts:'\\u2B22',css:'\\u25C8',svg:'\\u25C8',png:'\\u25A3',txt:'\\u25A4'};
function icon(n){ if(n.d) return ''; var x=n.n.split('.').pop(); return FIC[x]||'\\u00B7'; }
function cnt(n){ var d=0,f=0;(n.k||[]).forEach(function(k){ if(k.d){var r=cnt(k);d+=r[0];f+=r[1];} else f++; }); return [d,f]; }
function render(node, depth, ul){
  var li=document.createElement('li'); li.className='vn'; li.dataset.name=node.n.toLowerCase();
  var row=document.createElement('div'); row.className='vrow'; row.tabIndex=0;
  var car=document.createElement('span'); car.className='vcar'; car.textContent=node.d?(depth<OPEN_DEPTH?'\\u25BE':'\\u25B8'):' ';
  var dot=document.createElement('span'); dot.className='vdot'; dot.style.background=node.c;
  var nm=document.createElement('span'); nm.className='vname'+(node.d?' vdir':''); nm.textContent=node.n;
  row.appendChild(car); row.appendChild(dot); row.appendChild(nm);
  if(node.d){ var c=cnt(node); var b=document.createElement('span'); b.className='vcnt'; b.textContent=c[0]+'d \\u00B7 '+c[1]+'f'; row.appendChild(b); }
  else { var ic=document.createElement('span'); ic.className='vic'; ic.textContent=icon(node); row.appendChild(ic); }
  li.appendChild(row);
  if(node.d){
    var kids=document.createElement('ul'); kids.className='vkids';
    (node.k||[]).forEach(function(k){ render(k, depth+1, kids); });
    if(depth>=OPEN_DEPTH) kids.style.display='none';
    li.appendChild(kids);
    var toggle=function(){ var open=kids.style.display!=='none'; kids.style.display=open?'none':'block'; car.textContent=open?'\\u25B8':'\\u25BE'; };
    row.addEventListener('click',toggle);
    row.addEventListener('keydown',function(ev){ if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();toggle();} });
  }
  ul.appendChild(li);
}
function draw(){ host.innerHTML=''; var ul=document.createElement('ul'); ul.className='vt'; render(DATA,0,ul); host.appendChild(ul); }
draw();
document.getElementById('vexp').addEventListener('click',function(){ host.querySelectorAll('.vkids').forEach(function(u){u.style.display='block';}); host.querySelectorAll('li.vn .vcar').forEach(function(c){ if(c.textContent!==' ') c.textContent='\\u25BE'; }); });
document.getElementById('vcol').addEventListener('click',function(){ OPEN_DEPTH=0; draw(); OPEN_DEPTH=1; });
var q=document.getElementById('vq');
q.addEventListener('input',function(){
  var v=q.value.trim().toLowerCase();
  if(!v){ draw(); return; }
  host.querySelectorAll('li.vn').forEach(function(li){ li.classList.remove('hit'); li.style.display=''; });
  host.querySelectorAll('li.vn').forEach(function(li){
    if(li.dataset.name.indexOf(v)>=0){
      li.classList.add('hit');
      var p=li.parentElement;
      while(p&&p!==host){ if(p.tagName==='UL'&&p.classList.contains('vkids')){ p.style.display='block'; var lp=p.parentElement; if(lp){var c=lp.querySelector('.vcar'); if(c&&c.textContent!==' ')c.textContent='\\u25BE';} } p=p.parentElement; }
    }
  });
  host.querySelectorAll('li.vn').forEach(function(li){ if(!li.classList.contains('hit')&&!li.querySelector('li.hit')) li.style.display='none'; });
});
})();
"""


def tree_page_body() -> str:
    data = tree_data()
    d, f = _count(data)
    d -= 1  # root itself
    chips = (f"<div class='vchips'><span class='vchip'><b>{d}</b> folders</span>"
             f"<span class='vchip'><b>{f}</b> files</span>"
             f"<span class='vchip'><b>10</b> companies + holding</span>"
             f"<span class='vchip'><b>12</b> live deployments</span>"
             f"<span class='vchip'>built {data and __import__('datetime').date.today().isoformat()}</span></div>")
    legend = ("<div class='vleg'>"
              + "".join(f"<span><i style='background:{c}'></i>{n}</span>" for n, c in [
                  ("OS engine", CAT["cogops-os"]), ("tools", CAT["tools"]),
                  ("sites & functions", "#a78bfa"), ("governance / legal", CAT["structure"]),
                  ("research", CAT["analysis"]), ("brand & vault", CAT["brand"]),
                  ("root files", "#94a3b8")])
              + "<span><i style='background:linear-gradient(90deg,#7ee0b8,#b48eff,#6ea8fe,#ff9e7e)'></i>companies carry their own accent</span></div>")
    js = TREE_JS.replace("__DATA__", json.dumps(data, separators=(",", ":")))
    return ("<style>" + TREE_CSS + "</style>"
            "<h1>Structure — a map, not a listing</h1>"
            "<p>Click any folder to open it; search filters live; companies glow in their own accent. "
            "Generated from the repository at build time (excludes .git / caches / runtime state / deploy copies).</p>"
            + chips + legend
            + "<div class='vctl'><input id='vq' type='search' placeholder='Filter paths… (e.g. gates, DR, count.js)' aria-label='filter tree'>"
              "<button id='vexp' type='button'>Expand all</button><button id='vcol' type='button'>Collapse all</button></div>"
            + "<div id='vtree' aria-label='repository tree'></div>"
            + "<h2>Relationship graph</h2>"
            + "<p>The same structure as a network: hover a node to light its links; click to open the live site.</p>"
            + rel_graph()
            + "<details class='raw'><summary>raw listing (for copying exact paths)</summary><pre>" + tree() + "</pre></details>"
            + "<script>" + js + "</script>")


def modules() -> list:
    rows = []
    for f in sorted((ROOT / "cogops-os").glob("*.py")):
        txt = f.read_text(encoding="utf-8")
        m = re.search(r'"""(.+?)[\n"]', txt)
        doc = m.group(1).strip().splitlines()[0] if m else ""
        rows.append((f.name, doc))
    return rows


INVARIANTS = [
    ("I1", "AI-run, human-gated: nothing external/financial executes without the founder's keystroke"),
    ("I2", "Software, data and services only"),
    ("I3", "One gate nexus; fail-closed; append-only audit trail"),
    ("I4", "One spine, many skins (site factory)"),
    ("I5", "Evidence over claims (as-of dates, sources, version hashes, labeled AI modes)"),
    ("I6", "Profit sweeps to one capital engine; no leverage, no derivatives"),
    ("I7", "Internal trades at published prices land on both P&Ls"),
    ("I8", "Kill-as-WIN: failed validations are recorded wins, never sunk costs"),
    ("I9", "Deep tech is a market, not a method"),
    ("I10", "Token caps per company; free-tier-first LLM chain"),
    ("I11", "Honesty labels on every AI output (kb/llm/template/heuristic-v0)"),
    ("I12", "Human of record on every regulated/scientific deliverable"),
]

LIVE = [
    ("growth", "CogOps Growth", "https://cogops-growth.pages.dev", "Revenue engine: lead-gen, pSEO, media network"),
    ("dossia", "CogOps Dossia", "https://cogops-dossia.pages.dev", "Regulatory affairs & medical writing (co-signer conditional)"),
    ("intelligence", "CogOps Intelligence", "https://cogops-intelligence.pages.dev", "The multiplier: AI operations"),
    ("sentinel", "CogOps Sentinel", "https://cogops-sentinel.pages.dev", "Cybersecurity & AI security"),
    ("capitalco", "CogOps Capital", "https://cogops-capital.pages.dev", "Quant finance tools & research"),
    ("helix", "CogOps Helix", "https://cogops-helix.pages.dev", "Computational biology dry-lab"),
    ("medtech", "CogOps Medtech", "https://cogops-medtech.pages.dev", "MedTech R&D enablement"),
    ("verde", "CogOps Verde", "https://cogops-verde.pages.dev", "CleanTech software"),
    ("terra", "CogOps Terra", "https://cogops-terra.pages.dev", "Climate data & ESG analytics"),
    ("talent", "CogOps Talent", "https://cogops-talent.pages.dev", "Workforce: academy & placement"),
    ("group", "CogOps Group (holding)", "https://cogops-group.pages.dev", "Central business, public governance"),
]


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dorm = json.loads((ROOT / "cogops-os" / "data" / "dormancy.json").read_text())
    dec_txt = (ROOT / "structure" / "decisions.md").read_text(encoding="utf-8")
    drs = re.findall(r"(## DR-\d+.*?)(?=\n## DR-|\Z)", dec_txt, re.S)

    # index
    b = [f"<h1>The whole path, in one locked room</h1>"
         f"<p>Founder-only regroup of everything built since 2026-10: the conglomerate "
         f"blueprint, the executable OS, the live evidence machines, the decision trail, "
         f"the analyst rounds and the action kit. Gate: password at the edge; this URL is unlisted.</p>"
         f"<div class='grid'>"
         f"<div class='card'><h3>Group map</h3><img src='assets/map.png' alt='CogOps group map'></div>"
         f"<div class='card'><h3>State, as of 2026-10-22</h3><ul>"
         f"<li><span class='k'>10 companies</span> + holding · all active (DR-0015)</li>"
         f"<li><span class='k'>{len(drs)} decision records</span> append-only (DR-0001…)</li>"
         f"<li><span class='k'>156/156</span> OS selftest checks green</li>"
         f"<li><span class='k'>11 live sites</span> + this vault</li>"
         f"<li><span class='k'>0</span> unrelated-party revenue — the invoice wall ends 2027-06-16 (DR-0014)</li>"
         f"</ul></div>"
         f"<div class='card'><h3>The two dates that govern everything</h3><ul>"
         f"<li><span class='k'>2027-06-16</span> — majority: first lawful invoice (micro-entreprise day-1 kit ready)</li>"
         f"<li><span class='k'>2027-09</span> — relocation to CH; reservations expire 2027-09-30</li></ul></div>"
         f"</div>"
         f"<h2>Live machines</h2><div class='grid'>"
         + "".join(f"<div class='card'><h3>{n} "
                   f"<span class='pill{' d' if s in dorm['dormant'] else ''}'>"
                   f"{'dormant' if s in dorm['dormant'] else 'active'}</span></h3>"
                   f"<p>{d}</p><p><a href='{u}'>{u.replace('https://','')} →</a></p></div>"
                   for s, n, u, d in LIVE)
         + "</div>"]
    (OUT / "index.html").write_text(page("index", "".join(b)), encoding="utf-8")

    # tree — interactive visual (DR-0016): color-coded collapsible tree + relationship graph
    (OUT / "tree.html").write_text(page("tree", tree_page_body()), encoding="utf-8")

    # ai
    mods = "".join(f"<tr><td><code>{f}</code></td><td>{html.escape(d)}</td></tr>"
                   for f, d in modules())
    inv = "".join(f"<tr><td>{i}</td><td>{html.escape(n)}</td></tr>" for i, n in INVARIANTS)
    (OUT / "ai.html").write_text(page(
        "ai", "<h1>The AI & the OS</h1>"
        "<p>Pure-stdlib Python OS (<code>cogops-os/</code>). No employee anywhere: agents produce, "
        "the gate stages, the founder approves. LLM use is capped per company, KB-first, and every "
        "output carries an honesty label (<code>kb / llm / template / heuristic-v0</code>) — the system "
        "never pretends to be smarter than the mode it ran in.</p>"
        "<h2>Modules</h2><table><tr><th>file</th><th>responsibility (docstring)</th></tr>" + mods + "</table>"
        "<h2>Executable invariants I1–I12</h2><table><tr><th>#</th><th>invariant (proved in code, published on group site)</th></tr>" + inv + "</table>"
        "<h2>Doctrine</h2><ul>"
        "<li>Gates Type-1/2/3, levels G1–G3; consume-on-approve; fail-closed; append-only ledger (hash-chained).</li>"
        "<li>Nervous system: senses → reflexes → pain (freeze) → dependency nerves → consciousness dashboard (localhost-only).</li>"
        "<li>Capital: profit sweep → ladder → fortress; Swiss private-investor guardrails; no leverage, no derivatives.</li>"
        "<li>Dormancy instrument (DR-0013) stays enforced in <code>gates.stage()</code>: if a future DR re-dorms a company, its external/money/public actions are REFUSED at the door. Per DR-0015 all ten lines are currently active.</li>"
        "<li>Inbox has no send(): every external message waits for a human keystroke.</li></ul>"),
        encoding="utf-8")

    # decisions
    dbody = "".join(f"<div class='card'>{md(d)}</div>" for d in drs)
    (OUT / "decisions.html").write_text(page(
        "decisions", "<h1>Decision Records (append-only)</h1>"
        "<p>Never edited, only appended. A kill is a win (I8); a structural change without a DR is a defect.</p>"
        + dbody), encoding="utf-8")

    # companies
    rows = "".join(
        f"<tr><td>{n}</td><td>{'dormant' if s in dorm['dormant'] else 'active'}</td>"
        f"<td>{d}</td><td><a href='{u}'>site</a></td></tr>" for s, n, u, d in LIVE)
    (OUT / "companies.html").write_text(page(
        "companies", "<h1>Companies & clusters</h1>"
        "<p>Three clusters: deep-domain services (Helix, Dossia, Medtech, Sentinel, Capital, Terra, Verde), "
        "the multiplier (Intelligence), group engines (Growth, Talent). Pairs: Growth↔Talent, Verde↔Terra. "
        "Clique K5: Helix·Dossia·Medtech·Sentinel·Capital. Star: Intelligence↔all nine. "
        "Excluded forever-for-now: quantum, semis, nuclear, defense-tech, synbio, cell&gene, battery materials.</p>"
        "<h2>Relationship graph</h2><p>Hover a node to light its links; click to open the live site.</p>"
        + rel_graph() +
        "<h2>Roster</h2>"
        "<table><tr><th>company</th><th>mode</th><th>one line</th><th>evidence machine</th></tr>" + rows + "</table>"
        "<h2>Dormancy instrument (DR-0013 → DR-0015)</h2><p>All ten active since DR-0015; the refusal "
        "mechanism stays in <code>gates.stage()</code> and stays tested, so re-dorming any line remains "
        "one JSON edit away.</p><ul>" + "".join(f"<li>{r}</li>" for r in dorm["rules"]) + "</ul>"),
        encoding="utf-8")

    # analysis
    r3 = (ROOT / "analysis" / "round3.md").read_text(encoding="utf-8")
    (OUT / "analysis.html").write_text(page(
        "analysis", "<h1>Skeptical analyst — round 3 (full text)</h1>"
        "<p>Rounds 1–2 live in chat history; round 3 supersedes where contradicted. "
        "Labels: [FACT] verified vs cited sources · [FACT doc n] founder documents · "
        "[ASSUMPTION] reasoned, unverified · [OPINION] judgment · [UNVERIFIED] needs a human act.</p>"
        "<h2>Scores (round 2 → round 3)</h2><table><tr><th>dimension</th><th>R2</th><th>R3</th></tr>"
        + "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in [
            ("Coherence & plausibility", 5, 6), ("Offer", 6, 6), ("Market", 4, 4),
            ("GTM", 5, 6), ("Unit economics", 5, 5), ("Delivery", 7, 7),
            ("Legal & capacity", 3, 4), ("Focus", 4, 7), ("Moat", 3, 3),
            ("Founder bandwidth", 3, 3)])
        + "</table><p>Probability bands: CHF 3k in a single month by month 10: <span class='warn'>30–40%</span>; "
        "run-rate at month 10: 15–25%; by month 18–24: 50–60%; orderly downside: high.</p>"
        + md(r3)), encoding="utf-8")

    # actions
    fa = (ROOT / "analysis" / "founder-actions.md").read_text(encoding="utf-8")
    (OUT / "actions.html").write_text(page(
        "actions", "<h1>Founder action kit</h1><p>The six human acts the machine cannot perform, in order.</p>"
        + md(fa)), encoding="utf-8")

    # login
    (OUT / "login.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="robots" content="noindex,nofollow"><title>Vault · gate</title>'
        f'<style>{CSS}</style></head><body><main style="max-width:420px;margin:12vh auto">'
        '<div class="card"><h1 style="font-size:20px">CogOps Vault</h1>'
        '<p>Founder-only. Enter the vault password.</p>'
        '<form id="f"><input type="password" id="p" placeholder="password" autocomplete="current-password" '
        'style="width:100%;background:var(--card);border:1px solid var(--line);color:var(--ink);'
        'border-radius:10px;padding:12px 14px;font:inherit">'
        '<button style="margin-top:10px;width:100%;background:var(--acc);color:#06110b;border:0;'
        'border-radius:10px;padding:12px;font:inherit;font-weight:700;cursor:pointer">open</button>'
        '<p id="e" class="warn"></p></form></div><script>'
        'document.getElementById("f").addEventListener("submit",async(ev)=>{ev.preventDefault();'
        'const r=await fetch("/api/login",{method:"POST",body:new URLSearchParams({password:document.getElementById("p").value})});'
        'if(r.ok){location.href="/";}else{document.getElementById("e").textContent="denied";}});'
        '</script></main></body></html>', encoding="utf-8")
    print("vault pages written:", sorted(p.name for p in OUT.glob("*.html")))


if __name__ == "__main__":
    build()
