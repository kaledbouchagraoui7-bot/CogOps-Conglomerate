"""The Group Automaton (OS §8 cadence as a daemon; JARVIS automaton.py DNA).

`python automaton.py cycle`      — one operating cycle
`python automaton.py daemon`     — loop cycles until stopped
`python automaton.py mission set <slug> "keep working on ..."`  — persistent
        "keep working" instruction advanced every cycle until DONE/BLOCKED/ENDED
`python automaton.py mission status|end <slug>`

One cycle (deterministic order):
  1. boot/idempotent registration      (registry.ensure_registered)
  2. lifecycle sweep                   (timebox breaches → gate requests;
                                        kill-criteria evaluation → kill reviews)
  3. cadence dues                      (weekly sheet / monthly memos when due)
  4. active missions                   (advance each one step; block honestly)
  5. portfolio health + fortress check (invariant I2 alarm)
Every action the automaton takes is Type-2 inside envelopes or a staged
Type-1 request — it NEVER self-approves (invariant I3).
"""
from __future__ import annotations

import argparse
import json
import sys
import time

import cadence
import capital
import config
import gates
import ledger
import lifecycle
import registry
import squad

DUE_FILE = config.RUNTIME_DIR / "cadence_dues.json"


def _dues() -> dict:
    if DUE_FILE.exists():
        return json.loads(DUE_FILE.read_text(encoding="utf-8"))
    return {"last_weekly": None, "last_monthly": None}


def _save_dues(d: dict) -> None:
    DUE_FILE.write_text(json.dumps(d, indent=1, sort_keys=True), encoding="utf-8")


def _week_id() -> str:
    return time.strftime("%G-W%V", time.gmtime(config.now()))


def _month_id() -> str:
    return config.today()[:7]


def cycle() -> dict:
    report = {"cycle_at": config.stamp(), "boot": None, "lifecycle": [],
              "cadence": [], "missions": [], "health": None, "gate_queue": 0}
    # 1. boot
    report["boot"] = registry.ensure_registered()
    # 2. lifecycle sweep
    for slug in lifecycle.all_slugs():
        c = lifecycle.load(slug)
        if c["stage"] == 5:
            continue
        tb = lifecycle.timebox_report(slug)
        if tb["breached"]:
            aid = gates.stage(slug, {"kind": "timebox_review", "notify": True,
                                     "days": tb["days_in_stage"],
                                     "limit": tb["timebox_days"]},
                              proposed_by="automaton")
            report["lifecycle"].append({"slug": slug, "timebox_breached": True,
                                        "gate": aid})
            # Stage 0-2 timebox breach → kill review request (Type-1, OS §5)
            if c["stage"] in (1, 2):
                ok, why = (lifecycle.stage1_evidence_met(c) if c["stage"] == 1
                           else (True, "") if c.get("paying_customers", 0) else (False, "no paying customer"))
                if not ok:
                    kid = gates.stage(slug, {"kind": "kill", "reason_preview": why},
                                      proposed_by="automaton")
                    report["lifecycle"].append({"slug": slug, "kill_review_staged": kid})
    # 3. cadence dues
    d = _dues()
    if d["last_weekly"] != _week_id():
        p = cadence.weekly_sheet()
        d["last_weekly"] = _week_id()
        report["cadence"].append(f"weekly:{p.name}")
    if d["last_monthly"] != _month_id():
        for slug in lifecycle.all_slugs():
            c = lifecycle.load(slug)
            if c["stage"] >= 2:
                p = cadence.monthly_memo(slug)
                report["cadence"].append(f"memo:{p.name}")
        d["last_monthly"] = _month_id()
    _save_dues(d)
    # 4. missions
    for slug, m in squad.mission_status().items():
        if m.get("status") != "ACTIVE":
            continue
        step = _advance_mission(slug, m)
        report["missions"].append({"slug": slug, **step})
    # 4b. nervous system: sense -> reflexes (protective, never external)
    import nervous
    report["nervous"] = nervous.cycle()
    # 5. health
    import metrics
    cos = [lifecycle.load(s) for s in lifecycle.all_slugs()]
    report["health"] = metrics.portfolio_health(cos)
    if not capital.fortress_ok():
        report["health"]["ALARM"] = "cash fortress below floor — invariant I2"
        ledger.event("fortress_alarm", "group",
                     {"months": report["health"]["fortress_months"]})
    report["gate_queue"] = len(gates.queue("PENDING"))
    ledger.event("automaton_cycle", "group",
                 {"lifecycle_events": len(report["lifecycle"]),
                  "missions_active": len(report["missions"]),
                  "gate_queue": report["gate_queue"]})
    return report


