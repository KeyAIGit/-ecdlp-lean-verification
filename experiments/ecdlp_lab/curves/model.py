"""Immutable curve-fixture values shared by catalog adapters and consumers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

Point = tuple[int, int]


def _integer(value: Any, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _point(value: Any, name: str) -> Point:
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 2
        or any(isinstance(item, bool) or not isinstance(item, int) for item in value)
    ):
        raise ValueError(f"{name} must contain exactly two integers")
    return int(value[0]), int(value[1])


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value


@dataclass(frozen=True)
class ResolvedCurveFixture:
    """One catalog-authorized curve and generator in a prime-order subgroup."""

    catalog_sha256: str
    source_kind: str
    fixture_id: str
    curve_id: str
    family: str
    field_bits: int
    field_p: int
    curve_a: int
    curve_b: int
    full_order: int
    subgroup_order: int
    subgroup_order_bits: int
    cofactor: int
    generator: Point
    beta: int | None
    lambda_value: int | None
    order_certificate_type: str

    def __post_init__(self) -> None:
        for name in (
            "catalog_sha256",
            "source_kind",
            "fixture_id",
            "curve_id",
            "family",
            "order_certificate_type",
        ):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(f"{name} must be a non-empty string")
        if len(self.catalog_sha256) != 64 or any(
            character not in "0123456789abcdef" for character in self.catalog_sha256
        ):
            raise ValueError("catalog_sha256 must be lowercase hexadecimal SHA-256")
        for name, minimum in (
            ("field_bits", 3),
            ("field_p", 5),
            ("curve_a", 0),
            ("curve_b", 0),
            ("full_order", 2),
            ("subgroup_order", 2),
            ("subgroup_order_bits", 2),
            ("cofactor", 1),
        ):
            _integer(getattr(self, name), name, minimum=minimum)
        if self.field_bits != self.field_p.bit_length():
            raise ValueError("field_bits does not match field_p")
        if self.subgroup_order_bits != self.subgroup_order.bit_length():
            raise ValueError("subgroup_order_bits does not match subgroup_order")
        if self.full_order != self.cofactor * self.subgroup_order:
            raise ValueError("full_order must equal cofactor * subgroup_order")
        if not (0 <= self.curve_a < self.field_p and 0 <= self.curve_b < self.field_p):
            raise ValueError("curve coefficients must be canonical field elements")
        if any(not 0 <= coordinate < self.field_p for coordinate in self.generator):
            raise ValueError("generator coordinates must be canonical field elements")
        for name in ("beta", "lambda_value"):
            value = getattr(self, name)
            if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
                raise ValueError(f"{name} must be an integer or null")

    @classmethod
    def from_catalog_entry(
        cls,
        entry: Mapping[str, Any],
        *,
        catalog_sha256: str,
        source_kind: str = "committed_lab_catalog",
    ) -> "ResolvedCurveFixture":
        """Project one validated CI catalog entry into the consumer model."""

        if not isinstance(entry, Mapping):
            raise ValueError("catalog entry must be an object")
        endomorphism = entry.get("endomorphism")
        certificate = entry.get("order_certificate")
        if not isinstance(endomorphism, Mapping) or not isinstance(certificate, Mapping):
            raise ValueError("catalog entry lacks endomorphism or certificate data")
        return cls(
            catalog_sha256=catalog_sha256,
            source_kind=source_kind,
            fixture_id=_string(entry["fixture_id"], "fixture_id"),
            curve_id=_string(entry["curve_id"], "curve_id"),
            family=_string(entry["family"], "family"),
            field_bits=_integer(entry["field_bits"], "field_bits", minimum=3),
            field_p=_integer(entry["field_p"], "field_p", minimum=5),
            curve_a=_integer(entry["curve_a"], "curve_a"),
            curve_b=_integer(entry["curve_b"], "curve_b"),
            full_order=_integer(entry["full_order"], "full_order", minimum=2),
            subgroup_order=_integer(
                entry["subgroup_order"], "subgroup_order", minimum=2
            ),
            subgroup_order_bits=_integer(
                entry["subgroup_order_bits"], "subgroup_order_bits", minimum=2
            ),
            cofactor=_integer(entry["cofactor"], "cofactor", minimum=1),
            generator=_point(entry["generator"], "generator"),
            beta=endomorphism.get("beta"),
            lambda_value=endomorphism.get("lambda"),
            order_certificate_type=_string(
                certificate["type"], "order_certificate.type"
            ),
        )

    def public_curve_payload(self) -> dict[str, Any]:
        """Return the public curve fields used by target and method records."""

        return {
            "curve_fixture_id": self.fixture_id,
            "curve_id": self.curve_id,
            "field_bits": self.field_bits,
            "field_p": self.field_p,
            "curve_a": self.curve_a,
            "curve_b": self.curve_b,
            "generator": list(self.generator),
            "subgroup_order": self.subgroup_order,
            "subgroup_order_bits": self.subgroup_order_bits,
        }
