import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.CoprimePsi3Psi7

/-!
# `preΨ' 5` and `preΨ' 7` are coprime for secp256k1 — the 5- and 7-torsion loci are disjoint (`E[5] ⊥ E[7]`)

The 5- and 7-division polynomials of `E : Y² = X³ + 7` share no root: **no nonidentity point is
simultaneously 5-torsion and 7-torsion.** If a point `P` of order 5 and a point `Q` of order 7
shared an `x`-coordinate they would satisfy `Q = ±P`, forcing `ord Q = ord P`, i.e. `5 = 7` —
impossible. Equivalently `gcd(ψ₅, ψ₇) = 1`, a coprimality that is **not** in Mathlib. We certify it
constructively with an explicit **Bézout certificate** `u·(preΨ' 5) + v·(preΨ' 7) = 1` whose
cofactors come from extended-Euclid over `𝔽_p` (CAS; `scripts/certs/torsion_disjoint_5_7.py`, prints
`CERT_OK`; `Res(ψ₅,ψ₇) = 2¹⁹²·3¹⁴⁴·7⁹⁶`, whose prime support `{2,3,7}` is exactly the bad-reduction
primes of the curve — the only primes where the two loci can collide on reduction).

This is the last missing pair among `{2,3,5,7}`: with `CoprimePsi2Psi5`, `CoprimePsi2Psi7`,
`CoprimePsi3Psi5`, `CoprimePsi3Psi7` (and the `Ψ₂Sq`/`Ψ₃` pairs) already landed, `E[5] ⊥ E[7]`
completes pairwise disjointness of the `{2,3,5,7}`-torsion `x`-loci.

Both `preΨ' 5` (degree 12) and `preΨ' 7` (degree 24) live entirely on exponents `≡ 0 (mod 3)`
(they are polynomials in `X³`), so both Bézout cofactors are supported on the same `X³`-lattice
(`u` on `X²¹,…,X⁰`, eight terms; `v` on `X⁹,…,X⁰`, four terms) and the Bézout product collapses
onto the twelve powers `X³³,X³⁰,…,X³,X⁰` — twelve residue equations in `ZMod p` discharged by
`native_decide`, the twelve-power sibling of `CoprimePsi3Psi7`'s ten. Concrete forms reused from
`secp256k1_preΨ₅`/`secp256k1_preΨ₇`. No new axioms beyond the compiler trust of `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`, reduced to `ZMod p`):
`u = A₂₁X²¹+A₁₈X¹⁸+A₁₅X¹⁵+A₁₂X¹²+A₉X⁹+A₆X⁶+A₃X³+A₀` (cofactor of `preΨ' 5`, sparse on exponents
`≡ 0 mod 3`) and `v = B₉X⁹+B₆X⁶+B₃X³+B₀` (cofactor of `preΨ' 7`, same lattice), with
`u·(preΨ' 5) + v·(preΨ' 7) = 1`. -/
private def A21 : ZMod Secp256k1.p :=
  25418754901788692877968230069301035781322345993327045055693078279732374474840
private def A18 : ZMod Secp256k1.p :=
  31149924388287969177679352204388989030931030203670805087398347324246046343066
private def A15 : ZMod Secp256k1.p :=
  49211186798648142805860513445084897575145745245210730171181789223371186977209
private def A12 : ZMod Secp256k1.p :=
  61273599372568826488843419201368276182583111178355289425664316332950687168391
private def A9 : ZMod Secp256k1.p :=
  100126217730918582591344329768469461862996608308454767755954434804464573256009
private def A6 : ZMod Secp256k1.p :=
  34483031552161642009058939809038812941302927987352929355600269828150451256656
private def A3 : ZMod Secp256k1.p :=
  14145085083017900955176524238955464528192217881010034248940511093759575280120
private def A0 : ZMod Secp256k1.p :=
  53257433782909105051629229861861967795803404588319141155083360011440504424993
private def B9 : ZMod Secp256k1.p :=
  64552381668233930389716253528133480051391170480223942131260361234411757283445
private def B6 : ZMod Secp256k1.p :=
  110453074674719764909262463398144833790662114234606687033418896865394734435777
private def B3 : ZMod Secp256k1.p :=
  54531528258405019135935158326131517304662898818019237677375051197195086990683
private def B0 : ZMod Secp256k1.p :=
  17567766988617774777329237133145389294429870267045848376832079601129951103061

