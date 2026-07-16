import Mathlib
import Ecdlp.Proved.DivisionPolynomialEvalBridge
import Ecdlp.Proved.NormEDSConsecutiveZeros
import Ecdlp.Proved.CoprimePsi2Psi3
import Ecdlp.Proved.CoprimePsi3PrePsi4

/-!
# Node N5 closed: `Φ n` and `ΨSq n` are coprime for secp256k1, for every `n`

The composition that closes node **N5** (`gcd(Φₙ, ΨSqₙ) = 1`) of the `ψₙ ↔ E[n]` bridge
(`notes/DIVISION_POLY_TORSION_MAP.md`) — the step the map called the highest-value
unblocked node toward the counting half `#E[n] = n²` (N10(i)). Three previously landed
pieces snap together, with nothing new needed:

1. **The evaluation bridge + descent** (`DivisionPolynomialEvalBridge.lean`, #171):
   `¬ IsCoprime (Φ n) (ΨSq n)` over `𝔽_p` produces a point `x₀ ∈ 𝔽̄_p` and `β` with
   `β² = Ψ₂Sq(x₀)` such that the scalar sequence `w = normEDS β (Ψ₃ x₀) (preΨ₄ x₀)`
   has **two consecutive zeros** (`w n = 0` and `w (n±1) = 0`).
2. **Ward apparition rigidity** (`NormEDSConsecutiveZeros.lean`, #172): over an integral
   domain, `normEDS b c d` never has two consecutive zeros — provided `¬(b = 0 ∧ c = 0)`
   and `¬(c = 0 ∧ d = 0)`.
3. **The Bézout certificates** (`CoprimePsi2Psi3.lean`, `CoprimePsi3PrePsi4.lean`):
   `Ψ₂Sq ⊥ Ψ₃` and `Ψ₃ ⊥ preΨ₄` over `𝔽_p[X]`. Mapped up to `𝔽̄_p[X]` (coprimality is
   preserved by ring maps) and evaluated at `x₀`, they discharge exactly the two
   nondegeneracy hypotheses of (2): `β = 0` forces `Ψ₂Sq(x₀) = β² = 0`, so a degenerate
   pair would exhibit a common root that the certificates forbid.

The result holds for **every** `n : ℤ` — including `n = 0` and `n ≡ 0 (mod p)`: no
`char ∤ n` hypothesis enters, because the certificates are `n`-independent curve facts.
(In char `p` the classical *degree* of `ψ_p` collapses, but the *coprimality* survives —
`Φ n` stays monic, and this is exactly what the lowest-terms degree bookkeeping of
N10(i) consumes.) No `native_decide` in this file (the certificates carry their own);
no new axioms.
-/

namespace Ecdlp.Curve

open Polynomial

/-- The base-change ring hom `𝔽_p →+* 𝔽̄_p` used by `secp256k1Bar`. -/
private noncomputable abbrev φbar :
    ZMod Secp256k1.p →+* AlgebraicClosure (ZMod Secp256k1.p) :=
  algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p))

/-- Coprime polynomials over the closure have no common evaluation root. -/
private theorem no_common_root {K : Type*} [Field K] {F G : K[X]} (h : IsCoprime F G)
    {x₀ : K} (hF : F.eval x₀ = 0) (hG : G.eval x₀ = 0) : False := by
  obtain ⟨u, v, huv⟩ := h
  have h1 := congrArg (Polynomial.eval x₀) huv
  simp [hF, hG] at h1

/-- The `Ψ₂Sq ⊥ Ψ₃` certificate, transported to the algebraic closure. -/
theorem secp256k1Bar_isCoprime_Ψ₂Sq_Ψ₃ :
    IsCoprime secp256k1Bar.Ψ₂Sq secp256k1Bar.Ψ₃ := by
  have h := secp256k1_isCoprime_Ψ₂Sq_Ψ₃.map (Polynomial.mapRingHom φbar)
  simpa only [Polynomial.coe_mapRingHom, secp256k1Bar, WeierstrassCurve.map_Ψ₂Sq,
    WeierstrassCurve.map_Ψ₃] using h

