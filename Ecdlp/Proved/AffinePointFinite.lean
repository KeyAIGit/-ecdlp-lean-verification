import Mathlib

/-!
# Finiteness of the affine points of a Weierstrass curve over a finite ring

`WeierstrassCurve.Affine.Point` is the type of nonsingular affine points (plus the point
at infinity `zero`) of a Weierstrass curve. Over a *finite* commutative ring `R` this type
is itself finite, because every point injects into `Option (R × R)` (the base point `zero`
maps to `none`, and `some x y _` maps to `some (x, y)`), and `Option (R × R)` is finite
whenever `R` is.

This generalises the two curve-specific instances previously duplicated in the repository
(`instFiniteSecp256k1Point` in `Ecdlp/Proved/CurveCardinality.lean` and `instFiniteP256Point`
in `Ecdlp/Proved/P256Cardinality.lean`), which are now one-line corollaries obtained by
typeclass resolution.

The hypotheses are the weakest that the statement needs: only `[CommRing R]` (required to
even form `Point` / `Nonsingular`) and `[Finite R]` (to finiteness of the injection target).
Neither `Field` nor `Nontrivial` is needed. `ZMod p` satisfies both for any `p`, so the
instance fires for both secp256k1 and P-256.

This is a genuine Mathlib gap in v4.31.0 — no `Finite`/`Fintype` instance exists on any
`Point` variant — and hence a clean upstream candidate. The natural upstream home is
`Mathlib/AlgebraicGeometry/EllipticCurve/Affine/Point.lean`, in its `[CommRing R]` section.
-/

open WeierstrassCurve

namespace WeierstrassCurve.Affine

/-- The nonsingular affine points of a Weierstrass curve over a finite commutative ring form a
**finite** type, via the injection `Point ↪ Option (R × R)`.

Upstream candidate: Mathlib v4.31.0 has no `Finite`/`Fintype` instance on `Point`; this could
live in `Mathlib/AlgebraicGeometry/EllipticCurve/Affine/Point.lean`. Generalises the former
per-curve instances for secp256k1 and P-256. -/
instance instFinitePoint {R : Type*} [CommRing R] [Finite R] {W : WeierstrassCurve.Affine R} :
    Finite W.Point := by
  apply Finite.of_injective
    (fun P : W.Point =>
      match P with
      | .zero => (none : Option (R × R))
      | .some (x := x) (y := y) _ => some (x, y))
  intro P Q h
  cases P <;> cases Q <;> simp_all

end WeierstrassCurve.Affine
