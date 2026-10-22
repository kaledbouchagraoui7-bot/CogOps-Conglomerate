"""Site generator for the K5 clique landings (sentinel/capital/dossia/medtech).
One template, four copies, per-company copy tables. Re-runnable, deterministic.
Usage: python3 tools/clique_sitegen.py   (from repo root)"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS = """:root{--bg:#0b0e14;--ink:#e8edf6;--dim:#9aa7bf;--acc:%ACCENT%;--acc2:#6ea8fe;--line:#222c40;--card:#121a28}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;overflow-x:hidden}
.wrap{max-width:1060px;margin:0 auto;padding:0 20px}a{color:var(--acc2);text-decoration:none}
.blobs{position:fixed;inset:0;z-index:-1;filter:blur(90px);opacity:.5}.blobs i{position:absolute;border-radius:50%}
.blobs i:nth-child(1){width:480px;height:480px;background:%GLOW%;top:-120px;left:-100px}
.blobs i:nth-child(2){width:420px;height:420px;background:#274a7d;top:30%;right:-140px}
nav{position:sticky;top:0;z-index:9;backdrop-filter:blur(14px);background:rgba(11,14,20,.72);border-bottom:1px solid var(--line)}
.navin{display:flex;align-items:center;gap:18px;padding:14px 20px}
.brand{font-weight:800;letter-spacing:.6px}.brand em{color:var(--acc);font-style:normal}
.nlinks{display:flex;gap:16px;margin-left:auto;color:var(--dim);font-size:13.5px}.nlinks a:hover{color:var(--ink)}
.btn{display:inline-block;border:1px solid var(--acc);color:var(--acc);background:transparent;border-radius:99px;padding:9px 18px;font-weight:600;font-size:13.5px;cursor:pointer;transition:.2s}
.btn:hover{background:rgba(255,255,255,.06)}.btn.grad{background:linear-gradient(135deg,%GRADA%,%GRADB%);border:none;color:#fff}
.hero{text-align:center;padding:90px 0 52px}
.badge{display:inline-block;border:1px solid var(--line);background:var(--card);color:var(--acc);border-radius:99px;padding:6px 14px;font-size:12px;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:20px}
h1{font-size:clamp(32px,6vw,54px);line-height:1.08;letter-spacing:-.5px}
h1 em{font-style:normal;background:linear-gradient(120deg,var(--acc),var(--acc2));-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--dim);max-width:680px;margin:18px auto 30px;font-size:17px}
.counter{color:#ffcf6e;font-size:13.5px;margin-top:14px;min-height:20px}
.linkband{border:1px solid var(--line);background:var(--card);border-radius:14px;padding:13px 20px;color:var(--dim);font-size:13px;text-align:center}
.linkband b{color:var(--acc)}
.grade{border:1px solid #6b561f;background:#3a2f14;color:#ffcf6e;border-radius:12px;padding:11px 18px;font-size:13px;max-width:780px;margin:0 auto}
form.signup{max-width:560px;margin:0 auto;display:grid;gap:10px;text-align:left}
form.signup .row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
input,select,textarea{width:100%;background:var(--card);border:1px solid var(--line);color:var(--ink);border-radius:10px;padding:12px 14px;font:inherit}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--acc)}
.hp{position:absolute;left:-9999px}.msg{min-height:22px;font-size:14px;text-align:center;margin-top:8px}.msg.ok{color:var(--acc)}.msg.bad{color:#ff8f8f}
section{padding:56px 0}.eyebrow{color:var(--acc);font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px}
h2{font-size:clamp(24px,3.6vw,32px);margin-bottom:22px;letter-spacing:-.3px}
.grid{display:grid;gap:16px}.g3{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px}
.card h3{font-size:17px;margin:8px 0}.card p{color:var(--dim);font-size:14px}.num{color:var(--acc);font-weight:800;font-size:13px}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid var(--line);font-size:14px}
th{color:var(--acc);font-size:12px;letter-spacing:1px;text-transform:uppercase}td:last-child,th:last-child{text-align:right}
.faq details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:15px 20px;margin-bottom:10px}
.faq summary{cursor:pointer;font-weight:600}.faq p{color:var(--dim);margin-top:10px;font-size:14px}
footer{border-top:1px solid var(--line);color:var(--dim);font-size:13px;padding:32px 0;text-align:center}
.marquee{border-top:1px solid var(--line);border-bottom:1px solid var(--line);overflow:hidden;padding:12px 0;background:rgba(18,26,40,.5)}
.mtrack{display:flex;gap:48px;white-space:nowrap;animation:mv 30s linear infinite;color:var(--dim);font-size:13px;width:max-content}
.mtrack span b{color:var(--acc)}@keyframes mv{to{transform:translateX(-50%)}}
.rv{opacity:0;transform:translateY(18px);transition:.6s}.rv.in{opacity:1;transform:none}
@media(max-width:640px){.nlinks{display:none}form.signup .row{grid-template-columns:1fr}}
@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important}.rv{opacity:1;transform:none}}"""

TPL = open(os.path.join(ROOT, "tools", "clique_template.html"), encoding="utf-8").read()

CLIQUE = {"helix": "Helix", "dossia": "Dossia", "medtech": "Medtech",
          "sentinel": "Sentinel", "capitalco": "Capital"}

DOM = {"capitalco": "capital"}

def dom_of(slug):
    return DOM.get(slug, slug)

def clique_links(me):
    return " · ".join(f'<a href="https://cogops-{dom_of(k)}.pages.dev">{v}</a>'
                      for k, v in CLIQUE.items() if k != me)

COMPANIES = json.load(open(os.path.join(ROOT, "tools", "clique_copy.json"), encoding="utf-8"))

def build():
    for slug, c in COMPANIES.items():
        css = (CSS.replace("%ACCENT%", c["accent"])
                  .replace("%GLOW%", "#%02x%02x%02x" % tuple(c["glow"]))
                  .replace("%GRADA%", c["grada"]).replace("%GRADB%", c["gradb"]))
        marquee = "".join(f"<span>{m}</span>" for m in c["marquee"])
        scards = "".join(f'<div class="card rv"><div class="num">{n}</div><h3>{t}</h3><p>{p}</p></div>'
                         for n, t, p in c["services"])
        bcards = "".join(f'<div class="card rv"><div class="num">B{i:02d}</div><h3>{t}</h3><p>{p}</p></div>'
                         for i, (t, p) in enumerate(c["boundary"], 1))
        prows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{p}</td></tr>" for a, b, p in c["prices"])
        opts = "".join(f"<option>{o}</option>" for o in c["product_options"])
        faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in c["faq"])
        fields = dict(name=f"CogOps {c['word']}", word=c["word"], slug=slug, dom=dom_of(slug),
            tagline=c["tagline"], metadesc=c["metadesc"], css=css, jsonld=c["jsonld"],
            badge=c["badge"], h1a=c["h1a"], h1b=c["h1b"], sub=c["sub"],
            boundary_band=c["boundary_band"], cta=c["cta"], services_h2=c["services_h2"],
            service_cards=scards, boundary_cards=bcards, price_rows=prows,
            pricing_note=c["pricing_note"], form_h2=c["form_h2"], form_btn=c["form_btn"],
            product_options=opts, icp_ph=c["icp_ph"], sla_line=c["sla_line"],
            sla_line_short=c["sla_line_short"], counter_emoji=c["counter_emoji"],
            counter_one=c["counter_one"], counter_many=c["counter_many"],
            marquee=marquee, faq=faq, clique_links=clique_links(slug))
        html = TPL
        for k, v in fields.items():
            html = html.replace("{" + k + "}", str(v))
        out = os.path.join(ROOT, slug, "site", "public", "index.html")
        open(out, "w", encoding="utf-8").write(html)
        print(f"{slug}: {len(html)} bytes -> {out}")

if __name__ == "__main__":
    build()
