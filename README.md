# CogOps Group — The Conglomerate

> ## Repository contents
> | Document | What it is |
> |---|---|
> | **this file** | The blueprint v1.0 — the conglomerate and what each company does |
> | [`research/00-methodology.md`](research/00-methodology.md) | How benchmarks were selected & analyzed (12-mechanism frame, evidence rules) |
> | Case analyses — each with structure anatomy + adopt/adapt/reject decisions for CogOps: [01 Berkshire Hathaway](research/01-berkshire-hathaway.md) · [02 Alphabet](research/02-alphabet.md) · [03 Amazon](research/03-amazon.md) · [04 Constellation Software](research/04-constellation-software.md) · [05 Danaher (DBS)](research/05-danaher.md) · [06 Haier (Rendanheyi)](research/06-haier.md) · [07 Venture Studios](research/07-venture-studios.md) · [08 Micro-Holdcos](research/08-micro-holdcos.md) | The best existing companies that do what CogOps will do — decoded into 12 mechanisms each |
> | [`research/09-swiss-holding-law.md`](research/09-swiss-holding-law.md) | The Swiss legal frame: entity forms, holding/participation exemption, naming, VAT, entity-evolution path |
> | [`research/10-cross-case-synthesis.md`](research/10-cross-case-synthesis.md) | The comparison matrix (12 mechanisms × 8 benchmarks), scale-translation table, anti-pattern defenses, adoption ledger |
> | [`structure/OPERATING-STRUCTURE.md`](structure/OPERATING-STRUCTURE.md) | **The operating system v1.0** — topology, decision rights, capital doctrine, lifecycle, autonomy contract, platform, cadence, metrics, workforce (CBS), risk gates, compounding, ten-company instantiation, invariants, change control |
> | [`structure/decisions.md`](structure/decisions.md) | Decision Records (append-only) — DR-0001 profit split · DR-0002 internal prices · DR-0003 brand architecture · DR-0004 single-entity doctrine · DR-0005 Growth live validation |
> | [`ROADMAP.md`](ROADMAP.md) | Blueprint → real business: the founder's plan with owners (**YOU** / **ME** / **DONE**) and the critical path to the first franc |
> | [`legal/`](legal/tos.md) | **Legal drafts v0.9 (lawyer-review-ready):** client ToS · DPA (Art. 28 GDPR / nFADP, 3 annexes) · processing register (RoPA, 10 rows) · retention & deletion schedule — cross-ref `LEGAL.md` checklist |
> | [`intelligence/`](intelligence/OFFER.md) | **The Multiplier, live:** brain (think/research/recall) + star links to all nine · landing `intelligence/site/` → https://cogops-intelligence.pages.dev (DR-0010) |
> | [`group/`](holding/README.md) + https://cogops-group.pages.dev | **THE CENTRAL BUSINESS:** the holding as code (`holding.py`: clothes/keeper/allocator), brand lockups (`brand/`), and the state-assembled group site with live trade graph + executable invariants (DR-0012) |
> | [`CAPABILITIES.html`](CAPABILITIES.html) | **The capabilities artifact:** every company alone, every combination together (pairs + K5 clique), principles → code mechanisms |
> | [`sentinel/`](sentinel/OFFER.md) · [`capitalco/`](capitalco/OFFER.md) · [`dossia/`](dossia/OFFER.md) · [`medtech/`](medtech/OFFER.md) | **Regulatory-Science Clique live:** four new evidence machines + complete-graph internal market (DR-0009) |
> | [`verde/`](verde/OFFER.md) · [`terra/`](terra/OFFER.md) | **Climate pair, made real:** live landings (cogops-verde / cogops-terra), CSRD-lite ↔ risk-screen internal-market link (DR-0008), model-grade honesty published |
> | [`talent/`](talent/OFFER.md) | **CogOps Talent, made real:** offer & delivery playbook · live landing (`talent/site/` → https://cogops-talent.pages.dev) · Growth↔Talent internal-market link (DR-0007) |
> | [`helix/`](helix/OFFER.md) | **CogOps Helix, made real:** offer & delivery playbook · live landing source (`helix/site/` → https://cogops-helix.pages.dev) — free 48 h QC sample as the evidence machine |
> | [`growth/`](growth/OFFER.md) | **CogOps Growth, made real**: offer & sales playbook · live landing source (`growth/site/` → https://cogops-growth.pages.dev) · Swiss QR-bill invoicing tool (`growth/tools/`) |
> | [`cogops-os/`](cogops-os/README.md) | **The operating system as running code** — every mechanism executable: gates (+ phone notifications), lifecycle, capital ladder, autonomy contract, SPQP metrics, cadence generators, CBS, agent squads & missions, per-company LLM cost caps, brand theme, and a state-of-the-art task engine per company. Pure stdlib Python; 150-check selftest ALL GREEN |
>
> **Reading order:** methodology → cases → synthesis → operating structure → **cogops-os** (the structure, executed). Every structural element in `structure/` carries a lineage tag `[case §M#]` back to the research; every module in `cogops-os/` maps to an OS section in its README.

> **One central business. One company per domain.**
> A conglomerate of small, AI-operated companies — each owning one theme/domain — running on a single shared core. Every company is buildable with **today's** technology (software, data, AI, services). Deep-tech domains (quantum and anything needing technology that does not yet exist at accessible cost) are **explicitly excluded** — see [Excluded domains](#excluded-domains).

**Basis of domain selection:** two research analyses ranking domains by demand-to-supply gap and profitability — *Europe & America* (Top 12) and *Switzerland* (Top 10), 2025–2026 data (BLS, EU Commission, SIA, SANS, McKinsey, WEF). Each company below cites its domain's evidence.

---

## Structure

```
                        ┌─────────────────────────────┐
                        │      CogOps Group (CH)      │   ← the holding / central business
                        │  AI core · capital · gates  │     not client-facing
                        │  site factory · CRM · brand │
                        └──────────────┬──────────────┘
        ┌───────────┬───────────┬──────┴────┬───────────┬───────────┐
        │           │           │           │           │           │
  Intelligence  Sentinel     Capital      Helix       Dossia     Medtech
   (AI / ML)  (Cybersecurity) (Quant fin) (Comp. bio) (Regulatory) (MedTech SW)
        │           │           │           │           │           │
      Verde       Terra       Growth      Talent
    (CleanTech) (Climate/ESG) (Revenue engine) (Workforce)
```

**10 companies, 3 clusters:**
- **Deep-domain services** (sell expertise into scarce-skill markets): Helix, Dossia, Medtech, Sentinel, Capital, Terra, Verde
- **The multiplier** (AI itself): Intelligence
- **Group engines** (serve every company + external clients): Growth, Talent

---

## The Holding — CogOps Group

The central business. Not a company that sells — the machine that makes companies.

- **AI core** — the agent hierarchy (specialist agents per universe: revenue, delivery, capital, people, infrastructure, strategy, continuity) that operates every subsidiary.
- **The gate** — one human-approval nexus: every external, financial or high-stakes action in any company is staged as a plain-language request and executes only on the founder's keystroke. Fail-closed, append-only audit trail.
- **Capital engine** — profit sweep from all companies into one compliance-guarded investment automaton (no leverage, no derivatives, Swiss private-investor guardrails).
- **Site factory** — templated builds spin each company's public site, portal and assistant from one codebase: brand + content + product config, not a rebuild.
- **Shared spine** — one multi-provider LLM gateway, one CRM database, one auth/portal layer, one legal/privacy baseline, one brand system (CogOps handles + domain email already reserved).

**A subsidiary = an instance, not a startup.** Launching a company means: name, domain knowledge base, service catalog, site, pricing — on rails that already run.

---

## The Companies

### 1. CogOps Intelligence — *AI operations*
**Domain evidence:** AI/ML — gap **9.8/10** USA, 9.5/10 Europe (rank #1); Switzerland #3. 1.6M open positions vs ~518K qualified candidates (3.2:1). The analyses' "AI paradox": AI is the force multiplier for every other domain.

**What it does:** Builds and operates AI systems for businesses — the group's flagship and proof that one person can run a company-grade machine. Sells what the conglomerate runs on.

**Initial offerings:**
- AI operations retainers: agents, automations and assistants built, hosted and supervised for SMEs
- Custom concierge/assistant deployments (grounded on the client's own facts, human-gated actions)
- LLM-gateway and model-cost engineering (provider failover, zero-token routing, token economics)
- Automation audits: map a business process → deliver an agent-operated version with human gates

**Seed assets:** JARVIS platform (live), the 110-agent hierarchy, the multi-provider gateway, the Nexus gate.
**Boundary:** no model training, no frontier research — integration and operations only.

---

### 2. CogOps Sentinel — *cybersecurity & AI security*
**Domain evidence:** Cybersecurity — gap **9.1/10** (EU/US #4); Switzerland **#2**. US: 504K unfilled roles. Blue-ocean intersection #1 includes AI Safety (the non-quantum half is fully accessible).

**What it does:** Security as a managed service for companies too small for a CISO — plus the emerging niche of securing AI systems themselves (EU AI Act era).

**Initial offerings:**
- SME security audits & hardening packages (software/config only)
- Continuous monitoring & incident-response playbooks
- AI-security reviews: prompt-injection, data-leak and governance checks on deployed assistants
- Compliance readiness: nDSG/GDPR baselines, ISO 27001-lite preparation

**Boundary:** no offensive tooling, no hardware, no clearance work — defensive services and software only.

---

### 3. CogOps Capital — *quantitative finance tools & research*
**Domain evidence:** Quantitative finance — Switzerland **#4**, gap **8.5/10**, the most profitable per-individual domain (total comp to CHF 600K+). Post–Credit Suisse consolidation keeps demand structural.

**What it does:** Institutional-grade portfolio tooling and quant research for private investors and micro-institutions — software and analysis, never custody.

**Initial offerings:**
- Portfolio automation for private investors (DCA engines, compliance guardrails, approval gates)
- Quant research briefs: factor studies, allocation models, backtest reports
- Treasury tooling for small companies (sweep rules, cash-allocation policy engines)
- Alternative-data analysis on public datasets

**Seed assets:** the Investment Automaton (cashflow bridge, IBKR DCA engine, Swiss compliance guard, Nexus gate).
**Boundary:** no fund, no custody, no banking license, no financial advice — tools and research under the client's own keys and approvals.

---

### 4. CogOps Helix — *computational biology & AI drug-discovery support*
**Domain evidence:** Bioinformatics/computational biology — gap **7.8/10** USA, 7.6 Europe (EU/US #11); Switzerland #6 and the analyses' "**safest long-term bet**" (Basel ecosystem, permanent pharma buyers). Blue-ocean intersection **#2: AI + Drug Discovery, 9.8/10** — the highest-scoring intersection that is fully dry-lab accessible.

**What it does:** The dry-lab service house: computational pipelines for labs, biotechs and CROs that need results, not hires.

**Initial offerings:**
- Sequence & reference-transcript QC pipelines (NCBI-grade, auditable)
- Clinical-trial EDA as a service: audit-trailed cleaning, regulatory Table 1, reproducible figures
- In-silico discovery support: protein-structure prediction workflows, multi-omics analysis assistance (public models)
- Literature surveillance & evidence matrices for investigators (ICH M4-ready)

**Seed assets:** the Computational Biology Portfolio (3 shipped pipelines, ICH/ALCOA+-engineered, v1.1 verified).
**Boundary:** no wet lab, no clinical decisions, no diagnosis — computation and evidence only.

---

### 5. CogOps Dossia — *regulatory affairs, medical writing & clinical-research support*
**Domain evidence:** Regulatory affairs & clinical research — Switzerland **#9**, gap **7.0/10**, persistent mid-hundreds gap with only ~120 CROs servicing the market; regulatory complexity (Swissmedic/EMA/FDA) keeps growing.

**What it does:** The dossier factory — regulatory documentation and medical writing produced to ICH standards at machine cost, signed off by humans of record.

**Initial offerings:**
- ICH M4 module drafting & assembly support (CTD-ready documentation)
- Clinical study report statistics: Table 1s, validated stats, transparency figures
- Regulatory intelligence monitoring: PubMed/Europe PMC surveillance feeds per product area
- Pharmacovigilance literature screening pipelines

**Seed assets:** pipeline 03 (PMID-traceable synthesis), the FIXES.md verification discipline, ICH E6(R2)/E9/M4 engineering.
**Boundary:** never the signatory — every deliverable routes through the client's qualified RA/medical lead.

---

### 6. CogOps Medtech — *MedTech R&D enablement software*
**Domain evidence:** MedTech R&D — Switzerland **#7**, gap **7.5/10**; CHF 26B sector, 600+ core-R&D firms; EU MDR added massive documentation overhead; thin talent in AI-diagnostics/digital-health niches.

**What it does:** Software and data infrastructure that accelerates medtech R&D and absorbs MDR-era documentation burden — the picks-and-shovels layer for device companies.

**Initial offerings:**
- MDR technical-documentation automation (templates, traceability, audit trails)
- ALCOA+ experiment-data management for research teams
- Pre-clinical imaging-analysis pipelines (research-use tooling for AI-diagnostics teams)
- Digital-health R&D support: prototypes, data pipelines, verification plans

**Boundary:** not a medical-device manufacturer — research-use and documentation software only; anything patient-facing belongs to clients under their own certifications.

---

### 7. CogOps Verde — *cleantech & energy software*
**Domain evidence:** CleanTech/renewables — gap **7.8/10** (EU/US #9); Switzerland #8, gap 7.2, ~50 new firms/year with almost no domestic talent pipeline; net-zero and ESG mandates drive structural demand.

**What it does:** The software-and-services layer of the energy transition: measurement, reporting and matching — no hardware, no materials science.

**Initial offerings:**
- Energy monitoring & savings dashboards for SMEs and buildings
- Carbon accounting tooling (scope 1–3 bookkeeping for small entities)
- Sustainability reporting services (CSRD-lite packages for SMEs)
- Cleantech matchmaking: vendor/solution shortlists + funding-landscape intelligence

**Boundary:** no hardware, no materials R&D, no energy trading.

---

### 8. CogOps Terra — *climate data & ESG analytics*
**Domain evidence:** Climate science/environmental modeling/ESG — gap **7.5/10** (EU/US #10). Blue-ocean intersection **#5: Climate Modeling + Financial Risk, 9.0/10** — CSRD/SEC mandates create finance-scale demand for climate data.

**What it does:** Turns climate science into financial-grade data products — the bridge between models and money. Natural pair with CogOps Capital.

**Initial offerings:**
- Climate-risk data packs: physical & transition risk for real-estate, finance and insurance portfolios
- ESG research briefs and disclosure-data support (CSRD/SEC climate rules)
- Environmental modeling services on public datasets & established models
- Scenario analysis tooling for asset owners

**Boundary:** not a rating agency — data, models and research, never official ESG ratings.

---

### 9. CogOps Growth — *the revenue engine*
**Domain evidence:** Not a research domain — the machine that fills every other company's pipeline. Demand-generation is the one service all 10 companies need and all SMEs buy.

**What it does:** Hyper-personalized B2B lead enrichment and programmatic SEO at machine cost — the group's cash engine, sold internally first, externally always.

**Initial offerings:**
- B2B lead enrichment retainers (validated decision-maker data + per-prospect outreach copy)
- Programmatic SEO at scale (data-stream ingestion → long-tail page networks, autonomously refreshed)
- The group media network: one industry newsletter/journal per domain company — intelligence content that ranks, nurtures and feeds leads to every subsidiary
- Funnel automation for the group's own sites (one CRM, all companies)

**Seed assets:** the two live JARVIS products with published pricing (lead enrichment CHF 1–3/validated lead; pSEO CHF 15–60/page; retainers).
**Note:** the two uploaded domain analyses are literally media-network product zero.

---

### 10. CogOps Talent — *the workforce company*
**Domain evidence:** The talent gap **is** the subject of both analyses: 2M+ STEM deficit in Europe; every domain ranked by unfilled seats. Training and matching need no deep tech — only curriculum, data and platform.

**What it does:** Monetizes the scarcity directly: trains people into the gap domains and places them where the 3.2:1 demand ratios are.

**Initial offerings:**
- Academy: practical upskilling tracks in the accessible gap domains (AI operations, cybersecurity fundamentals, computational biology, regulatory writing)
- Placement & contract matching for scarce profiles (computational biologists, RA specialists, AI engineers)
- Career-intelligence products: the domain analyses published as subscription intelligence for candidates and employers
- Corporate training packages (teams, not just individuals)

**Boundary:** no accredited degrees, no headhunting licenses where restricted — education content and marketplace.

---

## How the research maps to the companies

| Company | EU/US domain (rank · gap) | Swiss domain (rank · gap) | Blue-ocean intersection |
|---|---|---|---|
| Intelligence | AI/ML — #1 · 9.8 | #3 | "AI paradox": multiplier of all |
| Sentinel | Cybersecurity — #4 · 9.1 | #2 | #1 (AI-safety half) |
| Capital | — | Quant finance — #4 · 8.5 | #5 (with Terra) |
| Helix | Bioinformatics — #11 · 7.8 | Comp. bio — #6 | **#2 · 9.8** (AI + drug discovery) |
| Dossia | — | Regulatory/clinical — #9 · 7.0 | — |
| Medtech | — | MedTech R&D — #7 · 7.5 | — |
| Verde | CleanTech — #9 · 7.8 | CleanTech — #8 · 7.2 | — |
| Terra | Climate/ESG — #10 · 7.5 | — | **#5 · 9.0** (climate × financial risk) |
| Growth | (serves all domains) | (serves all domains) | — |
| Talent | (monetizes the gap itself) | (monetizes the gap itself) | — |

---

## Excluded domains

Per the founding rule — **no quantum computing, nothing requiring much higher technology** — these ranked domains get no company. They stay on the watchlist; several remain excellent *customers* of the companies above (selling **to** an excluded domain never requires **doing** the deep tech).

| Excluded domain | Rank/gap in the analyses | Why excluded | Who can still serve it |
|---|---|---|---|
| Quantum computing & engineering | CH #1; EU/US #2 · 9.6 | Needs quantum hardware & physics-depth teams | Talent (training/placement), Growth (their leads), Sentinel (PQC-readiness consulting) |
| Semiconductors & microelectronics | EU/US #3 · 9.4 | Fabs, lithography, capital at nation-state scale | Growth, Talent |
| Semiconductor materials & nanophotonics | EU/US #12 · 7.4–7.6 | Nanofabrication labs | — |
| Advanced nuclear (SMR/AMR/fusion) | EU/US #5 · 8.9 | Reactors; regulatory + physical capital | Terra (environmental monitoring data), Sentinel (digital security) |
| Defense-tech AI (autonomy, edge) | EU/US #6 · 8.7 | Clearances, weapons-adjacent autonomy | — |
| Synthetic biology & biomanufacturing | EU/US #7 · 8.4 | Wet labs, bio-foundries | Helix (their dry-lab overflow), Dossia (their dossiers) |
| Cell & gene therapy R&D | EU/US #8 · 8.2; CH #5 | Clinical-grade wet labs | Dossia (regulatory), Helix (computational support) |
| Energy storage & battery materials | CH #10 · 6.8 | Electrochemistry labs, materials science | Verde (their software layer), Growth |

**Revisit rule:** when an excluded domain becomes software-accessible (quantum cloud APIs commoditized, lab-automation-as-a-service, fusion digital-twin markets), the conglomerate adds a company without restructuring — the core, gate and factory are domain-agnostic by design.

---

## Operating principles (inherited from the core)

1. **Every company is AI-operated and human-gated** — agents produce, the founder approves; nothing external or financial executes without a keystroke.
2. **Software, data and services only** — no labs, no fabs, no hardware, no licenses the group can't hold as a solo operator with partners of record.
3. **One spine, many skins** — sites, portals, assistants, CRM and gateway are instances of the shared core; a new company is content + configuration.
4. **Evidence over claims** — every deliverable across every company ships with reproducible verification (the FIXES.md discipline: reproduce → fix → verify, with logs).
5. **Profit flows to one capital engine** — sweeps invest under fixed Swiss compliance guardrails; no leverage, no derivatives, ever.
6. **Deep tech is a market, not a method** — excluded domains are served as customers, never entered as practitioners, until the technology threshold drops.

---

*CogOps Group — blueprint v1.0, 2026-10-22. Domain data: `europe-america-research-domains-analysis.md`, `switzerland-research-domains-analysis.md` (2025–2026 sources). Identity assets: `CogOps` + `CogOps-Group` GitHub handles, cogops.engine@gmail.com.*
