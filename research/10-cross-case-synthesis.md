# Cross-Case Synthesis — The Comparison Matrix and the Design Decisions

> The analytical hinge of the corpus: one matrix (12 mechanisms × 8 benchmarks), one scale-translation table, one anti-pattern list, and the complete adoption ledger that `../structure/OPERATING-STRUCTURE.md` instantiates.

## 1. The mechanism matrix

How each benchmark actually solves each mechanism (durable facts, sources in the case files):

| M# | Mechanism | Berkshire | Alphabet | Amazon | Constellation | Danaher | Haier | Studios | Micro-holdcos |
|---|---|---|---|---|---|---|---|---|---|
| M1 | Topology | Holding + autonomous opcos + equity portfolio | Holding + segments + independent-brand Bets + X factory | Federation of API-separated two-pizza teams | Holding → 6 operating groups → hundreds of niche firms | Holding → opcos → businesses, + horizontal DBS layer | Platform center + ~4,000 user-facing MEs | Small studio center → born-independent companies | Flat portfolio (products) / thin HQ → 75 companies |
| M2 | Decision rights | Center: capital, unit CEOs, buy/hold; units: everything else | Center: funding, Bet CEOs, grad/kill; Bets: roadmap | Type-1 top & slow; Type-2 delegated & fast; STL owns charter | Center: doctrine, spin-offs; **acquisition authority delegated** into groups with caps | Center: portfolio boundaries + the System; units: execution inside DBS | MEs hold three rights (decision/hiring/comp); platform: brand/capital/compliance | Studio-all during incubation; CEO-all post-spin | One person (Levelsio) / capital-only HQ (Tiny) |
| M3 | Capital allocation | Deployment ladder; cash fortress; never force deployment | Milestone funding; external rounds for validation; core cross-funds bets | Input-level reinvestment; tolerate failures portfolio-wide | FCF/share scoreboard; funnel discipline; no synergy premiums | Buy → improve with DBS → reinvest or exit industry | Tranche funding; ME external VC allowed; user-paid surplus sharing | Staged tranches against evidence; ~3% idea→company survival | Self-fund from revenue; acquire profitable niches (Tiny) |
| M4 | Lifecycle | Buy finished, hold forever (no kills) | **Full machine**: X → Bet → external capital → graduate/spin/IPO-track → kill | PR/FAQ → team → scale → API-productize or kill | Acquire → decentralize → reinvest → optionally list (Topicus, Lumine) | Acquire → DBS immersion → improve → retain/spin | ME born from a "dan" → scale → entity/IPO or dissolve (continuous) | Idea → screen → validate → build → spin-out → exit/kill | Ship fast/kill fast (Levelsio); acquire-and-hold (Tiny) |
| M5 | Autonomy contract | Written canon: ops freedom ↔ capital & integrity to center | Independence lasts as long as milestones do | STL freedom from coordination tax ↔ input-metric accountability | Keep name/team/customers; reporting & doctrine to center | *What* is local, *how* (DBS grammar) is universal | Autonomy **in the market**, never from users | Full autonomy post-spin; studio leverage = capital+services only | **Non-interference as identity** (Tiny); self-contract (Levelsio) |
| M6 | Shared platform | Minimal: capital + permanence credibility | Infra (compute/maps/cloud), corp functions, GV, brand halo | APIs, Bar Raiser hiring, fulfillment, AWS-from-internal | Deal funnel machinery, treasury, exec development | DBS tools + DBS Office + deployed DBSL coaches | Supply chain/mfg/HR/IT/COSMOPlat as pull-services | Shared build teams + P-suite services + playbooks | Audience+code reuse (Levelsio); near-zero HQ (Tiny) |
| M7 | Cadence | Annual letter + meeting; minimal routine reporting | Quarterly segments; milestone reviews per Bet | WBR weekly input metrics; six-pagers; OP1/OP2; silent reading | Quarterly reporting; annual letter; allocation reviews | Policy Deployment; daily boards; PQLs; leader standard work | Market-frequency results per ME; no management-chain meetings | Weekly incubation kill/scale reviews; tranche gates | Public dashboards (Levelsio); quarterly-light (Tiny) |
| M8 | Metrics | Intrinsic value/share; op earnings; float cost | Stage-appropriate: risk-retired → traction → FCF | **Input metrics**; mechanisms-not-intentions | **FCF/share**; retention; deal-return vs hurdle | 4P: People→Plan→Process→Performance | User value only; users pay the metric | Evidence metrics pre-revenue; kill-rate health | Revenue-in-public; owner-dependence; EBITDA |
| M9 | Talent | Buy & keep unit CEOs; simple unit-tied comp | Bet CEOs from market; founder voting control | Bar Raisers; STL proving grounds; LPs as hiring language | Internal allocator pipeline; group presidents for decades | DBS immersion mints leaders; internal CEO pipeline | Leaders emerge by proposing a dan; members pick MEs | EIR bench; **CEO-at-spin-out** | None (Levelsio); keep acquired management (Tiny) |
| M10 | Culture | Owner's Manual + 60 yrs letters (written canon) | Pluralism under one capital doctrine | 16 LPs + 1997 letter re-sent yearly | Letters + promoted-allocator culture | **DBS: culture as deployable artifact** — survives spins/founders | Market mechanism as culture; rendanheyi vocabulary | Playbooks (Rocket manuals; Idealab heuristics) | Persona/transparency (Levelsio); restraint (Tiny) |
| M11 | Risk & kills | Never risk ruin; cash fortress; no group leverage | Time-boxed capped bets; **kill bonuses**; affordable-by-construction burn | Two-way-door bias; pre-mortems; failure tolerance | Diversification across niches; price discipline; no synergy bets | Standard work + PSP escalation; spin-offs cap complexity | Small MEs, tranche-funded, dissolved early | Tranche caps; pre-committed kill authority; legal separation | No debt/no payroll → no forced outcomes |
| M12 | Compounding | Float + retention ladder, 60 yrs | Cash engine funds optionality; winners compound core | Flywheel; internal platform → external product | FCF → acquisitions → FCF flywheel (forced outward) | System improves per kaizen; mints leaders | Successful MEs thicken platform; ecosystem attracts outsiders | Exits recycle capital; alumni deal-flow; playbook learns | Audience+cash reuse; autonomy brand → deal flow |

