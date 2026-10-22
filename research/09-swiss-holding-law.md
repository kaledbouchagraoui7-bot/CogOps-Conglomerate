# Case 09 — The Swiss Legal Reality · Forms, Holding Structures, Naming, Tax

**Not a benchmark — the constraint frame.** Every mechanism adopted from Cases 01–08 must land in Swiss legal reality. This file states the forms, thresholds and structures as of **2026-10**, marked clearly where a professional (Treuhänder/notary) must confirm. **This is not legal or tax advice.**

## 1. The entity forms relevant to CogOps

| Form | Capital | Liability | Name rules | Public disclosure | Fit |
|---|---|---|---|---|---|
| **Einzelfirma** (sole proprietorship) | none | **unlimited, personal** | must contain the founder's **surname** (fantasy additions allowed, e.g. "Bouchagraoui CogOps Ventures") | minimal (HR entry) | Phase 0 only — cannot trade as "CogOps Group" alone |
| **GmbH** (Sàrl) | CHF 20,000, **fully paid** | limited to company assets | fantasy name free + "GmbH" | **shareholders public** in Handelsregister; ≥1 managing person with drawing rights resident in CH | Phase 1 workhorse — cheapest real limited liability + free naming |
| **AG** (SA) | CHF 100,000, ≥ CHF 50,000 paid-in | limited | fantasy name free + "AG" | shareholders **not public** (registered shares; register private); board required; ≥1 drawing-right holder resident in CH | Phase 2–3 holding form (privacy, investment readiness) |

Other facts that bite:
- **Commercial register (Handelsregister):** Einzelfirma registration mandatory once revenue > CHF 100,000/yr (optional below); GmbH/AG always registered.
- **VAT (MWST):** registration mandatory at **global** turnover > CHF 100,000/yr; standard rate **8.1%** (since 2024-01-01), reduced 2.6%. Selling digital services B2C into the EU: EU VAT via OSS once EU cross-border B2C sales exceed €10,000/yr (place-of-supply = customer). Cross-border rules must be checked per product by a professional.
- **Withholding tax (Verrechnungssteuer):** 35% on dividends — fully refundable for Swiss-resident recipients (neutral in a Swiss-only structure; treaty relief otherwise).
- **Emissionsabgabe (issuance stamp tax):** 1% on newly issued shares above CHF 1M — irrelevant at these capital sizes.
- **Social security:** Einzelfirma = self-employed AHV; GmbH/AG founder-employee = salary via AHV/ALV; salary-vs-dividend mix must be arm's length (tax authority reviews).

## 2. The "holding company" in Switzerland — what it actually is

A Swiss holding is **not a special legal form** — it is an AG or GmbH whose statutory purpose is the long-term holding and management of participations. Key regime points (post-STAF, since 2020-01-01):

