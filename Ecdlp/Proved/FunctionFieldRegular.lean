import Mathlib
import Ecdlp.Proved.FunctionFieldRepr

/-!
# Weil rung W3 (regularity weld): presentations `a/b` ↔ the local ring at `P`

`FunctionFieldRepr` extracts from every abstract function-field element `f ∈ F(E)` a presentation
`f = a/b` by regular functions, but with **no control on where `b` vanishes**; `PointEvaluation`
evaluates the elements of the local ring `F[E]_P = Localization.AtPrime ⟨X−x, Y−y⟩` by the residue
map `evalRatAt`, but rung W2's Miller function lives in `F(E)`, not in `F[E]_P`. This file welds
the two sides: it names the class of elements of `F(E)` that are **regular at `P`** — those with a
presentation whose denominator is nonzero at `P` — and identifies it with the image of `F[E]_P`:

* `evalAt_eq_zero_iff_mem` / `evalAt_ne_zero_iff_notMem` — nonvanishing of a regular function at
  `P` is exactly non-membership in the point's maximal ideal `⟨X−x, Y−y⟩`, by rewriting
  `evalAt_ker` through `RingHom.mem_ker`. This is the dictionary between the analytic hypothesis
  `b(P) ≠ 0` and the localization-theoretic hypothesis `b ∈ P.primeCompl`;
* `RegularAt h f` — **the definition**: `f` has a presentation `f = a/b` with `b(P) ≠ 0`;
* `regularAt_eval_unique` — the value at `P` through **any** admissible presentation is the same
  (pure reuse of `evalFracAt_num_den_well_defined`), so a `RegularAt` element has a well-defined
  value: `evalReg` (via `Exists.choose`) with characterization `evalReg_eq`;
* `toFunctionField` — **the canonical map** `F[E]_P →+* F(E)`, built by `IsLocalization.lift`:
  every denominator in `P.primeCompl` is nonzero at `P`, hence nonzero in `F[E]`, hence a unit of
  the field `F(E)`. (Mathlib's `Localization.mapToFractionRing` is the same construction, as an
  `AlgHom` under a `≤ nonZeroDivisors` side condition; the direct lift needs no extra instances.)
  `toFunctionField_algebraMap` says it extends `algebraMap F[E] F(E)`;
* `regularAt_toFunctionField` / `regularAt_of_toFunctionField_eq` — **bridge, direction (a)**:
  everything in the image of the local ring is `RegularAt` (`IsLocalization.surj` produces the
  presentation, the primeCompl witness makes its denominator nonvanishing);
* `RegularAt.exists_atPrime` — **bridge, direction (b)**: conversely a `RegularAt` presentation
  `a/b` determines the element `mk' a ⟨b, _⟩` of the local ring mapping to `f`. Together (a)+(b):
  the regular-at-`P` elements of `F(E)` are exactly the image of `F[E]_P`;
* `evalRatAt_eq_evalFracAt_of_toFunctionField` — **the payoff weld**: if `r ∈ F[E]_P` maps to `f`
  and `f = a/b` with `b(P) ≠ 0`, then `evalRatAt h r = evalFracAt h a b = a(P)/b(P)`. The proof
  needs no injectivity of `toFunctionField`: re-extract a presentation of `r` by `surj`, evaluate
  it by the landed `evalRatAt_eq_evalFracAt`, and compare presentations of `f` by
  `evalFracAt_num_den_well_defined`. Consequences: `evalRatAt_congr` (the residue value depends
  only on the underlying rational function) and `evalRatAt_eq_evalReg` (the two value notions
  coincide on their common domain);
* `secp256k1_miller_function_regularAt` — **Miller connection**: the W2 Miller function has a
  presentation `a/b` that makes it `RegularAt` every rational point where `b` does not vanish.

Mathlib names with no compiled precedent in this repository were source-verified against the
pinned rev (`lake-manifest.json`): `Ideal.primeCompl`, `Ideal.mem_primeCompl_iff`,
`RingHom.mem_ker`, `IsLocalization.lift`, `IsLocalization.lift_eq`, `IsLocalization.mk'`,
`IsLocalization.mk'_spec_mk`, and the instance `Localization.isLocalization` (which serves
`Localization.AtPrime`, an abbreviation of `Localization P.primeCompl`).

**Honest scope.** Injectivity of `toFunctionField` is not proved (not needed here —
`evalRatAt_congr` is the factoring statement the evaluation layer actually uses). Choosing, for a
`RegularAt` element, a presentation adapted to *several* points at once, evaluation at whole
divisors `f_P(D_Q)`, and Weil reciprocity (W4) remain open (`notes/FOUNDATIONS.md`).
Curve-agnostic except the final secp256k1 theorem. No new axioms; fully kernel-checked.
-/

