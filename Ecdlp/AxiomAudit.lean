import Ecdlp
import ResearchOS.NumberTheory.Elementary
import ResearchOS.NumberTheory.MoreFacts

/-!
# Axiom audit (CI trust gate)

This file is **not** part of the built proof base (it is never imported from `Ecdlp.lean`).
CI runs it standalone (`lake env lean Ecdlp/AxiomAudit.lean`) and pipes the output to
`scripts/check_axioms.py`, which **fails the build** if any audited result depends on
`sorryAx` (a leaked `sorry`) or on any axiom outside the allowed trusted base:

  * `propext`, `Classical.choice`, `Quot.sound` — Lean/Mathlib's standard axioms, used by
    essentially every Mathlib proof; "no axioms" in this repo means "none beyond these".
  * `Lean.ofReduceBool` — introduced by `native_decide`, which trusts the Lean **compiler**.
    This is a real extension of the trusted computing base; results that use it are listed
    in `TRUST_REPORT.md`. The audit makes that dependency visible rather than hidden.

Audited set = the headline kernel-verified results across all pillars (the deep object,
the generic-group core, protocol soundness, the curve instance, and a `native_decide`
sample that should surface `Lean.ofReduceBool`). `#print axioms` prints each dependency.
-/

-- GLV endomorphism object (homomorphism half)
#print axioms Ecdlp.Curve.glvPoint_add
#print axioms Ecdlp.Curve.glvHom
#print axioms Ecdlp.Curve.secp256k1_glv_slope
#print axioms Ecdlp.Curve.secp256k1_glv_addX
#print axioms Ecdlp.Curve.secp256k1_glv_preserves_equation
#print axioms Ecdlp.Curve.secp256k1_glv_cube_relation
#print axioms Ecdlp.Curve.secp256k1_glv_preserves_torsion
#print axioms Ecdlp.Curve.secp256k1_glv_preserves_dlog
#print axioms Ecdlp.Curve.secp256k1_glv_single_scalar

-- GLV covariance law for the division polynomials: ψ_m(βx)=β^((m²-1)/2)ψ_m(x)
#print axioms Ecdlp.Curve.secp256k1_Ψ₃_eval_glv
#print axioms Ecdlp.Curve.secp256k1_preΨ₅_eval_glv_invariant
#print axioms Ecdlp.Curve.secp256k1_preΨ₇_eval_glv_invariant

-- GLV orbit structure: orbits size ≤3 (group root of the measured ~3× constant)
#print axioms Ecdlp.Curve.secp256k1_glvPoint_orbit_closed
#print axioms Ecdlp.Curve.secp256k1_glvPoint_orbit_three_distinct

-- secp256k1 as a Mathlib elliptic curve
#print axioms Ecdlp.Curve.secp256k1_j_eq_zero
#print axioms Ecdlp.Curve.secp256k1_generator_nonsingular

-- base-point exact order `n` (weak point-counting keystone) + GLV `[λ]` at the generator
-- (these surface `Lean.ofReduceBool`: `native_decide` over the Mathlib group law)
#print axioms Ecdlp.Curve.secp256k1_generator_addOrderOf
#print axioms Ecdlp.Curve.secp256k1_glvPoint_generator
#print axioms Ecdlp.Curve.secp256k1_glvPoint_eq_lam_on_zmultiples

-- protocol algebra instantiated on the concrete secp256k1 subgroup ⟨G⟩
-- (bridge lemma inherits `Lean.ofReduceBool` from the order keystone)
#print axioms Ecdlp.Curve.secp256k1_grp_nsmul_eq_zero
#print axioms Ecdlp.Curve.secp256k1_dh_agree
#print axioms Ecdlp.Curve.secp256k1_schnorr_verify
#print axioms Ecdlp.Curve.secp256k1_taproot_tweak_verify

-- ⟨G⟩ group structure: exactly n elements, cyclic, and the discrete-log isomorphism
-- ZMod n ≃+ ⟨G⟩ (inherits `Lean.ofReduceBool` from the order keystone)
#print axioms Ecdlp.Curve.secp256k1_grp_card
#print axioms Ecdlp.Curve.secp256k1_grp_isAddCyclic
#print axioms Ecdlp.Curve.secp256k1_dlogEquiv

-- strong keystone: the exact curve cardinality #E(𝔽_p) = n, curve-specifically
-- (no Hasse/Schoof); inherits `Lean.ofReduceBool` from the native_decide non-cube leaf
#print axioms Ecdlp.Curve.secp256k1_card_point_eq_n
#print axioms Ecdlp.Curve.secp256k1_no_nonzero_two_torsion
#print axioms Ecdlp.Curve.secp256k1_card_point_le

