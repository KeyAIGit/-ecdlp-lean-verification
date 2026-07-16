import Mathlib
import Ecdlp.Proved.DivisionPolynomialSquarefree
import Ecdlp.Proved.DivisionPolynomialDegree
import Ecdlp.Proved.FiveTorsion
import Ecdlp.Proved.SevenTorsion
import Ecdlp.Proved.Secp256k1PrimeP

/-!
# Separability of the division polynomials, and exact torsion `x`-locus sizes over `𝔽̄_p`

The vocabulary upgrade of the B4 certificates (`DivisionPolynomialSquarefree.lean`) and
their first payoff. Mathlib's `Polynomial.Separable` is *defined* as
`IsCoprime f (derivative f)` — so the Bézout certificates `u·ψₙ + v·ψₙ′ = 1` literally
**are** separability proofs:

* `secp256k1_Ψ₃_separable`, `secp256k1_preΨ₅_separable`, `secp256k1_preΨ₇_separable`.

Separability survives base change (`Separable.map`), and over the algebraic closure a
polynomial splits with `natDegree`-many roots (`IsAlgClosed.splits`,
`splits_iff_card_roots`); separability makes those roots distinct (`nodup_roots`).
Combining with the proved degrees (`4 = (3²−1)/2`, `12 = (5²−1)/2`, `24 = (7²−1)/2`):

* `ψₙ` has **exactly `(n²−1)/2` distinct roots in `𝔽̄_p`** for `n = 3, 5, 7`
  (`…_roots_card_bar` + `…_roots_nodup_bar`) — the `n`-torsion `x`-locus at full size,
  the counting input of node **N11** at small `n` (`notes/DIVISION_POLY_TORSION_MAP.md`):
  together with the `±y`-pairing (N12) this pins `#E[n](𝔽̄_p) = n²` once the point-level
  bridge is transported to the closure — the next rung.

No new certificates and no `native_decide` here — this file only re-labels the B4
certificates in Mathlib's separability vocabulary and harvests the root counts.
-/

namespace Ecdlp.Curve

open Polynomial

/-- The base-change hom `𝔽_p →+* 𝔽̄_p`. -/
private noncomputable abbrev φac :
    ZMod Secp256k1.p →+* AlgebraicClosure (ZMod Secp256k1.p) :=
  algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p))

/-- **`Ψ₃` is separable** — the B4 Bézout certificate, in Mathlib's vocabulary
(`Separable f` is by definition `IsCoprime f (derivative f)`). -/
theorem secp256k1_Ψ₃_separable : secp256k1.Ψ₃.Separable :=
  secp256k1_isCoprime_Ψ₃_derivative

/-- **`preΨ₅` (the univariate 5-division polynomial) is separable.** -/
theorem secp256k1_preΨ₅_separable : (secp256k1.preΨ' 5).Separable :=
  secp256k1_isCoprime_preΨ₅_derivative

/-- **`preΨ₇` (the univariate 7-division polynomial) is separable.** -/
theorem secp256k1_preΨ₇_separable : (secp256k1.preΨ' 7).Separable :=
  secp256k1_isCoprime_preΨ₇_derivative

section RootCounts

/-- Generic harvest: a separable polynomial of known degree over `𝔽_p` has exactly that
many roots (with multiplicity) over `𝔽̄_p`. -/
private theorem roots_card_map_of_separable {f : Polynomial (ZMod Secp256k1.p)}
    (hf : f.Separable) {d : ℕ} (hdeg : f.natDegree = d) :
    (f.map φac).roots.card = d := by
  have hsplit : (f.map φac).roots.card = (f.map φac).natDegree :=
    (Polynomial.splits_iff_card_roots).mp (IsAlgClosed.splits _)
  rw [hsplit, Polynomial.natDegree_map_eq_of_injective (RingHom.injective φac), hdeg]

/-- Generic harvest: separability makes the closure roots distinct. -/
private theorem roots_nodup_map_of_separable {f : Polynomial (ZMod Secp256k1.p)}
    (hf : f.Separable) : (f.map φac).roots.Nodup :=
  Polynomial.nodup_roots (hf.map)

/-- **`Ψ₃` has exactly `4 = (3²−1)/2` roots over `𝔽̄_p`** (with multiplicity — and they
are distinct, `secp256k1_Ψ₃_roots_nodup_bar`): the 3-torsion `x`-locus at full size. -/
theorem secp256k1_Ψ₃_roots_card_bar :
    ((secp256k1.Ψ₃).map φac).roots.card = 4 :=
  roots_card_map_of_separable secp256k1_Ψ₃_separable secp256k1_Ψ₃_natDegree

/-- The closure roots of `Ψ₃` are pairwise distinct. -/
theorem secp256k1_Ψ₃_roots_nodup_bar :
    ((secp256k1.Ψ₃).map φac).roots.Nodup :=
  roots_nodup_map_of_separable secp256k1_Ψ₃_separable

/-- **`preΨ₅` has exactly `12 = (5²−1)/2` roots over `𝔽̄_p`** (distinct by
`secp256k1_preΨ₅_roots_nodup_bar`): the 5-torsion `x`-locus at full size. -/
theorem secp256k1_preΨ₅_roots_card_bar :
    ((secp256k1.preΨ' 5).map φac).roots.card = 12 :=
  roots_card_map_of_separable secp256k1_preΨ₅_separable secp256k1_preΨ₅_natDegree

/-- The closure roots of `preΨ₅` are pairwise distinct. -/
theorem secp256k1_preΨ₅_roots_nodup_bar :
    ((secp256k1.preΨ' 5).map φac).roots.Nodup :=
  roots_nodup_map_of_separable secp256k1_preΨ₅_separable

/-- **`preΨ₇` has exactly `24 = (7²−1)/2` roots over `𝔽̄_p`** (distinct by
`secp256k1_preΨ₇_roots_nodup_bar`): the 7-torsion `x`-locus at full size. -/
theorem secp256k1_preΨ₇_roots_card_bar :
    ((secp256k1.preΨ' 7).map φac).roots.card = 24 :=
  roots_card_map_of_separable secp256k1_preΨ₇_separable secp256k1_preΨ₇_natDegree

/-- The closure roots of `preΨ₇` are pairwise distinct. -/
theorem secp256k1_preΨ₇_roots_nodup_bar :
    ((secp256k1.preΨ' 7).map φac).roots.Nodup :=
  roots_nodup_map_of_separable secp256k1_preΨ₇_separable

end RootCounts

end Ecdlp.Curve
