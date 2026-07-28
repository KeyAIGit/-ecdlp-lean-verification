import Mathlib.Algebra.MvPolynomial.Equiv
import Ecdlp.Proved.TaskSylvesterConvention

/-!
# Frozen recursive projective Semaev family

This module gives the frozen TASK-018 recursive projective family an exact
Lean definition.  It uses the literal triquadratic form `H`, the frozen
left-fold leaf order, fixed resultant degrees, and the TASK-018 Sylvester
matrix convention.  No primitive-part, content, monic, actual-degree, or unit
normalization is inserted.

The stage index is deliberately offset:

* `frozenC R 0` is the form called `C₂`;
* `frozenC R s` is the form called `C_(s+2)`;
* `frozenC R 14` is therefore `C₁₆`.

At successor stage `s + 1`, the new form is the fixed resultant of
`C_(s+2)(Q₁,...,Q_(s+2);T)` and `H(T,Q_(s+3),Y)` at formal degrees
`(2^(s+1), 2)`.  If the mathematical target index is `r = s + 3`, this is
exactly `(2^(r-2), 2)`.

The principal theorems prove that specialization, including an explicit
coefficient map, commutes with this actual recursive family and lands in the
literal TASK-018 determinant with coefficient unit exactly `1`.  Affine
output `[y:1]` and infinity output `[1:0]` are separate corollaries.

The module also proves the uniform output-slice degree bound for every frozen
stage.  Consequently the common-projective-root interfaces are unconditional:
the formal predecessor degree used by the fixed resultant is always large
enough after every coefficient map and projective leaf specialization.  This
module does not claim the still-open universal `C₁₆ -> C₂` reverse induction,
a direct-S17 equivalence, or any solving-cost result.

The recursive definition is a symbolic DAG.  Nothing here expands, evaluates,
or materializes `C₁₆`.
-/

namespace Ecdlp.FrozenProjectiveSemaev

open Polynomial

/-- The first and second coordinates of a projective pair `[U:V]`. -/
inductive Axis
  | u
  | v
  deriving DecidableEq

/-- Variables of the frozen family: zero-based external leaves and one
distinguished output pair.  Thus `leaf 0` represents `Q₁`. -/
inductive Var
  | leaf (i : ℕ) (a : Axis)
  | output (a : Axis)
  deriving DecidableEq

/-- A representative of a projective point with the irrelevant pair `[0:0]`
excluded. -/
structure ProjectivePair (K : Type*) [Zero K] where
  u : K
  v : K
  valid : u ≠ 0 ∨ v ≠ 0

namespace ProjectivePair

variable {K : Type*} [Zero K] [One K] [NeZero (1 : K)]

/-- The affine projective representative `[x:1]`. -/
def affine (x : K) : ProjectivePair K :=
  ⟨x, 1, Or.inr one_ne_zero⟩

/-- The distinguished infinity representative `[1:0]`. -/
def infinity : ProjectivePair K :=
  ⟨1, 0, Or.inl one_ne_zero⟩

/-- Select a coordinate of a valid projective representative. -/
def coord (q : ProjectivePair K) : Axis → K
  | .u => q.u
  | .v => q.v

end ProjectivePair

/-- The literal TASK-018 homogeneous triquadratic
`H(Q₁,Q₂,Q₃)` for `y² = x³ + 7`.

The argument and coordinate order is fixed, and the coefficient of the final
three-term block is exactly `-28`. -/
def HValue {R : Type*} [CommRing R]
    (q₁ q₂ q₃ : Axis → R) : R :=
  q₁ .u ^ 2 * q₂ .u ^ 2 * q₃ .v ^ 2 +
  q₁ .u ^ 2 * q₂ .v ^ 2 * q₃ .u ^ 2 +
  q₁ .v ^ 2 * q₂ .u ^ 2 * q₃ .u ^ 2 -
  2 * q₁ .u ^ 2 * q₂ .u * q₂ .v * q₃ .u * q₃ .v -
  2 * q₁ .u * q₁ .v * q₂ .u ^ 2 * q₃ .u * q₃ .v -
  2 * q₁ .u * q₁ .v * q₂ .u * q₂ .v * q₃ .u ^ 2 -
  28 * (
    q₁ .u * q₁ .v * q₂ .v ^ 2 * q₃ .v ^ 2 +
    q₁ .v ^ 2 * q₂ .u * q₂ .v * q₃ .v ^ 2 +
    q₁ .v ^ 2 * q₂ .v ^ 2 * q₃ .u * q₃ .v)

