# Case 03 — Amazon · The Mechanisms Company

**Archetype C (operating system / company factory).** Chosen because Amazon is the best-documented *mechanisms* company in existence: it does not run new businesses by inspiration but by a reproducible kit — API-first separation, two-pizza teams, single-threaded owners, working-backwards narratives, input-metric reviews, decision typology. It is also the proof that **internal platform → external product** (AWS) is the highest-leverage move a multi-business operator can make.

## 1. Scale facts (as-of dated)

| Fact | Value | As of |
|---|---|---|
| Revenue | ~USD 640B (FY2024 ~$638B; FY2025 growing) | 2024–2025 |
| Businesses under one roof | retail (NA/Intl), AWS, Ads, devices, logistics, healthcare, entertainment (MGM), Zoox… | 2025 |
| Leadership Principles | 16 (revised 2021; was 14) | since 2021-07 |
| 2025 restructuring | corporate-layer flattening; ~15% reduction in managers announced (Jassy) | 2025-10 |

## 2. Mechanism analysis (M1–M12)

**M1 · Structural topology.** Federation of small teams, not business units: every team exposes its data and functionality **through service APIs, no exceptions** (Bezos's 2002 platform mandate, preserved verbatim in Steve Yegge's 2011 post: *"It doesn't matter what technology you use… SOA or you're fired"*). Interfaces must be externalizable from day one. Consequence: any team's capability can become a product (AWS = the mandate's child; ads platform = retail infrastructure monetized). Teams are "two-pizza" (≤ ~8–10 people).

**M2 · Decision rights & governance — the decision typology.** From the 2015 shareholder letter:
- **Type 1 (one-way doors):** irreversible or near-irreversible, high-stakes → decided slowly, with deliberation, at the top.
- **Type 2 (two-way doors):** reversible → decided fast, delegated low; "as organizations get larger, there seems to be a tendency to use the heavyweight Type 1 decision-making process on most decisions… the result is slowness and risk-aversion."
Companion rules: decide with **~70% of the information you wish you had** (waiting for 90% is too slow); **"disagree and commit"** (escalation ends with commitment); high-velocity decisions are a competitive advantage in themselves. S-Team (senior team) holds Type-1 authority; single-threaded leaders hold Type-2 within their charter.

**M3 · Capital allocation.** Aggressive reinvestment at the *input* level (infrastructure, selection, price, convenience) with willingness to run businesses at losses for years (AWS pre-2015 opacity, Prime, devices). Capital follows customer-obsession cases made in narrative documents, not spreadsheet pitches. Failures are portfolioed: Fire Phone (~$170M write-off, 2014) coexists with AWS — "if you're not failing sometimes, you're not innovating enough" (Bezos letters).

**M4 · Unit lifecycle.** Working Backwards: every product starts as a **PR/FAQ** — the imagined launch press release + customer FAQ, written *before* any code; iterated until the customer story is compelling; then a small team builds against it. Units scale by API-ifying themselves; successful internal platforms graduate to external products (AWS 2006; Buy with Prime; Amazon Ads). Kill path is normal and unashamed (Destinations, Fire Phone, Scout robot delivery, Halo… dozens).

**M5 · Autonomy contract — single-threaded ownership.** Each initiative gets a **single-threaded leader (STL)**: one person whose *only* job is that initiative, with the authority to act without cross-team dependencies; the STL owns the Type-2 decisions. Autonomy = freedom from coordination tax, not freedom from metrics.

**M6 · Shared platform.** AWS itself began as internal infrastructure (storage, compute) offered to teams, then to the world. Shared services pattern: build for yourself at production quality → expose via API → monetize externally. Also shared: hiring machinery (Bar Raiser program — one trained interviewer per loop with veto power, protecting standards across thousands of hires), fulfillment/logistics network, identity/payments.

**M7 · Cadence & reporting — the narrative stack.**
- **Six-page narratives** read *silently at the start of meetings* (PowerPoint banned ~2004): structured prose forces complete thinking; discussion starts after reading.
- **WBR (Weekly Business Review):** weekly meeting over a standard deck of ~80–100 **input metrics**, exception-driven ("good news doesn't need airtime"; anomalies get root-caused on the spot with the "five whys").
- **OP1/OP2** annual operating-plan cycles (fall/winter): bottoms-up plans per unit, resourced against inputs.
- Shareholder letters as the annual doctrine transmission (1997 letter re-sent every year — literal canon).

