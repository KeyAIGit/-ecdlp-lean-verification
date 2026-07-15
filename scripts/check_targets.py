#!/usr/bin/env python3
"""CI gate: the prover-loop target registry (`targets/*.json`) is well-formed.

Keeps the autonomous loop honest about its own queue. Every JSON under `targets/` that is a
*loop target* (has an `id` and a `stem_file`) must:

  * carry a non-empty `status`; and
  * if it is OPEN (`status` in {todo, searching}), its `stem_file` must exist on disk.

An open target whose stem was deleted is a silent no-op: `prover_loop.py` catches the missing
stem and SKIPs it, so the row *looks* queued but never runs and nobody notices. This gate turns
that into a hard failure.

Foreign files that live in `targets/` but are not loop targets — notably `queue.json`
(`agent_day.py`'s `{_comment, targets}` schema, which has no top-level `id`/`stem_file`) — are
ignored. Mirrors `prover_loop.load_specs`, which likewise skips non-target JSON.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "targets"
OPEN_STATUSES = {"todo", "searching"}


def is_loop_target(spec: object) -> bool:
    """A loop target is a dict carrying both an `id` and a `stem_file` (what the loop needs to
    build a proof stem). Foreign registry files (e.g. queue.json) lack these and are ignored."""
    return isinstance(spec, dict) and "id" in spec and "stem_file" in spec


def main() -> int:
    if not REGISTRY.exists():
        print("no targets/ directory — nothing to check")
        return 0

    errors: list[str] = []
    targets = 0
    ignored = 0
    open_ok = 0

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
        sid = spec.get("id")
        status = spec.get("status")
        if not status:
            errors.append(f"{path.name}: target '{sid}' has no status")
            continue
        if status in OPEN_STATUSES:
            stem = spec.get("stem_file", "")
            if not (ROOT / stem).exists():
                errors.append(
                    f"{path.name}: OPEN target '{sid}' (status={status}) points at a missing "
                    f"stem_file '{stem}' — the loop would silently skip it")
            else:
                open_ok += 1

    if errors:
        print("target-registry check FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"target-registry check OK: {targets} loop targets "
          f"({open_ok} open with present stems, {ignored} foreign files ignored).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