/-- The symbolic projective pair for zero-based external leaf `i`. -/
noncomputable def leafPair {R : Type*} [CommSemiring R] (i : ℕ) :
    Axis → MvPolynomial Var R
  | a => MvPolynomial.X (.leaf i a)

/-- The symbolic distinguished output pair. -/
noncomputable def outputPair {R : Type*} [CommSemiring R] :
    Axis → MvPolynomial Var R
  | a => MvPolynomial.X (.output a)

/-- Regard the distinguished output pair of a symbolic form as the eliminated
affine chart `[T:1]`, while all external leaves remain coefficient variables. -/
noncomputable def outputSlice {R : Type*} [CommRing R]
    (p : MvPolynomial Var R) :
    Polynomial (MvPolynomial Var R) :=
  MvPolynomial.eval₂Hom
    (Polynomial.C.comp (MvPolynomial.C : R →+* MvPolynomial Var R))
    (fun
      | .leaf i a => Polynomial.C (MvPolynomial.X (.leaf i a))
      | .output .u => Polynomial.X
      | .output .v => 1)
    p

/-- The right operand `H([T:1],Q_i,Y)` of one frozen resultant step. -/
noncomputable def localSlice {R : Type*} [CommRing R] (i : ℕ) :
    Polynomial (MvPolynomial Var R) :=
  HValue
    (fun
      | .u => Polynomial.X
      | .v => 1)
    (fun a => Polynomial.C (MvPolynomial.X (.leaf i a)))
    (fun a => Polynomial.C (MvPolynomial.X (.output a)))

/-- The actual frozen TASK-018 recursive family.

`frozenC R s` is the form called `C_(s+2)`.  The recursion is a left fold and
uses fixed formal degrees even when a specialization later drops actual
degree. -/
noncomputable def frozenC (R : Type*) [CommRing R] :
    ℕ → MvPolynomial Var R
  | 0 => HValue (leafPair 0) (leafPair 1) outputPair
  | s + 1 =>
      Polynomial.resultant
        (outputSlice (frozenC R s))
        (localSlice (s + 2))
        (2 ^ (s + 1)) 2

/-- The same-field assignment for all leaf and output variables. -/
def assignment {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) : Var → K
  | .leaf i a => (q i).coord a
  | .output a => y.coord a

/-- Same-field evaluation of a symbolic frozen form at valid projective
representatives. -/
def specialize {K : Type*} [Field K]
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    MvPolynomial Var K →+* K :=
  MvPolynomial.eval (assignment q y)

/-- Specialize the external leaves of a symbolic form while retaining its
output as the univariate affine chart `[T:1]`. -/
noncomputable def previousSliceAt {K : Type*} [Field K]
    (p : MvPolynomial Var K) (q : ℕ → ProjectivePair K) : K[X] :=
  MvPolynomial.eval₂Hom
    (Polynomial.C : K →+* K[X])
    (fun
      | .leaf i a => Polynomial.C ((q i).coord a)
      | .output .u => Polynomial.X
      | .output .v => 1)
    p

/-- The concrete local operand `H([T:1],q,y)`. -/
noncomputable def localSliceAt {K : Type*} [CommRing K]
    (q y : ProjectivePair K) : K[X] :=
  HValue
    (fun
      | .u => Polynomial.X
      | .v => 1)
    (fun a => Polynomial.C (q.coord a))
    (fun a => Polynomial.C (y.coord a))

/-- Same-field specialization commutes with turning the symbolic output into
the univariate chart `[T:1]`. -/
theorem map_outputSlice {K : Type*} [Field K]
    (p : MvPolynomial Var K)
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    (outputSlice p).map (specialize q y) = previousSliceAt p q := by
  change
    ((Polynomial.mapRingHom (specialize q y)).comp
      (MvPolynomial.eval₂Hom
        (Polynomial.C.comp (MvPolynomial.C : K →+* MvPolynomial Var K))
        (fun
          | .leaf i a => Polynomial.C (MvPolynomial.X (.leaf i a))
          | .output .u => Polynomial.X
          | .output .v => 1))) p =
      MvPolynomial.eval₂Hom
        (Polynomial.C : K →+* K[X])
        (fun
          | .leaf i a => Polynomial.C ((q i).coord a)
          | .output .u => Polynomial.X
          | .output .v => 1)
        p
  apply MvPolynomial.hom_eq_hom
  · ext k n
    simp [specialize, ProjectivePair.coord]
  · intro i
    cases i with
    | leaf i a => cases a <;> simp [specialize, assignment, ProjectivePair.coord]
    | output a => cases a <;> simp [specialize, ProjectivePair.coord]

