"""cogops.py — the founder console (single entry point).

  python cogops.py status                     group dashboard
  python cogops.py companies                  all ten, stages & tasks
  python cogops.py show <slug>                company record + scorecard
  python cogops.py tasks <slug>               engine tasks
  python cogops.py run <slug> <task> [--params '<json>']
  python cogops.py prfaq <slug> --pr "..." --premortem "..." [--faq Q=A ...]
  python cogops.py evidence <slug> <kind> <value> [--source S]
  python cogops.py spend <slug> <chf> <what>
  python cogops.py revenue <slug> <chf> [--recurring]
  python cogops.py promote <slug>             (stage → approve gate → re-run)
  python cogops.py kill <slug> --reason R [--confirm "cogops approves"]
  python cogops.py gate list|approve <id> [--confirm PHRASE]|refute <id> --why W
  python cogops.py sheet | memo <slug> | letter [year]
  python cogops.py sweep <net_profit_chf> <period> <price_chf>
  python cogops.py ladder <surplus_chf> [--opps '<json list>']
  python cogops.py audit                      the Auditing Agent (DBSL) run
  python cogops.py inbox pull|list|show ID    reply queue: AI drafts, YOU decide
  python cogops.py inbox approve ID [--text]  approve (edited) draft; then:
  python cogops.py inbox sent ID              record that you sent it
  python cogops.py inbox manual ID --text ..  your own words, recorded
  python cogops.py mission set|status|end ... (delegates to automaton)
  python cogops.py cycle | daemon [--interval S]
"""
from __future__ import annotations

import argparse
import json
import sys

import cadence
import capital
import cbs
import config
import gates
import ledger
import lifecycle
import metrics
import registry
import squad


def _p(x):
    print(json.dumps(x, indent=1, sort_keys=True, default=str))


def cmd_status(_a) -> int:
    registry.ensure_registered()
    cos = [lifecycle.load(s) for s in lifecycle.all_slugs()]
    health = metrics.portfolio_health(cos)
    print(config.summary())
    print(f"companies: {len(cos)}   live(2+): {sum(1 for c in cos if c['stage'] in (2,3,4))}"
          f"   gate queue: {len(gates.queue('PENDING'))}")
    _p(health)
    for c in cos:
        print(f"  {c['slug']:14s} stage {c['stage']} ({lifecycle.STAGES[c['stage']]:18s}) "
              f"rev {c['revenue_chf']:>9.2f} · spent {c['spent_chf']:>8.2f} · "
              f"contrib {c['contribution_chf']:>9.2f}")
    return 0


def cmd_companies(_a) -> int:
    _p(registry.list_all())
    return 0


def cmd_show(a) -> int:
    registry.ensure_registered()
    c = lifecycle.load(a.slug)
    _p({"record": c, "scorecard": metrics.scorecard(a.slug, c),
        "timebox": lifecycle.timebox_report(a.slug),
        "three_rights": __import__("autonomy").three_rights(c)})
    return 0


def cmd_tasks(a) -> int:
    _p({a.slug: registry.tasks(a.slug)})
    return 0


def cmd_run(a) -> int:
    registry.ensure_registered()
    params = json.loads(a.params) if a.params else {}
    _p(registry.run_task(a.slug, a.task, params))
    return 0


def cmd_prfaq(a) -> int:
    faq = [tuple(kv.split("=", 1)) for kv in (a.faq or [])]
    _p(lifecycle.attach_prfaq(a.slug, a.pr, faq, a.premortem))
    return 0


def cmd_evidence(a) -> int:
    val = float(a.value) if a.value.replace(".", "", 1).isdigit() else a.value
    _p(lifecycle.log_evidence(a.slug, a.kind, val, a.source or "cli"))
    return 0


def cmd_spend(a) -> int:
    _p(lifecycle.spend(a.slug, a.chf, a.what))
    return 0


def cmd_revenue(a) -> int:
    c = lifecycle.register_revenue(a.slug, a.chf, a.recurring)
    _p({"revenue_chf": c["revenue_chf"], "paying_customers": c.get("paying_customers", 0)})
    return 0


def cmd_promote(a) -> int:
    _p(lifecycle.promote(a.slug))
    return 0


