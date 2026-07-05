#!/usr/bin/env python3
"""
Autonomous "prover day": a budget- and time-bounded loop over a queue of targets.

For each target it runs the same propose -> server-verify -> repair loop as
`agent_prove.py` (whose kernel-clean guarantee it reuses verbatim), accumulates every
accepted Lean file, and writes a full human-readable trace. It stops the moment the USD
budget or the wall-clock budget is hit — so a run can never exceed the cap the caller set
(backstopped by the Anthropic Console spend limit).

It NEVER touches main and NEVER spends without a manual dispatch. The workflow
(`agent-day.yml`) collects the accepted files into ONE draft PR for human review; the Lean
kernel + CI re-verify everything before any merge.

Model tiering: cheap targets can run on a cheaper model to stretch the budget; only hard
targets need Opus. Per-target `model` overrides the default.

Output (last lines, machine-readable):
    RESULT: accepted=<n> attempted=<m> spent=~$<x>
    ACCEPTED: <module_name>          (one per accepted node)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("::error::the 'anthropic' package is not installed", file=sys.stderr)
    sys.exit(2)

# Reuse the audited single-target primitives (kernel check, extraction, prompt cache).
from agent_prove import verify_on_server, extract_lean, build_system  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUDGET_USD = float(os.environ.get("AGENT_BUDGET_USD", "20"))
TIME_BUDGET_MIN = float(os.environ.get("AGENT_TIME_BUDGET_MIN", "300"))
DEFAULT_MODEL = os.environ.get("AGENT_DEFAULT_MODEL", "claude-sonnet-5")
DEFAULT_MAX_ITERS = int(os.environ.get("AGENT_MAX_ITERS", "5"))
QUEUE_PATH = ROOT / os.environ.get("AGENT_QUEUE", "targets/queue.json")
OUT_DIR = ROOT / os.environ.get("AGENT_OUT_DIR", "agent_candidates")
TRACE_PATH = ROOT / "AGENT_TRACE.md"

# Per-1M-token USD (input, output). Cache reads ~0.1x input; we over-estimate to stay safe.
PRICES = {
    "claude-opus-4-8": (5.0, 25.0),
    "claude-sonnet-5": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


def usd_for(model: str, u) -> float:
    pin, pout = PRICES.get(model, PRICES["claude-opus-4-8"])
    inp = getattr(u, "input_tokens", 0)
    out = getattr(u, "output_tokens", 0)
    cr = getattr(u, "cache_read_input_tokens", 0)
    cw = getattr(u, "cache_creation_input_tokens", 0)
    return (inp * pin + out * pout + cr * pin * 0.1 + cw * pin * 1.25) / 1_000_000


def call_model(client, model: str, system, messages):
    """One Messages API call, degrading gracefully if newer params aren't accepted."""
    base = dict(model=model, max_tokens=12000, system=system, messages=messages)
    for kwargs in (
        {**base, "thinking": {"type": "adaptive"}, "output_config": {"effort": "high"}},
        {**base, "thinking": {"type": "enabled", "budget_tokens": 8000}, "max_tokens": 16000},
        base,
    ):
        try:
            return client.messages.create(**kwargs)
        except TypeError:
            continue
        except Exception as e:  # noqa: BLE001
            if e.__class__.__name__ in ("BadRequestError", "UnprocessableEntityError"):
                continue
            raise
    # Last resort: raise from a final plain attempt so the error is real.
    return client.messages.create(**base)


def prove_one(client, system, target: str, model: str, max_iters: int, budget_left: float):
    """Returns (accepted_lean|None, spent_usd, transcript_lines)."""
    messages = [{
        "role": "user",
        "content": f"Prove the following in a complete Lean file:\n\n{target}\n\n"
                   "Return ONLY the Lean file in a ```lean block.",
    }]
    spent = 0.0
    trace: list[str] = []
    for it in range(1, max_iters + 1):
        if spent >= budget_left:
            trace.append(f"  - iter {it}: budget for this target exhausted (~${spent:.2f})")
            break
        resp = call_model(client, model, system, messages)
        spent += usd_for(model, resp.usage)
        reply = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        lean = extract_lean(reply)
        if not lean:
            trace.append(f"  - iter {it}: no lean block returned; nudging")
            messages += [{"role": "assistant", "content": reply},
                         {"role": "user", "content": "Return ONLY the complete Lean file in a ```lean block."}]
            continue
        ok, out = verify_on_server(lean)
        trace.append(f"  - iter {it}: {'CLEAN' if ok else 'rejected'} (~${spent:.2f})")
        if ok:
            return lean, spent, trace
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": (
                         "The Lean kernel REJECTED that file. Fix it and return the full corrected "
                         "file in a ```lean block. No sorry/admit/axiom.\n\n" + out[-4000:])}]
    return None, spent, trace


