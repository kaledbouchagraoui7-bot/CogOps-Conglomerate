"""build_single.py — fold the generated vault pages into ONE self-contained
HTML file (tabs, inline CSS/JS, no network). For founder-only viewing in the
workspace viewer / offline; the hosted multi-page build stays the source of
truth for the eventual cogops-vault.pages.dev deploy."""
from __future__ import annotations

import re
from pathlib import Path

import build_vault as bv

PUB = Path(__file__).resolve().parent / "site" / "public"
OUT = Path(__file__).resolve().parent / "vault-single-file.html"

SECTIONS = [("index", "Overview"), ("tree", "Path structure"), ("ai", "AI & OS"),
            ("decisions", "Decisions"), ("companies", "Companies"),
            ("analysis", "Analyst"), ("actions", "Action kit")]

tabs, bodies = [], []
for key, label in SECTIONS:
    txt = (PUB / f"{key}.html").read_text(encoding="utf-8")
    m = re.search(r"<main>(.*)</main>", txt, re.S)
    inner = m.group(1)
    # neutralize internal nav hrefs (single-file: switch tabs instead)
    inner = re.sub(r'href="([a-z]+)\.html"', r'href="#\1" data-tab="\1"', inner)
    tabs.append(f'<button data-tab="{key}" class="tb">{label}</button>')
    bodies.append(f'<section id="sec-{key}" class="sec">{inner}</section>')

js = """
function show(id){document.querySelectorAll('.sec').forEach(s=>s.style.display=s.id==='sec-'+id?'block':'none');
document.querySelectorAll('.tb').forEach(b=>b.style.color=b.dataset.tab===id?'var(--acc)':'var(--dim)');
location.hash=id;window.scrollTo(0,0);}
document.querySelectorAll('[data-tab]').forEach(e=>e.addEventListener('click',ev=>{ev.preventDefault();show(e.dataset.tab);}));
show((location.hash||'#index').slice(1).replace('sec-',''));
if(!document.querySelector('.sec[style*="block"]'))show('index');
"""

html_out = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<meta name="robots" content="noindex,nofollow">'
    '<title>CogOps Vault — founder-only</title>'
    f'<style>{bv.CSS}'
    'nav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);'
    'padding:12px 20px;display:flex;gap:6px;flex-wrap:wrap;z-index:9}'
    '.tb{background:none;border:1px solid var(--line);border-radius:99px;color:var(--dim);'
    'padding:6px 14px;font:inherit;font-size:13px;cursor:pointer}'
    '.sec{display:none;max-width:1060px;margin:0 auto;padding:24px}'
    '.gate{max-width:420px;margin:14vh auto;padding:18px;background:var(--card);'
    'border:1px solid var(--line);border-radius:14px}'
    '</style></head><body>'
    '<div id="gate" class="gate"><h1 style="font-size:20px">CogOps Vault</h1>'
    '<p>Founder-only. This copy lives in your private workspace/repo; the hosted '
    'copy adds an edge password gate.</p>'
    '<input id="p" type="password" placeholder="vault password" style="width:100%;background:var(--bg);'
    'border:1px solid var(--line);color:var(--ink);border-radius:10px;padding:12px;font:inherit">'
    '<button id="go" style="margin-top:10px;width:100%;background:var(--acc);color:#06110b;border:0;'
    'border-radius:10px;padding:12px;font:inherit;font-weight:700;cursor:pointer">open</button>'
    '<p id="e" style="color:var(--warn)"></p></div>'
    '<div id="app" style="display:none"><nav>' + "".join(tabs) +
    '<span class="pill" style="margin-left:auto;align-self:center">founder-only</span></nav>'
    + "".join(bodies) + '</div>'
    '<script>const H="40ca14c17f1577860311205b6e4de544f24618cd2c847222833a6a7f292ae9c9";'
    'async function sha(s){const b=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s));'
    'return[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("");}'
    'const open=async()=>{if(sessionStorage.getItem("vault")==="1"){enter();return;}'
    'const v=document.getElementById("p").value;'
    'if(await sha(v)===H){sessionStorage.setItem("vault","1");enter();}else{document.getElementById("e").textContent="denied";}};'
    'function enter(){document.getElementById("gate").style.display="none";'
    'document.getElementById("app").style.display="block";' + js + '};'
    'document.getElementById("go").onclick=open;'
    'document.getElementById("p").addEventListener("keydown",e=>{if(e.key==="Enter")open();});'
    'if(sessionStorage.getItem("vault")==="1")enter();'
    '</script></body></html>')

OUT.write_text(html_out, encoding="utf-8")
print("single-file vault:", OUT.stat().st_size, "bytes")