/-- The `Ψ₃ ⊥ preΨ₄` certificate, transported to the algebraic closure. -/
theorem secp256k1Bar_isCoprime_Ψ₃_preΨ₄ :
    IsCoprime secp256k1Bar.Ψ₃ secp256k1Bar.preΨ₄ := by
  have h := secp256k1_isCoprime_Ψ₃_preΨ₄.map (Polynomial.mapRingHom φbar)
  simpa only [Polynomial.coe_mapRingHom, secp256k1Bar, WeierstrassCurve.map_Ψ₃,
    WeierstrassCurve.map_preΨ₄] using h

/-- **N5 for secp256k1: `Φ n` and `ΨSq n` are coprime over `𝔽_p[X]`, for every `n : ℤ`.**
A common factor would give a common root `x₀` over `𝔽̄_p` (L1), hence two consecutive
zeros of the scalar sequence `normEDS β (Ψ₃ x₀) (preΨ₄ x₀)` (the evaluation bridge),
which Ward apparition rigidity forbids — its two degeneracy escapes are exactly the
common roots the `Ψ₂Sq ⊥ Ψ₃` and `Ψ₃ ⊥ preΨ₄` Bézout certificates rule out. -/
theorem secp256k1_isCoprime_Φ_ΨSq (n : ℤ) :
    IsCoprime (secp256k1.Φ n) (secp256k1.ΨSq n) := by
  by_contra h
  obtain ⟨x₀, β, hβ, hwn, hcons⟩ :=
    secp256k1_exists_normEDS_consecutive_eq_zero_of_not_isCoprime n h
  -- Nondegeneracy of `(b, c, d) = (β, Ψ₃(x₀), preΨ₄(x₀))` from the certificates.
  have h23 : ¬(β = 0 ∧ secp256k1Bar.Ψ₃.eval x₀ = 0) := by
    rintro ⟨hb, hc⟩
    have hΨ2 : secp256k1Bar.Ψ₂Sq.eval x₀ = 0 := by rw [← hβ, hb]; norm_num
    exact no_common_root secp256k1Bar_isCoprime_Ψ₂Sq_Ψ₃ hΨ2 hc
  have h34 : ¬(secp256k1Bar.Ψ₃.eval x₀ = 0 ∧ secp256k1Bar.preΨ₄.eval x₀ = 0) := by
    rintro ⟨hc, hd⟩
    exact no_common_root secp256k1Bar_isCoprime_Ψ₃_preΨ₄ hc hd
  rcases hcons with hm | hp
  · exact Ecdlp.NormEDS.normEDS_not_consecutive_zeros' β
      (secp256k1Bar.Ψ₃.eval x₀) (secp256k1Bar.preΨ₄.eval x₀) h23 h34 n ⟨hwn, hm⟩
  · exact Ecdlp.NormEDS.normEDS_not_consecutive_zeros β
      (secp256k1Bar.Ψ₃.eval x₀) (secp256k1Bar.preΨ₄.eval x₀) h23 h34 n ⟨hwn, hp⟩

/-- **N5 over the closure** — the form the lowest-terms degree bookkeeping of N10(i)
consumes: `Φ n ⊥ ΨSq n` in `𝔽̄_p[X]`, by mapping the `𝔽_p` statement up. -/
theorem secp256k1Bar_isCoprime_Φ_ΨSq (n : ℤ) :
    IsCoprime (secp256k1Bar.Φ n) (secp256k1Bar.ΨSq n) := by
  have h := (secp256k1_isCoprime_Φ_ΨSq n).map (Polynomial.mapRingHom φbar)
  simpa only [Polynomial.coe_mapRingHom, secp256k1Bar, WeierstrassCurve.map_Φ,
    WeierstrassCurve.map_ΨSq] using h

end Ecdlp.Curve
