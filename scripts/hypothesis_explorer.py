#!/usr/bin/env python3
"""Hypothesis explorer — the DeepSeek breadth / preprocessing tier (parallel, self-verifying).

Design (see `notes/HYPOTHESIS_EXPLORER.md`): DeepSeek is the CHEAP wide front-end of the engine.
It fans out many axis-scoped agents; each must (a) propose ONE novel structural hypothesis about
ECDLP / secp256k1, (b) reduce it to a SMALL machine-checkable sub-claim, and (c) write a
self-contained sympy script that verifies that sub-claim offline. We RUN the script (never trust
the model's word): it prints `CERT_OK` or it fails. Outcomes:

  - refuted / no CERT_OK  → grows the honest no-go map (a result, not a failure),
  - supported (CERT_OK)   → a LEAD, handed to the depth tier (Fable) as a pre-chewed narrow target.

This is the token-optimisation the product wants: DeepSeek (cheap) does the broad generation +
algebra scripting; sympy (free) is the judge of the cheap filter; Fable (expensive) is spent ONLY
on leads that survive. The Lean kernel remains the final judge for anything promoted to the corpus.

DeepSeek exposes an OpenAI-compatible API. Safe no-op if DEEPSEEK_API_KEY is absent (zero spend).

Usage:
    DEEPSEEK_API_KEY=... python3 scripts/hypothesis_explorer.py --agents 12 --workers 8
    # each agent is pinned to one coverage axis (rotated); --workers caps concurrent API calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "notes" / "HYPOTHESIS_LEDGER.md"
LEADS = ROOT / "notes" / "HYPOTHESIS_LEADS.md"  # survivors → Fable depth tier
CERT_MARKER = "CERT_OK"
SYMPY_TIMEOUT_S = int(os.environ.get("CERTIFY_TIMEOUT_S", "60"))

# The six coverage axes. Each agent is pinned to one, so the fleet cannot collapse into one corner.
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
- Distinct-prime torsion x-loci are disjoint: gcd(psi_l, psi_l')=1 for primes l != l' (E[2]-E[3], E[5]-E[7] certified).
- Standard failed directions (do NOT restate as if novel): plain index calculus on prime-field EC,
  generic Weil descent (genus blows up), isogeny-to-weak-curve search (this is the HARD direction),
  generic Groebner on the point equations (exponential)."""


def canonical_signature(hypothesis: str) -> str:
    """Short stable signature for dedup: lowercased alnum tokens, hashed."""
    toks = re.findall(r"[a-z0-9]+", hypothesis.lower())
    return hashlib.sha1((" ".join(sorted(set(toks)))).encode()).hexdigest()[:12]


def load_seen() -> set[str]:
    if not LEDGER.exists():
        return set()
    return set(re.findall(r"`sig:([0-9a-f]{12})`", LEDGER.read_text(encoding="utf-8")))


def build_prompt(axis: str, n_seen: int) -> str:
    return f"""You are one agent of the exploration tier of a MACHINE-VERIFIED ECDLP research system.
The Lean kernel / sympy are the judges; only checkable claims matter. Propose ONE genuinely novel
research hypothesis about the structure of the elliptic-curve discrete-log problem on secp256k1
(y^2 = x^3 + 7 over F_p), strictly along the axis: **{axis}**.

HARD CONSTRAINTS:
1. Do NOT restate any already-known / machine-checked fact or standard failed approach:
{KNOWN_NOGO}
2. Your hypothesis must be OUTSIDE that list and orthogonal to the {n_seen} hypotheses already explored.
3. You MUST reduce it to a concrete, SMALL sub-claim that is a first test of the idea — a polynomial
   identity, a resultant/coprimality fact, a torsion/degree count, an explicit map — verifiable by
   sympy IN ISOLATION. If you cannot, the hypothesis is vacuous; produce a different one.
4. You MUST write a SELF-CONTAINED python+sympy script that RIGOROUSLY checks THAT EXACT sub-claim by
   exact symbolic computation (expand/cancel/Poly.rem/resultant — NO floats, NO `simplify`-as-proof)
   and prints exactly `{CERT_MARKER}` as the LAST line IFF every assertion passes (else it raises).
   Only sympy + stdlib, no files, no network, runs in seconds.

ANTI-GAMING (critical — violating this makes the result worthless):
- The script must verify the SPECIFIC quantity in YOUR sub-claim (the exact sparsity fraction /
  factor degree / degree count / map you stated). Do NOT substitute an easier, different, or
  already-known check. Do NOT fall back to printing `{CERT_MARKER}` for a trivial or unrelated fact.
- If, while writing it, you find your sub-claim is ill-posed or you cannot actually test it, then it
  was a bad sub-claim: STOP, pick a DIFFERENT hypothesis whose sub-claim you genuinely can verify,
  and return that instead. Never emit `{CERT_MARKER}` for anything other than the stated sub-claim.
- Use `sympy.GF(p)` / `Poly(..., modulus=p)` for F_p; do not pass unsupported kwargs. The script must
  actually RUN — a crashing script is a failure, not a proof.

Reply as STRICT JSON with keys:
  "hypothesis": "...", "why_novel": "...", "checkable_subclaim": "...",
  "sympy_script": "<the complete python script as a string>"
Return ONLY the JSON object."""


