#!/usr/bin/env python3
"""Generate the deterministic Research Engine v0 state."""
from __future__ import annotations

import sys

from research_engine_lib import STATE_PATH, render_state, validate_all


def main() -> int:
    problems, state = validate_all()
    if problems:
        print("research-engine build FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    rendered = render_state(state)
    if "--check" in sys.argv:
        if not STATE_PATH.is_file() or STATE_PATH.read_text(encoding="utf-8") != rendered:
            print(
                "research-engine state is stale; run "
                "`python scripts/build_research_engine_state.py`",
                file=sys.stderr,
            )
            return 1
        print(
            "research-engine state OK: "
            f"{state['counts']['normalized_hypotheses']} hypotheses, "
            f"{state['counts']['outcome_events']} outcomes, "
            f"{state['counts']['selected_explorations']} selected explorations, "
            f"{state['counts']['ready_explorations']} ready."
        )
        return 0
    STATE_PATH.write_text(rendered, encoding="utf-8")
    print(
        f"wrote {STATE_PATH.relative_to(STATE_PATH.parent.parent)}: "
        f"{state['counts']['normalized_hypotheses']} hypotheses, "
        f"{state['counts']['outcome_events']} outcomes, "
        f"{state['counts']['selected_explorations']} selected explorations, "
        f"{state['counts']['ready_explorations']} ready."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
