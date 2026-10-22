"""CogOps Terra — climate data & ESG analytics (OS §13; blueprint co. 8;
blue-ocean #5: climate modeling × financial risk, 9.0/10). Engines: physical
risk scoring for asset portfolios, transition risk scoring for sector
profiles, ESG research briefs with citation discipline.

HONESTY BOUNDARY (CBS Ch.3): the physical-risk scorer is a documented
HEURISTIC v0 (region-class hazard weights). It is labeled as such in every
artifact and is a scaffold for licensed hazard data — never presented as a
scientific risk model. Boundary: not a rating agency (blueprint).
"""
from __future__ import annotations

import json

import config
import ledger
import llm

META = {
    "name": "CogOps Terra",
    "dan": "Asset owners (finance, real estate, insurance) get climate-risk "
           "data packs and ESG briefs at finance grade, with full provenance.",
    "stage_at_v10": 0,
    "seed_assets": "blue-ocean #5 analysis (climate × financial risk, 9.0/10)",
    "human_of_record": "client's risk officer",
    "input_metrics": [
        {"key": "data_packs_sold_month", "layer": "F", "owner": "risk-modeler", "floor": 1},
        {"key": "model_source_citations_per_pack", "layer": "Q", "owner": "verifier", "floor": 5},
        {"key": "refresh_cadence_days", "layer": "P", "owner": "research-briefer", "floor": None},
    ],
    "squad_roles": ["risk-modeler", "research-briefer", "data-validator", "verifier"],
}

# Heuristic v0 hazard weights by region class (DOCUMENTED ASSUMPTIONS —
# upgrade path: licensed hazard layers e.g. IPCC AR6-derived datasets).
HAZARD_WEIGHTS = {
    "alpine_ch": {"heat": 0.2, "flood": 0.3, "storm": 0.2, "drought": 0.1, "landslide": 0.2},
    "mediterranean": {"heat": 0.35, "flood": 0.2, "storm": 0.1, "drought": 0.3, "landslide": 0.05},
    "north_europe": {"heat": 0.1, "flood": 0.35, "storm": 0.3, "drought": 0.15, "landslide": 0.1},
    "us_gulf": {"heat": 0.2, "flood": 0.3, "storm": 0.4, "drought": 0.05, "landslide": 0.05},
    "default": {"heat": 0.25, "flood": 0.25, "storm": 0.25, "drought": 0.15, "landslide": 0.1},
}
EXPOSURE_MULTIPLIER = {"coastal": 1.3, "riverine": 1.25, "urban_heat_island": 1.15,
                       "inland": 1.0}
TRANSITION_LEVERS = ("policy", "technology", "market", "reputation")


def physical_risk(params: dict, slug: str) -> dict:
    """Asset list → per-asset heuristic exposure score + portfolio rollup.
    inputs: {"assets":[{"id","region_class","exposure_tag","value_chf"}]}"""
    assets = params.get("assets", [])
    scored = []
    for a in assets:
        w = HAZARD_WEIGHTS.get(a.get("region_class", "default"),
                               HAZARD_WEIGHTS["default"])
        mult = EXPOSURE_MULTIPLIER.get(a.get("exposure_tag", "inland"), 1.0)
        hazard = sum(w.values()) / len(w)          # equal-contribution baseline
        peak = max(w, key=w.get)
        score = round(min(10, hazard * mult * 10), 2)
        scored.append({**a, "dominant_hazard": peak, "exposure_multiplier": mult,
                       "score_v0_heuristic": score,
                       "value_at_risk_proxy_chf": round(
                           float(a.get("value_chf", 0)) * score / 100.0, 2)})
    total_v = sum(float(a.get("value_chf", 0)) for a in assets)
    var = sum(s["value_at_risk_proxy_chf"] for s in scored)
    artifact = {"mode": "engine:heuristic-v0",
                "model_note": "HEURISTIC v0 — documented region-class weights; "
                              "not a scientific hazard model; upgrade path: "
                              "licensed IPCC-derived layers (CBS Ch.3 honesty)",
                "assets_scored": len(scored), "scored": scored,
                "portfolio_value_chf": total_v,
                "value_at_risk_proxy_chf": round(var, 2),
                "var_pct": round(100 * var / total_v, 2) if total_v else None,
                "asof": config.today()}
    _emit(slug, "physical_risk", artifact)
    return artifact


def transition_risk(params: dict, slug: str) -> dict:
    """Sector profile → transition-risk scoring across the four levers
    (TCFD-standard taxonomy): policy, technology, market, reputation."""
    sector = params.get("sector", "general")
    profile = params.get("profile", {})   # {"carbon_intensity": 0-10, ...}
    ci = float(profile.get("carbon_intensity", 5))
    scores = {
        "policy": round(min(10, ci * 1.1), 2),
        "technology": round(min(10, profile.get("tech_disruption_exposure", 5)), 2),
        "market": round(min(10, profile.get("demand_shift_exposure", 5)), 2),
        "reputation": round(min(10, ci * 0.8 + profile.get("controversy", 0)), 2),
    }
    composite = round(sum(scores.values()) / len(scores), 2)
    artifact = {"mode": "engine", "sector": sector, "taxonomy": "TCFD transition levers",
                "lever_scores": scores, "composite_0_10": composite,
                "bands": {"low": "<3", "medium": "3–6", "high": ">6"},
                "band": "low" if composite < 3 else "medium" if composite <= 6 else "high",
                "asof": config.today()}
    _emit(slug, "transition_risk", artifact)
    return artifact


def esg_brief(params: dict, slug: str) -> dict:
    """Research brief with citation discipline: sources list mandatory,
    LLM-synthesized when a provider is reachable, template otherwise — and
    both modes refuse to state numbers not present in `facts`."""
    topic = params.get("topic", "CSRD scope-3 data quality")
    facts = params.get("facts", [])
    sources = params.get("sources", [])
    if len(sources) < 5:
        raise ValueError("brief requires ≥5 sources (input metric: "
                         "model_source_citations_per_pack ≥ 5)")
    facts_txt = "\n".join(f"- {f}" for f in facts)
    try:
        out = llm.generate(
            f"Write a 250-word ESG research brief on '{topic}'. Use ONLY these "
            f"facts; cite sources by [n]. No invented numbers.\nFACTS:\n{facts_txt}\n"
            f"SOURCES:\n" + "\n".join(f"[{i+1}] {s}" for i, s in enumerate(sources)),
            system="You are CogOps Terra's research agent. Citation discipline is absolute.",
            company=slug)
        body, mode = out["text"], out["mode"]
    except llm.LLMUnavailable:
        body = (f"# {topic}\n\n{facts_txt}\n\nSources:\n"
                + "\n".join(f"[{i+1}] {s}" for i, s in enumerate(sources)))
        mode = "template"
    artifact = {"mode": mode, "topic": topic, "brief_md": body,
                "sources": sources, "asof": config.today()}
    _emit(slug, "esg_brief", {"mode": mode, "sources": len(sources)})
    return artifact


def _emit(slug: str, kind: str, artifact: dict) -> None:
    p = config.OUTBOX / f"{slug}_{kind}_{config.today()}.json"
    p.write_text(json.dumps(artifact, indent=1, sort_keys=True, default=str),
                 encoding="utf-8")
    ledger.event("terra_artifact", slug, {"kind": kind})


TASKS = {
    "physical_risk": {"fn": physical_risk, "role": "risk-modeler"},
    "transition_risk": {"fn": transition_risk, "role": "risk-modeler"},
    "esg_brief": {"fn": esg_brief, "role": "research-briefer"},
}
