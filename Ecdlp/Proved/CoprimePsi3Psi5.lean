import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial

/-!
# `Ψ₃` and `preΨ' 5` are coprime for secp256k1 — the 3-/5-torsion loci are disjoint (`E[3] ⊥ E[5]`)

The 3- and 5-division polynomials of `E : Y² = X³ + 7` share no root: **no point is simultaneously
3-torsion and 5-torsion.** If a point `P` of order 3 and a point `Q` of order 5 shared an
`x`-coordinate they would satisfy `Q = ±P`, forcing `ord Q = ord P`, i.e. `3 = 5` — impossible.
Equivalently `gcd(ψ₃, ψ₅) = 1`, a coprimality that is **not** in Mathlib. We certify it
constructively with an explicit **Bézout certificate** `u·Ψ₃ + v·(preΨ' 5) = 1` whose cofactors
come from extended-Euclid over `𝔽_p` (CAS; `scripts/certs/torsion_disjoint_3_5.py`, prints `CERT_OK`).

`Ψ₃ = 3X⁴+84X` lives on exponents `≡ 1 (mod 3)` and
`preΨ' 5 = 5X¹²+2660X⁹−11760X⁶−548800X³−614656` lives on exponents `≡ 0 (mod 3)`, so the cofactors
are **sparse** (`u` on `≡ 2`, `v` on `≡ 0`) and the Bézout product collapses onto the six powers
`X¹⁵,X¹²,X⁹,X⁶,X³,X⁰` — six residue equations in `ZMod p` discharged by `native_decide`, the
six-power analogue of the three-power `CoprimePsi2Psi3` and four-power `CoprimePsi3PrePsi4`.

