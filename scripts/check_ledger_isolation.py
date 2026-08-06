#!/usr/bin/env python3
"""ECDLP/ResearchOS ledger-isolation gate (S0_TRUST_DESIGN.md §4).

Machine-checks that the two trust lanes cannot leak into each other:

  1. VERIFIED.md stays ECDLP-only: no row cites a file under `ResearchOS/`
     and no claim id carries a registered non-ECDLP prefix (`RH-`, `nt-`).
  2. The ECDLP headline surface is untouched: no `ResearchOS.`-prefixed name
     in `data/result_registry.json["ledger_declarations"]`, and
     `data/stats.json`'s `ledger_rows` equals the registry's row count.
  3. `domains/registry.json` metrics contract: an `exploratory` domain claims
     no metrics; only `ecdlp-secp256k1` may point at `data/stats.json`; a
     ResearchOS-lane domain's non-null metrics_source must reference the
     ResearchOS ledger or its registry, never the ECDLP stats.
  4. Import closure: every non-audit `ResearchOS/**.lean` module is
     transitively imported from `ResearchOS.lean` ("source-scanned" must
     coincide with "kernel-checked"; review finding ADV-3).
  5. Audit-file whitelist: the only `*AxiomAudit.lean` files under `Ecdlp/`
     or `ResearchOS/` are the three exact known harnesses (never a glob;
     review finding ADV-2), and each generated audit prints only its own
     lane's declarations.
  6. Axiom-keyword ban: no `axiom` declaration in built `Ecdlp`/`ResearchOS`
     source, comments stripped (review finding ADV-1).

Pure Python, zero-toolchain; runs in the cheap pre-build CI phase.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from ledger_utils import parse_ledger  # noqa: E402

NON_ECDLP_PREFIXES = ("RH-", "nt-")
AUDIT_WHITELIST = {
    "Ecdlp/AxiomAudit.lean",
    "Ecdlp/LedgerAxiomAudit.lean",
    "ResearchOS/LedgerAxiomAudit.lean",
}
RESEARCHOS_LANE_DOMAINS = {"number-theory-elementary", "riemann-hypothesis"}
ALLOWED_RESEARCHOS_METRICS = {
    "VERIFIED_RESEARCHOS.md",
    "data/researchos_result_registry.json",
}
AXIOM_DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?"
    r"(?:(?:private|protected|noncomputable|scoped|local|unsafe)\s+)*"
    r"axiom\s+\S+"
)
IMPORT_RE = re.compile(r"^\s*import\s+([A-Za-z0-9_.]+)")
PRINT_AXIOMS_RE = re.compile(r"^#print axioms\s+(\S+)", re.MULTILINE)
BLOCK_COMMENT_RE = re.compile(r"/-.*?-/", re.DOTALL)
LINE_COMMENT_RE = re.compile(r"--.*$", re.MULTILINE)


def strip_lean_comments(text: str) -> str:
    return LINE_COMMENT_RE.sub("", BLOCK_COMMENT_RE.sub("", text))


def module_of(rel: str) -> str:
    return rel[:-len(".lean")].replace("/", ".")


def check_verified_md(root: Path, errors: list[str]) -> None:
    for row in parse_ledger(root):
        for file in row["files"]:
            if file.startswith("ResearchOS/") or file == "ResearchOS.lean":
                errors.append(
                    f"VERIFIED.md row {row['claim']!r} cites {file} — the "
                    "ECDLP ledger must never cite ResearchOS source"
                )
        if row["claim"].startswith(NON_ECDLP_PREFIXES):
            errors.append(
                f"VERIFIED.md row {row['claim']!r} carries a non-ECDLP "
                f"claim prefix {NON_ECDLP_PREFIXES} — it belongs in "
                "VERIFIED_RESEARCHOS.md"
            )


def check_headline_surface(root: Path, errors: list[str]) -> None:
    registry_path = root / "data" / "result_registry.json"
    stats_path = root / "data" / "stats.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for name in registry.get("ledger_declarations", []):
        if name.startswith("ResearchOS."):
            errors.append(
                f"data/result_registry.json ledger_declarations contains "
                f"{name!r} — ResearchOS results must never feed the ECDLP "
                "headline registry"
            )
    if stats_path.exists():
        stats = json.loads(stats_path.read_text(encoding="utf-8"))
        if stats.get("ledger_rows") != registry.get("ledger_rows"):
            errors.append(
                "data/stats.json ledger_rows "
                f"({stats.get('ledger_rows')}) != data/result_registry.json "
                f"ledger_rows ({registry.get('ledger_rows')})"
            )


def check_domain_metrics(root: Path, errors: list[str]) -> None:
    registry = json.loads(
        (root / "domains" / "registry.json").read_text(encoding="utf-8")
    )
    for domain in registry.get("domains", []):
        domain_id = domain.get("id")
        metrics = domain.get("metrics_source")
        if domain.get("status") in {"planned", "exploratory"}:
            if metrics is not None or domain.get("frontier_source") is not None:
                errors.append(
                    f"domains/registry.json: {domain_id} is "
                    f"{domain.get('status')} but claims metrics/frontier "
                    "sources (must stay null; check_domains rule 3)"
                )
        if metrics == "data/stats.json" and domain_id != "ecdlp-secp256k1":
            errors.append(
                f"domains/registry.json: {domain_id} points metrics_source at "
                "the ECDLP data/stats.json — forbidden for every domain "
                "except ecdlp-secp256k1"
            )
        if (
            domain_id in RESEARCHOS_LANE_DOMAINS
            and metrics is not None
            and metrics not in ALLOWED_RESEARCHOS_METRICS
        ):
            errors.append(
                f"domains/registry.json: {domain_id} metrics_source "
                f"{metrics!r} must reference the ResearchOS ledger "
                f"({sorted(ALLOWED_RESEARCHOS_METRICS)}), never ECDLP surfaces"
            )


def check_import_closure(root: Path, errors: list[str]) -> None:
    lib_root = root / "ResearchOS.lean"
    if not lib_root.exists():
        errors.append("ResearchOS.lean is missing")
        return
    modules: dict[str, Path] = {}
    for path in sorted((root / "ResearchOS").rglob("*.lean")):
        rel = path.relative_to(root).as_posix()
        if rel in AUDIT_WHITELIST:
            continue
        modules[module_of(rel)] = path

    imported: set[str] = set()
    frontier = [lib_root]
    while frontier:
        current = frontier.pop()
        for line in current.read_text(encoding="utf-8").splitlines():
            match = IMPORT_RE.match(line)
            if not match:
                continue
            module = match.group(1)
            if module in modules and module not in imported:
                imported.add(module)
                frontier.append(modules[module])
    for module, path in sorted(modules.items()):
        if module not in imported:
            errors.append(
                f"{path.relative_to(root).as_posix()} is not transitively "
                "imported from ResearchOS.lean — it would be source-scanned "
                "but never kernel-checked by lake build"
            )


def check_audit_files(root: Path, errors: list[str]) -> None:
    for base in ("Ecdlp", "ResearchOS"):
        directory = root / base
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*AxiomAudit.lean")):
            rel = path.relative_to(root).as_posix()
            if rel not in AUDIT_WHITELIST:
                errors.append(
                    f"rogue audit-suffixed file {rel} — only the exact "
                    f"whitelist {sorted(AUDIT_WHITELIST)} may match "
                    "*AxiomAudit.lean (glob exemptions are an escape hatch)"
                )
    ecdlp_audit = root / "Ecdlp" / "LedgerAxiomAudit.lean"
    if ecdlp_audit.exists():
        for name in PRINT_AXIOMS_RE.findall(
            ecdlp_audit.read_text(encoding="utf-8")
        ):
            if name.startswith("ResearchOS."):
                errors.append(
                    f"Ecdlp/LedgerAxiomAudit.lean prints {name!r} — the ECDLP "
                    "audit must not cover ResearchOS declarations"
                )
    researchos_audit = root / "ResearchOS" / "LedgerAxiomAudit.lean"
    if researchos_audit.exists():
        text = researchos_audit.read_text(encoding="utf-8")
        for name in PRINT_AXIOMS_RE.findall(text):
            if not name.startswith("ResearchOS."):
                errors.append(
                    f"ResearchOS/LedgerAxiomAudit.lean prints {name!r} — the "
                    "ResearchOS audit must only cover ResearchOS declarations"
                )
        for line in text.splitlines():
            match = IMPORT_RE.match(line)
            if match and match.group(1).split(".")[0] == "Ecdlp":
                errors.append(
                    "ResearchOS/LedgerAxiomAudit.lean imports Ecdlp — the "
                    "non-ECDLP audit must not elaborate ECDLP code"
                )


def check_axiom_keyword(root: Path, errors: list[str]) -> None:
    files = [root / "Ecdlp.lean", root / "ResearchOS.lean"]
    for base in ("Ecdlp", "ResearchOS"):
        directory = root / base
        if directory.exists():
            files.extend(sorted(directory.rglob("*.lean")))
    for path in files:
        if not path.exists():
            continue
        rel = path.relative_to(root).as_posix()
        if "Targets" in Path(rel).parts:
            continue
        stripped = strip_lean_comments(path.read_text(encoding="utf-8"))
        for line_number, line in enumerate(stripped.splitlines(), 1):
            if AXIOM_DECL_RE.match(line):
                errors.append(
                    f"{rel}:{line_number}: `axiom` declaration in built "
                    "source — forbidden (a hand-declared axiom named like a "
                    "compiler aux axiom could forge compiler trust)"
                )


def main(argv: list[str]) -> int:
    root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else (
        Path(__file__).resolve().parent.parent
    )
    errors: list[str] = []
    check_verified_md(root, errors)
    check_headline_surface(root, errors)
    check_domain_metrics(root, errors)
    check_import_closure(root, errors)
    check_audit_files(root, errors)
    check_axiom_keyword(root, errors)
    if errors:
        print("ledger-isolation check FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("ledger-isolation check OK: ECDLP and ResearchOS lanes are "
          "separated (ledger, headline surface, domain metrics, import "
          "closure, audit whitelist, no axiom declarations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