def cmd_kill(a) -> int:
    _p(lifecycle.kill(a.slug, {"reason": a.reason, "data": a.data or "",
                               "proposed_by": "founder-cli"}, confirm=a.confirm or ""))
    return 0


def cmd_gate(a) -> int:
    if a.gcmd == "list":
        _p(gates.queue(a.status))
    elif a.gcmd == "approve":
        _p({"approved": gates.approve(a.id, confirm=a.confirm or "")})
    elif a.gcmd == "refute":
        _p({"refuted": gates.refute(a.id, a.why or "no reason given")})
    return 0


def cmd_sheet(_a) -> int:
    print(cadence.weekly_sheet())
    return 0


def cmd_memo(a) -> int:
    print(cadence.monthly_memo(a.slug))
    return 0


def cmd_letter(a) -> int:
    print(cadence.annual_letter(a.year))
    return 0


def cmd_sweep(a) -> int:
    _p(capital.monthly_sweep(a.net, a.price, a.period))
    return 0


def cmd_ladder(a) -> int:
    opps = json.loads(a.opps) if a.opps else []
    _p(capital.ladder_recommend(a.surplus, opps))
    return 0


def cmd_dashboard(a) -> int:
    import dashboard
    if a.serve:
        dashboard.serve(a.port)
        return 0
    p = dashboard.write_dashboard(a.out)
    print(f"dashboard written: {p}")
    return 0


def cmd_signals(_a) -> int:
    import nervous
    _p(nervous.signals(40))
    return 0


def cmd_unfreeze(a) -> int:
    import nervous
    try:
        _p(nervous.unfreeze(a.reason, confirm=a.confirm or ""))
    except PermissionError as e:
        print(f"refused: {e}")
        return 1
    return 0


def cmd_group(a) -> int:
    import holding, groupsite
    if a.gcmd == "brand":
        _p(holding.brand_lockups())
    elif a.gcmd == "status":
        _p(holding.group_status(a.fetch_counts))
    elif a.gcmd == "invariants":
        _p(holding.invariants())
    elif a.gcmd == "build":
        _p(groupsite.build(a.fetch_counts))
    return 0


def cmd_audit(_a) -> int:
    """The Auditing Agent (Danaher DBSL analog): CBS conformance + invariants."""
    registry.ensure_registered()
    import autonomy
    findings, ok_all = [], True
    for slug in lifecycle.all_slugs():
        c = lifecycle.load(slug)
        if not c["dan"]:
            findings.append(f"{slug}: missing dan"); ok_all = False
        reg = [k for k in metrics._db()["registry"] if k.startswith(slug + ":")]
        if len(reg) < 3:
            findings.append(f"{slug}: <3 owned input metrics (OS §9)"); ok_all = False
        env = lifecycle.envelope_of(c)
        if env is not None and c["spent_chf"] > env + 1e-9:
            findings.append(f"{slug}: envelope breach {c['spent_chf']}>{env}"); ok_all = False
    chain_d = ledger.verify_chain(ledger.DECISIONS)
    chain_e = ledger.verify_chain(ledger.EVENTS)
    center = autonomy.center_audit()
    fortress = capital.fortress_ok()
    v = cbs.version()
    verif = cbs.verification_log()
    failed_verif = sum(1 for x in verif if not x["ok"])
    _p({"audit": {"companies_ok": ok_all, "findings": findings,
                  "ledger_chain_decisions": chain_d, "ledger_chain_events": chain_e,
                  "center_pull_only": center["ok"],
                  "fortress_ok(I2)": fortress,
                  "cbs_version": v["cbs_version"],
                  "verifications_failed": failed_verif,
                  "kills_recorded_as_wins": len(ledger.decisions(kind="KILL_WIN")),
                  "verdict": "PASS" if (ok_all and chain_d and chain_e and
                                        center["ok"] and fortress) else "REVIEW"},
         "at": config.stamp()})
    return 0


