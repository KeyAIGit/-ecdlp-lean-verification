import Mathlib
import Ecdlp.Proved.Secp256k1Curve
import Ecdlp.Proved.Torsion

/-!
# secp256k1-specific torsion: the abstract `E[n]` results, named for the curve

`Ecdlp/Proved/Torsion.lean` proves the `E[n]` facts generically over any
`AddCommGroup`. This file specializes them to the **actual secp256k1 elliptic-curve
point group** `secp256k1.toAffine.Point` (Mathlib's `WeierstrassCurve.Affine.Point`,
an `AddCommGroup` once `𝔽_p` is a field and the curve is elliptic), so the knowledge
base contains theorems that name secp256k1 directly — the navigable bridge from the
abstract torsion layer to the concrete curve.

It also realizes the SEC2 base point `G` as a genuine element of that group
(`secp256k1_G`), non-zero (not the point at infinity), via the proved Weierstrass
equation. All results carry `[Fact (Nat.Prime Secp256k1.p)]` (published primality of the
field characteristic) — a hypothesis discharged by the `Secp256k1PrimeP` instance, not an
axiom.
-/

namespace Ecdlp.Curve

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **`E[n]` for secp256k1 = the points of order dividing `n`.** A point of the secp256k1
elliptic-curve group lies in the `n`-torsion subgroup iff its additive order divides `n`
— the curve-named instance of `[n]P = O ⟺ ord(P) ∣ n`. -/
theorem secp256k1_mem_torsionBy_iff_addOrderOf_dvd {n : ℕ}
    (P : secp256k1.toAffine.Point) :
    P ∈ AddSubgroup.torsionBy secp256k1.toAffine.Point (n : ℤ) ↔ addOrderOf P ∣ n :=
  Ecdlp.Torsion.mem_torsionBy_iff_addOrderOf_dvd P

/-- **`E[n] = ker[n]` for secp256k1.** The `n`-torsion subgroup of the secp256k1 point
group is exactly the kernel of the multiplication-by-`n` endomorphism. -/
theorem secp256k1_torsionBy_eq_ker_nsmul (n : ℕ) :
    AddSubgroup.torsionBy secp256k1.toAffine.Point (n : ℤ)
      = (nsmulAddMonoidHom n : secp256k1.toAffine.Point →+ secp256k1.toAffine.Point).ker :=
  Ecdlp.Torsion.torsionBy_eq_ker_nsmul n

/-- **The secp256k1 base point `G` as an element of the Mathlib group `E(𝔽ₚ)`.** Built
from the proved Weierstrass equation `secp256k1_generator_equation` via `Point.mk`, this
is the SEC2 generator realized as a genuine point of `secp256k1.toAffine.Point`. -/
def secp256k1_G : secp256k1.toAffine.Point :=
  WeierstrassCurve.Affine.Point.mk secp256k1_generator_equation

/-- **The base point `G` is non-zero** (it is an affine point, not the point at infinity
`0`). With `secp256k1_mem_torsionBy_iff_addOrderOf_dvd` this anchors the prime-order-`n`
subgroup `⟨G⟩` that ECDLP operates in. -/
theorem secp256k1_G_ne_zero : secp256k1_G ≠ 0 :=
  WeierstrassCurve.Affine.Point.some_ne_zero _

/-- **Torsion filtration for secp256k1: `E[m] ≤ E[n]` when `m ∣ n`.** The curve-named
instance of the monotone torsion lattice. -/
theorem secp256k1_torsionBy_dvd_le {m k : ℤ} (h : m ∣ k) :
    AddSubgroup.torsionBy secp256k1.toAffine.Point m
      ≤ AddSubgroup.torsionBy secp256k1.toAffine.Point k :=
  Ecdlp.Torsion.torsionBy_dvd_le h

/-- **A finite-order point's subgroup lies in secp256k1 `E[n]`.** If a curve point `P`
has order dividing `n`, the cyclic subgroup `⟨P⟩` it generates is `n`-torsion — the
curve-named form of `⟨G⟩ ⊆ E[n]`. -/
theorem secp256k1_zmultiples_le_torsionBy {n : ℕ} {P : secp256k1.toAffine.Point}
    (h : addOrderOf P ∣ n) :
    AddSubgroup.zmultiples P ≤ AddSubgroup.torsionBy secp256k1.toAffine.Point (n : ℤ) :=
  Ecdlp.Torsion.zmultiples_le_torsionBy h

end Ecdlp.Curve
