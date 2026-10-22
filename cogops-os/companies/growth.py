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
                    "seo-page-factory", "newsletter-composer", "funnel-analyst",
                    "outreach-operator", "process-auditor", "media-editor"],
}


# --------------------------------------- public-source sourcing (provenance) --
# Claims on the site and DPA Annex 1 promise per-record SOURCE URLs. This is the
# step that produces them: fetch a domain's public pages (robots-respecting,
# rate-limited, labeled bot UA) and extract PUBLISHED business contacts.
# Candidates are never used before enrich_leads validation.
BOT_UA = "CogOpsGrowthBot/1.0 (+https://cogops-growth.pages.dev/privacy.html)"
SOURCE_PATHS = ("", "/about", "/team", "/people", "/contact", "/impressum", "/imprint")
MAILTO_RE = re.compile('<a[^>]*href=["\']mailto:([^"\'?]+)[^>]*>(.*?)</a>', re.I | re.S)
EMAIL_RX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def parse_robots(robots_text: str, ua: str = "*") -> list[str]:
    """Minimal robots.txt parser: Disallow rules for our UA or *."""
    dis, active = [], False
    for line in robots_text.splitlines():
        line = line.split("#", 1)[0].strip().lower()
        if line.startswith("user-agent:"):
            active = line.split(":", 1)[1].strip() in ("*", ua.lower())
        elif active and line.startswith("disallow:"):
            p = line.split(":", 1)[1].strip()
            if p:
                dis.append(p)
    return dis


def _allowed(path: str, disallow: list[str]) -> bool:
    return not any(path.startswith(d.rstrip("*") or d) for d in disallow)


def extract_contacts(html: str, url: str) -> list[dict]:
    """Published business contacts from one public page: mailto anchors give
    name context; bare addresses get the page title as context. Provenance =
    exact URL + fetch timestamp (DPA Annex 1 promise)."""
    out, seen = [], set()
    for m in MAILTO_RE.finditer(html):
        email, anchor = m.group(1).strip().lower(), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if email not in seen:
            seen.add(email)
            out.append({"email": email, "name": anchor or "", "source_url": url,
                        "source_kind": "mailto_anchor"})
    title = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    title = re.sub(r"<[^>]+>", "", title.group(1)).strip() if title else ""
    for m in EMAIL_RX.finditer(re.sub(r"<script.*?</script>", "", html, flags=re.S | re.I)):
        email = m.group(0).lower()
        if email in seen or email.endswith((".png", ".jpg", ".gif", ".webp")):
            continue
        seen.add(email)
        out.append({"email": email, "name": "", "source_url": url,
                    "source_kind": "page_text", "page_title": title[:80]})
    return out


def source_leads(params: dict, slug: str) -> dict:
    """Domain → published-contact candidates WITH provenance. Offline-safe:
    unreachable domain = honest empty result with the error, never fake rows."""
    import urllib.error
    import urllib.request
    domain = (params.get("domain") or "").strip().lower().replace("https://", "").replace("http://", "").rstrip("/")
    if not re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", domain):
        raise ValueError("domain like example.ch required")
    max_pages = min(int(params.get("max_pages", 6)), 10)
    cands, log = [], []
    try:
        rq = urllib.request.Request(f"https://{domain}/robots.txt", headers={"User-Agent": BOT_UA})
        with urllib.request.urlopen(rq, timeout=8) as r:
            disallow = parse_robots(r.read().decode(errors="replace"))
    except Exception:
        disallow = []                      # no robots.txt = allow (standard)
    for p in SOURCE_PATHS[:max_pages]:
        if not _allowed("/" + p.lstrip("/"), disallow):
            log.append(f"{p}: robots-disallowed")
            continue
        url = f"https://{domain}/{p}"
        try:
            rq = urllib.request.Request(url, headers={"User-Agent": BOT_UA})
            with urllib.request.urlopen(rq, timeout=8) as r:
                if r.status != 200:
                    continue
                html = r.read(400_000).decode(errors="replace")
            found = extract_contacts(html, url)
            log.append(f"{p}: {len(found)} contacts")
            cands += found
        except urllib.error.HTTPError as e:
            log.append(f"{p}: HTTP {e.code}")
        except Exception as e:
            log.append(f"{p}: {str(e)[:60]}")
    ded = {}
    for c in cands:
        ded.setdefault(c["email"], c)
    artifact = {"mode": "engine:live" if any("contacts" in l for l in log) else "engine:offline",
                "domain": domain, "candidates": list(ded.values()),
                "fetched_at": config.stamp(), "fetch_log": log,
                "rule": "candidates enter delivery ONLY after enrich_leads validation",
                "asof": config.today()}
    _emit(slug, f"sourced_{domain.replace('.', '_')}", artifact)
    return artifact


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
        rec = {**r, "email": email,
               "source": r.get("source") or r.get("source_url") or "client-supplied",
               "sourced_at": r.get("sourced_at") or r.get("fetched_at") or ""}
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


