import Mathlib
import Ecdlp.Proved.P256GeneratorOrder

/-!
# NIST P-256: the rational-point group is finite, and `n ∣ #E(𝔽_p)`

Mirrors secp256k1's `Ecdlp/Proved/CurveCardinality.lean` for the P-256 domain. The first
verified rung about the curve cardinality `#E(𝔽_p)` itself (all prior P-256 point-counting
work stayed inside the base-point subgroup `⟨G⟩`). Two facts:

* `Finite P256.toAffine.Point` — the group of `𝔽_p`-rational points is finite (points inject
  into `Option (𝔽_p × 𝔽_p)`, which is finite since `𝔽_p` is). Without this, Mathlib's
  `Nat.card E.toAffine.Point` is junk `0`; with it, the count is real.
* `p256_n_dvd_card_point : P256.n ∣ Nat.card P256.toAffine.Point` — the prime base-point order
  divides `#E` (Lagrange on `⟨G⟩`, whose order is the proved `n`).

This is only the **weak keystone**: it pins `#E ∈ {n, 2n, 3n, …}`. The **strong keystone**
`#E = n` (cofactor 1) is **NOT** proved here for P-256. The secp256k1 curve-specific route
(`CurveCardinalityExact.lean`: `#E ≤ 2p+1 < 3n` together with `E[2] = {O}`, the latter from
`−7` being a non-cube so there is no nonzero 2-torsion) is `j = 0`-specific and does **not**
transfer to P-256, whose `j`-invariant is nonzero (`c₄ = 144 ≠ 0`). A strong keystone for
P-256 would require the general Hasse bound, still absent from Mathlib v4.31.
-/

open WeierstrassCurve.Affine

namespace Ecdlp.P256

/-- The P-256 `𝔽_p`-rational point group is **finite**: `Point ↪ Option (𝔽_p × 𝔽_p)`. -/
instance instFiniteP256Point : Finite P256.toAffine.Point := by
  apply Finite.of_injective
    (fun P : P256.toAffine.Point =>
      match P with
      | .zero => (none : Option (ZMod p × ZMod p))
      | .some (x := x) (y := y) _ => some (x, y))
  intro P Q h
  cases P <;> cases Q <;> simp_all

/-- The concrete P-256 crypto subgroup `⟨G⟩ = zmultiples G`. -/
abbrev p256Grp : AddSubgroup P256.toAffine.Point := AddSubgroup.zmultiples p256G

/-- **`⟨G⟩` has exactly `n` elements**, from `Nat.card (zmultiples g) = addOrderOf g` and
`addOrderOf G = n`. -/
theorem p256_grp_card : Nat.card ↥p256Grp = n := by
  rw [Nat.card_zmultiples, p256_generator_addOrderOf]

/-- **`n ∣ #E(𝔽_p)`.** The prime base-point order divides the P-256 curve cardinality —
Lagrange applied to the subgroup `⟨G⟩` of proved order `n`. This is the weak keystone
(`#E ∈ {n, 2n, 3n, …}`); the strong keystone `#E = n` is not established here (see the header:
the secp256k1 `j = 0` route does not transfer, and Hasse is a Mathlib gap). -/
theorem p256_n_dvd_card_point :
    n ∣ Nat.card P256.toAffine.Point := by
  rw [← p256_grp_card]
  exact ⟨p256Grp.index, (AddSubgroup.card_mul_index p256Grp).symm⟩

end Ecdlp.P256
