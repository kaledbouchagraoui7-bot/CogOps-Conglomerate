"""Inquiry triage — AI drafts, the founder decides (founder rule 2026-10-22).

Every incoming request (landing signups today; email/portal later) gets an
AI-drafted reply — but NOTHING is ever sent automatically. A reply leaves
this system in exactly one of two ways:

  1. founder approves the draft (optionally editing it)  → status APPROVED → SENT
  2. founder writes the email personally                 → status MANUAL

There is deliberately no send() function in this module: automated sending
does not exist as a capability, so it cannot happen by accident (the same
fail-closed pattern as the Nexus gate, invariant I3).

Flow:  cogops.py inbox pull      — fetch new signups, draft replies (labeled mode)
       cogops.py inbox list      — queue with statuses
       cogops.py inbox show ID   — full draft + signup facts
       cogops.py inbox approve ID [--text "..."]   — approve (edited or as-drafted)
       cogops.py inbox sent ID   — mark delivered after you paste it into mail
       cogops.py inbox manual ID --text "..."      — your own words, recorded

SLA (OFFER.md §8): reply within 1 business day.
"""
from __future__ import annotations

import json
import os
import urllib.request

import config
import ledger
import llm

QUEUE = config.RUNTIME_DIR / "inbox_queue.json"
SEEN = config.RUNTIME_DIR / "inbox_seen.json"
EXPORT_URL = os.environ.get("GROWTH_EXPORT_URL",
                            "https://cogops-growth.pages.dev/api/export")
SLA_REPLY = "1 business day"

OFFER_FACTS = """CogOps Growth facts (draft ONLY from these):
- free sample batch: 25 validated leads + per-recipient openers, delivered within
  48 hours of the approved target definition, as branded HTML report + CSV
- validation per record: syntax check, disposable/role-trap domain rejection,
  dedupe against the client's list, public-source provenance with timestamp;
  rejected records cost CHF 0
- pricing: CHF 1-3 per validated lead; retainers CHF 1,500-3,500/month (cancel
  monthly); pSEO pilot CHF 900 / 2 weeks; pages CHF 15-60
- guarantees: wrong lead replaced free or credited within 14 days; deletion or
  objection executed within 30 days; reply time 1 business day, named person
- invoicing: Swiss QR-bill net 14 days; operator: CogOps Group, Switzerland"""

DRAFT_RULES = ("Draft ONE reply email, max 150 words, confident and direct, no "
               "hedging, no contradictions. Structure: one-line acknowledgement; "
               "what happens next (30-minute target-definition call or form, then "
               "the 48-hour sample); one concrete question about their ideal "
               "customer if the signup lacks it; signature 'K. Bouchagraoui — "
               "Founder, CogOps Growth · cogops.engine@gmail.com'. Promise ONLY "
               "what the facts list allows.")


def _load(p) -> list | dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else ([] if p == SEEN else {})


def _save(p, d) -> None:
    p.write_text(json.dumps(d, indent=1, sort_keys=True, default=str), encoding="utf-8")


def draft_reply(signup: dict) -> dict:
    """AI draft with honest mode label; template fallback is clearly marked."""
    facts = (f"signup: company={signup.get('company')} product={signup.get('product')} "
             f"icp={signup.get('icp', '')} note={signup.get('note', '')}")
    try:
        out = llm.generate(f"{facts}\n\n{DRAFT_RULES}", system=OFFER_FACTS,
                           company="growth")
        return {"text": out["text"], "mode": out["mode"]}
    except llm.LLMUnavailable:
        icp_q = (f"What does your ideal customer look like — sector, company size, "
                 f"region? One line is enough." if not signup.get("icp") else
                 f"Your ICP note ('{signup['icp'][:120]}') is our starting point.")
        t = (f"Hello {signup.get('company', '')} team,\n\n"
             f"Thank you for requesting the CogOps Growth sample batch "
             f"({signup.get('product', '')}). Here is what happens next: a "
             f"30-minute call (or the same by form) fixes your written target "
             f"definition; your 25 validated leads follow within 48 hours of that "
             f"approval, as a branded report plus CSV with full validation evidence.\n\n"
             f"{icp_q}\n\n"
             f"K. Bouchagraoui — Founder, CogOps Growth · cogops.engine@gmail.com")
        return {"text": t, "mode": "template"}


