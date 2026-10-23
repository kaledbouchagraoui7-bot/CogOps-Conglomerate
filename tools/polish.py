#!/usr/bin/env python3
"""polish.py — Persuasion pack v1 (DR-0016).
Injects into each company site's public/index.html:
  1. Aesthetic micro-interaction CSS (hover lift, focus rings, selection, smooth scroll)
  2. Trust band (verifiable signals only — NEVER fabricated testimonials)
  3. 3-step progress stepper + personalization line
  4. Scroll-aware sticky CTA (reuses the site's own hero label)
  5. Live sample-slot scarcity JS fed by /api/count (real weekly caps, DR-0016)
Idempotent: skips files already containing the marker.
"""
import pathlib, re, sys

MARK = "<!-- polish-pack v1 -->"
ROOT = pathlib.Path(__file__).resolve().parents[1]
SITES = ["growth", "talent", "helix", "verde", "terra",
         "sentinel", "capitalco", "dossia", "medtech", "intelligence"]

CSS = """
""" + MARK + """
<style>
html{scroll-behavior:smooth}
::selection{background:var(--accent);color:#0a0f16}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.btn{transition:transform .15s ease,box-shadow .15s ease,border-color .15s ease}
.btn:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.28)}
.btn.ghost:hover{border-color:var(--accent);color:var(--accent)}
.card{transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}
.card:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(0,0,0,.24);border-color:color-mix(in srgb,var(--accent) 35%,var(--line))}
details summary{transition:color .15s}
details summary:hover{color:var(--accent)}
.trustband{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:4px auto 0;padding:0 20px;max-width:1120px}
.tchip{font-size:11px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:4px 11px;background:rgba(127,127,127,.05);white-space:nowrap}
.tchip a{color:var(--muted);text-decoration:none;border-bottom:1px dotted}
.tchip.slots{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 45%,transparent);font-weight:600}
.stepper{display:flex;align-items:center;justify-content:center;gap:10px;margin:28px auto 6px;flex-wrap:wrap;padding:0 20px}
.stepper .st{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--dim)}
.stepper .st b{display:grid;place-items:center;width:22px;height:22px;border-radius:50%;background:color-mix(in srgb,var(--accent) 18%,transparent);color:var(--accent);font-size:11px;border:1px solid color-mix(in srgb,var(--accent) 45%,transparent)}
.stepper i{width:26px;height:1px;background:var(--line)}
.persuade{text-align:center;font-size:12px;color:var(--dim);min-height:18px;margin:6px auto 0;max-width:600px;padding:0 20px;transition:opacity .2s}
.stickycta{position:fixed;right:18px;bottom:18px;z-index:50;display:inline-block;background:var(--accent);color:#0a0f16;font-weight:700;font-size:13px;padding:11px 18px;border-radius:999px;text-decoration:none;box-shadow:0 8px 26px rgba(0,0,0,.4);transform:translateY(90px);opacity:0;transition:transform .25s ease,opacity .25s ease;pointer-events:none}
.stickycta.show{transform:translateY(0);opacity:1;pointer-events:auto}
.stickycta:hover{filter:brightness(1.08)}
@media (max-width:600px){.stepper i{display:none}}
</style>"""

TRUST = """<div class="trustband">
<span class="tchip">🔒 Human approval on every external act</span>
<span class="tchip">📜 Evidence attached to every record</span>
<span class="tchip"><a href="https://cogops-group.pages.dev/governance.html" target="_blank" rel="noopener">Public invariants &amp; governance ↗</a></span>
<span class="tchip slots" id="slots">checking weekly sample slots…</span>
</div>
"""

STEPPER = """<div class="stepper" aria-label="How it works">
<div class="st"><b>1</b><span>Tell us the target</span></div><i></i>
<div class="st"><b>2</b><span>Named reply ≤ 1 business day</span></div><i></i>
<div class="st"><b>3</b><span>Sample in 48 h — pay only after proof</span></div>
</div>
<p class="persuade" id="persuade"></p>
"""

