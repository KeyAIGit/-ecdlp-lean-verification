import Mathlib
import Ecdlp.Proved.GeneratorOrientationBlindness

/-!
# Uniform oriented-root circuit boundary

This file formalizes three narrow facts for
`UNIFORM-ORIENTED-ROOT-CIRCUIT-056`, track C.

1. In the ordinary binary arithmetic-gate model, a rational-degree envelope
   can at most double at one new gate. Therefore `s` gates imply only the
   upper bound `degree <= 2^s` and a degree-only lower bound is logarithmic.
2. Repeated squaring attains exponential degree with a uniform one-register
   straight-line program of exactly `s` instructions.
3. Explicit representation cost and marked-generator sensitivity cannot be
   omitted from the evaluator audit.

The file does not construct `Y_G`, a parity evaluator, an EDS-residue oracle,
or a sub-square-root ECDLP algorithm. It also does not claim a lower bound for
all arithmetic circuits computing the specific secp256k1 oriented root.
-/

namespace Ecdlp.ParityLift

/-- The five charged components required by the research target. -/
structure ChargedCircuitCost where
  preprocessing : ℕ
  advice : ℕ
  memory : ℕ
  representation : ℕ
  online : ℕ
  deriving DecidableEq, Repr

namespace ChargedCircuitCost

/-- No cost component is hidden when the total is formed. -/
def total (cost : ChargedCircuitCost) : ℕ :=
  cost.preprocessing + cost.advice + cost.memory +
    cost.representation + cost.online

/-- Explicit representation cost is bounded by the charged total. -/
theorem representation_le_total (cost : ChargedCircuitCost) :
    cost.representation ≤ cost.total := by
  unfold total
  omega

/-- Online cost is bounded by the charged total. -/
theorem online_le_total (cost : ChargedCircuitCost) :
    cost.online ≤ cost.total := by
  unfold total
  omega

end ChargedCircuitCost

/-- If an explicit object has at least `items` represented entries, a claimed
budget strictly below `items` is incompatible with the full charged ledger. -/
theorem explicitMaterialization_exceedsBudget
    (cost : ChargedCircuitCost)
    (items budget : ℕ)
    (hitems : items ≤ cost.representation)
    (hbudget : cost.total ≤ budget)
    (hsmall : budget < items) :
    False := by
  have hrepr : cost.representation ≤ cost.total :=
    ChargedCircuitCost.representation_le_total cost
  omega

/-- A binary arithmetic gate whose output rational-degree cap is bounded by the
sum of its input caps can at most double the current maximum cap. This covers
addition, subtraction, multiplication, and division after numerator and
denominator degrees are tracked together. -/
theorem binaryArithmeticGate_degreeCap
    (left right currentMax output : ℕ)
    (hleft : left ≤ currentMax)
    (hright : right ≤ currentMax)
    (houtput : output ≤ left + right) :
    output ≤ 2 * currentMax := by
  omega

/-- Starting from degree at most one, a straight-line program whose degree
maximum can at most double at each gate has degree at most `2^gates` after
`gates` instructions. -/
theorem arithmeticCircuit_degreeEnvelope
    (maxDegree : ℕ → ℕ)
    (hzero : maxDegree 0 ≤ 1)
    (hstep : ∀ gates, maxDegree (Nat.succ gates) ≤ 2 * maxDegree gates) :
    ∀ gates, maxDegree gates ≤ 2 ^ gates := by
  intro gates
  induction gates with
  | zero =>
      simpa using hzero
  | succ gates ih =>
      calc
        maxDegree (Nat.succ gates) ≤ 2 * maxDegree gates := hstep gates
        _ ≤ 2 * (2 ^ gates) := Nat.mul_le_mul_left 2 ih
        _ = 2 ^ Nat.succ gates := by
          simp [pow_succ, Nat.mul_comm]

/-- The one instruction needed for the exact high-degree witness. -/
inductive SquareInstruction where
  | square
  deriving DecidableEq, Repr

/-- A uniform one-register straight-line program consisting of `steps`
repeated squarings. -/
def squareProgram : ℕ → List SquareInstruction
  | 0 => []
  | Nat.succ steps => .square :: squareProgram steps

/-- Replay only the formal input degree. One square doubles it. -/
def runDegree : List SquareInstruction → ℕ → ℕ
  | [], degree => degree
  | .square :: program, degree => runDegree program (degree + degree)

@[simp]
theorem squareProgram_length (steps : ℕ) :
    (squareProgram steps).length = steps := by
  induction steps with
  | zero => simp [squareProgram]
  | succ steps ih => simp [squareProgram, ih]

/-- Repeated squaring multiplies the input degree by `2^steps`. -/
theorem runDegree_squareProgram (steps degree : ℕ) :
    runDegree (squareProgram steps) degree = degree * 2 ^ steps := by
  induction steps generalizing degree with
  | zero => simp [squareProgram, runDegree]
  | succ steps ih =>
      simp [squareProgram, runDegree, ih, pow_succ]
      ring

/-- Exact tight witness: `steps` uniform instructions reach degree `2^steps`.
Thus high degree by itself cannot imply a linear-size circuit lower bound. -/
theorem squareProgram_exponentialDegree (steps : ℕ) :
    runDegree (squareProgram steps) 1 = 2 ^ steps := by
  simpa using runDegree_squareProgram steps 1

/-- The short high-degree witness includes both its exact program length and
its exact output degree. -/
theorem exists_uniformProgram_with_exponentialDegree (steps : ℕ) :
    ∃ program : List SquareInstruction,
      program.length = steps ∧ runDegree program 1 = 2 ^ steps := by
  exact ⟨squareProgram steps, squareProgram_length steps,
    squareProgram_exponentialDegree steps⟩

/-- If compiling the marked generator and its negative gives the same circuit
code, that compiler cannot compute a target which flips under `G -> -G` for
both markings. -/
theorem generatorBlindCompiler_cannot_computeComplementaryTarget
    {Γ Code : Type*} [Neg Γ]
    (compile : Γ → Code)
    (run : Code → Γ → Bool)
    (target : Γ → Γ → Bool)
    (G Q : Γ)
    (hcompile : compile G = compile (-G))
    (hflip : target (-G) Q = !(target G Q))
    (hcorrectG : run (compile G) Q = target G Q)
    (hcorrectNeg : run (compile (-G)) Q = target (-G) Q) :
    False := by
  apply generatorBlind_cannot_decode_complementaryTargets
    (fun generator query => run (compile generator) query)
    target G Q
  · rw [hcompile]
  · exact hflip
  · exact hcorrectG
  · exact hcorrectNeg

/-- Equivalent positive requirement: correctness for both generator markings
forces the compiled circuit code to distinguish them. -/
theorem correctCompiler_forcesGeneratorSensitiveCode
    {Γ Code : Type*} [Neg Γ]
    (compile : Γ → Code)
    (run : Code → Γ → Bool)
    (target : Γ → Γ → Bool)
    (G Q : Γ)
    (hflip : target (-G) Q = !(target G Q))
    (hcorrectG : run (compile G) Q = target G Q)
    (hcorrectNeg : run (compile (-G)) Q = target (-G) Q) :
    compile G ≠ compile (-G) := by
  intro hcompile
  exact generatorBlindCompiler_cannot_computeComplementaryTarget
    compile run target G Q hcompile hflip hcorrectG hcorrectNeg

end Ecdlp.ParityLift