The 5-division polynomial has no prior explicit-coefficient theorem in the repo, so we first record
its concrete form `secp256k1_preΨ₅`. Because `5` is odd, `preΨ' 5` is genuinely univariate, and we
derive it by rewriting the goal directly with Mathlib's odd recursion `preΨ'_odd` at `m = 0`
(mirroring Mathlib's own `Φ_four` proof), collapsing to `preΨ₄·Ψ₂Sq² − Ψ₃³`. No new axioms beyond
the compiler trust of `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **The secp256k1 5-division polynomial is `preΨ' 5 = 5X¹² + 2660X⁹ − 11760X⁶ − 548800X³ − 614656`.**
Because `5` is odd, `preΨ' 5` *is* the genuine 5-division polynomial (no `ψ₂` factor), so it is a
literal `𝔽_p`-polynomial needing no curve relation. We rewrite the goal directly with Mathlib's
`preΨ'_odd` at `m = 0` — turning `5` into `2·(0+2)+1` first, exactly as Mathlib's own `Φ_four`
does — so `preΨ' 5 = preΨ' 4 · preΨ' 2³ · Ψ₂Sq² − preΨ' 1 · preΨ' 3³` collapses via
`preΨ'_four = preΨ₄`, `preΨ'_two = preΨ'_one = 1`, `preΨ'_three = Ψ₃` (both `if Even 0` branches
`if_pos Even.zero`) to `preΨ₄·Ψ₂Sq² − Ψ₃³`; substituting the concrete secp256k1 forms and `ring`
finishes. Extends the tower `Ψ₂Sq → Ψ₃ → preΨ₄` one rung to `preΨ' 5`. -/
theorem secp256k1_preΨ₅ :
    secp256k1.preΨ' 5
      = 5 * X ^ 12 + 2660 * X ^ 9 - 11760 * X ^ 6 - 548800 * X ^ 3 - 614656 := by
  rw [show (5 : ℕ) = 2 * (0 + 2) + 1 from rfl, WeierstrassCurve.preΨ'_odd,
    WeierstrassCurve.preΨ'_four, WeierstrassCurve.preΨ'_two, WeierstrassCurve.preΨ'_one,
    WeierstrassCurve.preΨ'_three, if_pos Even.zero, if_pos Even.zero,
    secp256k1_preΨ₄, secp256k1_Ψ₂Sq, secp256k1_Ψ₃]
  simp only [map_ofNat]
  ring

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`): `u = U₁₁X¹¹+U₈X⁸+U₅X⁵+U₂X²` (deg 11,
sparse on exponents `≡ 2 mod 3`) and `v = V₃X³+V₀` (deg 3, sparse on exponents `≡ 0 mod 3`), with
`u·Ψ₃ + v·(preΨ' 5) = 1`. -/
private def U₁₁ : ZMod Secp256k1.p :=
  31177840712345204383440702675357104180201715313433862087315362139048932203702
private def U₈ : ZMod Secp256k1.p :=
  50833951204485227496364311484852378098102338386479880943844279992526584060117
private def U₅ : ZMod Secp256k1.p :=
  69970874983990339768432868587673310710667172024916395574625392522883749089112
private def U₂ : ZMod Secp256k1.p :=
  43425072435009501839400542569054573740197890917139190071633944342682153936688
private def V₃ : ZMod Secp256k1.p :=
  27610131267519355539363972398260900633186964678195908363393816319734174546444
private def V₀ : ZMod Secp256k1.p :=
  111153103857739796084256904440306667401884537566138730673360705418592607296042

/-- **`Ψ₃` and `preΨ' 5` are coprime — the 3-torsion and 5-torsion `x`-loci are disjoint** (`E[3] ⊥ E[5]`).
Their only possible common root would be a point simultaneously 3- and 5-torsion, forcing `ord = 3`
and `ord = 5` on one point (impossible); realized here by an explicit Bézout certificate over `𝔽_p`.
This coprimality is missing from Mathlib. Mirrors `CoprimePsi2Psi3` / `CoprimePsi3PrePsi4` one rung
up (six collapsed powers instead of three/four). -/
theorem secp256k1_isCoprime_Ψ₃_preΨ₅ :
    IsCoprime secp256k1.Ψ₃ (secp256k1.preΨ' 5) := by
  refine ⟨C U₁₁ * X ^ 11 + C U₈ * X ^ 8 + C U₅ * X ^ 5 + C U₂ * X ^ 2,
    C V₃ * X ^ 3 + C V₀, ?_⟩
  rw [secp256k1_Ψ₃, secp256k1_preΨ₅]
  have e15 : (3 * U₁₁ + 5 * V₃ : ZMod Secp256k1.p) = 0 := by native_decide
  have e12 : (84 * U₁₁ + 3 * U₈ + 2660 * V₃ + 5 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e9 : (84 * U₈ + 3 * U₅ - 11760 * V₃ + 2660 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e6 : (84 * U₅ + 3 * U₂ - 548800 * V₃ - 11760 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e3 : (84 * U₂ - 614656 * V₃ - 548800 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e0 : (-614656 * V₀ : ZMod Secp256k1.p) = 1 := by native_decide
  -- collapse the sparse Bézout product to one `C` per power of `X`, then use the residue facts.
  have key : (C U₁₁ * X ^ 11 + C U₈ * X ^ 8 + C U₅ * X ^ 5 + C U₂ * X ^ 2)
        * (3 * X ^ 4 + 3 * C 28 * X)
      + (C V₃ * X ^ 3 + C V₀)
        * (5 * X ^ 12 + 2660 * X ^ 9 - 11760 * X ^ 6 - 548800 * X ^ 3 - 614656)
      = C (3 * U₁₁ + 5 * V₃) * X ^ 15
        + C (84 * U₁₁ + 3 * U₈ + 2660 * V₃ + 5 * V₀) * X ^ 12
        + C (84 * U₈ + 3 * U₅ - 11760 * V₃ + 2660 * V₀) * X ^ 9
        + C (84 * U₅ + 3 * U₂ - 548800 * V₃ - 11760 * V₀) * X ^ 6
        + C (84 * U₂ - 614656 * V₃ - 548800 * V₀) * X ^ 3
        + C (-614656 * V₀) := by
    simp only [map_add, map_sub, map_mul, map_neg, map_ofNat]; ring
  rw [key, e15, e12, e9, e6, e3, e0]
  simp

end Ecdlp.Curve
