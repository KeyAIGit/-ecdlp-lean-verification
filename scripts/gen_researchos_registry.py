#!/usr/bin/env python3
"""Build the declaration-level registry for the ResearchOS result ledger.

Implements the ledger half of the S0-TRUST closure
(`domains/riemann-hypothesis/S0_TRUST_DESIGN.md` §1.3): every row of
`VERIFIED_RESEARCHOS.md` must resolve to a kernel-checked public declaration
in built ResearchOS source, and — inversely — every public declaration in
built ResearchOS source must have a ledger row ("built ⇒ ledgered ⇒
audited"). The generated `data/researchos_result_registry.json` feeds
`scripts/gen_axiom_audit.py` (which emits `ResearchOS/LedgerAxiomAudit.lean`)
and `scripts/check_axioms.py` (which enforces the per-row `axiom_base`).

Hard failures (generation AND --check):
  * a ledger declaration that does not resolve to a built public ResearchOS
    declaration in the row's cited file;
  * duplicate qualified declaration names across ResearchOS source files
    (an anchor could otherwise point at a homonym of the audited decl);
  * a built public declaration with no ledger row (inverse coverage);
  * a stale statement anchor (file:line@sha256 of the statement slice);
  * a claim-id prefix outside the registered domain-prefix map, a domain id
    absent from domains/registry.json, a file outside ResearchOS/, an RH row
    outside ResearchOS/AnalyticNumberTheory/RiemannHypothesis/, a missing
    review record, an invalid axiom_base, or two rows citing one declaration.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from ledger_utils import expand_braces, parse_researchos_ledger, strip_md

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "researchos_result_registry.json"
DOMAIN_REGISTRY = ROOT / "domains" / "registry.json"

# Audit harnesses are the ONLY ResearchOS .lean files exempt from declaration
# scanning and inverse coverage — by exact path, never by glob
# (S0_TRUST_DESIGN.md §2.1, review finding ADV-2).
AUDIT_EXEMPT = {"ResearchOS/LedgerAxiomAudit.lean"}

# Machine-readable domain whitelist: claim-id prefix -> domains/registry.json id
# (S0_TRUST_DESIGN.md §1.2). Extend only together with a registered domain.
PREFIX_DOMAINS = {
    "nt-": "number-theory-elementary",
    "RH-": "riemann-hypothesis",
    "MB-": "analysis-generic",
}
# Rows of this domain must cite files under this subtree
# (domains/riemann-hypothesis/README.md:70-71). The `analysis-generic` entry
# is the same discipline applied in reverse: domain-neutral lemmas may not be
# filed inside a conjecture program's subtree, where they would read as that
# program's content.
DOMAIN_SUBTREES = {
    "riemann-hypothesis": "ResearchOS/AnalyticNumberTheory/RiemannHypothesis/",
    "analysis-generic": "ResearchOS/Analysis/",
}
ALLOWED_AXIOM_BASES = {"standard", "standard+native_decide"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?"
    r"(?P<mods>(?:(?:private|protected|noncomputable|scoped|local|unsafe|partial)\s+)*)"
    r"(?P<kind>theorem|lemma|def|abbrev|instance|opaque|structure|class|inductive)\s+"
    r"(?P<name>[^\s(:\[{]+)"
)
NAMESPACE_RE = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*$")
SECTION_RE = re.compile(r"^\s*section(?:\s+[A-Za-z_][A-Za-z0-9_']*)?\s*$")
END_RE = re.compile(r"^\s*end(?:\s+[^\s]+)?\s*$")

STATEMENT_SLICE_CAP = 40  # lines; a statement slice runs decl-line .. first ':='


def researchos_files(root: Path) -> list[Path]:
    files = [root / "ResearchOS.lean"]
    base = root / "ResearchOS"
    if base.exists():
        files.extend(
            path for path in sorted(base.rglob("*.lean"))
            if path.relative_to(root).as_posix() not in AUDIT_EXEMPT
        )
    return [path for path in files if path.exists()]


def statement_anchor(rel: str, lines: list[str], line_number: int) -> str:
    """`file:line@sha256:<12hex>` over the statement slice (decl line through
    the first line containing ':=', inclusive, each line rstripped)."""
    slice_lines: list[str] = []
    for offset in range(STATEMENT_SLICE_CAP):
        index = line_number - 1 + offset
        if index >= len(lines):
            break
        slice_lines.append(lines[index].rstrip())
        if ":=" in lines[index]:
            break
    digest = hashlib.sha256("\n".join(slice_lines).encode("utf-8")).hexdigest()
    return f"{rel}:{line_number}@sha256:{digest[:12]}"


def parse_declarations(root: Path) -> tuple[dict[str, dict], list[str]]:
    declarations: dict[str, dict] = {}
    errors: list[str] = []
    for path in researchos_files(root):
        rel = path.relative_to(root).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        contexts: list[tuple[str, str | None]] = []
        for line_number, line in enumerate(lines, 1):
            namespace = NAMESPACE_RE.match(line)
            if namespace:
                contexts.append(("namespace", namespace.group(1)))
                continue
            if SECTION_RE.match(line):
                contexts.append(("section", None))
                continue
            if END_RE.match(line):
                if contexts:
                    contexts.pop()
                continue
            match = DECL_RE.match(line)
            if not match:
                continue
            if set(match.group("mods").split()) & {"private", "local"}:
                continue
            ns = ".".join(value for kind, value in contexts
                          if kind == "namespace" and value)
            qualified = (f"{ns}.{match.group('name')}" if ns
                         else match.group("name"))
            if qualified in declarations:
                errors.append(
                    "duplicate qualified declaration name "
                    f"{qualified!r}: {declarations[qualified]['file']}:"
                    f"{declarations[qualified]['line']} vs {rel}:{line_number}"
                )
                continue
            declarations[qualified] = {
                "kind": match.group("kind"),
                "file": rel,
                "line": line_number,
                "anchor": statement_anchor(rel, lines, line_number),
            }
    return declarations, errors


def build_registry(root: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    declarations, errors_decl = parse_declarations(root)
    errors.extend(errors_decl)

    domain_ids: set[str] = set()
    if DOMAIN_REGISTRY.exists():
        registry_json = json.loads(DOMAIN_REGISTRY.read_text(encoding="utf-8"))
        domain_ids = {d["id"] for d in registry_json.get("domains", [])}
    else:
        errors.append("domains/registry.json is missing")

    try:
        rows = parse_researchos_ledger(root)
    except (ValueError, FileNotFoundError) as exc:
        return {}, errors + [str(exc)]

    cited: dict[str, str] = {}          # declaration -> claim_id
    axiom_base: dict[str, str] = {}     # declaration -> declared base
    seen_claims: set[str] = set()
    entries: list[dict] = []

    for row in rows:
        claim = row["claim_id"]
        where = f"VERIFIED_RESEARCHOS.md:{row['line']} ({claim})"
        if claim in seen_claims:
            errors.append(f"{where}: duplicate claim_id")
        seen_claims.add(claim)

        prefix = next((p for p in PREFIX_DOMAINS if claim.startswith(p)), None)
        if prefix is None:
            errors.append(f"{where}: claim_id prefix not in the registered "
                          f"domain-prefix map {sorted(PREFIX_DOMAINS)}")
        elif PREFIX_DOMAINS[prefix] != row["domain"]:
            errors.append(f"{where}: prefix {prefix!r} does not match domain "
                          f"{row['domain']!r}")
        if row["domain"] not in domain_ids:
            errors.append(f"{where}: domain {row['domain']!r} is not in "
                          "domains/registry.json")

        subtree = DOMAIN_SUBTREES.get(row["domain"])
        for file in row["files"] or [strip_md(row["file"])]:
            if not file.startswith("ResearchOS/"):
                errors.append(f"{where}: cited file {file!r} is not under "
                              "ResearchOS/")
            elif subtree and not file.startswith(subtree):
                errors.append(f"{where}: {row['domain']} rows must cite files "
                              f"under {subtree}")
            if not (root / file).is_file():
                errors.append(f"{where}: cited file {file!r} does not exist")

        if row["axiom_base"] not in ALLOWED_AXIOM_BASES:
            errors.append(f"{where}: axiom_base {row['axiom_base']!r} not in "
                          f"{sorted(ALLOWED_AXIOM_BASES)}")
        if row["status"] != "proved":
            errors.append(f"{where}: status must be 'proved'")
        if not DATE_RE.match(strip_md(row["date"])):
            errors.append(f"{where}: date must be ISO YYYY-MM-DD")

        review = strip_md(row["review_record"])
        if review != "—" and not (root / review).is_file():
            errors.append(f"{where}: review_record {review!r} does not exist")
        contract = strip_md(row["source_contract"])
        if contract != "—":
            contract_file = contract.split("#", 1)[0]
            if not (root / contract_file).is_file():
                errors.append(f"{where}: source_contract file "
                              f"{contract_file!r} does not exist")

        row_declarations: list[str] = []
        for pattern in row["name_patterns"]:
            for name in expand_braces(pattern):
                declaration = declarations.get(name)
                if declaration is None:
                    errors.append(f"{where}: declaration {name!r} does not "
                                  "resolve in built ResearchOS source")
                    continue
                if declaration["file"] not in row["files"]:
                    errors.append(f"{where}: declaration {name!r} lives in "
                                  f"{declaration['file']}, not the cited file")
                if name in cited:
                    errors.append(f"{where}: declaration {name!r} is already "
                                  f"cited by {cited[name]}")
                    continue
                anchor_cell = strip_md(row["statement_anchor"])
                if anchor_cell != declaration["anchor"] and len(
                    [p for p in row["name_patterns"]]
                ) == 1:
                    errors.append(
                        f"{where}: stale statement_anchor — ledger has "
                        f"{anchor_cell!r}, source gives "
                        f"{declaration['anchor']!r}"
                    )
                cited[name] = claim
                axiom_base[name] = row["axiom_base"]
                row_declarations.append(name)

        if len(row["name_patterns"]) > 1:
            # Multi-declaration rows carry one anchor per declaration,
            # separated by spaces inside the cell, in citation order.
            anchor_cells = strip_md(row["statement_anchor"]).split()
            expected = [declarations[n]["anchor"] for n in row_declarations
                        if n in declarations]
            if anchor_cells != expected:
                errors.append(f"{where}: stale statement_anchor list — ledger "
                              f"has {anchor_cells!r}, source gives {expected!r}")

        if not row_declarations:
            errors.append(f"{where}: row resolved no declaration")
        entries.append({
            "claim_id": claim,
            "domain": row["domain"],
            "declarations": row_declarations,
            "files": row["files"],
            "axiom_base": row["axiom_base"],
            "method": row["method"],
            "status": row["status"],
        })

    uncovered = sorted(set(declarations) - set(cited))
    for name in uncovered:
        errors.append(
            f"inverse coverage: built public declaration {name!r} "
            f"({declarations[name]['file']}:{declarations[name]['line']}) has "
            "no VERIFIED_RESEARCHOS.md row"
        )

    registry = {
        "schema_version": 1,
        "source": "VERIFIED_RESEARCHOS.md + built public ResearchOS source "
                  "(audit harnesses excluded by exact path)",
        "ledger_rows": len(entries),
        "ledger_declarations": sorted(cited),
        "axiom_base": {name: axiom_base[name] for name in sorted(axiom_base)},
        "ledger_entries": entries,
        "declarations": {
            name: declarations[name] for name in sorted(declarations)
        },
    }
    return registry, errors


def main() -> int:
    check = "--check" in sys.argv
    registry, errors = build_registry(ROOT)
    if errors:
        print("researchos-registry check FAILED:" if check
              else "researchos-registry generation FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1
    text = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    if check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("researchos-registry check FAILED — "
                  "data/researchos_result_registry.json is stale; run "
                  "python3 scripts/gen_researchos_registry.py")
            return 1
        print(
            "researchos-registry check OK: "
            f"{registry['ledger_rows']} ledger rows -> "
            f"{len(registry['ledger_declarations'])} declarations, inverse "
            "coverage complete, anchors fresh."
        )
        return 0
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)} — {registry['ledger_rows']} rows, "
          f"{len(registry['ledger_declarations'])} declarations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