namespace Ecdlp.Weil

open Polynomial WeierstrassCurve.Affine WeierstrassCurve.Affine.CoordinateRing

variable {F : Type*} [Field F] {W : WeierstrassCurve.Affine F}

/-- **Vanishing at `P` is membership in the maximal ideal of `P`.** A regular function has value
`0` at `P = (x,y)` iff it lies in `⟨X−x, Y−y⟩`. This is `evalAt_ker` (`PointEvaluation`) read
elementwise through `RingHom.mem_ker`. -/
theorem evalAt_eq_zero_iff_mem {x y : F} (h : W.Equation x y) (b : W.CoordinateRing) :
    evalAt h b = 0 ↔ b ∈ XYIdeal W x (C y) := by
  rw [← evalAt_ker h, RingHom.mem_ker]

/-- **The nonvanishing dictionary.** A regular function is nonzero at `P` iff it lies outside the
maximal ideal `⟨X−x, Y−y⟩` — i.e. iff it is a legitimate denominator for the localization at `P`.
This is the bridge between the presentation-side hypothesis `evalAt h b ≠ 0` and the
localization-side hypothesis `b ∈ (XYIdeal W x (C y)).primeCompl`. -/
theorem evalAt_ne_zero_iff_notMem {x y : F} (h : W.Equation x y) (b : W.CoordinateRing) :
    evalAt h b ≠ 0 ↔ b ∉ XYIdeal W x (C y) :=
  ⟨fun hne hmem => hne ((evalAt_eq_zero_iff_mem h b).mpr hmem),
    fun hnm h0 => hnm ((evalAt_eq_zero_iff_mem h b).mp h0)⟩

/-- A regular function nonzero at one point is nonzero in the coordinate ring (the zero function
vanishes everywhere). Lets pointwise nonvanishing feed lemmas expecting `b ≠ 0`. -/
theorem ne_zero_of_evalAt_ne_zero {x y : F} (h : W.Equation x y) {b : W.CoordinateRing}
    (hb : evalAt h b ≠ 0) : b ≠ 0 := by
  rintro rfl
  exact hb (map_zero (evalAt h))

/-- **Regularity at a rational point, presentation form.** A rational function `f ∈ F(E)` is
*regular at* `P = (x,y)` when it admits a presentation `f = a/b` by regular functions whose
denominator does not vanish at `P`. This is the class of functions the Weil pairing can evaluate
at `P`; `RegularAt.exists_atPrime` and `regularAt_toFunctionField` below identify it with the
image of the local ring `F[E]_P` in `F(E)`. -/
def RegularAt {x y : F} (h : W.Equation x y) (f : W.FunctionField) : Prop :=
  ∃ a b : W.CoordinateRing, evalAt h b ≠ 0 ∧
    f = algebraMap W.CoordinateRing W.FunctionField a
      / algebraMap W.CoordinateRing W.FunctionField b

/-- Introduction rule for `RegularAt`: any presentation with denominator nonvanishing at `P`
witnesses regularity. -/
theorem RegularAt.of_num_den {x y : F} {h : W.Equation x y} {f : W.FunctionField}
    {a b : W.CoordinateRing} (hb : evalAt h b ≠ 0)
    (hab : f = algebraMap W.CoordinateRing W.FunctionField a
        / algebraMap W.CoordinateRing W.FunctionField b) :
    RegularAt h f :=
  ⟨a, b, hb, hab⟩

/-- A `RegularAt` element has a presentation in **multiplicative form**
`f * (algebraMap b) = algebraMap a` with `b(P) ≠ 0` — the division-free witness shape consumed by
the evaluation layers (`evalFracAt_num_den_well_defined`, `evalRatAt_eq_evalFracAt`). -/
theorem RegularAt.exists_mul_num_den {x y : F} {h : W.Equation x y} {f : W.FunctionField}
    (hf : RegularAt h f) :
    ∃ a b : W.CoordinateRing, evalAt h b ≠ 0 ∧
      f * algebraMap W.CoordinateRing W.FunctionField b
        = algebraMap W.CoordinateRing W.FunctionField a := by
  obtain ⟨a, b, hb, hab⟩ := hf
  exact ⟨a, b, hb, functionField_num_den_mul (ne_zero_of_evalAt_ne_zero h hb) hab⟩

