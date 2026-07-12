import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.CoprimePsi3Psi5

/-!
# `Ψ₂Sq` and `preΨ' 5` are coprime for secp256k1 — the 2- and 5-torsion loci are disjoint (`E[2] ⊥ E[5]`)

The 2- and 5-division polynomials of `E : Y² = X³ + 7` share no root: **no point is simultaneously
2-torsion and 5-torsion.** A common root would be the `x`-coordinate of a nonzero point whose order
divides `gcd(2, 5) = 1` — impossible. Equivalently `gcd(ψ₂², ψ₅) = 1`, a coprimality that is
**not** in Mathlib. We certify it constructively with an explicit **Bézout certificate**
`u·Ψ₂Sq + v·(preΨ' 5) = 1` whose cofactors come from extended-Euclid over `𝔽_p`
(CAS; `scripts/certs/torsion_disjoint_2_5.py`, prints `CERT_OK`).

Both `Ψ₂Sq = 4X³+28` and `preΨ' 5 = 5X¹²+2660X⁹−11760X⁶−548800X³−614656` live on exponents
`≡ 0 (mod 3)`, so extended-Euclid stays inside `𝔽_p[X³]`: the cofactors are **maximally sparse**
(`u` on `X⁹,X⁶,X³,X⁰` and `v` a constant) and the Bézout product collapses onto the five powers
`X¹²,X⁹,X⁶,X³,X⁰` — five residue equations in `ZMod p` discharged by `native_decide`, the
five-power sibling of the six-power `CoprimePsi3Psi5` and the three-power `CoprimePsi2PrePsi4`.

Reuses the explicit 5-division form `secp256k1_preΨ₅` recorded in `CoprimePsi3Psi5`. No new
axioms beyond the compiler trust of `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`): `u = U₉X⁹+U₆X⁶+U₃X³+U₀` (deg 9,
sparse on exponents `≡ 0 mod 3`) and `v = V₀` (a constant), with `u·Ψ₂Sq + v·(preΨ' 5) = 1`. -/
private def U₉ : ZMod Secp256k1.p :=
  99142778494795567484546243715572291300534481701196779994490370184439965604459
private def U₆ : ZMod Secp256k1.p :=
  59310642212701184203405681774582306662379778255696243390989127279915174764288
private def U₃ : ZMod Secp256k1.p :=
  69446565655999351689642756084092762405069646257957980847129963197823042378350
private def U₀ : ZMod Secp256k1.p :=
  90429242334511927848674557712301290372769783732852059149176628780622904835439
private def V₀ : ZMod Secp256k1.p :=
  82794702136406219605362384039705237954150393170939365659648321463520396056761

/-- **`Ψ₂Sq` and `preΨ' 5` are coprime — the 2-torsion and 5-torsion `x`-loci are disjoint**
(`E[2] ⊥ E[5]`). Their only possible common root would be a nonzero point whose order divides
`gcd(2, 5) = 1` (impossible); realized here by an explicit Bézout certificate over `𝔽_p`.
This coprimality is missing from Mathlib. Mirrors `CoprimePsi2PrePsi4` two rungs up
(five collapsed powers instead of three). -/
theorem secp256k1_isCoprime_Ψ₂Sq_preΨ₅ :
    IsCoprime secp256k1.Ψ₂Sq (secp256k1.preΨ' 5) := by
  refine ⟨C U₉ * X ^ 9 + C U₆ * X ^ 6 + C U₃ * X ^ 3 + C U₀, C V₀, ?_⟩
  rw [secp256k1_Ψ₂Sq, secp256k1_preΨ₅]
  have e12 : (4 * U₉ + 5 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e9 : (28 * U₉ + 4 * U₆ + 2660 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e6 : (28 * U₆ + 4 * U₃ - 11760 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e3 : (28 * U₃ + 4 * U₀ - 548800 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e0 : (28 * U₀ - 614656 * V₀ : ZMod Secp256k1.p) = 1 := by native_decide
  -- collapse the sparse Bézout product to one `C` per power of `X`, then use the residue facts.
  have key : (C U₉ * X ^ 9 + C U₆ * X ^ 6 + C U₃ * X ^ 3 + C U₀) * (C 4 * X ^ 3 + C 28)
      + C V₀ * (5 * X ^ 12 + 2660 * X ^ 9 - 11760 * X ^ 6 - 548800 * X ^ 3 - 614656)
      = C (4 * U₉ + 5 * V₀) * X ^ 12
        + C (28 * U₉ + 4 * U₆ + 2660 * V₀) * X ^ 9
        + C (28 * U₆ + 4 * U₃ - 11760 * V₀) * X ^ 6
        + C (28 * U₃ + 4 * U₀ - 548800 * V₀) * X ^ 3
        + C (28 * U₀ - 614656 * V₀) := by
    simp only [map_add, map_sub, map_mul, map_ofNat]; ring
  rw [key, e12, e9, e6, e3, e0]
  simp

end Ecdlp.Curve
