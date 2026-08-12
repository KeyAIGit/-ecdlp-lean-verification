import Mathlib
import Ecdlp.Secp256k1Verified
import Ecdlp.Proved.GlobalMonodromyBoundary
import Ecdlp.Proved.GlobalMonodromyCarry

/-!
# Arithmetic boundary for sesquilinear CM pairings

This file records the fixed secp256k1 subgroup arithmetic used by
`SESQUILINEAR-CM-PAIRING-011`.

Let `ω` be the order-three CM automorphism and let `λ` be its scalar action on
the secp256k1 prime-order subgroup. The order-dependent CM element

`α = λ - ω`

annihilates that subgroup, while its conjugate `bar α = λ - ω²` acts there by
the nonzero scalar `λ-λ²=2λ+1`. Hence the rational subgroup lies in only one
of the two conjugate kernel directions required by the sesquilinear Weil/Tate
pairings.

Lean proves only the finite scalar arithmetic and the resulting surjectivity of
the conjugate action on the scalar line. It does not formalize CM elliptic
curves, sesquilinear pairings, or their source-level domain identifications.
-/

namespace Ecdlp.ParityLift

/-- Scalar by which the conjugate CM annihilator `λ-ω²` acts on the chosen
prime-order subgroup. -/
def secp256k1ConjugateCmAction : ZMod Secp256k1.n :=
  (2 * Secp256k1.lambda + 1 : ℕ)

/-- Explicit inverse of the conjugate action scalar. -/
def secp256k1ConjugateCmActionInv : ZMod Secp256k1.n :=
  52049339249440132347096509016808591601273271149061544929325695065753442342879

/-- The CM eigenvalue satisfies the fixed order-three relation. -/
theorem secp256k1_lambda_orderThree_relation :
    (Secp256k1.lambda : ZMod Secp256k1.n) ^ 2
      + Secp256k1.lambda + 1 = 0 := by
  native_decide

/-- On the subgroup, `λ-λ²` equals `2λ+1`. -/
theorem secp256k1_conjugateCmAction_formula :
    (Secp256k1.lambda : ZMod Secp256k1.n)
        - (Secp256k1.lambda : ZMod Secp256k1.n) ^ 2
      = secp256k1ConjugateCmAction := by
  native_decide

/-- The conjugate action is a unit on the rational prime-order line. -/
theorem secp256k1_conjugateCmAction_mul_inv :
    secp256k1ConjugateCmAction * secp256k1ConjugateCmActionInv = 1 := by
  native_decide

/-- Every scalar on the rational line is in the image of the conjugate CM
action. Thus its class in the corresponding quotient is zero. -/
theorem secp256k1_conjugateCmAction_surjective
    (k : ZMod Secp256k1.n) :
    secp256k1ConjugateCmAction
        * (secp256k1ConjugateCmActionInv * k) = k := by
  rw [← mul_assoc, secp256k1_conjugateCmAction_mul_inv, one_mul]

/-- Norm of the CM annihilator `λ-ω`. -/
def secp256k1CmAnnihilatorNorm : ℕ :=
  Secp256k1.lambda ^ 2 + Secp256k1.lambda + 1

/-- The CM annihilator norm is divisible by the subgroup order. -/
theorem secp256k1_order_dvd_cmAnnihilatorNorm :
    Secp256k1.n ∣ secp256k1CmAnnihilatorNorm := by
  native_decide

/-- The quotient of the annihilator norm by the subgroup order is itself a
253-bit integer. -/
def secp256k1CmAnnihilatorNormCofactor : ℕ :=
  secp256k1CmAnnihilatorNorm / Secp256k1.n

/-- Frozen exact cofactor used by the independent arithmetic replay. -/
theorem secp256k1_cmAnnihilatorNormCofactor_value :
    secp256k1CmAnnihilatorNormCofactor =
      12286276166636580012140862095472453253950970278553425451194017527274075467639 := by
  native_decide

/-- The conjugate kernel direction contains no nonzero scalar from the chosen
prime-order line. -/
theorem secp256k1_conjugateCmKernel_trivial
    (k : ZMod Secp256k1.n)
    (h : secp256k1ConjugateCmAction * k = 0) :
    k = 0 := by
  calc
    k = secp256k1ConjugateCmActionInv
        * (secp256k1ConjugateCmAction * k) := by
          rw [← mul_assoc]
          have hinv : secp256k1ConjugateCmActionInv
              * secp256k1ConjugateCmAction = 1 := by
            rw [mul_comm]
            exact secp256k1_conjugateCmAction_mul_inv
          rw [hinv, one_mul]
    _ = 0 := by rw [h, mul_zero]

end Ecdlp.ParityLift