/-- **The value of a regular function at `P` is well-defined.** Any two presentations of the same
`f` whose denominators are nonzero at `P` give the same presented value
`evalFracAt h a b = a(P)/b(P)`. Quotient-form counterpart of
`evalFracAt_num_den_well_defined` (`FunctionFieldRepr`), which it reuses verbatim — no new
mathematics, only the interchange of presentation shapes. -/
theorem regularAt_eval_unique {x y : F} (h : W.Equation x y) {f : W.FunctionField}
    {a₁ b₁ a₂ b₂ : W.CoordinateRing}
    (h₁ : f = algebraMap W.CoordinateRing W.FunctionField a₁
        / algebraMap W.CoordinateRing W.FunctionField b₁)
    (h₂ : f = algebraMap W.CoordinateRing W.FunctionField a₂
        / algebraMap W.CoordinateRing W.FunctionField b₂)
    (hb₁ : evalAt h b₁ ≠ 0) (hb₂ : evalAt h b₂ ≠ 0) :
    evalFracAt h a₁ b₁ = evalFracAt h a₂ b₂ :=
  evalFracAt_num_den_well_defined h
    (functionField_num_den_mul (ne_zero_of_evalAt_ne_zero h hb₁) h₁)
    (functionField_num_den_mul (ne_zero_of_evalAt_ne_zero h hb₂) h₂) hb₁ hb₂

/-- **The value at `P` of a function regular at `P`**, as data: evaluate any chosen presentation
(`Exists.choose`). By `regularAt_eval_unique` the result does not depend on the choice —
`evalReg_eq` is the usable characterization. -/
noncomputable def evalReg {x y : F} (h : W.Equation x y) {f : W.FunctionField}
    (hf : RegularAt h f) : F :=
  evalFracAt h (Exists.choose hf) (Exists.choose (Exists.choose_spec hf))

/-- **Characterization of `evalReg`:** through any presentation `f = a/b` with `b(P) ≠ 0`, the
value of `f` at `P` is the presented value `a(P)/b(P)`. In particular `evalReg` is independent of
the choice hidden in its definition. -/
theorem evalReg_eq {x y : F} (h : W.Equation x y) {f : W.FunctionField} (hf : RegularAt h f)
    {a b : W.CoordinateRing} (hb : evalAt h b ≠ 0)
    (hab : f = algebraMap W.CoordinateRing W.FunctionField a
        / algebraMap W.CoordinateRing W.FunctionField b) :
    evalReg h hf = evalFracAt h a b :=
  regularAt_eval_unique h (Exists.choose_spec (Exists.choose_spec hf)).2 hab
    (Exists.choose_spec (Exists.choose_spec hf)).1 hb

/-- **The canonical map from the local ring at `P` into the function field**,
`F[E]_P →+* F(E)`. Constructed by the universal property of the localization
(`IsLocalization.lift`): a denominator `b ∈ P.primeCompl` is nonzero at `P`
(`evalAt_ne_zero_iff_notMem`), hence nonzero in `F[E]`, hence a unit of the field `F(E)`
(`algebraMap_functionField_ne_zero`). Both `F[E]_P` and `F(E)` are localizations of `F[E]`, and
this is the unique `F[E]`-compatible comparison map (cf. `toFunctionField_algebraMap`). -/
noncomputable def toFunctionField {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] :
    Localization.AtPrime (XYIdeal W x (C y)) →+* W.FunctionField :=
  IsLocalization.lift (M := (XYIdeal W x (C y)).primeCompl)
    (g := algebraMap W.CoordinateRing W.FunctionField) fun b =>
      isUnit_iff_ne_zero.mpr (algebraMap_functionField_ne_zero
        (ne_zero_of_evalAt_ne_zero h ((evalAt_ne_zero_iff_notMem h (b : W.CoordinateRing)).mpr
          (Ideal.mem_primeCompl_iff.mp b.2))))

/-- `toFunctionField` extends the embedding of the coordinate ring: on the image of a regular
function it agrees with `algebraMap F[E] F(E)`. The defining equation of the lift. -/
theorem toFunctionField_algebraMap {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] (r : W.CoordinateRing) :
    toFunctionField h (algebraMap W.CoordinateRing
        (Localization.AtPrime (XYIdeal W x (C y))) r)
      = algebraMap W.CoordinateRing W.FunctionField r :=
  IsLocalization.lift_eq _ r

