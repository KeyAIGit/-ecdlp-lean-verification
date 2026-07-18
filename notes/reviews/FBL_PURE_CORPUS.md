# FBL-PURE corpus — claim-traceability for the 15 pure-math tasks

Machine-checkable-corpus tracking for the 15 tasks (FBL-PURE-001 … 015). Fixed objects:
`P0` = secp256k1 field prime, `K0 = ZMod P0`, `C0 : Y²Z = X³ + 7Z³`, `N0` = group order,
`T0` = P0+1−N0 (Frobenius trace), `V0` (CM `4P0 = T0²+3V0²`), `OMEGA` a primitive cube root
of unity in `K0`. **The Lean kernel via CI is the only verifier**; "verified" below means a
theorem the repo's CI compiles green with `0 sorry / 0 admit / 0 custom axioms`.

Legend: **verified** = exact statement already kernel-checked on `main`; **partial** = core
done, a stated generalization/piece is open; **open** = genuine gap being drafted.

Record fields per task: claim_id · status · lean_files · lean_theorems · source_docs · barrier
· next_action · paper_hook · limitations.

---

## Already kernel-verified in the repo (9)

### FBL-PURE-002 — P0 is prime — **verified**
- lean_files: `Ecdlp/Proved/Secp256k1PrimeP.lean`
- lean_theorems: Pratt-style certificate chain (`pr_*` helper primes) → `Nat.Prime Secp256k1.p`
  (consumed repo-wide as `[Fact (Nat.Prime Secp256k1.p)]`).
- source_docs: `TRUST_REPORT.md` §2 (native_decide arithmetic disclosure).
- barrier: none. next_action: none (matches FBL-PURE-002 exactly).
- paper_hook: "replayable Pratt certificate for the secp256k1 field prime in Lean".
- limitations: individual residue checks via `native_decide` (compiler-trusted, disclosed).

### FBL-PURE-004 — OMEGA is a primitive cube root of unity — **verified (core)**
- lean_files: `Ecdlp/Secp256k1Verified.lean`, `Ecdlp/Proved/CubeRoot.lean`
- lean_theorems: `beta_field_eigenvalue` (β²+β+1 ≡ 0 mod p), `beta_is_cube_root` (β³ ≡ 1),
  `Ecdlp.cube_root_of_eigenvalue`, `orderOf_eigenvalue_eq_three`.
- barrier: none for the cube-root/order-3 facts.
- next_action: minor — pin the exact identity `(-7)^((P0-1)/3) = OMEGA` as an equality (the
  `≠ 1` half is already `secp256k1_neg7_pow_ne_one`, see 011); one `native_decide`/`decide`.
- paper_hook: "explicit CM cube root and its GLV eigenvalue relation". limitations: value-level
  facts are `native_decide`.

### FBL-PURE-005 — order-3 automorphism of C0 — **verified**
- lean_files: `Ecdlp/Proved/GlvAutomorphism.lean`, `GlvHom.lean`
- lean_theorems: `glvPoint_cube_eq_id` (α∘α∘α = id), `glvPoint_bijective`, `glvPoint_add`
  (α is an additive hom / group automorphism), `glvHom`.
