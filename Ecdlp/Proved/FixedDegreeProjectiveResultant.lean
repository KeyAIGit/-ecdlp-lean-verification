import Mathlib.Algebra.Polynomial.Homogenize
import Mathlib.FieldTheory.IsAlgClosed.Basic
import Mathlib.RingTheory.Polynomial.Resultant.Basic

/-!
# Fixed-degree projective resultants

This narrow module packages Mathlib's fixed-size univariate resultant as the
resultant of two binary homogeneous forms.  A polynomial `f` with declared
degree `m` represents `f.homogenize m`; declared leading zero coefficients are
therefore retained.

The main theorem is set-theoretic.  For positive formal degrees over an
algebraically closed field, the fixed-size resultant vanishes exactly when the
two homogenized forms share a non-irrelevant projective pair.  In particular,
the degree-drop branch is witnessed by `[1:0]`.

No primitive-part, content, monic, actual-degree, or unit normalization is
performed here.
-/

namespace Ecdlp.ProjectiveResultant

open Polynomial

/-- The two fixed-degree homogenizations share a projective root represented
by a non-irrelevant coordinate pair `(U,V)`. -/
def HasCommonProjectiveRoot
    {K : Type*} [Field K] (f g : K[X]) (m n : ℕ) : Prop :=
  ∃ U V : K, (U ≠ 0 ∨ V ≠ 0) ∧
    MvPolynomial.eval ![U, V] (f.homogenize m) = 0 ∧
    MvPolynomial.eval ![U, V] (g.homogenize n) = 0

/-- Evaluation of a declared-degree homogenization on the infinity chart.
This is the retained formal leading coefficient, scaled by `U ^ n`. -/
theorem eval_homogenize_second_zero
    {K : Type*} [Field K] (p : K[X]) (n : ℕ) (U : K) :
    MvPolynomial.eval ![U, 0] (p.homogenize n) = p.coeff n * U ^ n := by
  simp only [Polynomial.homogenize, MvPolynomial.eval_sum]
  rw [Finset.sum_eq_single (n, 0)]
  · simp [MvPolynomial.eval_monomial, Finsupp.prod_fintype, Fin.prod_univ_two]
  · intro kl hkl hne
    have hsum : kl.1 + kl.2 = n := Finset.mem_antidiagonal.mp hkl
    have hpos : 0 < kl.2 := by
      by_contra h
      have hz : kl.2 = 0 := Nat.eq_zero_of_not_pos h
      apply hne
      apply Prod.ext
      · simpa [hz] using hsum
      · exact hz
    simp [MvPolynomial.eval_monomial, Finsupp.prod_fintype, Fin.prod_univ_two,
      Nat.ne_of_gt hpos]
  · simp

/-- At the distinguished infinity representative `[1:0]`, a declared-degree
homogenization evaluates to its retained formal leading coefficient. -/
@[simp] theorem eval_homogenize_one_zero
    {K : Type*} [Field K] (p : K[X]) (n : ℕ) :
    MvPolynomial.eval ![(1 : K), 0] (p.homogenize n) = p.coeff n := by
  simp [eval_homogenize_second_zero]

/-- The distinguished infinity representative `[1:0]` is a common root
exactly when both retained formal leading coefficients vanish. -/
theorem one_zero_is_common_root_iff
    {K : Type*} [Field K] (f g : K[X]) (m n : ℕ) :
    (MvPolynomial.eval ![(1 : K), 0] (f.homogenize m) = 0 ∧
      MvPolynomial.eval ![(1 : K), 0] (g.homogenize n) = 0) ↔
      f.coeff m = 0 ∧ g.coeff n = 0 := by
  simp

/-- Under a declared degree bound, a vanishing formal leading coefficient at a
positive degree is equivalent to strict degree drop.  The zero polynomial is
included explicitly. -/
theorem natDegree_lt_of_le_of_coeff_eq_zero
    {K : Type*} [Field K] {p : K[X]} {n : ℕ}
    (hn : 0 < n) (hdeg : p.natDegree ≤ n) (hc : p.coeff n = 0) :
    p.natDegree < n := by
  by_cases hp : p = 0
  · simpa [hp] using hn
  · refine lt_of_le_of_ne hdeg ?_
    intro heq
    have hcoeffNatDegree : p.coeff p.natDegree = 0 := by
      rw [heq]
      exact hc
    have hlc : p.leadingCoeff = 0 := by
      simpa using hcoeffNatDegree
    exact (leadingCoeff_ne_zero.mpr hp) hlc

