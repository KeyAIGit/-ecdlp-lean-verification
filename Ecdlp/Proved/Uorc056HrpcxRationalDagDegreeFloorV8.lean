import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# UORC-056 V8: exact secp256k1 arithmetic endpoint

The function-field and rational-DAG degree estimates are stated in the accompanying
mathematical note.  This file kernel-checks the exact final numerical threshold:
253 binary degree-doubling gates are insufficient, while 254 reach the necessary
pole-degree scale.
-/

namespace Ecdlp.Proved.Uorc056HrpcxRationalDagDegreeFloorV8

/-- The exact pole-degree target supplied by the divisor argument. -/
def targetPoleDegree : Nat := (Secp256k1.n - 1) / 2

/-- A DAG starting from maximum pole degree three cannot reach the target with
only 253 binary gates, even under the maximally permissive doubling ledger. -/
theorem gate253_insufficient :
    3 * 2 ^ 253 < targetPoleDegree := by
  native_decide

/-- The coarse degree ledger reaches the target scale at 254 gates.  This is not
an existence theorem for a decoder; it only proves that 254 is the first integer
not excluded by this degree count. -/
theorem gate254_reaches_degree_scale :
    targetPoleDegree ≤ 3 * 2 ^ 254 := by
  native_decide

/-- The exact minimum integer in the coarse secp256k1 degree ledger is 254. -/
theorem exact_gate_floor :
    (3 * 2 ^ 253 < targetPoleDegree) ∧
    (targetPoleDegree ≤ 3 * 2 ^ 254) := by
  exact ⟨gate253_insufficient, gate254_reaches_degree_scale⟩

end Ecdlp.Proved.Uorc056HrpcxRationalDagDegreeFloorV8
