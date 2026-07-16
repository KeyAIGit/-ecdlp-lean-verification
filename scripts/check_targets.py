#!/usr/bin/env python3
"""CI gate: the prover-loop target registry (`targets/*.json`) is well-formed.

Keeps the autonomous loop honest about its own queue. Every JSON under `targets/` that is a
*loop target* (has an `id` and a `stem_file` key) must:

  * carry a non-empty `status`;
  * if it is OPEN (`status` in {todo, searching}), its `stem_file` must name a file that
    exists on disk (a missing or null stem on an open target is a silent no-op:
    `prover_loop.py` catches it and SKIPs, so the row *looks* queued but never runs and
    nobody notices — this gate turns that into a hard failure);
  * whatever the status, a non-null `stem_file` must point at an existing file. Promotion
    consumes the stem (`promote_candidate.py` removes it from `Ecdlp/Targets/` and nulls
    the pointer), so a dead pointer means a promotion bypassed the script — flag it.

`targets/queue.json` (`agent_day.py`'s `{_comment, targets}` schema, no top-level `id`) is
not a loop target but is validated against the same registry:

  * every queue entry must name a registered loop target (match on the registry `name` or
    `id`) — the queue must never hold work the registry does not track;
  * a queue entry whose registry target is already `verified` is an error — a paid
    dispatch would re-prove a solved theorem (the defect that got the per-push prover
    step removed from ci.yml).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "targets"
QUEUE = REGISTRY / "queue.json"
OPEN_STATUSES = {"todo", "searching"}


def is_loop_target(spec: object) -> bool:
    """A loop target is a dict carrying both an `id` and a `stem_file` key (what the loop
    needs to build a proof stem; the value may be null once the stem is consumed by
    promotion). Foreign registry files (e.g. queue.json) lack these and are ignored."""
    return isinstance(spec, dict) and "id" in spec and "stem_file" in spec


def check_target(name: str, spec: dict, errors: list[str]) -> bool:
    """Validate one loop target. Returns True when it is an open target with a live stem."""
    sid = spec.get("id")
    status = spec.get("status")
    if not status:
        errors.append(f"{name}: target '{sid}' has no status")
        return False
    stem = spec.get("stem_file")
    if status in OPEN_STATUSES:
        if not stem:
            errors.append(
                f"{name}: OPEN target '{sid}' (status={status}) has a null/empty "
                f"stem_file — the loop would silently skip it")
        elif not (ROOT / stem).exists():
            errors.append(
                f"{name}: OPEN target '{sid}' (status={status}) points at a missing "
                f"stem_file '{stem}' — the loop would silently skip it")
        else:
            return True
    elif stem and not (ROOT / stem).exists():
        errors.append(
            f"{name}: target '{sid}' (status={status}) carries a dead stem_file pointer "
            f"'{stem}' — promotion consumes the stem and must null the pointer "
            f"(scripts/promote_candidate.py)")
    return False


def check_queue(by_key: dict[str, dict], errors: list[str]) -> int:
    """Validate queue.json entries against the loop-target registry. Returns entry count."""
    if not QUEUE.exists():
        return 0
    try:
        queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    except ValueError as exc:
        errors.append(f"queue.json: invalid JSON ({exc})")
        return 0
    entries = queue.get("targets") if isinstance(queue, dict) else None
    if not isinstance(entries, list):
        errors.append("queue.json: no `targets` list (agent_day.py schema)")
        return 0
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict) or not entry.get("name"):
            errors.append(f"queue.json: entry #{i} has no name")
            continue
        qname = entry["name"]
        spec = by_key.get(qname)
        if spec is None:
            errors.append(
                f"queue.json: entry '{qname}' has no registry JSON under targets/ "
                f"(need a loop target whose `name` or `id` is '{qname}') — the queue "
                f"must never hold work the registry does not track")
        elif spec.get("status") == "verified":
            where = spec.get("verified_in") or spec.get("proved_as") or "see registry"
            errors.append(
                f"queue.json: entry '{qname}' is already verified ({where}) — remove it "
                f"from the queue or a dispatch re-proves a solved target")
    return len(entries)


def main() -> int:
    if not REGISTRY.exists():
        print("no targets/ directory — nothing to check")
        return 0

    errors: list[str] = []
    targets = 0
    ignored = 0
    open_ok = 0
    by_key: dict[str, dict] = {}

    for path in sorted(REGISTRY.glob("*.json")):
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        if not is_loop_target(spec):
            ignored += 1
            continue
        targets += 1
        open_ok += check_target(path.name, spec, errors)
        for key in (spec.get("id"), spec.get("name")):
            if key:
                by_key[key] = spec

    queued = check_queue(by_key, errors)

    if errors:
        print("target-registry check FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"target-registry check OK: {targets} loop targets "
          f"({open_ok} open with present stems, {queued} queue entries registered, "
          f"{ignored} foreign files ignored).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
