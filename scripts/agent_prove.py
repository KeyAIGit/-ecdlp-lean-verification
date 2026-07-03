#!/usr/bin/env python3
"""
Variant-B prover harness: Claude proposes a Lean proof, the warm Hetzner server
verifies it with `lake env lean` (~5s), and on a kernel-clean result the caller
(the GitHub Actions workflow) opens a draft PR.

CRITICAL ARCHITECTURE NOTE
--------------------------
The Anthropic API is text-in / text-out only. It has NO filesystem, NO Lean, and
NO access to GitHub or the server. THIS orchestrator (running on a GitHub Actions
runner) is the only thing with access, via three secrets:

  ANTHROPIC_API_KEY            -> the model (the "brain": proposes Lean code)
  SSH_PRIVATE_KEY + SERVER_HOST-> the server (the "verifier": runs `lake env lean`)
  (the workflow's GITHUB_TOKEN)-> the repo   (the "hands": push branch, open PR)

Hard safety properties:
  * invoked only from a manual (workflow_dispatch) workflow — never auto-spends;
  * a per-dispatch USD budget cap (stops proposing once the estimated spend hits it);
  * a max-iterations cap;
  * refuses any candidate containing `sorry` / `admit` / `axiom`;
  * writes the accepted proof to the working tree only — the workflow branches off
    main and opens a DRAFT PR; main is never touched here.

This script prints `RESULT: accepted <path>` or `RESULT: failed <reason>` on the
last line so the workflow can branch on it. The API key is never printed.
"""
from __future__ import annotations

