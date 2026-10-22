"""Append-only ledgers (OS §3 decision ledger, §11, invariant I8/I11).

JSONL, append-only by construction: the module exposes no delete/update API.
Two ledgers: `decisions.jsonl` (Type-1 gate lifecycle, kills, promotions) and
`events.jsonl` (everything else: spends, evidence, tickets, squad runs).
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

import config

DECISIONS = config.LEDGER_DIR / "decisions.jsonl"
EVENTS = config.LEDGER_DIR / "events.jsonl"


def _append(path: Path, rec: dict) -> dict:
    rec = {**rec, "at": config.stamp(), "seq": _next_seq(path)}
    line = json.dumps(rec, sort_keys=True, ensure_ascii=False)
    # hash-chain: each record commits to the previous one (tamper-evidence,
    # the Auditing Agent verifies the chain in `cogops.py audit`)
    prev = _last_hash(path)
    rec_h = hashlib.sha256((prev + line).encode()).hexdigest()[:16]
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({**rec, "h": rec_h}, sort_keys=True, ensure_ascii=False) + "\n")
    return rec


def _next_seq(path: Path) -> int:
    if not path.exists():
        return 1
    with open(path, "rb") as f:
        f.seek(max(0, f.seek(0, 2) - 65536) if path.stat().st_size > 65536 else 0)
        lines = [l for l in f.read().decode(errors="replace").splitlines() if l.strip()]
    return (json.loads(lines[-1]).get("seq", 0) + 1) if lines else 1


def _last_hash(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return "genesis"
    with open(path, "rb") as f:
        size = path.stat().st_size
        f.seek(max(0, size - 65536))
        lines = [l for l in f.read().decode(errors="replace").splitlines() if l.strip()]
    return json.loads(lines[-1]).get("h", "genesis") if lines else "genesis"


def decide(kind: str, subject: str, evidence: dict | None = None, **kw) -> dict:
    """Record a Type-1-class decision artifact (staged/approved/killed/promoted)."""
    return _append(DECISIONS, {"kind": kind, "subject": subject,
                               "evidence": evidence or {}, **kw})


def event(kind: str, subject: str, payload: dict | None = None, **kw) -> dict:
    rec = {"kind": kind, "subject": subject}
    if payload:
        rec["payload"] = payload
    rec.update(kw)
    return _append(EVENTS, rec)


def read(path: Path = DECISIONS) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def verify_chain(path: Path = DECISIONS) -> bool:
    """Auditing-Agent instrument: recompute the hash chain end to end."""
    prev = "genesis"
    for rec in read(path):
        h = rec.pop("h", None)
        line = json.dumps(rec, sort_keys=True, ensure_ascii=False)
        if hashlib.sha256((prev + line).encode()).hexdigest()[:16] != h:
            return False
        prev = h
    return True


def decisions(kind: str | None = None, subject: str | None = None) -> list[dict]:
    out = read(DECISIONS)
    if kind:
        out = [d for d in out if d["kind"] == kind]
    if subject:
        out = [d for d in out if d["subject"] == subject]
    return out
