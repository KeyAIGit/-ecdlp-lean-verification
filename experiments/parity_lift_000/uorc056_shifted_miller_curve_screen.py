from __future__ import annotations

from uorc056_shifted_miller_core import *
from uorc056_shifted_miller_eval import *

def build_curve_payload(instance: Instance) -> tuple[dict[str, object], dict[str, object]]:
    p, n = instance.curve.p, instance.n
    d = smallest_nonsquare(p)
    field = Fp2Field(p, d)
    curve = ExtCurve(instance.curve, field)
    section = build_miller_section(instance)
    table_base = [instance.curve.mul(k, instance.G) for k in range(n)]
    table = [curve.embed(point) for point in table_base]
    shifts = twist_points(instance, field)
    expected_twist = 2 * p + 1 - n
    if len(shifts) != expected_twist:
        raise AssertionError(f"twist size mismatch: {len(shifts)} != {expected_twist}")
    for shift in shifts:
        assert shift is not None
        frobenius = (field.conj(shift[0]), field.conj(shift[1]))
        if frobenius != curve.neg(shift):
            raise AssertionError("anti-rational shift Frobenius profile failed")

    generator = primitive_element(field)
    logs = discrete_log_table(field, generator)
    character_histogram: dict[int, int] = {}
    quadratic_shift_survivors = 0
    gauge_checks = 0
    torus_checks = 0
    canonical_shift = shifts[0]
    canonical_states: list[Ext] = []
    canonical_torus: list[Ext] = []
    canonical_location_logs: list[list[int]] = []

    reference = table[2]
    assert reference is not None
    embedded_g = table[1]
    assert embedded_g is not None

    for shift_index, shift in enumerate(shifts):
        assert shift is not None
        shift_states: list[Ext] = []
        torus_values: list[Ext] = []
        for k in range(1, n):
            query = table[k]
            assert query is not None
            state = shifted_state(section, curve, shift, query)
            if state == field.zero:
                raise AssertionError("shifted state unexpectedly zero")
            shift_states.append(state)
            torus_values.append(field.pow(state, p - 1))

        state_logs = [logs[value] for value in shift_states]
        minimum = minimal_character_order(state_logs, n, p * p - 1)
        if minimum is None:
            raise AssertionError("full character failed to separate parity")
        character_histogram[minimum] = character_histogram.get(minimum, 0) + 1
        if minimum == 2:
            quadratic_shift_survivors += 1

        reference_state = shift_states[1]
        reference_f = section.eval_ext(reference, field)
        minus_shift = curve.neg(shift)
        gauge_reference = line_function(curve, embedded_g, minus_shift, reference)
        for k in range(2, n):
            query = table[k]
            assert query is not None
            state = shift_states[k - 1]
            query_f = section.eval_ext(query, field)
            gauge_query = line_function(curve, embedded_g, minus_shift, query)
            predicted = field.mul(
                field.div(query_f, reference_f),
                field.pow(field.div(gauge_reference, gauge_query), n),
            )
            if field.div(state, reference_state) != predicted:
                raise AssertionError("normalized shift-gauge identity failed")
            gauge_checks += 1

        torus_reference = torus_values[0]
        ratio_reference = centered_cross_ratio(instance, curve, shift, table[1])
        for k in range(1, n):
            query = table[k]
            assert query is not None
            ratio = centered_cross_ratio(instance, curve, shift, query)
            predicted = field.pow(field.div(ratio, ratio_reference), n)
            if field.div(torus_values[k - 1], torus_reference) != predicted:
                raise AssertionError("torus/Kummer collapse failed")
            if field.pow(ratio, p + 1) != field.one:
                raise AssertionError("centered ratio not in norm-one torus")
            torus_checks += 1

        if shift_index == 0:
            canonical_states = shift_states
            canonical_torus = torus_values

    assert canonical_shift is not None
    miller_denominator = miller_value(curve, n, embedded_g, canonical_shift)
    miller_comparisons = 0
    for k in range(1, n):
        query = table[k]
        assert query is not None
        direct = field.div(
            miller_value(curve, n, embedded_g, curve.add(query, canonical_shift)),
            miller_denominator,
        )
        if direct != canonical_states[k - 1]:
            raise AssertionError("Miller loop and local-section state disagree")
        miller_comparisons += 1

    state_to_parity: dict[Ext, int] = {}
    for k, state in enumerate(canonical_states, start=1):
        parity = 1 if k % 2 == 0 else -1
        if state in state_to_parity and state_to_parity[state] != parity:
            raise AssertionError("full shifted state does not determine parity")
        state_to_parity[state] = parity
    xs = list(state_to_parity)
    ys = [field.e(state_to_parity[x]) for x in xs]
    interpolant = interpolate(field, xs, ys)
    degree = len(interpolant) - 1
    nonzero_coefficients = sum(value != field.zero for value in interpolant)
    even_states = sum(value == 1 for value in state_to_parity.values())
    odd_states = sum(value == -1 for value in state_to_parity.values())

    torus_fibres: dict[Ext, list[int]] = {}
    for k, value in enumerate(canonical_torus, start=1):
        torus_fibres.setdefault(value, []).append(k)
    inverse_two = pow(2, -1, n)
    expected_fibres = []
    for fibre in torus_fibres.values():
        ordered = sorted(fibre)
        if len(ordered) == 1:
            if ordered[0] not in (1, inverse_two):
                raise AssertionError("unexpected singleton torus fibre")
        elif len(ordered) == 2:
            if (ordered[0] + ordered[1]) % n != 1:
                raise AssertionError("unexpected centered Kummer fibre")
            if ordered[0] % 2 != ordered[1] % 2:
                raise AssertionError("centered Kummer fibre mixes parity")
        else:
            raise AssertionError("unexpected torus fibre size")
        expected_fibres.append(ordered)

    t = (n - 1) // 2
    multipliers = (1, 2, 3, (t - 2) % n, t, (-t) % n, (-(t - 2)) % n)
    for multiplier in multipliers:
        profile: list[int] = []
        for k in range(1, n):
            point = table[(multiplier * k) % n]
            assert point is not None
            value = shifted_state(section, curve, canonical_shift, point)
            profile.append(logs[value])
        canonical_location_logs.append(profile)

    quadratic_subsets = 0
    for mask in range(1, 1 << len(multipliers)):
        valid = True
        reference_bit = sum(
            canonical_location_logs[index][0]
            for index in range(len(multipliers))
            if (mask >> index) & 1
        ) % 2
        for k in range(1, n):
            bit = sum(
                canonical_location_logs[index][k - 1]
                for index in range(len(multipliers))
                if (mask >> index) & 1
            ) % 2
            if (bit - reference_bit) % 2 != ((k + 1) & 1):
                valid = False
                break
        if valid:
            quadratic_subsets += 1

    curve_payload = {
        "instance": instance.name,
        "p": p,
        "n": n,
        "quadratic_nonsquare": d,
        "section": {
            "A_coefficients": len(section.A),
            "B_coefficients": len(section.B),
            "local_zero_order": n,
            "leading_local_coefficient_nonzero": section.leading_local_coefficient != 0,
            "only_rational_zero_is_G": True,
        },
        "twist_shifts": len(shifts),
        "shift_query_cases": len(shifts) * (n - 1),
        "normalized_shift_gauge_checks": gauge_checks,
        "torus_kummer_checks": torus_checks,
        "miller_loop_comparisons": miller_comparisons,
        "minimal_character_order_histogram": {
            str(key): value for key, value in sorted(character_histogram.items())
        },
        "quadratic_character_shift_survivors": quadratic_shift_survivors,
        "canonical_shift": {
            "x": list(canonical_shift[0]),
            "y": list(canonical_shift[1]),
            "distinct_full_states": len(state_to_parity),
            "interpolation_degree": degree,
            "interpolation_nonzero_coefficients": nonzero_coefficients,
            "distinct_even_states": even_states,
            "distinct_odd_states": odd_states,
            "rational_decoder_degree_lower_bound": max(even_states, odd_states),
            "distinct_torus_states": len(torus_fibres),
            "torus_fibres": expected_fibres,
            "three_carry_location_multipliers": list(multipliers),
            "quadratic_subset_exact_survivors": quadratic_subsets,
        },
    }
    grammar_data = {
        "instance": instance.name,
        "n": n,
        "group_order": p * p - 1,
        "logs": canonical_location_logs,
    }
    return curve_payload, grammar_data
