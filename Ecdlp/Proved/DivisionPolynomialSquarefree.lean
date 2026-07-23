import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.CoprimePsi3Psi5
import Ecdlp.Proved.CoprimePsi3Psi7

/-!
# Squarefreeness certificates for secp256k1's division polynomials (node B4 @ small `n`)

For `E : Y² = X³ + 7` over `𝔽_p` the odd division polynomials `ψₙ` are univariate in `X`.
This file proves, for `n = 3, 5, 7`, that `ψₙ` is **squarefree over `𝔽_p`** — equivalently,
that `ψₙ` is coprime to its own derivative `ψₙ′`. The theorem types are exactly
`IsCoprime ψₙ (derivative ψₙ)` over `𝔽_p`; nothing about `𝔽̄_p`, root counts, or the
`n`-torsion locus is asserted here.

*Motivation / downstream (not proved in this file).* Squarefreeness of `ψₙ` is the
separability input that a later `𝔽̄_p` root-count consumes (route B of
`notes/SEPARABILITY_ROUTES.md`, node **B4**): over the closure a squarefree `ψₙ` has as
many distinct roots as its degree. That downstream root-count, and any `#E[n] = n²`
consequence, are handled elsewhere — not here.

We certify `gcd(ψₙ, ψₙ′) = 1` at `n = 3, 5, 7` with explicit **Bézout certificates**
`u·ψₙ + v·ψₙ′ = 1`, cofactors from extended-Euclid over `𝔽_p`
(CAS; `scripts/certs/psi_squarefree_certs.py`, prints `CERT_OK`). Coprimality with the
derivative always *implies* squarefreeness; here (char `p` far exceeds every degree and
leading coefficient in sight, so no inseparability escape hatch exists) it is equivalent
to it. `ψₙ` lives on exponents `≡ 0 mod 3` (for `n = 3`, `≡ 1`), so cofactors are sparse
and each Bézout product collapses onto one residue class of powers of `X` — 3/8/16 residue
equations in `ZMod p` for `n = 3/5/7`, discharged by `native_decide`, exactly the
`CoprimePsi2Psi3` / `CoprimePsi3Psi5` / `CoprimePsi3Psi7` file pattern.

The polynomial objects are the repo's CI-proved concrete forms: `secp256k1.Ψ₃`
(`DivisionPolynomial.lean`), `secp256k1.preΨ' 5` (`CoprimePsi3Psi5.lean`) and
`secp256k1.preΨ' 7` (`CoprimePsi3Psi7.lean`); for odd `n`, `preΨ' n` *is* the genuine
univariate `n`-division polynomial (no `ψ₂` factor).

**Honest scope**: small-`n` certificates only (`n = 3, 5, 7`); B4 for general `n` with
`p ∤ n` remains open. A named `Mathlib.Squarefree` upgrade is deferred — over a field,
`IsCoprime f (derivative f)` *is* the standard squarefreeness certificate, and the
root-counting consumers use exactly this coprimality form. No new axioms beyond the
compiler trust of `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

/-! ## `n = 3`: `secp256k1.Ψ₃` is coprime to its derivative -/

/-- `Ψ₃′ = 12X³ + 84` — the derivative of the concrete 3-division polynomial
`Ψ₃ = 3X⁴ + 84X`. (Incidentally `Ψ₃′ = 3·Ψ₂Sq`, a `j = 0` coincidence.) -/
private lemma secp256k1_Ψ₃_derivative :
    derivative secp256k1.Ψ₃
      = 12 * X ^ 3 + 84 := by
  rw [secp256k1_Ψ₃]
  simp only [derivative_add, derivative_sub, derivative_mul, derivative_ofNat,
    derivative_C, derivative_X_pow, derivative_X, Nat.cast_ofNat, map_ofNat, Nat.reduceSub,
    zero_mul, mul_zero, zero_add, add_zero, sub_zero, mul_one]
  ring

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`): `u = u3_2·X²` (exponents
`≡ 2 mod 3`) and `v = v3_3·X³ + v3_0` (exponents `≡ 0 mod 3`), with `u·Ψ₃ + v·Ψ₃′ = 1`. -/
private def u3_2 : ZMod Secp256k1.p :=
  5776476107076998411153201066193047557305985629578440836435525732820848895185
