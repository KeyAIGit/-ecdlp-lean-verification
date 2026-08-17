#!/usr/bin/env python3
"""Generate a navigation-only index across the isolated verified ledgers.

The repository deliberately has two trust lanes:

* ``VERIFIED.md`` and ``data/result_registry.json`` for ECDLP / curve work;
* ``VERIFIED_RESEARCHOS.md`` and ``data/researchos_result_registry.json`` for
  ResearchOS domains.

This generator does not merge those sources of truth and never feeds the
ResearchOS rows into ECDLP headline statistics. It creates only a deterministic
cross-lane navigation layer for humans, the public site, and low-context agents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

ECDLP_REGISTRY = Path("data/result_registry.json")
RESEARCHOS_REGISTRY = Path("data/researchos_result_registry.json")
ECDLP_STATS = Path("data/stats.json")
OUT_JSON = Path("data/verified_index.json")
OUT_MARKDOWN = Path("VERIFIED_INDEX.md")
OUT_AGENT = Path("llms.txt")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "result"


def claim_title(value: str, limit: int = 180) -> str:
    text = compact_text(value)
    if len(text) <= limit:
        return text
    sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0]
    if 32 <= len(sentence) <= limit:
        return sentence
    return text[: limit - 1].rstrip() + "…"


def trust_level(
    *,
    lane: str,
    method: str,
    claim: str = "",
    display: str = "",
    axiom_base: str | None = None,
) -> str:
    trust_text = f"{method} {claim} {display} {axiom_base or ''}".casefold()
    compiler_markers = (
        "native_decide",
        "lean.ofreducebool",
        "compiler-trusted",
        "compiler trusted",
        "standard+native_decide",
    )
    if any(marker in trust_text for marker in compiler_markers):
        return "kernel_plus_compiler"
    if lane == "researchos" and axiom_base == "standard":
        return "kernel_standard"
    # The ECDLP registry records declarations and methods but does not persist a
    # complete per-row axiom-base classification. Absence of a native_decide
    # marker is therefore not enough to claim the standard-only trust base.
    return "kernel_audited"


def normalize_reference(reference: dict[str, Any]) -> dict[str, Any]:
    name = (
        reference.get("canonical_name")
        or reference.get("declaration")
        or reference.get("cited")
        or "<unresolved>"
    )
    result: dict[str, Any] = {
        "declaration": compact_text(name),
        "kind": compact_text(reference.get("kind", "declaration")),
        "file": compact_text(reference.get("file", "")),
    }
    line = reference.get("line")
    if isinstance(line, int) and line > 0:
        result["line"] = line
    return result


def normalize_ecdlp(registry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in registry.get("ledger_entries", []):
        ledger_id = compact_text(entry.get("id", ""))
        claim = compact_text(entry.get("claim", ""))
        display = compact_text(entry.get("theorem_cell", ""))
        references = [
            normalize_reference(reference)
            for reference in entry.get("references", [])
            if isinstance(reference, dict)
        ]
        files = sorted(
            {
                compact_text(path)
                for path in entry.get("declared_files", [])
                if compact_text(path)
            }
            | {reference["file"] for reference in references if reference["file"]}
        )
        method = compact_text(entry.get("method", "unspecified"))
        rows.append(
            {
                "uid": f"ecdlp/{ledger_id}",
                "slug": safe_slug(f"ecdlp-{ledger_id}"),
                "lane": "ecdlp",
                "domain": "ecdlp-ledger",
                "claim_id": claim,
                "title": claim_title(claim),
                "display": display,
                "method": method,
                "axiom_base": None,
                "trust_level": trust_level(
                    lane="ecdlp", method=method, claim=claim, display=display
                ),
                "status": compact_text(entry.get("status", "")),
                "files": files,
                "references": references,
                "source_ledger": "VERIFIED.md",
                "source_registry": ECDLP_REGISTRY.as_posix(),
            }
        )
    return rows


def normalize_researchos(registry: dict[str, Any]) -> list[dict[str, Any]]:
    declarations = registry.get("declarations", {})
    rows: list[dict[str, Any]] = []
    for entry in registry.get("ledger_entries", []):
        claim = compact_text(entry.get("claim_id", ""))
        names = [compact_text(name) for name in entry.get("declarations", [])]
        references: list[dict[str, Any]] = []
        for name in names:
            metadata = declarations.get(name, {}) if isinstance(declarations, dict) else {}
            references.append(
                normalize_reference(
                    {
                        "declaration": name,
                        "kind": metadata.get("kind", "declaration"),
                        "file": metadata.get("file", ""),
                        "line": metadata.get("line"),
                    }
                )
            )
        files = sorted(
            {
                compact_text(path)
                for path in entry.get("files", [])
                if compact_text(path)
            }
            | {reference["file"] for reference in references if reference["file"]}
        )
        method = compact_text(entry.get("method", "unspecified"))
        axiom_base = compact_text(entry.get("axiom_base", ""))
        rows.append(
            {
                "uid": f"researchos/{claim}",
                "slug": safe_slug(f"researchos-{claim}"),
                "lane": "researchos",
                "domain": compact_text(entry.get("domain", "unassigned")),
                "claim_id": claim,
                "title": claim_title(claim),
                "display": " ".join(f"`{name}`" for name in names),
                "method": method,
                "axiom_base": axiom_base,
                "trust_level": trust_level(
                    lane="researchos", method=method, claim=claim, axiom_base=axiom_base
                ),
                "status": compact_text(entry.get("status", "")),
                "files": files,
                "references": references,
                "source_ledger": "VERIFIED_RESEARCHOS.md",
                "source_registry": RESEARCHOS_REGISTRY.as_posix(),
            }
        )
    return rows


def validate(
    ecdlp_registry: dict[str, Any],
    researchos_registry: dict[str, Any],
    stats: dict[str, Any],
    rows: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    ecdlp_rows = [row for row in rows if row["lane"] == "ecdlp"]
    researchos_rows = [row for row in rows if row["lane"] == "researchos"]

    expected_ecdlp = ecdlp_registry.get("ledger_rows")
    expected_researchos = researchos_registry.get("ledger_rows")
    if len(ecdlp_rows) != expected_ecdlp:
        errors.append(
            f"ECDLP normalized rows {len(ecdlp_rows)} != registry rows {expected_ecdlp}"
        )
    if len(researchos_rows) != expected_researchos:
        errors.append(
            "ResearchOS normalized rows "
            f"{len(researchos_rows)} != registry rows {expected_researchos}"
        )
    if stats.get("ledger_rows") != expected_ecdlp:
        errors.append(
            f"data/stats.json ledger_rows {stats.get('ledger_rows')} != "
            f"ECDLP registry rows {expected_ecdlp}"
        )

    uids = [row["uid"] for row in rows]
    if len(uids) != len(set(uids)):
        duplicates = sorted(uid for uid, count in Counter(uids).items() if count > 1)
        errors.append(f"duplicate aggregate result uid(s): {duplicates}")

    slugs = [row["slug"] for row in rows]
    if len(slugs) != len(set(slugs)):
        duplicates = sorted(slug for slug, count in Counter(slugs).items() if count > 1)
        errors.append(f"duplicate aggregate result slug(s): {duplicates}")

    for row in rows:
        where = row["uid"]
        if row["status"] != "proved":
            errors.append(f"{where}: status must be proved")
        if not row["claim_id"]:
            errors.append(f"{where}: claim_id is empty")
        if row["lane"] == "ecdlp" and where == "ecdlp/":
            errors.append("ECDLP ledger row id is empty")
        if row["lane"] == "researchos" and not row.get("axiom_base"):
            errors.append(f"{where}: ResearchOS axiom_base is empty")
        if not row["files"]:
            errors.append(f"{where}: no source file recorded")
        for source_file in row["files"]:
            if row["lane"] == "ecdlp" and (
                source_file == "ResearchOS.lean" or source_file.startswith("ResearchOS/")
            ):
                errors.append(f"{where}: ECDLP lane leaks ResearchOS file {source_file}")
            if row["lane"] == "researchos" and not source_file.startswith("ResearchOS/"):
                errors.append(
                    f"{where}: ResearchOS lane cites file outside ResearchOS/: {source_file}"
                )
        for reference in row["references"]:
            line = reference.get("line")
            if line is not None and (not isinstance(line, int) or line < 1):
                errors.append(f"{where}: invalid source line {line!r}")

    return errors


def build_index(root: Path) -> dict[str, Any]:
    ecdlp_registry_path = root / ECDLP_REGISTRY
    researchos_registry_path = root / RESEARCHOS_REGISTRY
    stats_path = root / ECDLP_STATS

    ecdlp_registry = load_json(ecdlp_registry_path)
    researchos_registry = load_json(researchos_registry_path)
    stats = load_json(stats_path)

    rows = normalize_ecdlp(ecdlp_registry) + normalize_researchos(researchos_registry)
    rows.sort(key=lambda row: (row["lane"], row["domain"], row["claim_id"], row["uid"]))

    errors = validate(ecdlp_registry, researchos_registry, stats, rows)
    if errors:
        raise ValueError("verified-index validation failed:\n- " + "\n- ".join(errors))

    lanes = Counter(row["lane"] for row in rows)
    trust = Counter(row["trust_level"] for row in rows)
    domains = Counter(row["domain"] for row in rows)

    return {
        "schema_version": 1,
        "kind": "navigation_only_aggregate",
        "purpose": (
            "Cross-lane discovery of verified results while preserving the two canonical "
            "ledger and accounting boundaries."
        ),
        "generated_from": {
            ECDLP_REGISTRY.as_posix(): digest(ecdlp_registry_path),
            RESEARCHOS_REGISTRY.as_posix(): digest(researchos_registry_path),
            ECDLP_STATS.as_posix(): digest(stats_path),
        },
        "invariants": [
            "VERIFIED.md remains the canonical ECDLP ledger.",
            "VERIFIED_RESEARCHOS.md remains the canonical non-ECDLP ResearchOS ledger.",
            "ResearchOS rows do not feed data/stats.json or ECDLP headline counts.",
            "The aggregate row total is navigation only and is not a security metric.",
        ],
        "counts": {
            "navigation_rows_total": len(rows),
            "ecdlp_rows": lanes["ecdlp"],
            "researchos_rows": lanes["researchos"],
            "kernel_standard_rows": trust["kernel_standard"],
            "kernel_audited_rows": trust["kernel_audited"],
            "kernel_plus_compiler_rows": trust["kernel_plus_compiler"],
            "lanes": len(lanes),
            "domains": dict(sorted(domains.items())),
        },
        "lanes": [
            {
                "id": "ecdlp",
                "label": "ECDLP and curve formalization",
                "canonical_ledger": "VERIFIED.md",
                "registry": ECDLP_REGISTRY.as_posix(),
                "headline_accounting": ECDLP_STATS.as_posix(),
                "rows": lanes["ecdlp"],
            },
            {
                "id": "researchos",
                "label": "ResearchOS non-ECDLP domains",
                "canonical_ledger": "VERIFIED_RESEARCHOS.md",
                "registry": RESEARCHOS_REGISTRY.as_posix(),
                "headline_accounting": None,
                "rows": lanes["researchos"],
            },
        ],
        "results": rows,
    }


def md_cell(value: object) -> str:
    return compact_text(value).replace("|", "\\|")


def md_reference(reference: dict[str, Any]) -> str:
    file = reference.get("file", "")
    line = reference.get("line")
    declaration = md_cell(reference.get("declaration", "declaration"))
    if not file:
        return f"`{declaration}`"
    anchor = f"#L{line}" if line else ""
    return f"[`{declaration}`]({file}{anchor})"


def render_markdown(index: dict[str, Any]) -> str:
    counts = index["counts"]
    lines = [
        "# Verified results index",
        "",
        "> Generated by `scripts/gen_verified_index.py`. Do not hand-edit.",
        "",
        "This file is a navigation layer over two deliberately isolated ledgers. It is not a",
        "replacement source of truth, and the aggregate total is not an ECDLP security metric.",
        "",
        "## Trust boundary",
        "",
        "| Lane | Rows | Canonical ledger | Registry | Headline accounting |",
        "|---|---:|---|---|---|",
    ]
    for lane in index["lanes"]:
        accounting = lane["headline_accounting"] or "none (isolated from ECDLP counts)"
        lines.append(
            f"| {md_cell(lane['label'])} | {lane['rows']} | "
            f"[`{lane['canonical_ledger']}`]({lane['canonical_ledger']}) | "
            f"[`{lane['registry']}`]({lane['registry']}) | {md_cell(accounting)} |"
        )
    lines.extend(
        [
            "",
            "## Navigation snapshot",
            "",
            f"- Aggregate navigation rows: **{counts['navigation_rows_total']}**",
            "- ResearchOS rows declared with the standard kernel trust base: "
            f"**{counts['kernel_standard_rows']}**",
            "- ECDLP rows with allowed-TCB audit but no committed per-row base label: "
            f"**{counts['kernel_audited_rows']}**",
            "- Rows whose ledger metadata discloses compiler trust (`native_decide`): "
            f"**{counts['kernel_plus_compiler_rows']}**",
            "- Canonical live ECDLP counts remain in [`STATUS.md`](STATUS.md).",
            "",
        ]
    )

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in index["results"]:
        grouped.setdefault((row["lane"], row["domain"]), []).append(row)

    for (lane, domain), rows in grouped.items():
        lane_title = "ECDLP ledger" if lane == "ecdlp" else "ResearchOS ledger"
        lines.extend(
            [
                f"## {lane_title}: {domain}",
                "",
                "| Result | Claim | Declarations | Method | Trust |",
                "|---|---|---|---|---|",
            ]
        )
        for row in rows:
            refs = row["references"]
            declaration_cell = "<br>".join(md_reference(ref) for ref in refs[:4])
            if len(refs) > 4:
                declaration_cell += f"<br>+{len(refs) - 4} more declarations"
            if not declaration_cell:
                declaration_cell = "<unresolved display only>"
            trust_label = {
                "kernel_plus_compiler": "kernel + compiler",
                "kernel_standard": "kernel standard",
                "kernel_audited": "kernel audited; per-row base not materialized",
            }[row["trust_level"]]
            lines.append(
                f"| <a id=\"{row['slug']}\"></a>`{md_cell(row['uid'])}` | "
                f"{md_cell(row['title'])} | {declaration_cell} | "
                f"{md_cell(row['method'])} | {trust_label} |"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_agent_index(index: dict[str, Any]) -> str:
    counts = index["counts"]
    return f"""# KeyAI verified research workspace