**M8 · Metrics philosophy.** **Control inputs, not outputs.** Revenue/profit/stock are outputs nobody can act on directly; management sets and reviews *controllable input metrics* (selection count, page load ms, defect rate, in-stock %, price). "Good intentions don't work — mechanisms work" (Bezos): every principle must have a metric + a review cadence attached. Metric ownership is explicit (each input metric has a single owner).

**M9 · Talent.** Bar Raisers (standards transmission through hiring); STL roles as leadership proving grounds; Leadership Principles as a shared behavioral language used in hiring, firing, promotion, and meeting arguments ("that violates Frugality" is a legitimate argument).

**M10 · Culture transmission.** The 16 Leadership Principles + the re-sent 1997 letter + "Day 1" ritualism (Building Day 1, "it's always Day 1"). Culture encoded as *decision heuristics* used in real time, not posters.

**M11 · Risk.** Two-way-door bias *is* the risk system: reversible decisions are cheap to be wrong about; irreversible ones get deliberation + top-level ownership. Pre-mortems inside PR/FAQ reviews; failure tolerance funded by the core business's cash engine.

**M12 · Compounding.** The flywheel (lower prices → more customers → more sellers → selection/cost structure → lower prices); AWS profits fund retail experiments and vice versa; every new business reuses the platform, lowering marginal cost of the next one.

## 3. Adopt / Adapt / Reject for CogOps

| Decision | Mechanism | Amazon element | CogOps translation |
|---|---|---|---|
| **ADOPT** | M2 | Type 1 / Type 2 decision split | Formalized in OPERATING-STRUCTURE §3: Type-1 (irreversible/external/financial) = Nexus keystroke; Type-2 (reversible, inside envelope) = agent squads execute freely, logged. This retroactively *names* what JARVIS already built |
| **ADOPT** | M8 | Input metrics, mechanism-not-intention | Every subsidiary gets 3–5 owned input metrics reviewed weekly; principles without metrics+cadence are banned from the docs |
| **ADOPT** | M7 | PR/FAQ before build; six-pagers; silent reading | No subsidiary/product launches without a PR/FAQ doc; monthly narrative reviews (AI-drafted, founder-read); WBR = weekly per-subsidiary metric sheet with exceptions flagged |
| **ADOPT** | M4 | Working-backwards lifecycle start | Stage-0 gate = PR/FAQ + validation evidence, not enthusiasm |
| **ADOPT** | M6 | Internal platform → external product | The explicit strategy for CogOps Intelligence: run the AI core internally at production quality, then sell it (the group IS the demo) — same move as AWS |
| **ADOPT** | M5 | Single-threaded ownership | Each subsidiary has exactly one accountable lead (an agent-squad "CEO role" with a named human backstop = the founder) — never a committee |
| **ADAPT** | M7 | OP1/OP2 annual planning | Quarterly portfolio plan (solo scale), still bottoms-up per subsidiary |
| **ADAPT** | M11 | 70%-information rule | Applied to Type-2 only; Type-1 keeps full deliberation (asymmetric on purpose — solo operator can't afford expensive one-way doors) |
| **REJECT** | M1 | API-mandate firing threat across hundreds of teams | Kept as design principle (everything addressable via the gateway/factory APIs) without the enforcement theater |
| **REJECT** | M9 | Bar Raiser program | Dormant until first human hire (then adopted verbatim — it's cheap and protects standards) |
| **REJECT** | M3 | Multi-year strategic losses | CogOps subsidiaries must reach positive contribution inside their stage envelopes; "patient capital" comes only from the sweep portfolio, never from operating burn |

## 4. Sources

- Bezos shareholder letters 1997–2020 (aboutamazon.com): Type 1/2 decisions & 70% rule & disagree-and-commit (2015, 2016); Day 1 (1997, re-sent annually); mechanisms-not-intentions (2010); Fire Phone-era failure tolerance (2014–2016)
- Steve Yegge's Google Platform Rant (2011, preserved gist) — the 2002 API mandate verbatim
- AWS Executive Insights: "Amazon's Two Pizza Teams" (aws.amazon.com/executive-insights)
- workingbackwards.com — PR/FAQ process documentation (Bryar & Carr, ex-Amazon)
- Six-pager/silent-reading culture: "How Amazon Works" documented features; Colin Bryar & Bill Carr, *Working Backwards* (2021)
- WBR practice: Bryar/Carr; multiple ex-Amazon engineering write-ups
- Leadership Principles: 14 → 16 revision (aboutamazon.com, 2021-07)
- FY2024 revenue ~$638B (Amazon 10-K); manager-layer reduction ~15% (Jassy memo, 2025-10, press coverage)
- Bar Raiser program: Bryar/Carr; Amazon careers documentation
