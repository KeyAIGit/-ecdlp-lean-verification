# ECDLP verified knowledge graph (rendered view)

> Auto-generated from `VERIFIED.md` + the Lean import surface by `scripts/build_knowledge_graph.py`. Machine source of truth: `data/knowledge_graph.json`. Every theorem below is kernel-checked (no `sorry`, no axioms).

**74 theorems** · **6 barriers** · **54 edges**

By proof method: Mathlib (48), native_decide (17), Mathlib + native_decide (9)

By research area: curve-torsion (31), generic-hardness (17), protocol-soundness (16), primality (3), reduction (3), attack-resistance (2), params (1), other (1)

## Verified theorems by area

### curve-torsion (31)

| theorem | claim | method | file |
|---|---|---|---|
| `p_special_form` | sec2-secp256k1-field-005 | native_decide | `Secp256k1Verified.lean` |
| `glv_lambda_eigenvalue` | glv-subgroup-eigenvalue-006 | native_decide | `Secp256k1Verified.lean` |
| `glv_eigenvalue_zmod` | glv-subgroup-eigenvalue-006 (ZMod form) | Mathlib | `Statements.lean` |
| `lambda_is_cube_root` | supporting: lambda^3 = 1 mod n | native_decide | `Secp256k1Verified.lean` |
| `lambda_ne_one` | supporting: lambda != 1 | native_decide | `Secp256k1Verified.lean` |
| `beta_field_eigenvalue` | supporting: beta^2+beta+1 = 0 mod p | native_decide | `Secp256k1Verified.lean` |
| `beta_is_cube_root` | supporting: beta^3 = 1 mod p | native_decide | `Secp256k1Verified.lean` |
| `lam_lt_n` | supporting: lam < n | native_decide | `Secp256k1Verified.lean` |
| `beta_lt_p` | supporting: beta < p | native_decide | `Secp256k1Verified.lean` |
| `cofactor_card_mul_index` | sec2-secp256k1-group-006 / sec2-domain-parameters-001 (cofactor) | Mathlib | `Cofactor.lean` |
| `cube_root_of_eigenvalue` | GLV eigenvalue is a cube root of unity (ring form) | Mathlib | `CubeRoot.lean` |
| `secp256k1_Δ_ne_zero` | secp256k1 discriminant nonzero `Δ ≠ 0` in `𝔽_p | native_decide | `Secp256k1Curve.lean` |
| `IsElliptic`` | secp256k1 is a Mathlib `EllipticCurve` (grounds the group law) | Mathlib + native_decide | `Secp256k1Curve.lean` |
| `secp256k1_c₄_eq_zero` | secp256k1 invariant `c₄ = 0 | Mathlib | `Secp256k1Curve.lean` |
| `secp256k1_j_eq_zero` | secp256k1 j-invariant `j = 0` (CM by `ℤ[ζ₃]` ⇒ GLV `λ`) | Mathlib | `Secp256k1Curve.lean` |
| `three_dvd_p_sub_one` | secp256k1 `3 ∣ (p−1)` (cube root `β` in `𝔽_p`) | native_decide | `Secp256k1Params.lean` |
| `three_dvd_n_sub_one` | secp256k1 `3 ∣ (n−1)` (GLV eigenvalue `λ` in `ℤ/n`) | native_decide | `Secp256k1Params.lean` |
| `orderOf_eigenvalue_eq_three` | GLV eigenvalue has order exactly 3 (primitive cube root) | Mathlib | `CubeRoot.lean` |
| `secp256k1_beta_orderOf` | secp256k1 `β` has order 3 in `𝔽_p` (GLV CM generator) | Mathlib + native_decide | `Secp256k1Order.lean` |
| `secp256k1_lambda_orderOf` | secp256k1 `λ` has order 3 in `ℤ/n` (GLV CM generator) | Mathlib + native_decide | `Secp256k1Order.lean` |
| `secp256k1_three_cube_roots_of_unity` | X³ = 1` has exactly 3 roots in `𝔽_p` (GLV cube-root count) | Mathlib + native_decide | `Secp256k1Order.lean` |
| `generator_on_curve` | secp256k1 base point `G` is on the curve (`Gy ≡ Gx³+7 mod p`) | native_decide | `Secp256k1Verified.lean` |
| `secp256k1_generator_equation` | secp256k1 generator is a point of the Mathlib `EllipticCurve | Mathlib + native_decide | `Secp256k1Curve.lean` |
| `secp256k1_generator_nonsingular` | secp256k1 generator is nonsingular (a group element) | Mathlib + native_decide | `Secp256k1Curve.lean` |
| `secp256k1_b₂` | secp256k1 `b₂ = 0` (Weierstrass invariant) | Mathlib | `DivisionPolynomial.lean` |
| `secp256k1_b₄` | secp256k1 `b₄ = 0` (Weierstrass invariant) | Mathlib | `DivisionPolynomial.lean` |
| `secp256k1_b₆` | secp256k1 `b₆ = 28` (Weierstrass invariant) | Mathlib | `DivisionPolynomial.lean` |
| `secp256k1_b₈` | secp256k1 `b₈ = 0` (Weierstrass invariant) | Mathlib | `DivisionPolynomial.lean` |
| `secp256k1_Ψ₂Sq` | secp256k1 2-division polynomial `Ψ₂Sq = 4X³+28` (Mathlib torsion bridge; 2-torsion `x`-coords) | Mathlib | `DivisionPolynomial.lean` |
| `secp256k1_Ψ₃` | secp256k1 3-division polynomial `Ψ₃ = 3X⁴+84X` (3-torsion `E[3]`; the CM-by-ℤ[ζ₃] / GLV structure) | Mathlib | `DivisionPolynomial.lean` |
| `secp256k1_Ψ₂Sq_root_of_two_torsion` | 2-torsion `x`-coordinate ⇒ root of `Ψ₂Sq` (division-polynomial↔torsion, rung 4 forward) | Mathlib | `TwoTorsion.lean` |

### generic-hardness (17)

| theorem | claim | method | file |
|---|---|---|---|
| `order_dvd_card` | pollard-multistage-004 (Lagrange foundation) | Mathlib | `Lagrange.lean` |
| `collisionSet_card_le_one` | generic-group: distinct affine forms collide ≤ once | Mathlib | `GenericGroupBound.lean` |
| `badSet_card_le` | generic-group: ≤ q·q−q colliding logs (union bound) | Mathlib | `GenericGroupBound.lean` |
| `generic_dlog_query_bound` | generic-group DLP lower bound `p ≤ q·q` (Shoup/Nechaev `Ω(√p)`) | Mathlib | `GenericGroupBound.lean` |
| `generic_dlog_sqrt_bound` | generic-group lower bound, square-root form `√p ≤ q | Mathlib | `GenericGroupBound.lean` |
| `generic_success_le` | quantitative Shoup bound: success count ≤ q·q−q+1 | Mathlib | `GenericGroupBound.lean` |
| `two_pow_255_lt_secp256k1_n` | secp256k1 group order `2^255 < n | native_decide | `Secp256k1GenericSecurity.lean` |
| `secp256k1_generic_security` | secp256k1 ≥ 128-bit generic security (`2^127 < q`) | Mathlib + native_decide | `Secp256k1GenericSecurity.lean` |
| `bsgs_decomp` | baby-step giant-step decomposition (`O(√n)` upper bound) | Mathlib | `BabyStepGiantStep.lean` |
| `bsgs_steps_sq_ge` | baby/giant step count `n ≤ ⌈√n⌉` (`Θ(√n)` closure) | Mathlib | `BabyStepGiantStep.lean` |
| `pollard_rho_collision` | Pollard rho: a collision exists within `card` steps (pigeonhole) | Mathlib | `PollardRho.lean` |
| `pollard_rho_periodic` | Pollard rho ρ-shape: sequence is eventually periodic | Mathlib | `PollardRho.lean` |
| `secp256k1_bsgs_steps_le` | secp256k1 BSGS upper bound `⌈√n⌉ ≤ 2^128+1` (tight `√n` security) | native_decide | `Secp256k1GenericSecurity.lean` |
| `eval_add` | model soundness: `eval` is additive on forms (group mult ↔ form add) | Mathlib | `GenericGroupBound.lean` |
| `eval_neg` | model soundness: `eval` respects negation (group inverse ↔ form neg) | Mathlib | `GenericGroupBound.lean` |
| `eval_zero` | model soundness: identity is the zero form | Mathlib | `GenericGroupBound.lean` |
| `collision_modEq` | collision equation `a+xb ≡ c+xd (mod n)` (rho/BSGS solve step) | Mathlib | `CollisionEquation.lean` |

### protocol-soundness (16)

| theorem | claim | method | file |
|---|---|---|---|
| `schnorr_extract` | Schnorr special soundness / witness extraction | Mathlib | `SchnorrSoundness.lean` |
| `schnorr_witness_unique` | Schnorr: extracted witness is unique | Mathlib | `SchnorrSoundness.lean` |
| `pedersen_binding_extract` | Pedersen computational binding ⇒ DLP | Mathlib | `SchnorrSoundness.lean` |
| `secp256k1_schnorr_extract` | Schnorr soundness over secp256k1 scalar field | Mathlib | `SchnorrSoundness.lean` |
| `schnorr_verify` | Schnorr/EdDSA signature correctness (completeness) `s·G = R + c·P | Mathlib | `DlogCompleteness.lean` |
| `dh_agree` | Diffie–Hellman key agreement correctness | Mathlib | `DlogCompleteness.lean` |
| `elgamal_decrypt` | ElGamal decryption correctness | Mathlib | `DlogPrimitives.lean` |
| `pedersen_homomorphic` | Pedersen commitments are additively homomorphic | Mathlib | `DlogPrimitives.lean` |
| `okamoto_extract` | Okamoto identification — 2-witness extraction (soundness) | Mathlib | `DlogAdvanced.lean` |
| `chaum_pedersen_verify` | Chaum–Pedersen DLEQ (equality of discrete logs) — completeness | Mathlib | `DlogAdvanced.lean` |
| `threshold_schnorr_aggregate` | Aggregate Schnorr verification (MuSig/FROST/Taproot multisig) | Mathlib | `DlogCompleteness.lean` |
| `feldman_vss_verify` | Feldman VSS share verification (DKG) | Mathlib | `DlogCompleteness.lean` |
| `adaptor_extract` | Adaptor signature witness extraction (atomic swaps / Lightning) | Mathlib | `SchnorrSoundness.lean` |
| `blind_unblind` | Blind Schnorr signature unblinding (e-cash) | Mathlib | `SchnorrSoundness.lean` |
| `musig_key_aggregate` | MuSig2 coefficient-weighted key aggregation | Mathlib | `DlogCompleteness.lean` |
| `threshold_elgamal_combine` | Threshold ElGamal partial-decryption combination | Mathlib | `DlogCompleteness.lean` |

