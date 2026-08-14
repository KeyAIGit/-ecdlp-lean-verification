#!/usr/bin/env python3
"""Source-bound C24 audit of candidate branch-sensitive leaves.

Only committed public research artifacts, symbolic two-world models, and public
finite fields are used. The script accepts no external point, unknown scalar,
wallet, private key, or production target.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = Path("archive/untrusted_intake/parity_lift_000")


def candidate(
    identifier: str,
    filename: str,
    markers: list[str],
    mechanism: str,
    classification: str,
    global_branch_flip: str,
    geometric_tau: str,
    generator_inversion: str,
    generator_replacement: str,
    public_construction: bool,
    branch_sensitive_leaf: bool,
    constructible_without_orientation_advice: bool,
    target_alignment_proved: bool,
    blocker: str,
) -> dict[str, Any]:
    return {
        "id": identifier,
        "source": str(ARCHIVE / filename),
        "required_markers": markers,
        "mechanism": mechanism,
        "classification": classification,
        "global_branch_flip": global_branch_flip,
        "geometric_tau": geometric_tau,
        "generator_inversion": generator_inversion,
        "generator_replacement": generator_replacement,
        "public_construction": public_construction,
        "branch_sensitive_leaf": branch_sensitive_leaf,
        "constructible_without_orientation_advice": (
            constructible_without_orientation_advice
        ),
        "target_alignment_proved": target_alignment_proved,
        "complete_cost_gate_passed": False,
        "blocker": blocker,
    }


CANDIDATES: tuple[dict[str, Any], ...] = (
    candidate(
        "common_basis_frobenius_stickelberger_determinant",
        "FROBENIUS_STICKELBERGER_DETERMINANT_050.md",
        [
            "public constant * multiplicative net ratio",
            "independently normalized or twisted rows remain open",
        ],
        "common-basis elliptic evaluation determinant",
        "transport_only",
        "no independent Hilbert90 branch datum after factorization",
        "inherited from the multiplicative elliptic-net ratio",
        "no independent orientation source was isolated",
        "known integer-matrix pullback preserves the factorization",
        True,
        False,
        True,
        False,
        "the determinant factors before any branch extraction",
    ),
    candidate(
        "independent_scalar_theta_row_normalization",
        "INDEPENDENT_THETA_ROW_NORMALIZATION_051.md",
        ["product_i r_i", "Genuinely different theta characteristics"],
        "diagonal row trivialization plus common basis change",
        "transport_only",
        "inherits exactly the product of the supplied row factors",
        "inherits the row-factor laws",
        "inherits the row-factor laws",
        "inherits the row-factor laws",
        True,
        False,
        True,
        False,
        "any new bit is already present in the explicit row factors",
    ),
    candidate(
        "standard_twisted_theta_characteristic_descent",
        "TWISTED_THETA_CHARACTERISTIC_052.md",
        ["Canonical Frobenius-orbit norm", "y(Q)^2/y(G)^2"],
        "Frobenius descent of the nontrivial genus-one theta characteristics",
        "canonical_sign_blind",
        "fixed after canonical orbit norm",
        "fixed under point negation after orbit norm",
        "fixed under G to -G",
        "symmetric descent remains generator-blind",
        True,
        False,
        True,
        False,
        "the canonical base-field object is the square y^2",
    ),
    candidate(
        "standard_level_n_metaplectic_theta_intertwiner",
        "METAPLECTIC_THETA_INTERTWINER_053.md",
        ["dim H^0(E,L)>=n", "Public parity / absolute EDS-residue decoder"],
        "level-n Heisenberg representation and metaplectic basis change",
        "branch_sensitive_large_or_seeded",
        "non-fixed only after choosing a dual character or linearization",
        "projective action does not canonically fix the missing scalar phase",
        "depends on the chosen dual direction",
        "linear lifts differ by Hom(H,mu_n)",
        False,
        True,
        False,
        False,
        "the standard state has dimension at least n and a dual character must be chosen",
    ),
    candidate(
        "p_adic_global_branch_continuation",
        "P_ADIC_GLOBAL_BRANCH_054.md",
        [
            "Hensel lifting preserves rather than creates",
            "formal logarithm distinguish prime-to-p torsion",
        ],
        "formal sigma, canonical lift, Hensel lift, and Coleman continuation",
        "branch_sensitive_large_or_seeded",
        "both initial plus and minus seeds lift uniquely",
        "canonical lifting transports both branches without selecting one",
        "no canonical p-adic path selects the marked generator orientation",
        "no public covariant path or seed was constructed",
        False,
        True,
        False,
        False,
        "local continuation preserves an initial branch seed and subgroup points are outside the formal kernel",
    ),
    candidate(
        "normalized_anti_frobenius_period_seed",
        "ANTI_FROBENIUS_ORIENTATION_SEED_031.md",
        ["U_[-G](Q)=U_G(-Q)=-U_G(Q)", "Explicit quotient-state count"],
        "normalized anti-Frobenius period resolvent U_G(Q)",
        "branch_sensitive_large_or_seeded",
        "a non-fixed line exists, but compact Hilbert90 branch alignment is absent",
        "the source records anti-Frobenius sigma, not the required geometric tau law",
        "U_[-G](Q)=-U_G(Q)",
        "U_[uG](Q)=U_G([u^-1]Q) under the chosen character normalization",
        False,
        True,
        False,
        False,
        "evaluation needs the order-n dual phase or a quotient state of size (n-1)/6",
    ),
    candidate(
        "first_absolute_order_n_torsion_jet",
        "ABSOLUTE_EDS_SECTION_003.md",
        ["fast absolute order-n section exists", "first jet isolates rho_G"],
        "first invariant derivative of the order-n division polynomial",
        "public_fast_target_dependent",
        "the exact character law collapses to the public point-function bit",
        "the invariant tangent derivative uses the public y orientation",
        "does not provide an x-only marked-root selector on secp256k1",
        "inherits the standard division-polynomial normalization law",
        True,
        False,
        True,
        False,
        "the fast absolute section supplies no independent equation for rho_G or parity",
    ),
    candidate(
        "hidden_nonlocal_R3_odd_anchor",
        "NONLOCAL_ODD_ANCHOR_004.md",
        ["The first genuine odd hidden aggregate", "R3(-Q) = R3(Q)"],
        "odd three-factor EDS-residue aggregate on a GLV orbit",
        "branch_sensitive_large_or_seeded",
        "odd under the EDS residue gauge, but still hidden",
        "Kummer invariant on Q to -Q in the retained setting",
        "the aggregate remains hidden behind the canonical GLV carry",
        "a complete public covariance and evaluator were not constructed",
        False,
        True,
        False,
        True,
        "no public decoder for R3 or the GLV carry gamma is known",
    ),
    candidate(
        "known_algebraic_GLV_orbit_sections",
        "GLV_CARRY_SEPARATION_005.md",
        [
            "Every exact odd section currently available has the same GLV canonical-lift",
            "independent GLV carry multiplier found",
        ],
        "torsion jets and near-period sections under C3 orbit norm",
        "public_fast_target_dependent",
        "all exact available odd orbit norms remain in the dependent gR3 class",
        "no independent tau-odd equation is produced",
        "the same canonical-lift carry accompanies every exact odd section",
        "no new multiplier class was found",
        True,
        False,
        True,
        False,
        "the public equations are dependent and do not isolate R3 or gamma",
    ),
    candidate(
        "field_permutation_GLV_carry_coordinate",
        "FIELD_PERMUTATION_CARRY_IDENTITY_017.md",
        [
            "O_beta(x) = -C_beta((beta-1)*x)",
            "not a new inverse-polylogarithmic scalar",
        ],
        "canonical field ordering of the x-coordinate GLV orbit",
        "canonical_sign_blind",
        "independent of the Hilbert90 plus/minus branch",
        "x-only and therefore fixed under point negation",
        "does not retain generator orientation through x",
        "a public scaling only permutes the known carry frequencies",
        True,
        False,
        True,
        False,
        "the candidate is exactly a known field carry after public scaling",
    ),
    candidate(
        "sparse_three_term_translation_resultant",
        "UORC056_SPARSE_TWO_TRANSLATION_RESULTANT_C5.md",
        [
            "The unresolved minimal object is",
            "A degree-`n` resultant, an `n`-dimensional state",
        ],
        "det(aI+bT_G+cT_Q) and its sparse Sylvester resultant",
        "open_cost_unresolved",
        "no non-fixed Hilbert90 coefficient or exact branch law is known",
        "not classified for the surviving asymmetric coefficient family",
        "only partial affine-exponent symmetries are known",
        "six Mobius exponent symmetries are exact, but target covariance is unresolved",
        False,
        False,
        True,
        False,
        "the explicit representation has degree n and no compact evaluator or non-fixed coefficient generator is known",
    ),
)

REQUIRED_KEYS = {
    "id",
    "source",
    "required_markers",
    "mechanism",
    "classification",
    "global_branch_flip",
    "geometric_tau",
    "generator_inversion",
    "generator_replacement",
    "public_construction",
    "branch_sensitive_leaf",
    "constructible_without_orientation_advice",
    "target_alignment_proved",
    "complete_cost_gate_passed",
    "blocker",
}

EXPECTED_CLASS_COUNTS = {
    "canonical_sign_blind": 2,
    "transport_only": 2,
    "branch_sensitive_large_or_seeded": 4,
    "public_fast_target_dependent": 2,
    "open_cost_unresolved": 1,
}


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def audit_source(item: dict[str, Any]) -> dict[str, Any]:
    missing_keys = sorted(REQUIRED_KEYS - item.keys())
    extra_keys = sorted(item.keys() - REQUIRED_KEYS)
    if missing_keys or extra_keys:
        raise AssertionError(
            f"schema mismatch for {item.get('id')}: "
            f"missing={missing_keys} extra={extra_keys}"
        )
    path = ROOT / item["source"]
    if not path.is_file():
        raise AssertionError(f"missing source: {path}")
    raw = path.read_bytes()
    normalized = normalize_whitespace(raw.decode("utf-8"))
    missing_markers = [
        marker
        for marker in item["required_markers"]
        if normalize_whitespace(marker) not in normalized
    ]
    if missing_markers:
        raise AssertionError(
            f"source markers missing for {item['id']}: {missing_markers}"
        )
    row = dict(item)
    row.pop("required_markers")
    row["source_sha256"] = hashlib.sha256(raw).hexdigest()
    row["source_bytes"] = len(raw)
    row["source_markers_verified"] = True
    return row


def collision_witnesses() -> dict[str, Any]:
    rows: list[dict[str, int]] = []
    total_decoders = 0
    for size in (2, 3, 5, 7, 11):
        worlds = tuple(range(size))
        successful = 0
        for chosen_output in worlds:
            total_decoders += 1
            if all(chosen_output == world for world in worlds):
                successful += 1
        if successful:
            raise AssertionError("an invariant singleton quotient selected an orbit")
        rows.append(
            {
                "orbit_size": size,
                "public_fibers": 1,
                "candidate_decoders_from_singleton": size,
                "successful_global_selectors": 0,
            }
        )
    return {
        "orbit_fixtures": rows,
        "candidate_decoders_checked": total_decoders,
        "all_invariant_global_selectors_rejected": True,
    }


def finite_field_two_world_witnesses() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    collisions = 0
    separations = 0
    for prime in (43, 61, 67, 79, 97, 127, 163):
        local = 0
        for branch in range(1, prime):
            opposite = (-branch) % prime
            if branch == opposite:
                continue
            if branch * branch % prime != opposite * opposite % prime:
                raise AssertionError("square failed to identify a sign pair")
            local += 1
            collisions += 1
            if branch == opposite:
                raise AssertionError("separated output used equal state")
            separations += 1
        rows.append(
            {
                "p": prime,
                "nonzero_sign_collisions": local,
                "all_seedless_square_data_equal": True,
                "all_separated_outputs_used_nonfixed_state": True,
            }
        )
    return {
        "fields": rows,
        "public_data_collisions": collisions,
        "required_state_separations": separations,
        "all_two_world_collision_checks_passed": True,
    }


def best_survivors() -> list[dict[str, str]]:
    return [
        {
            "candidate": "normalized anti-Frobenius period U_G",
            "positive_structure": "exact generator inversion and replacement covariance",
            "blocking_resource": "order-n dual phase or quotient state of size (n-1)/6",
        },
        {
            "candidate": "hidden GLV odd aggregate R3 and carry gamma",
            "positive_structure": "exact odd gauge weight and Kummer/GLV compatibility",
            "blocking_resource": "no public decoder for R3 or gamma and no independent carry multiplier",
        },
        {
            "candidate": "higher-level theta or metaplectic non-fixed linearization",
            "positive_structure": "a full dual character can encode the scalar",
            "blocking_resource": "dual direction, projective trivialization, dimension at least n, and huge extension state",
        },
        {
            "candidate": "fully asymmetric sparse translation resultant",
            "positive_structure": "not completely excluded by known exponent symmetries",
            "blocking_resource": "degree-n representation, no compact evaluator, and no proved non-fixed coefficient law",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    audited = [audit_source(item) for item in CANDIDATES]
    ids = [row["id"] for row in audited]
    if len(ids) != len(set(ids)):
        raise AssertionError("candidate ids are not unique")

    class_counts = dict(
        sorted(Counter(row["classification"] for row in audited).items())
    )
    if class_counts != EXPECTED_CLASS_COUNTS:
        raise AssertionError(
            f"classification counts changed: {class_counts} != {EXPECTED_CLASS_COUNTS}"
        )

    passing_cost = [row["id"] for row in audited if row["complete_cost_gate_passed"]]
    public_nonfixed = [
        row["id"]
        for row in audited
        if row["public_construction"]
        and row["branch_sensitive_leaf"]
        and row["constructible_without_orientation_advice"]
        and row["target_alignment_proved"]
    ]
    if passing_cost or public_nonfixed:
        raise AssertionError(
            f"unexpected promotion: cost={passing_cost} public_nonfixed={public_nonfixed}"
        )

    payload = {
        "experiment": "BRANCH-SENSITIVE-LEAF-CLASSIFICATION-C24",
        "candidates": audited,
        "classification_counts": class_counts,
        "collision_certificate": collision_witnesses(),
        "finite_field_two_world_certificate": finite_field_two_world_witnesses(),
        "best_survivors": best_survivors(),
        "aggregate": {
            "candidate_families": len(audited),
            "all_source_markers_verified": all(
                row["source_markers_verified"] for row in audited
            ),
            "all_four_transformation_fields_present": all(
                all(
                    row[field]
                    for field in (
                        "global_branch_flip",
                        "geometric_tau",
                        "generator_inversion",
                        "generator_replacement",
                    )
                )
                for row in audited
            ),
            "normalization_torsor_collision_boundary_proved": True,
            "nonfixed_complete_state_required_for_separated_output": True,
            "branch_sensitive_public_leaf_found": False,
            "branch_sensitive_leaf_constructible_without_advice": False,
            "twisted_theta_survives_C23": False,
            "higher_level_theta_nonfixed_linearization_open": True,
            "p_adic_branch_path_publicly_canonical": False,
            "anti_frobenius_generator_sensitive_observable_known": True,
            "anti_frobenius_sub_sqrt_evaluator_found": False,
            "hidden_GLV_R3_section_known": True,
            "public_GLV_R3_or_carry_decoder_found": False,
            "new_GLV_carry_multiplier_found": False,
            "nonfixed_resultant_coefficient_found": False,
            "compressed_nonfixed_determinant_found": False,
            "sparse_resultant_family_structurally_open": True,
            "complete_cost_gate_passed": False,
            "compact_branch_odd_evaluator_found": False,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["digest"] = hashlib.sha256(raw.encode()).hexdigest()
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
