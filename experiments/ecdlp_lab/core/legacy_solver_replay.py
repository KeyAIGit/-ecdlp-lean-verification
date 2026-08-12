"""Authenticated, validation-side projection of the frozen P1 solver rows.

The retained assay contains discrete-log answers and observational floats.  It
is therefore never a method input and is not parsed by the lab's ordinary
integer-only JSON loader.  This module first authenticates its raw bytes, then
projects only the fixed replay fields.  A method can receive only the immutable
``PublicReplayInput`` returned by ``LegacyReplayCase.to_public_input()``.

The legacy runner is a provenance source, not an import dependency.  Importing
it would also pull numpy/scipy/sklearn into the dependency-light reference path.
"""

from __future__ import annotations

import importlib
import json
import math
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

from experiments.ecdlp_lab.curves.p1_adapter import (
    LegacyCatalog,
    load_legacy_catalog,
    resolve_legacy_generator,
)

from .canonical import (
    is_sha256,
    sha256_bytes,
    sha256_json,
    strict_loads,
)
from .catalog_registry import LEGACY_CATALOG_ID, resolve_catalog
from .issues import Issue
from .paths import PathSafetyError, resolve_artifact_path


REPO_ROOT = Path(__file__).resolve().parents[3]
LOCATOR_PATH = (
    "experiments/ecdlp_lab/fixtures/methods/legacy_p1_solver_replay_v1.json"
)
LOCATOR_RAW_SHA256 = (
    "56f21ebfdcf12e11ebeb803d230883fd143852c10572fd3dbe0253e3eddf058a"
)
LOCATOR_SEMANTIC_SHA256 = (
    "d5b1295f7e02aa3829aaa680786b9f39896f6dc77df0b8a5cec7828e6b39380d"
)

MAX_LOCATOR_BYTES = 64 * 1024
MAX_ASSAY_BYTES = 512 * 1024
MAX_SOURCE_BYTES = 512 * 1024
MAX_QUARANTINE_BYTES = 128 * 1024

_FIELD_BITS = (13, 16, 20, 24)
_LEGACY_METHODS = ("bsgs", "pollard_rho")
_METHOD_IDS = {
    "bsgs": "bsgs_v1",
    "pollard_rho": "ordinary_rho_xmod3_v1",
}
_SOURCE_FUNCTIONS = {
    "bsgs": "bsgs_solve",
    "pollard_rho": "pollard_rho_solve",
}
_EXPECTED_BASELINES = tuple(
    (field_bits, method)
    for field_bits in _FIELD_BITS
    for method in _LEGACY_METHODS
)

_LOCATOR_KEYS = frozenset(
    {
        "schema_version",
        "fixture_kind",
        "sources",
        "join",
        "methods",
        "golden",
        "schema_only_quarantine",
    }
)
_SOURCE_KEYS = frozenset(
    {
        "assay_result",
        "catalog_registry",
        "curve_catalog",
        "independent_oracle",
        "legacy_runner",
    }
)


class LegacyReplayError(ValueError):
    """The frozen replay authority or its semantic projection drifted."""


@dataclass(frozen=True)
class DerivedFrom:
    """Exact historical implementation locator carried by a replay case."""

    source_path: str
    source_function: str
    source_sha256: str


