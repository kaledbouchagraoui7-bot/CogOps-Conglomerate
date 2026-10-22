"""Operating cadence (OS §8) as artifact generators.

Total founder time budget is a design constraint: ≤2 h/week + 1 day/quarter.
Every artifact is AI-drafted when a provider is reachable (mode=llm:…) and a
deterministic offline composition otherwise (mode=template) — labeled, never
faked (JARVIS honesty principle). Artifacts land in runtime/outbox/.
"""
from __future__ import annotations

import json
from pathlib import Path

import capital
import config
import ledger
import lifecycle
import metrics


def _write(name: str, text: str, meta: dict) -> Path:
    p = config.OUTBOX / name
    p.write_text(text, encoding="utf-8")
    ledger.event("cadence_artifact", name, {"bytes": len(text), **meta})
    return p


def _draft(kind: str, facts: str) -> tuple[str, str]:
    """LLM-draft with honest template fallback. Returns (text, mode)."""
    import llm
    try:
        out = llm.generate(
            f"You are the CogOps Group reporting agent. Write a {kind} in concise "
            f"prose. Candor-first: problems before wins. Use ONLY these facts, "
            f"never invent numbers:\n{facts}")
        return out["text"], out["mode"]
    except llm.LLMUnavailable:
        return facts, "template"


def weekly_sheet() -> Path:
    """WBR-lite: per-company SPQP exceptions, gate queue, fortress, funnel."""
    import gates
    lines = [f"# Weekly Business Review — {config.today()}", ""]
    lines.append(f"**Fortress:** {capital.fortress_months():.1f} months "
                 f"({'OK' if capital.fortress_ok() else 'BELOW FLOOR — I2'})  ")
    pend = gates.queue("PENDING")
    lines.append(f"**Gate queue (Type-1 pending):** {len(pend)}")
    for g in pend:
        lines.append(f"- `{g['id']}` [{g['level']}] {g['company']}: "
                     f"{g['action'].get('kind')} — {g['reason']}")
    lines.append("")
    exceptions = 0
    for slug in lifecycle.all_slugs():
        c = lifecycle.load(slug)
        if c["stage"] == 5:
            continue
        sc = metrics.scorecard(slug, c)
        breaches = [m for layer in sc["spqp"].values() for m in layer if m["breach"]]
        tb = lifecycle.timebox_report(slug)
        lines.append(f"## {c['name']} — stage {c['stage']} "
                     f"({lifecycle.STAGES[c['stage']]}) · {tb['days_in_stage']}d in stage"
                     f"{' · ⚠ TIMEBOX BREACHED' if tb['breached'] else ''}")
        pnl = sc["performance_pnl"]
        lines.append(f"contribution CHF {pnl['contribution']:.2f} · revenue "
                     f"CHF {pnl['revenue']:.2f} · spent CHF {pnl['spent']:.2f} · "
                     f"platform charges CHF {pnl['platform_charges']:.2f}")
        if breaches:
            exceptions += len(breaches)
            for b in breaches:
                lines.append(f"- ⚠ **{b['metric']}** = {b['value']} < floor {b['floor']} "
                             f"(owner: {b['owner']}, as of {b['asof']})")
        lines.append("")
    lines.append(f"_Exceptions this week: {exceptions}. Good news needs no airtime "
                 f"(Amazon WBR)._")
    text = "\n".join(lines)
    body, mode = _draft("weekly business review summary (3 sentences max)",
                        text[:2500])
    text += f"\n\n---\n**Summary ({mode}):**\n{body}\n"
    return _write(f"wbr_{config.today()}.md", text, {"mode": mode, "kind": "weekly"})


def monthly_memo(slug: str) -> Path:
    """Six-pager-style narrative per Stage-2+ company: state, evidence,
    mistakes FIRST, decisions requested."""
    c = lifecycle.load(slug)
    sc = metrics.scorecard(slug, c)
    ev = c["evidence"][-10:]
    kills = [d for d in ledger.decisions(subject=slug) if d["kind"] == "KILL_WIN"]
    facts = (f"company={c['name']} stage={c['stage']} dan={c['dan']}\n"
             f"pnl={json.dumps(sc['performance_pnl'])}\n"
             f"evidence={json.dumps(ev)}\n"
             f"breaches={json.dumps([m for l in sc['spqp'].values() for m in l if m['breach']])}\n"
             f"kill_wins={len(kills)}")
    body, mode = _draft(
        "monthly narrative memo. Structure: 1) What went wrong (candor-first) "
        "2) State & evidence 3) Decisions requested. Prose, no slides", facts)
    text = (f"# Monthly memo — {c['name']} — {config.today()[:7]}\n\n"
            f"**Dan:** {c['dan']}\n\n**P&L (contribution):** "
            f"{json.dumps(sc['performance_pnl'], indent=1)}\n\n"
            f"## Narrative ({mode})\n{body}\n")
    return _write(f"memo_{slug}_{config.today()[:7]}.md", text,
                  {"mode": mode, "kind": "monthly", "slug": slug})


def quarterly_pd(slug: str, objectives: list[str]) -> dict:
    """PD-lite (Danaher Policy Deployment): 1–2 breakthrough objectives per
    quarter, set via gate catchball (Type-1), progress reviewed weekly."""
    if not 1 <= len(objectives) <= 2:
        raise ValueError("PD-lite: exactly 1–2 breakthrough objectives (OS §8)")
    c = lifecycle.load(slug)
    aid = gates_stage_pd(slug, objectives)
    c["pd_objectives"] = [{"q": config.today()[:7], "objectives": objectives,
                           "gate": aid, "set_at": config.stamp()}]
    lifecycle.save(c)
    return {"slug": slug, "objectives": objectives, "gate": aid}


def gates_stage_pd(slug: str, objectives: list[str]) -> str:
    import gates
    return gates.stage(slug, {"kind": "pd_objectives", "objectives": objectives,
                              "external": False, "notify": True},
                       proposed_by="cadence")


def annual_letter(year: str | None = None) -> Path:
    """Owner Letter (Berkshire M7): failures first, numbers second, doctrine
    changes third, invariants reaffirmed last (OS §8/§15)."""
    year = year or config.today()[:4]
    dec = ledger.decisions()
    kills = [d for d in dec if d["kind"] == "KILL_WIN"]
    promos = [d for d in dec if d["kind"] == "promoted"]
    grads = [d for d in dec if d["kind"] == "graduated"]
    health = metrics.portfolio_health([lifecycle.load(s) for s in lifecycle.all_slugs()])
    facts = (f"year={year} kills={len(kills)} promotions={len(promos)} "
             f"graduations={len(grads)} health={json.dumps(health)}")
    body, mode = _draft(
        "annual owner letter. Candor-first: what failed and what it cost, then "
        "the numbers, then doctrine changes, then reaffirm the invariants",
        facts)
    text = (f"# CogOps Group — Owner Letter {year}\n\n"
            f"## What went wrong first\n\n_(candor-first by doctrine, OS §1)_\n\n"
            f"{body}\n\n## The numbers\n\n```json\n{json.dumps(health, indent=1)}\n```\n\n"
            f"## Invariants reaffirmation (§14)\n\nI1–I12 reviewed and reaffirmed "
            f"for {int(year) + 1} — or amended only via Decision Record.\n\n"
            f"_Draft mode: {mode} · signed: {config.FOUNDER}_\n")
    return _write(f"owner_letter_{year}.md", text, {"mode": mode, "kind": "annual"})
