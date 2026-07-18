import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.CoprimePsi3Psi7

/-!
# `Ψ₂Sq` and `preΨ' 7` are coprime for secp256k1

This file proves one `𝔽_p`-polynomial fact and nothing more:
`IsCoprime secp256k1.Ψ₂Sq (secp256k1.preΨ' 7)` — the 2-division square `Ψ₂Sq = 4X³+28` and
the (odd, genuinely univariate) 7-division polynomial `preΨ' 7` share no common factor over
`𝔽_p[X]`. It is certified constructively by an explicit **Bézout certificate**
`u·Ψ₂Sq + v·(preΨ' 7) = 1` whose cofactors come from extended-Euclid over `𝔽_p`
(CAS; `scripts/certs/psi2_psi7_coprime_cert.py`, prints `CERT_OK`, and also generates this
file — zero hand transcription). This coprimality is **not** in Mathlib.

Both `Ψ₂Sq = 4X³+28` and the degree-24 `preΨ' 7` (concrete form `secp256k1_preΨ₇`,
`CoprimePsi3Psi7.lean`) live on exponents `≡ 0 (mod 3)`, so extended-Euclid stays inside
`𝔽_p[X³]`: the cofactors are **maximally sparse** (`u` on `X²¹,X¹⁸,…,X³,X⁰` and `v` a constant)
and the Bézout product collapses onto the nine powers `X²⁴,X²¹,…,X³,X⁰` — nine residue equations
in `ZMod p` discharged by `native_decide`, the nine-power sibling of the five-power
`CoprimePsi2Psi5`. No new axioms beyond the compiler trust of `native_decide`.

*Motivation / downstream (not proved in this file).* Classically this coprimality reflects
`gcd(2, 7) = 1` — no nonidentity point is simultaneously 2- and 7-torsion — and, transported to
`𝔽̄_p`, it is the `y ≠ 0`-at-every-`preΨ₇`-root input to the `±y`-pairing behind the count
`#E[7](𝔽̄_p) = 49`. None of that geometric reading — `E[2] ⊥ E[7]`, `y ≠ 0` at the roots, or
`#E[7] = 49` — is established here; the theorem below is purely the polynomial `IsCoprime`. The
`𝔽̄_p` transport and the count belong to the seven-torsion structure assembly, not to this file.
-/

namespace Ecdlp.Curve

open Polynomial

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`): `u = U₂₁X²¹+U₁₈X¹⁸+…+U₃X³+U₀`
(deg 21, sparse on exponents `≡ 0 mod 3`) and `v = V₀` (a constant), with
`u·Ψ₂Sq + v·(preΨ' 7) = 1`. (Fresh values — not the same-named private constants of
`CoprimePsi2Psi5`.) -/
private def U₂₁ : ZMod Secp256k1.p :=
  16905444402033651516461463693103388012565341377014455585577364808492354540672
private def U₁₈ : ZMod Secp256k1.p :=
  92075388586989847179037164761179497692777803228227881769432030494728725091102
private def U₁₅ : ZMod Secp256k1.p :=
  28023402571051265299951497052538033752847083528327545145260837683472466763737
private def U₁₂ : ZMod Secp256k1.p :=
  65164247640023297578389091055862555165364118222551786844951850955810765718504
private def U₉ : ZMod Secp256k1.p :=
  87153328281478476716983817185322769648863891590770536438741916259925034530087
private def U₆ : ZMod Secp256k1.p :=
  67005793722541508046460376198106351026378381000847182700831233914754275490641
private def U₃ : ZMod Secp256k1.p :=
  106814836014183167869012717503856269542177676938163969167515146561522723658239
private def U₀ : ZMod Secp256k1.p :=
  56630664332716687034668724228143843098598995324119019855688789975219734562790
private def V₀ : ZMod Secp256k1.p :=
  23423200123785397825899445034994609093754086260460472248086529825978321597234

/-- **`Ψ₂Sq` and `preΨ' 7` are coprime over `𝔽_p[X]`** (`IsCoprime secp256k1.Ψ₂Sq
(secp256k1.preΨ' 7)`), realized by an explicit Bézout certificate over `𝔽_p`. A polynomial
coprimality missing from Mathlib; mirrors `CoprimePsi2Psi5` one rung up (nine collapsed powers
instead of five). The classical `gcd(2,7)=1` / `E[2] ⊥ E[7]` reading and its `𝔽̄_p` `y ≠ 0`
consequence are motivation only — not part of this statement. -/
theorem secp256k1_isCoprime_Ψ₂Sq_preΨ₇ :
    IsCoprime secp256k1.Ψ₂Sq (secp256k1.preΨ' 7) := by
  refine ⟨C U₂₁ * X ^ 21 + C U₁₈ * X ^ 18 + C U₁₅ * X ^ 15 + C U₁₂ * X ^ 12
     + C U₉ * X ^ 9 + C U₆ * X ^ 6 + C U₃ * X ^ 3 + C U₀, C V₀, ?_⟩
  rw [secp256k1_Ψ₂Sq, secp256k1_preΨ₇]
  have e24 : (4 * U₂₁ + 7 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e21 : (28 * U₂₁ + 4 * U₁₈ + 27608 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e18 : (28 * U₁₈ + 4 * U₁₅ - 2101904 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e15 : (28 * U₁₅ + 4 * U₁₂ - 284585728 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e12 : (28 * U₁₂ + 4 * U₉ - 2228742656 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e9 : (28 * U₉ + 4 * U₆ - 26142548992 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e6 : (28 * U₆ + 4 * U₃ - 330576748544 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e3 : (28 * U₃ + 4 * U₀ - 661153497088 * V₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have e0 : (28 * U₀ + 377801998336 * V₀ : ZMod Secp256k1.p) = 1 := by native_decide
  -- collapse the sparse Bézout product to one `C` per power of `X`, then use the residue facts.
  have key : (C U₂₁ * X ^ 21 + C U₁₈ * X ^ 18 + C U₁₅ * X ^ 15 + C U₁₂ * X ^ 12
         + C U₉ * X ^ 9 + C U₆ * X ^ 6 + C U₃ * X ^ 3 + C U₀)
        * (C 4 * X ^ 3 + C 28)
      + C V₀
        * (7 * X ^ 24 + 27608 * X ^ 21 - 2101904 * X ^ 18 - 284585728 * X ^ 15
          - 2228742656 * X ^ 12 - 26142548992 * X ^ 9 - 330576748544 * X ^ 6
          - 661153497088 * X ^ 3 + 377801998336)
      = C (4 * U₂₁ + 7 * V₀) * X ^ 24
        + C (28 * U₂₁ + 4 * U₁₈ + 27608 * V₀) * X ^ 21
        + C (28 * U₁₈ + 4 * U₁₅ - 2101904 * V₀) * X ^ 18
        + C (28 * U₁₅ + 4 * U₁₂ - 284585728 * V₀) * X ^ 15
        + C (28 * U₁₂ + 4 * U₉ - 2228742656 * V₀) * X ^ 12
        + C (28 * U₉ + 4 * U₆ - 26142548992 * V₀) * X ^ 9
        + C (28 * U₆ + 4 * U₃ - 330576748544 * V₀) * X ^ 6
        + C (28 * U₃ + 4 * U₀ - 661153497088 * V₀) * X ^ 3
        + C (28 * U₀ + 377801998336 * V₀) := by
    simp only [map_add, map_sub, map_mul, map_ofNat]; ring
  rw [key, e24, e21, e18, e15, e12, e9, e6, e3, e0]
  simp

end Ecdlp.Curve
