"""CogOps Growth — the revenue engine (OS §13; blueprint co. 9).

State-of-the-art at solo+AI scale: the two live JARVIS products as code —
validated lead enrichment with per-prospect copy, and a programmatic-SEO page
factory with sitemap emission — plus the domain media network (Levelsio
"audience-as-platform": distribution is built BEFORE company #2 launches).
"""
from __future__ import annotations

import csv
import hashlib
import io
import re
import unicodedata

import config
import ledger
import llm

META = {
    "name": "CogOps Growth",
    "dan": "Every company here (and external SMEs) gets pipeline: validated "
           "decision-maker data, per-prospect copy, and pages that rank.",
    "stage_at_v10": 2,
    "seed_assets": "JARVIS lead-enrichment + pSEO products (live pricing)",
    "human_of_record": "founder",
    "input_metrics": [
        {"key": "validated_leads_month", "layer": "F", "owner": "data-validator", "floor": 50},
        {"key": "pages_ranking", "layer": "F", "owner": "seo-page-factory", "floor": 10},
        {"key": "newsletter_subs_per_domain", "layer": "F", "owner": "newsletter-composer", "floor": 100},
    ],
    "squad_roles": ["lead-researcher", "data-validator", "copywriter-personalization",
                    "seo-page-factory", "newsletter-composer", "funnel-analyst"],
}

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
DISPOSABLE = {"mailinator.com", "guerrillamail.com", "tempmail.com", "yopmail.com",
              "10minutemail.com", "trashmail.com"}


def _slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def enrich_leads(params: dict, slug: str) -> dict:
    """Pipeline: parse → validate → dedupe → score → per-prospect copy.
    Input: {"csv": "name,email,company,role,note\\n..."} (rows from the
    lead-researcher). Output artifacts land in outbox/; every row carries its
    validation evidence (CBS Ch.3). Copy is LLM-drafted with an honest
    template fallback — never faked."""
    raw = params.get("csv", "")
    rows = list(csv.DictReader(io.StringIO(raw)))
    seen, out, rejected = set(), [], []
    for r in rows:
        email = (r.get("email") or "").strip().lower()
        rec = {**r, "email": email}
        problems = []
        if not EMAIL_RE.match(email):
            problems.append("malformed_email")
        else:
            dom = email.split("@")[1]
            if any(dom == d or dom.endswith("." + d) for d in DISPOSABLE):
                problems.append("disposable_domain")   # subdomains covered
        if email in seen:
            problems.append("duplicate")
        seen.add(email)
        rec["valid"] = not problems
        rec["problems"] = problems
        rec["score"] = _score(rec)
        (out if rec["valid"] else rejected).append(rec)
    copies = []
    for rec in out[: params.get("copy_limit", 5)]:
        copies.append(_prospect_copy(rec, slug))
    reject_counts: dict = {}
    for r in rejected:
        for p in r["problems"]:
            reject_counts[p] = reject_counts.get(p, 0) + 1
    artifact = {"mode": copies[0]["mode"] if copies else "engine",
                "valid_leads": len(out), "rejected": len(rejected),
                "rejection_reasons": reject_counts,
                "leads": out, "copies": copies,
                "asof": config.today()}
    _emit(slug, "enrichment", artifact)
    return artifact


def _score(rec: dict) -> int:
    s = 0
    if rec.get("role"):
        s += 2                      # decision-maker signal
    if rec.get("company"):
        s += 1
    if rec.get("note") and len(rec["note"]) > 40:
        s += 2                      # researched context present
    return min(s, 5)


