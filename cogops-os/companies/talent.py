"""CogOps Talent — the workforce company (OS §13; blueprint co. 10).
Monetizes the gap itself (the two domain analyses ARE the market data).
Engines: curriculum generator (tracks from data/curricula.json, sourced from
the gap analyses), skills-vector cosine matcher for placements, and career-
intelligence market briefs. Boundary: no accredited degrees (blueprint).
"""
from __future__ import annotations

import json
import math

import config
import ledger

META = {
    "name": "CogOps Talent",
    "dan": "Scarce-domain talent gets trained and matched; employers get "
           "pipeline in the domains with the worst demand/supply ratios.",
    "stage_at_v10": 0,
    "seed_assets": "europe-america + switzerland domain analyses (market data)",
    "human_of_record": "founder (placement contracts)",
    "input_metrics": [
        {"key": "course_completions_month", "layer": "F", "owner": "training-coordinator", "floor": 5},
        {"key": "placement_rate_pct", "layer": "F", "owner": "placement-counselor", "floor": 20},
        {"key": "employer_repeat_rate_pct", "layer": "F", "owner": "partnership-scout", "floor": 30},
    ],
    "squad_roles": ["curriculum-designer", "matcher-engine", "placement-counselor",
                    "training-coordinator", "market-researcher", "partnership-scout"],
}


def curriculum(params: dict, slug: str) -> dict:
    """Track name → full curriculum document (modules, hours, capstone,
    assessment) from data/curricula.json. Each module cites its labor-market
    rationale (gap score) — the analyses are the syllabus's evidence base."""
    tracks = json.loads((config.ROOT / "data" / "curricula.json")
                        .read_text(encoding="utf-8"))
    name = params.get("track")
    if name not in tracks["tracks"]:
        raise ValueError(f"unknown track {name!r} — available: {sorted(tracks['tracks'])}")
    t = tracks["tracks"][name]
    total_h = sum(m["hours"] for m in t["modules"])
    md = [f"# {t['title']}", f"_Domain evidence: {t['market_evidence']}_", "",
          f"**Total: {total_h} h · {len(t['modules'])} modules · capstone: {t['capstone']}**", ""]
    for i, m in enumerate(t["modules"], 1):
        md.append(f"## {i}. {m['title']} ({m['hours']} h)")
        md.append(f"- outcomes: {'; '.join(m['outcomes'])}")
        md.append(f"- assessment: {m['assessment']}")
        md.append("")
    artifact = {"mode": "engine", "track": name, "total_hours": total_h,
                "curriculum_md": "\n".join(md), "asof": config.today(),
                "boundary": "no accredited degrees issued (blueprint)"}
    _emit(slug, f"curriculum_{name}", artifact)
    return artifact


def match(params: dict, slug: str) -> dict:
    """TF skills-vector cosine matcher: candidate ↔ role ranking. Deterministic,
    explainable (per-skill contributions listed — white-box by design)."""
    cand = {s.lower().strip() for s in params.get("candidate_skills", [])}
    roles = params.get("roles", [])          # [{"title", "skills": [...], "weights"?}]
    if not cand or not roles:
        raise ValueError("need candidate_skills and roles")
    ranked = []
    for r in roles:
        need = {s.lower().strip(): float(w)
                for s, w in (r.get("skill_weights") or
                             {s: 1.0 for s in r.get("skills", [])}).items()}
        num = sum(need.get(s, 0.0) for s in cand)
        den = math.sqrt(sum(w * w for w in need.values())) * math.sqrt(len(cand))
        score = round(num / den, 4) if den else 0.0
        matched = sorted(s for s in cand if s in need)
        missing = sorted(s for s in need if s not in cand)
        ranked.append({"title": r["title"], "score": score,
                       "matched_skills": matched, "skill_gaps": missing,
                       "training_bridge": (f"curriculum modules covering "
                                           f"{missing[:3]}" if missing else "none needed")})
    ranked.sort(key=lambda x: -x["score"])
    artifact = {"mode": "engine", "ranked_roles": ranked, "asof": config.today()}
    _emit(slug, "match", artifact)
    return artifact


def market_brief(params: dict, slug: str) -> dict:
    """Career-intelligence brief per domain: the subscription product. Facts
    are quoted from the embedded analysis snapshot (as-of dated per I11) —
    never live-scraped, never invented."""
    domain = params.get("domain", "ai_ml")
    snap = json.loads((config.ROOT / "data" / "curricula.json")
                      .read_text(encoding="utf-8"))["market_snapshot"]
    if domain not in snap:
        raise ValueError(f"no snapshot for {domain!r} — available: {sorted(snap)}")
    s = snap[domain]
    md = (f"# Market brief — {s['title']}\n\n"
          f"- Demand/supply gap: **{s['gap']}** ({s['scope']}) — as of {s['asof']}\n"
          f"- Salary band: {s['salary']} — as of {s['asof']}\n"
          f"- Why it matters: {s['why']}\n"
          f"- Source: {s['source']}\n")
    artifact = {"mode": "engine", "domain": domain, "brief_md": md,
                "asof": config.today()}
    _emit(slug, f"brief_{domain}", artifact)
    return artifact




def talent_report_html(params: dict, slug: str) -> dict:
    """Client-facing skill-gap report: candidate skills vs target roles via the
    explainable matcher, with training bridges — branded (sand accent),
    version-stamped, human-of-record line included."""
    import hashlib
    import json as _json
    theme = _json.loads((config.ROOT / "data" / "theme.json").read_text(encoding="utf-8"))
    gr, ac = theme["group"], theme["companies"]["talent"]["accent"]
    cand = params.get("candidate_skills", [])
    roles = params.get("roles", [])
    m = match({"candidate_skills": cand, "roles": roles}, slug)
    rows = "".join(
        f"<tr><td>{r['title']}</td><td>{r['score']:.3f}</td><td>{', '.join(r['matched_skills']) or '—'}</td>"
        f"<td>{', '.join(r['skill_gaps'][:4]) or 'none'}</td><td>{r['training_bridge']}</td></tr>"
        for r in m["ranked_roles"])
    body = (f"<!DOCTYPE html><html><head><meta charset=utf-8><title>Skill-gap scan — CogOps Talent</title>"
            f"<style>body{{background:{gr['bg']};color:{gr['ink']};font:14px/1.6 {gr['font']};padding:32px}}"
            f".wrap{{max-width:880px;margin:0 auto}}h1{{color:{ac};font-size:22px}}"
            f".badge{{display:inline-block;border:1px solid {gr['line']};color:{ac};border-radius:99px;padding:4px 12px;font-size:11px;letter-spacing:1px}}"
            f"table{{width:100%;border-collapse:collapse;margin:14px 0}}td,th{{padding:8px 10px;border-bottom:1px solid {gr['line']};text-align:left;font-size:13px}}"
            f"th{{color:{ac};font-size:11px;text-transform:uppercase;letter-spacing:1px}}"
            f".foot{{color:{gr['dim']};font-size:12px;margin-top:24px;border-top:1px solid {gr['line']};padding-top:12px}}</style>"
            f"</head><body><div class=wrap><span class=badge>COGOPS TALENT · a CogOps Group company</span>"
            f"<h1>Skill-gap scan — {len(cand)} skills vs {len(roles)} roles</h1>"
            f"<p>Generated {config.stamp()} · matcher: explainable TF cosine (per-skill contributions shown)</p>"
            f"<table><tr><th>Role</th><th>Match</th><th>You have</th><th>Gaps</th><th>Training bridge</th></tr>{rows}</table>"
            f"<div class=foot>Version stamp <b>{{HASH}}</b> · scores are decision support, not a hiring "
            f"decision — a human counselor reviews every paid report · "
            f"<b>Human of record: {META['human_of_record']}</b> · cogops.engine@gmail.com</div></div></body></html>")
    hh = hashlib.sha256(body.encode()).hexdigest()[:16]
    body = body.replace("{HASH}", hh)
    p = config.OUTBOX / f"talent_scan_{config.today()}_{hh[:8]}.html"
    p.write_text(body, encoding="utf-8")
    ledger.event("talent_deliverable", slug, {"version": hh, "roles": len(roles)})
    return {"mode": "engine", "html_file": p.name, "version_hash": hh,
            "ranked": m["ranked_roles"], "asof": config.today()}


def employer_prospects(params: dict, slug: str) -> dict:
    """The Growth↔Talent link, direction 1: Talent buys employer prospect lists
    FROM Growth through the internal market (platform ticket at DR-0002 price)
    and turns them into placement-sales pipeline. The charge is real (notional)
    on Talent's P&L — standalone books stay honest (I7)."""
    import platformsvc
    import registry
    csv = params.get("csv", "")
    n = max(1, len([l for l in csv.splitlines()[1:] if l.strip()]))
    ticket = platformsvc.request(slug, "lead_gen", spec="employer prospects for placement sales", units=n)
    enriched = registry.run_task("growth", "enrich_leads", {"csv": csv}, role="data-validator")
    platformsvc.serve(ticket["id"], {"ref": f"talent-employer-prospects:{ticket['id']}"})
    prospects = [l for l in enriched["leads"] if l["score"] >= 3]
    artifact = {"mode": "engine", "ticket": ticket["id"],
                "notional_chf": ticket["notional_chf"],
                "prospects": prospects, "rejected": enriched["rejected"],
                "next_action": "outreach-operator drafts touches via growth touch_draft; human sends",
                "asof": config.today()}
    _emit(slug, "employer_prospects", artifact)
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
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")
    ledger.event("talent_artifact", slug, {"kind": kind})


# Star link: Intelligence <-> this company (DR-0010)
LINKS = {"intelligence": "intelligence_ops"}

TASKS = {
    "intelligence_ops": {"fn": intelligence_ops, "role": "training-coordinator"},
    "curriculum": {"fn": curriculum, "role": "curriculum-designer"},
    "match": {"fn": match, "role": "matcher-engine"},
    "market_brief": {"fn": market_brief, "role": "market-researcher"},
    "talent_report_html": {"fn": talent_report_html, "role": "placement-counselor"},
    "employer_prospects": {"fn": employer_prospects, "role": "partnership-scout"},
}
