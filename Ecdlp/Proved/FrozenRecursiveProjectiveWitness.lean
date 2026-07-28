import Ecdlp.Proved.FrozenRecursiveProjectiveSemaev

/-!
# Recursive projective witnesses for the frozen Semaev family

This module closes the projective witness-extraction step left by
`FrozenRecursiveProjectiveSemaev`.  The key point is a declared-degree
homogenization identity for the actual frozen family, not merely an affine
degree bound.

The target field is algebraically closed because each fixed-degree resultant
step extracts a projective root in that field.  No claim is made that the
intermediate witnesses descend to a smaller base field.

The resulting chain is only the exact polynomial semantics of the frozen
family.  It is not a direct-`S17`, recovery, rationality, or solving-cost
theorem.
-/

namespace Ecdlp.FrozenProjectiveSemaev

open Polynomial

/-! ## Universal binary output -/

/-- Embed a valid projective pair as a constant pair over a binary
multivariate-polynomial ring. -/
noncomputable def binaryConstantPair {K : Type*} [Field K]
    (q : ProjectivePair K) :
    ProjectivePair (MvPolynomial (Fin 2) K) where
  u := MvPolynomial.C q.u
  v := MvPolynomial.C q.v
  valid := by
    rcases q.valid with hu | hv
    · exact Or.inl (MvPolynomial.C_ne_zero.mpr hu)
    · exact Or.inr (MvPolynomial.C_ne_zero.mpr hv)

/-- The universal valid projective pair `[X₀:X₁]`. -/
noncomputable def binaryPair {K : Type*} [Field K] :
    ProjectivePair (MvPolynomial (Fin 2) K) where
  u := MvPolynomial.X 0
  v := MvPolynomial.X 1
  valid := Or.inl (MvPolynomial.X_ne_zero 0)

/-- Specialize all leaves to constants while retaining the output as the
universal binary projective pair `[X₀:X₁]`. -/
noncomputable def projectiveOutputAtOver
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (p : MvPolynomial Var k)
    (q : ℕ → ProjectivePair K) : MvPolynomial (Fin 2) K :=
  specializeOver
    ((MvPolynomial.C : K →+* MvPolynomial (Fin 2) K).comp φ)
    (fun i ↦ binaryConstantPair (q i))
    binaryPair
    p

/-- Evaluating the universal binary output at a valid pair is exactly direct
projective specialization. -/
theorem eval_projectiveOutputAtOver
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (p : MvPolynomial Var k)
    (q : ℕ → ProjectivePair K) (z : ProjectivePair K) :
    MvPolynomial.eval ![z.u, z.v] (projectiveOutputAtOver φ p q) =
      specializeOver φ q z p := by
  change
    ((MvPolynomial.eval ![z.u, z.v]).comp
      (MvPolynomial.eval₂Hom
        ((MvPolynomial.C : K →+* MvPolynomial (Fin 2) K).comp φ)
        (fun
          | .leaf i a => (binaryConstantPair (q i)).coord a
          | .output a => binaryPair.coord a))) p =
      MvPolynomial.eval₂Hom φ
        (fun
          | .leaf i a => (q i).coord a
          | .output a => z.coord a)
        p
  apply MvPolynomial.hom_eq_hom
  · ext a
    simp
  · intro i
    cases i with
    | leaf i a =>
        cases a <;>
          simp [binaryConstantPair, ProjectivePair.coord]
    | output a =>
        cases a <;>
          simp [binaryPair, ProjectivePair.coord]

/-- Dehomogenizing the universal binary output on `[X:1]` gives the exact
predecessor affine slice. -/
theorem dehomogenize_projectiveOutputAtOver
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (p : MvPolynomial Var k)
    (q : ℕ → ProjectivePair K) :
    MvPolynomial.aeval ![(Polynomial.X : K[X]), 1]
        (projectiveOutputAtOver φ p q) =
      previousSliceAtOver φ p q := by
  change
    ((MvPolynomial.eval₂Hom
      (Polynomial.C : K →+* K[X])
      ![(Polynomial.X : K[X]), 1]).comp
      (MvPolynomial.eval₂Hom
        ((MvPolynomial.C : K →+* MvPolynomial (Fin 2) K).comp φ)
        (fun
          | .leaf i a => (binaryConstantPair (q i)).coord a
          | .output a => binaryPair.coord a))) p =
      MvPolynomial.eval₂Hom
        (Polynomial.C.comp φ)
        (fun
          | .leaf i a => Polynomial.C ((q i).coord a)
          | .output .u => Polynomial.X
          | .output .v => 1)
        p
  apply MvPolynomial.hom_eq_hom
  · ext a
    simp
  · intro i
    cases i with
    | leaf i a =>
        cases a <;>
          simp [binaryConstantPair, ProjectivePair.coord]
    | output a =>
        cases a <;>
          simp [binaryPair, ProjectivePair.coord]

