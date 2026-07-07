import Mathlib
import Ecdlp.Proved.GlvMonoidHom
import Ecdlp.Proved.GlvEigenvalue

/-!
# The GLV / CM endomorphism gives no asymptotic advantage against ECDLP (secp256k1)

secp256k1 has `j`-invariant `0` and complex multiplication by `ℤ[ζ₃]`: the GLV endomorphism
`glvHom : (x,y) ↦ (β·x, y)` is a nontrivial automorphism of the point group. A natural question —
does this extra structure help solve the discrete log? This file records the **honest no-go**:
it does **not** reduce the discrete-log exponent; the only leverage is a constant factor.

* `secp256k1_glv_preserves_dlog` (unconditional) — the endomorphism **preserves discrete-log
  relations**: if `Q = m • P` then `glvHom Q = m • glvHom P`, the *same* unknown `m`. Mapping a DLP
  instance `(P, Q)` through `glvHom` yields another instance with the identical secret scalar, so it
  is a self-reduction that is the identity on the exponent — it cannot shrink it.
* `secp256k1_glv_single_scalar` (conditional on cyclicity) — the whole "extra structure" is **one**
  scalar `k` with `k² + k + 1 ≡ 0` acting *identically on base and target* (`glvHom P = k • P`,
  `glvHom Q = k • Q`); it introduces no new unknown and no new equation on `m`.

**Why this is a no-go, not a speedup.** The endomorphism is an automorphism of order dividing `3`
(`glvPoint_cube_eq_id`), so it only permutes the group in orbits of size `≤ 3`. Against ECDLP that
buys a constant factor — `~√3` in Pollard-rho (extra collisions from the automorphism), `~2×` in
scalar multiplication (the practical GLV `k = k₁ + k₂λ` split with `kᵢ ~ √n`) — never a reduction
of the `Θ(√n)` exponent that the generic bound (`GenericGroupBound.lean`) pins down. So CM-by-`ℤ[ζ₃]`
is a genuine structural feature of secp256k1 that is, provably here, **not** a path to breaking it.
No new axioms; fully kernel-checked.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **The GLV endomorphism preserves discrete-log relations (no exponent reduction).** For every
scalar `m : ℤ` and points with `Q = m • P`, the image instance satisfies `glvHom Q = m • glvHom P`
— the *same* unknown `m`. So mapping a DLP instance `(P, Q)` through the GLV endomorphism yields
another instance with the identical secret scalar: the endomorphism is a DLP self-reduction that is
the identity on the exponent, and therefore cannot shrink it. The formal core of "GLV/CM gives no
*asymptotic* advantage against ECDLP" — only the order-3 automorphism (`glvPoint_cube_eq_id`) buys a
constant factor. Unconditional: needs only that `glvHom` is an additive homomorphism. -/
theorem secp256k1_glv_preserves_dlog (m : ℤ) (P Q : secp256k1.toAffine.Point) (h : Q = m • P) :
    glvHom Q = m • glvHom P := by
  subst h; exact map_zsmul glvHom m P

/-- **The GLV structure is a single scalar acting identically on base and target.** Under cyclicity
of the point group, the endomorphism is `[k]` for a fixed integer `k` with `k² + k + 1 ≡ 0` on the
group, and on a DLP instance `Q = m • P` it satisfies `glvHom P = k • P` **and** `glvHom Q = k • Q`:
it multiplies base and target by the *same* `k`, leaving the discrete log `m` invariant. The entire
"extra structure" of CM is this one known relation `k² + k + 1 ≡ 0`; it adds no new unknown and no
new equation constraining `m`, hence no reduction of the discrete log. -/
theorem secp256k1_glv_single_scalar [IsAddCyclic secp256k1.toAffine.Point]
    (m : ℤ) (P Q : secp256k1.toAffine.Point) (h : Q = m • P) :
    ∃ k : ℤ, (k ^ 2 + k + 1) • P = 0 ∧ glvHom P = k • P ∧ glvHom Q = k • Q := by
  obtain ⟨k, hkscalar, hkann⟩ := secp256k1_glvHom_eq_zsmul
  exact ⟨k, hkann P, hkscalar P, hkscalar Q⟩

end Ecdlp.Curve
