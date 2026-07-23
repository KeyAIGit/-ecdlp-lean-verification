#!/usr/bin/env python3
"""Regression tests for Lean #print axioms output parsing."""
from __future__ import annotations

from check_axioms import parse_audit_output


def test_identifier_apostrophe_is_not_a_quote_boundary() -> None:
    name = "Ecdlp.Curve.secp256k1_isCoprime_preΨ'_odd_primes"
    text = f"'{name}' depends on axioms: [propext,\n Classical.choice]\n"
    blocks, nodep = parse_audit_output(text)
    assert blocks == [(name, "propext,\n Classical.choice")]
    assert nodep == []


def test_axiom_free_identifier_with_apostrophe() -> None:
    name = "Ecdlp.example'"
    blocks, nodep = parse_audit_output(
        f"'{name}' does not depend on any axioms\n"
    )
    assert blocks == []
    assert nodep == [name]


def main() -> int:
    tests = [
        test_identifier_apostrophe_is_not_a_quote_boundary,
        test_axiom_free_identifier_with_apostrophe,
    ]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\nall {len(tests)} axiom-output fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
