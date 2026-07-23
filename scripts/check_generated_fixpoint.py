#!/usr/bin/env python3
"""Verify generated artifacts are fresh and reach a one-pass fixpoint."""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GENERATORS = [
    ["scripts/gen_stats.py"],
    ["scripts/build_frontier_map.py"],
    ["scripts/gen_result_registry.py"],
    ["scripts/gen_axiom_audit.py"],
    ["scripts/build_knowledge_graph.py"],
    ["scripts/coverage_report.py"],
    ["scripts/gen_status.py"],
    ["scripts/gen_source_registry.py"],
    ["scripts/build_ecdlp_decision_view.py"],
    ["scripts/export_agent_bundle.py", "--manifest"],
    ["scripts/build_dashboard.py"],
]

PURE_ARTIFACTS = [
    "data/stats.json",
    "badges/theorems.json",
    "data/frontier_map.json",
    "data/result_registry.json",
    "Ecdlp/LedgerAxiomAudit.lean",
    "data/knowledge_graph.json",
    "data/knowledge_graph.md",
    "COVERAGE.md",
    "STATUS.md",
    "data/source_registry.json",
    "repo/ECDLP_DECISION_SUBSTRATE.md",
    "bundles/MANIFEST.json",
]

SITE_ARTIFACTS = ["dashboard.html", "index.html", "explore.html"]
ALL_ARTIFACTS = PURE_ARTIFACTS + SITE_ARTIFACTS


def logical_digest(path: Path) -> str:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        data = text.encode("utf-8")
    except UnicodeDecodeError:
        pass
    return hashlib.sha256(data).hexdigest()


def snapshot(root: Path, paths: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for rel in paths:
        path = root / rel
        result[rel] = logical_digest(path) if path.exists() else "<missing>"
    return result


def changed(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(path for path in before if before[path] != after[path])


def run_generators(root: Path) -> None:
    env = dict(__import__("os").environ)
    env["PYTHONIOENCODING"] = "utf-8"
    for args in GENERATORS:
        result = subprocess.run(
            [sys.executable, *args],
            cwd=root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
        )
        if result.returncode:
            raise RuntimeError(
                f"generator failed ({' '.join(args)}):\n{result.stdout}"
            )


def ignore_copy(directory: str, names: list[str]) -> set[str]:
    ignored = {"__pycache__", ".lake", "node_modules"}
    return {name for name in names if name in ignored}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="fail when committed pure artifacts are stale")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="ecdlp-fixpoint-") as tmp:
        work = Path(tmp) / "repo"
        shutil.copytree(ROOT, work, ignore=ignore_copy)
        initial = snapshot(work, ALL_ARTIFACTS)
        try:
            run_generators(work)
            first = snapshot(work, ALL_ARTIFACTS)
            run_generators(work)
            second = snapshot(work, ALL_ARTIFACTS)
        except RuntimeError as exc:
            print(f"generated-fixpoint check FAILED: {exc}", file=sys.stderr)
            return 1

    stale = changed(
        {path: initial[path] for path in PURE_ARTIFACTS},
        {path: first[path] for path in PURE_ARTIFACTS},
    )
    non_idempotent = changed(first, second)
    if (args.check and stale) or non_idempotent:
        print("generated-fixpoint check FAILED:", file=sys.stderr)
        for path in stale if args.check else []:
            print(f"- stale pure artifact: {path}", file=sys.stderr)
        for path in non_idempotent:
            print(f"- changes again on second generator pass: {path}", file=sys.stderr)
        return 1

    site_refresh = changed(
        {path: initial[path] for path in SITE_ARTIFACTS},
        {path: first[path] for path in SITE_ARTIFACTS},
    )
    print(
        "generated-fixpoint check OK: "
        f"{len(PURE_ARTIFACTS)} pure artifacts fresh; "
        f"{len(ALL_ARTIFACTS)} artifacts stable after one pass"
        + (f"; site refresh candidates: {', '.join(site_refresh)}" if site_refresh else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