def load_queue():
    if not QUEUE_PATH.exists():
        print(f"::error::target queue {QUEUE_PATH} not found")
        return []
    data = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    return data.get("targets", data) if isinstance(data, dict) else data


def main() -> int:
    queue = load_queue()
    if not queue:
        print("RESULT: accepted=0 attempted=0 spent=~$0.00 (empty queue)")
        return 1
    client = anthropic.Anthropic()
    system = build_system()
    OUT_DIR.mkdir(exist_ok=True)

    t0 = time.monotonic()
    spent = 0.0
    accepted: list[str] = []
    trace = [f"# Autonomous prover-day trace",
             f"budget ${BUDGET_USD:.2f} / {TIME_BUDGET_MIN:.0f} min, default model `{DEFAULT_MODEL}`\n"]

    for i, t in enumerate(queue, 1):
        if spent >= BUDGET_USD:
            trace.append(f"\n**Stopped: USD budget reached (~${spent:.2f}).**")
            break
        if (time.monotonic() - t0) / 60.0 >= TIME_BUDGET_MIN:
            trace.append(f"\n**Stopped: time budget reached.**")
            break
        name = t.get("name") or t.get("id") or f"Target{i}"
        model = t.get("model", DEFAULT_MODEL)
        max_iters = int(t.get("max_iters", DEFAULT_MAX_ITERS))
        target = t.get("target") or t.get("statement") or ""
        if not target:
            continue
        trace.append(f"\n## {i}. {name}  (model `{model}`)")
        print(f"--- [{i}/{len(queue)}] {name} model={model} spent=~${spent:.2f} ---", flush=True)
        # Fable-in-CI: if the target carries a math claim to certify, design a
        # sympy-verified certificate first and prepend it, so the prover transcribes a
        # machine-checked identity instead of guessing one (the step that made the deep
        # torsion results tractable interactively). Best-effort; budget-bounded.
        if t.get("certify") and spent < BUDGET_USD:
            try:
                from certify import design_certificate
                cmodel = t.get("certify_model", "claude-opus-4-8")
                citers = int(t.get("certify_iters", 4))
                ok_c, cert, cs, ctr = design_certificate(
                    client, cmodel, str(t["certify"]), citers, BUDGET_USD - spent)
                spent += cs
                trace += ctr
                if ok_c:
                    target = (cert + "\n\n---\n\nUsing the sympy-verified certificate above, "
                              "prove the following in a complete Lean file:\n\n" + target)
                    print(f"  certificate VERIFIED (~${spent:.2f})", flush=True)
            except Exception as e:  # noqa: BLE001 — certification is optional; never abort the run
                trace.append(f"  - certify step errored ({e.__class__.__name__}); proceeding without")
        lean, s, tr = prove_one(client, system, target, model, max_iters, BUDGET_USD - spent)
        spent += s
        trace += tr
        if lean:
            mod = "".join(c if c.isalnum() else "_" for c in name)[:48] or f"Candidate{i}"
            (OUT_DIR / f"{mod}.lean").write_text(lean, encoding="utf-8")
            accepted.append(mod)
            trace.append(f"  → **ACCEPTED** as `agent_candidates/{mod}.lean`")
            print(f"ACCEPTED: {mod}", flush=True)

    trace.append(f"\n---\n**{len(accepted)} accepted / {len(queue)} attempted, "
                 f"estimated spend ~${spent:.2f}.**")
    TRACE_PATH.write_text("\n".join(trace), encoding="utf-8")
    print(f"RESULT: accepted={len(accepted)} attempted={len(queue)} spent=~${spent:.2f}")
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
