import Mathlib
import Ecdlp.Proved.SubgroupOrder
import Ecdlp.Proved.CurveFullGroup

/-!
# The full rational-point group structure theorem for secp256k1

`SubgroupOrder.lean` established the discrete-log isomorphism onto the *base-point subgroup*
`⟨G⟩ = zmultiples G`:
`secp256k1_dlogEquiv : ZMod n ≃+ ↥secp256k1Grp`, i.e. `c ↦ c·G` is an additive-group
isomorphism from the scalar ring `ZMod n` onto the cyclic crypto subgroup `⟨G⟩`.

`CurveFullGroup.lean` established the cofactor-`1` fact `secp256k1_grp_eq_top : ⟨G⟩ = ⊤`
(the base-point subgroup is the *whole* point group), from the exact point count `#E = n`.

Composing the two lifts the discrete-log isomorphism from the subgroup to the **entire**
rational point group `E(𝔽_p)`:

```
ZMod n  ≃+  ↥⟨G⟩  ≃+  ↥(⊤ : AddSubgroup E(𝔽_p))  ≃+  E(𝔽_p)
        │            │                              │
  dlogEquiv   addSubgroupCongr grp_eq_top     AddSubgroup.topEquiv
```

The middle equivalence transports across `⟨G⟩ = ⊤` (`AddEquiv.addSubgroupCongr`, the additive
image of `MulEquiv.subgroupCongr`); the last strips the `⊤` subtype (`AddSubgroup.topEquiv`).

This is the complete additive-group structure theorem for the secp256k1 point group: it is
isomorphic to `ℤ/n`. Unconditional given `#E = n` (which underlies `grp_eq_top`); no new
axioms. It inherits the `Lean.ofReduceBool` provenance of the order keystone through
`secp256k1_grp_eq_top`.
-/

open WeierstrassCurve.Affine

namespace Ecdlp.Curve

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **The full point-group structure theorem for secp256k1.**
`E(𝔽_p) ≃+ ℤ/n` as additive groups: base-point multiplication `c ↦ c·G` is an
additive-group isomorphism from the scalar ring `ZMod n` onto the *entire* group of rational
points, not merely the base-point subgroup `⟨G⟩`.

It is the composition of three isomorphisms:
* `secp256k1_dlogEquiv : ZMod n ≃+ ↥⟨G⟩` — the discrete-log bijection (from `addOrderOf G = n`);
* `AddEquiv.addSubgroupCongr secp256k1_grp_eq_top : ↥⟨G⟩ ≃+ ↥(⊤ : AddSubgroup _)` — transport
  across the cofactor-`1` identity `⟨G⟩ = ⊤`;
* `AddSubgroup.topEquiv : ↥(⊤ : AddSubgroup _) ≃+ E(𝔽_p)` — the top subgroup is the group.

Unconditional given `#E = n` (via `secp256k1_grp_eq_top`); the computational inversion of this
map is the open ECDLP hardness conjecture, but the bijection itself is a theorem. -/
noncomputable def secp256k1_pointGroupEquiv :
    ZMod Secp256k1.n ≃+ secp256k1.toAffine.Point :=
  secp256k1_dlogEquiv.trans
    ((AddEquiv.addSubgroupCongr secp256k1_grp_eq_top).trans AddSubgroup.topEquiv)

/-- On elements, the structure isomorphism is still base-point multiplication `c ↦ c·G`,
now valued in the ambient point group `E(𝔽_p)` (via the coercion `↥⟨G⟩ → E(𝔽_p)`). -/
@[simp] theorem secp256k1_pointGroupEquiv_apply (c : ZMod Secp256k1.n) :
    secp256k1_pointGroupEquiv c
      = ((c • secp256k1Gₙ : ↥secp256k1Grp) : secp256k1.toAffine.Point) := rfl

/-- **`E(𝔽_p)` is isomorphic, as an additive group, to `ℤ/n`.** The complete structure theorem
for the secp256k1 rational point group, packaged as an existence statement. Unconditional given
`#E = n` (`secp256k1_grp_eq_top`); no new axioms. Inherits `Lean.ofReduceBool` through the order
keystone. -/
theorem secp256k1_point_group_equiv_exists :
    Nonempty (ZMod Secp256k1.n ≃+ secp256k1.toAffine.Point) :=
  ⟨secp256k1_pointGroupEquiv⟩

end Ecdlp.Curve