/-- **`preΨ' 5` and `preΨ' 7` are coprime — the 5-torsion and 7-torsion `x`-loci are disjoint**
(`E[5] ⊥ E[7]`). Their only possible common root would be a nonidentity point annihilated by both
5- and 7-torsion, forcing `ord = 5` and `ord = 7` on one point (impossible); realized here by an
explicit Bézout certificate over `𝔽_p`. This coprimality is missing from Mathlib. Completes the
pairwise-disjoint `{2,3,5,7}`-torsion family (sibling of `CoprimePsi3Psi7`, twelve collapsed
powers instead of ten). -/
theorem secp256k1_isCoprime_preΨ₅_preΨ₇ :
    IsCoprime (secp256k1.preΨ' 5) (secp256k1.preΨ' 7) := by
  refine ⟨C A21 * X ^ 21 + C A18 * X ^ 18 + C A15 * X ^ 15 + C A12 * X ^ 12 + C A9 * X ^ 9
      + C A6 * X ^ 6 + C A3 * X ^ 3 + C A0,
    C B9 * X ^ 9 + C B6 * X ^ 6 + C B3 * X ^ 3 + C B0, ?_⟩
  rw [secp256k1_preΨ₅, secp256k1_preΨ₇]
  have e0 : (- 614656 * A0 + 377801998336 * B0 : ZMod Secp256k1.p) = 1 := by native_decide
  have e3 : (- 548800 * A0 - 614656 * A3 - 661153497088 * B0 + 377801998336 * B3
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e6 : (- 11760 * A0 - 548800 * A3 - 614656 * A6 - 330576748544 * B0 - 661153497088 * B3
      + 377801998336 * B6 : ZMod Secp256k1.p) = 0 := by native_decide
  have e9 : (2660 * A0 - 11760 * A3 - 548800 * A6 - 614656 * A9 - 26142548992 * B0
      - 330576748544 * B3 - 661153497088 * B6 + 377801998336 * B9 : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e12 : (5 * A0 + 2660 * A3 - 11760 * A6 - 548800 * A9 - 614656 * A12 - 2228742656 * B0
      - 26142548992 * B3 - 330576748544 * B6 - 661153497088 * B9 : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e15 : (5 * A3 + 2660 * A6 - 11760 * A9 - 548800 * A12 - 614656 * A15 - 284585728 * B0
      - 2228742656 * B3 - 26142548992 * B6 - 330576748544 * B9 : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e18 : (5 * A6 + 2660 * A9 - 11760 * A12 - 548800 * A15 - 614656 * A18 - 2101904 * B0
      - 284585728 * B3 - 2228742656 * B6 - 26142548992 * B9 : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e21 : (5 * A9 + 2660 * A12 - 11760 * A15 - 548800 * A18 - 614656 * A21 + 27608 * B0
      - 2101904 * B3 - 284585728 * B6 - 2228742656 * B9 : ZMod Secp256k1.p) = 0 := by
    native_decide
  have e24 : (5 * A12 + 2660 * A15 - 11760 * A18 - 548800 * A21 + 7 * B0 + 27608 * B3
      - 2101904 * B6 - 284585728 * B9 : ZMod Secp256k1.p) = 0 := by native_decide
  have e27 : (5 * A15 + 2660 * A18 - 11760 * A21 + 7 * B3 + 27608 * B6 - 2101904 * B9
      : ZMod Secp256k1.p) = 0 := by native_decide
  have e30 : (5 * A18 + 2660 * A21 + 7 * B6 + 27608 * B9 : ZMod Secp256k1.p) = 0 := by native_decide
  have e33 : (5 * A21 + 7 * B9 : ZMod Secp256k1.p) = 0 := by native_decide
  have key : (C A21 * X ^ 21 + C A18 * X ^ 18 + C A15 * X ^ 15 + C A12 * X ^ 12 + C A9 * X ^ 9
        + C A6 * X ^ 6 + C A3 * X ^ 3 + C A0)
        * (5 * X ^ 12 + 2660 * X ^ 9 - 11760 * X ^ 6 - 548800 * X ^ 3 - 614656)
      + (C B9 * X ^ 9 + C B6 * X ^ 6 + C B3 * X ^ 3 + C B0)
        * (7 * X ^ 24 + 27608 * X ^ 21 - 2101904 * X ^ 18 - 284585728 * X ^ 15
          - 2228742656 * X ^ 12 - 26142548992 * X ^ 9 - 330576748544 * X ^ 6
          - 661153497088 * X ^ 3 + 377801998336)
      = C (- 614656 * A0 + 377801998336 * B0)
        + C (- 548800 * A0 - 614656 * A3 - 661153497088 * B0 + 377801998336 * B3) * X ^ 3
        + C (- 11760 * A0 - 548800 * A3 - 614656 * A6 - 330576748544 * B0 - 661153497088 * B3
            + 377801998336 * B6) * X ^ 6
        + C (2660 * A0 - 11760 * A3 - 548800 * A6 - 614656 * A9 - 26142548992 * B0
            - 330576748544 * B3 - 661153497088 * B6 + 377801998336 * B9) * X ^ 9
        + C (5 * A0 + 2660 * A3 - 11760 * A6 - 548800 * A9 - 614656 * A12 - 2228742656 * B0
            - 26142548992 * B3 - 330576748544 * B6 - 661153497088 * B9) * X ^ 12
        + C (5 * A3 + 2660 * A6 - 11760 * A9 - 548800 * A12 - 614656 * A15 - 284585728 * B0
            - 2228742656 * B3 - 26142548992 * B6 - 330576748544 * B9) * X ^ 15
        + C (5 * A6 + 2660 * A9 - 11760 * A12 - 548800 * A15 - 614656 * A18 - 2101904 * B0
            - 284585728 * B3 - 2228742656 * B6 - 26142548992 * B9) * X ^ 18
        + C (5 * A9 + 2660 * A12 - 11760 * A15 - 548800 * A18 - 614656 * A21 + 27608 * B0
            - 2101904 * B3 - 284585728 * B6 - 2228742656 * B9) * X ^ 21
        + C (5 * A12 + 2660 * A15 - 11760 * A18 - 548800 * A21 + 7 * B0 + 27608 * B3
            - 2101904 * B6 - 284585728 * B9) * X ^ 24
        + C (5 * A15 + 2660 * A18 - 11760 * A21 + 7 * B3 + 27608 * B6 - 2101904 * B9) * X ^ 27
        + C (5 * A18 + 2660 * A21 + 7 * B6 + 27608 * B9) * X ^ 30
        + C (5 * A21 + 7 * B9) * X ^ 33 := by
    simp only [map_add, map_sub, map_mul, map_neg, map_ofNat]; ring
  rw [key, e0, e3, e6, e9, e12, e15, e18, e21, e24, e27, e30, e33]
  simp

end Ecdlp.Curve