/-- **Bridge, direction (a): the image of the local ring is regular at `P`.** Every rational
function coming from `F[E]_P` is `RegularAt`: `IsLocalization.surj` presents it as `a/b` with
`b ∈ P.primeCompl`, and non-membership in `⟨X−x, Y−y⟩` is exactly nonvanishing at `P`. -/
theorem regularAt_toFunctionField {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] (r : Localization.AtPrime (XYIdeal W x (C y))) :
    RegularAt h (toFunctionField h r) := by
  obtain ⟨⟨a, b⟩, hab⟩ := IsLocalization.surj (XYIdeal W x (C y)).primeCompl r
  have hb : evalAt h (b : W.CoordinateRing) ≠ 0 :=
    (evalAt_ne_zero_iff_notMem h (b : W.CoordinateRing)).mpr (Ideal.mem_primeCompl_iff.mp b.2)
  refine ⟨a, (b : W.CoordinateRing), hb, ?_⟩
  rw [eq_div_iff (algebraMap_functionField_ne_zero (ne_zero_of_evalAt_ne_zero h hb)),
    ← toFunctionField_algebraMap h (b : W.CoordinateRing), ← toFunctionField_algebraMap h a,
    ← map_mul, hab]

/-- Bridge (a), hypothesis form: if `r ∈ F[E]_P` maps to `f` under the canonical map, then `f` is
regular at `P`. -/
theorem regularAt_of_toFunctionField_eq {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] {r : Localization.AtPrime (XYIdeal W x (C y))}
    {f : W.FunctionField} (hr : toFunctionField h r = f) : RegularAt h f := by
  rw [← hr]
  exact regularAt_toFunctionField h r

/-- **Bridge, direction (b): a function regular at `P` comes from the local ring.** A `RegularAt`
presentation `f = a/b`, `b(P) ≠ 0` determines the element `mk' a ⟨b, _⟩` of `F[E]_P` — the
denominator lies in `P.primeCompl` by the nonvanishing dictionary — and that element maps to `f`
under the canonical map. With direction (a): the regular-at-`P` elements of `F(E)` are **exactly**
the image of `F[E]_P`. -/
theorem RegularAt.exists_atPrime {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] {f : W.FunctionField} (hf : RegularAt h f) :
    ∃ r : Localization.AtPrime (XYIdeal W x (C y)), toFunctionField h r = f := by
  obtain ⟨a, b, hb, hab⟩ := hf
  have hbmem : b ∈ (XYIdeal W x (C y)).primeCompl :=
    Ideal.mem_primeCompl_iff.mpr ((evalAt_ne_zero_iff_notMem h b).mp hb)
  refine ⟨IsLocalization.mk' (Localization.AtPrime (XYIdeal W x (C y))) a ⟨b, hbmem⟩, ?_⟩
  have hspec := IsLocalization.mk'_spec_mk
    (Localization.AtPrime (XYIdeal W x (C y))) a b hbmem
  have hmap := congrArg (toFunctionField h) hspec
  rw [map_mul, toFunctionField_algebraMap, toFunctionField_algebraMap] at hmap
  rw [hab, eq_div_iff (algebraMap_functionField_ne_zero (ne_zero_of_evalAt_ne_zero h hb))]
  exact hmap