## 2. Scale translation — how each borrowed mechanism survives the shrink to solo+AI

The #1 snowball risk in this whole project is copying a mechanism whose *precondition* (scale, staff, capital) CogOps lacks. Every adoption was translated through this table; anything that couldn't be translated was rejected:

| Big-org mechanism | Precondition at source | Solo+AI translation | Where |
|---|---|---|---|
| 25-person HQ governing 300k employees (Berkshire) | Trustworthy subsidiary CEOs | Agent squads as "managers" under CBS + gates; founder = the 25-person HQ | OS §2, §10 |
| Milestone funding of Bets (Alphabet) | $B cash engine | CHF stage envelopes (0–500 / ≤2k / monthly caps), founder-keystroke releases | OS §5 |
| Kill bonuses (Alphabet X) | Large teams needing incentives | Kill logged as WIN in decision ledger; squad earns envelope credibility | OS §5, §11 |
| WBR with 80–100 metrics (Amazon) | Analyst teams | AI-generated weekly metric sheet per subsidiary; exceptions-only review; 3–5 input metrics (not 100) | OS §8 |
| Six-pagers + silent reading (Amazon) | Meeting culture | Monthly narrative memo per subsidiary: AI-drafted, founder-read; PR/FAQ mandatory pre-launch | OS §5, §8 |
| Delegated acquisition caps (Constellation) | Group presidents | Delegated **spend caps** per stage; above cap = Type-1 gate | OS §3 |
| DBS immersion (Danaher) | 3-day human training | CBS loaded into squad context at formation; Auditing Agent = standing DBSL | OS §10 |
| Three rights per ME (Haier) | Labor market | Squad rights inside envelope: decisions (Type-2), agent-role staffing (propose from 110-hierarchy), budget-credibility | OS §6 |
| Studio funnel 5,000→150 (Studios) | Shared build teams | Funnel is agent-run & cheap; **build slots are the scarce resource: ≤2–3 incubations/quarter** | OS §5 |
| Audience-as-platform (Levelsio) | Personal brand | Growth's per-domain media network built BEFORE company #2 launches | OS §7 |
| Non-interference contract (Tiny) | Trusted acquired owners | Autonomy contract: post-gate, center acts only through gates | OS §6 |
| Spin-off-by-listing (Constellation/Alphabet) | Capital markets | Legal-entity spin-out (GmbH) as Stage-4+ event per Swiss path | OS §12, research/09 |

## 3. Anti-patterns — why conglomerates fail, and the standing defenses

The conglomerate discount is real; most multi-business groups destroy value. Documented failure modes → CogOps defenses (each defense is a numbered invariant in OS §14):

