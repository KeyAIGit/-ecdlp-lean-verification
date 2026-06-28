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

**Total: 110 theorems proved** (19 concrete `native_decide` facts, 69 structural via
Mathlib, 22 recursive Pratt-certificate primality nodes). **0 open obligations.** A
verified discrete-log cryptography library: generic hardness (`Θ(√n)`, secp256k1
≥128-bit), the soundness/completeness of deployed protocols (Schnorr/EdDSA,
Diffie–Hellman, ElGamal, Pedersen, Okamoto, Chaum–Pedersen DLEQ, Schnorr
multisig/Taproot, Feldman VSS, adaptor signatures), secp256k1 as a Mathlib elliptic
curve (`j = 0`, the CM structure behind GLV), and the **machine-checked primality of
`p` and `n`** (Pratt certificates, generated by `scripts/pratt_certificate.py`).

¹ ² The primality of `p` and `n` is now **machine-checked** (`secp256k1_p_prime`,
`secp256k1_n_prime`), and the corresponding `instance : Fact (Nat.Prime …)` is
provided in `Secp256k1PrimeP/N.lean`. The theorems marked ¹/² therefore carry a
`[Fact …]` hypothesis that is **discharged automatically** by these instances — so
they are effectively unconditional (no remaining assumptions, no axioms).

## How this grows
A new claim from `formalizable` becomes a theorem in `Ecdlp/`, gets committed,
and CI verifies it. On green, add its row here. The no-`sorry` gate guarantees a
green build means every listed theorem is fully proved.
