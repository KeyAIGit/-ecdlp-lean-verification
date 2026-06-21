# ECDLP Lean formalization (v0)

Machine-checked layer for the ECDLP knowledge graph (corpus folder 15_Knowledge_Graph,
formalization table 07_Formalization/KG_CLAIM_FORMORMALIZATION_v1.csv).

## Layout
- `Ecdlp/Secp256k1Verified.lean` - PROVED on Lean core alone (no Mathlib). 9 theorems
  verified with `native_decide`:
    - `p_special_form`        : p = 2^256 - 2^32 - 977            [sec2-secp256k1-field-005]
    - `glv_lambda_eigenvalue` : lam^2 + lam + 1 ≡ 0 (mod n)        [glv-subgroup-eigenvalue-006]
    - `lambda_is_cube_root`   : lam^3 ≡ 1 (mod n)
    - `beta_field_eigenvalue` : beta^2 + beta + 1 ≡ 0 (mod p)
    - `beta_is_cube_root`     : beta^3 ≡ 1 (mod p)
    - plus `lambda_ne_one`, `lam_lt_n`, `beta_lt_p`
- `Ecdlp/Statements.lean` - Mathlib-dependent formalization TARGETS (proofs pending,
  some `sorry`). One target (`order_dvd_card`) is already discharged by Mathlib.

## Build
Core verified file (no Mathlib):
    lean Ecdlp/Secp256k1Verified.lean
Full project incl. Mathlib targets:
    lake exe cache get && lake build
Toolchain pinned in `lean-toolchain` (Lean v4.31.0); Mathlib rev pinned in `lakefile.toml`.

## Pipeline role
This is stage 2 (formalization agent output) of the autonomous research mechanism.
Each `formalizable` claim in KG_CLAIM_FORMALIZATION_v1.csv becomes a theorem here;
`native_decide` handles concrete arithmetic facts, Mathlib handles structural ones.
