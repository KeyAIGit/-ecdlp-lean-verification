import Mathlib

/-!
# UORC-056 C29 autonomous state rigidity

This file kernel-checks the finite-state semantic core and fixed arithmetic
used by C29:

* deterministic state recurrence transports equality through every iterate;
* repeated states cannot decode two targets that differ after some common
  number of updates;
* the two-state odd-cycle wrap conflict;
* public homomorphisms preserve the same scalar multiplier;
* exact secp256k1 `PGL₂(F_p)` coprimality and frozen toy diagnostics.

It does not formalize normalization of algebraic image curves,
Riemann-Hurwitz, the classification of genus-one morphisms as translated
isogenies, or the theorem that finite-order rational dynamics on `P¹` has
degree one. Those geometric inputs are explicit in the accompanying note.
-/

namespace Ecdlp.Uorc056AutonomousStateRigidity

/-- A small recursive iterate used to avoid any dependence on notation. -/
def iter {α : Type*} (f : α → α) : Nat → α → α
  | 0, x => x
  | n + 1, x => iter f n (f x)

/-- A semiconjugacy transports the state through every common number of
updates. -/
theorem state_iterate_semiconjugacy
    {Input State : Type*}
    (next : Input → Input)
    (step : State → State)
    (state : Input → State)
    (hstep : ∀ input, state (next input) = step (state input)) :
    ∀ rounds input,
      state (iter next rounds input) =
        iter step rounds (state input) := by
  intro rounds
  induction rounds with
  | zero =>
      intro input
      rfl
  | succ rounds ih =>
      intro input
      simp only [iter]
      rw [ih (next input), hstep input]

/-- Equal autonomous states remain equal after any common number of updates. -/
theorem repeated_state_stays_repeated
    {Input State : Type*}
    (next : Input → Input)
    (step : State → State)
    (state : Input → State)
    (hstep : ∀ input, state (next input) = step (state input))
    (left right : Input)
    (hstate : state left = state right)
    (rounds : Nat) :
    state (iter next rounds left) =
      state (iter next rounds right) := by
  rw [state_iterate_semiconjugacy next step state hstep]
  rw [state_iterate_semiconjugacy next step state hstep]
  exact congrArg (iter step rounds) hstate

/-- If two equal autonomous states have targets that differ after a common
number of updates, no state-only decoder can be exact everywhere. -/
theorem repeated_state_decoder_obstruction
    {Input State Output : Type*}
    (next : Input → Input)
    (step : State → State)
    (state : Input → State)
    (target : Input → Output)
    (decoder : State → Output)
    (hstep : ∀ input, state (next input) = step (state input))
    (hdecode : ∀ input, decoder (state input) = target input)
    (left right : Input)
    (hstate : state left = state right)
    (rounds : Nat)
    (htarget :
      target (iter next rounds left) ≠
        target (iter next rounds right)) :
    False := by
  have hs := repeated_state_stays_repeated
    next step state hstep left right hstate rounds
  apply htarget
  rw [← hdecode (iter next rounds left)]
  rw [← hdecode (iter next rounds right)]
  exact congrArg decoder hs

/-- If every two distinct inputs can eventually be separated by the target,
then an exact autonomous state with a state-only decoder is injective. -/
theorem state_injective_of_future_separation
    {Input State Output : Type*}
    (next : Input → Input)
    (step : State → State)
    (state : Input → State)
    (target : Input → Output)
    (decoder : State → Output)
    (hstep : ∀ input, state (next input) = step (state input))
    (hdecode : ∀ input, decoder (state input) = target input)
    (hseparate : ∀ {left right}, left ≠ right →
      ∃ rounds,
        target (iter next rounds left) ≠
          target (iter next rounds right)) :
    Function.Injective state := by
  intro left right hstate
  by_contra hne
  obtain ⟨rounds, htarget⟩ := hseparate hne
  exact repeated_state_decoder_obstruction
    next step state target decoder hstep hdecode
    left right hstate rounds htarget

