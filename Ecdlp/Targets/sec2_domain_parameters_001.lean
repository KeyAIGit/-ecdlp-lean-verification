import Mathlib

namespace Ecdlp.Targets.Sec2DomainParameters001

/-- [sec2-domain-parameters-001] Elliptic-curve domain parameters over Fp are specified as T=(p,a,b,G,n,h), where p defines Fp, a and b define the curve, G is a base point, n is the … -/
theorem sec2_domain_parameters_001 {G : Type*} [Group G] (H : Subgroup G)
    [Fintype G] [DecidablePred (· ∈ H)] :
    Fintype.card H * H.index = Fintype.card G := by
  sorry

end Ecdlp.Targets.Sec2DomainParameters001
