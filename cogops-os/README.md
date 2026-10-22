# CogOps OS — the Operating Structure as Running Code

> The mechanisms of [`../structure/OPERATING-STRUCTURE.md`](../structure/OPERATING-STRUCTURE.md) implemented as an executable system: **agents and an automaton instead of employees**, one human keystroke on every Type-1 decision. Pure Python 3.10+ **standard library only** — runs anywhere, no install.
> Lineage: gate/mission/guard patterns descend from the JARVIS automaton (repo `Jarvis`, commits through `6c7429a`); verification discipline from the comp-bio portfolio; mechanisms from the benchmark research in `../research/`.

## Quickstart

```bash
cd cogops-os
python3 selftest.py                 # 89-check regression suite → ALL GREEN (run before any change)
python3 cogops.py status            # group dashboard
python3 cogops.py companies         # the ten, with stages & engine tasks
python3 cogops.py run verde carbon_account --params '{"fuel_l":{"diesel":340},"electricity_kwh":4200,"grid_region":"CH"}'
python3 automaton.py cycle          # one operating cycle (cadence + lifecycle sweep + missions)
python3 automaton.py mission set helix "keep validating until done"
python3 cogops.py audit             # the Auditing Agent: invariants + ledger chains + CBS conformance
```

Runtime state (ledgers, gates, companies, outbox artifacts) lives in `cogops-os/runtime/` by default — override with `COGOPS_RUNTIME_DIR`. All configuration is env-driven (`COGOPS_FREEZE_CLOCK` for byte-deterministic artifacts; see `config.py`).

## The founder loop (how a human runs ten companies in ≤2 h/week)

```
python3 cogops.py gate list          → the Type-1 queue (evidence packs attached)
python3 cogops.py gate approve GA-…  → the keystroke (G3 needs --confirm "cogops approves")
python3 cogops.py sheet              → weekly WBR-lite (exceptions only)
python3 cogops.py memo <slug>        → monthly narrative (candor-first)
python3 cogops.py letter [year]      → annual Owner Letter
```

Two-step gate flow everywhere: an action **stages** → founder **approves** → re-running the command **consumes** the approval and executes. The system never self-approves (invariant I3, fail-closed).

## OS section → module map

| OS § | Mechanism | Module | Proof (selftest) |
|---|---|---|---|
| §1 Charter / §10 CBS | versioned playbook, immersion packs | `cbs.py` + `cbs/*.md` | chapter amendment changes version hash |
| §2 Topology | registry of ten, divisions-first | `registry.py`, `companies/*` | boot: 10 companies, stages match §13 |
| §3 Decision rights | Type-1/2/3, G1/G2/G3, delegated caps, decision ledger | `gates.py`, `ledger.py` | fail-closed on unknown id; G3 phrase; consume-on-approve |
| §4 Capital | fortress (I2), deployment ladder, scoreboard, no-debt-by-absence | `capital.py` | ladder order; fortress blocks; dormant-Phase-2 flag |
| §5 Lifecycle | stages 0–5, CHF envelopes, time-boxes, evidence gates, **kill-as-win** | `lifecycle.py` | PR/FAQ gate; evidence unlocks; KILL_WIN + credibility |
| §6 Autonomy contract | NEVER-rules as runtime checks; three rights as data | `autonomy.py` | all 5 never-rules block; pull-only verified |
| §7 Platform | pull-only service catalog, notional charging (I7) | `platformsvc.py` | tickets charge company P&L; unknown service refused |
| §8 Cadence | WBR-lite, monthly memos, PD-lite, Owner Letter | `cadence.py` | deterministic artifacts; candor-first structure |
| §9 Metrics | SPQP scorecards, owned inputs, floors, portfolio health | `metrics.py` | ownerless metric refused; breach flags |
| §10 Workforce | squads from 7-universe roster, STL roles, missions, Auditing Agent | `squad.py`, `data/agent_roles.json`, `automaton.py` | out-of-squad role refused; mission blocks honestly |
| §11 Risk | classification rules, pre-mortems in PR/FAQ, tamper-evident ledgers | `gates.py`, `ledger.py` | hash-chain verification; tamper detected |
| §12 Compounding | 30% sweep → Pillar 3a + guarded fractional DCA; Swiss guard (I10) | `capital.py` | 100k fresh-capital passes; churn sells blocked; 1-cent floor |
| §13 Instantiation | ten company engines (below) | `companies/*.py` | one+ smoke check per engine |
| §14–15 Invariants/DR | audit command enforces I1–I12; frozen-clock determinism | `cogops.py audit`, `config.py` | audit verdict PASS on clean state |

