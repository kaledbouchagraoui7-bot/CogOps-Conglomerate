"""Gate notifications (OS §11 → founder's pocket).

A terminal prompt isn't a keystroke gate when you're away from the machine
(roadmap, Base). `notify()` pushes a message to COGOPS_NOTIFY_URL — works with
any ntfy.sh topic (phone app subscribes in 10 seconds), a Telegram-to-webhook
bridge, or any endpoint accepting a POST with a text body. No URL set → the
notification is logged to the ledger only (honest degradation, never a silent
drop).

Setup (one-time, founder):
  1. phone: install ntfy, subscribe to a private topic e.g. ntfy.sh/cogops-<random>
  2. project secret: COGOPS_NOTIFY_URL=https://ntfy.sh/cogops-<random>
"""
from __future__ import annotations

import json
import os
import urllib.request

import ledger

URL = os.environ.get("COGOPS_NOTIFY_URL", "")


def notify(title: str, body: str, priority: str = "high") -> dict:
    """Fire-and-forget push. Returns delivery status for the ledger."""
    rec = {"title": title, "pushed": False, "channel": "ledger-only"}
    if URL:
        try:
            req = urllib.request.Request(
                URL, data=body.encode("utf-8"),
                headers={"Title": title[:90], "X-Priority": {"min": "1", "low": "2",
                         "default": "3", "high": "4", "max": "5"}.get(priority, "4"),
                         "Tags": "cogops"})
            with urllib.request.urlopen(req, timeout=5) as r:
                rec.update(pushed=r.status == 200, channel="webhook")
        except Exception as e:
            rec.update(error=str(e)[:120], channel="webhook-failed→ledger")
    ledger.event("notification", title, rec)
    return rec


def notify_gate(gate_item: dict) -> dict:
    """Called by gates.stage() for G2/G3: the phone learns before the inbox."""
    a = gate_item["action"]
    body = (f"{gate_item['company']} requests [{gate_item['level']}]: "
            f"{a.get('kind', 'action')}"
            + (f" CHF {a['amount_chf']:.2f} — {a.get('what', '')}" if "amount_chf" in a else "")
            + f"\nreason: {gate_item['reason']}\napprove: python3 cogops.py gate approve {gate_item['id']}")
    return notify(f"CogOps gate {gate_item['id']}", body,
                  "max" if gate_item["level"] == "G3" else "high")
