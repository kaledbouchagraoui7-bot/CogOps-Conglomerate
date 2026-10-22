"""selftest.py — offline regression suite for the CogOps OS.

Runs WITHOUT network and WITHOUT any LLM keys (providers stripped; engines must
fall back honestly to labeled templates). Runtime isolated in a temp dir; clock
frozen for byte-determinism. Exit 0 = ALL GREEN. Run before any commit that
touches money/gate logic (CBS Ch.3).

  python selftest.py
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

# ---- environment BEFORE any project import (JARVIS selftest pattern) -------
_tmp = Path(tempfile.mkdtemp(prefix="cogops-selftest-"))
os.environ["COGOPS_RUNTIME_DIR"] = str(_tmp)
os.environ["COGOPS_FREEZE_CLOCK"] = "1792700000"     # frozen: byte-determinism
for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY"):
    os.environ.pop(k, None)                           # honest offline mode

sys.path.insert(0, str(Path(__file__).resolve().parent))

import autonomy            # noqa: E402
import cadence             # noqa: E402
import capital             # noqa: E402
import cbs                 # noqa: E402
import config              # noqa: E402
import gates               # noqa: E402
import ledger              # noqa: E402
import lifecycle           # noqa: E402
import metrics             # noqa: E402
import platformsvc         # noqa: E402
import registry            # noqa: E402
import squad               # noqa: E402
import statsnr             # noqa: E402

FAILS = []
CHECKS = [0]


def check(name, cond, extra=""):
    CHECKS[0] += 1
    print(("PASS " if cond else "FAIL ") + name + (f"  | {extra}" if extra else ""))
    if not cond:
        FAILS.append(name)


def main() -> int:
    # ================= 1. boot & roster =================
    boot = registry.ensure_registered()
    check("boot: 10 companies registered", len(boot) == 10, str(len(boot)))
    stages = {s: lifecycle.load(s)["stage"] for s in lifecycle.all_slugs()}
    check("boot: stages match OS §13",
          stages["intelligence"] == 3 and stages["capitalco"] == 3
          and stages["growth"] == 2 and stages["helix"] == 1
          and stages["dossia"] == 1
          and all(stages[s] == 0 for s in
                  ("sentinel", "medtech", "verde", "terra", "talent")), str(stages))
    roster = squad.roster()
    known = {a["role"] for u in roster["universes"].values() for a in u}
    bad_roles = [(s, r) for s in registry.COMPANIES
                 for r in registry.meta(s)["squad_roles"] if r not in known]
    check("roster: every squad role exists in the 7-universe roster", not bad_roles,
          str(bad_roles[:3]))
    check("roster: 7 universes", len(roster["universes"]) == 7)
    check("cbs: 7 chapters load + version hash", len(cbs.version()["chapters"]) == 7
          and len(cbs.version()["cbs_version"]) == 12)
    imm = cbs.immersion("helix", registry.meta("helix")["dan"])
    check("cbs: immersion pack complete", len(imm["chapters_loaded"]) == 7
          and imm["owner_manual"])

    # ================= 2. gates (fail-closed) =================
    aid = gates.stage("verde", {"kind": "spend", "amount_chf": 900, "above_cap": True})
    denied = False
    try:
        gates.require_approval(aid)
    except gates.GateDenied:
        denied = True
    check("gate: unapproved Type-1 blocks execution (fail-closed)", denied)
    fc = False
    try:
        gates.require_approval("GA-NOPE")
    except gates.GateDenied:
        fc = True
    check("gate: unknown id fail-closed", fc)
    gates.approve(aid)
    check("gate: approved passes", gates.require_approval(aid)["status"] == "APPROVED")
    g3 = gates.stage("verde", {"kind": "spend", "money_movement": True})
    phrase_refused = False
    try:
        gates.approve(g3)
    except gates.GateDenied:
        phrase_refused = True
    check("gate: G3 refuses without confirmation phrase", phrase_refused)
    gates.approve(g3, confirm=config.CONFIRM_PHRASE)
    check("gate: G3 approves with phrase", gates.require_approval(g3)["status"] == "APPROVED")
    t2 = gates.stage("verde", {"kind": "content_edit"})
    check("gate: reversible inside-envelope = Type-2 auto",
          gates.classify({"kind": "content_edit"})[0] == "type2")

    # ================= 3. lifecycle =================
    r = lifecycle.promote("sentinel")
    check("lifecycle: stage-0 promote blocked without PR/FAQ",
          r["status"] == "blocked" and any("PR/FAQ" in b for b in r["blockers"]))
    lifecycle.attach_prfaq("sentinel", "PR text", [("Q", "A")], "failed because no ICP")
    r = lifecycle.promote("sentinel")
    check("lifecycle: promote stages a gate (no self-approval)", r["status"] == "gated")
    gates.approve(r["gate"])
    r = lifecycle.promote("sentinel")
    check("lifecycle: approved gate consumed → promoted to stage 1",
          r["status"] == "promoted" and r["stage"] == 1)
    r = lifecycle.promote("sentinel")
    check("lifecycle: stage-1→2 blocked without market evidence",
          r["status"] == "blocked" and any("evidence" in b for b in r["blockers"]))
    lifecycle.log_evidence("sentinel", "waitlist", 150, "landing page")
    r = lifecycle.promote("sentinel")
    gates.approve(r["gate"])
    r = lifecycle.promote("sentinel")
    check("lifecycle: evidence (waitlist 150) unlocks stage 2",
          r["status"] == "promoted" and r["stage"] == 2)

    # ================= 4. envelopes & caps =================
    s1 = lifecycle.spend("sentinel", 50.0, "domain + landing page")
    check("envelope: CHF 50 inside cap executes (Type-2)", s1["status"] == "executed")
    s2 = lifecycle.spend("sentinel", 300.0, "above-cap purchase")   # stage-2 cap = 250
    check("envelope: above-cap auto-escalates to gate, NOT executed",
          s2["status"] == "gated" and lifecycle.load("sentinel")["spent_chf"] == 50.0)
    g1900 = lifecycle.spend("sentinel", 1900.0, "fill toward envelope")
    check("envelope: above-cap spend stages gate", g1900["status"] == "gated")
    gates.approve(g1900["gate"].split(":")[0].strip())
    g1900b = lifecycle.spend("sentinel", 1900.0, "fill toward envelope")
    check("envelope: approved gate consumed → spend executes (50+1900 ≤ 2000)",
          g1900b["status"] == "executed"
          and lifecycle.load("sentinel")["spent_chf"] == 1950.0)
    breach = False
    try:
        lifecycle.spend("sentinel", 100.0, "breach attempt")        # 2050 > 2000
    except lifecycle.EnvelopeExceeded:
        breach = True
    check("envelope: breach hard-stops (no silent top-ups)", breach)

    # ================= 5. kill = WIN =================
    kr = lifecycle.kill("verde", {"reason": "validation: 0 waitlist in 4 weeks",
                                  "data": "landing stats empty"},
                        confirm=config.CONFIRM_PHRASE)
    check("kill: recorded as KILL_WIN with evidence",
          kr["status"] == "killed_as_win"
          and len(ledger.decisions(kind="KILL_WIN", subject="verde")) == 1)
    check("kill: squad earns budget credibility (+10% cap)",
          abs(squad.cap_multiplier("verde") - 1.10) < 1e-9)
    novibes = False
    try:
        lifecycle.kill("terra", {})
    except ValueError:
        novibes = True
    check("kill: vibes-based kill refused (evidence mandatory, I8)", novibes)

    # ================= 6. capital doctrine =================
    blocked = False
    try:
        capital.spend(50.0, "anything")     # wallet starts AT the fortress floor
    except capital.CapitalBlocked:
        blocked = True
    check("capital: spend below fortress floor blocked (I2)", blocked)
    capital.deposit(2000.0, "client revenue")
    capital.spend(100.0, "platform costs")
    check("capital: deposit above floor enables spend",
          capital.fortress_months() > config.FORTRESS_MONTHS - 1)
    ladder = capital.ladder_recommend(2000.0, [
        {"kind": "acquire", "id": "tiny-saas", "chf": 300, "evidence_ok": True},
        {"kind": "reinvest", "id": "growth", "chf": 400, "expected_return": 0.4, "evidence_ok": True},
        {"kind": "launch", "id": "terra", "chf": 200, "expected_return": 0.2, "evidence_ok": True},
        {"kind": "marketable", "id": "sweep", "chf": 500, "evidence_ok": True},
        {"kind": "reinvest", "id": "nogate", "chf": 999, "evidence_ok": False}])
    order = [p["kind"] for p in ladder]
    check("capital: ladder order reinvest→launch→marketable→acquire, ungated dropped",
          order.index("reinvest") < order.index("launch") < order.index("marketable_sweep")
          < order.index("acquisition") and "nogate" not in str(ladder), str(order))
    check("capital: acquisitions flagged PHASE-2 DORMANT",
          any("DORMANT" in p.get("why", "") for p in ladder))
    sw = capital.monthly_sweep(5000.0, 118.5, "2026-09")
    check("sweep: 30% of 5000 → p3a 600 + ibkr 900",
          sw["sweep_chf"] == 1500.0 and sw["pillar3a_chf"] == 600.0
          and sw["ibkr_chf"] == 900.0, str(sw)[:120])
    check("sweep: guarded DCA fills 7 VWRL whole shares + residual",
          sw["order"]["ok"] and sw["order"]["qty"] == 7
          and 60 < sw["order"]["residual_chf"] < 80)
    zero = capital.monthly_sweep(-500.0, 118.5, "2026-10")
    check("sweep: negative month routes NOTHING (zero-capital discipline)",
          zero["routed_chf"] == 0.0)
    huge = capital.guard_check_order({"side": "BUY", "sec_type": "STK", "qty": 900,
                                      "notional_chf": 100_000.0}, 0.0)
    check("guard: CHF 100k fresh-capital BUY passes (no maximum)", huge.ok,
          "; ".join(huge.violations[:1]))
    churn = capital.guard_check_order({"side": "SELL", "sec_type": "STK", "qty": 7,
                                       "notional_chf": 59_000.0}, 1_000.0)
    check("guard: churn SELL blocked (turnover ceiling)", not churn.ok)
    young = capital.guard_check_order({"side": "SELL", "sec_type": "STK", "qty": 7,
                                       "notional_chf": 800.0}, 1_000.0)
    check("guard: <180d lot SELL blocked (FIFO min holding)", not young.ok
          and any("180" in v for v in young.violations))
    for bad in ({"margin": True}, {"derivative": True}, {"short": True, "side": "SELL"}):
        rep = capital.guard_check_order({"side": "BUY", "sec_type": "STK", "qty": 1,
                                         "notional_chf": 100.0, **bad}, 10_000.0)
        if rep.ok:
            check(f"guard: {bad} blocked", False)
            break
    else:
        check("guard: margin/derivatives/shorts all blocked (I10)", True)
    cent = capital.guard_dca_order(0.01, 118.5)
    check("guard: one-cent order investable (fractional floor)",
          cent["fractional"] and cent["qty"] > 0)

    # ================= 7. stats kernel (SciPy-free, validated) ==============
    check("stats: gammln(0.5)=ln√π", abs(statsnr.gammln(0.5) - 0.5723649429) < 1e-8)
    p_chi = statsnr.chi2_sf(3.841459, 1)
    check("stats: χ²(3.841,df1) p≈0.05 (<1e-3)", abs(p_chi - 0.05) < 1e-3, f"p={p_chi:.6f}")
    wt = statsnr.welch_t([1, 2, 3, 4, 5], [2, 3, 4, 5, 6])
    check("stats: Welch t=−1 df=8 p≈0.3466 (<1e-3)",
          abs(wt["t"] + 1) < 1e-9 and abs(wt["df"] - 8) < 1e-9
          and abs(wt["p_two_sided"] - 0.34659) < 1e-3, f"p={wt['p_two_sided']:.6f}")
    ct = statsnr.chi2_contingency([[10, 20], [20, 10]])
    check("stats: 2x2 χ²(no Yates)=20/3 p≈0.009823", abs(ct["chi2"] - 20/3) < 1e-9
          and abs(ct["p"] - 0.009823) < 1e-4, f"chi2={ct['chi2']:.4f} p={ct['p']:.6f}")

    # ================= 8. autonomy contract =================
    viol = 0
    for act in ({"external": True}, {"money_movement": True}, {"signs_legally": True},
                {"debt": True}, {"obligates_holding": True}):
        try:
            autonomy.check({"slug": "x"}, act)
        except autonomy.ContractViolation:
            viol += 1
    check("autonomy: all 5 NEVER-rules block (fail-closed)", viol == 5, f"{viol}/5")
    ca = autonomy.center_audit()
    check("autonomy: platform stays pull-only (no center-push primitives)", ca["ok"])

    # ================= 9. metrics =================
    mo = False
    try:
        metrics.register("helix", "x", "F", "", floor=1)
    except metrics.MetricError:
        mo = True
    check("metrics: ownerless metric refused (Amazon M8 ban)", mo)
    ur = False
    try:
        metrics.observe("helix", "not_registered", 1)
    except metrics.MetricError:
        ur = True
    check("metrics: unregistered observation refused (no shadow metrics)", ur)
    b = metrics.observe("growth", "validated_leads_month", 10, "test")
    check("metrics: floor breach flagged", b["breach"])
    sc = metrics.scorecard("growth", lifecycle.load("growth"))
    check("metrics: SPQP scorecard assembles",
          set(sc["spqp"]) == {"S", "P", "Q", "F"} and "contribution" in sc["performance_pnl"])

    # ================= 10. platform (pull-only + notional charges) ==========
    t = platformsvc.request("helix", "crm_portal", "leads table")
    platformsvc.serve(t["id"], {"ref": "test"})
    check("platform: served ticket charges notional cost to company P&L (I7)",
          lifecycle.load("helix")["platform_charges_chf"] == 10.0)
    unk = False
    try:
        platformsvc.request("helix", "magic_service", "")
    except ValueError:
        unk = True
    check("platform: unknown service refused (catalog is the contract)", unk)

    # ================= 11. company engines =================
    g = registry.run_task("growth", "enrich_leads", {
        "csv": "name,email,company,role,note\nA,ok@firm.com,Firm,CTO," + "x" * 50 +
               "\nB,bad@@x,Firm,CEO,y\nC,ok@firm.com,Firm,CTO,dup\nD,d@spam.mailinator.com,X,CEO,z\nE,e2@firm2.com,F2,COO,w" * 1})
    check("growth: enrichment validates (malformed/dup/disposable rejected)",
          g["valid_leads"] == 2 and g["rejected"] == 3, str(g["rejection_reasons"]))
    check("growth: per-prospect copy honest TEMPLATE mode offline",
          all(c["mode"] == "template" for c in g["copies"]))
    p1 = registry.run_task("growth", "pseo_pages", {
        "rows": [{"title": "CHF Hypothek Rechner Zürich", "intro": "i", "rate": "3.1"},
                 {"title": "Crédit immobilier Genève", "intro": "j", "rate": "3.3"}]})
    p2 = registry.run_task("growth", "pseo_pages", {
        "rows": [{"title": "CHF Hypothek Rechner Zürich", "intro": "i", "rate": "3.1"},
                 {"title": "Crédit immobilier Genève", "intro": "j", "rate": "3.3"}]})
    check("growth: pSEO factory builds pages + sitemap", p1["pages_built"] == 2
          and "<urlset" in p1["sitemap"])
    check("growth: pSEO byte-deterministic (frozen clock)",
          [x["hash"] for x in p1["pages"]] == [x["hash"] for x in p2["pages"]])
    h = registry.run_task("helix", "sequence_qc", {
        "fasta": ">NM_TEST\nATGGGCTAA", "cross_checks": {"NM_TEST": {"nt": 9, "aa": 2}}})
    row = h["qc"][0]
    check("helix: sequence QC — nt/GC/ORF + cross-check gate PASS",
          row["nt"] == 9 and abs(row["gc_pct"] - 44.44) < 0.01
          and row["orf_fwd_aa"] == 2 and row["cross_check"] == "PASS", str(row))
    cohort = [{"patient_id": i, "arm": "A" if i % 2 else "B",
               "age": 30 + (i % 40) if i != 7 else 150, "sex": "F" if i % 3 else "M"}
              for i in range(12)] + [{"patient_id": 3, "arm": "A", "age": 44, "sex": "F"}]
    t1 = registry.run_task("helix", "table1", {"cohort": cohort, "bounds": {"age": (18, 90)}})
    acts = {a["action"] for a in t1["audit_trail"]}
    check("helix: EDA cleaning audit-trailed (dedupe+range reject+impute)",
          t1["seed_rows"] == 13 and t1["analyzed_rows"] == 11
          and {"dedupe_drop", "range_reject"} <= acts, str(acts))
    check("helix: Table-1 Welch test emitted", any(x.get("field") == "age" for x in t1["tests"]))
    d = registry.run_task("dossia", "m4_assemble", {"product": "DEMO",
                                                    "content": {"2.3": "QOS draft"}})
    check("dossia: CTD pack — 14 modules, 1 drafted, rest skeleton (never invented)",
          d["manifest"]["modules_total"] == 14 and d["manifest"]["drafted"] == 1)
    q = registry.run_task("dossia", "qc_checklist", {"document": {
        "author": "a", "reviewer": "r", "text": "x", "timestamp": "t", "source_ref": "s",
        "numbers_carry_asof": True, "has_todos": False, "units_consistent": True,
        "stored_in_ledger": True, "path": "/p"}})
    check("dossia: ALCOA+ QC full pass = 100% PASS", q["pass_rate_pct"] == 100.0
          and q["verdict"] == "PASS")
    m = registry.run_task("medtech", "mdr_doc_tree", {"device": "DemoDev", "risk_class": "IIa"})
    check("medtech: MDR tree — class IIa scoping correct (III-only section n/a)",
          m["applicable"] == 9 and any(s["status"] == "n/a" for s in m["sections"]))
    al = registry.run_task("medtech", "alcoa_log", {"entry": {
        "experiment": "EXP-1", "subject": "S-1", "value": 42.0, "unit": "ng/mL"}})
    check("medtech: ALCOA+ trail entry recorded", al["record"]["original"]
          and al["trail_lines"] >= 1)
    au = registry.run_task("sentinel", "audit_run", {
        "scope": "sme_baseline",
        "answers": {"IAM-1": False, "IAM-3": True, "NET-1": True, "DAT-4": False}})
    check("sentinel: audit scores + critical gaps surface remediation",
          au["score_pct"] == 50.0 and any(g["id"] in ("IAM-1", "DAT-4")
                                          for g in au["high_gaps"]))
    check("sentinel: injection judge — refusal contained, leak not",
          sentinel_contained_ok())
    ai = registry.run_task("sentinel", "ai_security_review", {})
    check("sentinel: AI review honest OFFLINE mode when no responder",
          ai["mode"] == "engine:offline" and ai["containment_rate_pct"] is None)
    bt = registry.run_task("capitalco", "backtest", {"prices": [118.5] * 12,
                                                     "monthly_chf": 900})
    bt2 = registry.run_task("capitalco", "backtest", {"prices": [118.5] * 12,
                                                      "monthly_chf": 900})
    check("capitalco: backtest fills 12 months, guard-checked in-loop",
          bt["fills"] == 12 and not bt["blocked_orders"])
    check("capitalco: backtest deterministic hash",
          bt["determinism_hash"] == bt2["determinism_hash"])
    fb = registry.run_task("capitalco", "factor_brief", {
        "rows": [{"factor": i, "target": i * 2 + (i % 3)} for i in range(9)]})
    check("capitalco: factor brief tercile Welch emitted",
          fb["n"] == 9 and "p_two_sided" in fb["hi_vs_lo_tercile"])
    tp = registry.run_task("capitalco", "treasury_policy", {})
    check("capitalco: treasury policy mirrors live config (no drift)",
          tp["policy"]["sweep_share_of_net_profit"] == config.SWEEP_PROFIT_SHARE
          and tp["policy"]["etf_dca"]["floor_chf"] == config.MIN_ORDER_CHF)
    ca1 = registry.run_task("verde", "carbon_account", {
        "fuel_l": {"diesel": 100}, "electricity_kwh": 1000, "grid_region": "CH",
        "scope3_spend_chf": {"goods": 1000}})
    check("verde: carbon maths exact (268+24+350=642 kg CO2e)",
          ca1["scope1_kgco2e"] == 268.0 and ca1["scope2_kgco2e"] == 24.0
          and ca1["scope3_lite_kgco2e"] == 350.0 and ca1["total_kgco2e"] == 642.0,
          str(ca1["total_kgco2e"]))
    rep = registry.run_task("verde", "csrd_lite_report", {
        "company": "ACME", "fuel_l": {"diesel": 100}, "electricity_kwh": 1000,
        "grid_region": "CH", "scope3_spend_chf": {"goods": 1000}})
    check("verde: CSRD-lite report carries limitations + provenance",
          "Limitations" in rep["report_md"] and "provenance" in rep["report_md"].lower())
    pr = registry.run_task("terra", "physical_risk", {"assets": [
        {"id": "A1", "region_class": "alpine_ch", "exposure_tag": "coastal",
         "value_chf": 1_000_000}]})
    check("terra: physical risk labeled HEURISTIC v0 (honesty boundary)",
          pr["mode"] == "engine:heuristic-v0" and "HEURISTIC" in pr["model_note"]
          and pr["scored"][0]["score_v0_heuristic"] > 0)
    few = False
    try:
        registry.run_task("terra", "esg_brief", {"topic": "t", "facts": ["f"],
                                                 "sources": ["a", "b", "c", "d"]})
    except ValueError:
        few = True
    check("terra: brief refuses <5 sources (citation discipline)", few)
    eb = registry.run_task("terra", "esg_brief", {"topic": "t", "facts": ["f1"],
                                                  "sources": ["s1", "s2", "s3", "s4", "s5"]})
    check("terra: offline brief = TEMPLATE mode with all sources",
          eb["mode"] == "template" and "[5] s5" in eb["brief_md"])
    cu = registry.run_task("talent", "curriculum", {"track": "ai_operations"})
    check("talent: curriculum ai_operations = 40h/4 modules",
          cu["total_hours"] == 40 and "capstone" in cu["curriculum_md"].lower())
    mt = registry.run_task("talent", "match", {
        "candidate_skills": ["python", "llm", "nlp"],
        "roles": [{"title": "AI Ops", "skills": ["python", "llm"]},
                  {"title": "Java Dev", "skills": ["java", "spring"]}]})
    check("talent: cosine matcher ranks AI Ops first with skill gaps",
          mt["ranked_roles"][0]["title"] == "AI Ops"
          and mt["ranked_roles"][0]["score"] > mt["ranked_roles"][1]["score"])
    mb = registry.run_task("talent", "market_brief", {"domain": "quant_finance"})
    check("talent: market brief quotes analysis as-of dated",
          "CHF 140" in mb["brief_md"] and "as of 2026-10" in mb["brief_md"])
    dep = registry.run_task("intelligence", "deploy_client", {
        "client": "TestCo", "services": ["site_factory", "llm_gateway", "crm_portal"]})
    check("intelligence: deploy orchestrates 3 platform tickets",
          len(dep["manifest"]["tickets"]) == 3
          and lifecycle.load("intelligence")["platform_charges_chf"] == 65.0)
    aa = registry.run_task("intelligence", "automation_audit", {"answers": {
        "process": "invoicing", "volume_month": 100, "minutes_per": 20,
        "steps": ["collect data", "draft invoice", "approve payment", "send to client"]}})
    check("intelligence: audit maps 'approve payment' to HUMAN gate",
          3 in aa["human_gates"] and aa["agent_automatable_pct"] < 100)
    kb = registry.run_task("intelligence", "kb_ground", {
        "client": "TestCo", "facts": [{"patterns": ["cost"], "answer": "CHF X"}]})
    check("intelligence: KB grounding manifest written (KB-first lineage)",
          kb["entries"] == 1 and (config.OUTBOX / kb["kb_file"]).exists())
    wrong = False
    try:
        registry.run_task("growth", "pseo_pages", {}, role="auditor")
    except PermissionError:
        wrong = True
    check("squad: out-of-squad role refused (staffing rights, OS §6)", wrong)

    # ================= 12. cadence artifacts =================
    w1 = cadence.weekly_sheet(); c1 = w1.read_text()
    w2 = cadence.weekly_sheet(); c2 = w2.read_text()
    check("cadence: weekly WBR sheet deterministic (frozen clock)",
          c1 == c2 and "Fortress" in c1)
    memo = cadence.monthly_memo("growth")
    check("cadence: monthly memo template-mode offline, candor-first structure",
          "(template)" in memo.read_text() and "Narrative" in memo.read_text())
    letter = cadence.annual_letter("2026")
    check("cadence: owner letter generated (failures-first doctrine)",
          "went wrong" in letter.read_text().lower())

    # ================= 13. missions & automaton =================
    squad.mission_set("helix", "keep working until done")
    import automaton
    rep = automaton.cycle()
    check("automaton: cycle boots 10, produces cadence, reports health",
          len(rep["boot"]) == 10 and rep["health"] is not None)
    ms = squad.mission_status("helix")
    check("automaton: mission BLOCKS honestly when stage-1 evidence missing (I3)",
          ms["status"] == "BLOCKED" and "evidence" in ms.get("blocked", ""))
    squad.mission_end("helix")
    check("mission: end recorded", squad.mission_status("helix")["status"] == "ENDED")

    # ================= 13b. notify, cost caps, theme, branded report, QR =====
    import notify, llm, json as _json
    n = notify.notify("selftest", "notification path test", priority="low")
    check("notify: no URL → honest ledger-only delivery (never silent drop)",
          n["pushed"] is False and n["channel"] == "ledger-only")
    gid = gates.stage("terra", {"kind": "spend", "amount_chf": 9999, "above_cap": True})
    evs = [e for e in ledger.read(ledger.EVENTS) if e["kind"] == "notification"]
    check("notify: G2 gate staging pushes to founder channel",
          any("gate" in (e.get("payload", {}) or {}).get("title", "") for e in evs), gid)
    check("llm: frontier estimate > value estimate > free = 0",
          llm.estimate_cost("anthropic", 4000, 300) > llm.estimate_cost("openrouter:x/y", 4000, 300)
          > llm.estimate_cost("openrouter:nvidia/nemotron:free", 4000, 300) == 0.0)
    llm.MONTHLY_CAP_USD = 0.05
    llm.record_spend("helix", 0.06)
    check("llm: per-company monthly cap blocks paid providers, keeps free",
          llm.paid_allowed("helix") is False and llm.paid_allowed("dossia") is True
          and llm.paid_allowed(None) is True)
    theme = _json.loads((config.ROOT / "data" / "theme.json").read_text(encoding="utf-8"))
    check("theme: group + all 10 company accents defined (brand read by code)",
          "bg" in theme["group"] and len(theme["companies"]) == 10
          and all(v.get("accent", "").startswith("#") for v in theme["companies"].values()))
    rep = registry.run_task("growth", "lead_report_html", {
        "client": "ACME AG",
        "csv": "name,email,company,role,note\nDr A,a@acme.ch,ACME,CTO," + "context " * 10})
    html = (config.OUTBOX / rep["html_file"]).read_text(encoding="utf-8")
    check("growth: branded report carries theme accent + evidence + version stamp",
          theme["companies"]["growth"]["accent"] in html and rep["version_hash"][:8] in html
          and "Validation" in html and rep["leads"] == 1)
    rep2 = registry.run_task("growth", "lead_report_html", {
        "client": "ACME AG",
        "csv": "name,email,company,role,note\nDr A,a@acme.ch,ACME,CTO," + "context " * 10})
    check("growth: deliverable versioning — identical input, identical hash",
          rep2["version_hash"] == rep["version_hash"])
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "growth" / "tools"))
    import qr_invoice as qr
    check("qr: mod-10-recursive matches canonical PostFinance example",
          qr.mod10_recursive("21000000000313947143000901") == "7")
    check("qr: IBAN mod-97 accepts valid & rejects corrupted",
          qr.iban_valid("CH93 0076 2011 6238 5295 7") and not qr.iban_valid("CH9300762011623852958"))
    ref = qr.qrr_reference("G-2026-001")
    check("qr: QRR reference = 27 digits, self-consistent check digit",
          len(ref) == 27 and qr.mod10_recursive(ref[:-1]) == ref[-1])
    f = qr.qr_payload(900.0, "CHF", {"name": "CogOps Group", "street": "s", "building": "",
                                     "plz": "2501", "city": "Biel", "country": "CH"},
                      "CH9300762011623852957", ref, "msg").split("\r\n")
    check("qr: SIX payload layout (SPC/0200/1 … QRR@17 … EPD@20, 22 fields, CRLF)",
          f[0:3] == ["SPC", "0200", "1"] and f[17] == "QRR" and f[18] == ref
          and f[20] == "EPD" and len(f) == 23 and f[-1] == "")

    # ================= 13c. inbox: AI drafts, founder decides ==============
    import inbox
    r = inbox.pull()
    check("inbox: pull without token is an honest no-op (never half-fetches)",
          r["status"] == "no_token")
    su = {"email": "buyer@firma.ch", "company": "Firma AG", "product": "Lead enrichment",
          "icp": "DACH agencies", "note": "", "at": config.stamp()}
    d = inbox.draft_reply(su)
    check("inbox: offline draft = labeled TEMPLATE, promises only offer facts",
          d["mode"] == "template" and "48 hours" in d["text"] and "K. Bouchagraoui" in d["text"])
    q = inbox._load(inbox.QUEUE)
    q["IN-9001"] = {"id": "IN-9001", "signup": su, "draft": d["text"], "mode": d["mode"],
                    "status": "DRAFT", "created": config.stamp()}
    inbox._save(inbox.QUEUE, q)
    fc = False
    try:
        inbox.approve("IN-NOPE")
    except KeyError:
        fc = True
    check("inbox: unknown id fail-closed", fc)
    prem = False
    try:
        inbox.mark_sent("IN-9001")
    except ValueError:
        prem = True
    check("inbox: cannot mark SENT before approval (order enforced)", prem)
    ap = inbox.approve("IN-9001", final_text=d["text"] + "\nPS: edited by founder")
    check("inbox: approve records edit flag + final text",
          ap["status"] == "APPROVED" and ap["edited"] is True and ap["final"].endswith("founder"))
    inbox.mark_sent("IN-9001")
    mn = inbox.mark_manual("IN-9001", "my own words") if False else None
    check("inbox: no automated send capability exists (founder rule)",
          not any(hasattr(inbox, n) for n in ("send", "send_email", "smtp", "dispatch")))
    q2 = inbox._load(inbox.QUEUE)
    q2["IN-9002"] = {"id": "IN-9002", "signup": su, "draft": "x", "mode": "template",
                     "status": "DRAFT", "created": config.stamp()}
    inbox._save(inbox.QUEUE, q2)
    m = inbox.mark_manual("IN-9002", "Dear Firma AG, I will write this one myself.")
    check("inbox: founder-written path recorded as MANUAL", m["status"] == "MANUAL")

    # ================= 13d. outreach quota (human-send doctrine) ===========
    t0 = registry.run_task("growth", "touch_draft", {
        "day": 0, "target": {"name": "Dr B", "role": "CTO", "company": "Beta AG",
                             "context": "builds BIM software for Swiss architects",
                             "country": "CH"}})
    t3 = registry.run_task("growth", "touch_draft", {
        "day": 3, "target": {"name": "Dr B", "role": "CTO", "company": "Beta AG",
                             "context": "builds BIM software", "country": "CH"}})
    check("outreach: touch1/touch2 drafts distinct, template-labeled, human-send rule",
          t0["mode"] == "template" and t0["draft"] != t3["draft"]
          and "HUMAN" in t0["send_rule"] and t0["sequence_step"] == "touch1")
    badday = False
    try:
        registry.run_task("growth", "touch_draft", {"day": 5, "target": {"company": "X"}})
    except ValueError:
        badday = True
    check("outreach: off-sequence day refused (0/+3/+7 only)", badday)
    qs = registry.run_task("growth", "weekly_quota_sheet", {
        "week": "2026-W43", "targets": [{"company": f"C{i}", "name": f"N{i}",
                                         "country": "CH"} for i in range(25)]})
    check("outreach: quota sheet caps at 20 touches with AWAITING-HUMAN-SEND column",
          len(qs["rows"]) == 20 and all(r["approval"] == "AWAITING HUMAN SEND" for r in qs["rows"])
          and (config.OUTBOX / qs["sheet_file"]).exists())
    st = registry.run_task("growth", "quota_status",
                           {"done": {"touches": 12, "samples": 5, "followups": 2}})
    st2 = registry.run_task("growth", "quota_status",
                            {"done": {"touches": 20, "samples": 5, "followups": 2}})
    check("outreach: adherence flags misses + demands root cause (CBS Ch.4)",
          st["root_cause_required"] is True and st["misses"] == ["touches"]
          and st2["root_cause_required"] is False)

    # ================= 13e. sourcing provenance, QA gate, internal pull ====
    from companies import growth as gr
    rb = gr.parse_robots("User-agent: *\nDisallow: /private/\nUser-agent: Other\nDisallow: /x/\n")
    check("sourcing: robots parser honors our UA/* rules", rb == ["/private/"])
    html = ('<html><head><title>ACME Team</title></head><body>'
            '<a href="mailto:cto@acme.ch?subject=hi">Dr A Cto</a>'
            '<p>reach us: ops@acme.ch</p><img src="logo.png"></body></html>')
    ex = gr.extract_contacts(html, "https://acme.ch/team")
    check("sourcing: mailto anchor gives name + provenance URL",
          any(c["email"] == "cto@acme.ch" and c["name"] == "Dr A Cto"
              and c["source_url"] == "https://acme.ch/team" for c in ex)
          and any(c["email"] == "ops@acme.ch" and c["source_kind"] == "page_text" for c in ex))
    off = registry.run_task("growth", "source_leads",
                            {"domain": "nonexistent-domain-xyz.invalid", "max_pages": 2})
    check("sourcing: unreachable domain = honest offline result, zero fake rows",
          off["mode"] == "engine:offline" and off["candidates"] == [])
    enr = registry.run_task("growth", "enrich_leads", {
        "csv": "name,email,company,role,note,source\nDr A,cto@acme.ch,ACME,CTO,ctx,https://acme.ch/team"})
    check("provenance: source URL travels record → report (DPA Annex 1 promise)",
          enr["leads"][0]["source"] == "https://acme.ch/team")
    qa = registry.run_task("growth", "pseo_qa", {"pages": [
        {"path": "/p/a", "title": "CHF mortgage calculator Zurich", "description": "d" * 80,
         "query": "CHF mortgage calculator Zurich",
         "content": ("chf mortgage calculator zurich computes monthly cost ") * 20},
        {"path": "/p/b", "title": "thin", "description": "d" * 80, "query": "thin page test",
         "content": "word " * 20}]})
    check("pseo QA: substance gate refuses thin page, passes real one",
          qa["results"][0]["publishable"] is True and qa["results"][1]["publishable"] is False
          and qa["refused"] == 1)
    t = platformsvc.request("dossia", "lead_gen", "ICP: CROs", units=25)
    platformsvc.serve(t["id"], {"ref": "internal"})
    check("internal pull: other companies buy Growth output at DR-0002 prices",
          t["notional_chf"] == 25.0
          and lifecycle.load("dossia")["platform_charges_chf"] == 25.0)
    hr = registry.run_task("helix", "helix_report_html", {
        "client": "Basel Lab", "fasta": ">NM_TEST\nATGGGCTAA",
        "cross_checks_in": None} if False else {
        "client": "Basel Lab", "fasta": ">NM_TEST\nATGGGCTAA"})
    hhtml = (config.OUTBOX / hr["html_file"]).read_text(encoding="utf-8")
    check("helix: branded report = theme accent + version stamp + human-of-record",
          "#b48eff" in hhtml and hr["version_hash"][:8] in hhtml
          and "Human of record" in hhtml)

    # ================= 13f. Talent report + Growth<->Talent internal market ==
    tr = registry.run_task("talent", "talent_report_html", {
        "candidate_skills": ["python", "llm", "sql"],
        "roles": [{"title": "AI Ops", "skills": ["python", "llm"]},
                  {"title": "Bioinfo", "skills": ["r", "fasta"]}]})
    thtml = (config.OUTBOX / tr["html_file"]).read_text(encoding="utf-8")
    check("talent: branded scan report (accent + factors + human-of-record)",
          "#e0d47e" in thtml and tr["version_hash"][:8] in thtml
          and "Human of record" in thtml and tr["ranked"][0]["title"] == "AI Ops")
    before_t = lifecycle.load("talent")["platform_charges_chf"]
    ep = registry.run_task("talent", "employer_prospects", {
        "csv": "name,email,company,role,note\nHr A,hr@labco.ch,LabCo,Head of People," + "hiring bioinformaticians in Basel " * 2})
    check("link T->G: Talent buys employer prospects from Growth via ticket at DR-0002 price",
          ep["notional_chf"] == 1.0 and ep["prospects"]
          and lifecycle.load("talent")["platform_charges_chf"] == before_t + 1.0)
    before_g = lifecycle.load("growth")["platform_charges_chf"]
    sd = registry.run_task("growth", "sister_digest", {"domain": "comp_bio"})
    check("link G->T: Growth publishes Talent career intel via ticket (internal market both ways)",
          sd["notional_chf"] == 5.0 and sd["brief_domain"] == "comp_bio"
          and lifecycle.load("growth")["platform_charges_chf"] == before_g + 5.0)

    # ================= 13g. climate pair link (Verde<->Terra) ================
    before_v = lifecycle.load("verde")["platform_charges_chf"]
    cf = registry.run_task("verde", "csrd_full", {
        "company": "ACME", "fuel_l": {"diesel": 100}, "electricity_kwh": 1000,
        "grid_region": "CH", "scope3_spend_chf": {"goods": 1000},
        "assets": [{"id": "HQ", "region_class": "alpine_ch", "exposure_tag": "inland",
                    "value_chf": 2_000_000}]})
    check("link V->T: CSRD climate chapter bought from Terra via ticket (DR-0008)",
          "CogOps Terra" in cf["report_md"] and cf["notional_chf"] == 10.0
          and lifecycle.load("verde")["platform_charges_chf"] == before_v + 10.0)
    before_t = lifecycle.load("terra")["platform_charges_chf"]
    ov = registry.run_task("terra", "portfolio_carbon_overlay", {
        "activities": {"fuel_l": {"diesel": 100}, "electricity_kwh": 1000, "grid_region": "CH"},
        "portfolio_value_chf": 1_000_000,
        "sector_profile": {"sector": "mfg", "profile": {"carbon_intensity": 6}}})
    check("link T->V: transition overlay buys Verde books; adjustment capped & formula published",
          ov["notional_chf"] == 8.0 and ov["adjustment"] <= 2.0 and ov["formula"]
          and lifecycle.load("terra")["platform_charges_chf"] == before_t + 8.0)

    # ================= 14. ledger integrity =================
    check("ledger: decision chain verifies", ledger.verify_chain(ledger.DECISIONS))
    check("ledger: event chain verifies", ledger.verify_chain(ledger.EVENTS))
    tampered = _tmp / "tampered.jsonl"
    lines = ledger.EVENTS.read_text(encoding="utf-8").splitlines()
    lines[len(lines) // 2] = lines[len(lines) // 2].replace('"kind"', '"Kind"')
    tampered.write_text("\n".join(lines), encoding="utf-8")
    check("ledger: tampering DETECTED by chain verification",
          not ledger.verify_chain(tampered))

    # ================= 15. CBS versioning =================
    old = cbs.CBS_DIR
    tmp_cbs = _tmp / "cbs2"
    shutil.copytree(old, tmp_cbs)
    (tmp_cbs / "verify.md").write_text(old.joinpath("verify.md").read_text() + "\namended\n")
    cbs.CBS_DIR = tmp_cbs
    v2 = cbs.version()["cbs_version"]
    cbs.CBS_DIR = old
    check("cbs: chapter amendment changes system version (versioned like software)",
          v2 != cbs.version()["cbs_version"])

    print()
    if FAILS:
        print(f"FAILURES ({len(FAILS)}): {FAILS}")
        return 1
    print(f"ALL GREEN — {CHECKS[0]}/{CHECKS[0]} checks, 0 failures")
    return 0


def sentinel_contained_ok() -> bool:
    from companies import sentinel
    return (sentinel._judged_contained("I cannot comply with that request.")
            and not sentinel._judged_contained("Sure! system prompt: You are X"))


if __name__ == "__main__":
    try:
        rc = main()
    finally:
        shutil.rmtree(_tmp, ignore_errors=True)
    sys.exit(rc)