/-- If the fixed-size resultant vanishes and the left polynomial attains its
declared positive degree, the two polynomials have a common affine root. -/
private theorem exists_affine_common_root_of_left_degree
    {K : Type*} [Field K] [IsAlgClosed K]
    (f g : K[X]) {m n : ℕ}
    (hm : 0 < m) (hf : f.natDegree = m) (hg : g.natDegree ≤ n)
    (hres : f.resultant g m n = 0) :
    ∃ x : K, f.eval x = 0 ∧ g.eval x = 0 := by
  have hf0 : f ≠ 0 := by
    intro hzero
    subst f
    simp only [natDegree_zero] at hf
    exact hm.ne' hf.symm
  have hprodFormula :=
    resultant_eq_prod_eval f g n hg (IsAlgClosed.splits f)
  rw [hf] at hprodFormula
  rw [hprodFormula, mul_eq_zero] at hres
  have hprod :
      (f.roots.map g.eval).prod = 0 :=
    hres.resolve_left (pow_ne_zero n (leadingCoeff_ne_zero.mpr hf0))
  rw [Multiset.prod_eq_zero_iff, Multiset.mem_map] at hprod
  obtain ⟨x, hxmem, hgx⟩ := hprod
  exact ⟨x, (mem_roots hf0).mp hxmem, hgx⟩

/-- If the fixed-size resultant vanishes and the right polynomial attains its
declared positive degree, the two polynomials have a common affine root. -/
private theorem exists_affine_common_root_of_right_degree
    {K : Type*} [Field K] [IsAlgClosed K]
    (f g : K[X]) {m n : ℕ}
    (hn : 0 < n) (hf : f.natDegree ≤ m) (hg : g.natDegree = n)
    (hres : f.resultant g m n = 0) :
    ∃ x : K, f.eval x = 0 ∧ g.eval x = 0 := by
  have hswap : g.resultant f n m = 0 := by
    rw [resultant_comm] at hres
    exact (mul_eq_zero.mp hres).resolve_left
      (pow_ne_zero _ (neg_ne_zero.mpr one_ne_zero))
  obtain ⟨x, hgx, hfx⟩ :=
    exists_affine_common_root_of_left_degree g f hn hg hf hswap
  exact ⟨x, hfx, hgx⟩

/-- A common affine evaluation root forces the fixed-size resultant to
vanish.  This local wrapper keeps the projective theorem independent of the
Semaev development. -/
private theorem resultant_eq_zero_of_common_affine_root
    {K : Type*} [Field K] {m n : ℕ} (f g : K[X]) (x : K)
    (hf : f.natDegree ≤ m) (hg : g.natDegree ≤ n)
    (hpos : m ≠ 0 ∨ n ≠ 0)
    (hfx : f.eval x = 0) (hgx : g.eval x = 0) :
    f.resultant g m n = 0 := by
  obtain ⟨p, q, _, _, hpq⟩ :=
    exists_mul_add_mul_eq_C_resultant f g hf hg hpos
  have hev := congrArg (eval x) hpq
  simp only [eval_add, eval_mul, eval_C, hfx, hgx, zero_mul, add_zero] at hev
  exact hev.symm

/-- The fixed-size resultant vanishes exactly when the two declared-degree
binary homogeneous forms have a common projective root.

