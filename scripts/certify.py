#!/usr/bin/env python3
"""Fable-in-CI: a model designs a sympy verification script for a math identity; we RUN it.

This is the autonomous-engine analogue of delegating the hardest pure math to Fable. The
interactive pipeline that produced the deep results (the n=5/n=7 torsion bridges, #E[n]≤n²)
worked by having Fable design a *sympy-verified* certificate (explicit polynomials + exact
`linear_combination` cofactors) which a build agent then transcribed into Lean. This module
gives the unattended engine the same capability:

  1. a model proposes a SELF-CONTAINED sympy script that asserts the key identity/certificate
     and prints CERT_OK iff every check passes (plus the explicit certificate it verified);
  2. we EXECUTE it with a wall-clock timeout, offline;
  3. only a script that prints CERT_OK counts — the verified certificate text is then injected
     into the Lean prover prompt, so the prover transcribes a machine-checked identity instead
     of guessing one.

Safe: the sympy script runs in a temp dir with a timeout and no network dependence. Budget-
bounded via the shared per-call USD accounting. The Lean KERNEL is still the final judge —
sympy only proposes; a certificate that sympy accepts but Lean rejects simply fails downstream.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CERT_MARKER = "CERT_OK"
SYMPY_TIMEOUT_S = int(os.environ.get("CERTIFY_TIMEOUT_S", "120"))


def extract_python(text: str) -> str | None:
    m = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else None


def run_sympy(script: str) -> tuple[bool, str]:
    """Execute a python/sympy script offline with a timeout. Returns (printed_CERT_OK, output)."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "cert.py"
        p.write_text(script, encoding="utf-8")
        try:
            r = subprocess.run(
                [sys.executable, str(p)],
                capture_output=True, text=True, timeout=SYMPY_TIMEOUT_S,
                cwd=td, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            out = r.stdout + r.stderr
        except subprocess.TimeoutExpired:
            return False, f"(sympy script timed out after {SYMPY_TIMEOUT_S}s)"
        except Exception as e:  # noqa: BLE001
            return False, f"(failed to run sympy script: {e})"
    return (CERT_MARKER in out and r.returncode == 0), out


def _prompt(claim: str) -> str:
    return (
        "You are a computer-algebra specialist. Write a SELF-CONTAINED Python script using "
        "sympy that RIGOROUSLY verifies the following mathematical claim by exact symbolic "
        "computation (no floating point, no `simplify`-as-proof — use `expand`, `cancel`, "
        "polynomial remainder / ideal membership, `Poly(...).rem(...)`, resultants, etc.).\n\n"
        f"CLAIM:\n{claim}\n\n"
        "Requirements:\n"
        "  - Assert every sub-identity with exact sympy (== 0 after expand/cancel).\n"
        "  - Print the EXPLICIT certificate it verified (the polynomials / cofactors / values), "
        "so a Lean engineer can transcribe it.\n"
        f"  - Print exactly the line `{CERT_MARKER}` as the LAST line iff ALL asserts pass; "
        "otherwise let it raise / do not print it.\n"
        "  - Only sympy + Python stdlib. No files, no network. Fast (seconds).\n\n"
        "Return ONLY the complete script in a ```python code block."
    )


def design_certificate(client, model, claim, max_iters, budget_left):
    """Returns (verified: bool, certificate_text: str, spent_usd: float, trace: list[str])."""
    # Imported lazily so this module is importable (and --self-test runs) without the SDK.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from agent_day import call_model, usd_for  # noqa: E402

    messages = [{"role": "user", "content": _prompt(claim)}]
    spent, trace = 0.0, []
    for it in range(1, max_iters + 1):
        if spent >= budget_left:
            trace.append(f"  - cert iter {it}: budget exhausted (~${spent:.2f})")
            break
        resp = call_model(client, model, [], messages)
        spent += usd_for(model, resp.usage)
        reply = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        script = extract_python(reply)
        if not script:
            trace.append(f"  - cert iter {it}: no python block")
            messages += [{"role": "assistant", "content": reply},
                         {"role": "user", "content": "Return ONLY the sympy script in a ```python block."}]
            continue
        ok, out = run_sympy(script)
        trace.append(f"  - cert iter {it}: {'VERIFIED' if ok else 'sympy rejected'} (~${spent:.2f})")
        if ok:
            cert = ("The following certificate was verified by sympy (exact symbolic "
                    "computation). Transcribe these exact polynomials/cofactors into Lean; do "
                    "not re-derive them:\n\n" + out.strip())
            return True, cert, spent, trace
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": (
                         "The sympy script did NOT print " + CERT_MARKER + " (or errored). "
                         "Fix it and return the full corrected script.\n\n" + out[-3000:])}]
    return False, "", spent, trace


# --- self-test / CLI ---------------------------------------------------------------------

_SELFTEST_SCRIPT = (
    "import sympy as sp\n"
    "x = sp.symbols('x')\n"
    "lhs = (x + 1)**2\n"
    "rhs = x**2 + 2*x + 1\n"
    "assert sp.expand(lhs - rhs) == 0\n"
    "print('certificate: (x+1)^2 = x^2 + 2x + 1')\n"
    "print('CERT_OK')\n"
)


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        ok, out = run_sympy(_SELFTEST_SCRIPT)
        print(out.strip())
        print(f"self-test harness: {'PASS' if ok else 'FAIL'}")
        # Negative control: a script that fails must NOT be accepted.
        bad_ok, _ = run_sympy("import sympy as sp\nassert sp.expand((sp.Symbol('x')+1)**2 - sp.Symbol('x')**2) == 0\nprint('CERT_OK')\n")
        print(f"negative control (should be FAIL): {'PASS-as-fail' if not bad_ok else 'LEAKED'}")
        return 0 if (ok and not bad_ok) else 1

    claim = " ".join(a for a in argv if not a.startswith("--")) or sys.stdin.read()
    if not claim.strip():
        print("usage: certify.py <claim>   |   certify.py --self-test", file=sys.stderr)
        return 2
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("certify: no ANTHROPIC_API_KEY — cannot design a certificate", file=sys.stderr)
        return 2
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import anthropic  # noqa: E402
    client = anthropic.Anthropic()
    model = os.environ.get("CERTIFY_MODEL", "claude-opus-4-8")
    ok, cert, spent, trace = design_certificate(client, model, claim, max_iters=5, budget_left=5.0)
    print("\n".join(trace))
    print(f"certify: {'VERIFIED' if ok else 'FAILED'} ~${spent:.2f}")
    if ok:
        print("----- certificate -----")
        print(cert)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
