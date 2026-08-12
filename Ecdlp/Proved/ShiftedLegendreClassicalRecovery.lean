import Mathlib

/-!
# Shifted Legendre classical recovery gate

This file formalizes elementary algebraic identities used by
`SHIFTED-LEGENDRE-CLASSICAL-RECOVERY-041`.

Every affine scalar query factors into a public multiplier and a shifted query.
An injective fingerprint determines the hidden shift, and a correlation function
with one distinguished peak identifies it uniquely.

The file does not formalize finite-field quadratic characters, exact Legendre
autocorrelation, random fingerprint probabilities, FFT complexity, classical
query lower bounds, quantum algorithms, or secp256k1 ECDLP.
-/

namespace Ecdlp.ParityLift

/-- Every nonzero affine query has shifted normal form
`t*k+a = t*(k+a/t)`. -/
theorem affineQuery_factorization
    {K : Type*} [Field K]
    (t k a : K)
    (ht : t ≠ 0) :
    t * k + a = t * (k + a / t) := by
  field_simp [ht]
  ring

/-- Once multiplicativity has supplied the public scale factor, an affine
character query is exactly a scaled shifted query. -/
theorem affineCharacter_reducesToShift
    {K : Type*} [CommRing K]
    (affineCharacter scaleCharacter shiftedCharacter : K)
    (hfactor : affineCharacter = scaleCharacter * shiftedCharacter) :
    affineCharacter = scaleCharacter * shiftedCharacter := by
  exact hfactor

/-- An injective signature table recovers the hidden shift from an equal
signature. -/
theorem injectiveFingerprint_recoversShift
    {α β : Type*}
    (signature : α → β)
    (hinjective : Function.Injective signature)
    (hidden candidate : α)
    (hequal : signature candidate = signature hidden) :
    candidate = hidden := by
  exact hinjective hequal

/-- If a correlation has one peak value and every other point has a distinct
off-peak value, the peak determines the hidden shift uniquely. -/
theorem uniqueCorrelationPeak
    {α : Type*}
    (correlation : α → ℤ)
    (hidden : α)
    (peak offPeak : ℤ)
    (hpeak : correlation hidden = peak)
    (hoff : ∀ candidate, candidate ≠ hidden → correlation candidate = offPeak)
    (hne : peak ≠ offPeak) :
    ∀ candidate, correlation candidate = peak → candidate = hidden := by
  intro candidate hcandidate
  by_contra hnot
  have hoffValue : correlation candidate = offPeak := hoff candidate hnot
  have : peak = offPeak := by rw [← hcandidate, hoffValue]
  exact hne this

end Ecdlp.ParityLift
