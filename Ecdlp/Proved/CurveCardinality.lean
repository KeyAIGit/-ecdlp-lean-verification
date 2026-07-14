import Mathlib
import Ecdlp.Proved.SubgroupOrder
import Ecdlp.Proved.AffinePointFinite

/-!
# secp256k1: the rational-point group is finite, and `n ∣ #E(𝔽_p)`

The first verified rung about the curve cardinality `#E(𝔽_p)` itself (all prior point-counting
work stayed inside the base-point subgroup `⟨G⟩`). Two facts:

* `Finite secp256k1.toAffine.Point` — the group of `𝔽_p`-rational points is finite (points inject
  into `Option (𝔽_p × 𝔽_p)`, which is finite since `𝔽_p` is). Without this, Mathlib's
  `Nat.card E.toAffine.Point` (used in `EllipticCurve/LFunction.lean`) is junk `0`; with it, the
  count is real.
* `secp256k1_n_dvd_card_point : Secp256k1.n ∣ Nat.card secp256k1.toAffine.Point` — the prime
  base-point order divides `#E` (Lagrange on `⟨G⟩`, whose order is the proved `n`).

This is the **reachable half of the strong-keystone certificate route** (`notes/HASSE_RECON.md`):
it pins `#E ∈ {n, 2n, 3n, …}`; the strong keystone `#E = n` (cofactor 1) is **now proved** on top
of this — *curve-specifically* in `CurveCardinalityExact.lean` (`#E ≤ 2p+1 < 3n` plus `E[2] = {O}`),
without the general Hasse bound or Schoof (both still absent from Mathlib v4.31).
-/

open WeierstrassCurve.Affine

namespace Ecdlp.Curve

/-- The secp256k1 `𝔽_p`-rational point group is **finite** — a specialisation of the general
`WeierstrassCurve.Affine.instFinitePoint` (`Point ↪ Option (R × R)`, needing only `[CommRing R]`
`[Finite R]`), since `ZMod Secp256k1.p` is a finite commutative ring. -/
instance instFiniteSecp256k1Point : Finite secp256k1.toAffine.Point := inferInstance

/-- **`n ∣ #E(𝔽_p)`.** The prime base-point order divides the secp256k1 curve cardinality —
Lagrange applied to the subgroup `⟨G⟩` of proved order `n`. The first verified fact about `#E`
itself; the strong keystone `#E = n` is **now proved** on top (`CurveCardinalityExact.lean`,
curve-specifically, no Hasse/Schoof; see `notes/HASSE_RECON.md`). -/
theorem secp256k1_n_dvd_card_point :
    Secp256k1.n ∣ Nat.card secp256k1.toAffine.Point := by
  rw [← secp256k1_grp_card]
  exact ⟨secp256k1Grp.index, (AddSubgroup.card_mul_index secp256k1Grp).symm⟩

end Ecdlp.Curve
