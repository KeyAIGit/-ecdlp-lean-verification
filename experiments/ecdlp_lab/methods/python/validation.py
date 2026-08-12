"""Source-independent validation of Python reference-method candidates."""

from __future__ import annotations

from experiments.framework.ec_oracle import Curve as OracleCurve
from experiments.framework.ec_oracle import validate_scalar


def validate_candidate_independently(
    *,
    field_p: int,
    curve_a: int,
    curve_b: int,
    generator: tuple[int, int],
    target: tuple[int, int] | None,
    subgroup_order: int,
    candidate_scalar: int | None,
) -> bool:
    """Validate a canonical scalar with arithmetic independent of the method."""

    if candidate_scalar is None:
        return False
    if (
        isinstance(candidate_scalar, bool)
        or not isinstance(candidate_scalar, int)
        or not 0 <= candidate_scalar < subgroup_order
    ):
        return False
    oracle = OracleCurve(field_p, curve_a, curve_b)
    return validate_scalar(oracle, generator, target, candidate_scalar)


__all__ = ["validate_candidate_independently"]
