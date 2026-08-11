import Ecdlp.Proved.M16FactorBaseLiftableDefs

/-! Isolated native certificate for the M16 generator order and GLV powers. -/

namespace Ecdlp.M16FactorBaseLiftable.Certificates

theorem factorBaseGenerator_certificate :
    factorBaseGenerator ^ 564522 = 1 ∧
    factorBaseGenerator ^ 282261 ≠ 1 ∧
    factorBaseGenerator ^ 188174 ≠ 1 ∧
    factorBaseGenerator ^ 80646 ≠ 1 ∧
    factorBaseGenerator ^ 42 ≠ 1 ∧
    factorBaseGenerator ^ 188174 = (Secp256k1.beta : Fp) ^ 2 ∧
    factorBaseGenerator ^ 376348 = (Secp256k1.beta : Fp) := by
  native_decide

end Ecdlp.M16FactorBaseLiftable.Certificates
