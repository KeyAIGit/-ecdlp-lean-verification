import Mathlib
import Ecdlp.Proved.Secp13441CharacterBoundary

/-!
# Full order-13441 phase decimation boundary

This file records the exact query identity behind
`SECP-13441-PHASE-SPECTRUM-023`.

For a public point function `Phi`, a base point `G`, and `Q=[k]G`, querying the
same phase on `[t]Q` evaluates the known scalar-domain signal at `t*k`.  Thus the
hidden multiplier acts by multiplicative decimation.  The experiment studies
whether this full complex-valued signal has additive Fourier coefficients large
enough for a local sparse-Fourier reduction.

Lean proves the decimation and composition identities, plus coprimality of the
small deterministic phase powers used by the frozen screen.  It does not
formalize discrete Fourier transforms or the numerical spectral gate.
-/

namespace Ecdlp.ParityLift

/-- Multiplicative decimation of a signal on a commutative scalar monoid. -/
def multiplicativelyDecimated
    {S K : Type*} [CommMonoid S]
    (signal : S → K) (hidden : S) : S → K :=
  fun query => signal (query * hidden)

@[simp]
theorem multiplicativelyDecimated_apply
    {S K : Type*} [CommMonoid S]
    (signal : S → K) (hidden query : S) :
    multiplicativelyDecimated signal hidden query =
      signal (query * hidden) :=
  rfl

/-- Two hidden multiplicative decimations compose by multiplying their hidden
scalars. -/
theorem multiplicativelyDecimated_comp
    {S K : Type*} [CommMonoid S]
    (signal : S → K) (first second : S) :
    multiplicativelyDecimated
        (multiplicativelyDecimated signal first) second =
      multiplicativelyDecimated signal (first * second) := by
  funext query
  simp [multiplicativelyDecimated, mul_assoc, mul_comm, mul_left_comm]

/-- Evaluating any public point function on a chosen multiple of `Q=[k]G` is
exactly scalar-domain decimation. -/
theorem pointFunction_query_decimation
    {A K : Type*} [AddCommMonoid A]
    (pointFunction : A → K)
    (G : A) (hidden query : ℕ) :
    pointFunction (query • (hidden • G)) =
      pointFunction ((query * hidden) • G) := by
  rw [smul_smul]

/-- Applying a fixed public phase power preserves the same hidden decimation. -/
theorem poweredPointFunction_query_decimation
    {A K : Type*} [AddCommMonoid A] [Monoid K]
    (pointFunction : A → K)
    (G : A) (hidden query power : ℕ) :
    (pointFunction (query • (hidden • G))) ^ power =
      (pointFunction ((query * hidden) • G)) ^ power := by
  rw [smul_smul]

/-- Every deterministic phase power used in the frozen experiment is coprime
to the prime phase order `13441`. -/
theorem testedSecp13441PhasePowers_coprime :
    Nat.Coprime 1 secp13441CharacterOrder ∧
    Nat.Coprime 2 secp13441CharacterOrder ∧
    Nat.Coprime 3 secp13441CharacterOrder ∧
    Nat.Coprime 5 secp13441CharacterOrder ∧
    Nat.Coprime 7 secp13441CharacterOrder ∧
    Nat.Coprime 11 secp13441CharacterOrder ∧
    Nat.Coprime 13 secp13441CharacterOrder ∧
    Nat.Coprime 17 secp13441CharacterOrder := by
  native_decide

end Ecdlp.ParityLift