| Failure mode (observed at) | Mechanism of decay | CogOps defense |
|---|---|---|
| Cross-subsidy fog (GE-class) | Losers hide inside winners; capital flows to noise | Per-subsidiary standalone P&L from day 1; **no synergy counting** in launch cases (Constellation M3); internal work billed at notional market terms (Haier M1) |
| Bureaucratic ossification (Amazon's warning; Rocket's centralization) | Type-2 decisions migrate upward; coordination tax | Two-way-door default at squad level; center touches only gates; cadence = exceptions-only (Amazon M2/M7) |
| Overpayment for "strategic" deals (classic holdco sin) | Synergy premiums, empire motives | Price/ROI hurdles; Phase-2 acquisitions only at FCF-hurdle prices (Constellation M3) |
| Complexity creep (Danaher's answer: spin) | Units too big/diverse for one system | Two legal layers max; spin-out trigger list (research/09 §3); kill-rate reviewed quarterly (Studios M8) |
| Culture dilution on replication (Rocket's standards erosion) | Process transmitted, taste not | CBS transmits standards *with* verification discipline (FIXES-method: reproduce→fix→verify); Auditing Agent reviews against CBS, not just P&L |
| Platform becomes overlord (Haier's warning inverted) | Shared services start commanding | Pull-only platform rule with teeth: platform never pushes process into a subsidiary (Alphabet M6, Haier M6) |
| Founder single-point-of-failure | One human, all Type-1 rights | Documented decision rights + CBS + Owner's Manual + decision ledger = the group runs on *text*, not memory; succession-by-documentation (Berkshire M10) |
| Ruin risk (any leveraged holdco) | Forced selling at the bottom | Zero holding debt; 6-month cash fortress; sweep under compliance guard — kills always voluntary (Berkshire M11, Levelsio M11) |

## 4. The adoption ledger (complete, with lineage)

Every structural element of `../structure/OPERATING-STRUCTURE.md` traces to exactly one or more rows here — nothing in the structure exists without lineage (methodology rule #5):

| OS section | Structure element | Copied/adapted from | Mechanism |
|---|---|---|---|
| §1 Charter | Owner's Manual-style written canon, candor-first | Berkshire M10 | M10 |
| §2 Topology | Holding + 10 subsidiaries (divisions-first legally) + platform layer | Alphabet M1 + Haier M1 + Swiss path (research/09) | M1 |
| §3 Decision rights | Type-1/2/3 taxonomy; delegated spend caps; Nexus keystroke = ultimate Type-1 | Amazon M2 + Constellation M2 + Berkshire M2 | M2 |
| §4 Capital doctrine | Deployment ladder; cash fortress (6-mo); FCF-per-company scoreboard; no synergy counting | Berkshire M3 + Constellation M3 | M3 |
| §5 Lifecycle | Stages 0–5 with envelopes & gates; PR/FAQ entry; evidence metrics; kill-as-win; external capital at Stage 4 | Studios M4 + Alphabet M4 + Amazon M4 | M4 |
| §6 Autonomy contract | Post-gate non-interference; three-rights translation; center's reserved rights | Tiny M5 + Haier M2/M5 + Berkshire M5 | M5 |
| §7 Platform | Pull-only shared services catalog; internal-platform→external-product rule; audience-first | Alphabet M6 + Amazon M6 + Levelsio M6 | M6 |
| §8 Cadence | Weekly WBR-lite; monthly narratives; quarterly PD-lite + portfolio review; annual Owner Letter | Amazon M7 + Berkshire M7 + Danaher M7 | M7 |
| §9 Metrics | Input metrics per subsidiary (3–5, owned); SPQP scorecard order; user-paid value first | Amazon M8 + Danaher M8 + Haier M8 | M8 |
| §10 Workforce | CBS (deployable system); squad-CEO roles; immersion-on-entry; Auditing Agent = DBSL; Bar-Raiser dormancy | Danaher M10/M9 + Studios M9 + Amazon M9 | M9/M10 |
| §11 Risk | Fail-closed gates; tranche caps; kill-rate health; pre-mortems in PR/FAQ | Alphabet M11 + Studios M11 + Amazon M11 | M11 |
| §12 Compounding | Sweep → ladder; entity spin-outs as graduation; Phase-2 acquisition doctrine | Berkshire M12 + Constellation M12/M4 + Tiny M3 | M12 |
| §13–15 | Ledger, invariants, change control | Meta-mechanism (methodology rule 5) + Danaher "system versioning" | — |

---
*Cross-case synthesis v1.0, 2026-10-22. Case files: `01`–`08`; legal frame: `09`. Instantiation: `../structure/OPERATING-STRUCTURE.md`.*