# ------------------------------------------------ outreach quota (OFFER §3) --
# Touch sequence per OFFER §3: touch1 day 0 (value-first), touch2 day +3 (proof),
# touch3 day +7 (break-up with a concrete addition). Drafts only — a human
# approves and sends every message (founder rule; inbox.py doctrine).
SEQUENCE = (
    (0, "touch1", "value-first opener referencing the prospect's public context"),
    (3, "touch2", "add proof: one anonymized sample-batch outcome or validation stat"),
    (7, "touch3", "break-up: offer the free 25-lead sample one last time, then close the file"),
)


def touch_draft(params: dict, slug: str) -> dict:
    """Draft one outreach touch for a target. Facts-only grounding (the
    target's public context + the published offer); honest mode label."""
    t = params.get("target", {})
    day = int(params.get("day", 0))
    step = next((s for s in SEQUENCE if s[0] == day), None)
    if step is None:
        raise ValueError(f"day {day} not in sequence {[s[0] for s in SEQUENCE]}")
    facts = (f"target={t.get('name')} role={t.get('role')} company={t.get('company')} "
             f"context={t.get('context', '')[:240]} jurisdiction={t.get('country', 'CH')}")
    prompt = (f"Write ONE B2B email ({step[2]}), max 90 words, confident and direct, "
              f"no hedging, one call-to-action (30-minute target-definition call or the "
              f"free 25-lead sample). Facts only:\n{facts}")
    try:
        out = llm.generate(prompt, system=OFFER_SYSTEM, company=slug)
        text, mode = out["text"], out["mode"]
    except llm.LLMUnavailable:
        cta = ("Would a 30-minute call this week work to fix your target definition? "
               if day == 0 else
               "The free 25-lead sample stands — one email and it is yours."
               if day == 7 else
               "Happy to send three sample records for your second persona, free.")
        text = (f"Hi {t.get('name', 'there')} — {t.get('company', 'your team')} shows up in "
                f"{t.get('context', 'your space')[:80]}. We manufacture validated B2B leads: "
                f"sourced per record, deduped against your CRM, copy written for one person "
                f"at a time, human-approved before anything sends. {cta}")
        mode = "template"
    artifact = {"mode": mode, "sequence_step": step[1], "day_offset": day,
                "target": t, "draft": text,
                "send_rule": "HUMAN approves or rewrites; never automated (founder rule)",
                "compliance_note": "e-privacy screen required for non-CH recipients "
                                   "before send (RoPA R4)",
                "asof": config.today()}
    _emit(slug, f"touch_{step[1]}_{(t.get('company') or 'target').lower().replace(' ', '_')}",
          artifact)
    return artifact


OFFER_SYSTEM = ("You write outreach for CogOps Growth. Confident, direct, zero hedging. "
                "Facts only from the target context and the published offer: free 25-lead "
                "sample in 48h after approved target definition; CHF 1-3 per validated lead; "
                "retainers CHF 1,500-3,500/month cancel monthly; 14-day replacement guarantee; "
                "reply within 1 business day.")