/-! ## Homogeneous determinant tools -/

/-- Rowwise homogeneous entries give a determinant homogeneous of the sum of
the row degrees. -/
theorem det_isHomogeneous_sum_row
    {R σ ι : Type*} [CommRing R] [Fintype ι] [DecidableEq ι]
    (A : Matrix ι ι (MvPolynomial σ R)) (w : ι → ℕ)
    (hA : ∀ i j, (A i j).IsHomogeneous (w i)) :
    A.det.IsHomogeneous (∑ i, w i) := by
  rw [Matrix.det_apply']
  apply MvPolynomial.IsHomogeneous.sum
  intro π hπ
  have hsign :
      (((Equiv.Perm.sign π : ℤ) : MvPolynomial σ R)).IsHomogeneous 0 := by
    change
      (MvPolynomial.C ((Equiv.Perm.sign π : ℤ) : R)).IsHomogeneous 0
    exact MvPolynomial.isHomogeneous_C _ _
  have hprod :
      (∏ i, A (π i) i).IsHomogeneous (∑ i, w (π i)) := by
    apply MvPolynomial.IsHomogeneous.prod
    intro i hi
    exact hA (π i) i
  simpa only [zero_add, Equiv.sum_comp π w] using hsign.mul hprod

/-- A binary quadratic with coefficients listed in `X₀², X₀X₁, X₁²`
order. -/
noncomputable def binaryQuadratic
    {K : Type*} [Field K] (a b c : K) : MvPolynomial (Fin 2) K :=
  MvPolynomial.C a * MvPolynomial.X (R := K) (0 : Fin 2) ^ 2 +
    MvPolynomial.C b * MvPolynomial.X (R := K) (0 : Fin 2) *
      MvPolynomial.X (R := K) (1 : Fin 2) +
    MvPolynomial.C c * MvPolynomial.X (R := K) (1 : Fin 2) ^ 2

/-- A generic binary quadratic form is homogeneous of degree two. -/
theorem binaryQuadratic_isHomogeneous
    {K : Type*} [Field K] (a b c : K) :
    (binaryQuadratic a b c).IsHomogeneous 2 := by
  have hU : (MvPolynomial.X (R := K) (0 : Fin 2)).IsHomogeneous 1 :=
    MvPolynomial.isHomogeneous_X (R := K) (0 : Fin 2)
  have hV : (MvPolynomial.X (R := K) (1 : Fin 2)).IsHomogeneous 1 :=
    MvPolynomial.isHomogeneous_X (R := K) (1 : Fin 2)
  have hU2 :
      (MvPolynomial.C a *
        MvPolynomial.X (R := K) (0 : Fin 2) ^ 2).IsHomogeneous 2 := by
    simpa using (hU.pow 2).C_mul a
  have hUV :
      (MvPolynomial.C b * MvPolynomial.X (R := K) (0 : Fin 2) *
        MvPolynomial.X (R := K) (1 : Fin 2)).IsHomogeneous 2 := by
    simpa [add_comm, add_left_comm, add_assoc] using
      ((hU.C_mul b).mul hV)
  have hV2 :
      (MvPolynomial.C c *
        MvPolynomial.X (R := K) (1 : Fin 2) ^ 2).IsHomogeneous 2 := by
    simpa using (hV.pow 2).C_mul c
  exact (hU2.add hUV).add hV2

/-- The `T²` coefficient of `H([T:1],q,[X₀:X₁])`. -/
noncomputable def localBinaryCoeffTwo
    {K : Type*} [Field K] (q : ProjectivePair K) :
    MvPolynomial (Fin 2) K :=
  binaryQuadratic (q.v ^ 2) (-2 * q.u * q.v) (q.u ^ 2)

/-- The `T` coefficient of `H([T:1],q,[X₀:X₁])`. -/
noncomputable def localBinaryCoeffOne
    {K : Type*} [Field K] (q : ProjectivePair K) :
    MvPolynomial (Fin 2) K :=
  binaryQuadratic
    (-2 * q.u * q.v) (-2 * q.u ^ 2) (-28 * q.v ^ 2)

/-- The constant coefficient of `H([T:1],q,[X₀:X₁])`. -/
noncomputable def localBinaryCoeffZero
    {K : Type*} [Field K] (q : ProjectivePair K) :
    MvPolynomial (Fin 2) K :=
  binaryQuadratic
    (q.u ^ 2) (-28 * q.v ^ 2) (-28 * q.u * q.v)

theorem localBinaryCoeffTwo_isHomogeneous
    {K : Type*} [Field K] (q : ProjectivePair K) :
    (localBinaryCoeffTwo q).IsHomogeneous 2 :=
  binaryQuadratic_isHomogeneous _ _ _

theorem localBinaryCoeffOne_isHomogeneous
    {K : Type*} [Field K] (q : ProjectivePair K) :
    (localBinaryCoeffOne q).IsHomogeneous 2 :=
  binaryQuadratic_isHomogeneous _ _ _

theorem localBinaryCoeffZero_isHomogeneous
    {K : Type*} [Field K] (q : ProjectivePair K) :
    (localBinaryCoeffZero q).IsHomogeneous 2 :=
  binaryQuadratic_isHomogeneous _ _ _

/-- Literal expansion of `H([T:1],q,[X₀:X₁])` by powers of `T`. -/
theorem localSliceAt_binaryPair_explicit
    {K : Type*} [Field K] (q : ProjectivePair K) :
    localSliceAt (binaryConstantPair q) binaryPair =
      Polynomial.monomial 2 (localBinaryCoeffTwo q) +
        Polynomial.monomial 1 (localBinaryCoeffOne q) +
        Polynomial.C (localBinaryCoeffZero q) := by
  simp [localSliceAt, HValue, binaryConstantPair, binaryPair,
    ProjectivePair.coord, localBinaryCoeffTwo, localBinaryCoeffOne,
    localBinaryCoeffZero, binaryQuadratic]
  simp only [← Polynomial.C_mul_X_pow_eq_monomial]
  simp only [Polynomial.C_mul, Polynomial.C_pow]
  have hC2 :
      (MvPolynomial.C (2 : K) : MvPolynomial (Fin 2) K) = 2 := by
    simpa using
      (map_ofNat (MvPolynomial.C : K →+* MvPolynomial (Fin 2) K) 2)
  have hC28 :
      (MvPolynomial.C (28 : K) : MvPolynomial (Fin 2) K) = 28 := by
    simpa using
      (map_ofNat (MvPolynomial.C : K →+* MvPolynomial (Fin 2) K) 28)
  rw [hC2, hC28]
  simp only [Polynomial.C_ofNat]
  ring

/-- Every `T`-coefficient of the local binary slice is homogeneous of degree
two in `[X₀:X₁]`. -/
theorem localSliceAt_binaryPair_coeff_isHomogeneous
    {K : Type*} [Field K] (q : ProjectivePair K) (i : ℕ) :
    ((localSliceAt (binaryConstantPair q) binaryPair).coeff i).IsHomogeneous 2 := by
  rw [localSliceAt_binaryPair_explicit]
  by_cases hi2 : i = 2
  · subst i
    simp only [Polynomial.coeff_add, Polynomial.coeff_monomial,
      Polynomial.coeff_C, if_pos]
    rw [if_neg (by omega), if_neg (by omega)]
    simp only [add_zero]
    exact localBinaryCoeffTwo_isHomogeneous q
  · by_cases hi1 : i = 1
    · subst i
      simp only [Polynomial.coeff_add, Polynomial.coeff_monomial,
        Polynomial.coeff_C, if_pos]
      rw [if_neg (by omega), if_neg (by omega)]
      simp only [zero_add, add_zero]
      exact localBinaryCoeffOne_isHomogeneous q
    · by_cases hi0 : i = 0
      · subst i
        simp only [Polynomial.coeff_add, Polynomial.coeff_monomial,
          Polynomial.coeff_C, if_pos]
        rw [if_neg (by omega), if_neg (by omega)]
        simp only [zero_add]
        exact localBinaryCoeffZero_isHomogeneous q
      · simp only [Polynomial.coeff_add, Polynomial.coeff_monomial,
          Polynomial.coeff_C]
        rw [if_neg (Ne.symm hi2), if_neg (Ne.symm hi1), if_neg hi0]
        simp only [zero_add]
        exact MvPolynomial.isHomogeneous_zero (Fin 2) K 2

/-- Taking a predecessor slice after the binary constant embedding is the
coefficientwise binary constant embedding of the original slice. -/
theorem previousSliceAtOver_binaryConstantPair
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (p : MvPolynomial Var k)
    (q : ℕ → ProjectivePair K) :
    previousSliceAtOver
        ((MvPolynomial.C : K →+* MvPolynomial (Fin 2) K).comp φ)
        p (fun i ↦ binaryConstantPair (q i)) =
      (previousSliceAtOver φ p q).map MvPolynomial.C := by
  change
    MvPolynomial.eval₂Hom
        (Polynomial.C.comp
          ((MvPolynomial.C : K →+* MvPolynomial (Fin 2) K).comp φ))
        (fun
          | .leaf i a =>
              Polynomial.C ((binaryConstantPair (q i)).coord a)
          | .output .u => Polynomial.X
          | .output .v => 1)
        p =
      ((Polynomial.mapRingHom MvPolynomial.C).comp
        (MvPolynomial.eval₂Hom
          (Polynomial.C.comp φ)
          (fun
            | .leaf i a => Polynomial.C ((q i).coord a)
            | .output .u => Polynomial.X
            | .output .v => 1)))
        p
  apply MvPolynomial.hom_eq_hom
  · ext a n
    simp
  · intro i
    cases i with
    | leaf i a =>
        cases a <;>
          simp [binaryConstantPair, ProjectivePair.coord]
    | output a =>
        cases a <;> simp

/-- The frozen Sylvester determinant is homogeneous when its left
coefficients are binary constants and its right coefficients are binary
quadratics. -/
theorem taskSylvester_isHomogeneous_two_mul_left
    {K : Type*} [Field K]
    (f g : (MvPolynomial (Fin 2) K)[X]) (m : ℕ)
    (hf : ∀ i, (f.coeff i).IsHomogeneous 0)
    (hg : ∀ i, (g.coeff i).IsHomogeneous 2) :
    (Ecdlp.TaskSylvester.taskSylvester f g m 2).det.IsHomogeneous (2 * m) := by
  have hdet :
      (Ecdlp.TaskSylvester.taskSylvester f g m 2).det.IsHomogeneous
        (∑ i : Fin (m + 2), if (i : ℕ) < 2 then 0 else 2) := by
    apply det_isHomogeneous_sum_row
    intro i j
    simp only [Ecdlp.TaskSylvester.taskSylvester, Matrix.of_apply]
    by_cases hi : (i : ℕ) < 2
    · rw [if_pos hi]
      simp only [Ecdlp.TaskSylvester.descendingShift]
      split_ifs
      · simpa using hf _
      · exact MvPolynomial.isHomogeneous_zero (Fin 2) K 0
    · rw [if_neg hi]
      simp only [Ecdlp.TaskSylvester.descendingShift]
      split_ifs
      · simpa using hg _
      · exact MvPolynomial.isHomogeneous_zero (Fin 2) K 2
  convert hdet using 1
  rw [Fin.sum_univ_eq_sum_range
    (fun i : ℕ ↦ if i < 2 then 0 else 2) (m + 2)]
  rw [show m + 2 = 2 + m by omega, Finset.sum_range_add]
  have htail : ∀ x : ℕ, ¬ 2 + x < 2 := by omega
  simp [htail, Finset.sum_const, Nat.mul_comm]

/-! ## Exact output homogeneity of the frozen family -/

/-- The literal `H` at two constant pairs and the universal binary pair is a
named binary quadratic. -/
theorem HValue_binaryConstant_binaryPair_eq
    {K : Type*} [Field K] (q₁ q₂ : ProjectivePair K) :
    HValue (binaryConstantPair q₁).coord
        (binaryConstantPair q₂).coord binaryPair.coord =
      binaryQuadratic
        (q₁.u ^ 2 * q₂.v ^ 2 + q₁.v ^ 2 * q₂.u ^ 2 -
          2 * q₁.u * q₁.v * q₂.u * q₂.v)
        (-2 * q₁.u ^ 2 * q₂.u * q₂.v -
          2 * q₁.u * q₁.v * q₂.u ^ 2 -
          28 * q₁.v ^ 2 * q₂.v ^ 2)
        (q₁.u ^ 2 * q₂.u ^ 2 -
          28 * (q₁.u * q₁.v * q₂.v ^ 2 +
            q₁.v ^ 2 * q₂.u * q₂.v)) := by
  simp [HValue, binaryConstantPair, binaryPair, ProjectivePair.coord,
    binaryQuadratic]
  have hC2 :
      (MvPolynomial.C (2 : K) : MvPolynomial (Fin 2) K) = 2 := by
    simpa using
      (map_ofNat (MvPolynomial.C : K →+* MvPolynomial (Fin 2) K) 2)
  have hC28 :
      (MvPolynomial.C (28 : K) : MvPolynomial (Fin 2) K) = 28 := by
    simpa using
      (map_ofNat (MvPolynomial.C : K →+* MvPolynomial (Fin 2) K) 28)
  rw [hC2, hC28]
  ring

/-- The actual frozen output after any coefficient map and leaf
specialization is homogeneous of its declared output degree.  The successor
case uses the literal Sylvester row split and needs no induction hypothesis. -/
theorem projectiveOutputAtOver_frozenC_isHomogeneous
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (s : ℕ) (q : ℕ → ProjectivePair K) :
    (projectiveOutputAtOver φ (frozenC k s) q).IsHomogeneous
      (2 ^ (s + 1)) := by
  cases s with
  | zero =>
      rw [show
        projectiveOutputAtOver φ (frozenC k 0) q =
          HValue (binaryConstantPair (q 0)).coord
            (binaryConstantPair (q 1)).coord binaryPair.coord by
        simp [projectiveOutputAtOver, frozenC, specializeOver, HValue,
          leafPair, outputPair, binaryConstantPair, binaryPair,
          ProjectivePair.coord]]
      rw [HValue_binaryConstant_binaryPair_eq]
      exact binaryQuadratic_isHomogeneous _ _ _
  | succ s =>
      unfold projectiveOutputAtOver
      rw [specialize_frozenC_succ_over]
      rw [previousSliceAtOver_binaryConstantPair]
      have h := taskSylvester_isHomogeneous_two_mul_left
        ((previousSliceAtOver φ (frozenC k s) q).map MvPolynomial.C)
        (localSliceAt (binaryConstantPair (q (s + 2))) binaryPair)
        (2 ^ (s + 1))
        (by
          intro i
          rw [Polynomial.coeff_map]
          exact MvPolynomial.isHomogeneous_C (Fin 2) _)
        (by
          intro i
          exact localSliceAt_binaryPair_coeff_isHomogeneous _ _)
      convert h using 1
      simp only [pow_succ]
      ring

/-- The declared-degree homogenization of the predecessor slice is exactly
the actual frozen projective output form. -/
theorem homogenize_previousSliceAtOver_frozenC
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (s : ℕ) (q : ℕ → ProjectivePair K) :
    (previousSliceAtOver φ (frozenC k s) q).homogenize
        (2 ^ (s + 1)) =
      projectiveOutputAtOver φ (frozenC k s) q := by
  apply Polynomial.homogenize_eq_of_isHomogeneous
    (projectiveOutputAtOver_frozenC_isHomogeneous φ s q)
  exact dehomogenize_projectiveOutputAtOver φ _ q

/-- Evaluation of the declared predecessor homogenization at every valid
projective pair, including `[1:0]`, is direct frozen specialization. -/
theorem eval_homogenize_previousSliceAtOver_frozenC
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (s : ℕ)
    (q : ℕ → ProjectivePair K) (z : ProjectivePair K) :
    MvPolynomial.eval ![z.u, z.v]
        ((previousSliceAtOver φ (frozenC k s) q).homogenize
          (2 ^ (s + 1))) =
      specializeOver φ q z (frozenC k s) := by
  rw [homogenize_previousSliceAtOver_frozenC]
  exact eval_projectiveOutputAtOver φ _ q z

/-- Explicit affine-chart fixture for the frozen predecessor bridge. -/
theorem eval_homogenize_previousSliceAtOver_frozenC_affine
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (s : ℕ)
    (q : ℕ → ProjectivePair K) (t : K) :
    MvPolynomial.eval ![t, 1]
        ((previousSliceAtOver φ (frozenC k s) q).homogenize
          (2 ^ (s + 1))) =
      specializeOver φ q (.affine t) (frozenC k s) :=
  eval_homogenize_previousSliceAtOver_frozenC φ s q (.affine t)

/-- Explicit infinity-chart fixture for the frozen predecessor bridge. -/
theorem eval_homogenize_previousSliceAtOver_frozenC_infinity
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (s : ℕ)
    (q : ℕ → ProjectivePair K) :
    MvPolynomial.eval ![(1 : K), 0]
        ((previousSliceAtOver φ (frozenC k s) q).homogenize
          (2 ^ (s + 1))) =
      specializeOver φ q .infinity (frozenC k s) :=
  eval_homogenize_previousSliceAtOver_frozenC φ s q .infinity

/-! ## Exact local projective bridge -/

/-- The literal triquadratic is invariant under cyclic permutation of its
three projective arguments. -/
theorem HValue_cycle
    {R : Type*} [CommRing R] (q₁ q₂ q₃ : Axis → R) :
    HValue q₁ q₂ q₃ = HValue q₂ q₃ q₁ := by
  unfold HValue
  ring

/-- The universal binary form underlying the concrete local operand
`H([T:1],q,y)`. -/
noncomputable def localProjectiveAt
    {K : Type*} [Field K] (q y : ProjectivePair K) :
    MvPolynomial (Fin 2) K :=
  HValue binaryPair.coord
    (binaryConstantPair q).coord
    (binaryConstantPair y).coord

/-- The universal local binary form is homogeneous of its declared degree
two. -/
theorem localProjectiveAt_isHomogeneous
    {K : Type*} [Field K] (q y : ProjectivePair K) :
    (localProjectiveAt q y).IsHomogeneous 2 := by
  unfold localProjectiveAt
  rw [HValue_cycle]
  rw [HValue_binaryConstant_binaryPair_eq]
  exact binaryQuadratic_isHomogeneous _ _ _

/-- Dehomogenizing the universal local binary form on `[X:1]` is exactly the
concrete local slice. -/
theorem dehomogenize_localProjectiveAt
    {K : Type*} [Field K] (q y : ProjectivePair K) :
    MvPolynomial.aeval ![(Polynomial.X : K[X]), 1]
        (localProjectiveAt q y) =
      localSliceAt q y := by
  simp [localProjectiveAt, localSliceAt, HValue, binaryPair,
    binaryConstantPair, ProjectivePair.coord]

/-- The declared-degree homogenization of the local affine slice is exactly
its universal projective form. -/
theorem homogenize_localSliceAt
    {K : Type*} [Field K] (q y : ProjectivePair K) :
    (localSliceAt q y).homogenize 2 = localProjectiveAt q y := by
  apply Polynomial.homogenize_eq_of_isHomogeneous
    (localProjectiveAt_isHomogeneous q y)
  exact dehomogenize_localProjectiveAt q y

/-- Evaluation of the local universal form is the literal projective
triquadratic, for finite and infinite representatives alike. -/
theorem eval_localProjectiveAt
    {K : Type*} [Field K] (q y z : ProjectivePair K) :
    MvPolynomial.eval ![z.u, z.v] (localProjectiveAt q y) =
      HValue z.coord q.coord y.coord := by
  simp [localProjectiveAt, HValue, binaryPair, binaryConstantPair,
    ProjectivePair.coord]

/-- Exact local projective bridge used at every recursive witness step. -/
theorem eval_homogenize_localSliceAt
    {K : Type*} [Field K] (q y z : ProjectivePair K) :
    MvPolynomial.eval ![z.u, z.v]
        ((localSliceAt q y).homogenize 2) =
      HValue z.coord q.coord y.coord := by
  rw [homogenize_localSliceAt]
  exact eval_localProjectiveAt q y z

/-- Explicit affine-chart fixture for the local projective bridge. -/
theorem eval_homogenize_localSliceAt_affine
    {K : Type*} [Field K] (q y : ProjectivePair K) (t : K) :
    MvPolynomial.eval ![t, 1] ((localSliceAt q y).homogenize 2) =
      HValue (ProjectivePair.affine t).coord q.coord y.coord :=
  eval_homogenize_localSliceAt q y (.affine t)

/-- Explicit infinity-chart fixture for the local projective bridge. -/
theorem eval_homogenize_localSliceAt_infinity
    {K : Type*} [Field K] (q y : ProjectivePair K) :
    MvPolynomial.eval ![(1 : K), 0]
        ((localSliceAt q y).homogenize 2) =
      HValue (ProjectivePair.infinity (K := K)).coord q.coord y.coord :=
  eval_homogenize_localSliceAt q y .infinity

/-! ## Recursive projective witness chain -/

/-- A left-associated chain of valid projective intermediate witnesses for
the literal frozen family.  The level-zero case is `C₂`; each successor adds
one fresh leaf and one projective intermediate pair. -/
def FrozenProjectiveChain
    {K : Type*} [CommRing K] (q : ℕ → ProjectivePair K) :
    ℕ → ProjectivePair K → Prop
  | 0, y =>
      HValue (q 0).coord (q 1).coord y.coord = 0
  | s + 1, y =>
      ∃ z : ProjectivePair K,
        FrozenProjectiveChain q s z ∧
        HValue z.coord (q (s + 2)).coord y.coord = 0

/-- Direct specialization of the base member `C₂`. -/
theorem specializeOver_frozenC_zero
    {k K : Type*} [CommRing k] [CommRing K]
    (φ : k →+* K) (q : ℕ → ProjectivePair K)
    (y : ProjectivePair K) :
    specializeOver φ q y (frozenC k 0) =
      HValue (q 0).coord (q 1).coord y.coord := by
  simp [frozenC, specializeOver, HValue, leafPair, outputPair,
    ProjectivePair.coord]

/-- Vanishing of every actual frozen member is equivalent to a complete
chain of valid projective intermediate witnesses in the algebraically closed
target field.

No injectivity of the coefficient map is required.  The conclusion is a
chain in `K`; it does not assert descent of intermediate witnesses to a
smaller source field. -/
theorem specializeOver_frozenC_eq_zero_iff_projectiveChain
    {k K : Type*} [CommRing k] [Field K] [IsAlgClosed K]
    (φ : k →+* K) (s : ℕ)
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    specializeOver φ q y (frozenC k s) = 0 ↔
      FrozenProjectiveChain q s y := by
  induction s generalizing y with
  | zero =>
      rw [specializeOver_frozenC_zero]
      rfl
  | succ s ih =>
      rw [specialize_frozenC_succ_over_eq_zero_iff_common_projective_root]
      constructor
      · rintro ⟨U, V, hvalid, hprevious, hlocal⟩
        let z : ProjectivePair K :=
          { u := U
            v := V
            valid := hvalid }
        refine ⟨z, ?_, ?_⟩
        · apply (ih z).mp
          rw [← eval_homogenize_previousSliceAtOver_frozenC]
          exact hprevious
        · rw [← eval_homogenize_localSliceAt]
          exact hlocal
      · rintro ⟨z, hprevious, hlocal⟩
        refine ⟨z.u, z.v, z.valid, ?_, ?_⟩
        · rw [eval_homogenize_previousSliceAtOver_frozenC]
          exact (ih z).mpr hprevious
        · rw [eval_homogenize_localSliceAt]
          exact hlocal

/-- The concrete frozen `C₁₆` member has exactly the recursive projective
witness-chain semantics: leaves `q 0` through `q 15` and fourteen valid
intermediate projective pairs. -/
theorem specializeOver_frozenC16_eq_zero_iff_projectiveChain
    {k K : Type*} [CommRing k] [Field K] [IsAlgClosed K]
    (φ : k →+* K) (q : ℕ → ProjectivePair K)
    (y : ProjectivePair K) :
    specializeOver φ q y (frozenC k 14) = 0 ↔
      FrozenProjectiveChain q 14 y :=
  specializeOver_frozenC_eq_zero_iff_projectiveChain φ 14 q y

end Ecdlp.FrozenProjectiveSemaev
