#!/usr/bin/env python3
"""Fixture tests for scripts/check_ledger_isolation.py and the strict
12-column ResearchOS ledger parser (S0_TRUST_DESIGN.md §4.8): the checker
must FAIL on every injected violation and PASS on the clean fixture."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import check_ledger_isolation  # noqa: E402
from ledger_utils import parse_researchos_ledger  # noqa: E402

VERIFIED_HEADER = (
    "| claim_id | theorem | file | method | status |\n"
    "|---|---|---|---|---|\n"
)
LEDGER_HEADER = (
    "| claim_id | domain | declaration | file | statement_anchor "
    "| source_contract | review_record | axiom_base | method | date "
    "| status | claim_scope |\n"
    "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
)


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def clean_fixture(root: Path) -> None:
    write(root, "VERIFIED.md",
          VERIFIED_HEADER + "| ec-1 | `Ecdlp.foo` | Ecdlp/Foo.lean | norm_num | proved |\n")
    write(root, "data/result_registry.json", json.dumps(
        {"ledger_rows": 1, "ledger_declarations": ["Ecdlp.foo"]}))
    write(root, "data/stats.json", json.dumps({"ledger_rows": 1}))
    write(root, "domains/registry.json", json.dumps({"domains": [
        {"id": "ecdlp-secp256k1", "status": "live",
         "metrics_source": "data/stats.json", "frontier_source": None},
        {"id": "number-theory-elementary", "status": "live",
         "metrics_source": None, "frontier_source": None},
        {"id": "riemann-hypothesis", "status": "exploratory",
         "metrics_source": None, "frontier_source": None},
    ]}))
    write(root, "Ecdlp.lean", "import Ecdlp.Foo\n")
    write(root, "Ecdlp/Foo.lean",
          "theorem Ecdlp.foo : 1 = 1 := rfl\n"
          "-- axiom in a comment must NOT trip the ban\n"
          "/- axiom Fake._native.native_decide.ax_1 : False -/\n")
    write(root, "Ecdlp/AxiomAudit.lean", "#print axioms Ecdlp.foo\n")
    write(root, "Ecdlp/LedgerAxiomAudit.lean",
          "import Ecdlp\n\n#print axioms Ecdlp.foo\n")
    write(root, "ResearchOS.lean", "import ResearchOS.NumberTheory.Elementary\n")
    write(root, "ResearchOS/NumberTheory/Elementary.lean",
          "namespace ResearchOS.NumberTheory\n"
          "theorem prime_2017 : 1 = 1 := rfl\n"
          "end ResearchOS.NumberTheory\n")
    write(root, "ResearchOS/LedgerAxiomAudit.lean",
          "import ResearchOS\n\n"
          "#print axioms ResearchOS.NumberTheory.prime_2017\n")


def run_checker(root: Path) -> int:
    return check_ledger_isolation.main(["check", "--root", str(root)])


def expect(label: str, root: Path, expected: int, failures: list[str]) -> None:
    got = run_checker(root)
    status = "ok " if got == expected else "FAIL"
    print(f"{status} {label} (exit {got}, expected {expected})")
    if got != expected:
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    cases = [
        ("clean fixture passes", 0, lambda r: None),
        ("RH row smuggled into VERIFIED.md", 1, lambda r: write(
            r, "VERIFIED.md", VERIFIED_HEADER +
            "| RH-001-x | `Ecdlp.foo` | Ecdlp/Foo.lean | norm_num | proved |\n")),
        ("VERIFIED.md row citing ResearchOS source", 1, lambda r: write(
            r, "VERIFIED.md", VERIFIED_HEADER +
            "| ec-1 | `Ecdlp.foo` | ResearchOS/NumberTheory/Elementary.lean "
            "| norm_num | proved |\n")),
        ("ResearchOS name in ECDLP ledger_declarations", 1, lambda r: write(
            r, "data/result_registry.json", json.dumps(
                {"ledger_rows": 1,
                 "ledger_declarations": ["ResearchOS.NumberTheory.prime_2017"]}))),
        ("stats.json ledger_rows drift", 1, lambda r: write(
            r, "data/stats.json", json.dumps({"ledger_rows": 99}))),
        ("non-null metrics_source on exploratory RH domain", 1, lambda r: write(
            r, "domains/registry.json", json.dumps({"domains": [
                {"id": "ecdlp-secp256k1", "status": "live",
                 "metrics_source": "data/stats.json", "frontier_source": None},
                {"id": "riemann-hypothesis", "status": "exploratory",
                 "metrics_source": "data/stats.json", "frontier_source": None},
            ]}))),
        ("ResearchOS-lane domain pointing at ECDLP stats", 1, lambda r: write(
            r, "domains/registry.json", json.dumps({"domains": [
                {"id": "ecdlp-secp256k1", "status": "live",
                 "metrics_source": "data/stats.json", "frontier_source": None},
                {"id": "number-theory-elementary", "status": "live",
                 "metrics_source": "data/stats.json", "frontier_source": None},
            ]}))),
        ("unimported ResearchOS module", 1, lambda r: write(
            r, "ResearchOS/NumberTheory/Orphan.lean",
            "theorem ResearchOS.orphan : 1 = 1 := rfl\n")),
        ("rogue *AxiomAudit.lean file", 1, lambda r: write(
            r, "ResearchOS/FooAxiomAudit.lean", "-- sneaky\n")),
        ("ECDLP audit printing a ResearchOS declaration", 1, lambda r: write(
            r, "Ecdlp/LedgerAxiomAudit.lean",
            "import Ecdlp\n\n#print axioms ResearchOS.NumberTheory.prime_2017\n")),
        ("ResearchOS audit importing Ecdlp", 1, lambda r: write(
            r, "ResearchOS/LedgerAxiomAudit.lean",
            "import Ecdlp\nimport ResearchOS\n\n"
            "#print axioms ResearchOS.NumberTheory.prime_2017\n")),
        ("hand-declared axiom in ResearchOS source", 1, lambda r: write(
            r, "ResearchOS/NumberTheory/Elementary.lean",
            "namespace ResearchOS.NumberTheory\n"
            "axiom Evil._native.native_decide.ax_1_0 : False\n"
            "theorem prime_2017 : 1 = 1 := rfl\n"
            "end ResearchOS.NumberTheory\n")),
        ("hand-declared axiom in Ecdlp source", 1, lambda r: write(
            r, "Ecdlp/Foo.lean",
            "theorem Ecdlp.foo : 1 = 1 := rfl\naxiom evil : False\n")),
    ]
    for label, expected, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="ledger-iso-") as tmp:
            root = Path(tmp)
            clean_fixture(root)
            mutate(root)
            expect(label, root, expected, failures)

    # Strict 12-column parser: a literal '|' inside a cell (13 cells) must
    # hard-fail; the clean row must parse.
    with tempfile.TemporaryDirectory(prefix="ledger-iso-") as tmp:
        root = Path(tmp)
        good = ("| nt-x | number-theory-elementary | `A.b` | ResearchOS/A.lean "
                "| ResearchOS/A.lean:1@sha256:abcdefabcdef | — | notes/r.md "
                "| standard | norm_num | 2026-08-05 | proved | scope text |\n")
        write(root, "VERIFIED_RESEARCHOS.md", LEDGER_HEADER + good)
        write(root, "ResearchOS/A.lean", "theorem A.b : 1 = 1 := rfl\n")
        rows = parse_researchos_ledger(root)
        ok = len(rows) == 1 and rows[0]["claim_id"] == "nt-x"
        print(("ok " if ok else "FAIL") + " strict parser accepts a clean 12-cell row")
        if not ok:
            failures.append("parser-clean")
        bad = good.replace("scope text", "scope | text")
        write(root, "VERIFIED_RESEARCHOS.md", LEDGER_HEADER + bad)
        try:
            parse_researchos_ledger(root)
            print("FAIL strict parser accepted a 13-cell row")
            failures.append("parser-pipe")
        except ValueError:
            print("ok  strict parser rejects a literal '|' inside a cell")

    if failures:
        print(f"\n{len(failures)} ledger-isolation fixture(s) FAILED: {failures}")
        return 1
    print("\nall ledger-isolation fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