JS = """<a href="#signup" class="stickycta" id="scta">__LABEL__</a>
<script>
(function(){
var scta=document.getElementById('scta'),su=document.getElementById('signup');
function sync(){if(!su)return;var r=su.getBoundingClientRect();
if(r.top<window.innerHeight-80&&r.bottom>0){scta.classList.remove('show');}
else if(window.scrollY>420){scta.classList.add('show');}else{scta.classList.remove('show');}}
window.addEventListener('scroll',sync,{passive:true});sync();
var pers={
'lead':'Lead enrichment: only validated records — rejected candidates cost you nothing.',
'enrich':'Lead enrichment: only validated records — rejected candidates cost you nothing.',
'seo':'Programmatic SEO: pages built from your own data, QA-gated before they touch your domain.',
'newsletter':'Media placement: your offer inside the industry journal your prospects already open.',
'media':'Media placement: your offer inside the industry journal your prospects already open.',
'journal':'Media placement: your offer inside the industry journal your prospects already open.',
'audit':'Security work: scored controls and ranked fixes — defensive only, no offense sold.',
'security':'Security work: scored controls and ranked fixes — defensive only, no offense sold.',
'review':'Capital analytics: guard-inside-the-loop backtests — your keys, your approvals, your decisions.',
'threat':'Security work: scored controls and ranked fixes — defensive only, no offense sold.',
'backtest':'Capital analytics: guard-inside-the-loop backtests — your keys, your approvals, your decisions.',
'factor':'Capital analytics: guard-inside-the-loop backtests — your keys, your approvals, your decisions.',
'treasury':'Capital analytics: guard-inside-the-loop backtests — your keys, your approvals, your decisions.',
'plan':'Capital analytics: guard-inside-the-loop backtests — your keys, your approvals, your decisions.',
'dossier':'Regulatory deliverables: ICH-structured, source-tagged — your signatory signs, never us.',
'ctd':'Regulatory deliverables: ICH-structured, source-tagged — your signatory signs, never us.',
'module':'Regulatory deliverables: ICH-structured, source-tagged — your signatory signs, never us.',
'alcoa':'Regulatory deliverables: ICH-structured, source-tagged — your signatory signs, never us.',
'qc':'Regulatory deliverables: ICH-structured, source-tagged — your signatory signs, never us.',
'feed':'Regulatory deliverables: ICH-structured, source-tagged — your signatory signs, never us.',
'surveillance':'Regulatory deliverables: ICH-structured, source-tagged — your signatory signs, never us.',
'skeleton':'Regulatory deliverables: ICH-structured, source-tagged — your signatory signs, never us.',
'mdr':'Medtech documentation: Annex-scoped trees, append-only trails — research use, you stay signatory.',
'trail':'Medtech documentation: Annex-scoped trees, append-only trails — research use, you stay signatory.',
'spec':'Medtech documentation: Annex-scoped trees, append-only trails — research use, you stay signatory.',
'device':'Medtech documentation: Annex-scoped trees, append-only trails — research use, you stay signatory.',
'usability':'Medtech documentation: Annex-scoped trees, append-only trails — research use, you stay signatory.',
'carbon':'Carbon books: sourced factors on every line — proxies labeled coarse, never dressed as measured.',
'csrd':'Carbon books: sourced factors on every line — proxies labeled coarse, never dressed as measured.',
'reduction':'Carbon books: sourced factors on every line — proxies labeled coarse, never dressed as measured.',
'energy':'Carbon books: sourced factors on every line — proxies labeled coarse, never dressed as measured.',
'book':'Carbon books: sourced factors on every line — proxies labeled coarse, never dressed as measured.',
'risk':'Risk & transition packs: screening-grade, model grade stated on every artifact.',
'pack':'Risk & transition packs: screening-grade, model grade stated on every artifact.',
'brief':'Risk & transition packs: screening-grade, model grade stated on every artifact.',
'transition':'Risk & transition packs: screening-grade, model grade stated on every artifact.',
'screen':'Risk & transition packs: screening-grade, model grade stated on every artifact.',
'scan':'Talent: explainable matches — no black-box scores; fee only on hire.',
'track':'Talent: explainable matches — no black-box scores; fee only on hire.',
'academy':'Talent: explainable matches — no black-box scores; fee only on hire.',
'hire':'Talent: explainable matches — no black-box scores; fee only on hire.',
'deployment':'Intelligence: agents produce, humans approve — labeled AI, real sources, no invented numbers.',
'assistant':'Intelligence: agents produce, humans approve — labeled AI, real sources, no invented numbers.',
'agent':'Intelligence: agents produce, humans approve — labeled AI, real sources, no invented numbers.',
'concierge':'Intelligence: agents produce, humans approve — labeled AI, real sources, no invented numbers.',
'automat':'Intelligence: agents produce, humans approve — labeled AI, real sources, no invented numbers.'};
var sel=document.querySelector('#f select[name=product]'),pl=document.getElementById('persuade');
function upd(){if(!sel||!pl)return;var v=(sel.value||'').toLowerCase();pl.style.opacity=0;
setTimeout(function(){var line='Tell us the target — the rest is our burden, not yours.';
var keys=Object.keys(pers);for(var i=0;i<keys.length;i++){if(v.indexOf(keys[i])>=0){line=pers[keys[i]];break;}}
pl.textContent=line;pl.style.opacity=1;},160);}
if(sel&&pl){sel.addEventListener('change',upd);upd();}
var sl=document.getElementById('slots');
fetch('/api/count').then(function(r){return r.json();}).then(function(d){
if(sl&&typeof d.slots_left==='number'){sl.textContent=d.slots_left>0?
('⏳ '+d.slots_left+' free-sample slot'+(d.slots_left===1?'':'s')+' left this week'):
('Weekly sample slots full — next queue opens Monday');}}).catch(function(){if(sl)sl.textContent='';});
})();
</script>
"""

def hero_label(html):
    m = re.search(r'href="#signup"[^>]*>\s*([^<]+?)\s*<', html)
    return (m.group(1).strip() if m else "Request the free sample →")

def polish(path):
    p = pathlib.Path(path)
    s = p.read_text(encoding="utf-8")
    if MARK in s:
        return "skip (already polished)"
    s = s.replace("</head>", CSS + "\n</head>", 1)
    i = s.find("<section id=")
    assert i > 0, "no <section id= anchor"
    s = s[:i] + TRUST + s[i:]
    j = s.find('<form class="signup')
    assert j > 0, "no form anchor"
    s = s[:j] + STEPPER + s[j:]
    lbl = hero_label(s)
    s = s.replace("</body>", JS.replace("__LABEL__", lbl) + "\n</body>", 1)
    p.write_text(s, encoding="utf-8")
    return "polished (cta: %r)" % lbl

if __name__ == "__main__":
    for slug in SITES:
        f = ROOT / slug / "site" / "public" / "index.html"
        print(slug.ljust(13), polish(f) if f.exists() else "MISSING")