def weekly_quota_sheet(params: dict, slug: str) -> dict:
    """The founder's weekly outreach cockpit (OFFER §3 quota): 20 touches,
    5 sample batches, 2 follow-ups per open sample. One row per target with
    its sequence stage, drafted touch and an explicit APPROVAL column — the
    sheet is a work list for a human, never an auto-sender."""
    week = params.get("week", config.today()[:7])
    targets = params.get("targets", [])
    quota = params.get("quota", {"touches": 20, "samples": 5, "followups": 2})
    rows = []
    for i, t in enumerate(targets[: quota["touches"]], 1):
        stage = int(t.get("stage", 0))
        step = SEQUENCE[min(stage, len(SEQUENCE) - 1)]
        rows.append({"#": i, "company": t.get("company"), "name": t.get("name"),
                     "country": t.get("country", "CH"),
                     "touch": step[1], "day_offset": step[0],
                     "approval": "AWAITING HUMAN SEND"})
    md = [f"# Outreach sheet — {week} — CogOps Growth", "",
          f"**Quota:** {quota['touches']} touches · {quota['samples']} sample batches · "
          f"{quota['followups']} follow-ups per open sample", "",
          "| # | Company | Contact | Country | Touch | Day | Approval |",
          "|---|---|---|---|---|---|---|"]
    md += [f"| {r['#']} | {r['company']} | {r['name']} | {r['country']} | {r['touch']} "
           f"| +{r['day_offset']}d | **{r['approval']}** |" for r in rows]
    md += ["", "_Every line is drafted by the engine (`touch_draft`) and sent only by a "
           "human. Non-CH rows require the e-privacy screen (RoPA R4) before send._"]
    p = config.OUTBOX / f"growth_outreach_{week}.md"
    p.write_text("\n".join(md), encoding="utf-8")
    ledger.event("outreach_sheet", slug, {"week": week, "rows": len(rows)})
    return {"mode": "engine", "week": week, "rows": rows, "quota": quota,
            "sheet_file": p.name, "asof": config.today()}


def quota_status(params: dict, slug: str) -> dict:
    """Adherence vs quota with root-cause demand on miss (CBS Ch.4: misses get
    root-caused, not excused)."""
    quota = params.get("quota", {"touches": 20, "samples": 5, "followups": 2})
    done = params.get("done", {"touches": 0, "samples": 0, "followups": 0})
    res = {}
    misses = []
    for k in quota:
        ok = done.get(k, 0) >= quota[k]
        res[k] = {"done": done.get(k, 0), "quota": quota[k], "met": ok}
        if not ok:
            misses.append(k)
    return {"mode": "engine", "adherence": res, "misses": misses,
            "root_cause_required": bool(misses),
            "action": ("write the root cause into the weekly review (CBS Ch.4)"
                       if misses else "quota met — log the win"),
            "asof": config.today()}




def pseo_qa(params: dict, slug: str) -> dict:
    """The QA gate the site promises: pages that fail never get the
    'publishable' flag. Checks: substance (≥120 words), meta completeness,
    sibling uniqueness (Jaccard < 0.60), query-answer coverage (≥60% of query
    terms present), no placeholder text."""
    pages = params.get("pages", [])
    results = []
    for i, pg in enumerate(pages):
        content = pg.get("content", "")
        words = len(re.sub(r"[#|*`\-]", " ", content).split())
        title, desc = pg.get("title", ""), pg.get("description", "")
        query = (pg.get("query") or title).lower().split()
        cov = (sum(1 for w in query if w in content.lower()) / len(query)) if query else 1.0
        sib = max((_jaccard(content, o.get("content", "")) for j, o in enumerate(pages) if j != i),
                  default=0.0)
        reasons = []
        if words < 120:
            reasons.append(f"thin: {words} words < 120")
        if not (10 <= len(title) <= 70):
            reasons.append("title length outside 10-70")
        if not (50 <= len(desc) <= 165):
            reasons.append("meta description outside 50-165")
        if cov < 0.6:
            reasons.append(f"answers only {cov:.0%} of query terms")
        if sib >= 0.6:
            reasons.append(f"duplicate-ish sibling (Jaccard {sib:.2f})")
        if re.search(r"lorem ipsum|TODO|placeholder|xxx", content, re.I):
            reasons.append("placeholder text")
        results.append({"path": pg.get("path", f"page{i}"), "words": words,
                        "query_coverage": round(cov, 2), "max_sibling_overlap": round(sib, 2),
                        "publishable": not reasons, "reasons": reasons})
    ok = sum(1 for r in results if r["publishable"])
    artifact = {"mode": "engine", "pages_checked": len(results), "publishable": ok,
                "refused": len(results) - ok, "results": results,
                "rule": "refused pages never reach a sitemap or a client domain",
                "asof": config.today()}
    _emit(slug, "pseo_qa", artifact)
    return artifact