def call_deepseek(prompt: str, temperature: float) -> str | None:
    """DeepSeek via its OpenAI-compatible endpoint. Returns raw content or None on failure.

    Default model is `deepseek-chat` (V3): it follows strict-JSON formatting far more reliably than
    `deepseek-reasoner` (R1), is cheaper and faster, and supports JSON mode — the right tool for
    STRUCTURED generation. JSON mode (`response_format`) is requested for chat models so the returned
    object is always parseable with the embedded sympy script correctly escaped."""
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
    except Exception:
        print("::notice:: openai SDK not installed; run `pip install openai`.", file=sys.stderr)
        return None
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")
    kwargs = dict(model=model, messages=[{"role": "user", "content": prompt}],
                  temperature=temperature, max_tokens=4000)
    if "reasoner" not in model:  # reasoner (R1) does not support response_format / JSON mode
        kwargs["response_format"] = {"type": "json_object"}
    try:
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content
    except Exception as e:  # noqa: BLE001
        print(f"::warning:: DeepSeek call failed: {e}", file=sys.stderr)
        return None


def parse_json(raw: str) -> dict | None:
    if not raw:
        return None
    # strip ```json / ``` fences if present, then take the outermost {...}
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    try:
        return json.loads(s[s.index("{"):s.rindex("}") + 1])
    except Exception:
        return None