-- full-group corollaries of #E=n: ⟨G⟩ = ⊤ (cofactor 1), E(𝔽_p) cyclic, glvPoint=[λ] unconditional
#print axioms Ecdlp.Curve.secp256k1_grp_eq_top
#print axioms Ecdlp.Curve.secp256k1_glvHom_eq_zsmul_unconditional

-- full point-group structure theorem: E(𝔽_p) ≃+ ℤ/n (dlogEquiv lifted off ⟨G⟩ via grp_eq_top)
#print axioms Ecdlp.Curve.secp256k1_pointGroupEquiv
#print axioms Ecdlp.Curve.secp256k1_point_group_equiv_exists

-- point-group cofactor-1 security structure from #E=n prime: no proper nontrivial subgroup,
-- every nonzero point generates (group-level small-subgroup-attack resistance)
#print axioms Ecdlp.Curve.secp256k1_point_group_no_proper_subgroup
#print axioms Ecdlp.Curve.secp256k1_nonzero_point_generates

-- thesis capstone: the classical attack-resistance profile (cofactor 1 + prime order + not
-- supersingular + not anomalous + Hasse + embedding degree >100), one unconditional theorem
#print axioms Ecdlp.Curve.secp256k1_classical_security_profile

-- quadratic-twist security certificate: #Ẽ = 2p+2−n = 3²·13²·3319·22639·Q (Q a 220-bit prime),
-- nontrivial cofactor ⇒ twist has small subgroups; twist DLP ≈√Q<2¹¹⁰ < curve 2¹²⁸ (why x-only
-- secp256k1 code must validate points)
#print axioms Ecdlp.Curve.secp256k1_twist_order_factorization
#print axioms Ecdlp.Curve.secp256k1_twist_maxprime_prime
#print axioms Ecdlp.Curve.secp256k1_twist_security_profile

-- P-256 twist companion: 2p+2−n = 3·5·13·179·Q (Q a 241-bit prime), cofactor 34905 ≈ 2¹⁵,
-- twist DLP ≈√Q ≈ 2¹²⁰ < 2¹²⁸; interpretation as #Ẽ conditional on #E=n (in-repo: n∣#E only)
#print axioms Ecdlp.P256.p256_twist_order_factorization
#print axioms Ecdlp.P256.p256_twist_maxprime_prime
#print axioms Ecdlp.P256.p256_twist_security_profile

-- CM-by-ℤ[ω] Frobenius arithmetic certificate: N(π)=p, Tr(π)=p+1−n, 4p=t²+3b² (End⊗ℚ=ℚ(√−3))
#print axioms Ecdlp.Curve.secp256k1_frobenius_norm
#print axioms Ecdlp.Curve.secp256k1_frobenius_trace
#print axioms Ecdlp.Curve.secp256k1_four_p_eq_trace_sq

-- generic-group lower-bound combinatorial core + secp256k1 generic security
#print axioms Ecdlp.GenericGroup.generic_dlog_query_bound
#print axioms Ecdlp.GenericGroup.secp256k1_generic_security

-- discrete-log protocol algebra (representative)
#print axioms Ecdlp.Schnorr.schnorr_extract

-- ECDSA malleability core (BIP-62 r.5/BIP-146 low-s): sibling (r,−s) via point negation
-- preserving x; field-side lemmas pure-kernel, curve-side conditional on [Fact p.Prime]
#print axioms Ecdlp.Curve.secp256k1_pointX_neg
#print axioms Ecdlp.Curve.secp256k1_pointX_neg_zsmul_add
#print axioms Ecdlp.Schnorr.ecdsa_sibling_signing_equation
#print axioms Ecdlp.Schnorr.ecdsa_sibling_scalars

-- Semaev's 3rd summation polynomial, forward direction (clean base: pure `linear_combination`)
#print axioms Ecdlp.Semaev.S₃_eq_zero_of_chord
#print axioms Ecdlp.Semaev.secp256k1_semaev_three_chord
#print axioms Ecdlp.Semaev.S₃_eq_zero_of_tangent
#print axioms Ecdlp.Semaev.secp256k1_semaev_three_tangent
#print axioms Ecdlp.Semaev.secp256k1_semaev_three_point
#print axioms Ecdlp.Semaev.secp256k1_semaev_three_point_double
#print axioms Ecdlp.Semaev.S₃_root_of_eq_zero
#print axioms Ecdlp.Semaev.secp256k1_semaev_three_iff
#print axioms Ecdlp.Semaev.resultant_eq_zero_of_common_root
#print axioms Ecdlp.Semaev.S₄_eq_zero_of_common_root
#print axioms Ecdlp.Semaev.secp256k1_semaev_four_of_common_root
#print axioms Ecdlp.Semaev.S₃poly_master_factor
#print axioms Ecdlp.Semaev.S₄_common_root_of_eq_zero
#print axioms Ecdlp.Semaev.secp256k1_semaev_four_common_root_of_eq_zero
#print axioms Ecdlp.Semaev.S₄_symm₃₄

