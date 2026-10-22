"""build_vault.py — generate the founder-only vault site (vault/site/public).

Regroups the whole engagement: full path structure, the AI/OS architecture,
decision records, company roster with live URLs, analyst rounds, action kit.
Password-gated at the edge (functions/_middleware.ts); URL is unlisted.
Run: python3 vault/build_vault.py   then deploy with wrangler (see SECRETS.md).
"""
from __future__ import annotations

import html
import json
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
         f"<li><span class='k'>10 companies</span> + holding · 2 active lines, 8 dormant (DR-0013)</li>"
         f"<li><span class='k'>{len(drs)} decision records</span> append-only (DR-0001…)</li>"
         f"<li><span class='k'>155/155</span> OS selftest checks green</li>"
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

    # tree
    (OUT / "tree.html").write_text(page(
        "tree", "<h1>Complete path structure</h1><p>Generated from the repository at build time; "
        "excludes .git / caches / runtime state.</p><pre>" + tree() + "</pre>"),
        encoding="utf-8")

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
        "<li>Dormancy (DR-0013) is enforced in <code>gates.stage()</code>: dormant companies' external/money/public actions are REFUSED at the door.</li>"
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
        "<table><tr><th>company</th><th>mode</th><th>one line</th><th>evidence machine</th></tr>" + rows + "</table>"
        "<h2>Dormancy rules (DR-0013)</h2><ul>" + "".join(f"<li>{r}</li>" for r in dorm["rules"]) + "</ul>"),
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