def _advance_mission(slug: str, m: dict) -> dict:
    """Advance one mission step. Missions are bounded: each step must be a
    Type-2 action inside the envelope, or the mission BLOCKS on a gate —
    it never self-approves (I3)."""
    try:
        c = lifecycle.load(slug)
    except lifecycle.CompanyNotFound:
        squad.mission_end(slug, "no-such-company")
        return {"status": "ENDED", "why": "company not registered"}
    text = m["text"].lower()
    if c["stage"] == 5:
        squad.mission_end(slug, "company-closed")
        return {"status": "ENDED", "why": "company killed/graduated"}
    # simple deterministic step policy: run the company's first due task or
    # produce a status note; blocked when a gate is required and pending
    import registry as reg
    tasks = reg.tasks(slug)
    if not tasks:
        squad.mission_progress(slug, "no tasks available", blocked="empty engine")
        return {"status": "BLOCKED", "why": "empty engine"}
    if "done" in text and c["stage"] <= 1 and not c["evidence"]:
        squad.mission_progress(slug, "mission requires validation evidence first",
                               blocked="stage-1 evidence missing — founder must "
                                       "supply market evidence (envelope-safe)")
        return {"status": "BLOCKED", "why": "stage-1 evidence missing"}
    squad.mission_progress(slug, f"cycle advanced; envelope {c['spent_chf']} CHF used; "
                                 f"stage {c['stage']}")
    return {"status": m["status"], "cycles": m["cycles"] + 1}


def daemon(interval_s: float = 3600.0, max_cycles: int | None = None) -> None:
    n = 0
    while True:
        rep = cycle()
        n += 1
        print(f"[{rep['cycle_at']}] cycle {n}: lifecycle={len(rep['lifecycle'])} "
              f"cadence={len(rep['cadence'])} missions={len(rep['missions'])} "
              f"gate_queue={rep['gate_queue']} fortress={rep['health']['fortress_months']}mo")
        if max_cycles and n >= max_cycles:
            break
        if config.FREEZE_CLOCK:
            break                      # frozen clock ⇒ single cycle (tests)
        time.sleep(interval_s)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CogOps Group Automaton")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("cycle")
    d = sub.add_parser("daemon"); d.add_argument("--interval", type=float, default=3600.0)
    d.add_argument("--max-cycles", type=int, default=None)
    m = sub.add_parser("mission")
    msub = m.add_subparsers(dest="mcmd")
    ms = msub.add_parser("set"); ms.add_argument("slug"); ms.add_argument("text")
    msub.add_parser("status").add_argument("slug", nargs="?")
    me = msub.add_parser("end"); me.add_argument("slug")
    a = ap.parse_args(argv)
    if a.cmd == "cycle":
        print(json.dumps(cycle(), indent=1, default=str))
        return 0
    if a.cmd == "daemon":
        daemon(a.interval, a.max_cycles)
        return 0
    if a.cmd == "mission":
        if a.mcmd == "set":
            print(json.dumps(squad.mission_set(a.slug, a.text), indent=1))
        elif a.mcmd == "status":
            print(json.dumps(squad.mission_status(a.slug), indent=1))
        elif a.mcmd == "end":
            print(json.dumps(squad.mission_end(a.slug), indent=1))
        else:
            m.print_help()
        return 0
    ap.print_help()
    print("\n" + config.summary())
    return 0


if __name__ == "__main__":
    sys.exit(main())