- barrier: none. next_action: none (fixes ∞, preserves the curve, group-law-compatible — all
  covered, exceeding FBL-PURE-005's "coordinate check alone is insufficient").
- paper_hook: "the GLV endomorphism as a formally verified order-3 curve automorphism".

### FBL-PURE-006 — φ²+φ+1 = 0 (pointwise endomorphism relation) — **verified**
- lean_files: `Ecdlp/Proved/GlvCubeRelation.lean`
- lean_theorems: `secp256k1_glv_cube_relation (P) : glvPoint (glvPoint P) + glvPoint P + P = 0`
  (pointwise, additive; handles x=0 and ∞ / exceptional denominators).
- barrier: Mathlib has no direct End-ring API → the task's allowed pointwise form is what is
  proved. next_action: none. paper_hook: "pointwise CM quadratic relation φ²+φ+1=0 for j=0".
- limitations: stated pointwise, not as an End-ring element identity (Mathlib gap, per task's
  own fallback clause). **(GPT flagged this "most valuable for Fable" — already done.)**

### FBL-PURE-007 — division-polynomial symmetry ψ_m(ωx) — **verified**
- lean_files: `Ecdlp/Proved/GlvDivPoly.lean`
- lean_theorems: `secp256k1_Ψ₃_eval_glv` (Ψ₃(βx)=β·Ψ₃(x)), `secp256k1_{Ψ₂Sq,preΨ₅,preΨ₇}_eval_glv_invariant`.
- barrier: none for m∈{2,3,4,5,7} shown. next_action: the general odd-m dichotomy is 008.
- paper_hook: "GLV covariance of division polynomials". limitations: specific small m (the
  general statement is task 008).

### FBL-PURE-011 — x³ = −7 has no K0-solution; no affine y=0 point — **verified**
- lean_files: `Ecdlp/Proved/CurveCardinalityExact.lean`
- lean_theorems: `secp256k1_neg7_pow_ne_one` ((-7)^((p-1)/3) ≠ 1 ⇒ −7 not a cube),
  `secp256k1_no_nonzero_two_torsion` (P with 2•P=0 ⇒ P=0, i.e. ∞ is the only P=−P).
- barrier: none. next_action: none. paper_hook: "cube-residue obstruction ⇒ no 2-torsion on
  a j=0 curve". limitations: cube-residue value fact via `native_decide`.

### FBL-PURE-012 — Eisenstein/CM norm, 4P0 = T0²+3V0² — **verified (core)**
- lean_files: `Ecdlp/Proved/FrobeniusCM.lean`, `GlvOrderThree.lean`
- lean_theorems: `secp256k1_frobenius_norm`, `secp256k1_frobenius_trace`,
  `secp256k1_four_p_eq_trace_sq` (4P0 = T0² + 3V0²).
- barrier: none for the integer identities. next_action: if the task wants `Norm(π)=P0` with an
  explicit `ℤ[ρ]` norm form + A0=(T0+V0)/2 integrality, add the small parity lemma; the
  arithmetic core is done. paper_hook: "the secp256k1 Frobenius as an Eisenstein integer of
  norm P0". limitations: integer-identity checks via `native_decide`.

### FBL-PURE-013 — exact point count #C0(K0) = N0 — **verified** ⋆central⋆
- lean_files: `Ecdlp/Proved/CurveCardinalityExact.lean`
- lean_theorems: `secp256k1_card_point_eq_n : Nat.card secp256k1.toAffine.Point = Secp256k1.n`.
- method: **elementary, no Hasse bound** — `N0 ∣ #C0` (generator order) + `#C0 ≤ 2P0+1`
  (each x gives ≤2 points, X²−(x³+7) has ≤2 roots) + cofactor-1 pin. Only hypothesis
  `[Fact (Nat.Prime P0)]`.
- barrier: none. next_action: none. paper_hook: "kernel-checked exact cardinality of a
  cryptographic curve without Schoof or Hasse". limitations: none beyond the p-prime fact.
  **(GPT flagged this "central and hardest" — already done.)**

### FBL-PURE-014 — N0 is prime; point group ≅ ZMod N0 — **verified**
- lean_files: `Ecdlp/Proved/Secp256k1PrimeN.lean`, `PointGroupEquiv.lean`, `PointGroupSimple.lean`,
  `ScalarGroupStructure.lean`
- lean_theorems: Pratt chain → `Nat.Prime Secp256k1.n`; `secp256k1_pointGroupEquiv :
  secp256k1.toAffine.Point ≃+ ZMod Secp256k1.n` (+ `_apply`); prime-order ⇒ no proper nontrivial
  subgroup (`PointGroupSimple`).
- barrier: none. next_action: keep the generic prime-order-group lemma factored (already is).
  paper_hook: "the secp256k1 group is cyclic of prime order, formally". limitations: n-prime via
  Pratt/`native_decide`.

---

## Genuine gaps — agent-drafted, driven through CI (6)

### FBL-PURE-001 — general projective smoothness of Y²Z=X³+bZ³ — **verified** (#183)
- lean_files: `Ecdlp/Proved/CurveSmoothness.lean`
- lean_theorems: `Ecdlp.Curve.curveB_toProjective_nonsingular` (general-K:
  `2,3,b≠0 ⇒ (curveB b).toProjective.Nonsingular P` for `P≠0` on the curve — Mathlib's genuine
  `WeierstrassCurve.Projective.Nonsingular`, via `nonsingular_iff`'s three `pderiv` partials
  discharged by the two-chart `jacobian_core`); `secp256k1_projective_nonsingular` (b=7,K0);
  `secp256k1_infinity_nonsingular` (`[0:1:0]`); `curveB_Δ` (`=−432b²`), `curveB_Δ_ne_zero`.
- barrier: none (Mathlib projective API navigated). next_action: none.
- paper_hook: "reusable projective smoothness criterion for j=0 short-Weierstrass families, in
  Mathlib's own Nonsingular vocabulary, instantiated at secp256k1". limitations: kernel-only
  (no native_decide); `[Fact p.Prime]` hypothesis for the 𝔽_p specialization.

### FBL-PURE-003 — √ in K0 via a^((q+1)/4) for q≡3 mod 4 — **verified** (#184)
- lean_files: `Ecdlp/Proved/SqrtThreeModFour.lean`
- lean_theorems: `Ecdlp.Curve.sqrt_of_three_mod_four` (general: prime `q≡3 mod4`, `IsSquare a` ⇒
  `(a^((q+1)/4))² = a`, via `ZMod.pow_card` so `a=0` is uniform — no case split);
  `secp256k1_sqrt_of_isSquare` (q=p specialization, point decompression); congruences
  `p_mod_twelve` (`p≡7 mod12`), `p_mod_three` (`p≡1 mod3`); reuses `p_mod_four`.
- barrier: none — confirmed no ready-made Mathlib closed-form `q≡3 mod4` sqrt lemma (nearest
  are existence-only `ZMod.euler_criterion` / `FiniteField.isSquare_iff`); this is a genuine
  ~5-line formalization on `ZMod.pow_card`. next_action: none.
- paper_hook: "closed square-root map √a = a^((q+1)/4) for 3-mod-4 primes, machine-verified,
  instantiated at secp256k1 (point decompression)". limitations: general theorem kernel-pure;
  congruences `native_decide`; gives closed-form correctness only (not sign/parity selection).

### FBL-PURE-008 — compressed ψ_m = R_m(x³) [or x·R_m(x³)] + exact deg R_m — **partial**
- current: GLV invariance (007) done; specific degrees exist (`preΨ'11`=60, `preΨ'13`=84 in
  Eleven/ThirteenTorsion) but no general R_m existence + degree formula.
- next_action: from 007's covariance, prove ∃ R_m with the exponent-≡0-mod-3 structure and
  `deg R_m = (m²-1)/6` (3∤m) / `(m²-3)/6` (3∣m); specialize m=3,5,7,9,11,13.
- barrier: general division-poly recurrence bookkeeping. paper_hook: "3× compression of j=0
  division polynomials".

### FBL-PURE-009 — general coprimality ψ_m ⊥ ψ_n (coprime odd m,n) — **partial** ⋆GPT-top⋆
- current: 8 specific pairs proved (`CoprimePsi2Psi3/2Psi5/2Psi7/3PrePsi4/3Psi5/3Psi7/…`) via
  Bézout `native_decide`.
- next_action: prove the GENERAL theorem — common root ⇒ an affine point killed by both [m] and
  [n] ⇒ killed by [gcd(m,n)]=[1] ⇒ O (using opposite points share x); corollaries (5,7),(5,11),
  (7,11) for C0. Adversarial multi-agent (3–5).
- barrier: connecting polynomial common roots to simultaneous m,n-torsion generically (needs the
  closure torsion bridges, now partly on main). paper_hook: "generic division-polynomial
  coprimality from torsion disjointness".

### FBL-PURE-010 — general squarefree ψ_m + deg ψ_m = (m²-1)/2 — **partial** ⋆GPT-top⋆
- current: squarefree + exact root counts for m∈{3,5,7} landed (Split-PR 3:
  `DivisionPolynomialSquarefree/Separable`); general m open.
- next_action: general odd m, char∤m ⇒ ψ_m squarefree, deg=(m²-1)/2, root characterization,
  separability of [m]. Adversarial multi-agent.
- barrier: separability of [m] in general (the CORE hard item per `notes/DIVISION_POLY_TORSION_MAP.md`).
  paper_hook: "separability & squarefreeness of division polynomials, general m".

### FBL-PURE-015 — Frobenius characteristic polynomial X²−T0·X+P0 — **open/hard** ⋆GPT-top⋆
- current: trace facts (`secp256k1_trace_ordinary_nonanomalous`), norm/trace CM identities (012).
- next_action: the ENDOMORPHISM identity `Frob² − [T0]·Frob + [P0] = 0` (not the numeric
  P0+1−N0=T0). Identify the exact general theorem linking #E, trace, and the Frobenius char poly;
  formalize. Heavy adversarial multi-agent; expect a reduction to a missing Mathlib foundation
  (Frobenius endomorphism / char-poly on `EllipticCurve`), formalized per the task's fallback.
- barrier: **Mathlib lacks the elliptic-curve Frobenius endomorphism + its char-poly theorem.**
  paper_hook: "toward a formal Frobenius characteristic polynomial for elliptic curves".
  limitations: likely completes as a rigorous reduction, not a closed proof, until the foundation
  is built.

---

## Execution notes
- Order (deps): 001 → 003 → 008 → 009 → 010 → 015 (gaps only; the 9 verified tasks need no
  proof work, only these records). Each gap: independent agent drafts → synthesize → PR → CI.
- Invariants: no sorry/admit/custom axioms; deterministic certs print `CERT_OK`; nothing called
  "done" until CI is green. If a theorem is false, give the minimal counterexample + corrected
  theorem. If Mathlib lacks a foundation, isolate the smallest missing lemma (esp. 015).
