# CogOps Talent — Offer, Sales Routine & Delivery Procedures

> Mirror of the Growth/Helix playbook for the workforce engine. Landing live: https://cogops-talent.pages.dev · Engines: `../cogops-os/companies/talent.py` · Governance: DR-0007 · **Link to Growth: §7.**

## 1. ICP
**Candidates:** career-switchers, juniors and lab/IT professionals aiming into the four gap domains (AI ops, cyber, comp-bio, regulatory writing) — people who need a bridge, not another MOOC certificate.
**Employers:** SMEs, labs, CROs and agencies hiring in those domains who have felt the 3.2:1 demand/supply wall and refuse to pay search retainers.
**Disqualified:** anyone asking for an accredited degree claim, or employers wanting CV floods instead of shortlists.

## 2. Offer ladder
| Rung | Offer | Price | Purpose |
|---|---|---|---|
| 0 | **Free skill-gap scan** (ranked matches, gaps, training bridges; explainable factors), 48 h | CHF 0 | proof + funnel |
| 1 | Track access (40 h + capstone + assessment) | CHF 290 / track | first franc |
| 2 | Academy subscription (all tracks, monthly updates) | CHF 49 / month | recurring |
| 3 | Career-intelligence brief per domain | CHF 90 | content product |
| 4 | Employer talent feed (monthly scan-verified shortlist) | CHF 500 / month | B2B recurring |
| 5 | Placement fee | CHF 1,500 / signed hire | B2B event |

Honesty boundary published everywhere: certificates of completion, **not** accredited degrees.

## 3. Sales routine (weekly quota)
- **15 candidate-side touches/week** (communities, alumni networks, public gap-analysis posts) + **5 employer touches/week** (labs/CROs/agencies — prospected via the Growth link, §7).
- **10 free scans/week** cap (protects 48 h).
- Employer follow-ups: day +3 (sample anonymized shortlist), day +7 (feed pilot month at 50% off).
- Every touch drafted by engine, sent by human (inbox doctrine applies group-wide).

## 4. Delivery procedures
### 4.1 Skill-gap scan
1. Intake: skills list + target roles (form or email; 10 min).
2. Agents run `match` (explainable TF-cosine) + `talent_report_html` (branded, version-hashed).
3. Human review: counselor reads every paid report; free scans sampled 20% (100% first 20).
4. Deliverable: HTML report with matched skills, gaps, bridges. 48 h.
### 4.2 Tracks & subscription
Curriculum generated from `curriculum` engine (evidence-cited modules); capstones graded by checklist + human sign-off; monthly content updates logged with version stamps.
### 4.3 Employer feed
1. Intake: role profiles with weighted skills (human agrees weights with employer).
2. Agents: anonymized candidate pool → `match` → shortlist of ≤5 with score factors + consent flags.
3. Human review: counselor verifies consent + score sanity before any name leaves.
4. Monthly delivery; placement fee invoiced on signed hire (QR-bill).

## 5. Handover & compliance
Scan data anonymized until candidate approves an introduction; deletion ≤30 days with certificate (privacy page promise); employer role profiles are client data (DPA applies); no ranking of humans beyond decision-support scores — the counselor, not the cosine, owns recommendations.

## 6. Validation plan (DR-0007)
90-day window from 2026-10-22: **100 signups OR 3 pre-orders (track/feed) OR CHF 200+ paid**. Miss ⇒ kill review as KILL_WIN.

## 7. The Growth link (same category: Group engines)
- **Talent → Growth:** `employer_prospects` buys validated employer prospect lists from Growth's lead engine through a platform ticket at the internal price (CHF 1/lead, DR-0002); the charge lands on Talent's P&L — standalone books stay honest.
- **Growth → Talent:** `sister_digest` buys career-intel briefs from Talent (CHF 5/brief internal) and publishes them as the talent-careers vertical of Growth's media network — distribution for Talent, content for Growth.
- Both sites cross-link in nav-footers ("Group engines: Growth ↔ Talent — same machine, two doors"); the signup queues feed each other's ICPs (employers discovered by Growth can need Talent's feed, and vice versa) with explicit consent at intro.
