import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial
import Ecdlp.Proved.CoprimePsi3Psi5

/-!
# `Ψ₃` and `preΨ' 7` are coprime for secp256k1 — the 3- and 7-torsion loci are disjoint (`E[3] ⊥ E[7]`)

The 3- and 7-division polynomials of `E : Y² = X³ + 7` share no root: **no point is simultaneously
3-torsion and 7-torsion.** If a point `P` of order 3 and a point `Q` of order 7 shared an
`x`-coordinate they would satisfy `Q = ±P`, forcing `ord Q = ord P`, i.e. `3 = 7` — impossible.
Equivalently `gcd(ψ₃, ψ₇) = 1`, a coprimality that is **not** in Mathlib. We certify it
constructively with an explicit **Bézout certificate** `u·Ψ₃ + v·(preΨ' 7) = 1` whose cofactors
come from extended-Euclid over `𝔽_p` (CAS; `scripts/certs/torsion_disjoint_3_7.py`, prints `CERT_OK`).

`Ψ₃ = 3X⁴+84X` lives on exponents `≡ 1 (mod 3)` and `preΨ' 7` (degree 24) on exponents
`≡ 0 (mod 3)`, so the cofactors are **sparse** (`u` on `≡ 2`, eight terms; `v` on `≡ 0`, two
terms) and the Bézout product collapses onto the ten powers `X²⁷,X²⁴,…,X³,X⁰` — ten residue
equations in `ZMod p` discharged by `native_decide`, the ten-power analogue of the six-power
`CoprimePsi3Psi5`.

