#!/usr/bin/env python3
"""tools/polish2.py — Experience pack v2 (DR-0016c): distinct identity & motion,
interactive discovery widgets, zero-friction usability, surprise & delight.

Adds, idempotently (marker '<!-- polish-pack v2 -->') to each company site:
  1. Display-typography pairing + mono accents (no external fonts — instant load).
  2. Motion: hero entrance stagger, drifting blobs, card lift, button press,
     success pop, View Transitions for cross-page nav (progressive).
  3. Skip-to-content link, mobile table scroll, focus polish.
  4. One real interactive tool per company ("Try the math yourself") that runs
     the company's own engine logic client-side — discovery + value proof.
  5. Delight: haptic tick on signup success, per-company witty 404 pages.
Honesty: every estimator is labeled as an estimate/heuristic preview; no
fabricated numbers, factors are shown, the paid deliverable is the evidence.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARK = "<!-- polish-pack v2 -->"

CSS = """
/* ---- experience pack v2: identity, motion, usability, delight ---- */
:root{--font-display:"Space Grotesk","Avenir Next","Segoe UI Variable Display",system-ui,sans-serif;
      --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
html{scroll-behavior:smooth}
main h1,main h2{font-family:var(--font-display);font-weight:800;letter-spacing:-.02em}
.eyebrow,.num,.tchip,.stepper b,.slots,.slots strong,.slots em,.vt-sec{font-family:var(--mono)}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.hero section>*{animation:rise .7s cubic-bezier(.2,.7,.2,1) both}
.hero section>*:nth-child(2){animation-delay:.08s}
.hero section>*:nth-child(3){animation-delay:.16s}
.hero section>*:nth-child(4){animation-delay:.24s}
@keyframes drift{from{transform:translate(0,0) scale(1)}to{transform:translate(40px,-30px) scale(1.15)}}
.blob{animation:drift 22s ease-in-out infinite alternate}
.blob:nth-of-type(2){animation-duration:28s;animation-direction:alternate-reverse}
.card{transition:transform .25s ease,box-shadow .25s ease,border-color .25s ease}
.card:hover{transform:translateY(-4px);box-shadow:0 14px 34px rgba(15,20,27,.10)}
.btn:active{transform:scale(.97)}
.msg.ok{animation:pop .4s cubic-bezier(.2,1.4,.4,1)}
@keyframes pop{0%{transform:scale(.92);opacity:0}100%{transform:scale(1);opacity:1}}
.skip{position:fixed;top:-60px;left:16px;z-index:60;background:var(--accent);color:#fff;
  padding:10px 18px;border-radius:10px;font-weight:700;transition:top .2s;text-decoration:none}
.skip:focus{top:12px}
[role="status"],.slots{transition:background .3s}
table{scroll-margin-top:80px}
@media (max-width:640px){table{display:block;overflow-x:auto;max-width:100%;white-space:nowrap}}
.est{border:1px solid var(--line);border-radius:16px;padding:22px;background:var(--panel);
  box-shadow:0 2px 10px rgba(15,20,27,.04)}
.est .row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:14px}
.est label{display:block;font-size:.8rem;color:var(--dim);margin-bottom:5px;font-weight:600}
.est input[type=number],.est select,.est textarea{width:100%;background:var(--bg);border:1px solid var(--line);
  border-radius:10px;padding:10px 12px;color:var(--ink);font-family:var(--mono);font-size:.92rem}
.est textarea{min-height:96px;resize:vertical}
.est .chips{display:flex;flex-wrap:wrap;gap:8px}
.est .chip{cursor:pointer;user-select:none;border:1px solid var(--line);border-radius:99px;
  padding:7px 14px;font-size:.84rem;font-weight:600;color:var(--dim);background:var(--bg);
  transition:all .2s}
