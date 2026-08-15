#!/usr/bin/env python3
"""C29 autonomous high-degree state rigidity for UORC-056.

The package separates three notions:

* a finite autonomous state orbit with a state-only decoder;
* a recurrence fitted only on finitely many toy states;
* a global algebraic semiconjugacy S(P+G)=R(S(P)).

It proves/replays that exact canonical parity on an odd cycle has full cyclic
period, so every deterministic autonomous state orbit must contain n distinct
states. It also builds the exact Lagrange interpolation recurrence showing why
a recurrence fitted only on n toy states is tautological and costs n
coefficients. Finally it records the global curve classification and exact
PGL2 order obstruction for secp256k1.

No external target point, wallet, private key, unknown production scalar, or
scalar-indexed advice is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Sequence

PROFILE_ID = "UORC-056-AUTONOMOUS-STATE-RIGIDITY-C29"
DEFAULT_OUTPUT = Path(
    "experiments/parity_lift_000/uorc056_autonomous_state_rigidity_result.json"
)

SECP_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16
)
SECP_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)

FROZEN_CURVES = (
    (43, 31),
    (67, 79),
    (79, 67),
    (127, 127),
    (163, 139),
)
INTERPOLATION_ORDERS = (5, 7, 11, 13, 17, 19, 31)


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def canonical_parity(index: int) -> int:
    return -1 if index & 1 else 1


def parity_shift_collision(order: int, shift: int) -> tuple[int, int] | None:
    """Find k with parity(k+shift mod n) != parity(k)."""
    if order < 3 or order % 2 == 0:
        raise ValueError("order must be odd and at least three")
    d = shift % order
    if d == 0:
        return None
    for k in range(order):
        if canonical_parity((k + d) % order) != canonical_parity(k):
            return k, (k + d) % order
    raise AssertionError("nonzero shift unexpectedly preserved canonical parity")


def parity_minimal_cyclic_period(order: int) -> int:
    for period in range(1, order + 1):
        if all(
            canonical_parity((k + period) % order) == canonical_parity(k)
            for k in range(order)
        ):
            return period
    raise AssertionError("cyclic period not found")


def autonomous_state_orbit(
    transition: Sequence[int], initial: int, length: int
) -> list[int]:
    if not transition:
        raise ValueError("transition table must be nonempty")
    state = initial
    orbit: list[int] = []
    for _ in range(length):
        if not 0 <= state < len(transition):
            raise ValueError("state left transition domain")
        orbit.append(state)
        state = transition[state]
    return orbit


def state_decoder_conflict(
    states: Sequence[Any], outputs: Sequence[int]
) -> dict[str, Any] | None:
    if len(states) != len(outputs):
        raise ValueError("state/output length mismatch")
    seen: dict[Any, tuple[int, int]] = {}
    for index, (state, output) in enumerate(zip(states, outputs)):
        if state in seen and seen[state][1] != output:
            first_index, first_output = seen[state]
            return {
                "state": state,
                "first_index": first_index,
                "second_index": index,
                "first_output": first_output,
                "second_output": output,
            }
        seen[state] = (index, output)
    return None


def inv(value: int, prime: int) -> int:
    return pow(value % prime, -1, prime)


def trim(poly: Sequence[int], prime: int) -> list[int]:
    result = [coefficient % prime for coefficient in poly]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result or [0]


def poly_add(left: Sequence[int], right: Sequence[int], prime: int) -> list[int]:
    size = max(len(left), len(right))
    return trim(
        [
            (left[i] if i < len(left) else 0)
            + (right[i] if i < len(right) else 0)
            for i in range(size)
        ],
        prime,
    )


def poly_scale(poly: Sequence[int], scalar: int, prime: int) -> list[int]:
    return trim([scalar * coefficient for coefficient in poly], prime)


def poly_mul(left: Sequence[int], right: Sequence[int], prime: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] = (result[i + j] + a * b) % prime
    return trim(result, prime)


def poly_eval(poly: Sequence[int], value: int, prime: int) -> int:
    result = 0
    for coefficient in reversed(poly):
        result = (result * value + coefficient) % prime
    return result


def lagrange_interpolate(
    nodes: Sequence[int], values: Sequence[int], prime: int
) -> list[int]:
    if len(nodes) != len(values):
        raise ValueError("node/value length mismatch")
    if len({node % prime for node in nodes}) != len(nodes):
        raise ValueError("nodes must be distinct modulo prime")
    result = [0]
    for i, node in enumerate(nodes):
        basis = [1]
        denominator = 1
        for j, other in enumerate(nodes):
            if i == j:
                continue
            basis = poly_mul(basis, [(-other) % prime, 1], prime)
            denominator = denominator * (node - other) % prime
        basis = poly_scale(basis, values[i] * inv(denominator, prime), prime)
        result = poly_add(result, basis, prime)
    return trim(result, prime)


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def next_prime(value: int) -> int:
    candidate = max(2, value)
    while not is_prime(candidate):
        candidate += 1
    return candidate


def finite_cycle_interpolation(order: int) -> dict[str, Any]:
    """Fit the cyclic successor map on n distinct toy states.

    The chosen states are 0,...,n-1 in an auxiliary prime field q>2n. The
    successor values are 1,...,n-1,0. Lagrange interpolation always produces a
    polynomial of degree < n. This is a finite-table recurrence, not a compact
    public-Q construction.
    """
    prime = next_prime(2 * order + 1)
    nodes = list(range(order))
    values = [(index + 1) % order for index in nodes]
    polynomial = lagrange_interpolate(nodes, values, prime)
    checks = [poly_eval(polynomial, node, prime) for node in nodes]
    if checks != values:
        raise AssertionError("finite cycle interpolation failed")
    if len(polynomial) - 1 > order - 1:
        raise AssertionError("interpolation degree exceeded n-1")
    nonzero = sum(coefficient != 0 for coefficient in polynomial)
    return {
        "order": order,
        "auxiliary_field_prime": prime,
        "interpolated_degree": len(polynomial) - 1,
        "nonzero_coefficients": nonzero,
        "coefficient_slots": len(polynomial),
        "all_cycle_edges_verified": True,
        "finite_fit_is_linear_size": len(polynomial) >= order - 1,
    }


def pgl2_order(field_prime: int) -> int:
    return field_prime * (field_prime * field_prime - 1)


def pgl2_diagnostic(field_prime: int, subgroup_order: int) -> dict[str, Any]:
    group_order = pgl2_order(field_prime)
    gcd_value = math.gcd(group_order, subgroup_order)
    return {
        "p": field_prime,
        "n": subgroup_order,
        "pgl2_order": group_order,
        "gcd_n_pgl2_order": gcd_value,
        "order_n_element_not_excluded_by_group_order": gcd_value != 1,
        "characteristic_order_exception": field_prime == subgroup_order,
    }


def secp_record() -> dict[str, Any]:
    group_order = pgl2_order(SECP_P)
    gcd_value = math.gcd(SECP_N, group_order)
    if gcd_value != 1:
        raise AssertionError("secp PGL2 coprimality drifted")
    return {
        "p": SECP_P,
        "n": SECP_N,
        "pgl2_order": group_order,
        "gcd_n_pgl2_order": gcd_value,
        "n_divides_pgl2_order": group_order % SECP_N == 0,
        "one_coordinate_global_autonomous_rational_recurrence_excluded": True,
        "state_orbit_required_distinct_states": SECP_N,
        "state_orbit_required_distinct_states_bit_length": SECP_N.bit_length(),
        "additional_states_beyond_public_G_Q_not_interpreted": (
            "The orbit count is semantic, not a storage lower bound; one field "
            "element can take n values if a valid order-n action exists."
        ),
    }


def finite_state_controls() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for order in INTERPOLATION_ORDERS:
        parity_period = parity_minimal_cyclic_period(order)
        if parity_period != order:
            raise AssertionError("canonical parity lost full cyclic period")

        parity_states = [canonical_parity(k) for k in range(order)]
        conflict = state_decoder_conflict(
            parity_states,
            [canonical_parity(k) for k in range(order)],
        )
        # The state-only decoder has no conflict because state equals output;
        # the obstruction is in a deterministic transition on the two states.
        transition_edges: dict[int, set[int]] = {1: set(), -1: set()}
        for k in range(order):
            transition_edges[parity_states[k]].add(
                parity_states[(k + 1) % order]
            )
        deterministic_two_state_update = all(
            len(targets) == 1 for targets in transition_edges.values()
        )
        if deterministic_two_state_update:
            raise AssertionError("odd-cycle parity unexpectedly closed on two states")

        full_transition = [(index + 1) % order for index in range(order)]
        orbit = autonomous_state_orbit(full_transition, 0, order)
        if len(set(orbit)) != order:
            raise AssertionError("faithful n-cycle lost a state")
        outputs = [canonical_parity(index) for index in orbit]
        if state_decoder_conflict(orbit, outputs) is not None:
            raise AssertionError("faithful state orbit decoder conflict")

        rows.append(
            {
                "order": order,
                "canonical_parity_minimal_cyclic_period": parity_period,
                "two_state_transition_targets": {
                    str(key): sorted(value)
                    for key, value in transition_edges.items()
                },
                "two_state_autonomous_update_exists": False,
                "faithful_cycle_distinct_states": len(set(orbit)),
                "finite_interpolation": finite_cycle_interpolation(order),
                "state_equals_output_decoder_conflict": conflict,
            }
        )
    return rows


def run() -> dict[str, Any]:
    shift_witnesses = {
        str(order): {
            str(shift): parity_shift_collision(order, shift)
            for shift in range(1, order)
        }
        for order in (5, 7, 11, 13)
    }
    return {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "finite_autonomous_state_theorem": {
            "statement": (
                "For odd n, the cyclic word sigma(k)=(-1)^k on Z/nZ has "
                "minimal period n. Therefore any deterministic autonomous "
                "state orbit with a state-only exact decoder must have n "
                "distinct states on the marked cycle."
            ),
            "consequence": (
                "An autonomous exact state cannot be a genuine two-state or "
                "four-state summary. It carries a faithful n-phase orbit, even "
                "if encoded in one field element."
            ),
            "four_state_consequence": (
                "Neither (g_G,J_G) nor W_G=g_G+2J_G can be a closed "
                "autonomous state under Q->Q+G with a state-only decoder: "
                "they have only four values, while an exact autonomous orbit "
                "requires n distinct semantic states."
            ),
            "decoder_with_Q_warning": (
                "If the decoder also receives Q, collision arguments on S "
                "alone are invalid. The complete state is then (Q,S(Q)); its "
                "Q-coordinate already carries the original marked subgroup "
                "point, so the builder/decoder composition is the original "
                "parity problem in another factorization."
            ),
            "scope_warning": (
                "Distinct semantic values are not by themselves a memory or "
                "circuit lower bound; one field element can hold n values."
            ),
        },
        "finite_fit_warning": {
            "statement": (
                "Any prescribed successor relation on n distinct field states "
                "can be interpolated by a polynomial of degree below n."
            ),
            "consequence": (
                "A recurrence verified only on a frozen n-point orbit is "
                "tautological unless its compiler, coefficients and uniform "
                "cost are independently compact."
            ),
        },
        "global_semiconjugacy_theorem": {
            "premise": (
                "A nonconstant algebraic state S:E->V satisfies the global "
                "identity S(P+G)=R(S(P)) for one fixed algebraic update R."
            ),
            "normalized_image": (
                "The normalization X of S(E) is a projective curve of genus at "
                "most one."
            ),
            "genus_zero": (
                "X is P1 because S(O) is rational. The induced update has "
                "order n in PGL2(F_p). secp256k1 excludes this because "
                "gcd(n,p(p^2-1))=1."
            ),
            "genus_one": (
                "After using S(O) as origin, S is an isogeny phi:E->X and the "
                "update is translation by phi(G). Thus phi(Q)=[k]phi(G): the "
                "same hidden canonical scalar is merely recoded on an isogenous "
                "curve."
            ),
            "degree_growth_consequence": (
                "A fixed global autonomous update cannot use repeated degree "
                "growth to integrate translation. On the normalized image it "
                "is a finite-order automorphism."
            ),
            "genus_one_scope": (
                "The isogeny classification is a reduction, not a theorem that "
                "isogenous coordinates can never help. Any claimed advantage "
                "must be supplied by a separate public evaluator on the "
                "isogenous marked subgroup; autonomous compression itself has "
                "not removed the hidden scalar."
            ),
            "scope_warning": (
                "The theorem does not cover a recurrence fitted only on the "
                "finite subgroup, a nonautonomous target-dependent composition "
                "chain, branching, or a decoder that uses additional public "
                "coordinates not included in the complete state image."
            ),
        },
        "finite_state_controls": finite_state_controls(),
        "shift_witnesses": shift_witnesses,
        "pgl2_frozen_diagnostics": [
            pgl2_diagnostic(p, n) for p, n in FROZEN_CURVES
        ],
        "secp256k1": secp_record(),
        "decision": {
            "faithful_n_phase_required_for_autonomous_state": True,
            "finite_orbit_recurrence_without_cost_is_vacuous": True,
            "global_genus_zero_autonomous_state_excluded": True,
            "global_genus_one_state_is_isogeny_recoding": True,
            "global_autonomous_algebraic_escape_found": False,
            "nonautonomous_oriented_composition_found": False,
            "public_branch_sensitive_seed_found": False,
            "joint_A_B_recurrence_found": False,
            "modular_composition_state_found": False,
            "high_degree_low_size_state_blocked": False,
            "exact_parity_extraction_found": False,
            "complete_cost_gate_passed": False,
            "compact_branch_odd_evaluator_found": False,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "next_frontier": (
            "The surviving mechanism must be nonautonomous or target-dependent: "
            "a short composition/compiler that evaluates the oriented branch at "
            "one public Q without realizing every translation step as one fixed "
            "state update and without fitting an n-coefficient orbit table."
        ),
        "scientific_boundary": (
            "C29 classifies autonomous exact states. It is not an unrestricted "
            "arithmetic-circuit, modular-composition, parity, or ECDLP lower bound."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run())
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("C29 autonomous-state artifact drift")
        print("UORC056_AUTONOMOUS_STATE_RIGIDITY_C29_OK")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