Scope:
- This repository does not solve secp256k1 ECDLP and claims no shortcut.
- A green build means every built, ledgered theorem is accepted with no sorry.
- VERIFIED.md and VERIFIED_RESEARCHOS.md are separate canonical trust lanes.

Start here:
- Live canonical snapshot: STATUS.md
- Cross-lane verified-result navigation: VERIFIED_INDEX.md
- Machine-readable verified-result navigation: data/verified_index.json
- ECDLP canonical ledger: VERIFIED.md
- ResearchOS canonical ledger: VERIFIED_RESEARCHOS.md
- Repository architecture: REPOSITORY_ARCHITECTURE.md
- Current work router: tasks/NEXT.md
- Public result browser: results.html
- ECDLP route map: explore.html

Current navigation counts:
- ECDLP ledger rows: {counts['ecdlp_rows']}
- ResearchOS ledger rows: {counts['researchos_rows']}
- Aggregate navigation rows: {counts['navigation_rows_total']} (not a security metric)
- ResearchOS standard-base rows: {counts['kernel_standard_rows']}
- ECDLP audited rows without a committed per-row base label: {counts['kernel_audited_rows']}
- Rows with compiler trust disclosed in ledger metadata: {counts['kernel_plus_compiler_rows']}
"""


def expected_outputs(root: Path) -> dict[Path, str]:
    index = build_index(root)
    return {
        root / OUT_JSON: json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        root / OUT_MARKDOWN: render_markdown(index),
        root / OUT_AGENT: render_agent_index(index),
    }


def write_or_check(root: Path, *, check: bool) -> int:
    try:
        outputs = expected_outputs(root)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    stale: list[str] = []
    for path, text in outputs.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(path.relative_to(root).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")

    if stale:
        print("verified-index check FAILED; regenerate:", file=sys.stderr)
        for path in stale:
            print(f"- {path}", file=sys.stderr)
        return 1

    index = json.loads(outputs[root / OUT_JSON])
    counts = index["counts"]
    action = "verified" if check else "wrote"
    print(
        f"{action} cross-lane verified index: "
        f"{counts['ecdlp_rows']} ECDLP + {counts['researchos_rows']} ResearchOS = "
        f"{counts['navigation_rows_total']} navigation rows; trust lanes remain isolated."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args(argv)
    return write_or_check(args.root.resolve(), check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
