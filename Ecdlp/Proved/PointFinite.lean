import Mathlib

/-!
# Affine points of a Weierstrass curve over a finite base are finite (general, upstream-ready)

Mathlib v4.31 has **no** `Finite`/`Fintype` instance for `WeierstrassCurve.Affine.Point`, even over
a finite field (verified by `notes/HASSE_RECON.md`) — yet its new `EllipticCurve/LFunction.lean`
writes `Nat.card E.toAffine.Point`, which is silently junk `0` without such an instance. This file
supplies the general instance the library is missing:

> for **any** commutative ring `R` that is `Finite`, the affine point type of any Weierstrass curve
> over `R` is finite,

via the injection `Point ↪ Option (R × R)` sending `0 ↦ none` and an affine point `(x, y) ↦ some (x, y)`
(`Option (R × R)` is finite because `R` is). The concrete `instFiniteSecp256k1Point`
(`CurveCardinality.lean`) and `instFiniteP256Point` (`P256Cardinality.lean`) are exactly the
`R := ZMod p` special cases of this instance.

**Upstream candidate.** This is a clean, fully general, dependency-light lemma filling a real
Mathlib gap; it is a natural PR to `Mathlib.AlgebraicGeometry.EllipticCurve.Affine`. It is proved
here first ("build it for ourselves") so the rest of the point-counting layer (`n ∣ #E`, and any
future Hasse work) has a real `#E`, and can be submitted upstream unchanged. Pure-kernel: no
`native_decide`, no new axioms.
-/

open WeierstrassCurve.Affine

namespace Ecdlp.PointFinite

/-- **The affine points of any Weierstrass curve over a finite (commutative-ring) base form a finite
type.** The map `Point → Option (R × R)` (`0 ↦ none`, `some x y _ ↦ some (x, y)`) is injective, and
`Option (R × R)` is finite. Generalizes the concrete `ZMod p` instances for secp256k1 and P-256; a
standalone upstream candidate for the quantity `Nat.card E.toAffine.Point` that Mathlib now names but
does not prove finite. -/
instance instFiniteAffinePoint {R : Type*} [CommRing R] [Finite R] (W : WeierstrassCurve R) :
    Finite W.toAffine.Point := by
  apply Finite.of_injective
    (fun P : W.toAffine.Point =>
      match P with
      | .zero => (none : Option (R × R))
      | .some (x := x) (y := y) _ => some (x, y))
  intro P Q h
  cases P <;> cases Q <;> simp_all

end Ecdlp.PointFinite
