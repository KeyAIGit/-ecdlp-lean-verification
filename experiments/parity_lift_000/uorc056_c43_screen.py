from __future__ import annotations

from typing import Any

from uorc056_c43_core import (
    BASE_PAIRS, FEATURE_NAMES, PERIOD_SHIFTS, DivisionSequence,
    quadratic_character,
)

def feature_bits(value: int, p: int) -> tuple[int, int, int, int, int]:
    return (
        0 if quadratic_character(value, p) == 1 else 1,
        value & 1,
        1 if value > (p - 1) // 2 else 0,
        ((4 * value) // p) & 1,
        ((8 * value) // p) & 1,
    )


def mu6_code(value: int, p: int, beta: int) -> int:
    phase = pow(value, (p - 1) // 6, p)
    beta2 = beta * beta % p
    table = {
        1: 0,
        p - 1: 1,
        beta: 2,
        (-beta) % p: 3,
        beta2: 4,
        (-beta2) % p: 5,
    }
    return table[phase]


def no_mixed_parity(mask: int, odd: int, even: int) -> bool:
    return not ((mask & odd) and (mask & even))


def binary_pair_separates(
    left: int,
    right: int,
    odd: int,
    even: int,
    full: int,
) -> bool:
    not_left = full ^ left
    not_right = full ^ right
    return all(
        no_mixed_parity(mask, odd, even)
        for mask in (
            left & right,
            left & not_right,
            not_left & right,
            not_left & not_right,
        )
    )


def multistate_pair_separates(
    left_masks: tuple[int, ...],
    right_masks: tuple[int, ...],
    odd: int,
    even: int,
) -> bool:
    return all(
        no_mixed_parity(left & right, odd, even)
        for left in left_masks
        for right in right_masks
    )


def screen_period_ratios(
    sequences: list[DivisionSequence],
) -> dict[str, Any]:
    domains = [list(range(1, ds.n - 1)) for ds in sequences]
    row_count = sum(len(domain) for domain in domains)
    odd_mask = 0
    offset = 0
    for domain in domains:
        for k in domain:
            if k & 1:
                odd_mask |= 1 << offset
            offset += 1
    full_mask = (1 << row_count) - 1
    even_mask = full_mask ^ odd_mask

    candidates: list[dict[str, Any]] = []
    seen_field_profiles: set[tuple[tuple[int, ...], ...]] = set()

    for a, b in BASE_PAIRS:
        for r, s in PERIOD_SHIFTS:
            curve_values: list[list[int]] = []
            valid = True
            for ds, domain in zip(sequences, domains):
                values: list[int] = []
                for k in domain:
                    base = ds.dependent_net(a, b, k)
                    shifted = ds.dependent_net(a + r * ds.n, b + s * ds.n, k)
                    if not base or not shifted:
                        valid = False
                        break
                    values.append(shifted * pow(base, -1, ds.p) % ds.p)
                if not valid:
                    break
                curve_values.append(values)
            if not valid:
                continue
            signature = tuple(tuple(values) for values in curve_values)
            if signature in seen_field_profiles:
                continue
            seen_field_profiles.add(signature)

            feature_masks = [0 for _ in FEATURE_NAMES]
            mu6_masks = [0 for _ in range(6)]
            raw_mixed = False
            mu6_mixed = False
            global_index = 0
            for ds, domain, values in zip(sequences, domains, curve_values):
                raw_seen: dict[int, int] = {}
                mu_seen: dict[int, int] = {}
                for k, value in zip(domain, values):
                    parity = k & 1
                    if value in raw_seen and raw_seen[value] != parity:
                        raw_mixed = True
                    raw_seen[value] = parity
                    mu_code = mu6_code(value, ds.p, ds.beta)
                    if mu_code in mu_seen and mu_seen[mu_code] != parity:
                        mu6_mixed = True
                    mu_seen[mu_code] = parity
                    for feature_index, bit in enumerate(feature_bits(value, ds.p)):
                        if bit:
                            feature_masks[feature_index] |= 1 << global_index
                    mu6_masks[mu_code] |= 1 << global_index
                    global_index += 1

            candidates.append({
                "key": (a, b, r, s),
                "feature_masks": tuple(feature_masks),
                "mu6_masks": tuple(mu6_masks),
                "raw_mixed": raw_mixed,
                "mu6_mixed": mu6_mixed,
            })

    unique_binary_atoms: list[tuple[int, int, int]] = []
    seen_binary_masks: set[int] = set()
    exact_single_binary_decoders: list[dict[str, Any]] = []
    for candidate_index, candidate in enumerate(candidates):
        for feature_index, mask in enumerate(candidate["feature_masks"]):
            if mask == odd_mask or (full_mask ^ mask) == odd_mask:
                exact_single_binary_decoders.append({
                    "candidate": candidate["key"],
                    "feature": FEATURE_NAMES[feature_index],
                    "phase": 1 if mask == odd_mask else -1,
                })
            if mask not in seen_binary_masks:
                seen_binary_masks.add(mask)
                unique_binary_atoms.append((candidate_index, feature_index, mask))

    binary_pair_separators: list[dict[str, Any]] = []
    for left_index in range(len(unique_binary_atoms)):
        for right_index in range(left_index + 1, len(unique_binary_atoms)):
            left = unique_binary_atoms[left_index]
            right = unique_binary_atoms[right_index]
            if binary_pair_separates(
                left[2], right[2], odd_mask, even_mask, full_mask
            ):
                binary_pair_separators.append({
                    "left": {
                        "candidate": candidates[left[0]]["key"],
                        "feature": FEATURE_NAMES[left[1]],
                    },
                    "right": {
                        "candidate": candidates[right[0]]["key"],
                        "feature": FEATURE_NAMES[right[1]],
                    },
                })
                if len(binary_pair_separators) >= 20:
                    break
        if len(binary_pair_separators) >= 20:
            break

    unique_mu6_candidates: list[dict[str, Any]] = []
    seen_mu6_masks: set[tuple[int, ...]] = set()
    for candidate in candidates:
        signature = candidate["mu6_masks"]
        if signature not in seen_mu6_masks:
            seen_mu6_masks.add(signature)
            unique_mu6_candidates.append(candidate)

    mu6_pair_separators: list[dict[str, Any]] = []
    for left_index in range(len(unique_mu6_candidates)):
        for right_index in range(left_index + 1, len(unique_mu6_candidates)):
            left = unique_mu6_candidates[left_index]
            right = unique_mu6_candidates[right_index]
            if multistate_pair_separates(
                left["mu6_masks"], right["mu6_masks"], odd_mask, even_mask
            ):
                mu6_pair_separators.append({
                    "left": left["key"],
                    "right": right["key"],
                })
                if len(mu6_pair_separators) >= 20:
                    break
        if len(mu6_pair_separators) >= 20:
            break

    structural_survivors: list[dict[str, Any]] = []
    for b in range(-3, 4):
        if b == 0:
            continue
        expression_masks = {
            (name, feature): 0
            for name in ("even", "odd", "product", "quotient", "sum", "difference")
            for feature in FEATURE_NAMES
        }
        index = 0
        valid = True
        for ds, domain in zip(sequences, domains):
            for k in domain:
                even_base = ds.dependent_net(0, b, k)
                even_shifted = ds.dependent_net(0, b + ds.n, k)
                odd_base = ds.dependent_net(1, b, k)
                odd_shifted = ds.dependent_net(1, b + ds.n, k)
                if not all((even_base, even_shifted, odd_base, odd_shifted)):
                    valid = False
                    break
                even_ratio = even_shifted * pow(even_base, -1, ds.p) % ds.p
                odd_ratio = odd_shifted * pow(odd_base, -1, ds.p) % ds.p
                values = {
                    "even": even_ratio,
                    "odd": odd_ratio,
                    "product": even_ratio * odd_ratio % ds.p,
                    "quotient": even_ratio * pow(odd_ratio, -1, ds.p) % ds.p,
                    "sum": (even_ratio + odd_ratio) % ds.p,
                    "difference": (even_ratio - odd_ratio) % ds.p,
                }
                for name, value in values.items():
                    for feature_index, bit in enumerate(feature_bits(value, ds.p)):
                        if bit:
                            expression_masks[(name, FEATURE_NAMES[feature_index])] |= (
                                1 << index
                            )
                index += 1
            if not valid:
                break
        if valid:
            for (name, feature), mask in expression_masks.items():
                if mask == odd_mask or (full_mask ^ mask) == odd_mask:
                    structural_survivors.append({
                        "b": b,
                        "expression": name,
                        "feature": feature,
                        "phase": 1 if mask == odd_mask else -1,
                    })

    return {
        "chart": "k=1,...,n-2; Q=-G is a public exceptional point with even scalar n-1",
        "rows": row_count,
        "base_pairs": len(BASE_PAIRS),
        "period_shifts": len(PERIOD_SHIFTS),
        "defined_unique_ratios": len(candidates),
        "unique_binary_atoms": len(unique_binary_atoms),
        "unique_mu6_states": len(unique_mu6_candidates),
        "exact_single_binary_decoders": exact_single_binary_decoders,
        "binary_pair_separators": binary_pair_separators,
        "raw_state_separators": [
            candidate["key"] for candidate in candidates if not candidate["raw_mixed"]
        ],
        "mu6_state_separators": [
            candidate["key"] for candidate in candidates if not candidate["mu6_mixed"]
        ],
        "mu6_pair_separators": mu6_pair_separators,
        "structural_even_odd_shift_survivors": structural_survivors,
    }

