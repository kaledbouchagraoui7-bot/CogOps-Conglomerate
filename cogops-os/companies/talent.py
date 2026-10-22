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
                    "training-coordinator", "market-researcher"],
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


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")
    ledger.event("talent_artifact", slug, {"kind": kind})


TASKS = {
    "curriculum": {"fn": curriculum, "role": "curriculum-designer"},
    "match": {"fn": match, "role": "matcher-engine"},
    "market_brief": {"fn": market_brief, "role": "market-researcher"},
}