/-- **The payoff weld: the residue-map value equals the presented value.** If `r ∈ F[E]_P` maps to
`f` under the canonical map and `f = a/b` is any presentation with `b(P) ≠ 0`, then
`evalRatAt h r = evalFracAt h a b = a(P)/b(P)`. So evaluating an abstract rational function
regular at `P` may be done through **either** route — the local-ring residue map or any admissible
presentation — with the same result. No injectivity of `toFunctionField` is needed: `r` gets its
own presentation from `IsLocalization.surj`, the landed `evalRatAt_eq_evalFracAt` evaluates it,
and `evalFracAt_num_den_well_defined` compares the two presentations of `f`. -/
theorem evalRatAt_eq_evalFracAt_of_toFunctionField {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] {f : W.FunctionField} {a b : W.CoordinateRing}
    (hb : evalAt h b ≠ 0)
    (hab : f = algebraMap W.CoordinateRing W.FunctionField a
        / algebraMap W.CoordinateRing W.FunctionField b)
    {r : Localization.AtPrime (XYIdeal W x (C y))} (hr : toFunctionField h r = f) :
    evalRatAt h r = evalFracAt h a b := by
  obtain ⟨⟨a', b'⟩, hab'⟩ := IsLocalization.surj (XYIdeal W x (C y)).primeCompl r
  have hb' : evalAt h (b' : W.CoordinateRing) ≠ 0 :=
    (evalAt_ne_zero_iff_notMem h (b' : W.CoordinateRing)).mpr (Ideal.mem_primeCompl_iff.mp b'.2)
  have h1 : evalRatAt h r = evalFracAt h a' (b' : W.CoordinateRing) :=
    evalRatAt_eq_evalFracAt h a' (b' : W.CoordinateRing) hb' r (by rw [mul_comm]; exact hab')
  have h2 : f * algebraMap W.CoordinateRing W.FunctionField (b' : W.CoordinateRing)
      = algebraMap W.CoordinateRing W.FunctionField a' := by
    have hmap := congrArg (toFunctionField h) hab'
    rw [map_mul, toFunctionField_algebraMap, toFunctionField_algebraMap, hr] at hmap
    exact hmap
  rw [h1]
  exact evalFracAt_num_den_well_defined h h2
    (functionField_num_den_mul (ne_zero_of_evalAt_ne_zero h hb) hab) hb' hb

/-- **`evalRatAt` factors through the function field**: two elements of the local ring with the
same image in `F(E)` have the same value at `P`. This is the well-definedness statement the
evaluation layer needs from the (unproved, unneeded) injectivity of `toFunctionField`. -/
theorem evalRatAt_congr {x y : F} (h : W.Equation x y) [(XYIdeal W x (C y)).IsPrime]
    {r₁ r₂ : Localization.AtPrime (XYIdeal W x (C y))}
    (hrr : toFunctionField h r₁ = toFunctionField h r₂) :
    evalRatAt h r₁ = evalRatAt h r₂ := by
  obtain ⟨a, b, hb, hab⟩ := regularAt_toFunctionField h r₂
  rw [evalRatAt_eq_evalFracAt_of_toFunctionField h hb hab hrr,
    evalRatAt_eq_evalFracAt_of_toFunctionField h hb hab rfl]

/-- **The two value notions coincide.** For `f` regular at `P` and any `r ∈ F[E]_P` mapping to
`f`, the residue-map value of `r` is the presentation value of `f`:
`evalRatAt h r = evalReg h hf`. Both evaluation routes for the Miller function agree wherever both
are defined. -/
theorem evalRatAt_eq_evalReg {x y : F} (h : W.Equation x y)
    [(XYIdeal W x (C y)).IsPrime] {f : W.FunctionField} (hf : RegularAt h f)
    {r : Localization.AtPrime (XYIdeal W x (C y))} (hr : toFunctionField h r = f) :
    evalRatAt h r = evalReg h hf :=
  evalRatAt_eq_evalFracAt_of_toFunctionField h
    (Exists.choose_spec (Exists.choose_spec hf)).1
    (Exists.choose_spec (Exists.choose_spec hf)).2 hr

section Secp256k1

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **The Miller function is regular away from its extracted denominator's zero locus.** If `f`
is a Miller function for the torsion data `(P, n)` on secp256k1 — a generator of the fractional
ideal `(XYIdeal' h)ⁿ`, as produced by rung W2 — then `f` has a fixed presentation `a/b`
(`secp256k1_miller_function_num_den`, `FunctionFieldRepr`) which makes it `RegularAt` **every**
rational point `(x', y')` of the curve where `b` does not vanish. At all such points the value
`evalReg`/`evalFracAt h' a b` exists and, by `RegularAt.exists_atPrime` +
`evalRatAt_eq_evalReg`, agrees with the residue-map value on the local ring — the evaluation
recipe the Weil pairing consumes. -/
theorem secp256k1_miller_function_regularAt
    {x y : ZMod Secp256k1.p} (h : Ecdlp.Curve.secp256k1.toAffine.Nonsingular x y) (n : ℕ)
    (f : Ecdlp.Curve.secp256k1.toAffine.FunctionField)
    (hf : (↑(CoordinateRing.XYIdeal' h ^ n) :
        Submodule Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
          Ecdlp.Curve.secp256k1.toAffine.FunctionField)
        = Submodule.span Ecdlp.Curve.secp256k1.toAffine.CoordinateRing {f}) :
    ∃ a b : Ecdlp.Curve.secp256k1.toAffine.CoordinateRing, b ≠ 0 ∧
      f = algebraMap Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
            Ecdlp.Curve.secp256k1.toAffine.FunctionField a
        / algebraMap Ecdlp.Curve.secp256k1.toAffine.CoordinateRing
            Ecdlp.Curve.secp256k1.toAffine.FunctionField b ∧
      ∀ {x' y' : ZMod Secp256k1.p} (h' : Ecdlp.Curve.secp256k1.toAffine.Equation x' y'),
        evalAt h' b ≠ 0 → RegularAt h' f := by
  obtain ⟨a, b, hb, hab, _⟩ := secp256k1_miller_function_num_den h n f hf
  refine ⟨a, b, hb, hab, ?_⟩
  intro x' y' h' hb'
  exact ⟨a, b, hb', hab⟩

end Secp256k1

end Ecdlp.Weil