1. **Participation exemption (Beteiligungsabzug):** dividends and capital gains from qualifying participations are effectively **exempt from corporate profit tax** — qualifying = holding ≥ **10%** of share capital **or** market value ≥ **CHF 1M** (held ≥ 1 year for the exemption's clean application). Wholly-owned subsidiaries qualify trivially. Related expenses are only proportionally deductible (the exemption is a *reduction*, not a zero).
2. **Capital tax:** cantons reduce capital tax attributable to qualifying participations (cantonal rates differ; Zug/Schwyz etc. notably low — domicile choice matters and is a professional's call).
3. **No group taxation:** Switzerland has no consolidated fiscal group — **each entity files and pays separately**; losses stay in the entity that made them (7-year carryforward). Consequence for CogOps: don't incorporate subsidiaries *before* they profit (early losses would be trapped); run young companies as divisions/brands of the operating GmbH, spin out legal entities at maturity (mirrors Constellation/Alphabet graduation logic — legal separation is a *stage*, not a starting point).
4. **Old "holding privilege" is gone** (pre-2020 cantonal status regimes abolished); today's advantage = participation exemption + low cantonal rates + treaty network.

## 3. Recommended entity evolution path (design choice, professional must confirm)

```
PHASE 0 (now, revenue ≈ 0):        no entity or Einzelfirma "K. Bouchagraoui" (trading as CogOps Group)
PHASE 1 (first client revenue):    CogOps Group GmbH — CHF 20k — ONE legal entity;
                                   the 10 blueprint companies run as DIVISIONS/BRANDS
                                   (own sites, portals, KBs, P&L accounting — no legal separation yet)
PHASE 2 (per company, on trigger): subsidiary GmbH spun out when ANY trigger fires:
                                     · client liability exposure (contracts needing isolation)
                                     · external capital / investor at company level
                                     · sustained profit making the participation exemption +
                                       dividend routing attractive
                                     · a human GM with equity participation joins
                                   → Holding GmbH (or AG) owns ≥10% (participation exemption)
PHASE 3 (portfolio maturity):      holding converted to AG if external investors/privacy/listing
                                   ever matter (shareholder privacy, transferability)
```

Costs (indicative, 2026): GmbH formation ~CHF 1,000–3,000 (notary + HR + capital blocking account), 1–2 weeks; annual accounting/filing ~CHF 2,000–5,000 per entity via Treuhänder — **the reason Phase 1 keeps everything in one entity**: every premature GmbH is ~CHF 3–5k/yr of dead weight (Constellation's "bad revenue" logic applied to *bad structure*).

## 4. Naming & brand law (the "small error" zone)

- Einzelfirma **cannot** be "CogOps Group" alone (surname requirement) — the blueprint's brand needs GmbH/AG. Interim: trademark the brand (Swiss TM ~CHF 550 for 10 years, 3 classes; EUIPO for EU) and trade under "Bouchagraoui [surname-entity], doing business as CogOps Group" — *d/b/a-style usage must be checked for misleadingness (name law: no impression of a nonexistent corporation)*. This is exactly the kind of detail a professional confirms before launch.
- Company names must not deceive about form/scale ("Group" in a GmbH name: generally acceptable as fantasy element, but confirm with the HR office at formation).
- Domains/handles already secured: `CogOps` + `CogOps-Group` (GitHub), `cogops.engine@gmail.com` — align final `.ch/.com` domain purchase with the chosen legal name.

## 5. Structure-to-law mapping of the adopted mechanisms

| Adopted mechanism (source case) | Legal implication in CH |
|---|---|
| Subsidiary lifecycle stages (Alphabet/studios) | Stages 0–3 live as **divisions** of one GmbH; legal spin-out = Stage 4+ event (no-group-taxation rule) |
| Envelopes & gates (Berkshire/Constellation) | Internal policy — no legal form needed; becomes **shareholder/board resolution** discipline once entities exist |
| Profit sweep → ETF/Pillar 3a (JARVIS DNA) | Unchanged; at holding level dividends are participation-exempt; private investing stays under the existing compliance guard |
| Kill criteria (Alphabet X/studios) | Division shutdown = trivial; entity liquidation = formal process (another reason divisions-first) |
| Future human GMs with equity (Atomic/Tiny) | Requires entity + participation agreements (GmbH Stammanteile or phantom equity) — Phase 2 professional work |
| Agent-operated everything | No Swiss rule against AI-operated divisions; **signing authority stays human** (founder as sole drawing-right holder) — the Nexus gate is also the legal signature gate |

## 6. Sources

- wvant.com "Starting a Business in Switzerland" (2026-04): AG capital CHF 100k/50k paid-in, board requirement
- sigtax.com FAQ: GmbH CHF 20k fully paid; AG CHF 100k with pay-in obligation
- business-in-switzerland.com "Swiss holding company — participation exemption guide": AG art. 621 OR minimums; exemption structure
- swissincorporated.com "Swiss Holding Company": holding as AG/GmbH with long-term participation purpose
- theglobalwealth.com "Swiss Holding Company: Advantages and Taxes (2026)": Beteiligungsabzug as cornerstone; post-STAF regime
- VAT: ESTV/AFC guidance — 8.1% standard since 2024-01-01; CHF 100k global-turnover registration threshold; EU OSS €10k distance-sales threshold (EU VAT Directive)
- Einzelfirma naming (surname requirement) & HR obligation >CHF 100k: OR art. 944 ff. / HRegV practice (standard formation guides, e.g. STARTUPS.CH, firmengründung-schweiz.ch)
- Withholding tax 35% refundability; no consolidated group taxation; 7-year loss carryforward: Swiss federal tax law (DBG) summaries in the above guides
- **All thresholds/rates as of 2026-10; a Treuhänder/notary must confirm before execution. Nothing here is legal or tax advice.**
