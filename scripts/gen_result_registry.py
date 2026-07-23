#!/usr/bin/env python3
"""Build an exact declaration-level registry for every VERIFIED.md ledger row."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from ledger_utils import expand_braces, parse_ledger

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "result_registry.json"

DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?"
    r"(?P<mods>(?:(?:private|protected|noncomputable|scoped|local|unsafe|partial)\s+)*)"
    r"(?P<kind>theorem|lemma|def|abbrev|instance|opaque|structure|class|inductive)\s+"
    r"(?P<name>[^\s(:\[{]+)"
)
ANON_INSTANCE_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?"
    r"(?:(?:noncomputable|scoped|local)\s+)*instance\s*:\s*(?P<target>.+)"
)
NAMESPACE_RE = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*$")
SECTION_RE = re.compile(r"^\s*section(?:\s+[A-Za-z_][A-Za-z0-9_']*)?\s*$")
END_RE = re.compile(r"^\s*end(?:\s+[^\s]+)?\s*$")


def lean_files() -> list[Path]:
    files: set[Path] = set()
    for base in (ROOT / "Ecdlp", ROOT / "ResearchOS"):
        if base.exists():
            files.update(path for path in base.rglob("*.lean") if "Targets" not in path.parts)
    for root_file in (ROOT / "Ecdlp.lean", ROOT / "ResearchOS.lean"):
        if root_file.exists():
            files.add(root_file)
    return sorted(files)


def parse_declarations() -> tuple[dict[str, dict], list[dict]]:
    """Return public named declarations and anonymous instance evidence."""
    declarations: dict[str, dict] = {}
    anonymous: list[dict] = []
    for path in lean_files():
        contexts: list[tuple[str, str | None]] = []
        rel = path.relative_to(ROOT).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
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
            if match:
                modifiers = set(match.group("mods").split())
                if modifiers & {"private", "local"}:
                    continue
                name = match.group("name")
                ns = ".".join(value for kind, value in contexts
                              if kind == "namespace" and value)
                qualified = f"{ns}.{name}" if ns else name
                declarations.setdefault(
                    qualified,
                    {
                        "name": name,
                        "namespace": ns,
                        "kind": match.group("kind"),
                        "file": rel,
                        "line": line_number,
                    },
                )
                continue

            instance = ANON_INSTANCE_RE.match(line)
            if instance:
                target = instance.group("target").split(":=")[0].strip()
                ns = ".".join(value for kind, value in contexts
                              if kind == "namespace" and value)
                anonymous.append(
                    {
                        "namespace": ns,
                        "target": target,
                        "file": rel,
                        "line": line_number,
                    }
                )
    return declarations, anonymous


def _candidate_declarations(
    cited: str,
    files: list[str],
    declarations: dict[str, dict],
    by_simple: dict[str, list[str]],
) -> list[str]:
    if cited in declarations:
        return [cited]
    simple = cited.rsplit(".", 1)[-1]
    candidates = by_simple.get(simple, [])
    in_files = [name for name in candidates if declarations[name]["file"] in files]
    if len(in_files) == 1:
        return in_files
    return candidates if len(candidates) == 1 else []


def _anonymous_match(cited: str, files: list[str], anonymous: list[dict]) -> dict | None:
    suffixes = {cited, ".".join(cited.split(".")[-2:]), cited.rsplit(".", 1)[-1]}
    for item in anonymous:
        if files and item["file"] not in files:
            continue
        target = item["target"]
        if any(suffix and (target == suffix or target.endswith(suffix)) for suffix in suffixes):
            return item
    return None


def build_registry() -> dict:
    declarations, anonymous = parse_declarations()
    by_simple: dict[str, list[str]] = defaultdict(list)
    by_file: dict[str, list[str]] = defaultdict(list)
    for name, declaration in declarations.items():
        by_simple[name.rsplit(".", 1)[-1]].append(name)
        by_file[declaration["file"]].append(name)

    entries: list[dict] = []
    unresolved: list[dict] = []
    exemptions: list[dict] = []
    ledger_declarations: set[str] = set()

    for row in parse_ledger(ROOT):
        references: list[dict] = []

        if ".lean" in row["file_cell"] and not row["files"]:
            unresolved.append(
                {
                    "ledger_id": row["id"],
                    "cited": row["file_cell"],
                    "reason": "file-cell-did-not-resolve",
                }
            )
        for file in row["files"]:
            if not (ROOT / file).is_file():
                unresolved.append(
                    {
                        "ledger_id": row["id"],
                        "cited": file,
                        "reason": "cited-source-file-missing",
                    }
                )

        def add_declaration(cited: str, canonical: str, resolution: str) -> None:
            if any(ref.get("canonical_name") == canonical for ref in references):
                return
            declaration = declarations[canonical]
            references.append(
                {
                    "cited": cited,
                    "canonical_name": canonical,
                    "resolution": resolution,
                    "kind": declaration["kind"],
                    "file": declaration["file"],
                    "line": declaration["line"],
                }
            )
            ledger_declarations.add(canonical)

        for pattern in row["name_patterns"]:
            expanded_patterns = expand_braces(pattern)
            for cited in expanded_patterns:
                if cited.endswith(".*"):
                    if not row["files"]:
                        unresolved.append(
                            {
                                "ledger_id": row["id"],
                                "cited": cited,
                                "reason": "wildcard-requires-file-scope",
                            }
                        )
                        continue
                    prefix = cited[:-1]
                    matches = sorted(
                        name for name, declaration in declarations.items()
                        if name.startswith(prefix)
                        and (not row["files"] or declaration["file"] in row["files"])
                    )
                    if not matches:
                        unresolved.append({"ledger_id": row["id"], "cited": cited})
                    for canonical in matches:
                        add_declaration(cited, canonical, "file-scoped-pattern")
                    continue

                candidates = _candidate_declarations(
                    cited, row["files"], declarations, by_simple
                )
                if len(candidates) == 1:
                    resolution = "exact" if candidates[0] == cited else "unique-source-match"
                    add_declaration(cited, candidates[0], resolution)
                    continue

                instance = _anonymous_match(cited, row["files"], anonymous)
                if instance:
                    item = {
                        "ledger_id": row["id"],
                        "cited": cited,
                        "resolution": "anonymous-instance-target",
                        **instance,
                    }
                    references.append(item)
                    exemptions.append(item)
                    continue
                unresolved.append({"ledger_id": row["id"], "cited": cited})

        # Wildcard rows and explicit "supporting" summaries intentionally denote
        # all public declarations in their source files.
        if "supporting" in row["theorem_cell"]:
            for file in row["files"]:
                for canonical in sorted(by_file.get(file, [])):
                    add_declaration("<supporting declarations>", canonical, "supporting-expansion")

        # If a ledger cell claims an instance alongside a named result, preserve
        # anonymous instance evidence instead of pretending it has a source name.
        if "instance" in row["theorem_cell"]:
            for item in anonymous:
                if item["file"] in row["files"]:
                    evidence = {
                        "ledger_id": row["id"],
                        "cited": item["target"],
                        "resolution": "anonymous-instance-target",
                        **item,
                    }
                    if evidence not in exemptions:
                        references.append(evidence)
                        exemptions.append(evidence)

        if not references:
            unresolved.append(
                {
                    "ledger_id": row["id"],
                    "cited": row["theorem_cell"],
                    "reason": "ledger-row-has-no-resolved-evidence",
                }
            )

        entries.append(
            {
                "id": row["id"],
                "claim": row["claim"],
                "theorem_cell": row["theorem_cell"],
                "declared_files": row["files"],
                "method": row["method"],
                "status": row["status"],
                "references": references,
            }
        )

    total_references = sum(len(entry["references"]) for entry in entries)
    registry = {
        "schema_version": 2,
        "source": "VERIFIED.md + built public Lean source (Targets excluded)",
        "ledger_rows": len(entries),
        "ledger_reference_count": total_references,
        "ledger_named_declarations": len(ledger_declarations),
        "anonymous_instance_exemptions": len(exemptions),
        "unresolved_reference_count": len(unresolved),
        "coverage_percent": 100.0 if not unresolved else round(
            100 * (total_references - len(unresolved)) / max(1, total_references), 2
        ),
        "declaration_count": len(declarations),
        "distinct_qualified_names": len(declarations),
        "verified_md_citations": len(ledger_declarations),
        "unresolved_references": unresolved,
        "resolution_exemptions": exemptions,
        "note": "Ledger rows are canonical accounting units; grouped cells resolve to declaration-level evidence here.",
        "ledger_declarations": sorted(ledger_declarations),
        "ledger_entries": entries,
        "declarations": {
            name: declaration for name, declaration in sorted(declarations.items())
        },
    }
    return registry


def main() -> int:
    check = "--check" in sys.argv
    registry = build_registry()
    text = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    unresolved = registry["unresolved_references"]

    if check:
        failed = False
        if unresolved:
            failed = True
            print("result-registry check FAILED — unresolved ledger references:")
            for item in unresolved:
                print(f"  - {item['ledger_id']}: {item['cited']}")
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            failed = True
            print("result-registry check FAILED — data/result_registry.json is stale; "
                  "run python3 scripts/gen_result_registry.py")
        if failed:
            return 1
        print(
            "result-registry check OK: "
            f"{registry['ledger_rows']} ledger rows -> "
            f"{registry['ledger_named_declarations']} named declarations + "
            f"{registry['anonymous_instance_exemptions']} anonymous-instance records; "
            "100% resolved."
        )
        return 0

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(
        f"wrote {OUT.relative_to(ROOT)} — {registry['ledger_rows']} ledger rows, "
        f"{registry['ledger_named_declarations']} named declarations, "
        f"{registry['anonymous_instance_exemptions']} anonymous-instance records, "
        f"{registry['unresolved_reference_count']} unresolved."
    )
    return 0 if not unresolved else 1


if __name__ == "__main__":
    raise SystemExit(main())