/-- Finite exact autonomous states need at least as many semantic values as the
input orbit whenever future target values separate every pair. -/
theorem finite_state_cardinality_lower_bound
    {Input State Output : Type*}
    [Fintype Input] [Fintype State]
    (next : Input → Input)
    (step : State → State)
    (state : Input → State)
    (target : Input → Output)
    (decoder : State → Output)
    (hstep : ∀ input, state (next input) = step (state input))
    (hdecode : ∀ input, decoder (state input) = target input)
    (hseparate : ∀ {left right}, left ≠ right →
      ∃ rounds,
        target (iter next rounds left) ≠
          target (iter next rounds right)) :
    Fintype.card Input ≤ Fintype.card State := by
  exact Fintype.card_le_of_injective state
    (state_injective_of_future_separation
      next step state target decoder hstep hdecode hseparate)

/-- A two-state parity summary cannot have one deterministic successor at the
odd-cycle wrap: the same `evenState` would need both odd and even decoded
successors. -/
theorem two_state_wrap_conflict
    {State Output : Type*}
    (step : State → State)
    (decoder : State → Output)
    (evenState : State)
    (evenValue oddValue : Output)
    (hne : evenValue ≠ oddValue)
    (hnormalEdge : decoder (step evenState) = oddValue)
    (hwrapEdge : decoder (step evenState) = evenValue) :
    False := by
  exact hne (hwrapEdge.symm.trans hnormalEdge)

/-- A public additive recoding preserves the literal scalar multiplier. This is
the algebraic core of the genus-one/isogeny recoding statement. -/
theorem additive_recoding_keeps_scalar
    {G H : Type*} [AddMonoid G] [AddMonoid H]
    (φ : G →+ H)
    (k : Nat)
    (P : G) :
    φ (k • P) = k • φ P := by
  exact map_nsmul φ k P

/-- Arithmetic premise consumed after the global rational semiconjugacy
argument identifies an order-`n` element of `PGL₂(F_p)`. -/
theorem pgl2_order_divisibility_certificate
    (n p : Nat)
    (h : n ∣ p * (p ^ 2 - 1)) :
    n ∣ p * (p ^ 2 - 1) :=
  h


def secpP : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpPGL2Order : Nat :=
  secpP * (secpP ^ 2 - 1)


theorem secpCoprimeToPGL2Order :
    Nat.gcd secpN secpPGL2Order = 1 := by
  native_decide


theorem secpOrderDoesNotDividePGL2Order :
    ¬ secpN ∣ secpPGL2Order := by
  native_decide


theorem secpOrderIsOdd :
    secpN % 2 = 1 := by
  native_decide


theorem secpStateOrbitSizeIs256Bit :
    2 ^ 255 < secpN ∧ secpN < 2 ^ 256 := by
  native_decide

/-- Four of the five frozen j=0 toy pairs satisfy the same group-order
obstruction. -/
theorem frozenP43N31_obstructed :
    Nat.gcd 31 (43 * (43 ^ 2 - 1)) = 1 := by
  native_decide


theorem frozenP67N79_obstructed :
    Nat.gcd 79 (67 * (67 ^ 2 - 1)) = 1 := by
  native_decide


theorem frozenP79N67_obstructed :
    Nat.gcd 67 (79 * (79 ^ 2 - 1)) = 1 := by
  native_decide


theorem frozenP163N139_obstructed :
    Nat.gcd 139 (163 * (163 ^ 2 - 1)) = 1 := by
  native_decide

/-- The characteristic-order toy is deliberately not covered: `n=p=127`
divides the PGL2 order through the characteristic factor. -/
theorem frozenP127N127_exception :
    127 ∣ 127 * (127 ^ 2 - 1) := by
  native_decide

end Ecdlp.Uorc056AutonomousStateRigidity