def pull() -> dict:
    """Fetch unseen signups from the live export endpoint and draft replies."""
    token = os.environ.get("GROWTH_ADMIN_TOKEN", "")
    if not token:
        return {"status": "no_token",
                "note": "set GROWTH_ADMIN_TOKEN (workspace SECRETS.md) to pull signups"}
    try:
        req = urllib.request.Request(EXPORT_URL,
                                     headers={"x-admin-token": token,
                                              "User-Agent": "CogOps-OS/1.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=20).read())
    except Exception as e:
        return {"status": "fetch_failed", "error": str(e)[:120]}
    seen = set(_load(SEEN))
    q = _load(QUEUE)
    new = []
    for s in data.get("signups", []):
        if s["email"] in seen:
            continue
        d = draft_reply(s)
        q[f"IN-{len(q) + 1:04d}"] = {"id": f"IN-{len(q) + 1:04d}", "signup": s,
                                     "draft": d["text"], "mode": d["mode"],
                                     "status": "DRAFT", "created": config.stamp()}
        seen.add(s["email"])
        new.append(s["email"])
    _save(QUEUE, q)
    _save(SEEN, sorted(seen))
    ledger.event("inbox_pull", "growth", {"new": len(new), "emails": new})
    return {"status": "ok", "new_drafts": len(new), "queue_size": len(q)}


def listq() -> dict:
    return {k: {"status": v["status"], "company": v["signup"].get("company"),
                "mode": v["mode"], "created": v["created"]}
            for k, v in _load(QUEUE).items()}


def show(i: str) -> dict:
    q = _load(QUEUE)
    if i not in q:
        raise KeyError(f"unknown inquiry {i} — fail-closed")
    return q[i]


def approve(i: str, final_text: str | None = None) -> dict:
    """Founder keystroke #1: approve the draft (optionally edited)."""
    q = _load(QUEUE)
    if i not in q:
        raise KeyError(f"unknown inquiry {i} — fail-closed")
    q[i]["status"] = "APPROVED"
    q[i]["final"] = final_text if final_text is not None else q[i]["draft"]
    q[i]["approved_at"] = config.stamp()
    q[i]["edited"] = final_text is not None and final_text != q[i]["draft"]
    _save(QUEUE, q)
    ledger.decide("reply_approved", i, {"edited": q[i]["edited"],
                                        "mode": q[i]["mode"]})
    return q[i]


def mark_sent(i: str) -> dict:
    """Founder keystroke #2: you pasted it into mail and sent it."""
    q = _load(QUEUE)
    if i not in q:
        raise KeyError(f"unknown inquiry {i} — fail-closed")
    if q[i]["status"] not in ("APPROVED", "MANUAL"):
        raise ValueError(f"{i} is {q[i]['status']} — approve or write it first")
    q[i]["status"] = "SENT"
    q[i]["sent_at"] = config.stamp()
    _save(QUEUE, q)
    ledger.event("reply_sent", i, {})
    return q[i]


def mark_manual(i: str, text: str) -> dict:
    """Founder keystroke, alternative: your own words, recorded like the rest."""
    q = _load(QUEUE)
    if i not in q:
        raise KeyError(f"unknown inquiry {i} — fail-closed")
    if not text.strip():
        raise ValueError("manual replies need text")
    q[i].update(status="MANUAL", final=text, manual_at=config.stamp())
    _save(QUEUE, q)
    ledger.decide("reply_manual", i, {"chars": len(text)})
    return q[i]


# NOTE FOR AUDITORS: this module MUST NOT grow a send()/smtp()/post-to-mail
# function. Outbound mail is a human act here (founder rule 2026-10-22).