def _prospect_copy(rec: dict, slug: str = "growth") -> dict:
    facts = (f"prospect={rec.get('name')} role={rec.get('role')} "
             f"company={rec.get('company')} note={rec.get('note', '')[:200]}")
    try:
        out = llm.generate(
            f"Write ONE hyper-personalized cold-email opener (≤60 words, no "
            f"flattery, concrete) using only these facts:\n{facts}",
            system="You write B2B outreach for CogOps Growth. Grounded facts only.",
            company=slug)
        return {"email": rec["email"], "copy": out["text"], "mode": out["mode"]}
    except llm.LLMUnavailable:
        tmpl = (f"Hi {rec.get('name', 'there')} — saw {rec.get('company', 'your team')} "
                f"is working on { (rec.get('note') or 'your space') [:60] }. We run the "
                f"enrichment/pSEO engine behind jarvis-8wr.pages.dev; happy to send a "
                f"sample batch for {rec.get('company', 'you')}.")
        return {"email": rec["email"], "copy": tmpl, "mode": "template"}


def pseo_pages(params: dict, slug: str) -> dict:
    """Programmatic-SEO factory (JARVIS product #2): data rows × template →
    long-tail pages + sitemap fragment. Deterministic: same input ⇒ byte-
    identical pages (FROZEN clock)."""
    rows = params.get("rows", [])
    tmpl = params.get("template",
                      "# {title}\n\n{intro}\n\n| key | value |\n|---|---|\n{table}\n")
    base = params.get("base_url", "https://example.cogops.group")
    pages, sitemap = [], []
    for r in rows:
        title = r.get("title") or r.get("key", "untitled")
        table = "\n".join(f"| {k} | {v} |" for k, v in r.items()
                          if k not in ("title", "intro", "key"))
        body = tmpl.format(title=title, intro=r.get("intro", ""), table=table)
        ps = _slug(title)
        pages.append({"path": f"/p/{ps}.md", "content": body,
                      "hash": hashlib.sha256(body.encode()).hexdigest()[:12]})
        sitemap.append(f"{base}/p/{ps}.html")
    sm = ("<?xml version=\"1.0\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
          + "".join(f"  <url><loc>{u}</loc><changefreq>weekly</changefreq></url>\n"
                    for u in sitemap) + "</urlset>\n")
    artifact = {"mode": "engine", "pages_built": len(pages), "pages": pages,
                "sitemap": sm, "asof": config.today()}
    _emit(slug, "pseo", {"mode": "engine", "pages_built": len(pages),
                         "sitemap_urls": len(sitemap)})
    return artifact


def newsletter_issue(params: dict, slug: str) -> dict:
    """Domain journal issue (media network): items → composed issue, LLM-drafted
    editorial with template fallback."""
    domain = params.get("domain", "general")
    items = params.get("items", [])
    body_items = "\n".join(f"- **{i.get('title', 'item')}** — {i.get('summary', '')}"
                           for i in items)
    try:
        ed = llm.generate(f"Write a 3-sentence editor's note for the {domain} "
                          f"journal issue covering:\n{body_items}", company=slug)
        ed_txt, mode = ed["text"], ed["mode"]
    except llm.LLMUnavailable:
        ed_txt, mode = f"This issue of the {domain} journal: {len(items)} items.", "template"
    issue = (f"# CogOps {domain.title()} Journal — {config.today()}\n\n"
             f"_{ed_txt}_ ({mode})\n\n{body_items}\n")
    artifact = {"mode": mode, "domain": domain, "items": len(items),
                "issue_md": issue, "asof": config.today()}
    _emit(slug, f"newsletter_{domain}", artifact)
    return artifact


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    import json
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")
    ledger.event("growth_artifact", slug, {"kind": kind, "file": p.name})