def run_sympy(script: str) -> tuple[str, str]:
    """Execute a sympy script offline with a timeout. Returns (outcome, tail_of_output).
    outcome in {'supported','refuted','parked'}."""
    if not script or not script.strip():
        return "parked", "(no sympy script provided)"
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "cert.py"
        p.write_text(script, encoding="utf-8")
        try:
            r = subprocess.run(
                [sys.executable, str(p)], capture_output=True, text=True,
                timeout=SYMPY_TIMEOUT_S, cwd=td,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            out = (r.stdout + r.stderr)[-1500:]
        except subprocess.TimeoutExpired:
            return "parked", f"(timed out after {SYMPY_TIMEOUT_S}s)"
        except Exception as e:  # noqa: BLE001
            return "parked", f"(failed to run: {e})"
    if CERT_MARKER in out and r.returncode == 0:
        return "supported", out
    # Distinguish a genuine mathematical refutation (the script RAN and an assertion failed)
    # from a broken script (any other exception / import / syntax error). Only a clean
    # AssertionError counts as a no-go result; broken tooling is `parked`, not `refuted`,
    # so a crash never masquerades as a real "cannot" fact in the no-go map.
    if "AssertionError" in out and "Traceback" in out:
        # ensure the traceback's FINAL exception is AssertionError, not something else earlier
        last_exc = out.rstrip().splitlines()[-1] if out.strip() else ""
        if last_exc.startswith("AssertionError") or last_exc.strip() == "AssertionError":
            return "refuted", out
    if "Traceback" in out or "Error" in out:
        return "parked", "(script error — broken certificate, not a math refutation)\n" + out[-400:]
    return "parked", out


def explore_one(axis: str, n_seen: int, temperature: float) -> dict:
    """One DeepSeek agent: propose → self-write sympy check → run it offline.
    Always returns a dict; on failure it carries `_drop` (a reason) for diagnostics."""
    raw = call_deepseek(build_prompt(axis, n_seen), temperature)
    if not raw:
        return {"_drop": "no API response"}
    obj = parse_json(raw)
    if not obj:
        return {"_drop": "JSON parse failed", "_raw": raw[:200]}
    h = (obj.get("hypothesis") or "").strip()
    if not h:
        return {"_drop": "no hypothesis field"}
    if not obj.get("checkable_subclaim"):
        return {"_drop": "no checkable_subclaim"}
    if not (obj.get("sympy_script") or "").strip():
        return {"_drop": "no sympy_script"}
    outcome, tail = run_sympy(obj["sympy_script"])
    return {
        "hypothesis": h,
        "why_novel": obj.get("why_novel", ""),
        "checkable_subclaim": obj.get("checkable_subclaim", ""),
        "sympy_script": obj.get("sympy_script", ""),
        "_sig": canonical_signature(h),
        "_axis": axis,
        "_outcome": outcome,
        "_evidence": tail[-400:],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", type=int, default=6, help="how many hypothesis agents to run")
    ap.add_argument("--workers", type=int, default=6, help="max concurrent DeepSeek calls")
    ap.add_argument("--axis", type=str, default=None, help="force one axis; else rotate across all")
    ap.add_argument("--temperature", type=float, default=1.0)
    args = ap.parse_args()

    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("DEEPSEEK_API_KEY not set — hypothesis explorer no-ops (no spend).")
        return 0

    seen = load_seen()
    n_seen = len(seen)
    # assign each agent an axis: forced, or round-robin so the fleet spreads across all six.
    assignments = [args.axis or AXES[i % len(AXES)] for i in range(args.agents)]
    print(f"launching {args.agents} agents (<= {args.workers} concurrent) over "
          f"{1 if args.axis else len(AXES)} axes; {n_seen} hypotheses already explored")

    fresh: list[dict] = []
    drops: dict[str, int] = {}
    n_dupe = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(explore_one, ax, n_seen, args.temperature) for ax in assignments]
        for fut in as_completed(futs):
            o = fut.result()
            if "_drop" in o:
                drops[o["_drop"]] = drops.get(o["_drop"], 0) + 1
                if o.get("_raw"):
                    print(f"  drop ({o['_drop']}): raw head = {o['_raw']!r}")
                continue
            if o["_sig"] in seen:  # dedup across runs AND within this batch
                n_dupe += 1
                continue
            seen.add(o["_sig"])
            fresh.append(o)

    # diagnostics — always visible in the run log / artifact
    print(f"diagnostics: {len(fresh)} usable, {n_dupe} duplicates, "
          f"drops={drops or '{}'}")

    if not fresh:
        print("no novel, checkable hypotheses this run.")
        return 0

    supported = [o for o in fresh if o["_outcome"] == "supported"]
    refuted = [o for o in fresh if o["_outcome"] == "refuted"]
    parked = [o for o in fresh if o["_outcome"] == "parked"]
    print(f"results: {len(supported)} supported (→ Fable), {len(refuted)} refuted (→ no-go), "
          f"{len(parked)} parked, of {len(fresh)} novel.")

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    new_ledger = not LEDGER.exists() or LEDGER.stat().st_size == 0
    with LEDGER.open("a", encoding="utf-8") as f:
        if new_ledger:
            f.write("# Hypothesis ledger (auto-appended; see notes/HYPOTHESIS_EXPLORER.md)\n\n")
        for o in fresh:
            f.write(f"## `sig:{o['_sig']}` — axis: {o['_axis']} — outcome: **{o['_outcome']}**\n")
            f.write(f"- **Hypothesis:** {o['hypothesis']}\n")
            f.write(f"- **Why novel:** {o['why_novel']}\n")
            f.write(f"- **Checkable sub-claim:** {o['checkable_subclaim']}\n")
            if o["_outcome"] != "supported":
                f.write(f"- **Verifier evidence:** `{o['_evidence'][-200:].strip()}`\n")
            f.write("\n")

    # Leads (supported) get a dedicated file: pre-chewed narrow targets for the Fable depth tier.
    if supported:
        LEADS.parent.mkdir(parents=True, exist_ok=True)
        new_leads = not LEADS.exists() or LEADS.stat().st_size == 0
        with LEADS.open("a", encoding="utf-8") as f:
            if new_leads:
                f.write("# Live leads — sympy-supported sub-claims for the Fable depth tier\n\n")
                f.write("Each survived an independent offline sympy check (`CERT_OK`). Fable is spent "
                        "ONLY on these, as pre-verified narrow targets for kernel-depth work.\n\n")
            for o in supported:
                f.write(f"## `sig:{o['_sig']}` — axis: {o['_axis']}\n")
                f.write(f"- **Hypothesis:** {o['hypothesis']}\n")
                f.write(f"- **Sympy-supported sub-claim:** {o['checkable_subclaim']}\n")
                f.write("- **Verified certificate (sympy):**\n\n```python\n")
                f.write(o["sympy_script"].strip() + "\n```\n\n")

    print(f"appended {len(fresh)} to {LEDGER.relative_to(ROOT)}"
          + (f"; {len(supported)} leads to {LEADS.relative_to(ROOT)}" if supported else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