/-- Same-field specialization of the symbolic right operand is exactly the
concrete local slice. -/
theorem map_localSlice {K : Type*} [Field K]
    (i : ℕ) (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    (localSlice i).map (specialize q y) = localSliceAt (q i) y := by
  simp [localSlice, localSliceAt, HValue, specialize, assignment,
    ProjectivePair.coord]

/-- The concrete local operand retains formal degree at most two under every
projective specialization, including degree drop. -/
theorem localSliceAt_natDegree_le {K : Type*} [Field K]
    (q y : ProjectivePair K) :
    (localSliceAt q y).natDegree ≤ 2 := by
  unfold localSliceAt HValue
  compute_degree

/-- Exact same-field specialization of one actual frozen recursive step.

The right side is the literal TASK-018 Sylvester determinant, so its
coefficient unit is exactly `1`. -/
theorem specialize_frozenC_succ {K : Type*} [Field K]
    (s : ℕ) (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    specialize q y (frozenC K (s + 1)) =
      (Ecdlp.TaskSylvester.taskSylvester
        (previousSliceAt (frozenC K s) q)
        (localSliceAt (q (s + 2)) y)
        (2 ^ (s + 1)) 2).det := by
  rw [Ecdlp.TaskSylvester.det_taskSylvester_eq_resultant]
  rw [frozenC]
  rw [← Polynomial.resultant_map_map]
  rw [map_outputSlice, map_localSlice]

/-- The affine-output branch `[y:1]` of exact frozen-step specialization. -/
theorem specialize_frozenC_succ_affine {K : Type*} [Field K]
    (s : ℕ) (q : ℕ → ProjectivePair K) (y : K) :
    specialize q (.affine y) (frozenC K (s + 1)) =
      (Ecdlp.TaskSylvester.taskSylvester
        (previousSliceAt (frozenC K s) q)
        (localSliceAt (q (s + 2)) (.affine y))
        (2 ^ (s + 1)) 2).det :=
  specialize_frozenC_succ s q (.affine y)

/-- The output-infinity branch `[1:0]` of exact frozen-step specialization. -/
theorem specialize_frozenC_succ_infinity {K : Type*} [Field K]
    (s : ℕ) (q : ℕ → ProjectivePair K) :
    specialize q .infinity (frozenC K (s + 1)) =
      (Ecdlp.TaskSylvester.taskSylvester
        (previousSliceAt (frozenC K s) q)
        (localSliceAt (q (s + 2)) .infinity)
        (2 ^ (s + 1)) 2).det :=
  specialize_frozenC_succ s q .infinity

/-- Reusable one-step reverse interface for the same-field frozen family under
an explicit predecessor degree bound.

The root predicate excludes the eliminated irrelevant pair `[0:0]` and
retains affine and infinity roots.  The bound is discharged uniformly below. -/
theorem specialize_frozenC_succ_eq_zero_iff_common_projective_root_of_natDegree_le
    {K : Type*} [Field K] [IsAlgClosed K]
    (s : ℕ) (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hprev :
      (previousSliceAt (frozenC K s) q).natDegree ≤ 2 ^ (s + 1)) :
    specialize q y (frozenC K (s + 1)) = 0 ↔
      Ecdlp.ProjectiveResultant.HasCommonProjectiveRoot
        (previousSliceAt (frozenC K s) q)
        (localSliceAt (q (s + 2)) y)
        (2 ^ (s + 1)) 2 := by
  rw [specialize_frozenC_succ]
  exact Ecdlp.TaskSylvester.det_taskSylvester_eq_zero_iff_common_projective_root
    _ _ (by positivity) (by norm_num) hprev (localSliceAt_natDegree_le _ _)

/-! ## Explicit coefficient-map specialization -/

/-- Evaluate a symbolic source-ring frozen form after applying the named
coefficient map and assigning valid target-ring projective representatives. -/
def specializeOver {k K : Type*} [CommRing k] [CommRing K]
    (φ : k →+* K) (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    MvPolynomial Var k →+* K :=
  MvPolynomial.eval₂Hom φ (fun
    | .leaf i a => (q i).coord a
    | .output a => y.coord a)

/-- Apply a coefficient map and specialize the external leaves while retaining
the distinguished output as `[T:1]`. -/
noncomputable def previousSliceAtOver {k K : Type*} [CommRing k] [CommRing K]
    (φ : k →+* K) (p : MvPolynomial Var k)
    (q : ℕ → ProjectivePair K) : K[X] :=
  MvPolynomial.eval₂Hom
    (Polynomial.C.comp φ)
    (fun
      | .leaf i a => Polynomial.C ((q i).coord a)
      | .output .u => Polynomial.X
      | .output .v => 1)
    p

/-- Coefficient-map specialization commutes with turning the symbolic output
into the univariate chart `[T:1]`. -/
theorem map_outputSlice_over {k K : Type*} [CommRing k] [CommRing K]
    (φ : k →+* K) (p : MvPolynomial Var k)
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    (outputSlice p).map (specializeOver φ q y) =
      previousSliceAtOver φ p q := by
  change
    ((Polynomial.mapRingHom (specializeOver φ q y)).comp
      (MvPolynomial.eval₂Hom
        (Polynomial.C.comp (MvPolynomial.C : k →+* MvPolynomial Var k))
        (fun
          | .leaf i a => Polynomial.C (MvPolynomial.X (.leaf i a))
          | .output .u => Polynomial.X
          | .output .v => 1))) p =
      MvPolynomial.eval₂Hom
        (Polynomial.C.comp φ)
        (fun
          | .leaf i a => Polynomial.C ((q i).coord a)
          | .output .u => Polynomial.X
          | .output .v => 1)
        p
  apply MvPolynomial.hom_eq_hom
  · ext a n
    simp [specializeOver, ProjectivePair.coord]
  · intro i
    cases i with
    | leaf i a => cases a <;> simp [specializeOver, ProjectivePair.coord]
    | output a => cases a <;> simp [specializeOver, ProjectivePair.coord]

/-- Coefficient-map specialization of the symbolic right operand is exactly
the concrete target-ring local slice. -/
theorem map_localSlice_over {k K : Type*} [CommRing k] [CommRing K]
    (φ : k →+* K) (i : ℕ)
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    (localSlice (R := k) i).map (specializeOver φ q y) =
      localSliceAt (q i) y := by
  simp [localSlice, localSliceAt, HValue, specializeOver,
    ProjectivePair.coord]

/-- Exact coefficient-map specialization of one actual frozen recursive step.

This is the TASK-020 binding theorem.  It names the concrete frozen family,
keeps formal degrees `(2^(s+1),2)`, and equals the literal TASK-018 determinant
with coefficient unit exactly `1`. -/
theorem specialize_frozenC_succ_over
    {k K : Type*} [CommRing k] [CommRing K]
    (φ : k →+* K) (s : ℕ)
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    specializeOver φ q y (frozenC k (s + 1)) =
      (Ecdlp.TaskSylvester.taskSylvester
        (previousSliceAtOver φ (frozenC k s) q)
        (localSliceAt (q (s + 2)) y)
        (2 ^ (s + 1)) 2).det := by
  rw [Ecdlp.TaskSylvester.det_taskSylvester_eq_resultant]
  rw [frozenC]
  rw [← Polynomial.resultant_map_map]
  rw [map_outputSlice_over, map_localSlice_over]

/-- The affine-output branch `[y:1]` of coefficient-map specialization. -/
theorem specialize_frozenC_succ_over_affine
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (s : ℕ)
    (q : ℕ → ProjectivePair K) (y : K) :
    specializeOver φ q (.affine y) (frozenC k (s + 1)) =
      (Ecdlp.TaskSylvester.taskSylvester
        (previousSliceAtOver φ (frozenC k s) q)
        (localSliceAt (q (s + 2)) (.affine y))
        (2 ^ (s + 1)) 2).det :=
  specialize_frozenC_succ_over φ s q (.affine y)

/-- The output-infinity branch `[1:0]` of coefficient-map specialization. -/
theorem specialize_frozenC_succ_over_infinity
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (s : ℕ)
    (q : ℕ → ProjectivePair K) :
    specializeOver φ q .infinity (frozenC k (s + 1)) =
      (Ecdlp.TaskSylvester.taskSylvester
        (previousSliceAtOver φ (frozenC k s) q)
        (localSliceAt (q (s + 2)) .infinity)
        (2 ^ (s + 1)) 2).det :=
  specialize_frozenC_succ_over φ s q .infinity

/-- Reusable one-step reverse interface after an explicit coefficient map and
under an explicit predecessor degree bound.

The local degree-two bound, fixed formal degrees, literal determinant
convention, and non-irrelevant common-root domain are kernel checked.  The
predecessor bound is discharged uniformly below. -/
theorem specialize_frozenC_succ_over_eq_zero_iff_common_projective_root_of_natDegree_le
    {k K : Type*} [CommRing k] [Field K] [IsAlgClosed K]
    (φ : k →+* K) (s : ℕ)
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K)
    (hprev :
      (previousSliceAtOver φ (frozenC k s) q).natDegree ≤ 2 ^ (s + 1)) :
    specializeOver φ q y (frozenC k (s + 1)) = 0 ↔
      Ecdlp.ProjectiveResultant.HasCommonProjectiveRoot
        (previousSliceAtOver φ (frozenC k s) q)
        (localSliceAt (q (s + 2)) y)
        (2 ^ (s + 1)) 2 := by
  rw [specialize_frozenC_succ_over]
  exact Ecdlp.TaskSylvester.det_taskSylvester_eq_zero_iff_common_projective_root
    _ _ (by positivity) (by norm_num) hprev (localSliceAt_natDegree_le _ _)

/-! ## Narrow determinant-degree tool -/

/-- If every entry in row `i` of a square polynomial matrix has degree at
most `w i`, then the determinant has degree at most the sum of the row
weights.

This is the precise determinant estimate needed for a later proof of the
uniform predecessor-slice degree bound.  It does not assert that bound here. -/
theorem natDegree_det_le_sum_row
    {K ι : Type*} [Field K] [Fintype ι] [DecidableEq ι]
    (A : Matrix ι ι K[X]) (w : ι → ℕ)
    (hA : ∀ i j, (A i j).natDegree ≤ w i) :
    A.det.natDegree ≤ ∑ i, w i := by
  rw [Matrix.det_apply]
  apply Polynomial.natDegree_sum_le_of_forall_le
  intro σ hσ
  calc
    (Equiv.Perm.sign σ • ∏ i, A (σ i) i).natDegree
        ≤ (∏ i, A (σ i) i).natDegree := by
      exact Polynomial.natDegree_smul_le _ _
    _ ≤ ∑ i, w (σ i) :=
      (Polynomial.natDegree_prod_le (Finset.univ)
        (fun i => A (σ i) i)).trans
        (Finset.sum_le_sum fun i _ => hA (σ i) i)
    _ = ∑ i, w i := by
      exact Equiv.sum_comp σ w

/-! ## Uniform output-slice degree bound -/

/-- Embed a valid projective pair as a constant projective pair over a
polynomial ring. -/
noncomputable def constantPair {K : Type*} [Field K]
    (q : ProjectivePair K) : ProjectivePair K[X] where
  u := Polynomial.C q.u
  v := Polynomial.C q.v
  valid := by
    rcases q.valid with hu | hv
    · exact Or.inl (Polynomial.C_ne_zero.mpr hu)
    · exact Or.inr (Polynomial.C_ne_zero.mpr hv)

/-- Taking a predecessor slice after embedding every projective leaf as a
constant polynomial is the coefficientwise constant embedding of the
original predecessor slice. -/
theorem previousSliceAtOver_constantPair
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (p : MvPolynomial Var k)
    (q : ℕ → ProjectivePair K) :
    previousSliceAtOver (Polynomial.C.comp φ) p
        (fun i ↦ constantPair (q i)) =
      (previousSliceAtOver φ p q).map Polynomial.C := by
  change
    MvPolynomial.eval₂Hom
        (Polynomial.C.comp (Polynomial.C.comp φ))
        (fun
          | .leaf i a => Polynomial.C ((constantPair (q i)).coord a)
          | .output .u => Polynomial.X
          | .output .v => 1)
        p =
      ((Polynomial.mapRingHom Polynomial.C).comp
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
        cases a <;> simp [constantPair, ProjectivePair.coord]
    | output a =>
        cases a <;> simp

/-- A predecessor slice over `K` is the full frozen specialization over
`K[X]` at the symbolic affine output `[X:1]` and constant embedded leaves. -/
theorem previousSliceAtOver_eq_specializeOver_polynomial
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (p : MvPolynomial Var k)
    (q : ℕ → ProjectivePair K) :
    previousSliceAtOver φ p q =
      specializeOver (Polynomial.C.comp φ)
        (fun i ↦ constantPair (q i))
        (ProjectivePair.affine Polynomial.X)
        p := by
  change
    MvPolynomial.eval₂Hom
        (Polynomial.C.comp φ)
        (fun
          | .leaf i a => Polynomial.C ((q i).coord a)
          | .output .u => Polynomial.X
          | .output .v => 1)
        p =
      MvPolynomial.eval₂Hom
        (Polynomial.C.comp φ)
        (fun
          | .leaf i a => (constantPair (q i)).coord a
          | .output a => (ProjectivePair.affine Polynomial.X).coord a)
        p
  apply MvPolynomial.hom_eq_hom
  · ext a n
    simp
  · intro i
    cases i with
    | leaf i a =>
        cases a <;> simp [constantPair, ProjectivePair.coord]
    | output a =>
        cases a <;> simp [ProjectivePair.affine, ProjectivePair.coord]

/-- Every coefficient of a polynomial mapped into the constant subring has
outer polynomial degree zero. -/
theorem coeff_map_C_natDegree
    {K : Type*} [Field K] (p : K[X]) (i : ℕ) :
    ((p.map Polynomial.C).coeff i).natDegree = 0 := by
  rw [Polynomial.coeff_map, Polynomial.natDegree_C]

/-- Literal expansion of `H([T:1],q,[X:1])` as a polynomial in `T` whose
coefficients are polynomials in the new output `X`. -/
theorem localSliceAt_constantPair_affine_explicit
    {K : Type*} [Field K] (q : ProjectivePair K) :
    localSliceAt (constantPair q) (ProjectivePair.affine Polynomial.X) =
      Polynomial.monomial 2
          (Polynomial.C q.u ^ 2 +
            Polynomial.C q.v ^ 2 * Polynomial.X ^ 2 -
            2 * Polynomial.C q.u * Polynomial.C q.v * Polynomial.X) +
        Polynomial.monomial 1
          (-2 * Polynomial.C q.u ^ 2 * Polynomial.X -
            2 * Polynomial.C q.u * Polynomial.C q.v * Polynomial.X ^ 2 -
            28 * Polynomial.C q.v ^ 2) +
        Polynomial.C
          (Polynomial.C q.u ^ 2 * Polynomial.X ^ 2 -
            28 * (Polynomial.C q.u * Polynomial.C q.v +
              Polynomial.C q.v ^ 2 * Polynomial.X)) := by
  simp [localSliceAt, HValue, constantPair, ProjectivePair.affine,
    ProjectivePair.coord]
  simp only [← Polynomial.C_mul_X_pow_eq_monomial]
  simp only [Polynomial.C_mul, Polynomial.C_pow, Polynomial.C_ofNat]
  ring

/-- Every `T`-coefficient of `H([T:1],q,[X:1])` has degree at most two in
the new output `X`. -/
theorem localSliceAt_constantPair_affine_coeff_natDegree_le
    {K : Type*} [Field K] (q : ProjectivePair K) (i : ℕ) :
    ((localSliceAt (constantPair q)
      (ProjectivePair.affine Polynomial.X)).coeff i).natDegree ≤ 2 := by
  rw [localSliceAt_constantPair_affine_explicit]
  simp only [Polynomial.coeff_add, Polynomial.coeff_monomial,
    Polynomial.coeff_C]
  split_ifs with h2 h1 h0
  all_goals try omega
  all_goals simp_all
  all_goals try compute_degree
  all_goals simp only [max_le_iff]
  all_goals omega

/-- For the literal TASK-018 Sylvester layout, constant coefficients in the
left operand and degree-two coefficients in the right operand give determinant
degree at most `2 * m`.  The first two rows have weight zero and the remaining
`m` rows have weight two. -/
theorem taskSylvester_natDegree_le_two_mul_left
    {K : Type*} [Field K]
    (f g : (K[X])[X]) (m : ℕ)
    (hf : ∀ i, (f.coeff i).natDegree ≤ 0)
    (hg : ∀ i, (g.coeff i).natDegree ≤ 2) :
    (Ecdlp.TaskSylvester.taskSylvester f g m 2).det.natDegree ≤ 2 * m := by
  calc
    (Ecdlp.TaskSylvester.taskSylvester f g m 2).det.natDegree
        ≤ ∑ i : Fin (m + 2), if (i : ℕ) < 2 then 0 else 2 := by
      apply natDegree_det_le_sum_row
      intro i j
      simp only [Ecdlp.TaskSylvester.taskSylvester, Matrix.of_apply]
      by_cases hi : (i : ℕ) < 2
      · rw [if_pos hi]
        simp only [Ecdlp.TaskSylvester.descendingShift]
        split_ifs
        · simpa using hf _
        · simp
      · rw [if_neg hi]
        simp only [Ecdlp.TaskSylvester.descendingShift]
        split_ifs
        · simpa using hg _
        · simp
    _ = 2 * m := by
      rw [Fin.sum_univ_eq_sum_range
        (fun i : ℕ ↦ if i < 2 then 0 else 2) (m + 2)]
      rw [show m + 2 = 2 + m by omega, Finset.sum_range_add]
      have htail : ∀ x : ℕ, ¬ 2 + x < 2 := by omega
      simp [htail, Finset.sum_const, Nat.mul_comm]

/-- Uniform TASK-020 output-slice degree bound for the actual frozen family,
after every coefficient map and every valid projective leaf specialization.

For `frozenC k s = C_(s+2)`, the affine output degree is at most
`2^(s+1)`.  No induction hypothesis is needed: at a successor, the literal
Sylvester matrix has two output-constant rows and `2^(s+1)` rows of output
degree at most two. -/
theorem previousSliceAtOver_frozenC_natDegree_le
    {k K : Type*} [CommRing k] [Field K]
    (φ : k →+* K) (s : ℕ) (q : ℕ → ProjectivePair K) :
    (previousSliceAtOver φ (frozenC k s) q).natDegree ≤ 2 ^ (s + 1) := by
  cases s with
  | zero =>
      simp only [frozenC, previousSliceAtOver, HValue, leafPair, outputPair,
        ProjectivePair.coord]
      norm_num
      compute_degree
  | succ s =>
      rw [previousSliceAtOver_eq_specializeOver_polynomial]
      rw [specialize_frozenC_succ_over]
      apply (taskSylvester_natDegree_le_two_mul_left _ _ _ ?_ ?_).trans_eq
      · simp only [pow_succ]
        ring
      · intro i
        rw [previousSliceAtOver_constantPair]
        exact (coeff_map_C_natDegree _ _).le
      · intro i
        exact localSliceAt_constantPair_affine_coeff_natDegree_le _ _

/-! ## Unconditional one-step reverse interfaces -/

/-- Unconditional one-step reverse interface for the same-field frozen
family. -/
theorem specialize_frozenC_succ_eq_zero_iff_common_projective_root
    {K : Type*} [Field K] [IsAlgClosed K]
    (s : ℕ) (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    specialize q y (frozenC K (s + 1)) = 0 ↔
      Ecdlp.ProjectiveResultant.HasCommonProjectiveRoot
        (previousSliceAt (frozenC K s) q)
        (localSliceAt (q (s + 2)) y)
        (2 ^ (s + 1)) 2 :=
  specialize_frozenC_succ_eq_zero_iff_common_projective_root_of_natDegree_le
    s q y (previousSliceAtOver_frozenC_natDegree_le (RingHom.id K) s q)

/-- Unconditional one-step reverse interface after an explicit coefficient
map. -/
theorem specialize_frozenC_succ_over_eq_zero_iff_common_projective_root
    {k K : Type*} [CommRing k] [Field K] [IsAlgClosed K]
    (φ : k →+* K) (s : ℕ)
    (q : ℕ → ProjectivePair K) (y : ProjectivePair K) :
    specializeOver φ q y (frozenC k (s + 1)) = 0 ↔
      Ecdlp.ProjectiveResultant.HasCommonProjectiveRoot
        (previousSliceAtOver φ (frozenC k s) q)
        (localSliceAt (q (s + 2)) y)
        (2 ^ (s + 1)) 2 :=
  specialize_frozenC_succ_over_eq_zero_iff_common_projective_root_of_natDegree_le
    φ s q y (previousSliceAtOver_frozenC_natDegree_le φ s q)

end Ecdlp.FrozenProjectiveSemaev
