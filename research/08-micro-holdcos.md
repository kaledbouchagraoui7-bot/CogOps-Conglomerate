# Case 08 — Micro-Holdcos · Levelsio Portfolio & Tiny — One Person, Many Companies

**Archetype D (solo/micro portfolios).** Chosen because these are the only *empirically verified* answers to the actual constraint CogOps has: what can **one human** run? Levelsio proves the build-side (solo portfolio of live products, public numbers); Tiny proves the operate/acquire-side (minimal HQ, maximal autonomy, ~$300M sales approached with a tiny center).

## 1. Scale facts (as-of dated)

| Portfolio | Facts | As of |
|---|---|---|
| **Pieter Levels (@levelsio)** | Solo, no employees, no VC, no meetings; 70+ product attempts over ~12 years ("12 startups in 12 months", 2014–2016); current earners: **Nomad List ~$700K ARR · Remote OK ~$3.4M revenue/yr · PhotoAI (AI headshots) multi-$M cumulative, ~$100K+/month range**; public open-startup dashboards; deliberately primitive stack (PHP/jQuery/SQLite/Stripe on single servers) | podcast notes & interviews, 2025-07 |
| **Tiny (Andrew Wilkinson & Chris Sparling, Victoria BC)** | From design agency MetaLab (2003) to holdco: **"I've run 75 businesses"** (Wilkinson); portfolio approaching **~$300M yearly sales, valued >$1B at peak**; known assets: Dribbble, MetaLab + dozens of small internet businesses; philosophy: acquire, **maximum autonomy / minimum interference**, hold indefinitely; tiny HQ (a handful of people); Nasdaq listing via SPAC (2023, ticker TINY) | Lenny's Podcast 2025-07; Wilkinson's *Never Enough* (2023) |

## 2. Mechanism analysis (M1–M12)

**M1 · Topology.** Levelsio: flat portfolio of products under one personal brand/infrastructure — products, not companies (no legal separation). Tiny: legal companies under a minimal holding; each keeps name, team, customers, P&L.

**M2 · Decision rights.** Levelsio: all rights in one person, decisions made in hours (ship/kill). Tiny: HQ holds capital + buy/sell; company teams hold *everything operational* — Wilkinson's rule is famous: no mandatory meetings, no forced processes, no "synergy projects"; interference is considered a failure mode.

**M3 · Capital allocation.** Levelsio: self-fund from product revenue; spend near-zero (infrastructure <$1K/mo class); profits to personal investment. Tiny: acquire with cash/stock from profits and raised capital; allocate by letting good businesses keep their cash; buy only businesses that already work (profitable, owner-tired, moaty niches — the same profile Constellation hunts, at micro scale).

**M4 · Lifecycle.** Levelsio: **ship fast, kill fast** — most of 70+ attempts died within weeks/months; survivors are those users paid for immediately. No stage gates — the market is the gate. Tiny: acquire mature → hold → occasionally sell; birth-stage is outsourced to *other people's* entrepreneurial lives.

**M5 · Autonomy contract.** Tiny's is the cleanest written-in-practice contract in this corpus: *we will not touch your operations, ever; you keep running the business you built; we provide patient capital and leave you alone.* Levelsio's self-contract: no employees → nothing to manage → 100% equity, zero HR risk, total speed.

**M6 · Shared platform.** Levelsio: one personal infra stack reused by every product (auth, payments, hosting patterns, audience/distribution via social following — **the audience is the platform**). Tiny: minimal HQ services (legal, finance, M&A) — deliberately thin.

**M7 · Cadence.** Levelsio: public dashboards (open metrics) = cadence + marketing fused; building in public replaces reporting. Tiny: quarterly light financials; annual portfolio review; otherwise silence as policy.