def lead_report_html(params: dict, slug: str) -> dict:
    """The client-facing deliverable: branded HTML lead-batch report from the
    theme system (data/theme.json — the code reads the brand, never hardcodes
    it). Carries per-record validation evidence and a content-hash version
    stamp (roadmap: version history for every deliverable)."""
    import json as _json
    enrichment = params.get("enrichment") or enrich_leads(params, slug)
    client = params.get("client", "Client")
    theme = _json.loads((config.ROOT / "data" / "theme.json").read_text(encoding="utf-8"))
    gr, co = theme["group"], theme["companies"]["growth"]
    rows = "".join(
        f"<tr><td>{r.get('name','')}</td><td>{r['email']}</td><td>{r.get('company','')}</td>"
        f"<td>{r.get('role','')}</td><td>{r['score']}/5</td><td>✓ {'; '.join(r['problems']) or 'clean'}</td></tr>"
        for r in enrichment["leads"])
    copies = "".join(f"<div class=copy><b>{c['email']}</b> <span class=mode>({c['mode']})</span>"
                     f"<p>{c['copy']}</p></div>" for c in enrichment.get("copies", []))
    body = (f"<!DOCTYPE html><html><head><meta charset=utf-8><title>Lead batch — {client}</title>"
            f"<style>body{{background:{gr['bg']};color:{gr['ink']};font:14px/1.6 {gr['font']};padding:32px}}"
            f".wrap{{max-width:860px;margin:0 auto}}h1{{color:{co['accent']};font-size:22px}}"
            f".badge{{display:inline-block;border:1px solid {gr['line']};color:{co['accent']};border-radius:99px;padding:4px 12px;font-size:11px;letter-spacing:1px}}"
            f"table{{width:100%;border-collapse:collapse;margin:18px 0}}td,th{{padding:8px 10px;border-bottom:1px solid {gr['line']};text-align:left;font-size:13px}}"
            f"th{{color:{co['accent']};font-size:11px;text-transform:uppercase;letter-spacing:1px}}"
            f".copy{{background:{gr['surface']};border:1px solid {gr['line']};border-radius:10px;padding:12px 16px;margin:8px 0}}"
            f".mode{{color:{gr['dim']};font-size:11px}}.foot{{color:{gr['dim']};font-size:12px;margin-top:24px;border-top:1px solid {gr['line']};padding-top:12px}}"
            f".rej{{color:{gr['warn']}}}</style></head><body><div class=wrap>"
            f"<span class=badge>COGOPS GROWTH · a CogOps Group company</span>"
            f"<h1>Validated lead batch — {client}</h1>"
            f"<p>Generated {config.stamp()} · {enrichment['valid_leads']} validated · "
            f"<span class=rej>{enrichment['rejected']} rejected</span> "
            f"({', '.join(f'{k}: {v}' for k, v in enrichment['rejection_reasons'].items()) or 'none'})</p>"
            f"<table><tr><th>Name</th><th>Email</th><th>Company</th><th>Role</th><th>Score</th><th>Validation</th></tr>{rows}</table>"
            f"<h2 style='color:{co['accent']};font-size:16px>Per-prospect openers <span class=mode>(human review required before any send)</span></h2>{copies}"
            f"<div class=foot>Every record carries its validation evidence (format check, dedupe, disposable-domain screen). "
            f"Delivery version stamp: <b>{{HASH}}</b> · CogOps Growth · cogops.engine@gmail.com · "
            f"Deletion/objection honoured within 30 days (nFADP/GDPR).</div></div></body></html>")
    import hashlib
    h = hashlib.sha256(body.encode()).hexdigest()[:16]
    body = body.replace("{HASH}", h)
    p = config.OUTBOX / f"growth_lead_report_{client.lower().replace(' ', '_')}_{config.today()}_{h[:8]}.html"
    p.write_text(body, encoding="utf-8")
    ledger.event("growth_deliverable", slug, {"client": client, "version": h,
                                              "leads": enrichment["valid_leads"]})
    return {"mode": "engine", "html_file": p.name, "version_hash": h,
            "leads": enrichment["valid_leads"], "rejected": enrichment["rejected"],
            "client": client, "asof": config.today()}


TASKS = {
    "enrich_leads": {"fn": enrich_leads, "role": "data-validator"},
    "lead_report_html": {"fn": lead_report_html, "role": "copywriter-personalization"},
    "pseo_pages": {"fn": pseo_pages, "role": "seo-page-factory"},
    "newsletter_issue": {"fn": newsletter_issue, "role": "newsletter-composer"},
}
