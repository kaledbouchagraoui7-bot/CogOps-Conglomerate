"""CogOps Verde — cleantech & energy software (OS §13; blueprint co. 7; gap
7.8 EU/US, 7.2 CH). Engines: GHG-Protocol carbon accounting (Scope 1 fuel
combustion, Scope 2 electricity location-based, Scope 3-lite spend-based
categories 1/6/7) with sourced emission factors (data/emission_factors.json),
and a CSRD-lite report generator for SMEs. Boundary: no hardware, no energy
trading (blueprint).
"""
from __future__ import annotations

import json

import config
import ledger

META = {
    "name": "CogOps Verde",
    "dan": "SMEs meet sustainability reporting (CSRD-lite, carbon books) "
           "without a sustainability department.",
    "stage_at_v10": 0,
    "seed_assets": "—",
    "human_of_record": "client's management (report ownership)",
    "input_metrics": [
        {"key": "reports_delivered_month", "layer": "F", "owner": "esrs-reporter", "floor": 1},
        {"key": "data_source_coverage_pct", "layer": "Q", "owner": "data-validator", "floor": 80},
        {"key": "renewal_pct", "layer": "F", "owner": "partnership-scout", "floor": 70},
    ],
    "squad_roles": ["carbon-accountant", "esrs-reporter", "data-validator", "verifier"],
}

FACTORS_FILE = config.ROOT / "data" / "emission_factors.json"


def _factors() -> dict:
    return json.loads(FACTORS_FILE.read_text(encoding="utf-8"))


def carbon_account(params: dict, slug: str) -> dict:
    """Activities → CO2e per GHG Protocol scopes.
    params: {"fuel_l": {"diesel": 1200}, "electricity_kwh": 8000,
             "grid_region": "CH", "scope3_spend_chf": {"goods": 50000,
             "business_travel": 12000, "commuting": 6000}}
    Every factor carries as-of + source (invariant I11)."""
    f = _factors()
    s1 = 0.0
    detail1 = {}
    for fuel, litres in (params.get("fuel_l") or {}).items():
        fac = f["scope1_fuel_kgco2e_per_l"].get(fuel)
        if fac is None:
            raise ValueError(f"no emission factor for fuel {fuel!r} — add it with source+asof")
        kg = float(litres) * fac["value"]
        detail1[fuel] = {"litres": litres, "kgco2e": round(kg, 1),
                         "factor": fac}
        s1 += kg
    e = params.get("electricity_kwh", 0.0)
    region = params.get("grid_region", "CH")
    fac2 = f["scope2_electricity_kgco2e_per_kwh"].get(region)
    if fac2 is None:
        raise ValueError(f"no grid factor for {region!r}")
    s2 = float(e) * fac2["value"]
    s3 = 0.0
    detail3 = {}
    spend = params.get("scope3_spend_chf") or {}
    for cat_key, chf in spend.items():
        fac3 = f["scope3_spend_kgco2e_per_chf"].get(cat_key)
        if fac3 is None:
            raise ValueError(f"no spend factor for {cat_key!r}")
        kg = float(chf) * fac3["value"]
        detail3[cat_key] = {"chf": chf, "kgco2e": round(kg, 1), "factor": fac3}
        s3 += kg
    total = s1 + s2 + s3
    artifact = {"mode": "engine", "scope1_kgco2e": round(s1, 1),
                "scope2_kgco2e": round(s2, 1), "scope3_lite_kgco2e": round(s3, 1),
                "total_kgco2e": round(total, 1),
                "total_tco2e": round(total / 1000.0, 3),
                "detail": {"scope1": detail1,
                           "scope2": {"kwh": e, "region": region, "factor": fac2},
                           "scope3": detail3},
                "method": "GHG Protocol: S1 combustion, S2 location-based, "
                          "S3 spend-based (cats 1/6/7-lite)",
                "asof": config.today()}
    _emit(slug, "carbon", artifact)
    return artifact