The 7-division polynomial has no prior explicit-coefficient theorem in the repo, so we first record
its concrete form `secp256k1_preΨ₇`. Because `7` is odd, `preΨ' 7` is genuinely univariate, and we
derive it by rewriting the goal directly with Mathlib's odd recursion `preΨ'_odd` at `m = 1`
(both `if Even 1` branches discharged by `if_neg Nat.not_even_one`, exactly as Mathlib's own
`Φ_two` proof), collapsing to `preΨ'5·Ψ₃³ − preΨ₄³·Ψ₂Sq²`. No new axioms beyond the compiler
trust of `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- **The secp256k1 7-division polynomial is `preΨ' 7 = 7X²⁴ + 27608X²¹ − 2101904X¹⁸ −
284585728X¹⁵ − 2228742656X¹² − 26142548992X⁹ − 330576748544X⁶ − 661153497088X³ +
377801998336`.** Because `7` is odd, `preΨ' 7` *is* the genuine 7-division polynomial (no `ψ₂`
factor), so it is a literal `𝔽_p`-polynomial needing no curve relation. We rewrite the goal
directly with Mathlib's `preΨ'_odd` at `m = 1` — turning `7` into `2·(1+2)+1` first — then
normalize the shifted indices `1+4,…,1+1` to `5,…,2` so
`preΨ' 7 = preΨ' 5 · preΨ' 3³ · 1 − preΨ' 2 · preΨ' 4³ · Ψ₂Sq²` collapses via
`secp256k1_preΨ₅`, `preΨ'_two = 1`, `preΨ'_three = Ψ₃`, `preΨ'_four = preΨ₄` (both `if Even 1`
branches by `if_neg Nat.not_even_one` — the odd-`m` mirror of `secp256k1_preΨ₅`, where `Ψ₂Sq²`
now sits on the *subtracted* term) to `preΨ'5·Ψ₃³ − preΨ₄³·Ψ₂Sq²`; substituting the concrete
secp256k1 forms and `ring` finishes. Extends the tower `Ψ₂Sq → Ψ₃ → preΨ₄ → preΨ' 5` one rung
to `preΨ' 7`. -/
theorem secp256k1_preΨ₇ :
    secp256k1.preΨ' 7
      = 7 * X ^ 24 + 27608 * X ^ 21 - 2101904 * X ^ 18 - 284585728 * X ^ 15
        - 2228742656 * X ^ 12 - 26142548992 * X ^ 9 - 330576748544 * X ^ 6
        - 661153497088 * X ^ 3 + 377801998336 := by
  rw [show (7 : ℕ) = 2 * (1 + 2) + 1 from rfl, WeierstrassCurve.preΨ'_odd,
    show (1 : ℕ) + 4 = 5 from rfl, show (1 : ℕ) + 3 = 4 from rfl,
    show (1 : ℕ) + 2 = 3 from rfl, show (1 : ℕ) + 1 = 2 from rfl,
    if_neg Nat.not_even_one, if_neg Nat.not_even_one,
    secp256k1_preΨ₅, WeierstrassCurve.preΨ'_two, WeierstrassCurve.preΨ'_three,
    WeierstrassCurve.preΨ'_four, secp256k1_Ψ₃, secp256k1_preΨ₄, secp256k1_Ψ₂Sq]
  simp only [map_ofNat]
  ring

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`):
`u = U₂₃X²³+U₂₀X²⁰+U₁₇X¹⁷+U₁₄X¹⁴+U₁₁X¹¹+U₈X⁸+U₅X⁵+U₂X²` (deg 23, sparse on exponents
`≡ 2 mod 3`) and `v = V₃X³+V₀` (deg 3, sparse on exponents `≡ 0 mod 3`), with
`u·Ψ₃ + v·(preΨ' 7) = 1`. (Fresh values — not the same-named private constants of
`CoprimePsi3Psi5`.) -/
private def U₂₃ : ZMod Secp256k1.p :=
  68944590336790336836930321036541054571108089578262445502128972569398365568457
private def U₂₀ : ZMod Secp256k1.p :=
  63845044986596127917238406587884911877349497474344308019160463221897999565952
private def U₁₇ : ZMod Secp256k1.p :=
  22253398887951985727697958014689324670722641885893013284809964241804939424547
private def U₁₄ : ZMod Secp256k1.p :=
  101374513400142574387640111079567503864672689695122863264029523801075956397009
private def U₁₁ : ZMod Secp256k1.p :=
  3391696775842707751069407080766688069554051883385740844231428252699398029752
private def U₈ : ZMod Secp256k1.p :=
  101664364752688042620528964726208266071132221721823193954668754045372792705489
private def U₅ : ZMod Secp256k1.p :=
  106134497956017148058902191656989031970877659139882974899542335172254439863475
private def U₂ : ZMod Secp256k1.p :=
  75607205217650409999754433938468414630184630497968841867273699652761192112281
private def V₃ : ZMod Secp256k1.p :=
  3535772494894482905193000986821807427602242942356255938932607186803224662565
private def V₀ : ZMod Secp256k1.p :=
  104312091503547336002174865974034599278343573453365127323364127481039549803657

/-- **`Ψ₃` and `preΨ' 7` are coprime — the 3-torsion and 7-torsion `x`-loci are disjoint**
(`E[3] ⊥ E[7]`). Their only possible common root would be a point simultaneously 3- and
7-torsion, forcing `ord = 3` and `ord = 7` on one point (impossible); realized here by an
explicit Bézout certificate over `𝔽_p`. This coprimality is missing from Mathlib. Mirrors
`CoprimePsi3Psi5` one rung up (ten collapsed powers instead of six). -/
theorem secp256k1_isCoprime_Ψ₃_preΨ₇ :
    IsCoprime secp256k1.Ψ₃ (secp256k1.preΨ' 7) := by
  refine ⟨C U₂₃ * X ^ 23 + C U₂₀ * X ^ 20 + C U₁₇ * X ^ 17 + C U₁₄ * X ^ 14
    + C U₁₁ * X ^ 11 + C U₈ * X ^ 8 + C U₅ * X ^ 5 + C U₂ * X ^ 2,
    C V₃ * X ^ 3 + C V₀, ?_⟩
  rw [secp256k1_Ψ₃, secp256k1_preΨ₇]
  have e27 : (3 * U₂₃ + 7 * V₃ : ZMod Secp256k1.p) = 0 := by native_decide
  have e24 : (84 * U₂₃ + 3 * U₂₀ + 27608 * V₃ + 7 * V₀ : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e21 : (84 * U₂₀ + 3 * U₁₇ - 2101904 * V₃ + 27608 * V₀ : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e18 : (84 * U₁₇ + 3 * U₁₄ - 284585728 * V₃ - 2101904 * V₀ : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e15 : (84 * U₁₄ + 3 * U₁₁ - 2228742656 * V₃ - 284585728 * V₀ : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e12 : (84 * U₁₁ + 3 * U₈ - 26142548992 * V₃ - 2228742656 * V₀ : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e9 : (84 * U₈ + 3 * U₅ - 330576748544 * V₃ - 26142548992 * V₀ : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e6 : (84 * U₅ + 3 * U₂ - 661153497088 * V₃ - 330576748544 * V₀ : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e3 : (84 * U₂ + 377801998336 * V₃ - 661153497088 * V₀ : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e0 : (377801998336 * V₀ : ZMod Secp256k1.p) = 1 := by native_decide
  -- collapse the sparse Bézout product to one `C` per power of `X`, then use the residue facts.
  have key : (C U₂₃ * X ^ 23 + C U₂₀ * X ^ 20 + C U₁₇ * X ^ 17 + C U₁₄ * X ^ 14
        + C U₁₁ * X ^ 11 + C U₈ * X ^ 8 + C U₅ * X ^ 5 + C U₂ * X ^ 2)
        * (3 * X ^ 4 + 3 * C 28 * X)
      + (C V₃ * X ^ 3 + C V₀)
        * (7 * X ^ 24 + 27608 * X ^ 21 - 2101904 * X ^ 18 - 284585728 * X ^ 15
          - 2228742656 * X ^ 12 - 26142548992 * X ^ 9 - 330576748544 * X ^ 6
          - 661153497088 * X ^ 3 + 377801998336)
      = C (3 * U₂₃ + 7 * V₃) * X ^ 27
        + C (84 * U₂₃ + 3 * U₂₀ + 27608 * V₃ + 7 * V₀) * X ^ 24
        + C (84 * U₂₀ + 3 * U₁₇ - 2101904 * V₃ + 27608 * V₀) * X ^ 21
        + C (84 * U₁₇ + 3 * U₁₄ - 284585728 * V₃ - 2101904 * V₀) * X ^ 18
        + C (84 * U₁₄ + 3 * U₁₁ - 2228742656 * V₃ - 284585728 * V₀) * X ^ 15
        + C (84 * U₁₁ + 3 * U₈ - 26142548992 * V₃ - 2228742656 * V₀) * X ^ 12
        + C (84 * U₈ + 3 * U₅ - 330576748544 * V₃ - 26142548992 * V₀) * X ^ 9
        + C (84 * U₅ + 3 * U₂ - 661153497088 * V₃ - 330576748544 * V₀) * X ^ 6
        + C (84 * U₂ + 377801998336 * V₃ - 661153497088 * V₀) * X ^ 3
        + C (377801998336 * V₀) := by
    simp only [map_add, map_sub, map_mul, map_ofNat]; ring
  rw [key, e27, e24, e21, e18, e15, e12, e9, e6, e3, e0]
  simp

end Ecdlp.Curve