### primality (3)

| theorem | claim | method | file |
|---|---|---|---|
| `orderOf_eq_card_of_prime` | prime-order ⇒ generator (no small subgroup) | Mathlib | `PrimeOrder.lean` |
| `secp256k1_p_prime` | secp256k1 field prime `p` is prime (full Pratt certificate) | Mathlib + native_decide | `Secp256k1PrimeP.lean` |
| `secp256k1_n_prime` | secp256k1 group order `n` is prime (full Pratt certificate) | Mathlib + native_decide | `Secp256k1PrimeN.lean` |

### reduction (3)

| theorem | claim | method | file |
|---|---|---|---|
| `projection` | Pohlig–Hellman: projection to order-`d` subgroup | Mathlib | `PohligHellman.lean` |
| `component` | Pohlig–Hellman: component depends only on `x mod d | Mathlib | `PohligHellman.lean` |
| `reconstruct` | Pohlig–Hellman: CRT reconstruction | Mathlib | `PohligHellman.lean` |

### attack-resistance (2)

| theorem | claim | method | file |
|---|---|---|---|
| `secp256k1_embedding_degree_gt_100` | secp256k1 has no small embedding degree (`p^k ≢ 1 mod n` for `1≤k≤100`; MOV/FR resistance) | native_decide | `EmbeddingDegree.lean` |
| `secp256k1_trace_ordinary_nonanomalous` | secp256k1 trace of Frobenius: ordinary, non-anomalous, Hasse (`t≠0`, `t≠1`, `t≤4p`; Smart/SSSA + supersingular resistance) | native_decide | `TraceOfFrobenius.lean` |

### params (1)

| theorem | claim | method | file |
|---|---|---|---|
| `p_mod_four` | secp256k1 `p ≡ 3 (mod 4)` (point decompression) | native_decide | `Secp256k1Params.lean` |

### other (1)

| theorem | claim | method | file |
|---|---|---|---|
| `collision_zmod` | collision equation, `ZMod` subtractive form `(a−c)=x(d−b) | Mathlib | `CollisionEquation.lean` |

