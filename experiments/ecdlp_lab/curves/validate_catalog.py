"""Producer-independent validation for P02 curve catalogs.

The decisive elliptic-curve operations in this module come exclusively from
``experiments.framework.ec_oracle``.  In particular, this module must never
import the P1 producer arithmetic or the P02 catalog generator.

The committed CI catalog uses exact point counts only at 11 and 13 field bits.
The frozen legacy P1 catalog is intentionally validated by its prime-order
Hasse uniqueness certificates and GLV relations; exact counting its 24-bit
entries would violate the bounded offline-validation contract.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import gcd, isfinite, isqrt
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence

from experiments.ecdlp_lab.core.canonical import (
    StrictJSONError,
    is_sha256,
    sha256_bytes,
    strict_loads,
)
from experiments.ecdlp_lab.core.issues import Issue
from experiments.framework.ec_oracle import (
    MAX_TOY_FIELD,
    Curve as OracleCurve,
    is_prime,
    prime_divisors,
)


CI_CATALOG_KIND = "ecdlp_lab_ci_curve_catalog_v1"
CI_FIELD_BITS = (11, 13)
FAMILIES = (
    "j0_glv_like",
    "random_generic_j_prime_subgroup",
    "j0_no_fp_glv_control",
)
REQUIRED_LIMITS = MappingProxyType(
    {
        "max_prime_candidates": 4096,
        "max_curve_candidates": 4096,
        "max_point_attempts": 1024,
    }
)
MAX_CATALOG_BYTES = 1024 * 1024
MAX_EXACT_FIELD_BITS = 16

_CATALOG_KEYS = frozenset(
    {
        "schema_version",
        "catalog_kind",
        "classification",
        "native_research_outcome",
        "spec_sha256",
        "curve_count",
        "field_bits",
        "families",
        "limits",
        "fixtures",
    }
)
_FIXTURE_KEYS = frozenset(
    {
        "fixture_id",
        "curve_id",
        "family",
        "field_bits",
        "field_p",
        "curve_a",
        "curve_b",
        "j_invariant",
        "full_order",
        "subgroup_order",
        "subgroup_order_bits",
        "cofactor",
        "generator",
        "endomorphism",
        "family_property",
        "order_certificate",
        "generation_search",
    }
)
_FORBIDDEN_OBSERVATION_KEYS = frozenset(
    {
        "wall_time",
        "wall_time_seconds",
        "duration",
        "duration_seconds",
        "platform",
        "python",
        "python_version",
        "source_commit",
        "current_commit",
        "source_worktree_dirty",
        "dirty",
        "dirty_tree",
    }
)


@dataclass(frozen=True)
class FixtureValidation:
    """Stable result for one independently checked curve fixture."""

    fixture_id: str
    family: str
    certificate_type: str
    recomputed_full_order: int | None
    issues: tuple[Issue, ...]

    @property
    def passed(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "family": self.family,
            "certificate_type": self.certificate_type,
            "recomputed_full_order": self.recomputed_full_order,
            "passed": self.passed,
            "issues": [
                {"code": issue.code, "path": issue.path, "message": issue.message}
                for issue in self.issues
            ],
        }


@dataclass(frozen=True)
class CatalogValidation:
    """Stable, timing-free validation result for one catalog artifact."""

    catalog_sha256: str
    spec_sha256: str | None
    fixture_results: tuple[FixtureValidation, ...]
    issues: tuple[Issue, ...]
    declared_fixture_count: int | None = None

    @property
    def fixture_count(self) -> int:
        return len(self.fixture_results)

    @property
    def passed(self) -> bool:
        return not self.issues and all(row.passed for row in self.fixture_results)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "report_kind": "ecdlp_lab_curve_catalog_validation_v1",
            "catalog_sha256": self.catalog_sha256,
            "spec_sha256": self.spec_sha256,
            "fixture_count": self.fixture_count,
            "passed": self.passed,
            "issues": [
                {"code": issue.code, "path": issue.path, "message": issue.message}
                for issue in self.issues
            ],
            "fixtures": [row.to_dict() for row in self.fixture_results],
        }


@dataclass(frozen=True)
class _CommonCurve:
    p: int
    a: int
    b: int
    full_order: int
    subgroup_order: int
    cofactor: int
    generator: tuple[int, int]
    curve: OracleCurve
    hasse_lower: int
    hasse_upper: int
    j_invariant: int


def _problem(code: str, path: str, message: str) -> Issue:
    return Issue(f"curve.{code}", path, message)


def _dedupe(issues: Sequence[Issue]) -> tuple[Issue, ...]:
    return tuple(sorted(set(issues)))


def _prefixed(issue: Issue, prefix: str) -> Issue:
    suffix = issue.path[1:] if issue.path.startswith("$") else f".{issue.path}"
    return Issue(issue.code, prefix + suffix, issue.message)


def _exact_keys(
    value: Any,
    expected: frozenset[str],
    *,
    path: str,
    code: str,
    issues: list[Issue],
) -> Mapping[str, Any] | None:
    if not isinstance(value, dict):
        issues.append(_problem(code, path, "must be an object"))
        return None
    actual = frozenset(value)
    if actual != expected:
        issues.append(
            _problem(
                code,
                path,
                "key set drifted "
                f"(missing={sorted(expected - actual)}, unknown={sorted(actual - expected)})",
            )
        )
    return value


def _integer(
    value: Any,
    *,
    path: str,
    code: str,
    issues: list[Issue],
    minimum: int | None = None,
    maximum: int | None = None,
) -> int | None:
    if type(value) is not int:
        issues.append(_problem(code, path, "must be an integer (booleans are forbidden)"))
        return None
    if minimum is not None and value < minimum:
        issues.append(_problem(code, path, f"must be at least {minimum}"))
        return None
    if maximum is not None and value > maximum:
        issues.append(_problem(code, path, f"must be at most {maximum}"))
        return None
    return value


def _walk_forbidden_observations(
    value: Any, *, path: str = "$"
) -> tuple[Issue, ...]:
    issues: list[Issue] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _FORBIDDEN_OBSERVATION_KEYS:
                issues.append(
                    _problem(
                        "catalog.observation",
                        child_path,
                        "timing, platform, commit, and dirty-tree observations are not semantic catalog fields",
                    )
                )
            issues.extend(_walk_forbidden_observations(child, path=child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            issues.extend(_walk_forbidden_observations(child, path=f"{path}[{index}]"))
    return _dedupe(issues)


def _common_preflight(fixture: Mapping[str, Any], issues: list[Issue]) -> _CommonCurve | None:
    p = _integer(
        fixture.get("field_p"),
        path="$.field_p",
        code="field_prime",
        issues=issues,
        minimum=5,
        maximum=MAX_TOY_FIELD,
    )
    field_bits = _integer(
        fixture.get("field_bits"),
        path="$.field_bits",
        code="field_bits",
        issues=issues,
        minimum=3,
        maximum=32,
    )
    if p is not None:
        if not is_prime(p):
            issues.append(_problem("field_prime", "$.field_p", "must be prime"))
        if field_bits is not None and field_bits != p.bit_length():
            issues.append(
                _problem("field_bits", "$.field_bits", "does not match field_p.bit_length()")
            )

    a = _integer(
        fixture.get("curve_a"),
        path="$.curve_a",
        code="coefficient",
        issues=issues,
        minimum=0,
    )
    b = _integer(
        fixture.get("curve_b"),
        path="$.curve_b",
        code="coefficient",
        issues=issues,
        minimum=0,
    )
    if p is not None:
        for name, value in (("curve_a", a), ("curve_b", b)):
            if value is not None and value >= p:
                issues.append(
                    _problem(
                        "coefficient.canonical",
                        f"$.{name}",
                        "coefficient must be a canonical field element",
                    )
                )

    full_order = _integer(
        fixture.get("full_order"),
        path="$.full_order",
        code="order",
        issues=issues,
        minimum=2,
        maximum=(1 << 33),
    )
    subgroup_order = _integer(
        fixture.get("subgroup_order"),
        path="$.subgroup_order",
        code="subgroup_prime",
        issues=issues,
        minimum=2,
        maximum=MAX_TOY_FIELD,
    )
    subgroup_bits = _integer(
        fixture.get("subgroup_order_bits"),
        path="$.subgroup_order_bits",
        code="subgroup_bits",
        issues=issues,
        minimum=2,
        maximum=32,
    )
    cofactor = _integer(
        fixture.get("cofactor"),
        path="$.cofactor",
        code="cofactor",
        issues=issues,
        minimum=1,
        maximum=MAX_TOY_FIELD,
    )
    if subgroup_order is not None:
        if not is_prime(subgroup_order):
            issues.append(
                _problem("subgroup_prime", "$.subgroup_order", "must be prime")
            )
        if subgroup_bits is not None and subgroup_bits != subgroup_order.bit_length():
            issues.append(
                _problem(
                    "subgroup_bits",
                    "$.subgroup_order_bits",
                    "does not match subgroup_order.bit_length()",
                )
            )
    if (
        full_order is not None
        and subgroup_order is not None
        and cofactor is not None
        and full_order != cofactor * subgroup_order
    ):
        issues.append(
            _problem(
                "order.product",
                "$.full_order",
                "must equal cofactor * subgroup_order",
            )
        )

    generator_raw = fixture.get("generator")
    generator: tuple[int, int] | None = None
    if (
        not isinstance(generator_raw, list)
        or len(generator_raw) != 2
        or any(type(coordinate) is not int for coordinate in generator_raw)
    ):
        issues.append(
            _problem(
                "generator.shape",
                "$.generator",
                "must be a two-integer array (booleans are forbidden)",
            )
        )
    else:
        generator = generator_raw[0], generator_raw[1]
        if p is not None and any(not 0 <= coordinate < p for coordinate in generator):
            issues.append(
                _problem(
                    "generator.canonical",
                    "$.generator",
                    "coordinates must be canonical field elements",
                )
            )

    if (
        p is None
        or not is_prime(p)
        or a is None
        or b is None
        or a >= p
        or b >= p
        or full_order is None
        or subgroup_order is None
        or cofactor is None
        or generator is None
    ):
        return None

    discriminant = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    if discriminant == 0:
        issues.append(_problem("nonsingular", "$", "curve must be nonsingular"))
        return None
    try:
        curve = OracleCurve(p, a, b)
    except ValueError as error:
        issues.append(_problem("nonsingular", "$", str(error)))
        return None

    if not curve.is_on_curve(generator):
        issues.append(
            _problem("generator.off_curve", "$.generator", "generator is not on the curve")
        )
    else:
        try:
            if curve.scalar_mul(subgroup_order, generator) is not None:
                issues.append(
                    _problem(
                        "generator.order",
                        "$.generator",
                        "prime subgroup order does not annihilate the nonzero generator",
                    )
                )
        except (TypeError, ValueError) as error:
            issues.append(_problem("generator.order", "$.generator", str(error)))

    hasse_radius = isqrt(4 * p)
    lower = p + 1 - hasse_radius
    upper = p + 1 + hasse_radius
    if not lower <= full_order <= upper:
        issues.append(
            _problem(
                "order.hasse",
                "$.full_order",
                "reported full order is outside the independently computed Hasse interval",
            )
        )

    computed_j = 1728 * 4 * pow(a, 3, p) * pow(discriminant, -1, p) % p
    reported_j = _integer(
        fixture.get("j_invariant"),
        path="$.j_invariant",
        code="j_invariant",
        issues=issues,
        minimum=0,
        maximum=p - 1,
    )
    if reported_j is not None and reported_j != computed_j:
        issues.append(
            _problem(
                "j_invariant",
                "$.j_invariant",
                "does not match the independently recomputed j-invariant",
            )
        )

    return _CommonCurve(
        p=p,
        a=a,
        b=b,
        full_order=full_order,
        subgroup_order=subgroup_order,
        cofactor=cofactor,
        generator=generator,
        curve=curve,
        hasse_lower=lower,
        hasse_upper=upper,
        j_invariant=computed_j,
    )


def _certificate_shape(
    fixture: Mapping[str, Any], issues: list[Issue]
) -> tuple[str, Mapping[str, Any]] | None:
    certificate = _exact_keys(
        fixture.get("order_certificate"),
        frozenset({"type", "inputs"}),
        path="$.order_certificate",
        code="certificate.shape",
        issues=issues,
    )
    if certificate is None:
        return None
    certificate_type = certificate.get("type")
    inputs = certificate.get("inputs")
    if not isinstance(certificate_type, str) or not certificate_type:
        issues.append(
            _problem("certificate.shape", "$.order_certificate.type", "must be a string")
        )
        return None
    if not isinstance(inputs, dict):
        issues.append(
            _problem("certificate.shape", "$.order_certificate.inputs", "must be an object")
        )
        return None
    return certificate_type, inputs


def _expect_inputs(
    actual: Mapping[str, Any], expected: Mapping[str, Any], issues: list[Issue]
) -> None:
    if dict(actual) != dict(expected):
        issues.append(
            _problem(
                "certificate.inputs",
                "$.order_certificate.inputs",
                "certificate inputs do not match independently derived values",
            )
        )


def _validate_hasse_unique(
    common: _CommonCurve,
    inputs: Mapping[str, Any],
    *,
    exact_count_authorized: bool,
    issues: list[Issue],
) -> int | None:
    del exact_count_authorized
    expected = {
        "field_p": common.p,
        "generator": list(common.generator),
        "subgroup_order": common.subgroup_order,
        "full_order": common.full_order,
        "cofactor": common.cofactor,
        "hasse_lower": common.hasse_lower,
        "hasse_upper": common.hasse_upper,
        "twice_subgroup_order": 2 * common.subgroup_order,
    }
    _expect_inputs(inputs, expected, issues)
    if common.full_order != common.subgroup_order or common.cofactor != 1:
        issues.append(
            _problem(
                "certificate.hasse_unique",
                "$.order_certificate",
                "prime-order uniqueness requires full_order=subgroup_order and cofactor=1",
            )
        )
    if not common.hasse_lower <= common.subgroup_order <= common.hasse_upper:
        issues.append(
            _problem(
                "certificate.hasse_unique",
                "$.subgroup_order",
                "subgroup order is outside the Hasse interval",
            )
        )
    if 2 * common.subgroup_order <= common.hasse_upper:
        issues.append(
            _problem(
                "certificate.hasse_unique",
                "$.subgroup_order",
                "2*subgroup_order must exceed the independent Hasse upper bound",
            )
        )
    return common.subgroup_order if not any(
        issue.code == "curve.certificate.hasse_unique" for issue in issues
    ) else None


def _exact_legendre_full_order(common: _CommonCurve) -> int:
    count = 1
    exponent = (common.p - 1) // 2
    for x in range(common.p):
        rhs = (pow(x, 3, common.p) + common.a * x + common.b) % common.p
        if rhs == 0:
            count += 1
        elif pow(rhs, exponent, common.p) == 1:
            count += 2
    return count


def _validate_exact_legendre(
    common: _CommonCurve,
    inputs: Mapping[str, Any],
    *,
    exact_count_authorized: bool,
    issues: list[Issue],
) -> int | None:
    expected = {
        "field_p": common.p,
        "curve_a": common.a,
        "curve_b": common.b,
        "x_start": 0,
        "x_stop_exclusive": common.p,
        "legendre_exponent": (common.p - 1) // 2,
        "expected_full_order": common.full_order,
    }
    _expect_inputs(inputs, expected, issues)
    if not exact_count_authorized:
        issues.append(
            _problem(
                "certificate.exact_unauthorized",
                "$.order_certificate",
                "exact Legendre counting requires a registry-authorized committed CI spec",
            )
        )
        return None
    if common.p.bit_length() > MAX_EXACT_FIELD_BITS:
        issues.append(
            _problem(
                "certificate.exact_oversize",
                "$.field_bits",
                "exact Legendre counting is restricted to at most 16 field bits",
            )
        )
        return None
    recomputed = _exact_legendre_full_order(common)
    if recomputed != common.full_order:
        issues.append(
            _problem(
                "certificate.exact_count",
                "$.full_order",
                f"exact point count is {recomputed}, not the reported value",
            )
        )
    return recomputed


def _validate_j0_p_plus_one(
    common: _CommonCurve,
    inputs: Mapping[str, Any],
    *,
    exact_count_authorized: bool,
    issues: list[Issue],
) -> int | None:
    expected = {
        "field_p": common.p,
        "curve_a": 0,
        "curve_b": 7,
        "field_p_mod_3": 2,
        "expected_full_order": common.p + 1,
    }
    _expect_inputs(inputs, expected, issues)
    if common.a != 0 or common.b != 7 or common.p % 3 != 2:
        issues.append(
            _problem(
                "certificate.j0_p_plus_one",
                "$.order_certificate",
                "requires a=0, b=7, and field_p mod 3 = 2",
            )
        )
    if common.full_order != common.p + 1:
        issues.append(
            _problem(
                "certificate.j0_p_plus_one",
                "$.full_order",
                "full order must equal field_p + 1",
            )
        )
    if not exact_count_authorized:
        issues.append(
            _problem(
                "certificate.exact_unauthorized",
                "$.order_certificate",
                "committed CI p+1 certificates require an independent exact count",
            )
        )
        return None
    if common.p.bit_length() > MAX_EXACT_FIELD_BITS:
        issues.append(
            _problem(
                "certificate.exact_oversize",
                "$.field_bits",
                "CI exact point counting is restricted to at most 16 field bits",
            )
        )
        return None
    recomputed = _exact_legendre_full_order(common)
    if recomputed != common.full_order:
        issues.append(
            _problem(
                "certificate.exact_count",
                "$.full_order",
                f"CI exact point count is {recomputed}, not the reported value",
            )
        )
    return recomputed


_CertificateValidator = Callable[..., int | None]
_CERTIFICATE_VALIDATORS: Mapping[str, _CertificateValidator] = MappingProxyType(
    {
        "prime_order_hasse_unique_v1": _validate_hasse_unique,
        "exact_legendre_sum_v1": _validate_exact_legendre,
        "j0_p_plus_one_v1": _validate_j0_p_plus_one,
    }
)


def _validate_family(
    fixture: Mapping[str, Any], common: _CommonCurve, issues: list[Issue]
) -> None:
    family = fixture.get("family")
    endomorphism = fixture.get("endomorphism")
    family_property = fixture.get("family_property")
    if not isinstance(endomorphism, dict):
        issues.append(_problem("family.shape", "$.endomorphism", "must be an object"))
        return
    if not isinstance(family_property, dict):
        issues.append(
            _problem("family.shape", "$.family_property", "must be an object")
        )
        return

    if family == "j0_glv_like":
        expected_property = {
            "kind": "j0_glv_like_v1",
            "equation_shape": "y^2=x^3+7",
            "j_invariant": 0,
            "field_p_mod_3": 1,
        }
        if common.a != 0 or common.b != 7 or common.j_invariant != 0 or common.p % 3 != 1:
            issues.append(
                _problem(
                    "family.glv",
                    "$",
                    "j0_glv_like requires y^2=x^3+7, j=0, and field_p mod 3 = 1",
                )
            )
        if family_property != expected_property:
            issues.append(
                _problem("family.glv", "$.family_property", "GLV family claim drifted")
            )
        if frozenset(endomorphism) != frozenset({"status", "beta", "lambda", "reason"}):
            issues.append(
                _problem("family.glv", "$.endomorphism", "endomorphism shape drifted")
            )
            return
        beta = endomorphism.get("beta")
        eigenvalue = endomorphism.get("lambda")
        if (
            endomorphism.get("status") != "verified_j0_glv"
            or endomorphism.get("reason") is not None
            or type(beta) is not int
            or type(eigenvalue) is not int
            or not 0 <= beta < common.p
            or not 0 <= eigenvalue < common.subgroup_order
            or beta == 1
            or eigenvalue == 1
        ):
            issues.append(
                _problem(
                    "family.glv",
                    "$.endomorphism",
                    "requires canonical nontrivial beta/lambda and verified status",
                )
            )
            return
        if (beta * beta + beta + 1) % common.p != 0:
            issues.append(
                _problem("family.glv", "$.endomorphism.beta", "beta polynomial failed")
            )
        if (eigenvalue * eigenvalue + eigenvalue + 1) % common.subgroup_order != 0:
            issues.append(
                _problem(
                    "family.glv", "$.endomorphism.lambda", "lambda polynomial failed"
                )
            )
        if common.curve.is_on_curve(common.generator):
            image = (beta * common.generator[0] % common.p, common.generator[1])
            try:
                if (
                    not common.curve.is_on_curve(image)
                    or common.curve.scalar_mul(eigenvalue, common.generator) != image
                ):
                    issues.append(
                        _problem(
                            "family.glv",
                            "$.endomorphism",
                            "independent oracle rejected the GLV eigenpair relation",
                        )
                    )
            except (TypeError, ValueError) as error:
                issues.append(_problem("family.glv", "$.endomorphism", str(error)))

    elif family == "random_generic_j_prime_subgroup":
        expected_property = {
            "kind": "random_generic_j_prime_subgroup_v1",
            "j_invariant": common.j_invariant,
            "excluded_j_residues": [0, 1728 % common.p],
            "subgroup_selection": "largest_prime_factor",
        }
        expected_endomorphism = {
            "status": "not_claimed_generic_control",
            "beta": None,
            "lambda": None,
            "reason": "generic_j_control_has_no_claimed_j0_endomorphism",
        }
        if common.j_invariant in {0, 1728 % common.p}:
            issues.append(
                _problem(
                    "family.generic_j",
                    "$.j_invariant",
                    "generic control must have j outside {0, 1728}",
                )
            )
        if family_property != expected_property:
            issues.append(
                _problem(
                    "family.generic_j", "$.family_property", "generic-j family claim drifted"
                )
            )
        if endomorphism != expected_endomorphism:
            issues.append(
                _problem(
                    "family.generic_j",
                    "$.endomorphism",
                    "generic control must make no j=0 endomorphism claim",
                )
            )
        try:
            factors = prime_divisors(common.full_order)
        except ValueError as error:
            issues.append(_problem("family.generic_j", "$.full_order", str(error)))
        else:
            if not factors or common.subgroup_order != max(factors):
                issues.append(
                    _problem(
                        "family.generic_j",
                        "$.subgroup_order",
                        "must be the largest prime factor of the exact full order",
                    )
                )

    elif family == "j0_no_fp_glv_control":
        expected_property = {
            "kind": "j0_no_fp_glv_control_v1",
            "equation_shape": "y^2=x^3+7",
            "j_invariant": 0,
            "field_p_mod_3": 2,
            "cube_map_gcd": 1,
            "claim_scope": "base_field_only",
        }
        expected_endomorphism = {
            "status": "unavailable_no_base_field_cube_root",
            "beta": None,
            "lambda": None,
            "reason": "gcd(3,field_p-1)=1_no_nontrivial_base_field_cube_root",
        }
        if (
            common.a != 0
            or common.b != 7
            or common.j_invariant != 0
            or common.p % 3 != 2
            or gcd(3, common.p - 1) != 1
        ):
            issues.append(
                _problem(
                    "family.no_fp_glv",
                    "$",
                    "control requires j=0 and no nontrivial base-field cube root",
                )
            )
        if family_property != expected_property:
            issues.append(
                _problem(
                    "family.no_fp_glv",
                    "$.family_property",
                    "base-field-only family claim drifted",
                )
            )
        if endomorphism != expected_endomorphism:
            issues.append(
                _problem(
                    "family.no_fp_glv",
                    "$.endomorphism",
                    "beta/lambda must be null with the fixed base-field reason",
                )
            )
    else:
        issues.append(_problem("family.unknown", "$.family", "unknown curve family"))


def validate_fixture(
    fixture: Any, *, exact_count_authorized: bool = False
) -> FixtureValidation:
    """Independently validate one normalized P02 fixture.

    ``exact_count_authorized`` is an authority input, not a fact read from the
    fixture.  Normal callers should use :func:`validate_catalog_bytes`, which
    derives it only from a caller-supplied trusted spec digest.
    """

    issues: list[Issue] = []
    if type(exact_count_authorized) is not bool:
        issues.append(
            _problem(
                "certificate.exact_authority",
                "$",
                "exact_count_authorized must be a boolean authority input",
            )
        )
        exact_count_authorized = False
    fixture_id = fixture.get("fixture_id", "<invalid>") if isinstance(fixture, dict) else "<invalid>"
    family = fixture.get("family", "<invalid>") if isinstance(fixture, dict) else "<invalid>"
    certificate_type = "<invalid>"
    if not isinstance(fixture, dict):
        issues.append(_problem("fixture.type", "$", "fixture must be an object"))
        return FixtureValidation(
            str(fixture_id), str(family), certificate_type, None, _dedupe(issues)
        )
    if frozenset(fixture) != _FIXTURE_KEYS:
        issues.append(
            _problem(
                "fixture.shape",
                "$",
                "fixture key set drifted "
                f"(missing={sorted(_FIXTURE_KEYS - frozenset(fixture))}, "
                f"unknown={sorted(frozenset(fixture) - _FIXTURE_KEYS)})",
            )
        )
    if not isinstance(fixture_id, str) or not fixture_id:
        issues.append(_problem("fixture.id", "$.fixture_id", "must be a non-empty string"))
    if not isinstance(fixture.get("curve_id"), str) or not fixture.get("curve_id"):
        issues.append(_problem("fixture.id", "$.curve_id", "must be a non-empty string"))
    if not isinstance(family, str):
        issues.append(_problem("family.unknown", "$.family", "must be a string"))

    common = _common_preflight(fixture, issues)
    certificate = _certificate_shape(fixture, issues)
    recomputed: int | None = None
    if certificate is not None:
        certificate_type, inputs = certificate
        validator = _CERTIFICATE_VALIDATORS.get(certificate_type)
        if validator is None:
            issues.append(
                _problem(
                    "certificate.unknown",
                    "$.order_certificate.type",
                    "unknown certificate type",
                )
            )
        elif common is not None:
            recomputed = validator(
                common,
                inputs,
                exact_count_authorized=exact_count_authorized,
                issues=issues,
            )
    if common is not None:
        _validate_family(fixture, common, issues)
    return FixtureValidation(
        fixture_id if isinstance(fixture_id, str) else "<invalid>",
        family if isinstance(family, str) else "<invalid>",
        certificate_type,
        recomputed,
        _dedupe(issues),
    )


def _validate_generation_search(
    fixture: Mapping[str, Any], *, path: str, issues: list[Issue]
) -> None:
    search = fixture.get("generation_search")
    expected_keys = frozenset(
        {"prime_candidates_examined", "curve_candidates_examined", "point_attempts"}
    )
    if not isinstance(search, dict) or frozenset(search) != expected_keys:
        issues.append(
            _problem("catalog.search", f"{path}.generation_search", "search receipt shape drifted")
        )
        return
    bindings = {
        "prime_candidates_examined": "max_prime_candidates",
        "curve_candidates_examined": "max_curve_candidates",
        "point_attempts": "max_point_attempts",
    }
    for field_name, limit_name in bindings.items():
        value = search.get(field_name)
        if type(value) is not int or not 1 <= value <= REQUIRED_LIMITS[limit_name]:
            issues.append(
                _problem(
                    "catalog.search",
                    f"{path}.generation_search.{field_name}",
                    f"must be a positive integer no greater than {limit_name}",
                )
            )


def validate_catalog_bytes(
    raw_catalog: bytes,
    *,
    expected_spec_sha256: str | None = None,
    exact_count_authorized: bool = True,
) -> CatalogValidation:
    """Validate committed CI bytes against an externally trusted spec digest.

    Omitting ``expected_spec_sha256`` deliberately fails closed for the exact
    certificates in the CI catalog.  The registry integration is responsible
    for supplying the digest after independently authenticating the spec file.
    """

    if not isinstance(raw_catalog, bytes):
        raise TypeError("raw_catalog must be bytes")
    digest = sha256_bytes(raw_catalog)
    issues: list[Issue] = []
    if len(raw_catalog) > MAX_CATALOG_BYTES:
        issues.append(
            _problem("catalog.size", "$", f"catalog exceeds {MAX_CATALOG_BYTES} bytes")
        )
        return CatalogValidation(digest, None, (), _dedupe(issues))
    if expected_spec_sha256 is not None and not is_sha256(expected_spec_sha256):
        issues.append(
            _problem(
                "catalog.spec",
                "$.spec_sha256",
                "trusted spec digest must be lowercase SHA-256",
            )
        )
    try:
        document = strict_loads(raw_catalog, label="CI curve catalog")
    except (StrictJSONError, TypeError, RecursionError) as error:
        issues.append(_problem("catalog.json", "$", str(error)))
        return CatalogValidation(digest, None, (), _dedupe(issues))
    if not isinstance(document, dict):
        issues.append(_problem("catalog.type", "$", "catalog must be an object"))
        return CatalogValidation(digest, None, (), _dedupe(issues))
    issues.extend(_walk_forbidden_observations(document))
    _exact_keys(
        document,
        _CATALOG_KEYS,
        path="$",
        code="catalog.shape",
        issues=issues,
    )
    if document.get("schema_version") != 1:
        issues.append(_problem("catalog.identity", "$.schema_version", "must equal 1"))
    if document.get("catalog_kind") != CI_CATALOG_KIND:
        issues.append(
            _problem("catalog.identity", "$.catalog_kind", f"must equal {CI_CATALOG_KIND}")
        )
    if document.get("classification") != "engineering_only":
        issues.append(
            _problem("catalog.identity", "$.classification", "must equal engineering_only")
        )
    if document.get("native_research_outcome") is not False:
        issues.append(
            _problem(
                "catalog.identity", "$.native_research_outcome", "must be false"
            )
        )
    spec_sha256 = document.get("spec_sha256")
    if not is_sha256(spec_sha256):
        issues.append(_problem("catalog.spec", "$.spec_sha256", "must be lowercase SHA-256"))
        spec_sha256 = None
    if expected_spec_sha256 is None:
        issues.append(
            _problem(
                "catalog.spec_authority",
                "$.spec_sha256",
                "no externally trusted committed spec digest was supplied",
            )
        )
    elif spec_sha256 != expected_spec_sha256:
        issues.append(
            _problem(
                "catalog.spec",
                "$.spec_sha256",
                "catalog does not bind the externally trusted spec digest",
            )
        )
    if type(exact_count_authorized) is not bool:
        issues.append(
            _problem(
                "catalog.spec_authority",
                "$.spec_sha256",
                "exact_count_authorized must be a boolean authority input",
            )
        )
        exact_count_authorized = False
    exact_authorized = (
        exact_count_authorized
        and
        expected_spec_sha256 is not None
        and is_sha256(expected_spec_sha256)
        and spec_sha256 == expected_spec_sha256
    )

    if document.get("field_bits") != list(CI_FIELD_BITS):
        issues.append(
            _problem("catalog.coverage", "$.field_bits", "must be exactly [11, 13]")
        )
    if document.get("families") != list(FAMILIES):
        issues.append(
            _problem("catalog.coverage", "$.families", "family order drifted")
        )
    if document.get("limits") != dict(REQUIRED_LIMITS):
        issues.append(
            _problem("catalog.limits", "$.limits", "frozen search limits drifted")
        )
    curve_count = document.get("curve_count")
    if type(curve_count) is not int or curve_count != 6:
        issues.append(_problem("catalog.count", "$.curve_count", "must equal 6"))
        declared_count: int | None = None
    else:
        declared_count = curve_count
    fixtures = document.get("fixtures")
    if not isinstance(fixtures, list):
        issues.append(_problem("catalog.count", "$.fixtures", "must be an array"))
        return CatalogValidation(
            digest, spec_sha256, (), _dedupe(issues), declared_count
        )
    if len(fixtures) != 6:
        issues.append(_problem("catalog.count", "$.fixtures", "must contain six fixtures"))
        # The count is a CPU boundary, not merely a descriptive invariant.
        # Do not run primality, scalar multiplication, or exact counting over
        # an attacker-amplified array that happens to fit below the byte cap.
        return CatalogValidation(
            digest, spec_sha256, (), _dedupe(issues), declared_count
        )

    expected_pairs = [(bits, family) for bits in CI_FIELD_BITS for family in FAMILIES]
    observed_pairs: list[tuple[Any, Any]] = []
    fixture_ids: list[Any] = []
    curve_ids: list[Any] = []
    fixture_results: list[FixtureValidation] = []
    for index, fixture in enumerate(fixtures):
        path = f"$.fixtures[{index}]"
        if isinstance(fixture, dict):
            observed_pairs.append((fixture.get("field_bits"), fixture.get("family")))
            fixture_ids.append(fixture.get("fixture_id"))
            curve_ids.append(fixture.get("curve_id"))
            _validate_generation_search(fixture, path=path, issues=issues)
        result = validate_fixture(fixture, exact_count_authorized=exact_authorized)
        fixture_results.append(result)
        issues.extend(_prefixed(issue, path) for issue in result.issues)
    if observed_pairs != expected_pairs:
        issues.append(
            _problem(
                "catalog.coverage",
                "$.fixtures",
                "fixtures must be the complete ordered field_bits x family Cartesian product",
            )
        )
    if any(not isinstance(identifier, str) for identifier in fixture_ids):
        issues.append(
            _problem("catalog.duplicate", "$.fixtures", "fixture IDs must be strings")
        )
    elif len(fixture_ids) != len(set(fixture_ids)):
        issues.append(_problem("catalog.duplicate", "$.fixtures", "fixture IDs are not unique"))
    if any(not isinstance(identifier, str) for identifier in curve_ids):
        issues.append(
            _problem("catalog.duplicate", "$.fixtures", "curve IDs must be strings")
        )
    elif len(curve_ids) != len(set(curve_ids)):
        issues.append(_problem("catalog.duplicate", "$.fixtures", "curve IDs are not unique"))
    return CatalogValidation(
        digest,
        spec_sha256,
        tuple(fixture_results),
        _dedupe(issues),
        declared_count,
    )


def _legacy_fixture(curve: Any) -> dict[str, Any]:
    """Project one already authenticated LegacyCurve without producer imports."""

    p = curve.field_p
    subgroup_order = curve.full_order
    radius = isqrt(4 * p)
    generator = list(curve.base_point)
    return {
        "fixture_id": curve.curve_id,
        "curve_id": curve.curve_id,
        "family": "j0_glv_like",
        "field_bits": curve.field_bits,
        "field_p": p,
        "curve_a": curve.curve_a,
        "curve_b": curve.curve_b,
        "j_invariant": 0,
        "full_order": curve.full_order,
        "subgroup_order": subgroup_order,
        "subgroup_order_bits": subgroup_order.bit_length(),
        "cofactor": curve.cofactor,
        "generator": generator,
        "endomorphism": {
            "status": "verified_j0_glv",
            "beta": curve.beta,
            "lambda": curve.lambda_value,
            "reason": None,
        },
        "family_property": {
            "kind": "j0_glv_like_v1",
            "equation_shape": "y^2=x^3+7",
            "j_invariant": 0,
            "field_p_mod_3": 1,
        },
        "order_certificate": {
            "type": "prime_order_hasse_unique_v1",
            "inputs": {
                "field_p": p,
                "generator": generator,
                "subgroup_order": subgroup_order,
                "full_order": curve.full_order,
                "cofactor": curve.cofactor,
                "hasse_lower": p + 1 - radius,
                "hasse_upper": p + 1 + radius,
                "twice_subgroup_order": 2 * subgroup_order,
            },
        },
        # Legacy search receipts predate the three-counter P02 schema.  The
        # field is structurally required by the normalized fixture but is not
        # used as authority or validated by validate_fixture.
        "generation_search": {
            "prime_candidates_examined": 1,
            "curve_candidates_examined": 1,
            "point_attempts": 1,
        },
    }


@dataclass(frozen=True)
class _LegacyGeneratorView:
    generator_index: int
    generator_id: str
    base_multiplier: int
    point: tuple[int, int]


@dataclass(frozen=True)
class _LegacyCurveView:
    curve_id: str
    field_bits: int
    field_p: int
    curve_a: int
    curve_b: int
    full_order: int
    cofactor: int
    curve_index: int
    base_point: tuple[int, int]
    beta: int
    lambda_value: int
    generators: tuple[_LegacyGeneratorView, ...]


@dataclass(frozen=True)
class _LegacyCatalogView:
    raw_sha256: str
    curves: tuple[_LegacyCurveView, ...]


class _LegacyParseError(ValueError):
    pass


def _legacy_unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _LegacyParseError(f"duplicate legacy JSON key: {key}")
        result[key] = value
    return result


def _legacy_reject_constant(token: str) -> None:
    raise _LegacyParseError(f"non-finite legacy JSON number: {token}")


def _legacy_finite_float(token: str) -> float:
    value = float(token)
    if not isfinite(value):
        raise _LegacyParseError(f"non-finite legacy JSON number: {token}")
    return value


def _legacy_required_int(
    value: Any, name: str, minimum: int = 0, maximum: int | None = None
) -> int:
    if type(value) is not int or value < minimum:
        raise _LegacyParseError(f"{name} must be an integer >= {minimum}")
    if maximum is not None and value > maximum:
        raise _LegacyParseError(f"{name} must be an integer <= {maximum}")
    return value


def _legacy_required_point(value: Any, name: str) -> tuple[int, int]:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(type(coordinate) is not int for coordinate in value)
    ):
        raise _LegacyParseError(f"{name} must be a two-integer array")
    return value[0], value[1]


def _legacy_view(raw_catalog: bytes) -> tuple[_LegacyCatalogView, list[Issue]]:
    issues: list[Issue] = []
    digest = sha256_bytes(raw_catalog)
    try:
        text = raw_catalog.decode("utf-8", errors="strict")
        document = json.loads(
            text,
            object_pairs_hook=_legacy_unique_object,
            parse_float=_legacy_finite_float,
            parse_constant=_legacy_reject_constant,
        )
    except (UnicodeError, ValueError, RecursionError) as error:
        raise _LegacyParseError(f"invalid legacy catalog JSON: {error}") from error
    if not isinstance(document, dict):
        raise _LegacyParseError("legacy catalog root must be an object")
    if document.get("schema_version") != 1:
        issues.append(_problem("legacy.shape", "$.schema_version", "must equal 1"))
    if document.get("field_bits") != [13, 16, 20, 24]:
        issues.append(
            _problem("legacy.coverage", "$.field_bits", "legacy field ladder drifted")
        )
    curves_raw = document.get("curves")
    if not isinstance(curves_raw, list) or len(curves_raw) != 40:
        raise _LegacyParseError("legacy catalog must contain exactly 40 curve entries")
    if document.get("curve_count") != 40:
        issues.append(_problem("legacy.count", "$.curve_count", "must equal 40"))

    # The raw registry digest is the authority.  This secondary historical
    # digest check catches accidental changes to the P1 projection algorithm.
    declared_payload = document.get("catalog_sha256")
    without_payload = dict(document)
    without_payload.pop("catalog_sha256", None)
    try:
        legacy_canonical = json.dumps(
            without_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise _LegacyParseError(f"legacy payload cannot be hashed: {error}") from error
    if declared_payload != sha256_bytes(legacy_canonical):
        issues.append(
            _problem(
                "legacy.payload_digest",
                "$.catalog_sha256",
                "historical canonical payload digest mismatch",
            )
        )

    curves: list[_LegacyCurveView] = []
    for curve_index, raw_curve in enumerate(curves_raw):
        path = f"$.curves[{curve_index}]"
        try:
            if not isinstance(raw_curve, dict):
                raise _LegacyParseError("curve entry must be an object")
            glv = raw_curve.get("glv")
            raw_generators = raw_curve.get("generators")
            if not isinstance(glv, dict) or not isinstance(raw_generators, list):
                raise _LegacyParseError("curve lacks GLV or generator data")
            generators: list[_LegacyGeneratorView] = []
            for position, raw_generator in enumerate(raw_generators):
                if not isinstance(raw_generator, dict):
                    raise _LegacyParseError("generator must be an object")
                generator_id = raw_generator.get("id")
                if not isinstance(generator_id, str) or not generator_id:
                    raise _LegacyParseError("generator.id must be a non-empty string")
                generators.append(
                    _LegacyGeneratorView(
                        generator_index=_legacy_required_int(
                            raw_generator.get("generator_index"), "generator_index"
                        ),
                        generator_id=generator_id,
                        base_multiplier=_legacy_required_int(
                            raw_generator.get("base_multiplier"),
                            "base_multiplier",
                            1,
                        ),
                        point=_legacy_required_point(
                            raw_generator.get("point"), "generator.point"
                        ),
                    )
                )
                if generators[-1].generator_index != position:
                    issues.append(
                        _problem(
                            "legacy.generator",
                            f"{path}.generators[{position}].generator_index",
                            "generator index is not canonical",
                        )
                    )
            if len(generators) != 6:
                raise _LegacyParseError("curve must contain exactly six generators")
            curve_id = raw_curve.get("id")
            if not isinstance(curve_id, str) or not curve_id:
                raise _LegacyParseError("curve.id must be a non-empty string")
            curves.append(
                _LegacyCurveView(
                    curve_id=curve_id,
                    field_bits=_legacy_required_int(raw_curve.get("field_bits"), "field_bits", 3),
                    field_p=_legacy_required_int(
                        raw_curve.get("field_p"), "field_p", 5, MAX_TOY_FIELD
                    ),
                    curve_a=_legacy_required_int(
                        raw_curve.get("curve_a"), "curve_a", 0, MAX_TOY_FIELD
                    ),
                    curve_b=_legacy_required_int(
                        raw_curve.get("curve_b"), "curve_b", 0, MAX_TOY_FIELD
                    ),
                    full_order=_legacy_required_int(
                        raw_curve.get("group_order"), "group_order", 2, 1 << 33
                    ),
                    cofactor=_legacy_required_int(
                        raw_curve.get("cofactor"), "cofactor", 1, MAX_TOY_FIELD
                    ),
                    curve_index=_legacy_required_int(
                        raw_curve.get("curve_index"), "curve_index"
                    ),
                    base_point=_legacy_required_point(
                        raw_curve.get("base_point"), "base_point"
                    ),
                    beta=_legacy_required_int(glv.get("beta"), "glv.beta", 1),
                    lambda_value=_legacy_required_int(
                        glv.get("lambda"), "glv.lambda", 1
                    ),
                    generators=tuple(generators),
                )
            )
        except _LegacyParseError as error:
            issues.append(_problem("legacy.shape", path, str(error)))
    return _LegacyCatalogView(digest, tuple(curves)), issues


def validate_legacy_catalog_bytes(
    raw_catalog: bytes, *, expected_catalog_sha256: str
) -> CatalogValidation:
    """Authenticate, parse, and independently validate frozen P1 bytes.

    Legacy observational floats are accepted because they are part of the
    immutable P1 bytes, but they are never projected into a lab fixture.
    Duplicate keys and non-finite numbers are rejected.
    """

    if not isinstance(raw_catalog, bytes):
        raise TypeError("raw_catalog must be bytes")
    digest = sha256_bytes(raw_catalog)
    issues: list[Issue] = []
    if len(raw_catalog) > MAX_CATALOG_BYTES:
        issues.append(
            _problem("legacy.size", "$", f"legacy catalog exceeds {MAX_CATALOG_BYTES} bytes")
        )
        return CatalogValidation(digest, None, (), _dedupe(issues), 40)
    if not is_sha256(expected_catalog_sha256):
        issues.append(
            _problem(
                "legacy.authority", "$", "expected legacy digest must be lowercase SHA-256"
            )
        )
    if digest != expected_catalog_sha256:
        issues.append(
            _problem("legacy.digest", "$", "legacy bytes differ from registry authority")
        )
    try:
        view, parse_issues = _legacy_view(raw_catalog)
    except _LegacyParseError as error:
        issues.append(_problem("legacy.json", "$", str(error)))
        return CatalogValidation(digest, None, (), _dedupe(issues), 40)
    issues.extend(parse_issues)
    validated = validate_legacy_catalog(
        view, expected_catalog_sha256=expected_catalog_sha256
    )
    issues.extend(validated.issues)
    return CatalogValidation(
        digest,
        None,
        validated.fixture_results,
        _dedupe(issues),
        40,
    )


def validate_legacy_catalog(
    catalog: Any, *, expected_catalog_sha256: str
) -> CatalogValidation:
    """Validate an authenticated ``p1_adapter.LegacyCatalog`` without counting.

    The adapter authenticates and parses the legacy bytes.  This function still
    requires the registry digest explicitly, so a hand-constructed dataclass
    cannot silently become an authority.
    """

    digest = getattr(catalog, "raw_sha256", "")
    issues: list[Issue] = []
    if not is_sha256(expected_catalog_sha256):
        issues.append(
            _problem(
                "legacy.authority", "$", "expected legacy digest must be lowercase SHA-256"
            )
        )
    if digest != expected_catalog_sha256:
        issues.append(
            _problem(
                "legacy.digest", "$", "legacy catalog differs from registry authority"
            )
        )
    curves = getattr(catalog, "curves", None)
    if not isinstance(curves, tuple) or len(curves) != 40:
        issues.append(
            _problem("legacy.count", "$.curves", "legacy catalog must contain 40 curves")
        )
        return CatalogValidation(str(digest), None, (), _dedupe(issues), 40)
    fixture_results: list[FixtureValidation] = []
    observed_keys: list[tuple[Any, Any]] = []
    curve_ids: list[Any] = []
    for index, legacy_curve in enumerate(curves):
        fixture = _legacy_fixture(legacy_curve)
        result = validate_fixture(fixture, exact_count_authorized=False)
        fixture_results.append(result)
        path = f"$.curves[{index}]"
        issues.extend(_prefixed(issue, path) for issue in result.issues)
        observed_keys.append((legacy_curve.field_bits, legacy_curve.curve_index))
        curve_ids.append(legacy_curve.curve_id)

        # Independently bind all six retained generator projections to the
        # validated base point, without relying on producer arithmetic.
        try:
            oracle = OracleCurve(
                legacy_curve.field_p, legacy_curve.curve_a, legacy_curve.curve_b
            )
            base = legacy_curve.base_point
            for generator_index, generator in enumerate(legacy_curve.generators):
                generator_path = f"{path}.generators[{generator_index}]"
                if generator.generator_index != generator_index:
                    issues.append(
                        _problem(
                            "legacy.generator", generator_path, "generator index drifted"
                        )
                    )
                if generator.generator_id != f"{legacy_curve.curve_id}-g{generator_index}":
                    issues.append(
                        _problem("legacy.generator", generator_path, "generator ID drifted")
                    )
                point = generator.point
                if not oracle.is_on_curve(point):
                    issues.append(
                        _problem("legacy.generator", generator_path, "point is off curve")
                    )
                    continue
                if oracle.scalar_mul(generator.base_multiplier, base) != point:
                    issues.append(
                        _problem(
                            "legacy.generator",
                            generator_path,
                            "base multiplier does not reproduce the point",
                        )
                    )
                if oracle.scalar_mul(legacy_curve.full_order, point) is not None:
                    issues.append(
                        _problem(
                            "legacy.generator",
                            generator_path,
                            "full prime order does not annihilate the point",
                        )
                    )
        except (AttributeError, TypeError, ValueError) as error:
            issues.append(_problem("legacy.generator", path, str(error)))

    expected_keys = [(bits, index) for bits in (13, 16, 20, 24) for index in range(10)]
    if observed_keys != expected_keys:
        issues.append(
            _problem("legacy.coverage", "$.curves", "legacy curve ladder/index coverage drifted")
        )
    if len(curve_ids) != len(set(curve_ids)):
        issues.append(_problem("legacy.duplicate", "$.curves", "legacy curve IDs are not unique"))
    return CatalogValidation(
        str(digest), None, tuple(fixture_results), _dedupe(issues), 40
    )


__all__ = [
    "CI_CATALOG_KIND",
    "CI_FIELD_BITS",
    "FAMILIES",
    "REQUIRED_LIMITS",
    "CatalogValidation",
    "FixtureValidation",
    "validate_catalog_bytes",
    "validate_fixture",
    "validate_legacy_catalog",
    "validate_legacy_catalog_bytes",
]
