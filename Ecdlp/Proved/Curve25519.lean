import Mathlib

/-!
# Curve25519 as a Mathlib elliptic curve (Montgomery model)

A third curve grounded by the same machinery, and a genuinely *different* model: **Curve25519**
is a **Montgomery** curve `v² = u³ + 486662·u² + u` over `𝔽_p`, `p = 2²⁵⁵ − 19` — not short
Weierstrass. It embeds into Mathlib's `WeierstrassCurve` with a nonzero `a₂ = 486662` (the `u²`
coefficient), unlike secp256k1 / P-256 (`a₂ = 0`). Under the published primality of `p` (a
hypothesis `[Fact p.Prime]`, not an axiom) it is a genuine `EllipticCurve`, with the RFC 7748 base
point `u = 9` a verified rational point. All coordinate facts machine-checked by `native_decide`.

The `generator`-on-curve check simultaneously validates the constants `p`, `A`, `Gu`, `Gv`.

**Structural notes (context, not theorems).** Curve25519 has `a₂ ≠ 0` — the Montgomery `u²` term —
so the same Mathlib EC group law covers a curve model outside short Weierstrass form. It also has
**cofactor 8** (`#E = 8·ℓ`, `ℓ` prime), unlike the prime-order secp256k1 / P-256; X25519 handles
this by clamping. Grounding it here shows the formalization is not tied to one curve *shape* or to
prime order. No new axioms; fully kernel-checked (`native_decide` additionally trusts the compiler).
-/

namespace Ecdlp.Curve25519

/-- The Curve25519 field prime `p = 2²⁵⁵ − 19`. -/
def p : ℕ := 2 ^ 255 - 19

/-- The Montgomery coefficient `A = 486662` (the `a₂` / `u²` coefficient). -/
def A : ℕ := 486662

/-- The `u`-coordinate of the RFC 7748 base point (`u = 9`). -/
def Gu : ℕ := 9

/-- The `v`-coordinate of the RFC 7748 base point. -/
def Gv : ℕ := 14781619447589544791020593568409986887264606134616475288964881837755586237401

/-- Curve25519 as a Montgomery curve `v² = u³ + 486662·u² + u` over `𝔽_p`, embedded in Mathlib's
`WeierstrassCurve` with `a₂ = A` (nonzero — Montgomery, not short Weierstrass). -/
def Curve25519 : WeierstrassCurve (ZMod p) where
  a₁ := 0
  a₂ := (A : ZMod p)
  a₃ := 0
  a₄ := 1
  a₆ := 0

/-- The Curve25519 discriminant is nonzero in `𝔽_p` (machine-checked) — the curve is nonsingular. -/
theorem Curve25519_Δ_ne_zero : Curve25519.Δ ≠ 0 := by native_decide

/-- Curve25519 is a **Montgomery** curve: `a₂ = 486662 ≠ 0`, so it is genuinely outside short
Weierstrass form (`a₂ = 0`) — a different curve model handled by the same Mathlib EC group law. -/
theorem Curve25519_a₂_ne_zero : Curve25519.a₂ ≠ 0 := by native_decide

/-- **The Curve25519 base point lies on the curve.** The RFC 7748 generator `G = (Gu, Gv)`, cast
into `𝔽_p`, satisfies the Montgomery equation — one `native_decide` validating `p`, `A`, `Gu`, `Gv`
together. A genuine rational point of the Mathlib curve. -/
theorem Curve25519_generator_equation :
    Curve25519.toAffine.Equation (Gu : ZMod p) (Gv : ZMod p) := by
  rw [WeierstrassCurve.Affine.equation_iff]
  simp only [Curve25519]
  native_decide

variable [Fact (Nat.Prime p)]

/-- Curve25519 is a genuine elliptic curve: its discriminant is a unit in `𝔽_p`. The same Mathlib
group law now applies to a Montgomery-model, cofactor-8 curve. -/
instance : Curve25519.IsElliptic := by
  refine ⟨?_⟩
  rw [isUnit_iff_ne_zero]
  exact Curve25519_Δ_ne_zero

end Ecdlp.Curve25519