-- Point decomposition ⇒ Semaev relation (index-calculus entry point): R = P₁+P₂ ⇒ S₃ root
#print axioms Ecdlp.Semaev.secp256k1_point_decomposition_semaev
#print axioms Ecdlp.Semaev.secp256k1_point_decomposition_semaev_double

-- Semaev degree ⇒ bounded decomposition fan-out (prime-field barrier ingredient)
#print axioms Ecdlp.Semaev.secp256k1_S₃poly_natDegree
#print axioms Ecdlp.Semaev.secp256k1_decomposition_completions_le_two

-- Distinct-prime torsion x-locus disjointness (no-go certificate family): E[3] ⊥ E[5],
-- E[2] ⊥ E[5], E[3] ⊥ E[7] (missing from Mathlib; explicit 𝔽_p Bézout, native_decide residues)
#print axioms Ecdlp.Curve.secp256k1_preΨ₅
#print axioms Ecdlp.Curve.secp256k1_isCoprime_Ψ₃_preΨ₅
#print axioms Ecdlp.Curve.secp256k1_isCoprime_Ψ₂Sq_preΨ₅
#print axioms Ecdlp.Curve.secp256k1_preΨ₇
#print axioms Ecdlp.Curve.secp256k1_isCoprime_Ψ₃_preΨ₇

-- General division-resultant reduction and root-to-torsion frontier. The final theorems
-- are conditional on explicitly named propositions; no axiom or global instance supplies them.
#print axioms Ecdlp.Curve.exists_nonsingular_y
#print axioms Ecdlp.Curve.isCoprime_preΨ'_odd_primes_of_torsion_bridge
#print axioms Ecdlp.Curve.secp256k1_isCoprime_preΨ'_odd_primes_of_torsion_bridge
#print axioms Ecdlp.Curve.secp256k1Z_discriminant_pow_bad_prime_support
#print axioms Ecdlp.Curve.secp256k1_resultant_eq_intCast
#print axioms Ecdlp.Curve.secp256k1_isCoprime_preΨ'_of_integral_resultant_bad_prime_support
#print axioms Ecdlp.Curve.secp256k1_isCoprime_preΨ'_odd_primes_of_integral_resultant_bad_prime_support
#print axioms Ecdlp.Curve.secp256k1_isCoprime_preΨ'_odd_primes_of_integral_resultant_formula

-- Division-polynomial multiplication formula, base case n = 2 (torsion-bridge engine)
#print axioms Ecdlp.Curve.secp256k1_Φ₂
#print axioms Ecdlp.Curve.secp256k1_double_x_eq_Φ₂_div_Ψ₂Sq

-- Weil-pairing foundations, rungs 1–3: torsion ⟺ principal; Miller function exists + unique
#print axioms Ecdlp.Weil.secp256k1_torsion_iff_principal
#print axioms Ecdlp.Weil.secp256k1_miller_function_exists
#print axioms Ecdlp.Weil.secp256k1_miller_function_unique

-- Weil-pairing infrastructure (layer B): point-evaluation `F[E] →+* F` and its residue-field /
-- rational-function extension (re-imported & kernel-confirmed green — no longer parked).
#print axioms Ecdlp.Weil.evalAt
#print axioms Ecdlp.Weil.evalAt_surjective
#print axioms Ecdlp.Weil.evalAt_ker
#print axioms Ecdlp.Weil.xyIdeal_isMaximal
#print axioms Ecdlp.Weil.residueFieldEquiv
#print axioms Ecdlp.Weil.evalRatAt
#print axioms Ecdlp.Weil.evalRatAt_surjective
#print axioms Ecdlp.Weil.evalRatAt_algebraMap
#print axioms Ecdlp.Weil.evalRatAt_eq_zero_iff
#print axioms Ecdlp.Weil.evalRatAt_ne_zero_iff_isUnit
#print axioms Ecdlp.Weil.xyIdeal_ne_of_x_ne
#print axioms Ecdlp.Weil.xyIdeal_ne_of_y_ne
#print axioms Ecdlp.Weil.xyIdeal_ne_of_ne