## Barriers and their verified frontier

Each barrier is a foundation Mathlib lacks. The *frontier* lists verified theorems sitting at that boundary — the realised edge of the missing work.

### B1-cost-model — No oracle / group-operation cost model in Lean

- **Missing:** a general cost / oracle-query model in Mathlib
- **Blocks:** exact Theta running times, index-calculus subexponential bounds, distinguished-point parallel speedups
- **Partial progress:** generic-group Omega(sqrt p) lower bound and O(sqrt n) upper bounds are formalized: their information-theoretic core sidesteps a general cost model (collision count over affine forms a + b*X).
- **Verified frontier:** `generic_dlog_query_bound`, `generic_dlog_sqrt_bound`, `generic_success_le`, `bsgs_decomp`, `pollard_rho_collision`, `secp256k1_generic_security`

### B2-lattice — No lattice-reduction theory in Mathlib

- **Missing:** LLL/BKZ basis reduction, CVP/SVP
- **Blocks:** hidden-number-problem / biased-nonce ECDSA attacks

### B2-quantum — No quantum-circuit cost model in Mathlib

- **Missing:** quantum circuit resource model
- **Blocks:** Shor-style ECDLP resource estimates

### B3-semaev — Summation / Semaev polynomials not in Mathlib

- **Missing:** elliptic summation polynomials S_n over MvPolynomial
- **Blocks:** index calculus on elliptic curves over extension fields
- **Partial progress:** Mathlib has multivariate polynomials but not the S_n.

### B3-weil-pairing — Weil/Tate pairing and isogeny depth missing

- **Missing:** Weil pairing on EllipticCurve, isogeny machinery
- **Blocks:** MOV/FR transfer reductions to finite-field DLP
- **Partial progress:** Mathlib has the curve and isogeny base, not the pairing.
- **Verified frontier:** `secp256k1_j_eq_zero`, `secp256k1_embedding_degree_gt_100`, `secp256k1_trace_ordinary_nonanomalous`, `secp256k1_Ψ₂Sq`, `secp256k1_Ψ₂Sq_root_of_two_torsion`

### B3-point-counting — Concrete point count #E(F_p) = n not kernel-computable

- **Missing:** Schoof / efficient point counting in Mathlib
- **Blocks:** deriving #E = n abstractly for the concrete curve
- **Partial progress:** the concrete order is instead pinned via native_decide / the published value; primality of n is machine-checked (Pratt).
- **Verified frontier:** `secp256k1_n_prime`, `secp256k1_p_prime`

