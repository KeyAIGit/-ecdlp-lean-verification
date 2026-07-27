#!/usr/bin/env python3
"""Build the generated typed-evidence applicability state."""
from __future__ import annotations

import sys

from typed_evidence_lib import STATE_PATH, load_and_build, render_state


def main() -> int:
    check = "--check" in sys.argv
    problems, state = load_and_build()
    if problems:
        print("typed-evidence build FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    rendered = render_state(state)
    if check:
        if not STATE_PATH.is_file():
            print("typed-evidence check FAILED: generated state is missing")
            return 1
        if STATE_PATH.read_text(encoding="utf-8") != rendered:
            print("typed-evidence check FAILED: generated state is stale")
            return 1
        print(
            "typed-evidence check OK: "
            f"{state['counts']['cells']} cells, "
            f"{state['counts']['seed_eligible_cells']} seed-eligible, "
            f"{state['counts']['desk_decisions']} desk decisions, "
            "authorization remains zero."
        )
        return 0
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(rendered, encoding="utf-8")
    print(
        f"wrote {STATE_PATH.relative_to(STATE_PATH.parent.parent)}: "
        f"{state['counts']['cells']} cells, "
        f"{state['counts']['seed_eligible_cells']} seed-eligible."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
