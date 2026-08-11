"""Read-only adapter for the frozen 40-curve legacy P1 catalog."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from experiments.ecdlp_lab.core.canonical import sha256_bytes
from experiments.ecdlp_lab.core.paths import resolve_artifact_path

from .model import Point, ResolvedCurveFixture

REPO_ROOT = Path(__file__).resolve().parents[3]
LEGACY_CATALOG_PATH = (
    "experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json"
)
LEGACY_CATALOG_SHA256 = (
    "d293afa7e5b614f39ed00356e35ee81a400b57ee9656907170193cb3aca0bbd7"
)
LEGACY_PAYLOAD_SHA256 = (
    "e3aa11fa48357b9c1fdc5f0dbeb07108a34838ffbad1b734021627a3ef620c84"
)
MAX_LEGACY_CATALOG_BYTES = 1024 * 1024


class LegacyCatalogError(ValueError):
    """Raised when the frozen legacy authority cannot be loaded exactly."""


@dataclass(frozen=True)
class LegacyGenerator:
    generator_index: int
    generator_id: str
    role: str
    base_multiplier: int
    point: Point


@dataclass(frozen=True)
class LegacyCurve:
    curve_id: str
    field_bits: int
    field_p: int
    curve_a: int
    curve_b: int
    full_order: int
    cofactor: int
    curve_index: int
    base_point: Point
    beta: int
    lambda_value: int
    generators: tuple[LegacyGenerator, ...]


@dataclass(frozen=True)
class LegacyCatalog:
    raw_sha256: str
    payload_sha256: str
    curves: tuple[LegacyCurve, ...]

    def curve_by_key(self, field_bits: int, curve_index: int) -> LegacyCurve:
        matches = tuple(
            curve
            for curve in self.curves
            if curve.field_bits == field_bits and curve.curve_index == curve_index
        )
        if len(matches) != 1:
            raise KeyError(f"unknown legacy curve key ({field_bits}, {curve_index})")
        return matches[0]

    def curve_by_id(self, curve_id: str) -> LegacyCurve:
        matches = tuple(curve for curve in self.curves if curve.curve_id == curve_id)
        if len(matches) != 1:
            raise KeyError(f"unknown legacy curve id {curve_id!r}")
        return matches[0]


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise LegacyCatalogError(f"duplicate legacy JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise LegacyCatalogError(f"non-finite legacy JSON number: {token}")


def _safe_legacy_json(payload: bytes) -> Any:
    """Parse known bytes while allowing observational finite JSON decimals.

    The legacy catalog predates the lab's integer-only semantic domain and has
    one wall-time float.  It is authenticated before this parser runs, and the
    adapter projects no float into a lab fixture.
    """

    try:
        text = payload.decode("utf-8", errors="strict")
        return json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_float=Decimal,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise LegacyCatalogError(f"invalid legacy catalog JSON: {error}") from error


def _integer(value: Any, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise LegacyCatalogError(f"{name} must be an integer >= {minimum}")
    return value


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise LegacyCatalogError(f"{name} must be a non-empty string")
    return value


def _point(value: Any, name: str) -> Point:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(isinstance(item, bool) or not isinstance(item, int) for item in value)
    ):
        raise LegacyCatalogError(f"{name} must be a two-integer array")
    return int(value[0]), int(value[1])


def _project_curve(value: Any) -> LegacyCurve:
    if not isinstance(value, dict):
        raise LegacyCatalogError("legacy curve entry must be an object")
    glv = value.get("glv")
    generators = value.get("generators")
    if not isinstance(glv, dict) or not isinstance(generators, list):
        raise LegacyCatalogError("legacy curve lacks GLV or generator data")
    projected_generators: list[LegacyGenerator] = []
    for expected_index, generator in enumerate(generators):
        if not isinstance(generator, dict):
            raise LegacyCatalogError("legacy generator must be an object")
        index = _integer(generator.get("generator_index"), "generator_index")
        if index != expected_index:
            raise LegacyCatalogError("legacy generator order is not canonical")
        projected_generators.append(
            LegacyGenerator(
                generator_index=index,
                generator_id=_string(generator.get("id"), "generator.id"),
                role=_string(generator.get("role"), "generator.role"),
                base_multiplier=_integer(
                    generator.get("base_multiplier"), "generator.base_multiplier", minimum=1
                ),
                point=_point(generator.get("point"), "generator.point"),
            )
        )
    if len(projected_generators) != 6:
        raise LegacyCatalogError("legacy curve must retain exactly six generators")
    return LegacyCurve(
        curve_id=_string(value.get("id"), "curve.id"),
        field_bits=_integer(value.get("field_bits"), "field_bits", minimum=3),
        field_p=_integer(value.get("field_p"), "field_p", minimum=5),
        curve_a=_integer(value.get("curve_a"), "curve_a"),
        curve_b=_integer(value.get("curve_b"), "curve_b"),
        full_order=_integer(value.get("group_order"), "group_order", minimum=2),
        cofactor=_integer(value.get("cofactor"), "cofactor", minimum=1),
        curve_index=_integer(value.get("curve_index"), "curve_index"),
        base_point=_point(value.get("base_point"), "base_point"),
        beta=_integer(glv.get("beta"), "glv.beta", minimum=1),
        lambda_value=_integer(glv.get("lambda"), "glv.lambda", minimum=1),
        generators=tuple(projected_generators),
    )


def load_legacy_catalog(
    *,
    catalog_path: str,
    catalog_sha256: str,
    repo_root: Path | str = REPO_ROOT,
) -> LegacyCatalog:
    """Authenticate and project a registry-authorized legacy P1 catalog.

    The caller must supply the path and raw digest obtained from the repository
    catalog registry.  Constants in this module are regression locators only;
    they do not independently authorize input bytes.
    """

    root = Path(repo_root)
    if not isinstance(catalog_path, str) or not catalog_path:
        raise LegacyCatalogError("registry catalog path must be a non-empty string")
    if (
        not isinstance(catalog_sha256, str)
        or len(catalog_sha256) != 64
        or any(character not in "0123456789abcdef" for character in catalog_sha256)
    ):
        raise LegacyCatalogError("registry catalog digest must be lowercase SHA-256")
    catalog_file = resolve_artifact_path(root, catalog_path, must_exist=True)
    try:
        size = catalog_file.stat().st_size
        if size > MAX_LEGACY_CATALOG_BYTES:
            raise LegacyCatalogError("legacy catalog exceeds its input-size bound")
        raw = catalog_file.read_bytes()
    except OSError as error:
        raise LegacyCatalogError(f"cannot read legacy catalog: {error}") from error
    raw_sha256 = sha256_bytes(raw)
    if raw_sha256 != catalog_sha256:
        raise LegacyCatalogError("registry-authorized legacy catalog digest mismatch")
    document = _safe_legacy_json(raw)
    if not isinstance(document, dict):
        raise LegacyCatalogError("legacy catalog root must be an object")
    if document.get("schema_version") != 1:
        raise LegacyCatalogError("legacy catalog schema version drifted")
    if document.get("catalog_sha256") != LEGACY_PAYLOAD_SHA256:
        raise LegacyCatalogError("legacy catalog payload digest declaration drifted")
    if document.get("field_bits") != [13, 16, 20, 24]:
        raise LegacyCatalogError("legacy field ladder drifted")
    curves = document.get("curves")
    if not isinstance(curves, list) or len(curves) != 40:
        raise LegacyCatalogError("legacy catalog must contain exactly 40 curves")
    projected = tuple(_project_curve(curve) for curve in curves)
    if document.get("curve_count") != len(projected):
        raise LegacyCatalogError("legacy curve count declaration mismatch")
    keys = [(curve.field_bits, curve.curve_index) for curve in projected]
    if len(set(keys)) != 40 or keys != sorted(keys):
        raise LegacyCatalogError("legacy curve keys are not unique and sorted")
    return LegacyCatalog(
        raw_sha256=raw_sha256,
        payload_sha256=LEGACY_PAYLOAD_SHA256,
        curves=projected,
    )


def resolve_legacy_generator(
    field_bits: int,
    curve_index: int,
    generator_index: int,
    *,
    catalog: LegacyCatalog,
) -> ResolvedCurveFixture:
    """Resolve the exact generator locator used by retained P1 solver rows."""

    if not isinstance(catalog, LegacyCatalog):
        raise TypeError("catalog must be a registry-authenticated LegacyCatalog")
    curve = catalog.curve_by_key(field_bits, curve_index)
    if isinstance(generator_index, bool) or not isinstance(generator_index, int):
        raise KeyError("generator index must be an integer")
    matches = tuple(
        generator
        for generator in curve.generators
        if generator.generator_index == generator_index
    )
    if len(matches) != 1:
        raise KeyError(
            f"unknown legacy generator key ({field_bits}, {curve_index}, {generator_index})"
        )
    generator = matches[0]
    return ResolvedCurveFixture(
        catalog_sha256=catalog.raw_sha256,
        source_kind="read_only_legacy_catalog",
        fixture_id=generator.generator_id,
        curve_id=curve.curve_id,
        family="j0_glv_like",
        field_bits=curve.field_bits,
        field_p=curve.field_p,
        curve_a=curve.curve_a,
        curve_b=curve.curve_b,
        full_order=curve.full_order,
        subgroup_order=curve.full_order,
        subgroup_order_bits=curve.full_order.bit_length(),
        cofactor=curve.cofactor,
        generator=generator.point,
        beta=curve.beta,
        lambda_value=curve.lambda_value,
        order_certificate_type="prime_order_hasse_unique_v1",
    )


def resolve_legacy_base_point(
    curve_id: str,
    *,
    catalog: LegacyCatalog,
) -> ResolvedCurveFixture:
    """Resolve a legacy base point for compatibility with the P01 fixture."""

    if not isinstance(catalog, LegacyCatalog):
        raise TypeError("catalog must be a registry-authenticated LegacyCatalog")
    curve = catalog.curve_by_id(curve_id)
    return ResolvedCurveFixture(
        catalog_sha256=catalog.raw_sha256,
        source_kind="read_only_legacy_catalog",
        fixture_id=curve.curve_id,
        curve_id=curve.curve_id,
        family="j0_glv_like",
        field_bits=curve.field_bits,
        field_p=curve.field_p,
        curve_a=curve.curve_a,
        curve_b=curve.curve_b,
        full_order=curve.full_order,
        subgroup_order=curve.full_order,
        subgroup_order_bits=curve.full_order.bit_length(),
        cofactor=curve.cofactor,
        generator=curve.base_point,
        beta=curve.beta,
        lambda_value=curve.lambda_value,
        order_certificate_type="prime_order_hasse_unique_v1",
    )


__all__ = [
    "LEGACY_CATALOG_PATH",
    "LEGACY_CATALOG_SHA256",
    "LegacyCatalog",
    "LegacyCatalogError",
    "LegacyCurve",
    "LegacyGenerator",
    "load_legacy_catalog",
    "resolve_legacy_base_point",
    "resolve_legacy_generator",
]
