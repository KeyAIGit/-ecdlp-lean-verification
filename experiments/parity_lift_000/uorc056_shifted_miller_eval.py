from __future__ import annotations

from uorc056_shifted_miller_core import *

def line_function(curve: ExtCurve, left: ExtPoint, right: ExtPoint, at: ExtPoint) -> Ext:
    """Miller g_(left,right)(at), including the opposite-point case."""
    if left is None or right is None or at is None:
        raise ValueError("line function requires affine points")
    F = curve.field
    x1, y1 = left
    x2, y2 = right
    x, y = at
    if x1 == x2 and F.add(y1, y2) == F.zero:
        return F.sub(x, x1)
    if left == right:
        slope = F.div(
            F.add(F.scale(3, F.mul(x1, x1)), F.e(curve.base.a)),
            F.scale(2, y1),
        )
    else:
        slope = F.div(F.sub(y2, y1), F.sub(x2, x1))
    line = F.sub(F.sub(y, y1), F.mul(slope, F.sub(x, x1)))
    total = curve.add(left, right)
    if total is None:
        return line
    return F.div(line, F.sub(x, total[0]))


def miller_value(curve: ExtCurve, n: int, source: ExtPoint, at: ExtPoint) -> Ext:
    if source is None or at is None:
        raise ValueError("Miller evaluation requires affine points")
    F = curve.field
    value = F.one
    current = source
    for bit in bin(n)[3:]:
        value = F.mul(F.mul(value, value), line_function(curve, current, current, at))
        current = curve.add(current, current)
        if bit == "1":
            value = F.mul(value, line_function(curve, current, source, at))
            current = curve.add(current, source)
    if current is not None:
        raise AssertionError("Miller terminal point is not O")
    return value


def shifted_state(
    section: MillerSection,
    curve: ExtCurve,
    shift: ExtPoint,
    query: ExtPoint,
) -> Ext:
    F = curve.field
    return F.div(section.eval_ext(curve.add(query, shift), F), section.eval_ext(shift, F))


def centered_cross_ratio(
    instance: Instance,
    curve: ExtCurve,
    shift: ExtPoint,
    query: ExtPoint,
) -> Ext:
    if shift is None or query is None:
        raise ValueError("affine inputs required")
    F = curve.field
    half = curve.embed(instance.curve.mul(pow(2, -1, instance.n), instance.G))
    assert half is not None
    centered = curve.add(query, curve.neg(half))
    if centered is None:
        return F.one
    first = curve.add(half, shift)
    second = curve.add(shift, curve.neg(half))
    assert first is not None and second is not None
    return F.div(F.sub(centered[0], first[0]), F.sub(centered[0], second[0]))


def primitive_element(field: Fp2Field) -> Ext:
    order = field.p * field.p - 1
    primes = factor_integer(order)
    for a in range(field.p):
        for b in range(field.p):
            candidate = (a, b)
            if candidate == field.zero:
                continue
            if all(field.pow(candidate, order // prime) != field.one for prime in primes):
                return candidate
    raise AssertionError("primitive element not found")


def discrete_log_table(field: Fp2Field, generator: Ext) -> dict[Ext, int]:
    order = field.p * field.p - 1
    table: dict[Ext, int] = {}
    value = field.one
    for exponent in range(order):
        if value in table:
            raise AssertionError("generator repeated early")
        table[value] = exponent
        value = field.mul(value, generator)
    if value != field.one or len(table) != order:
        raise AssertionError("incomplete discrete-log table")
    return table


def minimal_character_order(logs: list[int], n: int, group_order: int) -> int | None:
    for order in divisors_from_factorization(factor_integer(group_order)):
        if order == 1:
            continue
        even = {logs[k - 1] % order for k in range(1, n) if k % 2 == 0}
        odd = {logs[k - 1] % order for k in range(1, n) if k % 2 == 1}
        if even.isdisjoint(odd):
            return order
    return None


def poly_add(field: Fp2Field, left: list[Ext], right: list[Ext]) -> list[Ext]:
    size = max(len(left), len(right))
    out = [field.zero] * size
    for index in range(size):
        out[index] = field.add(
            left[index] if index < len(left) else field.zero,
            right[index] if index < len(right) else field.zero,
        )
    while len(out) > 1 and out[-1] == field.zero:
        out.pop()
    return out


def poly_mul(field: Fp2Field, left: list[Ext], right: list[Ext]) -> list[Ext]:
    out = [field.zero] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            out[i + j] = field.add(out[i + j], field.mul(x, y))
    while len(out) > 1 and out[-1] == field.zero:
        out.pop()
    return out


def interpolate(field: Fp2Field, xs: list[Ext], ys: list[Ext]) -> list[Ext]:
    if len(xs) != len(set(xs)):
        raise ValueError("interpolation x-values must be distinct")
    divided = ys[:]
    for width in range(1, len(xs)):
        for index in range(len(xs) - 1, width - 1, -1):
            divided[index] = field.div(
                field.sub(divided[index], divided[index - 1]),
                field.sub(xs[index], xs[index - width]),
            )
    polynomial = [field.zero]
    basis = [field.one]
    for index, coefficient in enumerate(divided):
        polynomial = poly_add(
            field,
            polynomial,
            [field.mul(coefficient, value) for value in basis],
        )
        basis = poly_mul(field, basis, [field.neg(xs[index]), field.one])
    return polynomial
