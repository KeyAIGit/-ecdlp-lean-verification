#!/usr/bin/env python3
"""Axiom-audit checker (CI trust gate).

Reads the output of `lake env lean Ecdlp/LedgerAxiomAudit.lean` (a sequence of
`#print axioms` results) and FAILS (exit 1) if any audited result:

  * depends on `sorryAx`  — a `sorry`/`admit` leaked into a built proof, or
  * depends on any axiom outside the allowed trusted base.

Allowed trusted base:
  - propext, Classical.choice, Quot.sound  (Lean/Mathlib standard axioms)
  - Lean.ofReduceBool                      (native_decide; trusts the compiler — disclosed)

Usage:  python3 scripts/check_axioms.py axiom_audit.txt [result_registry.json]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Lean/Mathlib's three standard axioms — used by essentially every Mathlib proof.
ALLOWED_STANDARD = {"propext", "Classical.choice", "Quot.sound"}
# `native_decide` trusts the Lean COMPILER. Depending on the toolchain it shows up as the
# generic `Lean.ofReduceBool` OR a per-declaration auxiliary axiom named like
# `<decl>._native.native_decide.ax_<n>_<m>` (Lean v4.31). Both are the same compiler-trust
# extension of the TCB — allowed, but flagged (catalogued in TRUST_REPORT.md).
NATIVE_DECIDE_EXACT = {"Lean.ofReduceBool", "Lean.trustCompiler"}
# `sorryAx` is the axiom Lean inserts for `sorry`/`admit`; it must never appear.
FORBIDDEN_ALWAYS = {"sorryAx", "Lean.guardMsgsAx"}


def is_native_decide(ax: str) -> bool:
    """True for compiler-trust axioms introduced by `native_decide`."""
    return ax in NATIVE_DECIDE_EXACT or ".native_decide.ax" in ax or "_native.native_decide" in ax


def parse_audit_output(text: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Parse Lean output while preserving apostrophes inside identifiers."""
    blocks = re.findall(
        r"^'(.+)' depends on axioms: \[([^\]]*)\]",
        text,
        flags=re.MULTILINE,
    )
    nodep = re.findall(
        r"^'(.+)' does not depend on any axioms$",
        text,
        flags=re.MULTILINE,
    )
    return blocks, nodep


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 3}:
        print("usage: check_axioms.py <axiom_audit.txt> [result_registry.json]",
              file=sys.stderr)
        return 2
    text = Path(argv[1]).read_text(encoding="utf-8")

    # A Lean error in the audit file (e.g. an unknown theorem name) means the audit is
    # not actually checking what it claims — treat as failure so names stay correct.
    if re.search(r"^.*\berror:", text, re.MULTILINE) or "unknown identifier" in text:
        print("AXIOM AUDIT FAILED: the audit file did not elaborate cleanly "
              "(unknown name or error). Output:\n" + text)
        return 1

    # Each `#print axioms foo` yields either
    #   'foo' depends on axioms: [a, b, c]
    # or
    #   'foo' does not depend on any axioms
    blocks, nodep = parse_audit_output(text)

    if not blocks and not nodep:
        print("AXIOM AUDIT FAILED: no `#print axioms` output found — did the audit run?\n"
              + text)
        return 1

    audited_names = {name for name, _ in blocks} | set(nodep)
    if len(argv) == 3:
        import json

        registry = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
        expected = set(registry.get("ledger_declarations", []))
        missing = sorted(expected - audited_names)
        unexpected = sorted(audited_names - expected)
        if missing or unexpected:
            print("AXIOM AUDIT FAILED: output does not match the ledger registry.")
            for name in missing:
                print(f"  [missing] {name}")
            for name in unexpected:
                print(f"  [unexpected] {name}")
            return 1

    violations: list[str] = []
    native_decide_users: list[str] = []
    for name, axlist in blocks:
        axioms = {a.strip() for a in axlist.split(",") if a.strip()}
        bad = set()
        uses_native = False
        for ax in axioms:
            if ax in FORBIDDEN_ALWAYS:
                bad.add(ax)
            elif ax in ALLOWED_STANDARD:
                pass
            elif is_native_decide(ax):
                uses_native = True
            else:
                bad.add(ax)
        if bad:
            violations.append(f"  {name}: disallowed axiom(s) {sorted(bad)}")
        if uses_native:
            native_decide_users.append(name)

    print(f"axiom audit: {len(blocks) + len(nodep)} results checked, "
          f"{len(native_decide_users)} transitively use native_decide (compiler-trusted axiom).")
    for n in native_decide_users:
        print(f"  [native_decide / compiler-trusted] {n}")

    if violations:
        print("\nAXIOM AUDIT FAILED — disallowed axioms found:")
        print("\n".join(violations))
        return 1

    print("\nAXIOM AUDIT OK: every audited result depends only on the allowed trusted "
          "base (no sorryAx, no custom axioms).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
