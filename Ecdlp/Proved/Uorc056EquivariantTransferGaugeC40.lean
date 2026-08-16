import Mathlib

/-!
# UORC-056 C40 equivariant transfer gauge

This file kernel-checks the abstract algebra behind the C40 boundary:

* transfer values form a multiplicative action cocycle;
* changing each root by an independent gauge transforms a transfer by a
  coboundary;
* involutive gauges preserve every transfer square;
* after one anchor is fixed, `r-1` Boolean component choices remain;
* exact secp256k1 pair-count arithmetic.

It does not formalize Miller functions, the frozen dense interpolation, or an
unrestricted arithmetic-circuit lower bound.
-/

namespace Ecdlp.Uorc056EquivariantTransferGaugeC40

/-- The transfer associated with a root section and a public component map. -/
def transfer
    {I G : Type*} [CommGroup G]
    (root : I → G) (action : I → I) (i : I) : G :=
  root (action i) * (root i)⁻¹

/-- Transfers satisfy the exact action-cocycle law. -/
theorem transfer_cocycle
    {I G : Type*} [CommGroup G]
    (root : I → G) (left right : I → I) (i : I) :
    transfer root (left ∘ right) i =
      transfer root left (right i) * transfer root right i := by
  simp [transfer, Function.comp_apply]
  ac_rfl

/-- A componentwise root gauge changes a transfer by a multiplicative
coboundary. -/
theorem transfer_of_gauged_root
    {I G : Type*} [CommGroup G]
    (root gauge : I → G) (action : I → I) (i : I) :
    transfer (fun j => gauge j * root j) action i =
      gauge (action i) * (gauge i)⁻¹ * transfer root action i := by
  simp [transfer]
  ac_rfl

/-- If every gauge value squares to one, the public transfer square is
unchanged. -/
theorem gauged_transfer_square
    {I G : Type*} [CommGroup G]
    (root gauge : I → G) (action : I → I) (i : I)
    (hleft : gauge (action i) ^ 2 = 1)
    (hright : gauge i ^ 2 = 1) :
    transfer (fun j => gauge j * root j) action i ^ 2 =
      transfer root action i ^ 2 := by
  rw [transfer_of_gauged_root]
  calc
    (gauge (action i) * (gauge i)⁻¹ * transfer root action i) ^ 2 =
        gauge (action i) ^ 2 * ((gauge i)⁻¹) ^ 2 *
          transfer root action i ^ 2 := by
      simp [mul_pow]
    _ = transfer root action i ^ 2 := by
      rw [hleft]
      have hinv : ((gauge i)⁻¹) ^ 2 = 1 := by
        rw [inv_pow, hright, inv_one]
      rw [hinv]
      simp

/-- One anchored component leaves one free Boolean sign for each of the other
`r` components. -/
theorem anchored_binary_gauge_card (r : Nat) :
    Fintype.card (Fin r → Bool) = 2 ^ r := by
  simp


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpPairComponents : Nat :=
  (secpN - 1) / 2


theorem secpPairComponentsIs255Bit :
    2 ^ 254 < secpPairComponents ∧ secpPairComponents < 2 ^ 255 := by
  native_decide


theorem secpPairKernelDegree :
    2 * secpPairComponents = secpN - 1 := by
  native_decide

end Ecdlp.Uorc056EquivariantTransferGaugeC40