## Company engines (state-of-the-art per task, honest modes)

| Company | Engine tasks (real algorithms, not mockups) |
|---|---|
| **intelligence** | `deploy_client` (orchestrates platform tickets) · `automation_audit` (process→agent map with human-gate placement) · `kb_ground` (KB-first grounding manifests) |
| **sentinel** | `audit_run` (22-control baseline: CIS-flavored + nDSG/GDPR, scored, remediation) · `ai_security_review` (6-probe injection battery + config checks) · `heartbeat` |
| **capitalco** | `backtest` (guard-checked-in-loop DCA, deterministic hash) · `factor_brief` (tercile Welch) · `treasury_policy` (mirrors live config — no drift) |
| **helix** | `sequence_qc` (GC/ORF both strands + cross-check gate) · `table1` (audit-trailed cleaning + SciPy-free validated stats) · `lit_surveil` (PubMed→EuropePMC fallback, PMID-traceable) |
| **dossia** | `m4_assemble` (ICH M4 CTD pack — never invents clinical content) · `surveillance_feed` · `qc_checklist` (ALCOA+) |
| **medtech** | `mdr_doc_tree` (Annex II/III, class-scoped, signoff flags) · `alcoa_log` (append-only experiment trail) · `imaging_pipeline_spec` (research-use only) |
| **verde** | `carbon_account` (GHG Protocol S1/S2/S3-lite, sourced factors) · `csrd_lite_report` (limitations section mandatory) |
| **terra** | `physical_risk` (**labeled heuristic v0**) · `transition_risk` (TCFD levers) · `esg_brief` (≥5 sources enforced) |
| **growth** | `enrich_leads` (validate/dedupe/disposable-incl-subdomains/score + per-prospect copy) · `pseo_pages` (byte-deterministic page factory + sitemap) · `newsletter_issue` |
| **talent** | `curriculum` (gap-evidence-sourced tracks) · `match` (explainable cosine matcher) · `market_brief` (as-of-dated analysis quotes) |

**Statistics kernel** (`statsnr.py`): Welch t-test and χ² from Numerical Recipes (series + continued-fraction, correct initialization per the portfolio's FIXES.md #2) — validated in-suite against textbook critical values (χ²(3.841, df1)→p≈0.05; t=−1, df8→p≈0.3466; 2×2 no-Yates χ²=20/3→p≈0.00982).

**Honesty rules (non-negotiable, JARVIS lineage):** every artifact carries a `mode` label (`kb` / `llm:<provider>` / `engine` / `template` / `engine:heuristic-v0` / `offline`). With no API keys, everything degrades to labeled templates — the system never fakes AI, never invents numbers, and every published figure carries as-of + source (invariant I11). Emission factors in `data/emission_factors.json` are explicitly **placeholder-grade** and must be replaced with a licensed factor set before client-facing statements.

## Environment

| Var | Purpose |
|---|---|
| `COGOPS_RUNTIME_DIR` | state directory (default `./runtime`) |
| `COGOPS_FREEZE_CLOCK` | epoch seconds → byte-deterministic artifacts (tests) |
| `COGOPS_CONFIRM_PHRASE` | G3 dual-confirm phrase (default `cogops approves`) |
| `OPENROUTER_API_KEY` / `OPENROUTER_MODELS` / `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | LLM chain (absent ⇒ honest template mode) |
| `ENV_STAGE*` / `FORTRESS_MONTHS` / `MONTHLY_FIXED_COSTS_CHF` / `SWEEP_PROFIT_SHARE` | doctrine tunables (DR-governed defaults in `config.py`) |

## Anti-snowball protocol (OS §15) — for any future session

1. `python3 selftest.py` must be **ALL GREEN (89/89)** before and after any change.
2. Never weaken a selftest to make it pass; fix the mechanism or write a Decision Record.
3. Money/gate logic changes require new regression checks in the same commit.
4. `python3 cogops.py audit` must return verdict PASS on a clean runtime.
