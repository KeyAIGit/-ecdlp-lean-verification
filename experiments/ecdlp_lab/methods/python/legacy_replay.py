"""Exact replay of the 64 retained P1 generic-solver rows.

The legacy files are authenticated before use. Targets are derived only inside
this validation-side replay from the retained expected scalar; the reference
method receives only public curve, generator, order, target, seed, and budgets.
Historical wall times and memory estimates are descriptive fields and are never
compared as if they were current telemetry.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from experiments.ecdlp_lab.core.canonical import sha256_file
from experiments.ecdlp_lab.curves.p1_adapter import (
    LEGACY_CATALOG_PATH,
    LEGACY_CATALOG_SHA256,
    load_legacy_catalog,
    resolve_legacy_generator,
)
from experiments.ecdlp_lab.curves.producer_adapter import Curve
from experiments.framework.ec_oracle import Curve as OracleCurve

from .reference_dlog import (
    BSGS_METHOD_ID,
    RHO_METHOD_ID,
    MethodBudget,
    solve_reference,
)
from .validation import validate_candidate_independently

REPO_ROOT = Path(__file__).resolve().parents[4]
LEGACY_ASSAY_PATH = (
    REPO_ROOT
    / "experiments/ml_structure_probe/reports/p1_toy_scaling/assay_result.json"
)
LEGACY_ASSAY_SHA256 = (
    "6a4a6b8302877a9b6505d70fc246677c741c7b26cda314bdc17ac36a4edd044f"
)
LEGACY_RUNNER_PATH = (
    REPO_ROOT / "experiments/ml_structure_probe/p1_toy_scaling/run_assay.py"
)
LEGACY_RUNNER_SHA256 = (
    "6ab905adf8187729e818a92b047c83ff5f6b12d61fca95cfcd512cc3e24820c0"
)
EXPECTED_REPLAY_ROWS = 64


@dataclass(frozen=True)
class LegacyReplayRow:
    field_bits: int
    curve_index: int
    generator_index: int
    sample_ordinal: int
    legacy_method: str
    method_id: str
    expected_scalar: int
    legacy_candidate_scalar: int | None
    candidate_scalar: int | None
    legacy_p1_group_operations: int
    replay_group_operations: int
    candidate_matches: bool
    operation_count_matches: bool
    independently_validated: bool
    legacy_memory_bytes: int
    legacy_memory_is_estimate: bool
    legacy_wall_time_seconds: str
    timing_comparison: str

    @property
    def passed(self) -> bool:
        return (
            self.candidate_matches
            and self.operation_count_matches
            and self.independently_validated
        )


def _walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, Mapping):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _baseline_groups(document: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    groups: list[Mapping[str, Any]] = []
    seen: set[int] = set()
    for value in _walk(document):
        if not isinstance(value, Mapping):
            continue
        method = value.get("method")
        runs = value.get("runs")
        if method in {"bsgs", "pollard_rho"} and isinstance(runs, list):
            marker = id(value)
            if marker not in seen:
                groups.append(value)
                seen.add(marker)
    groups.sort(key=lambda row: (int(row["field_bits"]), str(row["method"])))
    return groups


def _verify_sources() -> None:
    if sha256_file(LEGACY_ASSAY_PATH) != LEGACY_ASSAY_SHA256:
        raise RuntimeError("legacy assay result digest mismatch")
    if sha256_file(LEGACY_RUNNER_PATH) != LEGACY_RUNNER_SHA256:
        raise RuntimeError("legacy P1 solver source digest mismatch")


def run_legacy_replay() -> list[LegacyReplayRow]:
    _verify_sources()
    document = json.loads(LEGACY_ASSAY_PATH.read_text(encoding="utf-8"))
    groups = _baseline_groups(document)
    catalog = load_legacy_catalog(
        catalog_path=LEGACY_CATALOG_PATH,
        catalog_sha256=LEGACY_CATALOG_SHA256,
        repo_root=REPO_ROOT,
    )
    output: list[LegacyReplayRow] = []
    generous = MethodBudget(
        max_group_law_invocations=2_000_000,
        max_steps=2_000_000,
        max_table_entries=65_536,
        max_memory_bytes=128 * 1024 * 1024,
    )

    for group in groups:
        field_bits = int(group["field_bits"])
        legacy_method = str(group["method"])
        method_id = BSGS_METHOD_ID if legacy_method == "bsgs" else RHO_METHOD_ID
        for run in group["runs"]:
            curve_index = int(run["curve_index"])
            generator_index = int(run["generator_index"])
            sample_ordinal = int(run["sample_ordinal"])
            fixture = resolve_legacy_generator(
                field_bits,
                curve_index,
                generator_index,
                catalog=catalog,
            )
            expected = int(run["expected_scalar"])
            legacy_candidate = run.get("candidate_scalar")
            if legacy_candidate is not None:
                legacy_candidate = int(legacy_candidate)
            oracle = OracleCurve(fixture.field_p, fixture.curve_a, fixture.curve_b)
            target = oracle.scalar_mul(expected, fixture.generator)
            curve = Curve(fixture.field_p, fixture.curve_a, fixture.curve_b)
            seed = field_bits * 1000 + sample_ordinal
            replay = solve_reference(
                method_id,
                curve,
                fixture.subgroup_order,
                fixture.generator,
                target,
                seed=seed,
                budget=generous,
            )
            independent = validate_candidate_independently(
                field_p=fixture.field_p,
                curve_a=fixture.curve_a,
                curve_b=fixture.curve_b,
                generator=fixture.generator,
                target=target,
                subgroup_order=fixture.subgroup_order,
                candidate_scalar=replay.candidate_scalar,
            )
            output.append(
                LegacyReplayRow(
                    field_bits=field_bits,
                    curve_index=curve_index,
                    generator_index=generator_index,
                    sample_ordinal=sample_ordinal,
                    legacy_method=legacy_method,
                    method_id=method_id,
                    expected_scalar=expected,
                    legacy_candidate_scalar=legacy_candidate,
                    candidate_scalar=replay.candidate_scalar,
                    legacy_p1_group_operations=int(run["group_operations"]),
                    replay_group_operations=replay.legacy_p1_group_operations,
                    candidate_matches=(
                        replay.candidate_scalar == legacy_candidate == expected
                    ),
                    operation_count_matches=(
                        replay.legacy_p1_group_operations
                        == int(run["group_operations"])
                    ),
                    independently_validated=independent,
                    legacy_memory_bytes=int(run["memory_bytes"]),
                    legacy_memory_is_estimate=True,
                    legacy_wall_time_seconds=str(run["wall_time_seconds"]),
                    timing_comparison=(
                        "historical_descriptive_only_not_current_telemetry"
                    ),
                )
            )

    if len(output) != EXPECTED_REPLAY_ROWS:
        raise RuntimeError(
            f"legacy solver replay produced {len(output)} rows, expected "
            f"{EXPECTED_REPLAY_ROWS}"
        )
    return output


def replay_summary(rows: list[LegacyReplayRow]) -> dict[str, Any]:
    return {
        "scope": "engineering replay of frozen toy baselines only",
        "expected_rows": EXPECTED_REPLAY_ROWS,
        "observed_rows": len(rows),
        "passed_rows": sum(row.passed for row in rows),
        "candidate_mismatches": sum(not row.candidate_matches for row in rows),
        "operation_count_mismatches": sum(
            not row.operation_count_matches for row in rows
        ),
        "validation_failures": sum(not row.independently_validated for row in rows),
        "historical_timing_policy": (
            "retained as descriptive strings; never compared with current runs"
        ),
        "rows": [asdict(row) | {"passed": row.passed} for row in rows],
    }


def main() -> int:
    rows = run_legacy_replay()
    print(json.dumps(replay_summary(rows), indent=2, sort_keys=True))
    return 0 if all(row.passed for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