.est .chip.on{background:var(--accent);border-color:var(--accent);color:#fff}
.est .out{margin-top:16px;padding:16px;border-radius:12px;background:var(--bg);border:1px dashed var(--line)}
.est .big{font-family:var(--mono);font-size:1.7rem;font-weight:700;color:var(--accent)}
.est .note{font-size:.82rem;color:var(--dim);margin-top:10px;line-height:1.55}
.est ul{margin:8px 0 0 18px;font-size:.88rem;color:var(--ink)}
@media (prefers-reduced-motion:reduce){.hero section>*,.blob,.msg.ok{animation:none}}
"""

JS = r"""
/* experience pack v2 */
(function(){
  /* View Transitions for cross-page nav (progressive enhancement) */
  if (document.startViewTransition) {
    document.addEventListener('click', function(e){
      var a = e.target.closest && e.target.closest('a[href]');
      if (!a || a.target === '_blank' || e.metaKey || e.ctrlKey) return;
      var u = new URL(a.href, location.href);
      if (u.origin !== location.origin || u.pathname === location.pathname) return;
      e.preventDefault();
      document.startViewTransition(function(){ location.href = a.href; });
    });
  }
  /* haptic tick when the signup succeeds (mobile), purely decorative */
  var m = document.getElementById('m');
  if (m && window.MutationObserver) {
    new MutationObserver(function(){
      if ((m.className||'').indexOf('ok') >= 0 && navigator.vibrate) navigator.vibrate([8,24,8]);
    }).observe(m, {attributes:true, attributeFilter:['class']});
  }
  /* ---- interactive discovery widget ---- */
  var cfgEl = document.getElementById('est-cfg');
  var host = document.getElementById('est');
  if (!cfgEl || !host) return;
  var C = JSON.parse(cfgEl.textContent);
  var $ = function(t, cls, txt){ var e = document.createElement(t); if(cls) e.className = cls; if(txt!=null) e.textContent = txt; return e; };
  var state = {};

  function run(){
    var out = document.getElementById('est-out'); out.innerHTML = '';
    var res = null;
    try { res = LIB[C.type](C, state); } catch(err){ res = {big:'—', note:'Check the inputs.'}; }
    out.appendChild($('<div class="big">', null, res.big));
    if (res.rows) { var ul = $('ul'); res.rows.forEach(function(r){ ul.appendChild($('li', null, r)); }); out.appendChild(ul); }
    out.appendChild($('<div class="note">', null, res.note || C.note || ''));
    out.style.animation = 'none'; void out.offsetWidth; out.style.animation = 'pop .3s';
  }

  var LIB = {
    calc: function(c, s){
      var v = {}; c.inputs.forEach(function(i){ v[i.k] = parseFloat(s[i.k] != null ? s[i.k] : i.d); });
      var r = (new Function(Object.keys(v), 'return (' + c.formula + ')')).apply(null, Object.keys(v).map(function(k){return v[k];}));
      return {big: (Math.round(r*100)/100).toLocaleString('de-CH') + ' ' + c.unit, note: c.note};
    },
    match: function(c, s){
      var role = c.roles[s.role || c.defRole]; var got = s.skills || [];
      var tot = 0, hit = 0, gaps = [];
      Object.keys(role).forEach(function(k){ tot += role[k]; if (got.indexOf(k) >= 0) hit += role[k]; else gaps.push(k); });
      var pct = Math.round(100*hit/tot);
      return {big: pct + '% match — ' + (s.roleLabel || ''),
        rows: gaps.length ? ['Missing for this role: ' + gaps.join(', ')] : ['No gaps for this role — the scan would go straight to portfolio evidence.'],
        note: pct < 70 ? 'Below 70%? The free skill-gap scan shows exactly where, and what it costs to close.' : c.note};
    },
    fasta: function(c, s){
      var seq = (s.seq || '').toUpperCase().replace(/[^ACGTUN]/g, '');
      if (seq.length < 20) return {big: 'paste a sequence', note: '20+ bases needed (browser-side preview only).'};
      var gc = (seq.match(/[GC]/g) || []).length;
      var pct = Math.round(1000*gc/seq.length)/10;
      var best = 0;
      var frames = [seq, seq.slice(1), seq.slice(2)];
      frames.forEach(function(f){
        for (var i = 0; i + 3 <= f.length; i += 3) {
          var codon = f.substr(i, 3), run = 0;
          while (codon !== 'TAA' && codon !== 'TAG' && codon !== 'TGA' && i + 3 <= f.length) {
            run++; i += 3; codon = f.substr(i, 3);
          }
          if (run > best) best = run;
        }
      });
      var rows = ['Length: ' + seq.length + ' nt', 'GC: ' + pct + '% (' + (pct >= 40 && pct <= 60 ? 'in range' : 'flagged') + ')',
        'Longest ORF frame-scan: ~' + best + ' aa'];
      return {big: pct + '% GC', rows: rows, note: c.note};
    },
    quiz: function(c, s){
      var yes = 0; c.qs.forEach(function(q, i){ if (s['q'+i] === 'yes') yes++; });
      var pct = Math.round(100*yes/c.qs.length);
      var verdict = pct >= 84 ? 'Strong baseline — the snapshot would hunt the subtle stuff.' :
        pct >= 50 ? 'Half-covered. The un-checked items are exactly where the free snapshot starts.' :
        'Exposed. Take the free edge snapshot before it gets expensive.';
      return {big: pct + '% covered', rows: [verdict], note: c.note};
    },
    map: function(c, s){
      var sel = s.pick || c.options[0].v;
      var opt = null; c.options.forEach(function(o){ if (o.v === sel) opt = o; });
      return {big: opt.h, rows: opt.rows, note: c.note};
    },
    classify: function(c, s){
      var lines = (s.steps || '').split('\n').map(function(x){return x.trim();}).filter(Boolean);
      if (!lines.length) return {big: 'list your steps', note: 'One step per line.'};
      var agent = [], human = [], gate = [];
      lines.forEach(function(l){
        var t = l.toLowerCase();
        if (c.gateKw.some(function(k){ return t.indexOf(k) >= 0; })) gate.push(l);
        else if (c.agentKw.some(function(k){ return t.indexOf(k) >= 0; })) agent.push(l);
        else human.push(l);
      });
      return {big: agent.length + ' agent · ' + gate.length + ' gated · ' + human.length + ' human',
        rows: ['Delegation potential: ' + Math.round(100*agent.length/lines.length) + '% of listed steps'],
        note: c.note};
    }
  };

  /* render inputs */
  var form = $('<div>'); var row = $('<div class="row">'); form.appendChild(row);
  function numIn(i){
    var lab = $('<label>'); lab.textContent = i.label;
    var inp = $('<input type="number">'); inp.value = i.d; inp.step = 'any';
    inp.addEventListener('input', function(){ state[i.k] = inp.value; run(); });
    state[i.k] = i.d; lab.appendChild(inp); return lab;
  }
  function selIn(i, onChange){
    var lab = $('<label>'); lab.textContent = i.label;
    var sel = $('<select>');
    i.o.forEach(function(o){
      var op = $('<option>'); op.value = (typeof o === 'object') ? o.v : o;
      op.textContent = (typeof o === 'object') ? o.label : o; sel.appendChild(op);
    });
    state[i.k] = sel.value = (i.d != null ? i.d : ((typeof i.o[0] === 'object') ? i.o[0].v : i.o[0]));
    sel.value = state[i.k];
    sel.addEventListener('change', function(){ state[i.k] = sel.value; onChange && onChange(sel); run(); });
    lab.appendChild(sel); return lab;
  }
  if (C.type === 'calc') C.inputs.forEach(function(i){
    row.appendChild(i.t === 'select' ? selIn(i) : numIn(i));
  });
  else if (C.type === 'match') {
    var wrap = $('<div>'); wrap.appendChild($('<label>', null, 'Your skills (tap)'));
    var chips = $('<div class="chips">'); state.skills = [];
    C.skills.forEach(function(sk){
      var ch = $('<span class="chip">', null, sk);
      ch.addEventListener('click', function(){
        var ix = state.skills.indexOf(sk);
        if (ix >= 0) { state.skills.splice(ix, 1); ch.classList.remove('on'); }
        else { state.skills.push(sk); ch.classList.add('on'); }
        run();
      });
      chips.appendChild(ch);
    });
    wrap.appendChild(chips); row.appendChild(wrap);
    row.appendChild(selIn({k:'role', label:'Target role', o: Object.keys(C.roles).map(function(r){return {v:r, label:r};}), d: C.defRole},
      function(sel){ state.roleLabel = sel.options[sel.selectedIndex].textContent; }));
    state.roleLabel = C.defRole;
  }
  else if (C.type === 'fasta') {
    var lab = $('<label>', null, C.label || 'Paste DNA (FASTA or raw)');
    var ta = $('<textarea>'); ta.placeholder = '>seq1\nATGCGT…';
    ta.addEventListener('input', function(){ state.seq = ta.value; run(); });
    lab.appendChild(ta); row.appendChild(lab);
  }
  else if (C.type === 'quiz') {
    C.qs.forEach(function(q, i){
      row.appendChild(selIn({k:'q'+i, label:q, o:[{v:'no',label:'no'},{v:'yes',label:'yes'}], d:'no'}));
    });
  }
  else if (C.type === 'map') {
    row.appendChild(selIn({k:'pick', label:C.pickLabel, o: C.options.map(function(o){return {v:o.v, label:o.label};}), d: C.options[0].v}));
  }
  else if (C.type === 'classify') {
    var lab2 = $('<label>', null, C.label || 'Your process, one step per line');
    var ta2 = $('<textarea>'); ta2.placeholder = 'extract invoices\ncheck compliance\nemail client';
    ta2.addEventListener('input', function(){ state.steps = ta2.value; run(); });
    lab2.appendChild(ta2); row.appendChild(lab2);
  }
  var btn = $('<button class="btn ghost">', null, C.runLabel || 'Run');
  btn.type = 'button'; btn.addEventListener('click', run);
  form.appendChild(btn);
  var out = $('<div class="out" id="est-out">'); form.appendChild(out);
  host.appendChild(form);
  run();
})();
"""

WIDGET_HEAD = """  <!-- interactive discovery (pack v2) -->
  <section class="block" id="try"><div class="inner">
    <span class="eyebrow">Interactive</span>
    <h2>Try the math yourself</h2>
    <p class="sub">__SUB__</p>
    <div class="est" id="est"></div>
  </div></section>
  <script type="application/json" id="est-cfg">__CFG__</script>
"""

# ---------------------------------------------------------------- per company
CFG = {
 "growth": {
  "sub": "Model your lead flow with real numbers — then let the sample prove we can hit them.",
  "type": "calc",
  "inputs": [{"k": "leads", "label": "validated leads / month", "t": "number", "d": 200},
             {"k": "price", "label": "CHF per lead", "t": "select", "o": ["1", "2", "3"], "d": "2"}],
  "formula": "leads*price", "unit": "CHF / month",
  "note": "Performance model only: rejected records are always CHF 0 and refresh claims are free for 30 days. Retainers (CHF 1,500–3,500/mo) bundle copy + refresh. The sample is the real proof."},
 "talent": {
  "sub": "Tap your skills, pick a Swiss target role — the free scan does this properly, with salary bands and visa path.",
  "type": "match",
  "skills": ["python", "llm", "sql", "stats", "writing", "gcp"],
  "defRole": "AI Ops Engineer",
  "roles": {"AI Ops Engineer": {"python": 3, "llm": 3, "sql": 1, "gcp": 1},
            "Bioinformatics": {"python": 2, "stats": 3, "gcp": 1},
            "RA Medical Writer": {"writing": 3, "stats": 1},
            "Security Analyst": {"python": 1, "sql": 1, "gcp": 2}},
  "note": "Preview weighting is indicative; the paid scan uses the live Swiss role dataset."},
 "helix": {
  "sub": "Paste a sequence — instant browser-side QC preview. The paid report cross-checks every number with evidence.",
  "type": "fasta", "label": "Paste DNA (FASTA or raw)",
  "note": "Rough frame-scan in your browser, labeled as a preview. The paid QC runs Biopython/EMBOSS/QIIME2 pipelines and delivers the evidence table — same numbers, but reproducible and signed."},
 "sentinel": {
  "sub": "Six yes/no questions. Your honest score — and the free snapshot starts wherever you said no.",
  "type": "quiz",
  "qs": ["MFA on all admin accounts?", "CSP header deployed?", "Backups restore-tested this quarter?",
         "AI assistant injection-tested?", "Incident playbook tested?", "Deletion procedure documented?"],
  "note": "Self-assessment, not an audit. The free edge snapshot checks the real HTTP/DNS reality of one domain."},
 "capitalco": {
  "sub": "Swiss-style boring compounding, computed live. Then the free plan check stress-tests your actual numbers.",
  "type": "calc",
  "inputs": [{"k": "m", "label": "CHF per month", "t": "number", "d": 900},
             {"k": "y", "label": "years", "t": "number", "d": 10},
             {"k": "r", "label": "return % / year", "t": "number", "d": 5}],
  "formula": "m*((Math.pow(1+r/1200,y*12)-1)/(r/1200))", "unit": "CHF projected",
  "note": "Arithmetic, not advice — no fees, taxes or inflation modeled. Real mandates run under the risk & concentration guardrails, with a human of record on every recommendation."},
 "verde": {
  "sub": "Rough footprint now, sourced factors later. Placeholder-grade emission factors are shown, not hidden.",
  "type": "calc",
  "inputs": [{"k": "diesel", "label": "diesel L / yr", "t": "number", "d": 500},
             {"k": "kwh", "label": "electricity kWh / yr", "t": "number", "d": 4000},
             {"k": "grid", "label": "grid factor kgCO2e/kWh", "t": "select",
              "o": [{"v": "0.024", "label": "CH 0.024"}, {"v": "0.23", "label": "EU 0.23"}, {"v": "0.38", "label": "US 0.38"}], "d": "0.024"},
             {"k": "spend", "label": "procurement CHF / yr", "t": "number", "d": 10000}],
  "formula": "(diesel*2.68 + kwh*grid + spend*0.35)/1000", "unit": "tCO2e / yr",
  "note": "Diesel 2.68 kg/L and spend 0.35 kg/CHF are placeholder-grade factors (labeled per doctrine). Paid books use sourced, versioned factors with per-invoice computation and the signed reduction plan."},
 "terra": {
  "sub": "A one-minute heuristic screen — the same v0 logic family our analysts start from, before evidence upgrades it.",
  "type": "calc",
  "inputs": [{"k": "value", "label": "asset value CHF", "t": "number", "d": 1000000},
             {"k": "region", "label": "region risk weight", "t": "select",
              "o": [{"v": "0.3", "label": "CH"}, {"v": "0.5", "label": "EU"}, {"v": "0.7", "label": "US"}, {"v": "1", "label": "EM"}], "d": "0.5"},
             {"k": "expo", "label": "exposure multiplier", "t": "select",
              "o": [{"v": "0.5", "label": "low"}, {"v": "1", "label": "medium"}, {"v": "2", "label": "high"}], "d": "1"}],
  "formula": "value*region*expo*0.01", "unit": "CHF 1-in-100 tail proxy",
  "note": "heuristic-v0: a multiplicative proxy, not a validated VaR. The paid screen builds the evidence chain (sources, computations, versions) and flags every assumption."},
 "dossia": {
  "sub": "Pick a CTD module — see its real section skeleton and the TODO count a draft starts with.",
  "type": "map", "pickLabel": "CTD module",
  "options": [
   {"v": "2.3", "label": "2.3 Quality Overview", "h": "2.3 · 5 sections · starts with 5 TODOs",
    "rows": ["2.3.S Drug Substance", "2.3.P Drug Product", "2.3.A Regional info", "2.3.R References", "2.3.Q QOS (regional)"]},
   {"v": "3.2.S", "label": "3.2.S Drug Substance", "h": "3.2.S · 7 sections · starts with 7 TODOs",
    "rows": ["3.2.S.1 General info", "3.2.S.2 Manufacture", "3.2.S.3 Characterisation", "3.2.S.4 Controls", "3.2.S.5 Reference standards", "3.2.S.6 Container closure", "3.2.S.7 Stability"]},
   {"v": "3.2.P", "label": "3.2.P Drug Product", "h": "3.2.P · 7 sections · starts with 7 TODOs",
    "rows": ["3.2.P.1 Description & composition", "3.2.P.2 Pharmaceutical development", "3.2.P.3 Manufacture", "3.2.P.4 Controls (excipients)", "3.2.P.5 Controls (product)", "3.2.P.6 Stability", "3.2.P.7 Container closure"]},
   {"v": "5.3.5", "label": "5.3.5 Clinical literature", "h": "5.3.5 · 4 sections · starts with 4 TODOs",
    "rows": ["5.3.5.1 Biopharmaceutics lit.", "5.3.5.2 PK lit.", "5.3.5.3 PD lit.", "5.3.5.4 Efficacy/safety lit."]}],
  "note": "These skeletons come from the live module templates — the free sample gives you this file with your data mapped in; the paid module is evidence-complete and human-reviewed."},
 "medtech": {
  "sub": "Pick your device class — see what MDR documentation actually applies before you spend a franc.",
  "type": "map", "pickLabel": "MDR class",
  "options": [
   {"v": "I", "label": "Class I", "h": "Class I · 5 workstreams · 1 human sign-off",
    "rows": ["Technical documentation (Annex II)", "Post-market surveillance (Annex III)", "Vigilance registration", "Labeling & IFU", "Declaration of conformity"]},
   {"v": "IIa", "label": "Class IIa", "h": "Class IIa · 7 workstreams · 1 human sign-off",
    "rows": ["Everything in Class I", "Clinical evaluation (Annex XIV)", "Notified-body assessment", "QMS basic requirements"]},
   {"v": "IIb", "label": "Class IIb", "h": "Class IIb · 8 workstreams · 2 human sign-offs",
    "rows": ["Everything in Class IIa", "Full QMS audit readiness", "PMS plan + PMCF plan", "Second sign-off on clinical evidence"]},
   {"v": "III", "label": "Class III", "h": "Class III · 9 workstreams · 2 human sign-offs",
    "rows": ["Everything in Class IIb", "Scrutiny-ready clinical dossier", "PRRC alignment check", "Summary of safety & clinical performance"]}],
  "note": "Indicative mapping, not regulatory advice — the free gap snapshot checks your actual documents against the annexes and numbers every gap."},
 "intelligence": {
  "sub": "List a real process — the classifier that runs our internal market decides what an agent may do and what needs a human or a gate.",
  "type": "classify", "label": "Your process, one step per line",
  "agentKw": ["extract", "parse", "summarize", "draft", "monitor", "scrape", "format",
              "translate", "tag", "classify", "search", "compare", "generate", "collect", "report"],
  "gateKw": ["legal", "medical", "sign", "approve", "file", "submit", "certify", "pay",
             "contract", "regulator", "delete personal"],
  "note": "Same delegation rules as the paid audit (agents draft, humans decide, gates on money/regulator/medical/legal). The audit adds the runbook, cost model and KPI pack per agent."}}

FOUR04 = {
 "growth": ("404. This page's copy tested badly — so we killed it.", "Killing weak assets is the product."),
 "talent": ("404 — this URL doesn't match any role in the dataset.", "The free scan never misses like this."),
 "helix": ("404 · SEQUENCE NOT FOUND", "No contig maps to this path. Frame-checked twice."),
 "verde": ("404 — this page's footprint was measured and it wasn't worth keeping.", "Every byte has a number. This one didn't earn it."),
 "terra": ("404 — uncharted coordinate.", "Our risk maps are honest: nothing verified lives here."),
 "sentinel": ("404 — the edge checked this path and answered honestly.", "Nothing here. That is the correct, verified response."),
 "capitalco": ("404 — written off.", "Discipline, not drama: this path was cut. The compounding continues."),
 "dossia": ("404 · MODULE NOT FOUND", "No CTD section maps to this URL. The template itself is intact."),
 "medtech": ("404 — non-conformity: requested page does not exist.", "CAPA: use the buttons below. Root cause: an old link."),
 "intelligence": ("404 — no agent answered, because nothing lives at this path.", "Humans verified. The classifier is not that dumb."),
}

def four04_html(slug):
    src = (ROOT / slug / "site" / "public" / "index.html").read_text(encoding="utf-8")
    accent = re.search(r'--acc:\s*(#[0-9a-fA-F]{3,8})', src).group(1)
    glow   = accent + '55'
    t = re.search(r'<title>([^<]*)</title>', src).group(1)
    name = re.split(r'[·|—-]', t)[0].strip() or 'CogOps'
    joke, sub = FOUR04[slug]
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark"><meta name="robots" content="noindex">
<title>404 · {name}</title>
<link rel="icon" href="/favicon.svg">
<style>
*{{box-sizing:border-box;margin:0}}
:root{{--accent:{accent};--glow:{glow}}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  background:#0b0e13;color:#e8edf4;min-height:100vh;display:flex;align-items:center;justify-content:center;
  padding:24px;text-align:center}}
.n{{font-size:clamp(90px,22vw,180px);font-weight:800;letter-spacing:-.04em;
  background:linear-gradient(135deg,#fff,var(--accent));-webkit-background-clip:text;background-clip:text;color:transparent;
  animation:pulse 3s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{filter:drop-shadow(0 0 12px var(--glow))}}50%{{filter:drop-shadow(0 0 30px var(--glow))}}}}
h1{{font-size:clamp(18px,3vw,26px);margin:14px 0 8px;font-weight:700}}
p{{color:#93a0b4;max-width:520px;margin:0 auto 26px;line-height:1.6}}
a.b{{display:inline-block;background:var(--accent);color:#0b0e13;font-weight:700;text-decoration:none;
  padding:12px 26px;border-radius:99px;margin:5px;transition:transform .2s,box-shadow .2s}}
a.b:hover{{transform:translateY(-2px);box-shadow:0 10px 30px var(--glow)}}
a.g{{display:inline-block;border:1px solid #232b39;color:#e8edf4;font-weight:600;text-decoration:none;
  padding:12px 26px;border-radius:99px;margin:5px}}
</style></head>
<body><div>
<div class="n">404</div>
<h1>{joke}</h1>
<p>{sub}</p>
<a class="b" href="/">Back to {name}</a>
<a class="g" href="/#try">Try the interactive tool</a>
<a class="g" href="https://cogops-group.pages.dev">The Group</a>
</div></body></html>
"""

def polish(slug):
    d = ROOT / slug / "site" / "public"
    f = d / "index.html"
    s = f.read_text(encoding="utf-8")
    if MARK in s:
        print(f"{slug:12s} already v2")
    else:
        import json as _json
        cfg = CFG[slug]
        widget = WIDGET_HEAD.replace("__SUB__", cfg.pop("sub")).replace("__CFG__", _json.dumps(cfg))
        s = s.replace("</style>", CSS + MARK + "\n</style>", 1)
        s = s.replace("<body>", '<body>\n<a class="skip" href="#main">Skip to content</a>', 1)
        s = re.sub(r'(<body[^>]*>)', r'\1\n<a class="skip" href="#main">Skip to content</a>', s, count=1) if 'class="skip"' not in s else s
        m = re.search(r'[ \t]*<section[^>]*id="signup"', s)
        if m:
            s = s[:m.start()] + widget + s[m.start():]
        else:
            s = s.replace("</main>", widget + "</main>", 1)
        s = s.replace("</body>", f"<script>\n{JS}\n</script>\n</body>", 1)
        f.write_text(s, encoding="utf-8")
        print(f"{slug:12s} pack v2 applied")
    # alias vars so every pack reference resolves against the site's dark theme
    if "ALIAS-VARS" not in s:
        s = s.replace("</style>",
            ":root{/*ALIAS-VARS*/--accent:var(--acc);--muted:var(--dim);--panel:var(--card)}\n</style>", 1)
        f.write_text(s, encoding="utf-8")
        print(f"{slug:12s} alias vars injected")
    (d / "404.html").write_text(four04_html(slug), encoding="utf-8")
    print(f"{slug:12s} 404 rewritten")

for slug in CFG:
    polish(slug)
print("pack v2 done")