-- Weil H4 bridge: division-polynomial tower ⟺ Miller/divisor tower (ψ n root ⟺ n·([P]−[O]) principal)
#print axioms Ecdlp.Weil.secp256k1_psi3_root_iff_class_torsion
#print axioms Ecdlp.Weil.secp256k1_psi5_root_iff_class_torsion
#print axioms Ecdlp.Weil.secp256k1_psi7_root_iff_class_torsion

-- NIST P-256 grounding (curve-agnostic; native_decide facts surface `Lean.ofReduceBool`)
#print axioms Ecdlp.P256.P256_Δ_ne_zero
#print axioms Ecdlp.P256.P256_c₄_ne_zero
#print axioms Ecdlp.P256.P256_generator_equation

-- P-256 weak cardinality rung: E(𝔽_p) finite + n ∣ #E (mirrors the secp256k1 template;
-- inherits `Lean.ofReduceBool` via the native_decide generator-order anchor `addOrderOf G = n`)
#print axioms Ecdlp.P256.instFiniteP256Point
#print axioms Ecdlp.P256.p256_grp_card
#print axioms Ecdlp.P256.p256_n_dvd_card_point

-- General finiteness of affine Weierstrass points over any finite ring (Mathlib-gap upstream
-- candidate; pure-kernel — should depend ONLY on the standard base, no `Lean.ofReduceBool`)
#print axioms WeierstrassCurve.Affine.instFinitePoint

-- Curve25519 grounding (Montgomery model, cofactor 8; native_decide facts surface `Lean.ofReduceBool`)
#print axioms Ecdlp.Curve25519.Curve25519_Δ_ne_zero
#print axioms Ecdlp.Curve25519.Curve25519_a₂_ne_zero
#print axioms Ecdlp.Curve25519.Curve25519_generator_equation

-- native_decide samples (these SHOULD surface `Lean.ofReduceBool`)
#print axioms Secp256k1.p_special_form
#print axioms Secp256k1.beta_field_eigenvalue

-- NON-ECC domain (elementary number theory): the second-subject portability instance.
-- Pure `norm_num`, so these should depend ONLY on the standard base (no `Lean.ofReduceBool`).
#print axioms ResearchOS.NumberTheory.prime_2017
#print axioms ResearchOS.NumberTheory.mersenne_M13_prime
#print axioms ResearchOS.NumberTheory.carmichael_561_not_prime
#print axioms ResearchOS.NumberTheory.carmichael_561_factorization
#print axioms ResearchOS.NumberTheory.mersenne_M17_prime
#print axioms ResearchOS.NumberTheory.mersenne_M19_prime
#print axioms ResearchOS.NumberTheory.carmichael_1105_not_prime
#print axioms ResearchOS.NumberTheory.carmichael_1105_factorization
#print axioms ResearchOS.NumberTheory.carmichael_1729_not_prime
#print axioms ResearchOS.NumberTheory.carmichael_1729_factorization
#print axioms ResearchOS.NumberTheory.prime_10007
#print axioms ResearchOS.NumberTheory.prime_10009

-- geometric torsion structure family: E[n](𝔽̄_p) ≅ (ℤ/n)² for n ∈ {2,3,5,7} (closure), via
-- closure bridge + exact root count + ±y pairing + N10(iii); the ψₙ↔E[n] critical path N13@n
#print axioms Ecdlp.Curve.secp256k1Bar_two_torsion_structure
#print axioms Ecdlp.Curve.secp256k1Bar_three_torsion_structure
#print axioms Ecdlp.Curve.secp256k1Bar_five_torsion_structure
#print axioms Ecdlp.Curve.secp256k1Bar_seven_torsion_structure

-- 2-torsion cubic separability (X³+7 has 3 distinct roots over 𝔽̄_p) — counting brick of E[2]
#print axioms Ecdlp.Curve.secp256k1_cubic_separable

-- N7 multiplication-by-n x-coordinate formulas x(nP)=Φₙ/ΨSqₙ, n = 4 (doubling²) and n = 5 (chord)
#print axioms Ecdlp.Curve.secp256k1_quadruple_x_eq_Φ₄_div_ΨSq₄
#print axioms Ecdlp.Curve.secp256k1_quintuple_x_eq_Φ₅_div_ΨSq₅

-- Weil W3 function-field evaluation layer: fraction eval well-definedness + a/b extraction + RegularAt
#print axioms Ecdlp.Weil.evalFracAt_well_defined
#print axioms Ecdlp.Weil.functionField_exists_num_den
#print axioms Ecdlp.Weil.evalRatAt_eq_evalReg