@dataclass(frozen=True)
class PublicReplayInput:
    """Only the public ECDLP problem that may cross the method boundary."""

    method_id: str
    curve_catalog_sha256: str
    curve_fixture_id: str
    curve_id: str
    field_bits: int
    subgroup_order_bits: int
    p: int
    a: int
    b: int
    G: tuple[int, int]
    Q: tuple[int, int]
    ell: int
    seed: int

    def __post_init__(self) -> None:
        for name in (
            "method_id",
            "curve_catalog_sha256",
            "curve_fixture_id",
            "curve_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise LegacyReplayError(f"public replay {name} must be non-empty")
        if not is_sha256(self.curve_catalog_sha256):
            raise LegacyReplayError("public replay catalog digest is invalid")
        for name, minimum in (
            ("field_bits", 3),
            ("subgroup_order_bits", 2),
            ("p", 5),
            ("a", 0),
            ("b", 0),
            ("ell", 2),
            ("seed", 0),
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                raise LegacyReplayError(
                    f"public replay {name} must be an integer >= {minimum}"
                )
        if self.seed > (1 << 64) - 1:
            raise LegacyReplayError("public replay seed exceeds unsigned 64-bit range")
        if self.field_bits != self.p.bit_length():
            raise LegacyReplayError("public replay field bit length drifted")
        if self.subgroup_order_bits != self.ell.bit_length():
            raise LegacyReplayError("public replay subgroup bit length drifted")
        if not (0 <= self.a < self.p and 0 <= self.b < self.p):
            raise LegacyReplayError(
                "public replay curve coefficients are not canonical"
            )
        for name in ("G", "Q"):
            point = getattr(self, name)
            if (
                not isinstance(point, tuple)
                or len(point) != 2
                or any(
                    isinstance(coordinate, bool)
                    or not isinstance(coordinate, int)
                    or not 0 <= coordinate < self.p
                    for coordinate in point
                )
            ):
                raise LegacyReplayError(
                    f"public replay {name} must be a canonical affine point"
                )

    def as_dict(self) -> dict[str, Any]:
        """Return the alias-preserving map used by the methods adapter."""

        return {
            "method_id": self.method_id,
            "curve_catalog_sha256": self.curve_catalog_sha256,
            "curve_fixture_id": self.curve_fixture_id,
            "curve_id": self.curve_id,
            "field_bits": self.field_bits,
            "subgroup_order_bits": self.subgroup_order_bits,
            "p": self.p,
            "a": self.a,
            "b": self.b,
            "G": list(self.G),
            "Q": list(self.Q),
            "ell": self.ell,
            "seed": self.seed,
        }


@dataclass(frozen=True)
class ValidatorReplayExpectation:
    """Private replay evidence; never pass this object to a method."""

    sample_ordinal: int
    record_index: int
    curve_index: int
    generator_index: int
    expected_scalar: int = field(repr=False)
    legacy_candidate_scalar: int = field(repr=False)
    legacy_group_operations: int
    legacy_memory_bytes: int
    bsgs_offline_setup_group_law_invocations: int | None
    bsgs_online_target_group_law_invocations: int | None
    bsgs_table_entries: int | None


@dataclass(frozen=True)
class LegacyReplayCase:
    """One authenticated replay case with an explicit public/private split."""

    case_id: str
    legacy_method: str
    derived_from: DerivedFrom
    validator_only: ValidatorReplayExpectation = field(repr=False)
    _public_input: PublicReplayInput = field(repr=False)

    def to_public_input(self) -> PublicReplayInput:
        """Project away all source-row identities and discrete-log answers."""

        return self._public_input


@dataclass(frozen=True)
class LegacyReplayReport:
    """Summary of a fully authenticated and structurally verified replay set."""

    passed: bool
    issues: tuple[Issue, ...]
    fixture_kind: str
    locator_raw_sha256: str
    locator_semantic_sha256: str
    case_count: int
    success_count: int
    bsgs_case_count: int
    rho_case_count: int
    case_identity_sha256: str
    legacy_group_operations_vector_sha256: str
    bsgs_legacy_group_operations: int
    bsgs_offline_setup_group_law_invocations: int
    bsgs_online_target_group_law_invocations: int
    bsgs_table_entries: int
    bsgs_estimated_algorithmic_table_bytes: int
    rho_legacy_group_operations: int
    expected_rho_floyd_iterations: int
    expected_rho_restarts: int
    expected_rho_collisions: int
    expected_rho_noninvertible_collisions: int
    expected_rho_invalid_candidate_collisions: int
    schema_only_quarantine_verified: bool


def _fail(path: str, detail: str) -> LegacyReplayError:
    return LegacyReplayError(f"{path}: {detail}")


def _exact_object(
    value: Any, expected_keys: frozenset[str], path: str
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _fail(path, "must be an object")
    actual = frozenset(value)
    if actual != expected_keys:
        raise _fail(
            path,
            "key set drifted "
            f"(missing={sorted(expected_keys - actual)}, "
            f"unknown={sorted(actual - expected_keys)})",
        )
    return value


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _fail(path, "must be an object")
    return value


def _array(value: Any, path: str, *, length: int | None = None) -> list[Any]:
    if not isinstance(value, list):
        raise _fail(path, "must be an array")
    if length is not None and len(value) != length:
        raise _fail(path, f"must contain exactly {length} entries")
    return value


def _integer(value: Any, path: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise _fail(path, f"must be an integer >= {minimum}")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise _fail(path, "must be a non-empty string")
    return value


def _read_verified(
    repo_root: Path,
    entry: dict[str, Any],
    path: str,
    *,
    max_bytes: int,
) -> bytes:
    relative_path = _string(entry.get("path"), f"{path}.path")
    expected_sha256 = entry.get("sha256")
    if not is_sha256(expected_sha256):
        raise _fail(f"{path}.sha256", "must be a lowercase SHA-256 digest")
    try:
        resolved = resolve_artifact_path(repo_root, relative_path, must_exist=True)
    except (OSError, PathSafetyError, TypeError, ValueError) as error:
        raise _fail(f"{path}.path", str(error)) from error
    if not resolved.is_file():
        raise _fail(f"{path}.path", "must resolve to a regular file")
    try:
        size = resolved.stat().st_size
        if size > max_bytes:
            raise _fail(f"{path}.path", f"file exceeds {max_bytes} byte limit")
        raw = resolved.read_bytes()
    except OSError as error:
        raise _fail(f"{path}.path", f"cannot read file: {error}") from error
    if len(raw) > max_bytes:
        raise _fail(f"{path}.path", f"file exceeds {max_bytes} byte limit")
    if sha256_bytes(raw) != expected_sha256:
        raise _fail(f"{path}.sha256", "raw file digest mismatch")
    return raw


def _unique_legacy_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise LegacyReplayError(f"duplicate legacy JSON key: {key}")
        result[key] = value
    return result


def _legacy_int(token: str) -> int:
    if token == "-0":
        raise LegacyReplayError("negative zero in legacy JSON")
    return int(token, 10)


def _reject_legacy_constant(token: str) -> None:
    raise LegacyReplayError(f"non-finite legacy JSON number: {token}")


def _safe_legacy_json(payload: bytes, *, label: str) -> Any:
    """Parse authenticated legacy bytes while retaining finite decimals."""

    try:
        text = payload.decode("utf-8", errors="strict")
        return json.loads(
            text,
            object_pairs_hook=_unique_legacy_object,
            parse_int=_legacy_int,
            parse_float=Decimal,
            parse_constant=_reject_legacy_constant,
        )
    except LegacyReplayError:
        raise
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise LegacyReplayError(f"{label}: invalid legacy JSON: {error}") from error


def _load_locator(repo_root: Path) -> dict[str, Any]:
    try:
        path = resolve_artifact_path(repo_root, LOCATOR_PATH, must_exist=True)
    except (OSError, PathSafetyError, TypeError, ValueError) as error:
        raise _fail("$.locator", str(error)) from error
    if not path.is_file():
        raise _fail("$.locator", "must resolve to a regular file")
    try:
        size = path.stat().st_size
        if size > MAX_LOCATOR_BYTES:
            raise _fail("$.locator", f"file exceeds {MAX_LOCATOR_BYTES} byte limit")
        raw = path.read_bytes()
    except OSError as error:
        raise _fail("$.locator", f"cannot read file: {error}") from error
    if len(raw) > MAX_LOCATOR_BYTES:
        raise _fail("$.locator", f"file exceeds {MAX_LOCATOR_BYTES} byte limit")
    if sha256_bytes(raw) != LOCATOR_RAW_SHA256:
        raise _fail("$.locator", "raw checksum does not match frozen P03 locator")
    try:
        locator = strict_loads(raw, label=LOCATOR_PATH)
    except ValueError as error:
        raise _fail("$.locator", str(error)) from error
    locator = _exact_object(locator, _LOCATOR_KEYS, "$")
    semantic_sha256 = sha256_json(locator)
    if semantic_sha256 != LOCATOR_SEMANTIC_SHA256:
        raise _fail("$.locator", "semantic checksum does not match frozen P03 locator")
    if locator.get("schema_version") != 1:
        raise _fail("$.schema_version", "must equal 1")
    if locator.get("fixture_kind") != "legacy_p1_solver_replay_locator_v1":
        raise _fail("$.fixture_kind", "unexpected fixture kind")
    _exact_object(locator.get("sources"), _SOURCE_KEYS, "$.sources")
    return locator


def _verify_quarantine(repo_root: Path, locator: dict[str, Any]) -> None:
    quarantine = _object(
        locator.get("schema_only_quarantine"), "$.schema_only_quarantine"
    )
    if quarantine.get("eligible_for_conformance") is not False:
        raise _fail(
            "$.schema_only_quarantine.eligible_for_conformance", "must be false"
        )
    raw = _read_verified(
        repo_root,
        quarantine,
        "$.schema_only_quarantine",
        max_bytes=MAX_QUARANTINE_BYTES,
    )
    try:
        result = strict_loads(raw, label=quarantine["path"])
    except ValueError as error:
        raise _fail("$.schema_only_quarantine.path", str(error)) from error
    result = _object(result, "$.schema_only_quarantine.result")
    counters = _object(
        result.get("counters"), "$.schema_only_quarantine.result.counters"
    )
    observed = {
        "legacy_p1_group_operations": counters.get("legacy_p1_group_operations"),
        "method_self_check_group_law_invocations": _object(
            counters.get("method_self_check"),
            "$.schema_only_quarantine.result.counters.method_self_check",
        ).get("group_law_invocations"),
        "offline_setup_group_law_invocations": _object(
            counters.get("offline_setup"),
            "$.schema_only_quarantine.result.counters.offline_setup",
        ).get("group_law_invocations"),
        "online_target_group_law_invocations": _object(
            counters.get("online_target"),
            "$.schema_only_quarantine.result.counters.online_target",
        ).get("group_law_invocations"),
    }
    if observed != quarantine.get("declared_counters"):
        raise _fail(
            "$.schema_only_quarantine.declared_counters",
            "does not describe the authenticated schema example",
        )


def _catalog_from_locator(
    repo_root: Path, sources: dict[str, Any]
) -> LegacyCatalog:
    registry = _object(sources.get("catalog_registry"), "$.sources.catalog_registry")
    _read_verified(
        repo_root,
        registry,
        "$.sources.catalog_registry",
        max_bytes=MAX_SOURCE_BYTES,
    )
    catalog_source = _object(sources.get("curve_catalog"), "$.sources.curve_catalog")
    if catalog_source.get("catalog_id") != LEGACY_CATALOG_ID:
        raise _fail("$.sources.curve_catalog.catalog_id", "wrong catalog authority")
    digest = catalog_source.get("sha256")
    try:
        authority = resolve_catalog(digest, repo_root=repo_root)
    except ValueError as error:
        raise _fail("$.sources.curve_catalog", str(error)) from error
    if (
        authority.catalog_id != catalog_source.get("catalog_id")
        or authority.path != catalog_source.get("path")
        or authority.sha256 != digest
    ):
        raise _fail(
            "$.sources.curve_catalog", "locator differs from registry authority"
        )
    try:
        return load_legacy_catalog(
            catalog_path=authority.path,
            catalog_sha256=authority.sha256,
            repo_root=repo_root,
        )
    except ValueError as error:
        raise _fail("$.sources.curve_catalog", str(error)) from error


def _method_metadata(locator: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = _array(locator.get("methods"), "$.methods", length=2)
    result: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(rows):
        row = _object(value, f"$.methods[{index}]")
        method = _string(row.get("legacy_method"), f"$.methods[{index}].legacy_method")
        if method in result:
            raise _fail(f"$.methods[{index}].legacy_method", "duplicate method")
        if row.get("method_id") != _METHOD_IDS.get(method):
            raise _fail(f"$.methods[{index}].method_id", "method mapping drifted")
        if row.get("source_function") != _SOURCE_FUNCTIONS.get(method):
            raise _fail(f"$.methods[{index}].source_function", "source locator drifted")
        if row.get("case_count") != 32:
            raise _fail(f"$.methods[{index}].case_count", "must equal 32")
        result[method] = row
    if tuple(result) != _LEGACY_METHODS:
        raise _fail("$.methods", "method rows are not in frozen order")
    return result


def _oracle_module(repo_root: Path, sources: dict[str, Any]) -> Any:
    oracle = _object(sources.get("independent_oracle"), "$.sources.independent_oracle")
    _read_verified(
        repo_root,
        oracle,
        "$.sources.independent_oracle",
        max_bytes=MAX_SOURCE_BYTES,
    )
    return importlib.import_module("experiments.framework.ec_oracle")


def _ceil_sqrt(value: int) -> int:
    root = math.isqrt(value)
    return root if root * root == value else root + 1


def _build_cases(
    repo_root: Path,
    locator: dict[str, Any],
    catalog: LegacyCatalog,
) -> tuple[LegacyReplayCase, ...]:
    sources = _object(locator["sources"], "$.sources")
    runner = _object(sources.get("legacy_runner"), "$.sources.legacy_runner")
    _read_verified(
        repo_root,
        runner,
        "$.sources.legacy_runner",
        max_bytes=MAX_SOURCE_BYTES,
    )
    assay_source = _object(sources.get("assay_result"), "$.sources.assay_result")
    assay_raw = _read_verified(
        repo_root,
        assay_source,
        "$.sources.assay_result",
        max_bytes=MAX_ASSAY_BYTES,
    )
    assay = _safe_legacy_json(assay_raw, label=assay_source["path"])
    assay = _object(assay, "$.assay")
    if assay.get("catalog_sha256") != catalog.raw_sha256:
        raise _fail("$.assay.catalog_sha256", "does not bind the trusted catalog")

    oracle = _oracle_module(repo_root, sources)
    method_rows = _method_metadata(locator)
    baselines = _array(
        assay.get("solver_baselines"),
        "$.assay.solver_baselines",
        length=8,
    )
    observed_baselines: list[tuple[int, str]] = []
    cases: list[LegacyReplayCase] = []

    for baseline_index, raw_baseline in enumerate(baselines):
        baseline_path = f"$.assay.solver_baselines[{baseline_index}]"
        baseline = _object(raw_baseline, baseline_path)
        field_bits = _integer(
            baseline.get("field_bits"),
            f"{baseline_path}.field_bits",
            minimum=3,
        )
        legacy_method = _string(baseline.get("method"), f"{baseline_path}.method")
        observed_baselines.append((field_bits, legacy_method))
        if legacy_method not in method_rows:
            raise _fail(f"{baseline_path}.method", "unknown legacy method")
        if baseline.get("targets") != 8 or baseline.get("successes") != 8:
            raise _fail(baseline_path, "must retain eight successful targets")
        success_rate = baseline.get("success_rate")
        if isinstance(success_rate, bool) or success_rate != 1:
            raise _fail(f"{baseline_path}.success_rate", "must equal one")
        if baseline.get("memory_is_estimate") is not True:
            raise _fail(f"{baseline_path}.memory_is_estimate", "must be true")
        if baseline.get("measurement_mode") != (
            "cold start; any table is rebuilt for every target"
        ):
            raise _fail(
                f"{baseline_path}.measurement_mode", "measurement mode drifted"
            )
        if baseline.get("precomputation_reusable_for_same_curve_generator") is not (
            legacy_method == "bsgs"
        ):
            raise _fail(
                f"{baseline_path}.precomputation_reusable_for_same_curve_generator",
                "reuse declaration drifted",
            )

        runs = _array(baseline.get("runs"), f"{baseline_path}.runs", length=8)
        run_memories: list[int] = []
        for run_index, raw_run in enumerate(runs):
            run_path = f"{baseline_path}.runs[{run_index}]"
            run = _object(raw_run, run_path)
            sample_ordinal = _integer(
                run.get("sample_ordinal"), f"{run_path}.sample_ordinal"
            )
            if sample_ordinal != run_index:
                raise _fail(f"{run_path}.sample_ordinal", "run order drifted")
            record_index = _integer(run.get("record_index"), f"{run_path}.record_index")
            curve_index = _integer(run.get("curve_index"), f"{run_path}.curve_index")
            generator_index = _integer(
                run.get("generator_index"), f"{run_path}.generator_index"
            )
            if curve_index not in (7, 8, 9) or generator_index not in (4, 5):
                raise _fail(
                    run_path,
                    "replay row left the frozen blind curve/generator set",
                )
            expected_scalar = _integer(
                run.get("expected_scalar"), f"{run_path}.expected_scalar", minimum=1
            )
            candidate_scalar = _integer(
                run.get("candidate_scalar"), f"{run_path}.candidate_scalar", minimum=0
            )
            if candidate_scalar != expected_scalar:
                raise _fail(
                    f"{run_path}.candidate_scalar",
                    "legacy solver did not reproduce the target scalar",
                )
            operations = _integer(
                run.get("group_operations"), f"{run_path}.group_operations"
            )
            memory_bytes = _integer(
                run.get("memory_bytes"), f"{run_path}.memory_bytes"
            )
            run_memories.append(memory_bytes)

            try:
                legacy_curve = catalog.curve_by_key(field_bits, curve_index)
                legacy_generator = legacy_curve.generators[generator_index]
                if legacy_generator.generator_index != generator_index:
                    raise KeyError("generator order drifted")
                if legacy_generator.role != "blind":
                    raise KeyError("generator role is not blind")
                fixture = resolve_legacy_generator(
                    field_bits,
                    curve_index,
                    generator_index,
                    catalog=catalog,
                )
            except (IndexError, KeyError, ValueError) as error:
                raise _fail(
                    run_path, f"cannot resolve legacy generator: {error}"
                ) from error
            if expected_scalar >= fixture.subgroup_order:
                raise _fail(
                    f"{run_path}.expected_scalar",
                    "is outside the subgroup range",
                )
            if fixture.cofactor != 1:
                raise _fail(run_path, "legacy replay requires cofactor one")

            try:
                curve = oracle.Curve(fixture.field_p, fixture.curve_a, fixture.curve_b)
                if not oracle.is_prime(fixture.subgroup_order):
                    raise ValueError("subgroup order is not prime")
                if not curve.is_on_curve(fixture.generator):
                    raise ValueError("generator is off curve")
                if (
                    curve.scalar_mul(fixture.subgroup_order, fixture.generator)
                    is not None
                ):
                    raise ValueError("generator order certificate failed")
                target = curve.scalar_mul(expected_scalar, fixture.generator)
                if target is None or not curve.is_on_curve(target):
                    raise ValueError("derived target is not affine and on curve")
            except (TypeError, ValueError) as error:
                raise _fail(
                    run_path, f"independent target derivation failed: {error}"
                ) from error

            offline: int | None = None
            online: int | None = None
            table_entries: int | None = None
            if legacy_method == "bsgs":
                table_entries = _ceil_sqrt(fixture.subgroup_order)
                offline = (
                    table_entries
                    + table_entries.bit_length()
                    + table_entries.bit_count()
                )
                online = operations - offline
                if online < 0:
                    raise _fail(
                        run_path,
                        "legacy BSGS operation decomposition is negative",
                    )
                if memory_bytes != table_entries * 64:
                    raise _fail(run_path, "legacy BSGS memory estimate drifted")
            elif memory_bytes != 1024:
                raise _fail(run_path, "legacy rho memory estimate must equal 1024")

            case_id = (
                f"legacy-p1-b{field_bits}-{legacy_method}-s{sample_ordinal}"
            )
            seed = (
                field_bits * 1000 + sample_ordinal
                if legacy_method == "pollard_rho"
                else 0
            )
            public_input = PublicReplayInput(
                method_id=_METHOD_IDS[legacy_method],
                curve_catalog_sha256=fixture.catalog_sha256,
                curve_fixture_id=fixture.fixture_id,
                curve_id=fixture.curve_id,
                field_bits=fixture.field_bits,
                subgroup_order_bits=fixture.subgroup_order_bits,
                p=fixture.field_p,
                a=fixture.curve_a,
                b=fixture.curve_b,
                G=fixture.generator,
                Q=target,
                ell=fixture.subgroup_order,
                seed=seed,
            )
            cases.append(
                LegacyReplayCase(
                    case_id=case_id,
                    legacy_method=legacy_method,
                    derived_from=DerivedFrom(
                        source_path=runner["path"],
                        source_function=_SOURCE_FUNCTIONS[legacy_method],
                        source_sha256=runner["sha256"],
                    ),
                    validator_only=ValidatorReplayExpectation(
                        sample_ordinal=sample_ordinal,
                        record_index=record_index,
                        curve_index=curve_index,
                        generator_index=generator_index,
                        expected_scalar=expected_scalar,
                        legacy_candidate_scalar=candidate_scalar,
                        legacy_group_operations=operations,
                        legacy_memory_bytes=memory_bytes,
                        bsgs_offline_setup_group_law_invocations=offline,
                        bsgs_online_target_group_law_invocations=online,
                        bsgs_table_entries=table_entries,
                    ),
                    _public_input=public_input,
                )
            )
        if baseline.get("peak_memory_bytes") != max(run_memories):
            raise _fail(
                f"{baseline_path}.peak_memory_bytes",
                "does not match retained runs",
            )

    if tuple(observed_baselines) != _EXPECTED_BASELINES:
        raise _fail("$.assay.solver_baselines", "baseline Cartesian order drifted")
    return tuple(cases)


def _verify_golden(
    locator: dict[str, Any], cases: tuple[LegacyReplayCase, ...]
) -> LegacyReplayReport:
    golden = _object(locator.get("golden"), "$.golden")
    identity_rows = [
        {
            "case_id": case.case_id,
            "record_index": case.validator_only.record_index,
            "curve_index": case.validator_only.curve_index,
            "generator_index": case.validator_only.generator_index,
        }
        for case in cases
    ]
    operations = [case.validator_only.legacy_group_operations for case in cases]
    identity_sha256 = sha256_json(identity_rows)
    operations_sha256 = sha256_json(operations)
    if len(cases) != golden.get("case_count"):
        raise _fail("$.golden.case_count", "does not match projected replay")
    if identity_sha256 != golden.get("case_identity_sha256"):
        raise _fail("$.golden.case_identity_sha256", "replay identities drifted")
    if operations_sha256 != golden.get("legacy_group_operations_vector_sha256"):
        raise _fail(
            "$.golden.legacy_group_operations_vector_sha256",
            "operation vector drifted",
        )
    if sorted(
        {case.to_public_input().field_bits for case in cases}
    ) != golden.get("field_bits"):
        raise _fail("$.golden.field_bits", "field ladder drifted")

    bsgs_cases = tuple(case for case in cases if case.legacy_method == "bsgs")
    rho_cases = tuple(case for case in cases if case.legacy_method == "pollard_rho")
    success_count = sum(
        case.validator_only.legacy_candidate_scalar
        == case.validator_only.expected_scalar
        for case in cases
    )
    if success_count != golden.get("success_count"):
        raise _fail("$.golden.success_count", "legacy success count drifted")

    bsgs_expected = _object(golden.get("bsgs"), "$.golden.bsgs")
    bsgs_observed = {
        "case_count": len(bsgs_cases),
        "legacy_group_operations": sum(
            case.validator_only.legacy_group_operations for case in bsgs_cases
        ),
        "offline_setup_group_law_invocations": sum(
            case.validator_only.bsgs_offline_setup_group_law_invocations or 0
            for case in bsgs_cases
        ),
        "online_target_group_law_invocations": sum(
            case.validator_only.bsgs_online_target_group_law_invocations or 0
            for case in bsgs_cases
        ),
        "table_entries": sum(
            case.validator_only.bsgs_table_entries or 0 for case in bsgs_cases
        ),
        "estimated_algorithmic_table_bytes": sum(
            case.validator_only.legacy_memory_bytes for case in bsgs_cases
        ),
    }
    if bsgs_observed != bsgs_expected:
        raise _fail("$.golden.bsgs", "BSGS aggregate anchors drifted")

    rho_expected = _object(
        golden.get("ordinary_rho_xmod3"), "$.golden.ordinary_rho_xmod3"
    )
    if len(rho_cases) != rho_expected.get("case_count"):
        raise _fail("$.golden.ordinary_rho_xmod3.case_count", "rho count drifted")
    rho_operations = sum(
        case.validator_only.legacy_group_operations for case in rho_cases
    )
    if rho_operations != rho_expected.get("legacy_group_operations"):
        raise _fail(
            "$.golden.ordinary_rho_xmod3.legacy_group_operations",
            "rho operation aggregate drifted",
        )

    return LegacyReplayReport(
        passed=True,
        issues=(),
        fixture_kind=locator["fixture_kind"],
        locator_raw_sha256=LOCATOR_RAW_SHA256,
        locator_semantic_sha256=LOCATOR_SEMANTIC_SHA256,
        case_count=len(cases),
        success_count=success_count,
        bsgs_case_count=len(bsgs_cases),
        rho_case_count=len(rho_cases),
        case_identity_sha256=identity_sha256,
        legacy_group_operations_vector_sha256=operations_sha256,
        bsgs_legacy_group_operations=bsgs_observed["legacy_group_operations"],
        bsgs_offline_setup_group_law_invocations=bsgs_observed[
            "offline_setup_group_law_invocations"
        ],
        bsgs_online_target_group_law_invocations=bsgs_observed[
            "online_target_group_law_invocations"
        ],
        bsgs_table_entries=bsgs_observed["table_entries"],
        bsgs_estimated_algorithmic_table_bytes=bsgs_observed[
            "estimated_algorithmic_table_bytes"
        ],
        rho_legacy_group_operations=rho_operations,
        expected_rho_floyd_iterations=_integer(
            rho_expected.get("floyd_iterations"),
            "$.golden.ordinary_rho_xmod3.floyd_iterations",
        ),
        expected_rho_restarts=_integer(
            rho_expected.get("restarts"),
            "$.golden.ordinary_rho_xmod3.restarts",
        ),
        expected_rho_collisions=_integer(
            rho_expected.get("collisions"),
            "$.golden.ordinary_rho_xmod3.collisions",
        ),
        expected_rho_noninvertible_collisions=_integer(
            rho_expected.get("noninvertible_collisions"),
            "$.golden.ordinary_rho_xmod3.noninvertible_collisions",
        ),
        expected_rho_invalid_candidate_collisions=_integer(
            rho_expected.get("invalid_candidate_collisions"),
            "$.golden.ordinary_rho_xmod3.invalid_candidate_collisions",
        ),
        schema_only_quarantine_verified=True,
    )


def _load_and_validate(
    *, repo_root: Path | str
) -> tuple[tuple[LegacyReplayCase, ...], LegacyReplayReport]:
    root = Path(repo_root)
    locator = _load_locator(root)
    _verify_quarantine(root, locator)
    sources = _object(locator["sources"], "$.sources")
    catalog = _catalog_from_locator(root, sources)
    cases = _build_cases(root, locator, catalog)
    report = _verify_golden(locator, cases)
    return cases, report


def load_legacy_replay(
    *, repo_root: Path | str = REPO_ROOT
) -> tuple[LegacyReplayCase, ...]:
    """Load all 64 authenticated cases without exposing them to a method."""

    cases, _ = _load_and_validate(repo_root=repo_root)
    return cases


def validate_legacy_replay(
    *, repo_root: Path | str = REPO_ROOT
) -> LegacyReplayReport:
    """Fail closed on any drift and return the verified replay summary."""

    _, report = _load_and_validate(repo_root=repo_root)
    return report


__all__ = [
    "LOCATOR_PATH",
    "LOCATOR_RAW_SHA256",
    "LOCATOR_SEMANTIC_SHA256",
    "DerivedFrom",
    "LegacyReplayCase",
    "LegacyReplayError",
    "LegacyReplayReport",
    "PublicReplayInput",
    "ValidatorReplayExpectation",
    "load_legacy_replay",
    "validate_legacy_replay",
]
