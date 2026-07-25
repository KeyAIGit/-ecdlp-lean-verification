#!/usr/bin/env python3
"""Validate Research Engine v0 policy, events, selector, and generated state."""
from __future__ import annotations

import sys

from research_engine_lib import STATE_PATH, render_state, validate_all


def main() -> int:
    problems, state = validate_all()
    if STATE_PATH.is_file():
        if STATE_PATH.read_text(encoding="utf-8") != render_state(state):
            problems.append("data/research_engine_state.json is stale")
    else:
        problems.append("data/research_engine_state.json is missing")
    if problems:
        print("research-engine check FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    selected = ", ".join(
        item["candidate_id"] for item in state["selected_sequence"]
    )
    print(
        "research-engine check OK: "
        f"{state['counts']['normalized_hypotheses']} hypotheses, "
        f"{state['counts']['outcome_events']} retained outcomes, "
        f"selected sequence [{selected}], "
        f"{state['counts']['ready_explorations']} ready, "
        "promotion remains disabled."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