private def v3_3 : ZMod Secp256k1.p :=
  85399947901217896964889938489967669000625992091835812820484306572726413779951
private def v3_0 : ZMod Secp256k1.p :=
  56517567365832904909123933159002431214096063943943608638306677908622169304026

/-- **`Ψ₃` is squarefree, by certificate: it is coprime to its own derivative** (B4 at
`n = 3`). The type is exactly `IsCoprime Ψ₃ (derivative Ψ₃)` over `𝔽_p`. Explicit Bézout
certificate over `𝔽_p`; the analogue of the separability of `[3]`. (Downstream, not here:
combined with `deg Ψ₃ = 4` this squarefreeness is what a later `𝔽̄_p` root-count of the
3-torsion `x`-locus consumes.) -/
theorem secp256k1_isCoprime_Ψ₃_derivative :
    IsCoprime (secp256k1.Ψ₃) (derivative secp256k1.Ψ₃) := by
  refine ⟨C u3_2 * X ^ 2,
    C v3_3 * X ^ 3 + C v3_0, ?_⟩
  rw [secp256k1_Ψ₃_derivative, secp256k1_Ψ₃]
  have e6 : (3 * u3_2 + 12 * v3_3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e3 : (84 * u3_2 + 84 * v3_3 + 12 * v3_0 : ZMod Secp256k1.p) = 0 := by native_decide
  have e0 : (84 * v3_0 : ZMod Secp256k1.p) = 1 := by native_decide
  -- collapse the Bézout product to one `C` per power of `X`, then use the
  -- residue facts.
  have key : (C u3_2 * X ^ 2)
        * (3 * X ^ 4 + 3 * C 28 * X)
      + (C v3_3 * X ^ 3 + C v3_0)
        * (12 * X ^ 3 + 84)
      = C (3 * u3_2 + 12 * v3_3) * X ^ 6
        + C (84 * u3_2 + 84 * v3_3 + 12 * v3_0) * X ^ 3
        + C (84 * v3_0) := by
    simp only [map_add, map_sub, map_mul, map_neg, map_ofNat]; ring
  rw [key, e6, e3, e0]
  simp

/-! ## `n = 4`: `secp256k1.preΨ₄` is coprime to its derivative -/

/-- `(preΨ₄)′ = 12X⁵ + 840X²` — the derivative of the concrete primitive-4-division
polynomial `preΨ₄ = 2X⁶ + 280X³ − 784`. -/
private lemma secp256k1_preΨ₄_derivative :
    derivative secp256k1.preΨ₄
      = 12 * X ^ 5 + 840 * X ^ 2 := by
  rw [secp256k1_preΨ₄]
  simp only [derivative_add, derivative_sub, derivative_mul, derivative_ofNat,
    derivative_C, derivative_X_pow, derivative_X, Nat.cast_ofNat, map_ofNat, Nat.reduceSub,
    zero_mul, mul_zero, zero_add, add_zero, sub_zero, mul_one]
  ring

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`): `u = u4_3·X³ + u4_0`
(exponents `≡ 0 mod 3`) and `v = v4_4·X⁴ + v4_1·X` (exponents `≡ 1 mod 3`), with
`u·preΨ₄ + v·(preΨ₄)′ = 1`. -/
private def u4_3 : ZMod Secp256k1.p :=
  11932346038556848923038934480551236428068688794757576075751117448228889638126
private def u4_0 : ZMod Secp256k1.p :=
  68382318006221171532032354667120537418448983291060690242689874229160447006352
private def v4_4 : ZMod Secp256k1.p :=
  36608638739345923654017172589470763213078546756087258667194008427931463284200
private def v4_1 : ZMod Secp256k1.p :=
  3781695532221494540635018627299362573817113066838916128398762743014659283022

/-- **`preΨ₄` (the primitive-4-division polynomial) is squarefree, by certificate: it is
coprime to its own derivative** (B4 at `n = 4`). The type is exactly
`IsCoprime preΨ₄ (derivative preΨ₄)` over `𝔽_p`. Explicit Bézout certificate over `𝔽_p`; the
even-index companion to the odd `n = 3,5,7` squarefreeness. (Downstream, not here: with
`deg preΨ₄ = 6` this feeds a `𝔽̄_p` count of distinct primitive-4-torsion `x`-coordinates.) -/
theorem secp256k1_isCoprime_preΨ₄_derivative :
    IsCoprime (secp256k1.preΨ₄) (derivative secp256k1.preΨ₄) := by
  refine ⟨C u4_3 * X ^ 3 + C u4_0,
    C v4_4 * X ^ 4 + C v4_1 * X ^ 1, ?_⟩
  rw [secp256k1_preΨ₄_derivative, secp256k1_preΨ₄]
  have e0 : (- 784 * u4_0 : ZMod Secp256k1.p) = 1 := by native_decide
  have e3 : (- 784 * u4_3 + 280 * u4_0 + 840 * v4_1 : ZMod Secp256k1.p) = 0 := by native_decide
  have e6 : (280 * u4_3 + 2 * u4_0 + 840 * v4_4 + 12 * v4_1 : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e9 : (2 * u4_3 + 12 * v4_4 : ZMod Secp256k1.p) = 0 := by native_decide
  have key : (C u4_3 * X ^ 3 + C u4_0)
        * (2 * X ^ 6 + 280 * X ^ 3 - 784)
      + (C v4_4 * X ^ 4 + C v4_1 * X ^ 1)
        * (12 * X ^ 5 + 840 * X ^ 2)
      = C (- 784 * u4_0)
        + C (- 784 * u4_3 + 280 * u4_0 + 840 * v4_1) * X ^ 3
        + C (280 * u4_3 + 2 * u4_0 + 840 * v4_4 + 12 * v4_1) * X ^ 6
        + C (2 * u4_3 + 12 * v4_4) * X ^ 9 := by
    simp only [map_add, map_sub, map_mul, map_neg, map_ofNat]; ring
  rw [key, e0, e3, e6, e9]
  simp

/-! ## `n = 5`: `secp256k1.preΨ' 5` is coprime to its derivative -/

/-- `(preΨ' 5)′ = 60X¹¹ + 23940X⁸ − 70560X⁵ − 1646400X²` — the derivative of the
concrete 5-division polynomial. -/
private lemma secp256k1_preΨ₅_derivative :
    derivative (secp256k1.preΨ' 5)
      = 60 * X ^ 11 + 23940 * X ^ 8 - 70560 * X ^ 5 - 1646400 * X ^ 2 := by
  rw [secp256k1_preΨ₅]
  simp only [derivative_add, derivative_sub, derivative_mul, derivative_ofNat,
    derivative_C, derivative_X_pow, derivative_X, Nat.cast_ofNat, map_ofNat, Nat.reduceSub,
    zero_mul, mul_zero, zero_add, add_zero, sub_zero, mul_one]
  ring

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`): `u = u5_9·X⁹ + ⋯ + u5_0`
(deg 9, exponents `≡ 0 mod 3`) and `v = v5_10·X¹⁰ + ⋯ + v5_1·X` (deg 10, exponents
`≡ 1 mod 3`), with `u·(preΨ' 5) + v·(preΨ' 5)′ = 1`. -/
private def u5_9 : ZMod Secp256k1.p :=
  113131088913662661143741071087717198722079965902118159833396522292348778303863
private def u5_6 : ZMod Secp256k1.p :=
  75272105371993739872185548071487380063490237200476292778868854302361980909780
private def u5_3 : ZMod Secp256k1.p :=
  49301053454498551075074343639283384855134681496860212056757114987897389588910
private def u5_0 : ZMod Secp256k1.p :=
  111153103857739796084256904440306667401884537566138730673360705418592607296042
private def v5_10 : ZMod Secp256k1.p :=
  77416476185181924805699816165872830996445824674053909710143477814902561145092
private def v5_7 : ZMod Secp256k1.p :=
  23220078139493859945432750284801411198731854862333622218937696155593793000635
private def v5_4 : ZMod Secp256k1.p :=
  82654344384167363628540735774824333554066283531971536661299363690623143350558
private def v5_1 : ZMod Secp256k1.p :=
  114371636305804362191790721573974245371584183895398771198894898476587062973232

/-- **`preΨ' 5` (= the univariate 5-division polynomial) is squarefree, by certificate: it
is coprime to its own derivative** (B4 at `n = 5`). The type is exactly
`IsCoprime (preΨ' 5) (derivative (preΨ' 5))` over `𝔽_p`. Explicit Bézout certificate over
`𝔽_p`; the analogue of the separability of `[5]`. (Downstream, not here: with
`deg = 12 = (5² − 1)/2` this squarefreeness feeds a later `𝔽̄_p` count of distinct
5-torsion `x`-coordinates.) -/
theorem secp256k1_isCoprime_preΨ₅_derivative :
    IsCoprime (secp256k1.preΨ' 5) (derivative (secp256k1.preΨ' 5)) := by
  refine ⟨C u5_9 * X ^ 9 + C u5_6 * X ^ 6 + C u5_3 * X ^ 3 + C u5_0,
    C v5_10 * X ^ 10 + C v5_7 * X ^ 7 + C v5_4 * X ^ 4 + C v5_1 * X, ?_⟩
  rw [secp256k1_preΨ₅_derivative, secp256k1_preΨ₅]
  have e21 : (5 * u5_9 + 60 * v5_10 : ZMod Secp256k1.p) = 0 := by native_decide
  have e18 : (2660 * u5_9 + 5 * u5_6 + 23940 * v5_10 + 60 * v5_7
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e15 : (-11760 * u5_9 + 2660 * u5_6 + 5 * u5_3 - 70560 * v5_10 + 23940 * v5_7 + 60 * v5_4
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e12 : (-548800 * u5_9 - 11760 * u5_6 + 2660 * u5_3 + 5 * u5_0 - 1646400 * v5_10
      - 70560 * v5_7 + 23940 * v5_4 + 60 * v5_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e9 : (-614656 * u5_9 - 548800 * u5_6 - 11760 * u5_3 + 2660 * u5_0 - 1646400 * v5_7
      - 70560 * v5_4 + 23940 * v5_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e6 : (-614656 * u5_6 - 548800 * u5_3 - 11760 * u5_0 - 1646400 * v5_4 - 70560 * v5_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e3 : (-614656 * u5_3 - 548800 * u5_0 - 1646400 * v5_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e0 : (-614656 * u5_0 : ZMod Secp256k1.p) = 1 := by native_decide
  -- collapse the Bézout product to one `C` per power of `X`, then use the
  -- residue facts.
  have key : (C u5_9 * X ^ 9 + C u5_6 * X ^ 6 + C u5_3 * X ^ 3 + C u5_0)
        * (5 * X ^ 12 + 2660 * X ^ 9 - 11760 * X ^ 6 - 548800 * X ^ 3 - 614656)
      + (C v5_10 * X ^ 10 + C v5_7 * X ^ 7 + C v5_4 * X ^ 4 + C v5_1 * X)
        * (60 * X ^ 11 + 23940 * X ^ 8 - 70560 * X ^ 5 - 1646400 * X ^ 2)
      = C (5 * u5_9 + 60 * v5_10) * X ^ 21
        + C (2660 * u5_9 + 5 * u5_6 + 23940 * v5_10 + 60 * v5_7) * X ^ 18
        + C (-11760 * u5_9 + 2660 * u5_6 + 5 * u5_3 - 70560 * v5_10 + 23940 * v5_7 + 60 * v5_4
            ) * X ^ 15
        + C (-548800 * u5_9 - 11760 * u5_6 + 2660 * u5_3 + 5 * u5_0 - 1646400 * v5_10
            - 70560 * v5_7 + 23940 * v5_4 + 60 * v5_1) * X ^ 12
        + C (-614656 * u5_9 - 548800 * u5_6 - 11760 * u5_3 + 2660 * u5_0 - 1646400 * v5_7
            - 70560 * v5_4 + 23940 * v5_1) * X ^ 9
        + C (-614656 * u5_6 - 548800 * u5_3 - 11760 * u5_0 - 1646400 * v5_4 - 70560 * v5_1
            ) * X ^ 6
        + C (-614656 * u5_3 - 548800 * u5_0 - 1646400 * v5_1) * X ^ 3
        + C (-614656 * u5_0) := by
    simp only [map_add, map_sub, map_mul, map_neg, map_ofNat]; ring
  rw [key, e21, e18, e15, e12, e9, e6, e3, e0]
  simp

/-! ## `n = 7`: `secp256k1.preΨ' 7` is coprime to its derivative -/

/-- `(preΨ' 7)′ = 168X²³ + 579768X²⁰ − 37834272X¹⁷ − ⋯ − 1983460491264X²` — the
derivative of the concrete 7-division polynomial. -/
private lemma secp256k1_preΨ₇_derivative :
    derivative (secp256k1.preΨ' 7)
      = 168 * X ^ 23 + 579768 * X ^ 20 - 37834272 * X ^ 17 - 4268785920 * X ^ 14
        - 26744911872 * X ^ 11 - 235282940928 * X ^ 8 - 1983460491264 * X ^ 5
        - 1983460491264 * X ^ 2 := by
  rw [secp256k1_preΨ₇]
  simp only [derivative_add, derivative_sub, derivative_mul, derivative_ofNat,
    derivative_C, derivative_X_pow, derivative_X, Nat.cast_ofNat, map_ofNat, Nat.reduceSub,
    zero_mul, mul_zero, zero_add, add_zero, sub_zero, mul_one]
  ring

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`): `u = u7_21·X²¹ + ⋯ + u7_0`
(deg 21, exponents `≡ 0 mod 3`) and `v = v7_22·X²² + ⋯ + v7_1·X` (deg 22, exponents
`≡ 1 mod 3`), with `u·(preΨ' 7) + v·(preΨ' 7)′ = 1`. -/
private def u7_21 : ZMod Secp256k1.p :=
  22869295865591509752656913320170309861882195809517511110223723989380176545170
private def u7_18 : ZMod Secp256k1.p :=
  106233510044546409635640790583812462585660494939146751889751335749911056255661
private def u7_15 : ZMod Secp256k1.p :=
  703594002184619188611868400570085649302904296561641589055405919881016231814
private def u7_12 : ZMod Secp256k1.p :=
  81010031984365796836743128133156686046726391804689606001136754324535946833455
private def u7_9 : ZMod Secp256k1.p :=
  100361735720667722243512642947812278888669098785725183237424150102838336846031
private def u7_6 : ZMod Secp256k1.p :=
  92998714396874781351386415376569342545285585345032883787436265208649729448360
private def u7_3 : ZMod Secp256k1.p :=
  37345734766814145782977593351747371975141889392824396713356924407298116875411
private def u7_0 : ZMod Secp256k1.p :=
  104312091503547336002174865974034599278343573453365127323364127481039549803657
private def v7_22 : ZMod Secp256k1.p :=
  27995134981596069282865374863831547385739071341013578046938407502419701311867
private def v7_19 : ZMod Secp256k1.p :=
  70987904668148723548667593689748265121913551591087666967860822099140009369727
private def v7_16 : ZMod Secp256k1.p :=
  83752630924135947205396332574879500435666503265483835307057492880374969935218
private def v7_13 : ZMod Secp256k1.p :=
  60795616322198260964696380504637791324876773797471140534867689374494756309227
private def v7_10 : ZMod Secp256k1.p :=
  91843685305206661337851977053135916215549674679134743242106000947496021082317
private def v7_7 : ZMod Secp256k1.p :=
  711708316615692242059789278929537404362183377195060757286678895152683944659
private def v7_4 : ZMod Secp256k1.p :=
  29322110405154746969491982288947483121998048895711548906344633264653816340756
private def v7_1 : ZMod Secp256k1.p :=
  104676592392286377203923331037964622925268675017767392025564801021510840523617

/-- **`preΨ' 7` (= the univariate 7-division polynomial) is squarefree, by certificate: it
is coprime to its own derivative** (B4 at `n = 7`). The type is exactly
`IsCoprime (preΨ' 7) (derivative (preΨ' 7))` over `𝔽_p`. Explicit Bézout certificate over
`𝔽_p`; the analogue of the separability of `[7]`. (Downstream, not here: with
`deg = 24 = (7² − 1)/2` this squarefreeness feeds a later `𝔽̄_p` count of distinct
7-torsion `x`-coordinates.) -/
theorem secp256k1_isCoprime_preΨ₇_derivative :
    IsCoprime (secp256k1.preΨ' 7) (derivative (secp256k1.preΨ' 7)) := by
  refine ⟨C u7_21 * X ^ 21 + C u7_18 * X ^ 18 + C u7_15 * X ^ 15 + C u7_12 * X ^ 12
      + C u7_9 * X ^ 9 + C u7_6 * X ^ 6 + C u7_3 * X ^ 3 + C u7_0,
    C v7_22 * X ^ 22 + C v7_19 * X ^ 19 + C v7_16 * X ^ 16 + C v7_13 * X ^ 13 + C v7_10 * X ^ 10
      + C v7_7 * X ^ 7 + C v7_4 * X ^ 4 + C v7_1 * X, ?_⟩
  rw [secp256k1_preΨ₇_derivative, secp256k1_preΨ₇]
  have e45 : (7 * u7_21 + 168 * v7_22 : ZMod Secp256k1.p) = 0 := by native_decide
  have e42 : (27608 * u7_21 + 7 * u7_18 + 579768 * v7_22 + 168 * v7_19
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e39 : (-2101904 * u7_21 + 27608 * u7_18 + 7 * u7_15 - 37834272 * v7_22 + 579768 * v7_19
      + 168 * v7_16
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e36 : (-284585728 * u7_21 - 2101904 * u7_18 + 27608 * u7_15 + 7 * u7_12
      - 4268785920 * v7_22 - 37834272 * v7_19 + 579768 * v7_16 + 168 * v7_13
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e33 : (-2228742656 * u7_21 - 284585728 * u7_18 - 2101904 * u7_15 + 27608 * u7_12 + 7 * u7_9
      - 26744911872 * v7_22 - 4268785920 * v7_19 - 37834272 * v7_16 + 579768 * v7_13 + 168 * v7_10
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e30 : (-26142548992 * u7_21 - 2228742656 * u7_18 - 284585728 * u7_15 - 2101904 * u7_12
      + 27608 * u7_9 + 7 * u7_6 - 235282940928 * v7_22 - 26744911872 * v7_19 - 4268785920 * v7_16
      - 37834272 * v7_13 + 579768 * v7_10 + 168 * v7_7
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e27 : (-330576748544 * u7_21 - 26142548992 * u7_18 - 2228742656 * u7_15 - 284585728 * u7_12
      - 2101904 * u7_9 + 27608 * u7_6 + 7 * u7_3 - 1983460491264 * v7_22 - 235282940928 * v7_19
      - 26744911872 * v7_16 - 4268785920 * v7_13 - 37834272 * v7_10 + 579768 * v7_7 + 168 * v7_4
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e24 : (-661153497088 * u7_21 - 330576748544 * u7_18 - 26142548992 * u7_15
      - 2228742656 * u7_12 - 284585728 * u7_9 - 2101904 * u7_6 + 27608 * u7_3 + 7 * u7_0
      - 1983460491264 * v7_22 - 1983460491264 * v7_19 - 235282940928 * v7_16 - 26744911872 * v7_13
      - 4268785920 * v7_10 - 37834272 * v7_7 + 579768 * v7_4 + 168 * v7_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e21 : (377801998336 * u7_21 - 661153497088 * u7_18 - 330576748544 * u7_15
      - 26142548992 * u7_12 - 2228742656 * u7_9 - 284585728 * u7_6 - 2101904 * u7_3 + 27608 * u7_0
      - 1983460491264 * v7_19 - 1983460491264 * v7_16 - 235282940928 * v7_13 - 26744911872 * v7_10
      - 4268785920 * v7_7 - 37834272 * v7_4 + 579768 * v7_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e18 : (377801998336 * u7_18 - 661153497088 * u7_15 - 330576748544 * u7_12
      - 26142548992 * u7_9 - 2228742656 * u7_6 - 284585728 * u7_3 - 2101904 * u7_0
      - 1983460491264 * v7_16 - 1983460491264 * v7_13 - 235282940928 * v7_10 - 26744911872 * v7_7
      - 4268785920 * v7_4 - 37834272 * v7_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e15 : (377801998336 * u7_15 - 661153497088 * u7_12 - 330576748544 * u7_9
      - 26142548992 * u7_6 - 2228742656 * u7_3 - 284585728 * u7_0 - 1983460491264 * v7_13
      - 1983460491264 * v7_10 - 235282940928 * v7_7 - 26744911872 * v7_4 - 4268785920 * v7_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e12 : (377801998336 * u7_12 - 661153497088 * u7_9 - 330576748544 * u7_6
      - 26142548992 * u7_3 - 2228742656 * u7_0 - 1983460491264 * v7_10 - 1983460491264 * v7_7
      - 235282940928 * v7_4 - 26744911872 * v7_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e9 : (377801998336 * u7_9 - 661153497088 * u7_6 - 330576748544 * u7_3 - 26142548992 * u7_0
      - 1983460491264 * v7_7 - 1983460491264 * v7_4 - 235282940928 * v7_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e6 : (377801998336 * u7_6 - 661153497088 * u7_3 - 330576748544 * u7_0
      - 1983460491264 * v7_4 - 1983460491264 * v7_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e3 : (377801998336 * u7_3 - 661153497088 * u7_0 - 1983460491264 * v7_1
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e0 : (377801998336 * u7_0 : ZMod Secp256k1.p) = 1 := by native_decide
  -- collapse the Bézout product to one `C` per power of `X`, then use the
  -- residue facts.
  have key : (C u7_21 * X ^ 21 + C u7_18 * X ^ 18 + C u7_15 * X ^ 15 + C u7_12 * X ^ 12
        + C u7_9 * X ^ 9 + C u7_6 * X ^ 6 + C u7_3 * X ^ 3 + C u7_0)
        * (7 * X ^ 24 + 27608 * X ^ 21 - 2101904 * X ^ 18 - 284585728 * X ^ 15
          - 2228742656 * X ^ 12 - 26142548992 * X ^ 9 - 330576748544 * X ^ 6
          - 661153497088 * X ^ 3 + 377801998336)
      + (C v7_22 * X ^ 22 + C v7_19 * X ^ 19 + C v7_16 * X ^ 16 + C v7_13 * X ^ 13
        + C v7_10 * X ^ 10 + C v7_7 * X ^ 7 + C v7_4 * X ^ 4 + C v7_1 * X)
        * (168 * X ^ 23 + 579768 * X ^ 20 - 37834272 * X ^ 17 - 4268785920 * X ^ 14
          - 26744911872 * X ^ 11 - 235282940928 * X ^ 8 - 1983460491264 * X ^ 5
          - 1983460491264 * X ^ 2)
      = C (7 * u7_21 + 168 * v7_22) * X ^ 45
        + C (27608 * u7_21 + 7 * u7_18 + 579768 * v7_22 + 168 * v7_19) * X ^ 42
        + C (-2101904 * u7_21 + 27608 * u7_18 + 7 * u7_15 - 37834272 * v7_22 + 579768 * v7_19
            + 168 * v7_16) * X ^ 39
        + C (-284585728 * u7_21 - 2101904 * u7_18 + 27608 * u7_15 + 7 * u7_12 - 4268785920 * v7_22
            - 37834272 * v7_19 + 579768 * v7_16 + 168 * v7_13) * X ^ 36
        + C (-2228742656 * u7_21 - 284585728 * u7_18 - 2101904 * u7_15 + 27608 * u7_12 + 7 * u7_9
            - 26744911872 * v7_22 - 4268785920 * v7_19 - 37834272 * v7_16 + 579768 * v7_13
            + 168 * v7_10) * X ^ 33
        + C (-26142548992 * u7_21 - 2228742656 * u7_18 - 284585728 * u7_15 - 2101904 * u7_12
            + 27608 * u7_9 + 7 * u7_6 - 235282940928 * v7_22 - 26744911872 * v7_19
            - 4268785920 * v7_16 - 37834272 * v7_13 + 579768 * v7_10 + 168 * v7_7) * X ^ 30
        + C (-330576748544 * u7_21 - 26142548992 * u7_18 - 2228742656 * u7_15 - 284585728 * u7_12
            - 2101904 * u7_9 + 27608 * u7_6 + 7 * u7_3 - 1983460491264 * v7_22
            - 235282940928 * v7_19 - 26744911872 * v7_16 - 4268785920 * v7_13 - 37834272 * v7_10
            + 579768 * v7_7 + 168 * v7_4) * X ^ 27
        + C (-661153497088 * u7_21 - 330576748544 * u7_18 - 26142548992 * u7_15
            - 2228742656 * u7_12 - 284585728 * u7_9 - 2101904 * u7_6 + 27608 * u7_3 + 7 * u7_0
            - 1983460491264 * v7_22 - 1983460491264 * v7_19 - 235282940928 * v7_16
            - 26744911872 * v7_13 - 4268785920 * v7_10 - 37834272 * v7_7 + 579768 * v7_4
            + 168 * v7_1) * X ^ 24
        + C (377801998336 * u7_21 - 661153497088 * u7_18 - 330576748544 * u7_15
            - 26142548992 * u7_12 - 2228742656 * u7_9 - 284585728 * u7_6 - 2101904 * u7_3
            + 27608 * u7_0 - 1983460491264 * v7_19 - 1983460491264 * v7_16 - 235282940928 * v7_13
            - 26744911872 * v7_10 - 4268785920 * v7_7 - 37834272 * v7_4 + 579768 * v7_1) * X ^ 21
        + C (377801998336 * u7_18 - 661153497088 * u7_15 - 330576748544 * u7_12
            - 26142548992 * u7_9 - 2228742656 * u7_6 - 284585728 * u7_3 - 2101904 * u7_0
            - 1983460491264 * v7_16 - 1983460491264 * v7_13 - 235282940928 * v7_10
            - 26744911872 * v7_7 - 4268785920 * v7_4 - 37834272 * v7_1) * X ^ 18
        + C (377801998336 * u7_15 - 661153497088 * u7_12 - 330576748544 * u7_9
            - 26142548992 * u7_6 - 2228742656 * u7_3 - 284585728 * u7_0 - 1983460491264 * v7_13
            - 1983460491264 * v7_10 - 235282940928 * v7_7 - 26744911872 * v7_4 - 4268785920 * v7_1
            ) * X ^ 15
        + C (377801998336 * u7_12 - 661153497088 * u7_9 - 330576748544 * u7_6 - 26142548992 * u7_3
            - 2228742656 * u7_0 - 1983460491264 * v7_10 - 1983460491264 * v7_7
            - 235282940928 * v7_4 - 26744911872 * v7_1) * X ^ 12
        + C (377801998336 * u7_9 - 661153497088 * u7_6 - 330576748544 * u7_3 - 26142548992 * u7_0
            - 1983460491264 * v7_7 - 1983460491264 * v7_4 - 235282940928 * v7_1) * X ^ 9
        + C (377801998336 * u7_6 - 661153497088 * u7_3 - 330576748544 * u7_0
            - 1983460491264 * v7_4 - 1983460491264 * v7_1) * X ^ 6
        + C (377801998336 * u7_3 - 661153497088 * u7_0 - 1983460491264 * v7_1) * X ^ 3
        + C (377801998336 * u7_0) := by
    simp only [map_add, map_sub, map_mul, map_neg, map_ofNat]; ring
  rw [key, e45, e42, e39, e36, e33, e30, e27, e24, e21, e18, e15, e12, e9, e6, e3, e0]
  simp

end Ecdlp.Curve