def cmd_inbox(a) -> int:
    import inbox
    if a.icmd == "pull":
        _p(inbox.pull())
    elif a.icmd == "list":
        _p(inbox.listq())
    elif a.icmd == "show":
        _p(inbox.show(a.id))
    elif a.icmd == "approve":
        _p(inbox.approve(a.id, a.text))
    elif a.icmd == "sent":
        _p(inbox.mark_sent(a.id))
    elif a.icmd == "manual":
        _p(inbox.mark_manual(a.id, a.text or ""))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cogops.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("companies").set_defaults(fn=cmd_companies)
    x = sub.add_parser("show"); x.add_argument("slug"); x.set_defaults(fn=cmd_show)
    x = sub.add_parser("tasks"); x.add_argument("slug"); x.set_defaults(fn=cmd_tasks)
    x = sub.add_parser("run"); x.add_argument("slug"); x.add_argument("task")
    x.add_argument("--params"); x.set_defaults(fn=cmd_run)
    x = sub.add_parser("prfaq"); x.add_argument("slug"); x.add_argument("--pr", required=True)
    x.add_argument("--premortem", required=True); x.add_argument("--faq", nargs="*")
    x.set_defaults(fn=cmd_prfaq)
    x = sub.add_parser("evidence"); x.add_argument("slug"); x.add_argument("kind")
    x.add_argument("value"); x.add_argument("--source"); x.set_defaults(fn=cmd_evidence)
    x = sub.add_parser("spend"); x.add_argument("slug"); x.add_argument("chf", type=float)
    x.add_argument("what"); x.set_defaults(fn=cmd_spend)
    x = sub.add_parser("revenue"); x.add_argument("slug"); x.add_argument("chf", type=float)
    x.add_argument("--recurring", action="store_true"); x.set_defaults(fn=cmd_revenue)
    x = sub.add_parser("promote"); x.add_argument("slug"); x.set_defaults(fn=cmd_promote)
    x = sub.add_parser("kill"); x.add_argument("slug"); x.add_argument("--reason", required=True)
    x.add_argument("--data"); x.add_argument("--confirm"); x.set_defaults(fn=cmd_kill)
    x = sub.add_parser("gate"); x.add_argument("gcmd", choices=["list", "approve", "refute"])
    x.add_argument("id", nargs="?"); x.add_argument("--confirm"); x.add_argument("--why")
    x.add_argument("--status", default="PENDING"); x.set_defaults(fn=cmd_gate)
    sub.add_parser("sheet").set_defaults(fn=cmd_sheet)
    x = sub.add_parser("memo"); x.add_argument("slug"); x.set_defaults(fn=cmd_memo)
    x = sub.add_parser("letter"); x.add_argument("year", nargs="?"); x.set_defaults(fn=cmd_letter)
    x = sub.add_parser("sweep"); x.add_argument("net", type=float); x.add_argument("period")
    x.add_argument("price", type=float); x.set_defaults(fn=cmd_sweep)
    x = sub.add_parser("ladder"); x.add_argument("surplus", type=float); x.add_argument("--opps")
    x.set_defaults(fn=cmd_ladder)
    sub.add_parser("audit").set_defaults(fn=cmd_audit)
    x = sub.add_parser("dashboard"); x.add_argument("--serve", action="store_true")
    x.add_argument("--port", type=int, default=8020); x.add_argument("--out")
    x.set_defaults(fn=cmd_dashboard)
    sub.add_parser("signals").set_defaults(fn=cmd_signals)
    x = sub.add_parser("unfreeze"); x.add_argument("--reason"); x.add_argument("--confirm")
    x.set_defaults(fn=cmd_unfreeze)
    x = sub.add_parser("group"); x.add_argument("gcmd",
        choices=["brand", "status", "invariants", "build"])
    x.add_argument("--fetch-counts", action="store_true"); x.set_defaults(fn=cmd_group)
    x = sub.add_parser("inbox"); x.add_argument("icmd",
        choices=["pull", "list", "show", "approve", "sent", "manual"])
    x.add_argument("id", nargs="?"); x.add_argument("--text")
    x.set_defaults(fn=cmd_inbox)
    x = sub.add_parser("cycle"); x.set_defaults(fn=lambda a: __import__("automaton").main(["cycle"]))
    x = sub.add_parser("daemon"); x.add_argument("--interval", type=float, default=3600.0)
    x.set_defaults(fn=lambda a: __import__("automaton").main(["daemon", "--interval", str(a.interval)]))
    a = ap.parse_args(argv)
    if not getattr(a, "fn", None):
        ap.print_help()
        print("\n" + config.summary())
        return 0
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
