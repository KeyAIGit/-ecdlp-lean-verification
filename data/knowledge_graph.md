# ECDLP verified knowledge graph (rendered view)

> Auto-generated from `VERIFIED.md` + the Lean import surface by `scripts/build_knowledge_graph.py`. Machine source of truth: `data/knowledge_graph.json`. Every theorem below is kernel-checked (no `sorry`, no axioms).

**125 theorems** · **6 barriers** · **113 edges**

By proof method: Mathlib (92), native_decide (18), Mathlib + native_decide (15)

By research area: curve-torsion (70), protocol-soundness (21), generic-hardness (17), primality (5), other (5), reduction (3), attack-resistance (3), params (1)

## Verified theorems by area

### curve-torsion (70)

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
| `secp256k1_Ψ₂Sq_natDegree` | deg Ψ₂Sq = 3` (2-torsion count: `#E[2] ≤ 4`) | Mathlib + native_decide | `DivisionPolynomialDegree.lean` |
| `secp256k1_two_torsion_x_card_le` | ≤ 3 two-torsion `x`-coordinates (`#roots Ψ₂Sq ≤ 3`) | Mathlib | `DivisionPolynomialDegree.lean` |
| `secp256k1_Ψ₂Sq_ne_zero` | Ψ₂Sq ≠ 0` (2-torsion is a proper finite set) | Mathlib | `DivisionPolynomialDegree.lean` |
| `secp256k1_Ψ₃_natDegree` | deg Ψ₃ = 4` (3-torsion count `#E[3] ≤ 9`; GLV-relevant CM torsion) | Mathlib + native_decide | `DivisionPolynomialDegree.lean` |
| `mem_torsionBy_iff_addOrderOf_dvd` | E[n]` = points of order dividing `n` (`P∈E[n] ⟺ ord P ∣ n`) | Mathlib | `Torsion.lean` |
| `torsionBy_dvd_le` | torsion filtration (`E[m] ≤ E[n]` when `m ∣ n`) | Mathlib | `Torsion.lean` |
| `zmod_module_nsmul_eq_zero` | a `ZMod n`-module is killed by `n` (`n • x = 0`) | Mathlib | `Torsion.lean` |
| `torsionBy_eq_top` | the DL group is its own `n`-torsion (`G[n] = ⊤`; cofactor-1 shape) | Mathlib | `Torsion.lean` |
| `torsionBy_eq_ker_nsmul` | E[n] = ker[n]` (torsion = kernel of the multiplication-by-`n` endomorphism) | Mathlib | `Torsion.lean` |
| `zmultiples_le_torsionBy` | ⟨G⟩ ⊆ E[n]` (base-point subgroup lies in the `n`-torsion when `ord G ∣ n`) | Mathlib | `Torsion.lean` |
| `secp256k1_mem_torsionBy_iff_addOrderOf_dvd` | secp256k1 `E[n]` = points of order dividing `n` (curve-named) | Mathlib | `CurveTorsion.lean` |
| `secp256k1_torsionBy_eq_ker_nsmul` | secp256k1 `E[n] = ker[n]` (torsion = kernel of `[n]` on the curve group) | Mathlib | `CurveTorsion.lean` |
| `secp256k1_G_ne_zero` | secp256k1 base point `G ≠ O` (SEC2 generator as a non-zero curve point) | Mathlib | `CurveTorsion.lean` |
| `secp256k1_Ψ₃_ne_zero` | Ψ₃ ≠ 0` (3-torsion is a proper finite set) | Mathlib | `ThreeTorsion.lean` |
| `secp256k1_three_torsion_x_card_le` | ≤ 4 three-torsion `x`-coordinates (`#E[3] ≤ 9`; GLV/CM torsion) | Mathlib | `ThreeTorsion.lean` |
| `secp256k1_c₆` | secp256k1 `c₆ = -6048` (Weierstrass `c₆` invariant) | Mathlib | `Invariants.lean` |
| `secp256k1_c_relation` | discriminant identity `1728·Δ = -c₆` (since `c₄ = 0`) | Mathlib | `Invariants.lean` |
| `secp256k1_torsionBy_dvd_le` | secp256k1 torsion filtration (`E[m] ≤ E[n]` when `m ∣ n`, curve-named) | Mathlib | `CurveTorsion.lean` |
| `secp256k1_zmultiples_le_torsionBy` | secp256k1 `⟨P⟩ ⊆ E[n]` (finite-order point's subgroup is `n`-torsion) | Mathlib | `CurveTorsion.lean` |
| `secp256k1_preΨ₄` | preΨ₄ = 2X⁶ + 280X³ − 784` (secp256k1 4-division polynomial auxiliary) | Mathlib | `FourDivisionPolynomial.lean` |
| `secp256k1_preΨ₄_natDegree` | deg preΨ₄ = 6` (4-torsion bound up the tower) | Mathlib + native_decide | `FourDivisionPolynomial.lean` |
| `secp256k1_preΨ₄_ne_zero` | preΨ₄ ≠ 0` (proper finite root set) | Mathlib | `FourDivisionPolynomial.lean` |
| `secp256k1_glv_preserves_equation` | GLV endomorphism preserves the curve (`(x,y)↦(βx,y)` keeps `Y=X³+7`, via `β³=1`) | Mathlib + native_decide | `GlvEndomorphism.lean` |
| `secp256k1_glv_preserves_nonsingular` | GLV endomorphism preserves nonsingularity (smooth `(x,y)` ↦ smooth `(βx,y)`; `β` a unit) | Mathlib + native_decide | `GlvEndomorphism.lean` |
| `secp256k1_glv_slope_of_X_ne` | GLV slope scaling, secant branch (`x₁≠x₂`: `slope(βx₁,βx₂)=β·slope`, via `β⁻=β`) | Mathlib | `GlvSlope.lean` |
| `secp256k1_glv_slope_of_Y_ne` | GLV slope scaling, tangent branch (doubling `x₁=x₂`: `3(βx)/(2y)=β·slope`) | Mathlib | `GlvSlopeTangent.lean` |
| `secp256k1_glv_slope` | GLV slope scaling, all branches (unconditional: GLV scales the addition slope by exactly `β`) | Mathlib | `GlvSlopeAll.lean` |
| `secp256k1_glv_addX` | GLV β-equivariance of `addX` (`addX(βx₁,βx₂,βℓ)=β·addX`; new `X`-coord scales by `β`) | Mathlib | `GlvAddFormula.lean` |
| `secp256k1_glv_addY` | GLV β-equivariance of `addY` (`addY(βx₁,βx₂,y₁,βℓ)=addY`; `Y`-coord unchanged) | Mathlib | `GlvAddFormula.lean` |
| `glvPoint_add` | GLV map is an additive endomorphism (`glvPoint(P+Q)=glvPoint P+glvPoint Q`, all branches; homomorphism half only — the `glvPoint=[λ]` eigenvalue property is not proved) | Mathlib | `GlvHom.lean` |
| `glvHom` | GLV endomorphism bundled as `AddMonoidHom` (`glvHom : Point →+ Point`; *supporting* — repackages `glvPoint_add`, no new content) | Mathlib | `GlvMonoidHom.lean` |
| `secp256k1_glv_cube_relation` | GLV endomorphism is a primitive cube root of unity (`φ+φ+1=0`: `glvPoint(P)+glvPoint(P)+P=0` for all `P`; the CM / `End(E)` structure behind GLV — reached with no `λ`, no point-counting) | Mathlib | `GlvCubeRelation.lean` |
| `secp256k1_glv_preserves_torsion` | GLV endomorphism preserves `n`-torsion (`glvPoint` maps `E[n]→E[n]`; restricts to an endomorphism of the torsion, still `φ+φ+1=0` there — the scene where `[λ]` lives) | Mathlib | `GlvTorsion.lean` |
| `glvHom_minpoly` | GLV endomorphism satisfies its minimal polynomial in `End(E)` (operator form: `glvHom∘glvHom+glvHom+id=0` as `AddMonoidHom`s — `φ+φ+1=0` in the endomorphism ring, composable with Mathlib's hom API; *alternate/operator form* of `secp256k1_glv_cube_relation`) | Mathlib | `GlvMinPoly.lean` |
| `glvPoint_cube_eq_id` | GLV endomorphism has order dividing 3 (`glvPoint³=id`: iterating `(x,y)↦(βx,y)` scales `x` by `β³=1`; the CM automorphism is order-3) | Mathlib | `GlvAutomorphism.lean` |
| `glvPoint_bijective` | GLV endomorphism is an automorphism (`glvPoint` is bijective — `glvPoint` is its two-sided inverse, from `glvPoint³=id`) | Mathlib | `GlvAutomorphism.lean` |
| `secp256k1_preΨ₅_natDegree` | secp256k1 5-division polynomial has degree 12 (`deg(ψ₅=preΨ' 5)=(5−1)/2=12`; instantiates Mathlib's general `natDegree_preΨ'` at `n=5`) | Mathlib + native_decide | `FiveTorsion.lean` |
| `secp256k1_preΨ₅_ne_zero` | 5-division polynomial is nonzero (deg 12 ⇒ `ψ₅≠0`; 5-torsion `x`-coords are a proper finite set) | Mathlib | `FiveTorsion.lean` |
| `secp256k1_five_torsion_x_card_le` | ≤ 12 five-torsion `x`-coordinates (`#E[5]≤25`; roots of the odd division polynomial `ψ₅` are the order-5 `x`-coords, consistent with `E[5]≅(ℤ/5)`) | Mathlib | `FiveTorsion.lean` |

### protocol-soundness (21)

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
| `schnorr_batch_verify` | batch Schnorr verification (per-signature challenges `(∑sᵢ)G=∑Rᵢ+∑cᵢPᵢ`) | Mathlib | `DlogCompleteness.lean` |
| `elgamal_rerandomize_decrypt` | ElGamal ciphertext re-randomization (mixnet unlinkability) | Mathlib | `DlogPrimitives.lean` |
| `elgamal_additively_homomorphic` | ElGamal additive homomorphism (e-voting homomorphic tally) | Mathlib | `DlogPrimitives.lean` |
| `pedersen_vector_homomorphic` | vector Pedersen commitment homomorphism (Bulletproofs / confidential tx) | Mathlib | `DlogPrimitives.lean` |
| `adaptor_complete` | adaptor signature completeness (atomic swaps / Lightning PTLC) | Mathlib | `DlogCompleteness.lean` |

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

### primality (5)

| theorem | claim | method | file |
|---|---|---|---|
| `orderOf_eq_card_of_prime` | prime-order ⇒ generator (no small subgroup) | Mathlib | `PrimeOrder.lean` |
| `secp256k1_p_prime` | secp256k1 field prime `p` is prime (full Pratt certificate) | Mathlib + native_decide | `Secp256k1PrimeP.lean` |
| `secp256k1_n_prime` | secp256k1 group order `n` is prime (full Pratt certificate) | Mathlib + native_decide | `Secp256k1PrimeN.lean` |
| `secp256k1_odd_preΨ_natDegree` | deg(ψₙ)=(n−1)/2` for all odd `n` coprime to `p` (uniform division-polynomial degree; generalizes the `Ψ₃`/`ψ₅` per-level facts via Mathlib's `natDegree_preΨ'`) | Mathlib | `OddTorsionBound.lean` |
| `secp256k1_odd_torsion_x_card_le` | ≤ `(n−1)/2` odd-`n`-torsion `x`-coordinates (uniform `#E[n]≤n` for every odd `n` coprime to `p`; the general statement behind the 3-/5-torsion nodes) | Mathlib | `OddTorsionBound.lean` |

### other (5)

| theorem | claim | method | file |
|---|---|---|---|
| `collision_zmod` | collision equation, `ZMod` subtractive form `(a−c)=x(d−b) | Mathlib | `CollisionEquation.lean` |
| `collision_recovers_log` | discrete-log recovery `x=(a−c)(d−b)⁻` (collision solve, `d−b` a unit) | Mathlib | `CollisionEquation.lean` |
| `dlog_unique` | discrete log well-defined mod `n` (`g^x=g^y ⇒ x≡y`) | Mathlib | `CollisionEquation.lean` |
| `taproot_tweak_verify` | Taproot key-tweak verification (BIP-341 key-path spend, `Q=P+t·G`) | Mathlib | `DlogCompleteness.lean` |
| `secp256k1_c₆_ne_zero` | secp256k1 `c₆ ≠ 0` (`-6048 ≢ 0 mod p`) | native_decide | `Invariants.lean` |

### reduction (3)

| theorem | claim | method | file |
|---|---|---|---|
| `projection` | Pohlig–Hellman: projection to order-`d` subgroup | Mathlib | `PohligHellman.lean` |
| `component` | Pohlig–Hellman: component depends only on `x mod d | Mathlib | `PohligHellman.lean` |
| `reconstruct` | Pohlig–Hellman: CRT reconstruction | Mathlib | `PohligHellman.lean` |

### attack-resistance (3)

| theorem | claim | method | file |
|---|---|---|---|
| `secp256k1_embedding_degree_gt_100` | secp256k1 has no small embedding degree (`p^k ≢ 1 mod n` for `1≤k≤100`; MOV/FR resistance) | native_decide | `EmbeddingDegree.lean` |
| `secp256k1_trace_ordinary_nonanomalous` | secp256k1 trace of Frobenius: ordinary, non-anomalous, Hasse (`t≠0`, `t≠1`, `t≤4p`; Smart/SSSA + supersingular resistance) | native_decide | `TraceOfFrobenius.lean` |
| `anomalous_iff_trace_one` | anomalous ⟺ trace one (`#E=p ⟺ a_p=1`; Smart/SSSA scope) ³ | Mathlib | `AnomalousScope.lean` |

### params (1)

| theorem | claim | method | file |
|---|---|---|---|
| `p_mod_four` | secp256k1 `p ≡ 3 (mod 4)` (point decompression) | native_decide | `Secp256k1Params.lean` |

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

