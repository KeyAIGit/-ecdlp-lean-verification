# Verified claims ledger

Index of machine-checked theorems. Each row maps a knowledge-graph claim to the
Lean theorem that verifies it. `status = proved` means Lean's trusted kernel
accepts the proof with **no `sorry`** (enforced by the CI gate). The
authoritative commit is the latest green `main`; the full operation log lives in
git history and the GitHub Actions tab.

| claim_id | Lean theorem | file | method | status |
|---|---|---|---|---|
| sec2-secp256k1-field-005 | `Secp256k1.p_special_form` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| glv-subgroup-eigenvalue-006 | `Secp256k1.glv_lambda_eigenvalue` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| glv-subgroup-eigenvalue-006 (ZMod form) | `Ecdlp.Targets.glv_eigenvalue_zmod` | Ecdlp/Statements.lean | Mathlib | proved |
| supporting: lambda^3 = 1 mod n | `Secp256k1.lambda_is_cube_root` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| supporting: lambda != 1 | `Secp256k1.lambda_ne_one` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| supporting: beta^2+beta+1 = 0 mod p | `Secp256k1.beta_field_eigenvalue` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| supporting: beta^3 = 1 mod p | `Secp256k1.beta_is_cube_root` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| supporting: lam < n | `Secp256k1.lam_lt_n` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| supporting: beta < p | `Secp256k1.beta_lt_p` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| pollard-multistage-004 (Lagrange foundation) | `order_dvd_card` | Ecdlp/Lagrange.lean | Mathlib | proved |
| sec2-secp256k1-group-006 / sec2-domain-parameters-001 (cofactor) | `Ecdlp.Proved.cofactor_card_mul_index` | Ecdlp/Proved/Cofactor.lean | Mathlib | proved |
| prime-order ⇒ generator (no small subgroup) | `Ecdlp.Proved.orderOf_eq_card_of_prime` | Ecdlp/Proved/PrimeOrder.lean | Mathlib | proved |
| GLV eigenvalue is a cube root of unity (ring form) | `Ecdlp.Proved.cube_root_of_eigenvalue` | Ecdlp/Proved/CubeRoot.lean | Mathlib | proved |
| generic-group: distinct affine forms collide ≤ once | `Ecdlp.GenericGroup.collisionSet_card_le_one` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| generic-group: ≤ q·q−q colliding logs (union bound) | `Ecdlp.GenericGroup.badSet_card_le` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| **generic-group DLP lower bound `p ≤ q·q` (Shoup/Nechaev `Ω(√p)`)** | `Ecdlp.GenericGroup.generic_dlog_query_bound` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| generic-group lower bound, square-root form `√p ≤ q` | `Ecdlp.GenericGroup.generic_dlog_sqrt_bound` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| quantitative Shoup bound: success count ≤ q·q−q+1 | `Ecdlp.GenericGroup.generic_success_le` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| secp256k1 group order `2^255 < n` | `Ecdlp.GenericGroup.two_pow_255_lt_secp256k1_n` | Ecdlp/Proved/Secp256k1GenericSecurity.lean | native_decide | proved |
| **secp256k1 ≥ 128-bit generic security (`2^127 < q`)** | `Ecdlp.GenericGroup.secp256k1_generic_security` | Ecdlp/Proved/Secp256k1GenericSecurity.lean | Mathlib + native_decide | proved¹ |
| baby-step giant-step decomposition (`O(√n)` upper bound) | `Ecdlp.GenericGroup.bsgs_decomp` | Ecdlp/Proved/BabyStepGiantStep.lean | Mathlib | proved |
| baby/giant step count `n ≤ ⌈√n⌉²` (`Θ(√n)` closure) | `Ecdlp.GenericGroup.bsgs_steps_sq_ge` | Ecdlp/Proved/BabyStepGiantStep.lean | Mathlib | proved |
| Pollard rho: a collision exists within `card` steps (pigeonhole) | `Ecdlp.GenericGroup.pollard_rho_collision` | Ecdlp/Proved/PollardRho.lean | Mathlib | proved |
| Pollard rho ρ-shape: sequence is eventually periodic | `Ecdlp.GenericGroup.pollard_rho_periodic` | Ecdlp/Proved/PollardRho.lean | Mathlib | proved |
| secp256k1 BSGS upper bound `⌈√n⌉ ≤ 2^128+1` (tight `√n` security) | `Ecdlp.GenericGroup.secp256k1_bsgs_steps_le` | Ecdlp/Proved/Secp256k1GenericSecurity.lean | native_decide | proved |
| model soundness: `eval` is additive on forms (group mult ↔ form add) | `Ecdlp.GenericGroup.eval_add` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| model soundness: `eval` respects negation (group inverse ↔ form neg) | `Ecdlp.GenericGroup.eval_neg` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| model soundness: identity is the zero form | `Ecdlp.GenericGroup.eval_zero` | Ecdlp/Proved/GenericGroupBound.lean | Mathlib | proved |
| **Schnorr special soundness / witness extraction** | `Ecdlp.Schnorr.schnorr_extract` | Ecdlp/Proved/SchnorrSoundness.lean | Mathlib | proved |
| Schnorr: extracted witness is unique | `Ecdlp.Schnorr.schnorr_witness_unique` | Ecdlp/Proved/SchnorrSoundness.lean | Mathlib | proved |
| **Pedersen computational binding ⇒ DLP** | `Ecdlp.Schnorr.pedersen_binding_extract` | Ecdlp/Proved/SchnorrSoundness.lean | Mathlib | proved |
| Schnorr soundness over secp256k1 scalar field | `Ecdlp.Secp256k1Schnorr.secp256k1_schnorr_extract` | Ecdlp/Proved/SchnorrSoundness.lean | Mathlib | proved¹ |
| **Schnorr/EdDSA signature correctness (completeness)** `s·G = R + c·P` | `Ecdlp.Schnorr.schnorr_verify` | Ecdlp/Proved/DlogCompleteness.lean | Mathlib | proved |
| **Diffie–Hellman key agreement correctness** | `Ecdlp.Schnorr.dh_agree` | Ecdlp/Proved/DlogCompleteness.lean | Mathlib | proved |
| **ElGamal decryption correctness** | `Ecdlp.Schnorr.elgamal_decrypt` | Ecdlp/Proved/DlogPrimitives.lean | Mathlib | proved |
| **Pedersen commitments are additively homomorphic** | `Ecdlp.Schnorr.pedersen_homomorphic` | Ecdlp/Proved/DlogPrimitives.lean | Mathlib | proved |
| **Okamoto identification — 2-witness extraction (soundness)** | `Ecdlp.Schnorr.okamoto_extract` | Ecdlp/Proved/DlogAdvanced.lean | Mathlib | proved |
| **Chaum–Pedersen DLEQ (equality of discrete logs) — completeness** | `Ecdlp.DLEQ.chaum_pedersen_verify` | Ecdlp/Proved/DlogAdvanced.lean | Mathlib | proved |
| **Aggregate Schnorr verification (MuSig/FROST/Taproot multisig)** | `Ecdlp.Schnorr.threshold_schnorr_aggregate` | Ecdlp/Proved/DlogCompleteness.lean | Mathlib | proved |
| **Feldman VSS share verification (DKG)** | `Ecdlp.Schnorr.feldman_vss_verify` | Ecdlp/Proved/DlogCompleteness.lean | Mathlib | proved |
| secp256k1 discriminant nonzero `Δ ≠ 0` in `𝔽_p` | `Ecdlp.Curve.secp256k1_Δ_ne_zero` | Ecdlp/Proved/Secp256k1Curve.lean | native_decide | proved |
| **secp256k1 is a Mathlib `EllipticCurve`** (grounds the group law) | `Ecdlp.Curve.secp256k1.IsElliptic` (instance) | Ecdlp/Proved/Secp256k1Curve.lean | Mathlib + native_decide | proved² |
| secp256k1 invariant `c₄ = 0` | `Ecdlp.Curve.secp256k1_c₄_eq_zero` | Ecdlp/Proved/Secp256k1Curve.lean | Mathlib | proved |
| **secp256k1 j-invariant `j = 0`** (CM by `ℤ[ζ₃]` ⇒ GLV `λ`) | `Ecdlp.Curve.secp256k1_j_eq_zero` | Ecdlp/Proved/Secp256k1Curve.lean | Mathlib | proved² |
| secp256k1 `p ≡ 3 (mod 4)` (point decompression) | `Ecdlp.Curve.p_mod_four` | Ecdlp/Proved/Secp256k1Params.lean | native_decide | proved |
| secp256k1 `3 ∣ (p−1)` (cube root `β` in `𝔽_p`) | `Ecdlp.Curve.three_dvd_p_sub_one` | Ecdlp/Proved/Secp256k1Params.lean | native_decide | proved |
| secp256k1 `3 ∣ (n−1)` (GLV eigenvalue `λ` in `ℤ/n`) | `Ecdlp.Curve.three_dvd_n_sub_one` | Ecdlp/Proved/Secp256k1Params.lean | native_decide | proved |
| **Adaptor signature witness extraction** (atomic swaps / Lightning) | `Ecdlp.Schnorr.adaptor_extract` | Ecdlp/Proved/SchnorrSoundness.lean | Mathlib | proved |
| **Blind Schnorr signature unblinding** (e-cash) | `Ecdlp.Schnorr.blind_unblind` | Ecdlp/Proved/SchnorrSoundness.lean | Mathlib | proved |
| **MuSig2 coefficient-weighted key aggregation** | `Ecdlp.Schnorr.musig_key_aggregate` | Ecdlp/Proved/DlogCompleteness.lean | Mathlib | proved |
| **Threshold ElGamal partial-decryption combination** | `Ecdlp.Schnorr.threshold_elgamal_combine` | Ecdlp/Proved/DlogCompleteness.lean | Mathlib | proved |
| **GLV eigenvalue has order exactly 3** (primitive cube root) | `Ecdlp.Proved.orderOf_eigenvalue_eq_three` | Ecdlp/Proved/CubeRoot.lean | Mathlib | proved |
| **secp256k1 `β` has order 3 in `𝔽_p`** (GLV CM generator) | `Ecdlp.Curve.secp256k1_beta_orderOf` | Ecdlp/Proved/Secp256k1Order.lean | Mathlib + native_decide | proved² |
| **secp256k1 `λ` has order 3 in `ℤ/n`** (GLV CM generator) | `Ecdlp.Curve.secp256k1_lambda_orderOf` | Ecdlp/Proved/Secp256k1Order.lean | Mathlib + native_decide | proved² |
| **`X³ = 1` has exactly 3 roots in `𝔽_p`** (GLV cube-root count) | `Ecdlp.Curve.secp256k1_three_cube_roots_of_unity` | Ecdlp/Proved/Secp256k1Order.lean | Mathlib + native_decide | proved² |
| **secp256k1 base point `G` is on the curve** (`Gy² ≡ Gx³+7 mod p`) | `Secp256k1.generator_on_curve` | Ecdlp/Secp256k1Verified.lean | native_decide | proved |
| **secp256k1 generator is a point of the Mathlib `EllipticCurve`** | `Ecdlp.Curve.secp256k1_generator_equation` | Ecdlp/Proved/Secp256k1Curve.lean | Mathlib + native_decide | proved² |
| **secp256k1 generator is nonsingular** (a group element) | `Ecdlp.Curve.secp256k1_generator_nonsingular` | Ecdlp/Proved/Secp256k1Curve.lean | Mathlib + native_decide | proved² |
| **secp256k1 field prime `p` is prime** (full Pratt certificate) | `Ecdlp.Primality.secp256k1_p_prime` | Ecdlp/Proved/Secp256k1PrimeP.lean | Mathlib + native_decide | proved |
| **secp256k1 group order `n` is prime** (full Pratt certificate) | `Ecdlp.Primality.secp256k1_n_prime` | Ecdlp/Proved/Secp256k1PrimeN.lean | Mathlib + native_decide | proved |
| **Pohlig–Hellman: projection to order-`d` subgroup** | `Ecdlp.PohligHellman.projection` | Ecdlp/Proved/PohligHellman.lean | Mathlib | proved |
| **Pohlig–Hellman: component depends only on `x mod d`** | `Ecdlp.PohligHellman.component` | Ecdlp/Proved/PohligHellman.lean | Mathlib | proved |
| **Pohlig–Hellman: CRT reconstruction** | `Ecdlp.PohligHellman.reconstruct` | Ecdlp/Proved/PohligHellman.lean | Mathlib | proved |
| **secp256k1 has no small embedding degree** (`p^k ≢ 1 mod n` for `1≤k≤100`; MOV/FR resistance) | `Ecdlp.Curve.secp256k1_embedding_degree_gt_100` | Ecdlp/Proved/EmbeddingDegree.lean | native_decide | proved |
| **secp256k1 trace of Frobenius: ordinary, non-anomalous, Hasse** (`t≠0`, `t≠1`, `t²≤4p`; Smart/SSSA + supersingular resistance) | `Ecdlp.Curve.secp256k1_trace_ordinary_nonanomalous` | Ecdlp/Proved/TraceOfFrobenius.lean | native_decide | proved |
| secp256k1 `b₂ = 0` (Weierstrass invariant) | `Ecdlp.Curve.secp256k1_b₂` | Ecdlp/Proved/DivisionPolynomial.lean | Mathlib | proved |
| secp256k1 `b₄ = 0` (Weierstrass invariant) | `Ecdlp.Curve.secp256k1_b₄` | Ecdlp/Proved/DivisionPolynomial.lean | Mathlib | proved |
| secp256k1 `b₆ = 28` (Weierstrass invariant) | `Ecdlp.Curve.secp256k1_b₆` | Ecdlp/Proved/DivisionPolynomial.lean | Mathlib | proved |
| secp256k1 `b₈ = 0` (Weierstrass invariant) | `Ecdlp.Curve.secp256k1_b₈` | Ecdlp/Proved/DivisionPolynomial.lean | Mathlib | proved |
| **secp256k1 2-division polynomial `Ψ₂Sq = 4X³+28`** (Mathlib torsion bridge; 2-torsion `x`-coords) | `Ecdlp.Curve.secp256k1_Ψ₂Sq` | Ecdlp/Proved/DivisionPolynomial.lean | Mathlib | proved |
| **secp256k1 3-division polynomial `Ψ₃ = 3X⁴+84X`** (3-torsion `E[3]`; the CM-by-ℤ[ζ₃] / GLV structure) | `Ecdlp.Curve.secp256k1_Ψ₃` | Ecdlp/Proved/DivisionPolynomial.lean | Mathlib | proved |
| **2-torsion `x`-coordinate ⇒ root of `Ψ₂Sq`** (division-polynomial↔torsion, rung 4 forward) | `Ecdlp.Curve.secp256k1_Ψ₂Sq_root_of_two_torsion` | Ecdlp/Proved/TwoTorsion.lean | Mathlib | proved |
| **collision equation `a+xb ≡ c+xd (mod n)`** (rho/BSGS solve step) | `Ecdlp.GenericGroup.collision_modEq` | Ecdlp/Proved/CollisionEquation.lean | Mathlib | proved |
| collision equation, `ZMod` subtractive form `(a−c)=x(d−b)` | `Ecdlp.GenericGroup.collision_zmod` | Ecdlp/Proved/CollisionEquation.lean | Mathlib | proved |
| **discrete-log recovery `x=(a−c)(d−b)⁻¹`** (collision solve, `d−b` a unit) | `Ecdlp.GenericGroup.collision_recovers_log` | Ecdlp/Proved/CollisionEquation.lean | Mathlib | proved |
| **discrete log well-defined mod `n`** (`g^x=g^y ⇒ x≡y`) | `Ecdlp.GenericGroup.dlog_unique` | Ecdlp/Proved/CollisionEquation.lean | Mathlib | proved |
| **`deg Ψ₂Sq = 3`** (2-torsion count: `#E[2] ≤ 4`) | `Ecdlp.Curve.secp256k1_Ψ₂Sq_natDegree` | Ecdlp/Proved/DivisionPolynomialDegree.lean | Mathlib + native_decide | proved |
| **≤ 3 two-torsion `x`-coordinates** (`#roots Ψ₂Sq ≤ 3`) | `Ecdlp.Curve.secp256k1_two_torsion_x_card_le` | Ecdlp/Proved/DivisionPolynomialDegree.lean | Mathlib | proved |
| `Ψ₂Sq ≠ 0` (2-torsion is a proper finite set) | `Ecdlp.Curve.secp256k1_Ψ₂Sq_ne_zero` | Ecdlp/Proved/DivisionPolynomialDegree.lean | Mathlib | proved |
| **`deg Ψ₃ = 4`** (3-torsion count `#E[3] ≤ 9`; GLV-relevant CM torsion) | `Ecdlp.Curve.secp256k1_Ψ₃_natDegree` | Ecdlp/Proved/DivisionPolynomialDegree.lean | Mathlib + native_decide | proved |
| **batch Schnorr verification** (per-signature challenges `(∑sᵢ)G=∑Rᵢ+∑cᵢPᵢ`) | `Ecdlp.Schnorr.schnorr_batch_verify` | Ecdlp/Proved/DlogCompleteness.lean | Mathlib | proved |
| **ElGamal ciphertext re-randomization** (mixnet unlinkability) | `Ecdlp.Schnorr.elgamal_rerandomize_decrypt` | Ecdlp/Proved/DlogPrimitives.lean | Mathlib | proved |
| **ElGamal additive homomorphism** (e-voting homomorphic tally) | `Ecdlp.Schnorr.elgamal_additively_homomorphic` | Ecdlp/Proved/DlogPrimitives.lean | Mathlib | proved |
| **vector Pedersen commitment homomorphism** (Bulletproofs / confidential tx) | `Ecdlp.Schnorr.pedersen_vector_homomorphic` | Ecdlp/Proved/DlogPrimitives.lean | Mathlib | proved |
| **adaptor signature completeness** (atomic swaps / Lightning PTLC) | `Ecdlp.Schnorr.adaptor_complete` | Ecdlp/Proved/DlogCompleteness.lean | Mathlib | proved |
| **Taproot key-tweak verification** (BIP-341 key-path spend, `Q=P+t·G`) | `Ecdlp.Schnorr.taproot_tweak_verify` | Ecdlp/Proved/DlogCompleteness.lean | Mathlib | proved |
| **`E[n]` = points of order dividing `n`** (`P∈E[n] ⟺ ord P ∣ n`) | `Ecdlp.Torsion.mem_torsionBy_iff_addOrderOf_dvd` | Ecdlp/Proved/Torsion.lean | Mathlib | proved |
| **torsion filtration** (`E[m] ≤ E[n]` when `m ∣ n`) | `Ecdlp.Torsion.torsionBy_dvd_le` | Ecdlp/Proved/Torsion.lean | Mathlib | proved |
| **a `ZMod n`-module is killed by `n`** (`n • x = 0`) | `Ecdlp.Torsion.zmod_module_nsmul_eq_zero` | Ecdlp/Proved/Torsion.lean | Mathlib | proved |
| **the DL group is its own `n`-torsion** (`G[n] = ⊤`; cofactor-1 shape) | `Ecdlp.Torsion.torsionBy_eq_top` | Ecdlp/Proved/Torsion.lean | Mathlib | proved |
| **`E[n] = ker[n]`** (torsion = kernel of the multiplication-by-`n` endomorphism) | `Ecdlp.Torsion.torsionBy_eq_ker_nsmul` | Ecdlp/Proved/Torsion.lean | Mathlib | proved |
| **`⟨G⟩ ⊆ E[n]`** (base-point subgroup lies in the `n`-torsion when `ord G ∣ n`) | `Ecdlp.Torsion.zmultiples_le_torsionBy` | Ecdlp/Proved/Torsion.lean | Mathlib | proved |
| **secp256k1 `E[n]` = points of order dividing `n`** (curve-named) | `Ecdlp.Curve.secp256k1_mem_torsionBy_iff_addOrderOf_dvd` | Ecdlp/Proved/CurveTorsion.lean | Mathlib | proved |
| **secp256k1 `E[n] = ker[n]`** (torsion = kernel of `[n]` on the curve group) | `Ecdlp.Curve.secp256k1_torsionBy_eq_ker_nsmul` | Ecdlp/Proved/CurveTorsion.lean | Mathlib | proved |
| **secp256k1 base point `G ≠ O`** (SEC2 generator as a non-zero curve point) | `Ecdlp.Curve.secp256k1_G_ne_zero` | Ecdlp/Proved/CurveTorsion.lean | Mathlib | proved |
| **`Ψ₃ ≠ 0`** (3-torsion is a proper finite set) | `Ecdlp.Curve.secp256k1_Ψ₃_ne_zero` | Ecdlp/Proved/ThreeTorsion.lean | Mathlib | proved |
| **≤ 4 three-torsion `x`-coordinates** (`#E[3] ≤ 9`; GLV/CM torsion) | `Ecdlp.Curve.secp256k1_three_torsion_x_card_le` | Ecdlp/Proved/ThreeTorsion.lean | Mathlib | proved |
| **secp256k1 `c₆ = -6048`** (Weierstrass `c₆` invariant) | `Ecdlp.Curve.secp256k1_c₆` | Ecdlp/Proved/Invariants.lean | Mathlib | proved |
| **secp256k1 `c₆ ≠ 0`** (`-6048 ≢ 0 mod p`) | `Ecdlp.Curve.secp256k1_c₆_ne_zero` | Ecdlp/Proved/Invariants.lean | native_decide | proved |
| **discriminant identity `1728·Δ = -c₆²`** (since `c₄ = 0`) | `Ecdlp.Curve.secp256k1_c_relation` | Ecdlp/Proved/Invariants.lean | Mathlib | proved |
| **secp256k1 torsion filtration** (`E[m] ≤ E[n]` when `m ∣ n`, curve-named) | `Ecdlp.Curve.secp256k1_torsionBy_dvd_le` | Ecdlp/Proved/CurveTorsion.lean | Mathlib | proved |
| **secp256k1 `⟨P⟩ ⊆ E[n]`** (finite-order point's subgroup is `n`-torsion) | `Ecdlp.Curve.secp256k1_zmultiples_le_torsionBy` | Ecdlp/Proved/CurveTorsion.lean | Mathlib | proved |
| **`preΨ₄ = 2X⁶ + 280X³ − 784`** (secp256k1 4-division polynomial auxiliary) | `Ecdlp.Curve.secp256k1_preΨ₄` | Ecdlp/Proved/FourDivisionPolynomial.lean | Mathlib | proved |
| **`deg preΨ₄ = 6`** (4-torsion bound up the tower) | `Ecdlp.Curve.secp256k1_preΨ₄_natDegree` | Ecdlp/Proved/FourDivisionPolynomial.lean | Mathlib + native_decide | proved |
| **`preΨ₄ ≠ 0`** (proper finite root set) | `Ecdlp.Curve.secp256k1_preΨ₄_ne_zero` | Ecdlp/Proved/FourDivisionPolynomial.lean | Mathlib | proved |
| **anomalous ⟺ trace one** (`#E=p ⟺ a_p=1`; Smart/SSSA scope) ³ | `Ecdlp.Curve.anomalous_iff_trace_one` | Ecdlp/Proved/AnomalousScope.lean | Mathlib | proved |
| **GLV endomorphism preserves the curve** (`(x,y)↦(βx,y)` keeps `Y²=X³+7`, via `β³=1`) | `Ecdlp.Curve.secp256k1_glv_preserves_equation` | Ecdlp/Proved/GlvEndomorphism.lean | Mathlib + native_decide | proved |
| **GLV endomorphism preserves nonsingularity** (smooth `(x,y)` ↦ smooth `(βx,y)`; `β` a unit) | `Ecdlp.Curve.secp256k1_glv_preserves_nonsingular` | Ecdlp/Proved/GlvEndomorphism.lean | Mathlib + native_decide | proved |
| **GLV slope scaling, secant branch** (`x₁≠x₂`: `slope(βx₁,βx₂)=β²·slope`, via `β⁻¹=β²`) | `Ecdlp.Curve.secp256k1_glv_slope_of_X_ne` | Ecdlp/Proved/GlvSlope.lean | Mathlib | proved |
| **GLV slope scaling, tangent branch** (doubling `x₁=x₂`: `3(βx)²/(2y)=β²·slope`) | `Ecdlp.Curve.secp256k1_glv_slope_of_Y_ne` | Ecdlp/Proved/GlvSlopeTangent.lean | Mathlib | proved |
| **GLV slope scaling, all branches** (unconditional: GLV scales the addition slope by exactly `β²`) | `Ecdlp.Curve.secp256k1_glv_slope` | Ecdlp/Proved/GlvSlopeAll.lean | Mathlib | proved |
| **GLV β-equivariance of `addX`** (`addX(βx₁,βx₂,β²ℓ)=β·addX`; new `X`-coord scales by `β`) | `Ecdlp.Curve.secp256k1_glv_addX` | Ecdlp/Proved/GlvAddFormula.lean | Mathlib | proved |
| **GLV β-equivariance of `addY`** (`addY(βx₁,βx₂,y₁,β²ℓ)=addY`; `Y`-coord unchanged) | `Ecdlp.Curve.secp256k1_glv_addY` | Ecdlp/Proved/GlvAddFormula.lean | Mathlib | proved |
| **GLV map is an additive endomorphism** (`glvPoint(P+Q)=glvPoint P+glvPoint Q`, all branches; homomorphism half only — the `glvPoint=[λ]` eigenvalue property is **not** proved) | `Ecdlp.Curve.glvPoint_add` | Ecdlp/Proved/GlvHom.lean | Mathlib | proved |
| GLV endomorphism bundled as `AddMonoidHom` (`glvHom : Point →+ Point`; *supporting* — repackages `glvPoint_add`, no new content) | `Ecdlp.Curve.glvHom` | Ecdlp/Proved/GlvMonoidHom.lean | Mathlib | proved |
| **GLV endomorphism is a primitive cube root of unity** (`φ²+φ+1=0`: `glvPoint²(P)+glvPoint(P)+P=0` for all `P`; the CM / `End(E)` structure behind GLV — reached with **no `λ`, no point-counting**) | `Ecdlp.Curve.secp256k1_glv_cube_relation` | Ecdlp/Proved/GlvCubeRelation.lean | Mathlib | proved |
| **GLV endomorphism preserves `n`-torsion** (`glvPoint` maps `E[n]→E[n]`; restricts to an endomorphism of the torsion, still `φ²+φ+1=0` there — the scene where `[λ]` lives) | `Ecdlp.Curve.secp256k1_glv_preserves_torsion` | Ecdlp/Proved/GlvTorsion.lean | Mathlib | proved |
| **GLV endomorphism satisfies its minimal polynomial in `End(E)`** (operator form: `glvHom∘glvHom+glvHom+id=0` as `AddMonoidHom`s — `φ²+φ+1=0` in the endomorphism ring, composable with Mathlib's hom API; *alternate/operator form* of `secp256k1_glv_cube_relation`) | `Ecdlp.Curve.glvHom_minpoly` | Ecdlp/Proved/GlvMinPoly.lean | Mathlib | proved |
| **GLV endomorphism has order dividing 3** (`glvPoint³=id`: iterating `(x,y)↦(βx,y)` scales `x` by `β³=1`; the CM automorphism is order-3) | `Ecdlp.Curve.glvPoint_cube_eq_id` | Ecdlp/Proved/GlvAutomorphism.lean | Mathlib | proved |
| **GLV endomorphism is an automorphism** (`glvPoint` is bijective — `glvPoint²` is its two-sided inverse, from `glvPoint³=id`) | `Ecdlp.Curve.glvPoint_bijective` | Ecdlp/Proved/GlvAutomorphism.lean | Mathlib | proved |
| **secp256k1 5-division polynomial has degree 12** (`deg(ψ₅=preΨ' 5)=(5²−1)/2=12`; instantiates Mathlib's general `natDegree_preΨ'` at `n=5`) | `Ecdlp.Curve.secp256k1_preΨ₅_natDegree` | Ecdlp/Proved/FiveTorsion.lean | Mathlib + native_decide | proved |
| **5-division polynomial is nonzero** (deg 12 ⇒ `ψ₅≠0`; 5-torsion `x`-coords are a proper finite set) | `Ecdlp.Curve.secp256k1_preΨ₅_ne_zero` | Ecdlp/Proved/FiveTorsion.lean | Mathlib | proved |
| **≤ 12 five-torsion `x`-coordinates** (`#E[5]≤25`; roots of the odd division polynomial `ψ₅` are the order-5 `x`-coords, consistent with `E[5]≅(ℤ/5)²`) | `Ecdlp.Curve.secp256k1_five_torsion_x_card_le` | Ecdlp/Proved/FiveTorsion.lean | Mathlib | proved |
| **`deg(ψₙ)=(n²−1)/2` for all odd `n` coprime to `p`** (uniform division-polynomial degree; generalizes the `Ψ₃`/`ψ₅` per-level facts via Mathlib's `natDegree_preΨ'`) | `Ecdlp.Curve.secp256k1_odd_preΨ_natDegree` | Ecdlp/Proved/OddTorsionBound.lean | Mathlib | proved |
| **≤ `(n²−1)/2` odd-`n`-torsion `x`-coordinates** (uniform `#E[n]≤n²` for every odd `n` coprime to `p`; the general statement behind the 3-/5-torsion nodes) | `Ecdlp.Curve.secp256k1_odd_torsion_x_card_le` | Ecdlp/Proved/OddTorsionBound.lean | Mathlib | proved |
| **point-level 2-torsion criterion `2•P=0 ⟺ y=0`** (both-directions `ψ₂↔E[2]` bridge at the point level — the criterion Mathlib records only as a TODO; upgrades the forward-only `Ψ₂Sq`-root fact) | `Ecdlp.Curve.secp256k1_two_nsmul_eq_zero_iff` | Ecdlp/Proved/TwoTorsionPoint.lean | Mathlib + native_decide | proved |
| **GLV endomorphism is *not* the identity** (`glvHom ≠ id`, witnessed by `β·Gx ≠ Gx` on the base point — rules out the degenerate case, so with `glvHom³=id` and `φ²+φ+1=0` the order in `Aut(E)` is *exactly* 3: `glvHom` is a **primitive** cube root of unity ⇒ `ℤ[ω]↪End(E)`, genuine CM) | `Ecdlp.Curve.secp256k1_glvHom_ne_id` | Ecdlp/Proved/GlvOrderThree.lean | Mathlib + native_decide | proved |
| **point-level trace-zero identity `P+λP+λ²P=0`** (pointwise reading of `glvHom_minpoly`: `X²+X+1` applied to any `P` returns `O`; the three points of a `⟨λ⟩`-orbit sum to zero) | `Ecdlp.Curve.secp256k1_glvPoint_orbit_sum` | Ecdlp/Proved/GlvOrderThree.lean | Mathlib | proved |
| **fixed locus of the GLV automorphism `φ(P)=P ⟺ x=0`** (`β·x=x ⇒ (β−1)x=0 ⇒ x=0` since `β≠1`; the ramification locus of `E→E/⟨φ⟩`, pins the order-3 automorphism's action together with `glvHom≠id`) | `Ecdlp.Curve.secp256k1_glvPoint_fixed_iff` | Ecdlp/Proved/GlvFixedLocus.lean | Mathlib + native_decide | proved |
| **`φ`-fixed points are 3-torsion `φP=P ⇒ 3•P=0`** (composes the trace-zero identity with the fixed hypothesis: `φP=P` collapses `P+φP+φ²P=O` to `3P=O`; the group-law form of `ker(φ−1)⊆E[3]`, `N(ω−1)=3`) | `Ecdlp.Curve.secp256k1_glvPoint_fixed_three_torsion` | Ecdlp/Proved/GlvFixedLocus.lean | Mathlib | proved |
| **secp256k1 7-division polynomial has degree 24** (`deg(ψ₇=preΨ' 7)=(7²−1)/2=24`; instantiates Mathlib's general `natDegree_preΨ'` at `n=7`) | `Ecdlp.Curve.secp256k1_preΨ₇_natDegree` | Ecdlp/Proved/SevenTorsion.lean | Mathlib + native_decide | proved |
| **7-division polynomial is nonzero** (deg 24 ⇒ `ψ₇≠0`; 7-torsion `x`-coords are a proper finite set) | `Ecdlp.Curve.secp256k1_preΨ₇_ne_zero` | Ecdlp/Proved/SevenTorsion.lean | Mathlib | proved |
| **≤ 24 seven-torsion `x`-coordinates** (`#E[7]≤49`; roots of the odd division polynomial `ψ₇` are the order-7 `x`-coords, consistent with `E[7]≅(ℤ/7)²`; the concrete `n=7` level of the uniform odd bound) | `Ecdlp.Curve.secp256k1_seven_torsion_x_card_le` | Ecdlp/Proved/SevenTorsion.lean | Mathlib | proved |
| **GLV eigenvalue property `φ=[k]`, conditional on cyclicity** (if `E(𝔽_p)` is cyclic then `glvHom` is multiplication by a fixed `k:ℤ` with `(k²+k+1)•P=0` for all `P` — the geometric `β`-action *is* scalar `[λ]`; a genuine **reduction** isolating the one deep missing input, point-counting `#E=n`, as the explicit `[IsAddCyclic]` hypothesis) | `Ecdlp.Curve.secp256k1_glvHom_eq_zsmul` | Ecdlp/Proved/GlvEigenvalue.lean | Mathlib (`map_cyclic`) | proved |
| **odd torsion ∩ 2-torsion = {O}** (odd `n`: a point killed by both `n` and `2` is `O`, since `addOrderOf P ∣ gcd(n,2)=1`; node **N12** of the `ψₙ↔E[n]` bridge decomposition — a reachable leaf toward the deep torsion correspondence, see `notes/DIVISION_POLY_TORSION_MAP.md`) | `Ecdlp.Curve.secp256k1_odd_two_torsion_disjoint` | Ecdlp/Proved/TorsionCoprime.lean | Mathlib | proved |
| **`[n]`-numerator strictly dominates its denominator** (`deg ΨSqₙ = n²−1 < n² = deg Φₙ`; so the rational map `x∘[n]=Φₙ/ψₙ²` attains degree `n²` at the numerator — the differential-free **Route-B** crux for `deg[n]=n²`, modulo coprimality; see `notes/SEPARABILITY_ROUTES.md`) | `Ecdlp.Curve.secp256k1_ΨSq_natDegree_lt_Φ` | Ecdlp/Proved/NumeratorDominates.lean | Mathlib (`natDegree_Φ`,`natDegree_ΨSq`) | proved |
| **`Ψ₂Sq` and `Ψ₃` are coprime** (`IsCoprime (4X³+28) (3X⁴+84X)` — "no point is both 2- and 3-torsion", where `Δ≠0` enters; node **L5** of the B1 coprimality plan, proved by an explicit CAS-computed Bézout certificate over `𝔽_p`; first hand-built sub-lemma toward `gcd(Φₙ,ψₙ²)=1`) | `Ecdlp.Curve.secp256k1_isCoprime_Ψ₂Sq_Ψ₃` | Ecdlp/Proved/CoprimePsi2Psi3.lean | Bézout certificate + native_decide | proved |
| **`Ψ₃` and `preΨ₄` are coprime** (`IsCoprime (3X⁴+84X) (2X⁶+280X³−784)` — "no point is both 3- and 4-torsion", the second place `Δ≠0` enters; node **L6** of B1, CAS-computed Bézout certificate over `𝔽_p`) | `Ecdlp.Curve.secp256k1_isCoprime_Ψ₃_preΨ₄` | Ecdlp/Proved/CoprimePsi3PrePsi4.lean | Bézout certificate + native_decide | proved |
| **`Ψ₂Sq` and `preΨ₄` are coprime** (`IsCoprime (4X³+28) (2X⁶+280X³−784)` — "no point is both 2- and *primitive* 4-torsion"; completes the pairwise low-torsion disjointness with L5/L6, third manifestation of `Δ≠0`; node **L6b** of B1, CAS-computed Bézout certificate over `𝔽_p`) | `Ecdlp.Curve.secp256k1_isCoprime_Ψ₂Sq_preΨ₄` | Ecdlp/Proved/CoprimePsi2PrePsi4.lean | Bézout certificate + native_decide | proved |
| **`IsCoprime` ↔ no common root** (over a field `k`, non-coprime `f,g ∈ k[X]` ⇒ a genuine common root in any algebraically-closed extension, + easy converse — the field↔`k̄` bridge B1 consumes, **independent of the open L4 TODO**; node **L1** of B1, general/upstreamable) | `Ecdlp.DivisionPoly.exists_common_root_of_not_isCoprime` | Ecdlp/Proved/CoprimeCommonRoot.lean | Mathlib (`EuclideanDomain.gcd`, `IsAlgClosed.exists_root`, `degree_map_eq_of_injective`) | proved |
| **GLV eigenvalue ⇒ scalar action** (an endomorphism `φ` fixing a cyclic group's generator as a `λ`-eigenvector acts as `[λ]` on the whole subgroup: `φ x = λ•x`; the algebraic core of the GLV speed-up used on secp256k1, promoted from stem `glv_root_mod_n_condition_008`) | `Ecdlp.Curve.glv_root_mod_n_condition` | Ecdlp/Proved/GlvScalarAction.lean | Mathlib (`map_zsmul`, `smul_comm`) | proved |
| **`r`-general elliptic-sequence identity ⇐ its `r=1` case** (`isEllSequence_of_rec_one`: any `W:ℤ→R` over a `CommRing` satisfying the two-index recurrence is an `IsEllSequence`; pure `linear_combination`, **no `W 1=1` needed** — more general than the roadmap expected. Isolates all remaining content of the open Mathlib TODO "`normEDS` is elliptic" into the `r=1` master recurrence; **first upstream-Mathlib stepping stone** toward it, see `notes/B1_TRACTABILITY_MAP.md`) | `Ecdlp.EDS.isEllSequence_of_rec_one` | Ecdlp/Proved/EllSequenceRecOne.lean | Mathlib (`IsEllSequence`) + `linear_combination` | proved |
| **Somos-4 recurrence for `normEDS`** (`normEDS_somos4`: `normEDS(m+2)·normEDS(m−2) = b²·normEDS(m+1)·normEDS(m−1) − c·normEDS(m)²` for all `m:ℤ` over any `CommRing` — the `n=2` slice of Ward's master recurrence and the companion identity for the open Mathlib TODO "`normEDS` is elliptic"; single-parameter `normEDSRec'` strong induction, `b²`-cancellation over the domain `MvPolynomial (Fin 3) ℤ`, reflected by `normEDS_neg` and transported to any `CommRing` via `map_normEDS`; **second upstream-Mathlib stepping stone** toward L4, see `notes/L4_WARD_INDUCTION.md`) | `Ecdlp.NormEDS.normEDS_somos4` | Ecdlp/Proved/NormEDSSomos4.lean | Mathlib (`normEDSRec'`, `normEDS_even`/`normEDS_odd`, `map_normEDS`) + `linear_combination` | proved |
| **Dependence relation recovers the discrete log** (`jacobson_xedni_dependence_recovers_log`: for `Q = x•P` in any `AddCommGroup`, a nontrivial integer relation `a•P + b•Q = 0` with `b` a unit mod `n = addOrderOf P` pins the discrete log `x ≡ -a·b⁻¹ (mod n)` — the neutral algebraic core of the Jacobson–Xedni point-dependence idea; **Layer-3 generated** from corpus claim `jacobson-xedni-dependence-recovers-log-003`, closed via `addOrderOf_dvd_iff_zsmul_eq_zero` + `ZMod` arithmetic) | `Ecdlp.jacobson_xedni_dependence_recovers_log` | Ecdlp/Proved/DependenceRecoversLog.lean | Mathlib (`addOrderOf_dvd_iff_zsmul_eq_zero`, `ZMod.intCast_zmod_eq_zero_iff_dvd`, `Ring.inverse`) | proved |
| **`ψ 3` evaluated at a secp256k1 point = `3x⁴+84x`** (`secp256k1_psi3_evalEval`: the bivariate 3-division polynomial reduces to the concrete univariate on the curve; the bookkeeping half of the n=3 torsion bridge) | `Ecdlp.Curve.secp256k1_psi3_evalEval` | Ecdlp/Proved/ThreeTorsionBridge.lean | Mathlib (`ψ_three`, `evalEval_C`) + `secp256k1_Ψ₃` | proved |
| **Point-level 3-torsion bridge `3•P = 0 ⟺ ψ₃(P)=0`** (`secp256k1_three_nsmul_eq_zero_iff`: for a nonzero affine `P=(x,y)` on secp256k1, the group relation `3•P=0` holds iff the 3-division polynomial vanishes — the full `ψ₃ ↔ E[3]` equivalence, upgrading the forward-only `Ψ₃`-root fact; original elementary proof via the doubling identity `addX−x = −(3x⁴+84x)/(4y²)`, the n=3 analogue of the n=2 bridge) | `Ecdlp.Curve.secp256k1_three_nsmul_eq_zero_iff` | Ecdlp/Proved/ThreeTorsionBridge.lean | Mathlib (`Affine.Point` group law, `slope`/`addX`/`addY`/`negY`) + `linear_combination` | proved |
| **3-torsion `x`-coordinate set is finite** (`secp256k1_threeTorsionX_finite`: the set `threeTorsionX = {x | ∃ y h, 3•(x,y)=0}` of `x`-coordinates of nonzero 3-torsion points is finite — via the bridge it embeds into the roots of `Ψ₃`) | `Ecdlp.Curve.secp256k1_threeTorsionX_finite` | Ecdlp/Proved/ThreeTorsionCard.lean | bridge + Mathlib (`Set.Finite.subset`, `Multiset.toFinset`) | proved |
| **≤ 4 nonzero 3-torsion `x`-coordinates on secp256k1** (`secp256k1_threeTorsionX_ncard_le`: `threeTorsionX.ncard ≤ 4` — upgrades the forward-only degree-4 *root* bound to a bound on the actual *set* of 3-torsion `x`-values, the set-level payoff of the n=3 bridge) | `Ecdlp.Curve.secp256k1_threeTorsionX_ncard_le` | Ecdlp/Proved/ThreeTorsionCard.lean | bridge + `secp256k1_three_torsion_x_card_le` + Mathlib (`Set.ncard_le_ncard`, `Multiset.toFinset_card_le`) | proved |
| *(alternate/supporting, n=3 bridge)* concrete iff `3•P=0 ⟺ 3x⁴+84x=0` (`secp256k1_three_nsmul_eq_zero_iff_poly`), root-form iff (`secp256k1_three_nsmul_eq_zero_iff_eval`), `Ψ₃`/torsion-poly eval lemmas (`secp256k1_Ψ₃_eval`, `secp256k1_eval_threeTorsionPoly`), point↦root map (`secp256k1_three_torsion_x_mem_Ψ₃_roots`), its set form (`secp256k1_threeTorsionX_subset_Ψ₃_roots`), and the dedup card bound (`secp256k1_Ψ₃_roots_toFinset_card_le`) | `Ecdlp.Curve.*` | Ecdlp/Proved/ThreeTorsionCard.lean | bridge + Mathlib | proved |
| **`ψ 5` at a secp256k1 point reduces to a concrete degree-12 univariate** (`secp256k1_psi5_evalEval`: on the curve `y²=x³+7`, `(ψ 5).evalEval x y = 5x¹²+2660x⁹−11760x⁶−548800x³−614656` — a polynomial in `x³`, reflecting the `j=0`/CM structure; via the master `ψ_odd` recursion `ψ₅ = preΨ₄·ψ₂⁴ − Ψ₃³`, the bookkeeping half of the n=5 torsion bridge) | `Ecdlp.Curve.secp256k1_psi5_evalEval` | Ecdlp/Proved/FiveTorsionBridge.lean | Mathlib (`ψ_odd`/`ψ_four`/`ψ_three`/`ψ_two`) + `linear_combination` | proved |
| **Point-level 5-torsion bridge `5•P = 0 ⟺ ψ₅(P)=0`** (`secp256k1_five_nsmul_eq_zero_iff`: for a nonzero affine `P=(x,y)` on secp256k1, `5•P=0` holds iff the 5-division polynomial vanishes — the full `ψ₅ ↔ E[5]` equivalence, the n=5 analogue of the n=2/n=3 bridges; original elementary proof via the route `5•P=0 ⟺ x(2P)=x(3P) ⟺ ψ₅=0`, the core `x`-difference identity designed by a sympy-verified certificate and re-checked by the Lean kernel; reuses the merged n=2/n=3 bridges to close the degenerate branches) | `Ecdlp.Curve.secp256k1_five_nsmul_eq_zero_iff` | Ecdlp/Proved/FiveTorsionBridge.lean | Mathlib (`Affine.Point` group law, `add_self_of_Y_ne`/`add_some`/`slope`) + `linear_combination` + n=2/n=3 bridges | proved |
| *(alternate/supporting, n=5 bridge)* the core `x(2P)=x(3P) ⟺ ψ₅=0` field-algebra identity (`five_core`) and the concrete eval lemmas `secp256k1_preΨ₄_eval` (`= 2x⁶+280x³−784`), `secp256k1_psi2_evalEval` (`= 2y`) | `Ecdlp.Curve.*` | Ecdlp/Proved/FiveTorsionBridge.lean | Mathlib + `linear_combination` | proved |
| **`ψ 7` at a secp256k1 point reduces to a concrete degree-24 univariate** (`secp256k1_psi7_evalEval`: on the curve `y²=x³+7`, `(ψ 7).evalEval x y = 7x²⁴+27608x²¹−2101904x¹⁸−284585728x¹⁵−2228742656x¹²−26142548992x⁹−330576748544x⁶−661153497088x³+377801998336`; via `ψ_odd 3` (`ψ₇ = ψ₅·ψ₃³ − ψ₂·ψ₄³`), the bookkeeping half of the n=7 torsion bridge) | `Ecdlp.Curve.secp256k1_psi7_evalEval` | Ecdlp/Proved/SevenTorsionBridge.lean | Mathlib (`ψ_odd`) + `linear_combination` | proved |
| **Point-level 7-torsion bridge `7•P = 0 ⟺ ψ₇(P)=0`** (`secp256k1_seven_nsmul_eq_zero_iff`: for a nonzero affine `P=(x,y)` on secp256k1, `7•P=0` holds iff the 7-division polynomial vanishes — the full `ψ₇ ↔ E[7]` equivalence, the n=7 analogue of the n=2/n=3/n=5 bridges; original elementary proof via the route `7•P=0 ⟺ x(3P)=x(4P) ⟺ ψ₇=0`, the core slope-algebra identity designed by a sympy-verified certificate and re-checked by the Lean kernel; reuses the merged n=3 bridge to close the 3-torsion branch) | `Ecdlp.Curve.secp256k1_seven_nsmul_eq_zero_iff` | Ecdlp/Proved/SevenTorsionBridge.lean | Mathlib (`Affine.Point` group law, `add_self_of_Y_ne`/`add_some`/`slope`) + `linear_combination` + n=3 bridge | proved |
| *(alternate/supporting, n=7 bridge)* the core slope-algebra certificate `seven_master` (`G·(ℓ₂²−3x)⁶·(2y)¹² = −4(x³+7)·ψ₇`) and the `x(3P)=x(4P) ⟺ ψ₇=0` step `seven_core` | `Ecdlp.Curve.*` | Ecdlp/Proved/SevenTorsionBridge.lean | Mathlib + `linear_combination` | proved |

### Coverage restatements (tier-0, tracked separately — NOT in the headline figure)
Ten elementary finite-group / torsion facts — standard Mathlib lemmas restated in the ECDLP
ontology and closed by the zero-cost tier-0 layer (`Ecdlp/Proved/FrontierGroupFacts.lean`,
namespace `Ecdlp.Frontier`): `orderOf g ∣ |G|`, `0 < |G|`, `g^|G| = 1`, `orderOf 1 = 1`,
`addOrderOf a ∣ n ↔ n•a = 0`, `0 ∈ torsionBy A n`, `x ∈ torsionBy A n ⇒ −x ∈ …`,
`x ∈ torsionBy A 0`, `torsionBy A 0 = ⊤`, `torsionBy A 1 = ⊥`. These are **restatements**, not
novel results: kernel-verified and built (so the one-invariant still holds), but deliberately
**excluded from the headline count** to keep it honest.

### Ported / upstream-derived (attributed — NOT original, NOT in the headline figure)
The elliptic half of the open Mathlib TODO ("`normEDS` satisfies `IsEllSequence`") is
**kernel-verified in this repo by porting an existing proof**, not by an original derivation:

| Result | Lean name | File | Provenance |
|---|---|---|---|
| **`normEDS` is an elliptic sequence** — `IsEllSequence (normEDS b c d)` for every `b c d` over an arbitrary `CommRing` (Mathlib's own `IsEllSequence`). The flagship L4 target's elliptic half. | `normEDS_isEllSequence` | `Ecdlp/Proved/NormEDSIsElliptic.lean` | **Port of mathlib4 PR #13155** — proof, strategy, and certificates by **Junyan Xu (`alreadydone`) & David Angdinata**. This repo only transcribes their `namespace EllSequence` net-relation block onto pinned Mathlib v4.31 (2024→v4.31 API drift) and instantiates it for `normEDS` over `MvPolynomial (Fin 3) ℤ`, transporting via `map_normEDS`. Kernel-verified, 0 `sorry`; `#print axioms` = `[propext, Classical.choice, Quot.sound]`. |

This is a **verified asset, explicitly not a novel result of this project**: the mathematics
is Xu & Angdinata's. It is built and gated (the one-invariant holds), but deliberately
**excluded from the headline count** to keep authorship claims honest. The independent
`isEllSequence_of_rec_one` (headline row above) remains this repo's own contribution.

### Canonical count (single source of truth — propagate this exact figure)
**155 ledger rows / ~138 distinct kernel-verified results** (17 rows are alternate-form
or `supporting:` restatements of the same fact, e.g. the `ZMod`/ring forms of the GLV
eigenvalue and the operator form of the GLV cube relation — see the tagged rows above).
**0 `sorry`, 0 `admit`, 0 open obligations.**

*Axiom / trust-base note (precise).* No result depends on any **custom** axiom or on
`sorryAx`; this is **machine-enforced** by the axiom-audit CI gate (`Ecdlp/AxiomAudit.lean`
+ `scripts/check_axioms.py`). "No axioms" here means *no axioms beyond Lean/Mathlib's
standard `{propext, Classical.choice, Quot.sound}`* — which every Mathlib proof uses.
Results proved by `native_decide` (~33 concrete 256-bit facts) **additionally trust the
Lean compiler** via the `Lean.ofReduceBool` axiom, a real extension of the trusted base;
these are catalogued in `TRUST_REPORT.md`. The earlier "128 theorems" figure counted the
~22 internal recursive Pratt-certificate sub-lemmas individually and is **retired**.

What the ~105 results cover: the generic-group `Θ(√n)` combinatorial core and secp256k1
≥128-bit *generic* security; an **abstract** discrete-log protocol algebra over
`[Module (ZMod n) G]` (Schnorr/EdDSA, DH, ElGamal, Pedersen, Okamoto, Chaum–Pedersen,
MuSig2/Taproot, Feldman VSS, adaptor/blind Schnorr) — algebraic identities **not yet
instantiated at the secp256k1 point group, with no adversary/hash/probability model**
(see `ABSTRACT_SCOPE.md`); secp256k1 as a Mathlib `EllipticCurve` (`j = 0`, the CM
structure behind GLV) with the GLV map proved to be an **additive** endomorphism
(`glvPoint_add`; the `glvPoint = [λ]` eigenvalue property is **not yet** proved); and the
**machine-checked primality of `p` and `n`** (full Pratt certificates).

¹ ² The primality of `p` and `n` is now **machine-checked** (`secp256k1_p_prime`,
`secp256k1_n_prime`), and the corresponding `instance : Fact (Nat.Prime …)` is
provided in `Secp256k1PrimeP/N.lean`. The theorems marked ¹/² therefore carry a
`[Fact …]` hypothesis that is **discharged automatically** by these instances — so
they are effectively unconditional (no remaining assumptions, no axioms).

## How this grows
A new claim from `formalizable` becomes a theorem in `Ecdlp/`, gets committed,
and CI verifies it. On green, add its row here. The no-`sorry` gate guarantees a
green build means every listed theorem is fully proved.
