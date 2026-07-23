#!/usr/bin/env python3
"""Ensure every GitHub workflow has one explicit operational disposition."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "repo" / "AUTOMATION_INVENTORY.json"
WORKFLOWS = ROOT / ".github" / "workflows"

EXPECTED_TRIGGERS = {
    "manual_only": {"workflow_dispatch"},
    "manual_or_self_test": {"workflow_dispatch", "push"},
    "push_pr_manual": {"push", "pull_request", "workflow_dispatch"},
    "scoped_push_pr_manual": {"push", "pull_request", "workflow_dispatch"},
    "target_push_or_manual": {"push", "workflow_dispatch"},
    "experiment_pr_or_manual": {"pull_request", "workflow_dispatch"},
}
SCOPED_POLICIES = {
    "manual_or_self_test",
    "scoped_push_pr_manual",
    "target_push_or_manual",
    "experiment_pr_or_manual",
}


def trigger_blocks(text: str) -> tuple[set[str], dict[str, str]]:
    match = re.search(r"^on:\s*$", text, flags=re.MULTILINE)
    if not match:
        return set(), {}
    tail = text[match.end():]
    end = re.search(r"^\S", tail, flags=re.MULTILINE)
    block = tail[:end.start()] if end else tail
    starts = list(re.finditer(r"^  ([a-z_]+):\s*$", block, flags=re.MULTILINE))
    names = {item.group(1) for item in starts}
    sections: dict[str, str] = {}
    for index, item in enumerate(starts):
        stop = starts[index + 1].start() if index + 1 < len(starts) else len(block)
        sections[item.group(1)] = block[item.end():stop]
    return names, sections


def main() -> int:
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    entries = data.get("workflows", [])
    errors: list[str] = []
    files = [entry.get("file") for entry in entries]
    actual = {
        path.relative_to(ROOT).as_posix() for path in WORKFLOWS.glob("*.yml")
    }
    declared = {path for path in files if isinstance(path, str)}

    if len(files) != len(declared):
        errors.append("workflow inventory contains duplicate or empty file entries")
    for path in sorted(actual - declared):
        errors.append(f"workflow is not classified: {path}")
    for path in sorted(declared - actual):
        errors.append(f"inventory references a missing workflow: {path}")

    allowed_dispositions = {
        "keep", "keep_conditional", "break_glass", "park", "review_for_retirement"
    }
    for entry in entries:
        path = entry.get("file", "<missing>")
        if entry.get("disposition") not in allowed_dispositions:
            errors.append(f"{path}: unsupported disposition {entry.get('disposition')!r}")
        if not entry.get("reason"):
            errors.append(f"{path}: missing reason")
        text = (ROOT / path).read_text(encoding="utf-8") if (ROOT / path).exists() else ""
        actual_triggers, blocks = trigger_blocks(text)
        policy = entry.get("trigger_policy")
        expected_triggers = EXPECTED_TRIGGERS.get(policy)
        if expected_triggers is None:
            errors.append(f"{path}: unsupported trigger_policy {policy!r}")
        elif actual_triggers != expected_triggers:
            errors.append(
                f"{path}: trigger policy mismatch "
                f"(declared={policy}, actual={sorted(actual_triggers)})"
            )
        if policy in SCOPED_POLICIES:
            for event in actual_triggers - {"workflow_dispatch", "workflow_call"}:
                if not re.search(r"^    paths:\s*$", blocks.get(event, ""),
                                 flags=re.MULTILINE):
                    errors.append(f"{path}: {event} trigger must be paths-scoped")
        if entry.get("spends_external_budget"):
            if policy not in {"manual_only", "manual_or_self_test"}:
                errors.append(f"{path}: paid workflow is not manual/self-test scoped")
            if "schedule" in actual_triggers:
                errors.append(f"{path}: paid workflow must not have a schedule trigger")

    by_disposition = {
        disposition: sum(entry.get("disposition") == disposition for entry in entries)
        for disposition in allowed_dispositions
    }
    if errors:
        print("automation-inventory check FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"automation-inventory check OK: {len(entries)} workflows classified; "
        f"{by_disposition['keep'] + by_disposition['keep_conditional']} kept, "
        f"{by_disposition['park']} parked, "
        f"{by_disposition['review_for_retirement']} retirement candidates, "
        f"{by_disposition['break_glass']} break-glass"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
