#!/usr/bin/env python3
"""Exact doubling-cycle and open-translation analysis for UORC-056 C55."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from uorc056_c54_transfer_core import Curve, state, chi
from uorc056_c55_cycle_core import (
    ALL,
    INHERITED,
    NEW,
    canonical_cycle_representative,
    cycle_carries,
    cycle_label,
    cycle_orientation_norm,
    cycle_phase_index,
    doubling_cycles,
    mixed_parity,
    multiplicative_order_two,
    pair_cycle_label,
    parity_sign,
    secp_certificate,
    verify_curve_fixture,
)


def affine_character_survivors(
    values: list[int], targets: list[int], prime: int, shifts: list[int]
) -> list[int]:
    survivors = []
    for shift in shifts:
        signs = [chi(value + shift, prime) for value in values]
        if 0 in signs:
            continue
        if signs == targets or signs == [-target for target in targets]:
            survivors.append(shift)
    return survivors


def representation_survivors(values: list[int], target_bits: list[int], prime: int) -> list[str]:
    survivors = []
    for mode in ("lsb", "half", "quartile", "octant"):
        bits = []
        for value in values:
            value %= prime
            if mode == "lsb":
                bit = value & 1
            elif mode == "half":
                bit = 1 if value > (prime - 1) // 2 else 0
            elif mode == "quartile":
                bit = ((4 * value) // prime) & 1
            else:
                bit = ((8 * value) // prime) & 1
            bits.append(bit)
        if bits == target_bits or [1 - bit for bit in bits] == target_bits:
            survivors.append(mode)
    return survivors


def analyze_curve(row, label: str) -> dict[str, Any]:
    verify_curve_fixture(row)
    p, n, generator, beta, lam = row
    curve = Curve(p)
    ord_two = multiplicative_order_two(n)
    cycles = doubling_cycles(n)
    if any(len(cycle) != ord_two for cycle in cycles):
        raise AssertionError("nonuniform doubling cycles")
    index = (n - 1) // ord_two
    if len(cycles) != index or index % 2:
        raise AssertionError("cycle index")

    states = {
        scalar: state(curve, n, generator, curve.mul(scalar, generator, n))
        for scalar in range(1, n)
    }

    labels = set()
    pair_labels = set()
    orientation_targets = []
    cycle_feature_values: dict[str, list[int]] = {
        f"{op}_{name}": []
        for op in ("prod", "sum")
        for name in ("A", "B", "N", "T", "R", "S")
    }
    cycle_feature_values.update({
        "label": [],
        "pair_label": [],
        "canonical_representative": [],
    })
    phase_values: dict[str, list[int]] = {
        "A_ratio": [], "B_ratio": [], "N_ratio": [],
        "T_difference": [], "R_difference": [],
    }
    phase_targets: list[int] = []
    cycle_records = []
    carry_checks = parity_word_checks = label_checks = 0

    for cycle in cycles:
        representative = canonical_cycle_representative(cycle)
        full_label = cycle_label(representative, n, ord_two)
        pair_label = pair_cycle_label(representative, n, ord_two)
        labels.add(full_label)
        pair_labels.add(pair_label)
        orientation = cycle_orientation_norm(cycle)
        carries = cycle_carries(cycle, n)
        if not mixed_parity(cycle):
            raise AssertionError("doubling cycle has constant parity")
        if sum(cycle) != n * sum(carries):
            raise AssertionError("cycle carry sum identity")
        if orientation != (-1 if sum(carries) & 1 else 1):
            raise AssertionError("orientation norm is not carry parity")
        if orientation != (-1 if sum(cycle) & 1 else 1):
            raise AssertionError("orientation norm is not residue-sum parity")
        neg_cycle = sorted((-scalar) % n for scalar in cycle)
        matching = next(other for other in cycles if sorted(other) == neg_cycle)
        if cycle_orientation_norm(matching) != -orientation:
            raise AssertionError("cycle orientation is not odd under negation")
        if cycle_label((-representative) % n, n, ord_two) != (-full_label) % n:
            raise AssertionError("full cycle label is not odd")
        if pair_cycle_label((-representative) % n, n, ord_two) != pair_label:
            raise AssertionError("pair label is not negation invariant")
        for scalar in cycle:
            if cycle_label(scalar, n, ord_two) != full_label:
                raise AssertionError("cycle label varies inside a cycle")
            if pair_cycle_label(scalar, n, ord_two) != pair_label:
                raise AssertionError("pair label varies inside a cycle")
            index_in_cycle = cycle_phase_index(cycle, scalar)
            if cycle[index_in_cycle] != scalar:
                raise AssertionError("phase index")
            target_next = cycle[(index_in_cycle + 1) % ord_two]
            carry = carries[index_in_cycle]
            if parity_sign(target_next) != (-1 if carry else 1):
                raise AssertionError("long-division carry is not next parity")
            carry_checks += 1
            parity_word_checks += 1

        orientation_targets.append(orientation)
        cycle_feature_values["label"].append(full_label % p)
        cycle_feature_values["pair_label"].append(pair_label % p)
        cycle_feature_values["canonical_representative"].append(representative % p)
        for name in ("A", "B", "N", "T", "R", "S"):
            product = 1
            total = 0
            for scalar in cycle:
                value = states[scalar][name]
                product = product * value % p
                total = (total + value) % p
            cycle_feature_values[f"prod_{name}"].append(product)
            cycle_feature_values[f"sum_{name}"].append(total)

        phase_anchor = next(
            (candidate for candidate in cycle
             if all(states[candidate][name] != 0 for name in ("A", "B", "N"))),
            None,
        )
        if phase_anchor is None:
            raise AssertionError("cycle has no common nonzero phase anchor")
        base = states[phase_anchor]
        for scalar in cycle:
            current = states[scalar]
            for name in ("A", "B", "N"):
                phase_values[f"{name}_ratio"].append(
                    current[name] * pow(base[name], -1, p) % p
                )
            phase_values["T_difference"].append((current["T"] - base["T"]) % p)
            phase_values["R_difference"].append((current["R"] - base["R"]) % p)
            phase_targets.append(scalar & 1)

        cycle_records.append({
            "representative": representative,
            "size": len(cycle),
            "label": full_label,
            "pair_label": pair_label,
            "orientation_norm": orientation,
            "even_points": sum(1 for scalar in cycle if scalar % 2 == 0),
            "odd_points": sum(1 for scalar in cycle if scalar % 2 == 1),
            "carry_count": sum(carries),
        })
        label_checks += len(cycle)

    if len(labels) != index or len(pair_labels) != index // 2:
        raise AssertionError("cycle label image size")

    structural_shifts = sorted({
        0, 1, p - 1, beta % p, beta * beta % p,
        generator[0] % p, generator[1] % p, lam % p,
        (n - 1) % p, ord_two % p, index % p,
    })
    complete_shifts = list(range(p)) if p <= 211 else structural_shifts

    cycle_affine = {}
    cycle_representation = {}
    for name, values in cycle_feature_values.items():
        cycle_affine[name] = affine_character_survivors(
            values, orientation_targets, p, structural_shifts
        )
        cycle_representation[name] = representation_survivors(
            values,
            [0 if target == 1 else 1 for target in orientation_targets],
            p,
        )

    phase_affine = {}
    phase_representation = {}
    phase_sign_targets = [1 if bit == 0 else -1 for bit in phase_targets]
    for name, values in phase_values.items():
        phase_affine[name] = affine_character_survivors(
            values, phase_sign_targets, p, structural_shifts
        )
        phase_representation[name] = representation_survivors(values, phase_targets, p)

    complete_small_curve_survivors = {}
    if p <= 211:
        for name, values in cycle_feature_values.items():
            complete_small_curve_survivors['cycle_' + name] = affine_character_survivors(
                values, orientation_targets, p, complete_shifts
            )
        for name, values in phase_values.items():
            complete_small_curve_survivors['phase_' + name] = affine_character_survivors(
                values, phase_sign_targets, p, complete_shifts
            )

    all_cycle_decoder_survivors = [
        (name, shift)
        for name, shifts in cycle_affine.items()
        for shift in shifts
    ]
    all_phase_decoder_survivors = [
        (name, shift)
        for name, shifts in phase_affine.items()
        for shift in shifts
    ]

    return {
        "label": label,
        "p": p,
        "n": n,
        "ord_n_2": ord_two,
        "ord_n_2_is_odd": True,
        "full_cycle_count": index,
        "pair_cycle_count": index // 2,
        "full_cycle_label_values": len(labels),
        "pair_cycle_label_values": len(pair_labels),
        "all_cycles_mixed_parity": all(
            record["even_points"] > 0 and record["odd_points"] > 0
            for record in cycle_records
        ),
        "cycle_label_alone_can_decode_parity": False,
        "cycle_orientation_norm_is_doubling_invariant": True,
        "cycle_orientation_norm_is_negation_odd": True,
        "cycle_affine_character_survivors": all_cycle_decoder_survivors,
        "cycle_representation_survivors": [
            (name, mode)
            for name, modes in cycle_representation.items()
            for mode in modes
        ],
        "within_cycle_affine_character_survivors": all_phase_decoder_survivors,
        "within_cycle_representation_survivors": [
            (name, mode)
            for name, modes in phase_representation.items()
            for mode in modes
        ],
        "structural_affine_shifts": structural_shifts,
        "complete_small_curve_affine_survivors": complete_small_curve_survivors,
        "carry_checks": carry_checks,
        "parity_word_checks": parity_word_checks,
        "label_checks": label_checks,
        "cycle_records": cycle_records,
        "errors": 0,
    }


def build_payload() -> dict[str, Any]:
    curves = []
    for index, row in enumerate(ALL):
        label = (
            f"inherited-{index + 1}"
            if index < len(INHERITED)
            else f"heldout-c55-{index + 1 - len(INHERITED)}"
        )
        curves.append(analyze_curve(row, label))

    secp = secp_certificate()
    aggregate = {
        "curves": len(curves),
        "inherited": len(INHERITED),
        "new_heldout": len(NEW),
        "scalar_rows": sum(curve["n"] - 1 for curve in curves),
        "cycles": sum(curve["full_cycle_count"] for curve in curves),
        "pair_cycles": sum(curve["pair_cycle_count"] for curve in curves),
        "carry_checks": sum(curve["carry_checks"] for curve in curves),
        "parity_word_checks": sum(curve["parity_word_checks"] for curve in curves),
        "label_checks": sum(curve["label_checks"] for curve in curves),
        "all_cycles_mixed_parity": all(
            curve["all_cycles_mixed_parity"] for curve in curves
        ),
        "all_cycle_labels_have_correct_image_size": all(
            curve["full_cycle_label_values"] == curve["full_cycle_count"]
            and curve["pair_cycle_label_values"] == curve["pair_cycle_count"]
            for curve in curves
        ),
        "universal_cycle_affine_character_survivors": [],
        "universal_cycle_representation_survivors": [],
        "universal_within_cycle_affine_character_survivors": [],
        "universal_within_cycle_representation_survivors": [],
        "errors": sum(curve["errors"] for curve in curves),
    }

    for field_name, aggregate_name in (
        ("cycle_affine_character_survivors", "universal_cycle_affine_character_survivors"),
        ("cycle_representation_survivors", "universal_cycle_representation_survivors"),
        ("within_cycle_affine_character_survivors", "universal_within_cycle_affine_character_survivors"),
        ("within_cycle_representation_survivors", "universal_within_cycle_representation_survivors"),
    ):
        common = None
        for curve in curves:
            names = {entry[0] for entry in curve[field_name]}
            common = names if common is None else common & names
        aggregate[aggregate_name] = sorted(common or set())

    payload: dict[str, Any] = {
        "profile_id": "UORC-056-CYCLE-LABEL-OPEN-TRANSLATION-C55",
        "schema_version": "1.0",
        "exact_cycle_label": {
            "full_label": "L(k)=k^M mod n, M=ord_n(2)",
            "pair_label": "L_pair(k)=k^(2M) mod n",
            "full_label_invariance": "L(2k)=L(k)",
            "negation": "L(-k)=-L(k) when M is odd",
            "pair_label_negation": "L_pair(-k)=L_pair(k)",
            "kernel": "ker(L)=<2>",
        },
        "cycle_phase_theorem": {
            "canonical_recurrence": "r_(j+1)=2r_j-n d_j, d_j in {0,1}",
            "next_parity": "(-1)^(r_(j+1))=(-1)^d_j",
            "cycle_sum": "sum_j r_j=n sum_j d_j",
            "orientation_norm": "prod_j (-1)^r_j=(-1)^(sum_j d_j)",
            "mixed_parity": (
                "every nonzero odd-length doubling cycle contains both even and odd "
                "canonical residues; otherwise r_j or n-r_j doubles strictly as integers "
                "around a closed cycle"
            ),
        },
        "arbitrary_decoder_obstruction": {
            "statement": (
                "any state constant on a complete doubling cycle has an exact mixed-parity "
                "collision and therefore cannot decode point parity, even with an arbitrary lookup"
            ),
            "cycle_label_only": "insufficient",
            "cycle_orientation_norm_only": "insufficient",
        },
        "rational_cycle_label_boundary": {
            "statement": (
                "if a nonconstant rational function f on E is invariant under doubling on all "
                "n-1 nonzero subgroup points and has pole degree d, then 5d >= n-1"
            ),
            "reason": (
                "f o [2]-f has pole degree at most 5d; if it vanished identically, pole degree "
                "would satisfy 4d=d, forcing f constant"
            ),
            "secp_minimum_pole_degree": secp["rational_cycle_invariant_pole_degree_lower_bound"],
        },
        "within_cycle_problem": {
            "normal_form": "k=r 2^j mod n after choosing a cycle representative r",
            "hidden_value": "the exponent j in the odd-order subgroup <2>",
            "generic_baseline": "baby-step giant-step costs Theta(sqrt(M))",
            "secp_generic_cost": secp["generic_within_cycle_bsgs_cost"],
            "consequence": (
                "knowing the exact 64-state secp cycle label gives only a constant-factor "
                "generic speedup and no sub-square-root exponent improvement"
            ),
        },
        "secp256k1": secp,
        "curves": curves,
        "aggregate": aggregate,
        "cost_ledger": {
            "cycle_label_from_scalar": "O(log n) modular exponentiation, but scalar k is unavailable",
            "cycle_label_from_point": "no public evaluator found",
            "explicit_cycle_walk": "Theta(M)=Theta(n) point doublings",
            "generic_within_cycle_search": "Theta(sqrt(M))=Theta(sqrt(n)) up to a constant factor",
            "explicit_cycle_orbit_factor": "Theta(M) coefficients or values",
        },
        "decision": {
            "exact_64_state_secp_cycle_label_found": True,
            "cycle_label_is_publicly_evaluable_from_Q": False,
            "cycle_label_alone_can_decode_parity": False,
            "exact_cycle_orientation_norm_found": True,
            "cycle_orientation_norm_alone_can_decode_point_parity": False,
            "bounded_rational_cycle_label_is_subsqrt": False,
            "declared_cycle_and_phase_character_grammars_closed": all(
                not aggregate[name]
                for name in (
                    "universal_cycle_affine_character_survivors",
                    "universal_cycle_representation_survivors",
                    "universal_within_cycle_affine_character_survivors",
                    "universal_within_cycle_representation_survivors",
                )
            ),
            "compressed_unsquared_open_translation_found": False,
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "successor": {
            "id": "DYNAMICAL-NORM-OR-CROSS-CYCLE-TRANSPORT-C56",
            "target": (
                "construct a sublinear evaluator for a doubling-orbit norm or a public cross-cycle "
                "charged transport; reject any construction that materializes one value per cycle vertex"
            ),
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload
