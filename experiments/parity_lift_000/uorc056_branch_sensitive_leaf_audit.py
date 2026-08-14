#!/usr/bin/env python3
"""C24 source-bound audit of candidate branch-sensitive leaves.

This package uses only committed public research artifacts, symbolic two-world
models, and public finite fields. It accepts no external point, unknown scalar,
wallet, private key, or production target.

The audit distinguishes five mechanism classes:

1. canonical sign-blind descent;
2. determinant/resultant transport of an already non-fixed resource;
3. exact non-fixed objects whose public evaluation still needs a dual state,
   path, seed, or hidden scalar index;
4. fast public sections whose transformation law is dependent on an already
   public factor rather than the desired branch;
5. structurally open mechanisms with unresolved representation cost.

The abstract collision and complete-state theorems are formalized separately in
Ecdlp/Proved/Uorc056BranchSensitiveLeaf.lean.
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


CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "id": "common_basis_frobenius_stickelberger_determinant",
        "source": str(ARCHIVE / "FROBENIUS_STICKELBERGER_DETERMINANT_050.md"),
        "required_markers": [
            "public constant * multiplicative net ratio",
            "independently normalized or twisted rows remain open",
        ],
        "mechanism": "common-basis elliptic evaluation determinant",
        "classification": "transport_only",
        "global_branch_flip": "no independent Hilbert90 branch datum after factorization",
        "geometric_tau": "inherited from the multiplicative elliptic-net ratio",
        "generator_inversion": "no independent orientation source was isolated",
        "generator_replacement": "known integer-matrix pullback preserves the factorization",
        "public_construction": True,
        "branch_sensitive_leaf": False,
        "constructible_without_orientation_advice": True,
        "target_alignment_proved": False,
        "complete_cost_gate_passed": False,
        "blocker": "the determinant factors before any branch extraction",
    },
    {
        "id": "independent_scalar_theta_row_normalization",
        "source": str(ARCHIVE / "INDEPENDENT_THETA_ROW_NORMALIZATION_051.md"),
        "required_markers": [
            "product_i r_i.",
            "Genuinely different theta characteristics or row-dependent section spaces remain open",
        ],
        "mechanism": "diagonal row trivialization plus common basis change",
        "classification": "transport_only",
        "global_branch_flip": "inherits exactly the product of the supplied row factors",
        "geometric_tau": "inherits the row-factor laws",
        "generator_inversion": "inherits the row-factor laws",
        "generator_replacement": "inherits the row-factor laws",
        "public_construction": True,
        "branch_sensitive_leaf": False,
        "constructible_without_orientation_advice": True,
        "target_alignment_proved": False,
        "complete_cost_gate_passed": False,
        "blocker": "any new bit is already present in the explicit row factors",
    },
    {
        "id": "standard_twisted_theta_characteristic_descent",
        "source": str(ARCHIVE / "TWISTED_THETA_CHARACTERISTIC_052.md"),
        "required_markers": [
            "Canonical Frobenius-orbit norm",
            "y(Q)^2/y(G)^2",
        ],
        "mechanism": "Frobenius descent of the three nontrivial genus-one theta characteristics",
        "classification": "canonical_sign_blind",
        "global_branch_flip": "fixed after canonical orbit norm",
        "geometric_tau": "fixed under point negation after orbit norm",
        "generator_inversion": "fixed under G to -G",
        "generator_replacement": "symmetric descent remains generator-blind",
        "public_construction": True,
        "branch_sensitive_leaf": False,
        "constructible_without_orientation_advice": True,
        "target_alignment_proved": False,
        "complete_cost_gate_passed": False,
        "blocker": "the canonical base-field object is the square y^2",
    },
    {
        "id": "standard_level_n_metaplectic_theta_intertwiner",
        "source": str(ARCHIVE / "METAPLECTIC_THETA_INTERTWINER_053.md"),
        "required_markers": [
            "dim H^0(E,L)>=n",
            "Public parity / absolute EDS-residue decoder",
        ],
        "mechanism": "level-n Heisenberg representation and metaplectic basis change",
        "classification": "branch_sensitive_large_or_seeded",
        "global_branch_flip": "non-fixed only after choosing a dual character or linearization",
        "geometric_tau": "projective action does not canonically fix the missing scalar phase",
        "generator_inversion": "depends on the chosen dual direction",
        "generator_replacement": "linear lifts differ by Hom(H,mu_n)",
        "public_construction": False,
        "branch_sensitive_leaf": True,
        "constructible_without_orientation_advice": False,
        "target_alignment_proved": False,
        "complete_cost_gate_passed": False,
        "blocker": "the standard state has dimension at least n and a dual character must be chosen",
    },
    {
        "id": "p_adic_global_branch_continuation",
        "source": str(ARCHIVE / "P_ADIC_GLOBAL_BRANCH_054.md"),
        "required_markers": [
            "Hensel lifting preserves rather than creates an initial square-root choice",
            "formal logarithm distinguish prime-to-p torsion?        no; it vanishes",
        ],
        "mechanism": "formal sigma, canonical lift, Hensel lift, and Coleman continuation",
        "classification": "branch_sensitive_large_or_seeded",
        "global_branch_flip": "both initial plus and minus seeds lift uniquely",
        "geometric_tau": "canonical lifting transports both branches without selecting one",
        "generator_inversion": "no canonical p-adic path selects the marked generator orientation",
        "generator_replacement": "no public covariant path or seed was constructed",
        "public_construction": False,
        "branch_sensitive_leaf": True,
        "constructible_without_orientation_advice": False,
        "target_alignment_proved": False,
        "complete_cost_gate_passed": False,
        "blocker": "local continuation preserves an initial branch seed and nonzero subgroup points are outside the formal kernel",
    },
    {
        "id": "normalized_anti_frobenius_period_seed",
        "source": str(ARCHIVE / "ANTI_FROBENIUS_ORIENTATION_SEED_031.md"),
        "required_markers": [
            "U_[-G](Q)=U_G(-Q)=-U_G(Q).",
            "Explicit quotient-state count",
        ],
        "mechanism": "normalized anti-Frobenius period resolvent U_G(Q)",
        "classification": "branch_sensitive_large_or_seeded",
        "global_branch_flip": "a non-fixed anti-Frobenius line is available, but identification with the Hilbert90 branch is not a compact construction",
        "geometric_tau": "the source records anti-Frobenius sigma, not the geometric tau law required by C24",
        "generator_inversion": "U_[-G](Q)=-U_G(Q)",
        "generator_replacement": "U_[uG](Q)=U_G([u^-1]Q) under the chosen character normalization",
        "public_construction": False,
        "branch_sensitive_leaf": True,
        "constructible_without_orientation_advice": False,
        "target_alignment_proved": False,
        "complete_cost_gate_passed": False,
        "blocker": "evaluation still requires the order-n dual phase or a quotient state of size (n-1)/6",
    },
    {
        "id": "first_absolute_order_n_torsion_jet",
        "source": str(ARCHIVE / "ABSOLUTE_EDS_SECTION_003.md"),
        "required_markers": [
            "fast absolute order-n section exists:",
            "first jet isolates rho_G:",
        ],
        "mechanism": "first invariant derivative of the order-n division polynomial",
        "classification": "public_fast_target_dependent",
        "global_branch_flip": "the exact character law collapses to the already-public point-function bit",
        "geometric_tau": "the invariant tangent derivative uses the public y orientation",
        "generator_inversion": "does not provide an x-only marked-root selector on secp256k1",
        "generator_replacement": "inherits the standard division-polynomial normalization law",
        "public_construction": True,
        "branch_sensitive_leaf": False,
        "constructible_without_orientation_advice": True,
        "target_alignment_proved": False,
        "complete_cost_gate_passed": False,
        "blocker": "the fast absolute section supplies no independent equation for rho_G or parity",
    },
    {
        "id": "hidden_nonlocal_R3_odd_anchor",
        "source": str(ARCHIVE / "NONLOCAL_ODD_ANCHOR_004.md"),
        "required_markers": [
            "odd Kummer/GLV residue aggregate exists:",
            "R3(-Q) = R3(Q)",
        ],
        "mechanism": "odd three-factor EDS-residue aggregate on a GLV orbit",
        "classification": "branch_sensitive_large_or_seeded",
        "global_branch_flip": "odd under the EDS residue gauge, but still hidden",
        "geometric_tau": "Kummer invariant on Q to -Q in the retained setting",
        "generator_inversion": "the aggregate is hidden behind the canonical GLV carry",
        "generator_replacement": "a complete public covariance and evaluator were not constructed",
        "public_construction": False,
        "branch_sensitive_leaf": True,
        "constructible_without_orientation_advice": False,
        "target_alignment_proved": True,
        "complete_cost_gate_passed": False,
        "blocker": "no public decoder for R3 or the GLV carry gamma is known",
    },
    {
        "id": "known_algebraic_GLV_orbit_sections",
        "source": str(ARCHIVE / "GLV_CARRY_SEPARATION_005.md"),
        "required_markers": [
            "Every exact odd section currently available has the same GLV canonical-lift",
            "independent GLV carry multiplier found:",
        ],
        "mechanism": "torsion jets and near-period sections under C3 orbit norm",
        "classification": "public_fast_target_dependent",
        "global_branch_flip": "all exact available odd orbit norms remain in the dependent gR3 class",
        "geometric_tau": "no independent tau-odd equation is produced",
        "generator_inversion": "the same canonical-lift carry accompanies every exact odd section",
        "generator_replacement": "no new multiplier class was found",
        "public_construction": True,
        "branch_sensitive_leaf": False,
        "constructible_without_orientation_advice": True,
        "target_alignment_proved": False,
        "complete_cost_gate_passed": False,
        "blocker": "the public equations are dependent and do not isolate R3 or gamma",
    },
    {
        "id": "field_permutation_GLV_carry_coordinate",
        "source": str(ARCHIVE / "FIELD_PERMUTATION_CARRY_IDENTITY_017.md"),
        "required_markers": [
            "O_beta(x) = -C_beta((beta-1)*x)",
            "not a new inverse-polylogarithmic scalar observable",
        ],
        "mechanism": "canonical field ordering of the x-coordinate GLV orbit",
        "classification": "canonical_sign_blind",
        "global_branch_flip": "independent of the Hilbert90 plus/minus branch",
        "geometric_tau": "x-only and therefore fixed under point negation",
        "generator_inversion": "does not retain generator orientation through x",
        "generator_replacement": "a public field scaling only permutes the known carry frequencies",
        "public_construction": True,
        "branch_sensitive_leaf": False,
        "constructible_without_orientation_advice": True,
        "target_alignment_proved": False,
        "complete_cost_gate_passed": False,
        "blocker": "the candidate is exactly a known field carry after public scaling",
    },
    {
        "id": "sparse_three_term_translation_resultant",
        "source": str(ARCHIVE / "UORC056_SPARSE_TWO_TRANSLATION_RESULTANT_C5.md"),
        "required_markers": [
            "The unresolved minimal object is",
            "A degree-`n` resultant, an `n`-dimensional state",
        ],
        "mechanism": "det(aI+bT_G+cT_Q) and its sparse Sylvester resultant",
        "classification": "open_cost_unresolved",
        "global_branch_flip": "no non-fixed Hilbert90 coefficient or exact branch law has been exhibited",
        "geometric_tau": "not classified for the surviving asymmetric coefficient family",
        "generator_inversion": "only partial affine-exponent symmetries are known",
        "generator_replacement": "the six Möbius exponent symmetries are exact, but target covariance is unresolved",
        "public_construction": False,
        "branch_sensitive_leaf": False,
        "constructible_without_orientation_advice": True,
        "target_alignment_proved": False,
        "complete_cost_gate_passed": False,
        "blocker": "the explicit representation has degree n and no sub-square-root coordinate evaluator or non-fixed coefficient generator is known",
    },
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit_source(candidate: dict[str, Any]) -> dict[str, Any]:
    missing_keys = sorted(REQUIRED_KEYS - candidate.keys())
    extra_keys = sorted(candidate.keys() - REQUIRED_KEYS)
    if missing_keys or extra_keys:
        raise AssertionError(
            f"schema mismatch for {candidate.get('id')}: "
            f"missing={missing_keys} extra={extra_keys}"
        )
    path = ROOT / candidate["source"]
    if not path.is_file():
        raise AssertionError(f"missing source: {path}")
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    missing_markers = [
        marker for marker in candidate["required_markers"] if marker not in text
    ]
    if missing_markers:
        raise AssertionError(
            f"source markers missing for {candidate['id']}: {missing_markers}"
        )
    row = dict(candidate)
    row.pop("required_markers")
    row["source_sha256"] = sha256_bytes(raw)
    row["source_bytes"] = len(raw)
    row["source_markers_verified"] = True
    return row


def collision_witnesses() -> dict[str, Any]:
    orbit_sizes = (2, 3, 5, 7, 11)
    rows = []
    total_decoders = 0
    for size in orbit_sizes:
        worlds = tuple(range(size))
        public_data = {world: 0 for world in worlds}
        successful_global_selectors = 0
        for chosen_output in worlds:
            total_decoders += 1
            if all(chosen_output == world for world in worlds):
                successful_global_selectors += 1
        if len(set(public_data.values())) != 1:
            raise AssertionError("quotient collision fixture is not constant")
        if successful_global_selectors != 0:
            raise AssertionError("an invariant quotient unexpectedly selected an orbit")
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
    primes = (43, 61, 67, 79, 97, 127, 163)
    collisions = 0
    seed_separations = 0
    rows = []
    for prime in primes:
        local_collisions = 0
        for branch in range(1, prime):
            opposite = (-branch) % prime
            if branch == opposite:
                continue
            public_plus = branch * branch % prime
            public_minus = opposite * opposite % prime
            if public_plus != public_minus:
                raise AssertionError("square failed to identify a sign pair")
            local_collisions += 1
            collisions += 1

            # A deterministic aggregate may transport a complete non-fixed
            # state, but separated outputs require the states to differ.
            state_plus, state_minus = branch, opposite
            output_plus, output_minus = state_plus, state_minus
            if output_plus == output_minus:
                raise AssertionError("branch-sensitive state fixture collapsed")
            if state_plus == state_minus:
                raise AssertionError("separated outputs used equal state")
            seed_separations += 1
        rows.append(
            {
                "p": prime,
                "nonzero_sign_collisions": local_collisions,
                "all_seedless_square_data_equal": True,
                "all_separated_outputs_used_nonfixed_state": True,
            }
        )
    return {
        "fields": rows,
        "public_data_collisions": collisions,
        "required_state_separations": seed_separations,
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
            "positive_structure": "not completely excluded by the known exponent symmetries",
            "blocking_resource": "degree-n representation, no sub-square-root evaluator, and no proved non-fixed coefficient law",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    audited = [audit_source(candidate) for candidate in CANDIDATES]
    ids = [row["id"] for row in audited]
    if len(ids) != len(set(ids)):
        raise AssertionError("candidate ids are not unique")

    class_counts = dict(sorted(Counter(row["classification"] for row in audited).items()))
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
            f"unexpected positive promotion: cost={passing_cost} public_nonfixed={public_nonfixed}"
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