def csrd_lite_report(params: dict, slug: str) -> dict:
    """ESRS-lite SME report skeleton populated with the computed carbon books:
    governance, strategy, impacts (E1 climate numbers from carbon_account),
    metrics table, and an explicit limitations section (honesty rule)."""
    carbon = params.get("carbon") or carbon_account(params, slug)
    company = params.get("company", "CLIENT")
    md = f"""# {company} — Sustainability Report (CSRD-lite / VSME-aligned)
_Generated {config.today()} · method: {carbon['method']}_

## 1. Governance
Management owns this report (human of record). Data pipeline: CogOps Verde
carbon accounting engine; every factor carries source + as-of date.

## 2. Strategy
Climate impacts material to {company}: energy use (Scope 2), fleet/fuels
(Scope 1), purchased goods & travel (Scope 3-lite).

## 3. Impacts — E1 Climate (tCO2e)
| Scope | tCO2e |
|---|---|
| Scope 1 (combustion) | {carbon['scope1_kgco2e'] / 1000:.3f} |
| Scope 2 (electricity, location-based) | {carbon['scope2_kgco2e'] / 1000:.3f} |
| Scope 3-lite (spend-based cats 1/6/7) | {carbon['scope3_lite_kgco2e'] / 1000:.3f} |
| **Total** | **{carbon['total_tco2e']}** |

## 4. Limitations (mandatory)
Spend-based Scope 3 is an average-data proxy (GHG Protocol scope 3 standard);
grid factor is location-based as of the factor table date. Figures are
management information, not assured statements.

## 5. Metric provenance
```json
{json.dumps(carbon['detail'], indent=1, sort_keys=True)[:1800]}
```
"""
    artifact = {"mode": "engine", "report_md": md, "total_tco2e": carbon["total_tco2e"],
                "asof": config.today()}
    _emit(slug, "csrd_lite", {"mode": "engine", "total_tco2e": carbon["total_tco2e"]})
    return artifact




def csrd_full(params: dict, slug: str) -> dict:
    """The Verde<->Terra link, direction 1: the CSRD-lite report's climate-risk
    chapter is bought from Terra through the internal market (ticket at the
    DR-0008 price) — one integrated deliverable, two provenance chains, both
    P&Ls honest (I7). ESRS logic: impacts (books) + risks & resilience (screens)."""
    import platformsvc
    from companies import terra as terra_co
    carbon = carbon_account(params, slug)
    assets = params.get("assets") or [{"id": "HQ", "region_class": params.get("region_class", "alpine_ch"),
                                       "exposure_tag": params.get("exposure_tag", "inland"),
                                       "value_chf": params.get("asset_value_chf", 1_000_000)}]
    ticket = platformsvc.request(slug, "climate_risk", spec="climate-risk chapter for CSRD-lite",
                                 units=len(assets))
    risk = terra_co.physical_risk({"assets": assets}, "terra")
    trans = None
    if params.get("sector_profile"):
        trans = terra_co.transition_risk(params["sector_profile"], "terra")
    platformsvc.serve(ticket["id"], {"ref": f"verde-csrd-climate-chapter:{ticket['id']}"})
    base = csrd_lite_report({**params, "carbon": carbon}, slug)
    chapter = ("\n## 3b. Climate risks & resilience (via CogOps Terra, internal market)\n"
               f"- Physical screen (model grade: {risk['model_note'].split('—')[0].strip()}): "
               f"portfolio VaR proxy CHF {risk['value_at_risk_proxy_chf']:,.2f} "
               f"({risk['var_pct']}% of stated value)\n"
               + "".join(f"- asset {a['id']}: score {a['score_v0_heuristic']}/10, dominant hazard {a['dominant_hazard']}\n"
                         for a in risk["scored"])
               + (f"- Transition composite: {trans['composite_0_10']}/10 ({trans['band']})\n" if trans else "")
               + "- Provenance: Terra ticket " + ticket["id"] + " at internal price; "
                 "screening-grade v0, upgrade path documented (Terra model-grade doctrine).\n")
    base["report_md"] = base["report_md"].replace("## 4. Limitations (mandatory)",
                                                  chapter + "\n## 4. Limitations (mandatory)")
    base["climate_chapter_ticket"] = ticket["id"]
    base["notional_chf"] = ticket["notional_chf"]
    _emit(slug, "csrd_full", {"mode": "engine", "ticket": ticket["id"],
                              "total_tco2e": carbon["total_tco2e"]})
    return base




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
    ledger.event("verde_artifact", slug, {"kind": kind})


# Star link: Intelligence <-> this company (DR-0010)
LINKS = {"terra": "csrd_full", "intelligence": "intelligence_ops"}

TASKS = {
    "intelligence_ops": {"fn": intelligence_ops, "role": "carbon-accountant"},
    "carbon_account": {"fn": carbon_account, "role": "carbon-accountant"},
    "csrd_lite_report": {"fn": csrd_lite_report, "role": "esrs-reporter"},
    "csrd_full": {"fn": csrd_full, "role": "esrs-reporter"},
}