import base64
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("::error::the 'anthropic' package is not installed", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
MODEL = os.environ.get("AGENT_MODEL", "claude-opus-4-8")
MAX_ITERS = int(os.environ.get("AGENT_MAX_ITERS", "6"))
BUDGET_USD = float(os.environ.get("AGENT_BUDGET_USD", "5"))
EFFORT = os.environ.get("AGENT_EFFORT", "high")  # 'high'=Extra (best for coding/agentic)
SERVER_HOST = os.environ["SERVER_HOST"]
SERVER_USER = os.environ.get("SERVER_USER", "root")
SSH_KEY = os.environ.get("SSH_KEY_PATH", str(Path.home() / ".ssh" / "id_ed25519"))

# Opus 4.8 pricing per 1M tokens (see the claude-api skill). Cache reads ~0.1x input,
# cache writes ~1.25x input. We over-estimate slightly to stay safely under budget.
PRICE_IN, PRICE_OUT = 5.0, 25.0
PRICE_CACHE_READ, PRICE_CACHE_WRITE = 0.5, 6.25


def usd(u) -> float:
    return (
        getattr(u, "input_tokens", 0) * PRICE_IN
        + getattr(u, "output_tokens", 0) * PRICE_OUT
        + getattr(u, "cache_read_input_tokens", 0) * PRICE_CACHE_READ
        + getattr(u, "cache_creation_input_tokens", 0) * PRICE_CACHE_WRITE
    ) / 1_000_000


def ssh_run(remote_script: str, timeout: int = 120) -> tuple[int, str]:
    """Run a script on the server over SSH. Returns (returncode, combined output)."""
    cmd = [
        "ssh", "-i", SSH_KEY,
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=25",
        f"{SERVER_USER}@{SERVER_HOST}", remote_script,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr)


def verify_on_server(lean_source: str) -> tuple[bool, str]:
    """Place the candidate inside the server's warm repo and `lake env lean` it (~5s)."""
    b64 = base64.b64encode(lean_source.encode()).decode()
    scratch = "_agent_candidate.lean"
    remote = (
        'set -e; export PATH="$HOME/.elan/bin:$PATH"; '
        "cd ~/-ecdlp-lean-verification; git pull --quiet || true; "
        f"echo {b64} | base64 -d > {scratch}; "
        f"lake env lean {scratch} > /tmp/agent_out.txt 2>&1; rc=$?; "
        f"cat /tmp/agent_out.txt; rm -f {scratch} /tmp/agent_out.txt; exit $rc"
    )
    rc, out = ssh_run(remote)
    # `lake env lean` exits non-zero on any error and prints `error:`; warnings (incl.
    # `sorry`) keep rc=0, so we also scan the source and output defensively.
    lowered = out.lower()
    clean = (
        rc == 0
        and "error:" not in lowered
        and not re.search(r"\b(sorry|admit)\b", lean_source)
        and "axiom" not in lean_source
    )
    return clean, out


def extract_lean(text: str) -> str | None:
    m = re.search(r"```(?:lean)?\s*\n(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else None


def read_example(rel: str, limit: int = 4000) -> str:
    p = ROOT / rel
    if not p.exists():
        return ""
    return f"=== {rel} ===\n" + p.read_text(encoding="utf-8")[:limit]


def build_system() -> list[dict]:
    conventions = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")[:6000]
    examples = "\n\n".join(
        read_example(r)
        for r in (
            "Ecdlp/Proved/TwoTorsionPoint.lean",
            "Ecdlp/Proved/FiveTorsion.lean",
            "Ecdlp/Proved/GlvAutomorphism.lean",
        )
    )
    system_text = textwrap.dedent(
        f"""
        You are an expert Lean 4 + Mathlib prover working inside the repository
        KeyAIGit/-ecdlp-lean-verification. You produce ONE complete, self-contained
        Lean file that the Lean kernel accepts with NO `sorry`, NO `admit`, and NO
        added `axiom`. The invariant is absolute: a proof is only real if `lake env
        lean` accepts it. Never weaken a statement to make it pass.

        House rules:
        - `import Mathlib` plus the specific `Ecdlp.Proved.*` modules you build on.
        - Put theorems in `namespace Ecdlp.Curve` and `open WeierstrassCurve.Affine`
          when working with the point group, mirroring the examples.
        - Only use lemmas that exist in Mathlib v4.31.0 or in the repo's Proved modules.
        - Output ONLY the Lean file inside a single ```lean code block, nothing else.

        --- repository conventions (CLAUDE.md) ---
        {conventions}

        --- worked examples of accepted files ---
        {examples}
        """
    ).strip()
    # Cache the (large, stable) system prompt so repair iterations are cheap.
    return [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}]


def create_message(client, system, messages):
    """Call the Messages API robustly.

    Newer Opus 4.8 knobs (extended `thinking`, an `effort`/`output_config`) may or
    may not be accepted by the exact API surface this runner talks to. Rather than
    hard-depend on their schema (a first-dispatch 400 would waste a run), try the
    rich call, then peel off the exotic params on any TypeError/BadRequest and retry.
    """
    base = dict(model=MODEL, max_tokens=12000, system=system, messages=messages)
    attempts = [
        {**base, "thinking": {"type": "adaptive"}, "output_config": {"effort": EFFORT}},
        {**base, "thinking": {"type": "enabled", "budget_tokens": 8000}, "max_tokens": 16000},
        base,
    ]
    last_exc = None
    for kwargs in attempts:
        try:
            return client.messages.create(**kwargs)
        except TypeError as e:      # SDK doesn't know a kwarg
            last_exc = e
        except Exception as e:      # incl. anthropic.BadRequestError (400) on an unknown field
            if e.__class__.__name__ in ("BadRequestError", "UnprocessableEntityError"):
                last_exc = e
                continue
            raise
    raise last_exc


def main() -> int:
    target = os.environ.get("AGENT_TARGET", "").strip()
    if not target:
        print("RESULT: failed no AGENT_TARGET provided")
        return 1

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    system = build_system()
    messages = [{
        "role": "user",
        "content": (
            f"Prove the following in a complete Lean file:\n\n{target}\n\n"
            "Return ONLY the Lean file in a ```lean block."
        ),
    }]

    spent = 0.0
    for it in range(1, MAX_ITERS + 1):
        if spent >= BUDGET_USD:
            print(f"RESULT: failed budget exhausted (~${spent:.2f} >= ${BUDGET_USD:.2f})")
            return 1
        print(f"--- iteration {it}/{MAX_ITERS} (spent so far ~${spent:.2f}) ---", flush=True)
        resp = create_message(client, system, messages)
        spent += usd(resp.usage)
        reply = "".join(b.text for b in resp.content if b.type == "text")
        lean = extract_lean(reply)
        if not lean:
            print("model did not return a lean code block; nudging.", flush=True)
            messages += [
                {"role": "assistant", "content": reply},
                {"role": "user", "content": "Return ONLY the complete Lean file in a ```lean block."},
            ]
            continue

        ok, out = verify_on_server(lean)
        print(f"server verify: {'CLEAN' if ok else 'REJECTED'}", flush=True)
        if ok:
            print(f"estimated spend this run: ~${spent:.2f}")
            (ROOT / "AGENT_CANDIDATE.lean").write_text(lean, encoding="utf-8")
            print("RESULT: accepted AGENT_CANDIDATE.lean")
            return 0

        # Feed the exact Lean error back for repair.
        tail = out[-4000:]
        messages += [
            {"role": "assistant", "content": reply},
            {"role": "user", "content": (
                "The Lean kernel REJECTED that file. Fix it and return the full corrected "
                "file in a ```lean block. Do not add `sorry`/`admit`/`axiom`. "
                f"`lake env lean` output:\n\n{tail}"
            )},
        ]

    print(f"RESULT: failed no accepted proof in {MAX_ITERS} iterations (~${spent:.2f})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
