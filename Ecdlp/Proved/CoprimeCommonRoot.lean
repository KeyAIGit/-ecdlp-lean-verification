import Mathlib

/-!
# `IsCoprime` ↔ no common root — the field↔algebraic-closure bridge (node L1 of B1)

The structural half of the B1 coprimality plan (`notes/B1_COPRIMALITY_PLAN.md`) that is *independent
of the open Mathlib TODO L4*: the classical dictionary "coprime polynomials over a field share no
root in the algebraic closure". We give the direction B1 actually consumes —
**not coprime ⇒ a genuine common root exists** in any algebraically closed extension — plus the easy
converse. Over a field `k`, `gcd f g` is a non-unit exactly when `f, g` are not coprime; a non-unit
has `degree ≠ 0`, an injective coefficient map preserves that, and an algebraically closed field then
supplies a root of the mapped gcd, which divides both `f` and `g`.

General, curve-agnostic, and reusable (a candidate for upstreaming). Verified kernel-clean via
`lake env lean` before promotion; no `sorry`, no new axioms. The design was produced by an
adversarially-verified proof-design workflow over the exact Mathlib v4.31 API and accepted by the
kernel on the first attempt.
-/

namespace Ecdlp.DivisionPoly

open Polynomial

/-- **[L1], the direction B1 needs.** For `f g : k[X]` over a field `k` and an injective ring hom
`φ : k →+* K` into an algebraically closed field `K`: if `f, g` are **not** coprime, they have a
common root in `K`. Instantiate `φ := algebraMap k (AlgebraicClosure k)` for the "common root in
`k̄`" reading (`(f.map φ).eval x` is defeq to `aeval x f`). -/
theorem exists_common_root_of_not_isCoprime
    {k K : Type*} [Field k] [Field K] [IsAlgClosed K]
    (φ : k →+* K) (hφ : Function.Injective φ)
    {f g : k[X]} (h : ¬ IsCoprime f g) :
    ∃ x : K, (f.map φ).eval x = 0 ∧ (g.map φ).eval x = 0 := by
  classical
  -- `gcd f g` divides both and is a non-unit (⇔ not coprime over a field).
  set d : k[X] := EuclideanDomain.gcd f g with hd
  have hdf : d ∣ f := EuclideanDomain.gcd_dvd_left f g
  have hdg : d ∣ g := EuclideanDomain.gcd_dvd_right f g
  have hdu : ¬ IsUnit d := fun hu => h (EuclideanDomain.gcd_isUnit_iff.mp hu)
  -- A non-unit over a field has `degree ≠ 0` (this also absorbs `d = 0`, whose degree is `⊥ ≠ 0`).
  have hdeg : d.degree ≠ 0 := fun hz => hdu (Polynomial.isUnit_iff_degree_eq_zero.mpr hz)
  -- An injective map preserves degree, so the mapped gcd stays non-constant.
  have hdeg' : (d.map φ).degree ≠ 0 := by
    rwa [Polynomial.degree_map_eq_of_injective hφ]
  -- Algebraically closed ⇒ the mapped gcd has a root `a`, which kills every multiple of `d`.
  obtain ⟨a, ha⟩ := IsAlgClosed.exists_root _ hdeg'
  have ha' : (d.map φ).eval a = 0 := ha
  have key : ∀ p : k[X], d ∣ p → (p.map φ).eval a = 0 := by
    intro p hp
    obtain ⟨c, rfl⟩ := hp
    rw [Polynomial.map_mul, Polynomial.eval_mul, ha', zero_mul]
  exact ⟨a, key f hdf, key g hdg⟩

/-- Easy converse (no algebraic closure needed): coprime ⇒ no common root, from a Bézout witness
`a*f + b*g = 1` mapped through `φ` and evaluated at the putative common root. Together with
`exists_common_root_of_not_isCoprime` this is the full `IsCoprime ↔ no common root` dictionary. -/
theorem no_common_root_of_isCoprime
    {k K : Type*} [Field k] [CommRing K] [Nontrivial K]
    (φ : k →+* K) {f g : k[X]} (h : IsCoprime f g) (x : K)
    (hf : (f.map φ).eval x = 0) (hg : (g.map φ).eval x = 0) : False := by
  obtain ⟨a, b, hab⟩ := h
  have hev := congrArg (fun p => (p.map φ).eval x) hab
  simp only [Polynomial.map_add, Polynomial.map_mul, Polynomial.map_one,
    Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_one, hf, hg,
    mul_zero, add_zero] at hev
  exact zero_ne_one hev

end Ecdlp.DivisionPoly
