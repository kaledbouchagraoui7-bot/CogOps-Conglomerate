"""The group website builder — the holding's skin (DR-0012).

Assembles group/site/public/{index,governance}.html from LIVE state:
the trade graph (nervous.system), the ten organs, the six principles, the
executable invariants (I1–I12, as-of dated), the DR trail. Deterministic per
state snapshot. Static legal pages + signup machine are copied/templated
separately (same verified pattern as the ten companies).
"""
from __future__ import annotations

import json

import config
import dashboard
import holding
import nervous

OUT = config.ROOT.parent / "group" / "site" / "public"

HEAD = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title><meta name="description" content="__DESC__">
<meta property="og:title" content="__TITLE__"><meta property="og:description" content="__DESC__">
<meta property="og:type" content="website">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="canonical" href="https://cogops-group.pages.dev/__PAGE__">
<meta name="theme-color" content="#0b0e14">
<meta property="og:image" content="https://cogops-group.pages.dev/og-image.png">
<meta property="og:url" content="https://cogops-group.pages.dev/__PAGE__">
<meta property="og:site_name" content="CogOps Group">
<style>
:root{--bg:#0b0e14;--ink:#e8edf6;--dim:#9aa7bf;--acc:#7ee0b8;--acc2:#6ea8fe;--line:#222c40;--card:#121a28;--warn:#ffcf6e}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font:14.5px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;overflow-x:hidden}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}a{color:var(--acc2);text-decoration:none}
.blobs{position:fixed;inset:0;z-index:-1;filter:blur(90px);opacity:.45}.blobs i{position:absolute;border-radius:50%}
.blobs i:nth-child(1){width:520px;height:520px;background:#1d6e4e;top:-140px;left:-120px}
.blobs i:nth-child(2){width:420px;height:420px;background:#274a7d;top:32%;right:-140px}
nav{position:sticky;top:0;z-index:9;backdrop-filter:blur(14px);background:rgba(11,14,20,.72);border-bottom:1px solid var(--line)}
.navin{display:flex;align-items:center;gap:18px;padding:14px 20px}
.brand{font-weight:800;letter-spacing:.6px}.brand em{color:var(--acc);font-style:normal}
.nlinks{display:flex;gap:16px;margin-left:auto;color:var(--dim);font-size:13.5px}.nlinks a:hover{color:var(--ink)}
.btn{display:inline-block;border:1px solid var(--acc);color:var(--acc);border-radius:99px;padding:9px 18px;font-weight:600;font-size:13.5px}
.btn.grad{background:linear-gradient(135deg,#2ea97c,#3d7dd8);border:none;color:#fff}
.hero{text-align:center;padding:88px 0 46px}
.badge{display:inline-block;border:1px solid var(--line);background:var(--card);color:var(--acc);border-radius:99px;padding:6px 14px;font-size:12px;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:20px}
h1{font-size:clamp(32px,6vw,56px);line-height:1.08;letter-spacing:-.5px}
h1 em{font-style:normal;background:linear-gradient(120deg,var(--acc),var(--acc2));-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--dim);max-width:720px;margin:18px auto 30px;font-size:17px}
section{padding:52px 0}.eyebrow{color:var(--acc);font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px}
h2{font-size:clamp(23px,3.4vw,31px);margin-bottom:20px;letter-spacing:-.3px}
.grid{display:grid;gap:14px}.g2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}.g3{grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}.g5{grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px}
.card h3{font-size:15.5px;margin:6px 0;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.card p{color:var(--dim);font-size:13px}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block}
.pill{font-size:10px;letter-spacing:1px;border-radius:99px;padding:3px 9px;font-weight:700;background:#12351f;color:#7ee0b8;border:1px solid #1d5c36}
.pill.s0,.pill.s1{background:#3a2f14;color:#ffcf6e;border-color:#6b561f}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:10px 0}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line);font-size:13px;vertical-align:top}
th{color:var(--acc);font-size:11px;letter-spacing:1px;text-transform:uppercase}
.ok{color:#7ee0b8;font-weight:800}.no{color:#ff8f8f;font-weight:800}
code{font:11.5px ui-monospace,Menlo,Consolas,monospace;background:#0d1526;border:1px solid var(--line);border-radius:5px;padding:1px 5px;color:#bcd3ff}
form.signup{max-width:560px;margin:0 auto;display:grid;gap:10px}
form.signup .row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
input,select,textarea{width:100%;background:var(--card);border:1px solid var(--line);color:var(--ink);border-radius:10px;padding:12px 14px;font:inherit}
.hp{position:absolute;left:-9999px}.msg{min-height:22px;font-size:14px;text-align:center;margin-top:8px}.msg.ok2{color:var(--acc)}.msg.bad{color:#ff8f8f}
footer{border-top:1px solid var(--line);color:var(--dim);font-size:13px;padding:32px 0;text-align:center}
svg.graph{width:100%;height:auto;background:var(--card);border:1px solid var(--line);border-radius:14px}
.node-label{font-size:11px;fill:#e8edf6;font-weight:700}.node-sub{font-size:9px;fill:#9aa7bf}
.stamp{color:var(--dim);font-size:12px}
@media(max-width:640px){.nlinks{display:none}form.signup .row{grid-template-columns:1fr}}
</style></head><body>
<div class="blobs"><i></i><i></i></div>
<nav><div class="wrap navin"><span class="brand">CogOps <em>Group</em></span>
<div class="nlinks"><a href="/#companies">Companies</a><a href="/#central">The central business</a><a href="/governance.html">Governance</a><a href="/#talk">Talk to us</a><a href="/imprint.html">Legal</a></div>
<a class="btn grad" href="/#talk">Talk to the group</a></div></nav>
"""

FOOT = """<footer><div class="wrap">
<b>CogOps Group</b> · Switzerland · legal entity in formation (GmbH, DR-0004)<br>
__SITELINKS__<br>
<a href="mailto:cogops.engine@gmail.com">cogops.engine@gmail.com</a> · <a href="/privacy.html">Privacy</a> · <a href="/imprint.html">Impressum</a> · <a href="https://cogops-growth.pages.dev/terms.html">Terms v1.0</a><br>
<span style="opacity:.7">© 2026 CogOps Group · one group · ten companies · one keystroke</span>
</div></footer></body></html>"""

PRINCIPLES = [
    ("AI-run, human-gated", "agents produce; one founder keystroke approves anything external, financial or irreversible"),
    ("Software & data only", "no labs, fabs, hardware or licenses a solo operator cannot hold"),
    ("One spine, many skins", "site factory, LLM gateway, CRM, gates, theme: a new company is config + content"),
    ("Evidence over claims", "as-of dates, sources, version hashes, reproduce→fix→verify, 145-check regression suite"),
    ("Profit to one engine", "surplus flows through one capital ladder; internal trades at published prices"),
    ("Deep tech is a market", "excluded domains are served as customers, never entered as practitioners"),
]

CENTRAL = [
    ("AI core", "the 110-role agent hierarchy in 7 universes; squads per company; missions that block honestly"),
    ("The gate", "Type-1/2/3 classification, G1/G2/G3 levels, fail-closed, phone-push on staging, consume-on-approve"),
    ("Capital engine", "fortress first, deployment ladder, 30% sweep under the Swiss guard, FCF-per-company scoreboard"),
    ("Site factory", "one codebase → ten live evidence machines + this site; theme.json is the only brand source"),
    ("Shared spine", "LLM gateway with caps, CRM, auth/portal patterns, CBS playbook, hash-chained ledgers"),
    ("Nervous system", "senses → reflexes → pain (freeze) → nerves (dependency flags) → consciousness (dashboard)"),
]


def _company_cards(st: dict) -> str:
    theme = json.loads((config.ROOT / "data" / "theme.json").read_text(encoding="utf-8"))
    cards = []
    for c in st["companies"]:
        slug = c["slug"]
        acc = theme["companies"][slug]["accent"]
        cnt = st["counts"].get(slug)
        cnt_s = f" · queue {cnt}" if isinstance(cnt, int) else ""
        dorm = (' <span class="pill" style="background:#3a2c14;color:var(--warn);'
                'border:1px solid var(--warn)">DORMANT · DR-0013</span>'
                if c.get("dormant") else "")
        cards.append(
            f'<div class="card"><h3><span class="dot" style="background:{acc}"></span>'
            f'{c["name"].replace("CogOps ", "")} <span class="pill s{c["stage"]}">S{c["stage"]} {c["stage_name"]}</span>{dorm}</h3>'
            f'<p>{theme["companies"][slug]["tagline"].capitalize()}.</p>'
            f'<p style="margin-top:6px">Promise: <b style="color:var(--ink)">{c["promise"]}</b>{cnt_s}<br>'
            f'Boundary: {c["boundary"]}</p>'
            f'<p style="margin-top:6px"><a href="{c["url"]}">{c["url"].replace("https://", "")} →</a></p></div>')
    return "".join(cards)


def _invariants_table(inv: list) -> str:
    rows = "".join(
        f'<tr><td>{r["id"]}</td><td>{r["name"]}</td><td class="{"ok" if r["ok"] else "no"}">'
        f'{"PASS" if r["ok"] else "FAIL"}</td><td>{r["how"]}</td></tr>' for r in inv)
    return ('<table><tr><th>#</th><th>Invariant</th><th>Now</th><th>How it is proved</th></tr>'
            + rows + '</table>')


def _dr_table(drs: list) -> str:
    return ('<table><tr><th>DR</th><th>Decision</th></tr>' +
            "".join(f'<tr><td>{d["id"]}</td><td>{d["title"]}</td></tr>' for d in drs) + '</table>')


FORM = """<section id="talk"><div class="wrap" style="max-width:640px">
<div class="eyebrow" style="text-align:center">One door for everything</div>
<h2 style="text-align:center">Talk to the group</h2>
<form class="signup" id="f">
  <div class="row"><input name="email" type="email" required placeholder="Email *" aria-label="Email">
  <input name="company" type="text" required placeholder="Organization *" aria-label="Organization"></div>
  <div class="row"><select name="product" required aria-label="Reason">
    <option value="" disabled selected>I am… *</option>
    <option>a client (any company)</option><option>a partner / alliance</option>
    <option>investor / fiduciary / lawyer</option><option>press</option><option>a candidate</option></select>
  <input name="icp" type="text" placeholder="Which company or topic?" aria-label="Company or topic"></div>
  <textarea name="note" rows="2" placeholder="One paragraph is plenty (optional)" aria-label="Message, optional"></textarea>
  <div class="hp" aria-hidden="true"><input name="website" tabindex="-1" autocomplete="off"></div>
  <button class="btn grad" type="submit" id="go">Send to the group →</button>
  <div class="msg" id="m"></div></form>
<p style="color:var(--dim);font-size:13px;text-align:center;margin-top:12px">Routed by a human to the right company within 1 business day. Nothing auto-replies.</p>
</div></section>
<script>
document.getElementById("f").addEventListener("submit",function(ev){
  ev.preventDefault();var m=document.getElementById("m"),b=document.getElementById("go");
  var d=Object.fromEntries(new FormData(this).entries());
  b.disabled=true;m.textContent="";m.className="msg";
  fetch("/api/signup",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d)})
  .then(function(r){return r.json().then(function(j){return{s:r.status,j:j}})})
  .then(function(x){if(x.s===200&&x.j.ok){m.className="msg ok2";m.textContent="✓ Received — a human routes this within 1 business day."}
    else{m.className="msg bad";m.textContent=x.j.error==="duplicate"?"Already received — a human is on it.":(x.j.error||"Failed. Email cogops.engine@gmail.com directly.")}})
  .catch(function(){m.className="msg bad";m.textContent="Failed. Email cogops.engine@gmail.com directly."})
  .finally(function(){b.disabled=false});
});
</script>"""


def build(fetch_counts: bool = False, out=None) -> dict:
    st = holding.group_status(fetch_counts=fetch_counts)
    graph = dashboard._svg(nervous.state())
    sitelinks = " · ".join(
        f'<a href="{c["url"]}">{c["name"].replace("CogOps ", "")}</a>' for c in st["companies"])
    comp_cards = _company_cards(st)
    prin = "".join(f'<div class="card"><h3>{t}</h3><p>{p}</p></div>' for t, p in PRINCIPLES)
    cent = "".join(f'<div class="card"><h3>{t}</h3><p>{p}</p></div>' for t, p in CENTRAL)
    idx = HEAD.replace("__TITLE__", "CogOps Group — one group, ten companies, one keystroke") \
        .replace("__DESC__", "The holding company: structure, principles, governance and the live trade graph of ten AI-operated Swiss companies under one human gate.") \
        .replace("__PAGE__", "")
    idx += f"""<header class="hero"><div class="wrap">
<div class="badge">Swiss · AI-operated · human-gated · entity in formation (GmbH)</div>
<h1>One group. Ten companies.<br><em>One keystroke.</em></h1>
<p class="sub">CogOps Group is the central business: it owns the gate, the capital ladder, the brand, the playbook and the platform — and nothing else. Every company below faces its market alone with its own P&L; together they trade verified evidence on an internal market at published prices. The graph is live, not decorative.</p>
<p class="stamp">state as of {st["generated_at"]} · fortress {st["fortress_months"]} months · {len(st["drs"])} decision records · invariants audited below</p>
</div></header>
<section id="graph"><div class="wrap">
<div class="eyebrow">The living structure</div>
<h2>Every line is a trade route that exists in code</h2>
<svg class="graph" viewBox="0 0 1000 660" role="img" aria-label="CogOps trade graph">{graph.split('>',1)[1] if graph.startswith('<svg') else graph}</svg>
<p class="stamp" style="margin-top:8px">Rose solid = pairs (Growth↔Talent, Verde↔Terra) · blue = the Regulatory-Science Clique (complete graph K5) · mint dashed = the Multiplier's star (Intelligence ↔ everyone). Edges are platform tickets at published internal prices; each charge lands on both P&Ls.</p>
</div></section>
<section id="companies"><div class="wrap">
<div class="eyebrow">The ten</div>
<h2>Each alone: a company. Together: a supply chain of evidence.</h2>
<div class="grid g2">{comp_cards}</div>
</div></section>
<section id="central"><div class="wrap">
<div class="eyebrow">The central business</div>
<h2>What the holding owns — and all it owns</h2>
<div class="grid g3">{cent}</div>
<div class="grid g3" style="margin-top:14px">{prin}</div>
</div></section>
<section id="gov"><div class="wrap">
<div class="eyebrow">Governance, executable</div>
<h2>Twelve invariants, proved on demand</h2>
{_invariants_table(st["invariants"])}
<p class="stamp">Full doctrine, decision records and the nervous-system dashboard: <a href="/governance.html">governance page</a>. The invariants table is generated by code (<code>holding.invariants()</code>) — it cannot be edited into looking better.</p>
</div></section>
{FORM}
""" + FOOT.replace("__SITELINKS__", sitelinks)

    gov = HEAD.replace("__TITLE__", "Governance — CogOps Group") \
        .replace("__DESC__", "Decision records, invariants, gate doctrine and the nervous system: how one human governs ten AI-operated companies.") \
        .replace("__PAGE__", "governance.html")
    gov += f"""<header class="hero" style="padding-bottom:20px"><div class="wrap">
<h1 style="font-size:clamp(28px,4vw,40px)">Governance</h1>
<p class="sub" style="margin-bottom:0">Doctrine lives in <code>structure/OPERATING-STRUCTURE.md</code> v1.1; amendments only via Decision Records; the nervous system enforces what prose promises.</p>
</div></header>
<section><div class="wrap">
<div class="eyebrow">Decision records (append-only)</div>
<h2>Every structural choice, dated and evidenced</h2>
{_dr_table(st["drs"])}
</div></section>
<section><div class="wrap">
<div class="eyebrow">Invariants I1–I12</div>
<h2>The lines that do not move</h2>
{_invariants_table(st["invariants"])}
</div></section>
<section><div class="wrap">
<div class="eyebrow">Doctrine in one breath</div>
<h2>How one human governs ten companies</h2>
<div class="grid g2">
<div class="card"><h3>The gate</h3><p>Type-1 (external/financial/irreversible) actions stage with an evidence pack and wait for a keystroke — pushed to the founder's phone on staging. Type-2 runs free inside envelopes. Nothing self-approves; the inbox has no send() function at all.</p></div>
<div class="card"><h3>The pain</h3><p>Critical signals (broken ledger chain, fortress breach) freeze group spending automatically. Integrity freezes release only via the founder's confirmation phrase. The machine stops; it does not limp.</p></div>
<div class="card"><h3>The nerves</h3><p>Every trade edge is a dependency nerve: if a seller degrades, every buyer's evidence chain is flagged automatically. Pairs, clique and star are derived from code registries, not diagrams.</p></div>
<div class="card"><h3>The consciousness</h3><p>The founder dashboard (localhost-only) renders the body: organ map, vitals, gate queue, signal feed, missions. Public transparency stops at this page by design — the consciousness is private, the facts are public.</p></div>
</div>
</div></section>
""" + FOOT.replace("__SITELINKS__", sitelinks)

    from pathlib import Path
    OUTD = Path(out) if out else OUT
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / "index.html").write_text(idx, encoding="utf-8")
    (OUTD / "governance.html").write_text(gov, encoding="utf-8")
    return {"index": len(idx), "governance": len(gov),
            "generated_at": st["generated_at"],
            "invariants_pass": sum(1 for r in st["invariants"] if r["ok"]),
            "invariants_total": len(st["invariants"])}
