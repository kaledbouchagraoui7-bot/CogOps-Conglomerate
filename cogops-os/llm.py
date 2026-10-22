"""LLM gateway (OS §7) — Python port of the JARVIS `_llm.js` doctrine:
provider chain with fast-fail timeouts, KB-first zero-token routing, honest
mode labels, never a fake answer.

Chain: ANTHROPIC_API_KEY > OPENAI_API_KEY > OPENROUTER_API_KEY (strongest-first
model chain verified against the live catalog 2026-10-22) > offline. Workers-AI
is site-side only (Pages Functions); locally the offline fallback is a
deterministic template composer — labeled `template`, never `llm`.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

import config

TIMEOUT_S = float(os.environ.get("LLM_TIMEOUT_S", "8"))
OPENROUTER_MODELS = [m.strip() for m in os.environ.get(
    "OPENROUTER_MODELS",
    "anthropic/claude-fable-5.1,openai/gpt-6-astra,google/gemini-4-argon,"
    "x-ai/grok-4.7,deepseek/deepseek-v4-pro-0813,"
    "nvidia/nemotron-3-ultra-550b-a55b:free,minimax/minimax-m3.1-flash:free,"
    "google/gemma-4-31b-it:free,recursive/flint-v1.0:free").split(",") if m.strip()]
MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "300"))


class LLMUnavailable(RuntimeError):
    pass


def _extract(j: dict) -> str:
    if not isinstance(j, dict):
        return ""
    for k in ("response", "result"):
        if j.get(k):
            return str(j[k])
    ch = j.get("choices") or [{}]
    msg = (ch[0] or {}).get("message") or {}
    return str(msg.get("content") or "")


def _post(url: str, headers: dict, body: dict):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        return json.loads(r.read())


def generate(prompt: str, system: str = "", kb_hit: str | None = None) -> dict:
    """KB-first routing (JARVIS b0969fb): a grounded KB answer costs ZERO model
    tokens. Only out-of-scope prompts reach a provider. Returns
    {text, mode: kb|anthropic|openai|openrouter:<model>|template, provider_errs}."""
    if kb_hit:
        return {"text": kb_hit, "mode": "kb", "provider_errs": []}
    errs = []
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            j = _post("https://api.anthropic.com/v1/messages",
                      {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                       "anthropic-version": "2023-06-01"},
                      {"model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
                       "max_tokens": MAX_TOKENS, "system": system,
                       "messages": [m for m in msgs if m["role"] != "system"]})
            t = "".join(c.get("text", "") for c in j.get("content", [])
                        if c.get("type") == "text")
            if t:
                return {"text": t, "mode": "anthropic", "provider_errs": errs}
        except Exception as e:
            errs.append(f"anthropic: {str(e)[:90]}")
    if os.environ.get("OPENAI_API_KEY"):
        try:
            j = _post("https://api.openai.com/v1/chat/completions",
                      {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]},
                      {"model": os.environ.get("OPENAI_MODEL", "gpt-5-mini"),
                       "messages": msgs, "max_completion_tokens": MAX_TOKENS})
            t = _extract(j)
            if t:
                return {"text": t, "mode": "openai", "provider_errs": errs}
        except Exception as e:
            errs.append(f"openai: {str(e)[:90]}")
    if os.environ.get("OPENROUTER_API_KEY"):
        for m in OPENROUTER_MODELS:
            try:
                j = _post("https://openrouter.ai/api/v1/chat/completions",
                          {"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                           "HTTP-Referer": "https://cogops.group", "X-Title": "CogOps OS"},
                          {"model": m, "messages": msgs, "max_tokens": MAX_TOKENS})
                t = _extract(j)
                if t:
                    return {"text": t, "mode": f"openrouter:{m}", "provider_errs": errs}
                errs.append(f"{m}: empty content")
            except urllib.error.HTTPError as e:
                errs.append(f"{m}: HTTP {e.code}")       # 402/429 → next model, fast
                if e.code in (401, 403):
                    break                                 # key problem — stop chain
            except Exception as e:
                errs.append(f"{m}: {str(e)[:70]}")
    raise LLMUnavailable("; ".join(errs[-4:]) or "no provider configured")
