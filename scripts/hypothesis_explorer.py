#!/usr/bin/env python3
"""Hypothesis explorer — the DeepSeek breadth/exploration tier.

Generates DIVERSE, non-repeating research hypotheses about ECDLP / secp256k1 structure, forces
each into a concrete machine-checkable sub-claim, and files the outcome. See
`notes/HYPOTHESIS_EXPLORER.md` for the design and the honest purpose (this maps the no-go space;
it is not a breakthrough machine).

Safe no-op if DEEPSEEK_API_KEY is absent (zero spend). DeepSeek exposes an OpenAI-compatible API.

Usage:
    DEEPSEEK_API_KEY=... python3 scripts/hypothesis_explorer.py --samples 4 [--axis algebraic]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "notes" / "HYPOTHESIS_LEDGER.md"

# The six coverage axes (see design doc). The director rotates to the least-explored one.
AXES = [
    "algebraic (endomorphism ring / CM, isogeny graph, torsion structure E[n])",
    "index-calculus / factor-base (Semaev summation, Weil descent, decomposition bases)",
    "analytic / p-adic (formal groups, canonical heights, Frobenius / L-functions)",
    "geometric (higher genus, abelian varieties, moduli, covers)",
    "cross-domain analogy (lattices, codes, dynamical systems, tensor networks, category theory)",
    "reduction / equivalence (to factoring, to other DLPs, to hidden-subgroup variants)",
]

# Machine-checked no-go facts already in the repo — fed to the model so it does NOT restate them.
KNOWN_NOGO = """\
- secp256k1 resists MOV/Frey-Ruck: embedding degree > 100 (p^k != 1 mod n for k<=100). PROVEN here.
- secp256k1 is not anomalous / not supersingular: trace of Frobenius t != 0, t != 1 (anti-Smart). PROVEN here.
- Semaev summation polynomials give NO subexponential advantage over a PRIME field (secp256k1's F_p). Documented.
- Generic (black-box) attacks are provably Omega(sqrt n): brute force is out. PROVEN here (Shoup/Nechaev).
- Standard failed directions (do NOT restate as if novel): plain index calculus on prime-field EC,
  generic Weil descent (genus blows up), isogeny-to-weak-curve search (this is the HARD direction),
  generic Groebner on the point equations (exponential)."""


def canonical_signature(hypothesis: str) -> str:
    """Short stable signature for dedup: lowercased alnum tokens, hashed."""
    toks = re.findall(r"[a-z0-9]+", hypothesis.lower())
    return hashlib.sha1((" ".join(sorted(set(toks)))).encode()).hexdigest()[:12]


def load_seen() -> list[str]:
    if not LEDGER.exists():
        return []
    return re.findall(r"`sig:([0-9a-f]{12})`", LEDGER.read_text(encoding="utf-8"))


def build_prompt(axis: str, seen_sigs: list[str]) -> str:
    return f"""You are the exploration tier of a machine-verified ECDLP research system. The Lean
kernel is the judge; only checkable claims matter. Propose ONE genuinely novel research hypothesis
about the structure of the elliptic-curve discrete-log problem on secp256k1 (y^2 = x^3 + 7 over
F_p), along the axis: **{axis}**.

HARD CONSTRAINTS:
1. Do NOT restate any of these already-known / machine-checked facts or standard failed approaches:
{KNOWN_NOGO}
2. Your hypothesis must be OUTSIDE the standard list and orthogonal to prior runs.
3. You MUST name a concrete, SMALL, machine-checkable sub-claim that would be a first test of the
   idea — a polynomial identity, a resultant/coprimality fact, a torsion/degree count, an explicit
   map, etc. — something verifiable by sympy or the Lean kernel in isolation. If you cannot, the
   hypothesis is vacuous; produce a different one.

Reply as strict JSON: {{"hypothesis": "...", "why_novel": "...", "checkable_subclaim": "...",
"how_to_check": "sympy|lean + one sentence"}}. There are already {len(seen_sigs)} explored
hypotheses; be different from all of them."""


def call_deepseek(prompt: str, temperature: float) -> str | None:
    """DeepSeek via its OpenAI-compatible endpoint. Returns raw content or None on failure."""
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
    except Exception:
        print("::notice:: openai SDK not installed; run `pip install openai`.", file=sys.stderr)
        return None
    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-reasoner"),
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=1200,
    )
    return resp.choices[0].message.content


def novelty_ok(hypothesis: str, seen: list[str]) -> bool:
    return canonical_signature(hypothesis) not in seen


def verify_subclaim(subclaim: str, how: str) -> str:
    """Hook: route an algebraic sub-claim to sympy, or a Lean statement to the server.
    v0 stub — returns 'parked'; wire to scripts/certify.py (sympy) and the warm server (kernel)."""
    # TODO: parse `how`; if sympy -> exec a sandboxed certificate; if lean -> lake env lean on server.
    return "parked"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=4)
    ap.add_argument("--axis", type=str, default=None, help="force an axis; else rotate")
    ap.add_argument("--temperature", type=float, default=1.0)
    args = ap.parse_args()

    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("DEEPSEEK_API_KEY not set — hypothesis explorer no-ops (no spend).")
        return 0

    seen = load_seen()
    # rotate to the least-explored axis unless forced
    axis = args.axis or AXES[len(seen) % len(AXES)]
    print(f"axis: {axis}\nalready explored: {len(seen)} hypotheses")

    fresh = []
    for i in range(args.samples):
        raw = call_deepseek(build_prompt(axis, seen), args.temperature)
        if not raw:
            continue
        try:
            obj = json.loads(raw[raw.index("{"):raw.rindex("}") + 1])
        except Exception:
            continue
        h = obj.get("hypothesis", "").strip()
        if not h or not obj.get("checkable_subclaim") or not novelty_ok(h, seen):
            continue
        sig = canonical_signature(h)
        seen.append(sig)
        obj["_sig"] = sig
        obj["_axis"] = axis
        obj["_outcome"] = verify_subclaim(obj["checkable_subclaim"], obj.get("how_to_check", ""))
        fresh.append(obj)

    if not fresh:
        print("no novel, checkable hypotheses this run.")
        return 0

    with LEDGER.open("a", encoding="utf-8") as f:
        if LEDGER.stat().st_size == 0 if LEDGER.exists() else True:
            f.write("# Hypothesis ledger (auto-appended; see notes/HYPOTHESIS_EXPLORER.md)\n\n")
        for o in fresh:
            f.write(f"## `sig:{o['_sig']}` — axis: {o['_axis']} — outcome: {o['_outcome']}\n")
            f.write(f"- **Hypothesis:** {o['hypothesis']}\n")
            f.write(f"- **Why novel:** {o.get('why_novel','')}\n")
            f.write(f"- **Checkable sub-claim:** {o['checkable_subclaim']}\n")
            f.write(f"- **How to check:** {o.get('how_to_check','')}\n\n")
    print(f"appended {len(fresh)} novel hypotheses to {LEDGER.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
