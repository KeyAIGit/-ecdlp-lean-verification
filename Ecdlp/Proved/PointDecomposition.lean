import Mathlib
import Ecdlp.Proved.SemaevThree

/-!
# Point decomposition ⇒ Semaev relation: the index-calculus entry point (secp256k1)

Index calculus on an elliptic curve rests on the **point-decomposition problem**: given a target
point `R`, write it as a sum of "factor-base" points, `R = P₁ + P₂` (the `m = 2` relation; higher
`m` uses `S_{m+1}`). Semaev's insight is that this group-theoretic search is confined to an
algebraic variety: whenever `R = P₁ + P₂`, the three `x`-coordinates satisfy the summation
polynomial `S₃(x₁, x₂, x_R) = 0`. So instead of ranging over the whole group one solves a single
codimension-1 polynomial condition on coordinates — that reduction *is* index calculus's leverage.

This file states and proves exactly that reduction on secp256k1, on Mathlib's formalized
elliptic-curve group law. The forward direction `R = P₁ + P₂ ⇒ S₃(x₁,x₂,x_R) = 0` is the one that
matters for the attack: it says every decomposition of `R` lies on the Semaev variety, so the
solution set the attacker searches is cut out by `S₃`. Both branches are covered — the generic
sum (`x₁ ≠ x₂`) and the doubling `R = 2·P₁`.

The only mathematical content beyond the already-proven `secp256k1_semaev_three_point` is the
identity `x(−R) = x(R)`: a decomposition `R = P₁ + P₂` is the same as the sum-to-zero relation
`P₁ + P₂ + (−R) = 0`, and negation on a Weierstrass curve fixes the `x`-coordinate
(`Point.neg_some`: `−(x,y) = (x, negY x y)`). Rewriting through that reduces to the sum-form
already established.

**Honest scope.** This is the *forward*, structural half — "solutions of the decomposition problem
are Semaev roots". It records where the search lives; it is **not** a decomposition *algorithm* and
says nothing about the cost of *finding* those roots. Over the prime field `𝔽_p` that root-finding
(a single Semaev equation of large degree, with no Weil-restriction structure to exploit) is exactly
the studied barrier that keeps prime-field ECDLP at `Θ(√n)` — see `BARRIERS.md`. No new axioms;
fully kernel-checked.
-/

namespace Ecdlp.Semaev

open Ecdlp.Curve

variable [Fact (Nat.Prime Secp256k1.p)]

open WeierstrassCurve.Affine in
/-- **Point decomposition ⇒ Semaev relation (generic sum), secp256k1.** If a point `R = (x_R, y_R)`
decomposes as a sum of two curve points `R = P₁ + P₂` with distinct `x`-coordinates, then the three
`x`-coordinates are a root of secp256k1's third Semaev polynomial: `S₃(x₁, x₂, x_R) = 0`. This is
the index-calculus entry point — every 2-term decomposition of `R` lies on the Semaev variety. The
proof recasts `R = P₁ + P₂` as `P₁ + P₂ + (−R) = 0`, uses `x(−R) = x_R` (`Point.neg_some`), and
applies the sum-form `secp256k1_semaev_three_point`. -/
theorem secp256k1_point_decomposition_semaev
    {x₁ y₁ x₂ y₂ xR yR : ZMod Secp256k1.p}
    (h₁ : secp256k1.toAffine.Nonsingular x₁ y₁)
    (h₂ : secp256k1.toAffine.Nonsingular x₂ y₂)
    (hR : secp256k1.toAffine.Nonsingular xR yR)
    (hx : x₁ ≠ x₂)
    (hdecomp : Point.some xR yR hR = Point.some x₁ y₁ h₁ + Point.some x₂ y₂ h₂) :
    S₃ (0 : ZMod Secp256k1.p) 7 x₁ x₂ xR = 0 := by
  have hsum : Point.some x₁ y₁ h₁ + Point.some x₂ y₂ h₂ + (-Point.some xR yR hR) = 0 := by
    rw [← hdecomp]; exact add_neg_cancel _
  rw [Point.neg_some] at hsum
  exact secp256k1_semaev_three_point h₁ h₂ _ hx hsum

open WeierstrassCurve.Affine in
/-- **Point decomposition ⇒ Semaev relation (doubling), secp256k1.** The `P₁ = P₂` companion: if
`R = 2·P₁` for a curve point `P₁` that is not `2`-torsion (`y₁ ≠ negY x₁ y₁`), then
`S₃(x₁, x₁, x_R) = 0`. Together with `secp256k1_point_decomposition_semaev` this covers every
2-term decomposition of `R`. Same recast `2·P₁ + (−R) = 0` with `x(−R) = x_R`, then
`secp256k1_semaev_three_point_double`. -/
theorem secp256k1_point_decomposition_semaev_double
    {x₁ y₁ xR yR : ZMod Secp256k1.p}
    (h₁ : secp256k1.toAffine.Nonsingular x₁ y₁)
    (hR : secp256k1.toAffine.Nonsingular xR yR)
    (hy : y₁ ≠ secp256k1.toAffine.negY x₁ y₁)
    (hdecomp : Point.some xR yR hR = Point.some x₁ y₁ h₁ + Point.some x₁ y₁ h₁) :
    S₃ (0 : ZMod Secp256k1.p) 7 x₁ x₁ xR = 0 := by
  have hsum : Point.some x₁ y₁ h₁ + Point.some x₁ y₁ h₁ + (-Point.some xR yR hR) = 0 := by
    rw [← hdecomp]; exact add_neg_cancel _
  rw [Point.neg_some] at hsum
  exact secp256k1_semaev_three_point_double h₁ _ hy hsum

end Ecdlp.Semaev