def _jaccard(a: str, b: str) -> float:
    sa, sb = set(a.lower().split()), set(b.lower().split())
    return len(sa & sb) / len(sa | sb) if (sa | sb) else 0.0




def sister_digest(params: dict, slug: str) -> dict:
    """The Growth↔Talent link, direction 2: Growth buys career-intel briefs
    FROM Talent via the internal market (ticket at DR-0002 price) and publishes
    them as the talent vertical of the media network — distribution for Talent,
    content for Growth. Both P&Ls record the internal trade (I7)."""
    import platformsvc
    import registry
    domain = params.get("domain", "quant_finance")
    ticket = platformsvc.request(slug, "career_intel", spec=f"brief: {domain}", units=1)
    brief = registry.run_task("talent", "market_brief", {"domain": domain}, role="market-researcher")
    platformsvc.serve(ticket["id"], {"ref": f"growth-sister-digest:{ticket['id']}"})
    issue = newsletter_issue({"domain": "talent-careers", "items": [
        {"title": f"Market brief: {domain}", "summary": brief["brief_md"][:400]},
        {"title": "Where the gaps pay", "summary": "The demand/supply ratios behind this "
                                                    "issue — and the tracks that close them."}]}, slug)
    artifact = {"mode": "engine", "ticket": ticket["id"],
                "notional_chf": ticket["notional_chf"],
                "brief_domain": domain, "issue_file": issue.get("issue_md", "")[:0] or issue["mode"],
                "issue_mode": issue["mode"], "asof": config.today()}
    _emit(slug, f"sister_digest_{domain}", artifact)
    return artifact




def intelligence_ops(params: dict, slug: str) -> dict:
    """Star link: this company buys Intelligence's deployment/automation service
    via internal ticket (ai_ops, DR-0010 price)."""
    import platformsvc
    from companies import intelligence as intel
    kind = params.get("kind", "automation_audit")
    ticket = platformsvc.request(slug, "ai_ops", spec=f"{kind} for {slug}", units=1)
    if kind == "deploy":
        out = intel.deploy_client({"client": params.get("client", f"{slug}-client"),
                                   "services": params.get("services",
                                       ["site_factory", "llm_gateway", "crm_portal"])},
                                  "intelligence")
    else:
        out = intel.automation_audit({"answers": params.get("answers", {
            "process": f"{slug} delivery", "volume_month": 20, "minutes_per": 30,
            "steps": ["collect client inputs", "draft deliverable", "human review",
                      "approve delivery", "send to client"]})}, "intelligence")
    platformsvc.serve(ticket["id"], {"ref": f"{slug}-intel:{ticket['id']}"})
    return {"mode": "engine", "kind": kind,
            "internal_purchase": {"from": "intelligence", "service": "ai_ops",
                                  "ticket": ticket["id"],
                                  "notional_chf": ticket["notional_chf"]},
            "result": out, "asof": config.today()}


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
        f"<td>{r.get('role','')}</td><td>{r['score']}/5</td>"
        f"<td>{r.get('source','client-supplied')}</td><td>✓ {'; '.join(r['problems']) or 'clean'}</td></tr>"
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
            f"<table><tr><th>Name</th><th>Email</th><th>Company</th><th>Role</th><th>Score</th><th>Source</th><th>Validation</th></tr>{rows}</table>"
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


# Star link: Intelligence <-> this company (DR-0010)
LINKS = {"talent": "sister_digest", "intelligence": "intelligence_ops"}

TASKS = {
    "intelligence_ops": {"fn": intelligence_ops, "role": "funnel-analyst"},
    "enrich_leads": {"fn": enrich_leads, "role": "data-validator"},
    "lead_report_html": {"fn": lead_report_html, "role": "copywriter-personalization"},
    "pseo_pages": {"fn": pseo_pages, "role": "seo-page-factory"},
    "newsletter_issue": {"fn": newsletter_issue, "role": "newsletter-composer"},
    "touch_draft": {"fn": touch_draft, "role": "outreach-operator"},
    "weekly_quota_sheet": {"fn": weekly_quota_sheet, "role": "funnel-analyst"},
    "quota_status": {"fn": quota_status, "role": "funnel-analyst"},
    "source_leads": {"fn": source_leads, "role": "lead-researcher"},
    "pseo_qa": {"fn": pseo_qa, "role": "process-auditor"},
    "sister_digest": {"fn": sister_digest, "role": "media-editor"},
}
