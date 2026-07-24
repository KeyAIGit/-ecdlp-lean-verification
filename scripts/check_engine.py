#!/usr/bin/env python3
"""CI gate for the ECDLP decision layer (``engine/``).

Fails the build when the mechanical gates stop agreeing with the project's own
recorded route dispositions, when a pre-registration is malformed, or when the
unit tests regress.

The point of gating the retrospective checks is drift. The substrate's route
dispositions and the gates in ``engine/core.py`` are two independent expressions
of the same judgement; if they diverge, someone must say which one is wrong. A
silent divergence would leave a selector that looks principled while ranking
against decisions the project actually made.

Run: ``python3 scripts/check_engine.py``
"""

from __future__ import annotations

import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from engine import retro  # noqa: E402  (path must be set first)
from engine.report import build_report  # noqa: E402


def main() -> int:
    failures: list[str] = []

    # ---- retrospective validation -------------------------------------
    report = retro.run_all()
    for check in report["checks"]:
        if not check["passed"]:
            name = check["check"]
            if name == "R1_threat_model_reproduction":
                if check["missed"]:
                    failures.append(
                        f"{name}: routes {check['missed']} declare a non-primary "
                        "threat model but were not shelved by threat_model_gate")
                if check.get("wrongly_shelved"):
                    failures.append(
                        f"{name}: routes {check['wrongly_shelved']} DO carry the "
                        "primary threat model but were shelved — the gate would "
                        "remove real work from consideration")
            elif name == "R1a_primary_threat_model_anchor":
                failures.append(
                    f"{name}: engine PRIMARY_THREAT_MODEL is "
                    f"{check['engine_constant']!r} but the substrate declares "
                    f"{check['substrate_declares']!r} — every threat-model check "
                    "downstream is measuring against the wrong target")
            elif name == "R2_non_degeneracy":
                failures.append(
                    f"{name}: gates disagree with the recorded route decision "
                    f"(promotable={check['gate_promotable']}, "
                    f"explorable={check['gate_explorable_without_prereg']}, "
                    f"substrate_selected={check['substrate_selected']})")
            elif name == "R0_preregistrations_wellformed":
                for prob in check["problems"]:
                    for err in prob["errors"]:
                        failures.append(f"{name}: {prob['candidate_id']}: {err}")
            else:
                failures.append(f"{name}: failed")

    # ---- the report must build for both tiers -------------------------
    for tier in ("exploration", "promotion"):
        try:
            build_report(tier)
        except Exception as exc:  # pragma: no cover - defensive
            failures.append(f"report build failed for tier {tier}: {exc!r}")

    # ---- unit tests ---------------------------------------------------
    loader = unittest.TestLoader()
    suite = loader.discover(str(REPO / "engine"), pattern="test_engine.py",
                            top_level_dir=str(REPO))
    result = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(suite)
    if not result.wasSuccessful():
        failures.append(
            f"engine unit tests: {len(result.failures)} failure(s), "
            f"{len(result.errors)} error(s)")

    if failures:
        print("ENGINE CHECK FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    r1 = next(c for c in report["checks"] if c["check"] == "R1_threat_model_reproduction")
    cal = next(c for c in report["checks"] if c["check"] == "R3_calibration")
    exploration = build_report("exploration")
    print(
        "engine check OK: "
        f"{r1['routes_total']} routes, {len(r1['gate_shelved'])} shelved by threat model "
        f"(0 missed); {exploration['counts']['proposals']} proposal(s), "
        f"{exploration['counts']['ranked']} ranked, "
        f"{exploration['counts']['shelved_wrong_threat_model']} shelved; "
        f"{cal['resolved_but_not_preregistered']} historical record(s) excluded from "
        f"calibration by design; {result.testsRun} unit tests passed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