**M8 · Metrics.** Levelsio: revenue (public, per product), growth rate, his own time-per-product. Tiny: EBITDA/profit per company, owner-dependence (a business needing its owner isn't an asset), management retention.

**M9 · Talent.** Levelsio: none — contractors where unavoidable; AI increasingly substitutes labor (his stated direction: one person + AI agents ≈ old 10-person startup). Tiny: keep acquired management; HQ hires extremely selectively (culture > credentials; "don't be an asshole" as an operating principle per *Never Enough*).

**M10 · Culture.** Levelsio: transparency (public numbers), speed, anti-fragile leanness — transmitted by the persona itself. Tiny: autonomy-respect transmitted by *what HQ refuses to do* (no meetings ritual, no integration playbooks) — culture as restraint.

**M11 · Risk.** Levelsio: portfolio of tiny bets — any single product death is noise; no debt, no payroll = no forced outcomes; platform risk (Twitter/X audience dependence, API changes) is his main unhedged exposure — a documented lesson. Tiny: diversification across 75 businesses; no leverage games; owner-dependence screening prevents buying fragile assets.

**M12 · Compounding.** Levelsio: audience + code reuse + cash → each new product launches cheaper with bigger initial distribution. Tiny: profits → more acquisitions → more profits (Constellation flywheel at micro scale); brand of "we don't interfere" → better deal flow (owners *choose* Tiny).

## 3. Adopt / Adapt / Reject for CogOps

| Decision | Mechanism | Micro-holdco element | CogOps translation |
|---|---|---|---|
| **ADOPT** | M5 | Tiny's non-interference contract | Verbatim spirit in the Autonomy Contract (§6): once a subsidiary passes its stage gates, the center interferes only via gates — never ad-hoc |
| **ADOPT** | M4 | Ship fast / kill fast; market as gate | Stage-1 validation is *market contact within weeks* (pre-sales/waitlists), never internal debate |
| **ADOPT** | M6 | Audience-as-platform | Growth's media network (per-domain newsletters) = the distribution platform every new subsidiary launches into — built before, not after, company #2 |
| **ADOPT** | M11 | No debt/no payroll → no forced outcomes | Group invariant: zero debt at holding level; cost base kept ≤ sweep-portfolio-safe levels; the 6-month cash fortress (Berkshire M3) makes kills always voluntary |
| **ADAPT** | M7 | Open dashboards | Selective transparency: public metric dashboards per subsidiary where it *markets* (Growth decides); financials stay private |
| **ADAPT** | M9 | One person + AI agents ≈ 10-person startup | This IS the CogOps thesis — formalized: every headcount question must first pass "can an agent squad + CBS do this?" (default yes; exceptions via gate) |
| **ADAPT** | M3 | Tiny's acquire-don't-build option | Phase-2 doctrine (with Constellation/Danaher): when sweep capital accumulates, buy tiny profitable niche software/services instead of building — CBS deploys into acquisitions |
| **REJECT** | M1 | Products-not-companies (Levelsio's zero legal separation) | Rejected for liability reasons: CogOps subsidiaries need legal separation once they contract with clients (Swiss GmbH per company, §9 file) |
| **REJECT** | M6 | Deliberately primitive stack as identity | Keep *boring* stack (CF Pages + Supabase) but not primitive: the platform is engineered (gate, audit trail, CBS) because money/compliance flow through it |

## 4. Sources

- podcastnotes.org — "Pieter Levels on $3M Solo Startups" (Cheeky Pint w/ John Collison, 2025-07-11): Nomad List ~$700K ARR; Remote OK ~$3.4M revenue; PhotoAI figures; never-raise-VC stance
- Lenny's Newsletter — "I've run 75 businesses" (Andrew Wilkinson, 2025-07-03): portfolio approaching ~$300M yearly sales; >$1B valuation at one point
- YouTube — "How I Bought 35+ Businesses and Built a $240M HoldCo At 38" (Wilkinson interview): 30+ business holdco operating lessons
- Andrew Wilkinson, *Never Enough* (2023): Tiny philosophy — autonomy, no-meetings culture, acquisition criteria, MetaLab origin
- levels.io open-startup dashboards (public, continuous); "12 startups in 12 months" archive (2014–2016)
- Tiny SPAC listing (Nasdaq: TINY, 2023): press coverage
- Levelsio AI-leverage direction: public posts/interviews 2023–2025 (AI-built products, no employees)

*Fact-confidence note: Levelsio revenue figures are self-published (dashboard/interview-grade, not audited) — cited as-of 2025-07 and marked accordingly. Tiny figures are podcast-stated (owner-grade, not audited). Both are the standard of evidence available for private micro-portfolios and are used only where owner-reported numbers suffice.*