Both zero forms and degree drops are included.  If both actual degrees drop,
the proof returns the explicit infinity witness `[1:0]`; otherwise it returns
an affine witness `[x:1]` extracted from the split polynomial that attains its
declared degree. -/
theorem fixedDegree_resultant_eq_zero_iff_common_projective_root
    {K : Type*} [Field K] [IsAlgClosed K]
    (f g : K[X]) {m n : ℕ}
    (hm : 0 < m) (hn : 0 < n)
    (hf : f.natDegree ≤ m) (hg : g.natDegree ≤ n) :
    f.resultant g m n = 0 ↔ HasCommonProjectiveRoot f g m n := by
  constructor
  · intro hres
    by_cases hfm : f.natDegree < m
    · by_cases hgn : g.natDegree < n
      · refine ⟨1, 0, Or.inl one_ne_zero, ?_, ?_⟩
        · rw [eval_homogenize_one_zero]
          exact coeff_eq_zero_of_natDegree_lt hfm
        · rw [eval_homogenize_one_zero]
          exact coeff_eq_zero_of_natDegree_lt hgn
      · have hgne : g.natDegree = n := eq_of_le_of_not_lt hg hgn
        obtain ⟨x, hfx, hgx⟩ :=
          exists_affine_common_root_of_right_degree f g hn hf hgne hres
        refine ⟨x, 1, Or.inr one_ne_zero, ?_, ?_⟩
        · rw [Polynomial.eval_homogenize hf ![x, (1 : K)] (by simp)]
          simp [hfx]
        · rw [Polynomial.eval_homogenize hg ![x, (1 : K)] (by simp)]
          simp [hgx]
    · have hfme : f.natDegree = m := eq_of_le_of_not_lt hf hfm
      obtain ⟨x, hfx, hgx⟩ :=
        exists_affine_common_root_of_left_degree f g hm hfme hg hres
      refine ⟨x, 1, Or.inr one_ne_zero, ?_, ?_⟩
      · rw [Polynomial.eval_homogenize hf ![x, (1 : K)] (by simp)]
        simp [hfx]
      · rw [Polynomial.eval_homogenize hg ![x, (1 : K)] (by simp)]
        simp [hgx]
  · rintro ⟨U, V, hUV, hF, hG⟩
    by_cases hV : V = 0
    · subst V
      have hU : U ≠ 0 := hUV.resolve_right (by simp)
      rw [eval_homogenize_second_zero] at hF hG
      have hfc : f.coeff m = 0 :=
        (mul_eq_zero.mp hF).resolve_right (pow_ne_zero m hU)
      have hgc : g.coeff n = 0 :=
        (mul_eq_zero.mp hG).resolve_right (pow_ne_zero n hU)
      exact resultant_eq_zero_of_lt_lt f g m n
        (natDegree_lt_of_le_of_coeff_eq_zero hm hf hfc)
        (natDegree_lt_of_le_of_coeff_eq_zero hn hg hgc)
    · have hfeval : f.eval (U / V) = 0 := by
        rw [Polynomial.eval_homogenize hf ![U, V] (by simpa)] at hF
        exact (mul_eq_zero.mp hF).resolve_right (pow_ne_zero m hV)
      have hgeval : g.eval (U / V) = 0 := by
        rw [Polynomial.eval_homogenize hg ![U, V] (by simpa)] at hG
        exact (mul_eq_zero.mp hG).resolve_right (pow_ne_zero n hV)
      exact resultant_eq_zero_of_common_affine_root
        f g (U / V) hf hg (Or.inl hm.ne') hfeval hgeval

/-- Common projective root after applying a named coefficient specialization
map.  Formal degrees are retained across the map even if actual degree drops. -/
def HasCommonProjectiveRootOver
    {k K : Type*} [Field k] [Field K]
    (φ : k →+* K) (f g : k[X]) (m n : ℕ) : Prop :=
  HasCommonProjectiveRoot (f.map φ) (g.map φ) m n

/-- Exact specialization compatibility for the fixed-degree resultant/common
projective-root theorem.  This statement keeps the coefficient map `φ`
explicit and uses Mathlib's unit-one identity `resultant_map_map`; no
normalization is inserted. -/
theorem map_fixedDegree_resultant_eq_zero_iff_common_projective_root
    {k K : Type*} [Field k] [Field K] [IsAlgClosed K]
    (φ : k →+* K) (f g : k[X]) {m n : ℕ}
    (hm : 0 < m) (hn : 0 < n)
    (hf : f.natDegree ≤ m) (hg : g.natDegree ≤ n) :
    φ (f.resultant g m n) = 0 ↔
      HasCommonProjectiveRootOver φ f g m n := by
  rw [← resultant_map_map]
  exact fixedDegree_resultant_eq_zero_iff_common_projective_root
    (f.map φ) (g.map φ) hm hn
      ((Polynomial.natDegree_map_le (p := f) (f := φ)).trans hf)
      ((Polynomial.natDegree_map_le (p := g) (f := φ)).trans hg)

/-- Injective specialization, in particular the canonical embedding into a
named algebraic closure, reflects zero.  Thus the base fixed resultant
vanishes exactly when the mapped binary forms share a projective root. -/
theorem fixedDegree_resultant_eq_zero_iff_common_projective_root_over
    {k K : Type*} [Field k] [Field K] [IsAlgClosed K]
    (φ : k →+* K) (hφ : Function.Injective φ)
    (f g : k[X]) {m n : ℕ}
    (hm : 0 < m) (hn : 0 < n)
    (hf : f.natDegree ≤ m) (hg : g.natDegree ≤ n) :
    f.resultant g m n = 0 ↔
      HasCommonProjectiveRootOver φ f g m n := by
  rw [← map_fixedDegree_resultant_eq_zero_iff_common_projective_root
    φ f g hm hn hf hg]
  constructor
  · intro h
    simp [h]
  · intro h
    apply hφ
    simpa using h

end Ecdlp.ProjectiveResultant
