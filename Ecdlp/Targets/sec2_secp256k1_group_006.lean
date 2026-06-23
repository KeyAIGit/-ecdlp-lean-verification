import Mathlib

namespace Ecdlp.Targets.Sec2Secp256k1Group006

/-- [sec2-secp256k1-group-006] SEC 2 specifies the secp256k1 base point G, its prime order n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141, and cofactor h=1. -/
theorem sec2_secp256k1_group_006 {G : Type*} [Group G] (H : Subgroup G)
    [Fintype G] [DecidablePred (· ∈ H)] :
    Fintype.card H * H.index = Fintype.card G := by
  sorry

end Ecdlp.Targets.Sec2Secp256k1Group006
