import Mathlib

namespace Ecdlp.ParityLift

/-- The difference of two additive two-torsion classes is again two-torsion. -/
theorem difference_of_twoTorsion
    {A : Type*} [AddCommGroup A]
    (first second : A)
    (hfirst : 2 • first = 0)
    (hsecond : 2 • second = 0) :
    2 • (first - second) = 0 := by
  rw [smul_sub, hfirst, hsecond, sub_zero]

/-- Product identity for the three roots of a depressed cubic. -/
theorem cubicCharacteristicNorm
    {R : Type*} [CommRing R]
    (x r₁ r₂ r₃ b : R)
    (hsum : r₁ + r₂ + r₃ = 0)
    (hpair : r₁ * r₂ + r₁ * r₃ + r₂ * r₃ = 0)
    (hprod : r₁ * r₂ * r₃ = -b) :
    (x - r₁) * (x - r₂) * (x - r₃) = x ^ 3 + b := by
  calc
    (x - r₁) * (x - r₂) * (x - r₃) =
        x ^ 3 - (r₁ + r₂ + r₃) * x ^ 2
          + (r₁ * r₂ + r₁ * r₃ + r₂ * r₃) * x
          - r₁ * r₂ * r₃ := by ring
    _ = x ^ 3 + b := by rw [hsum, hpair, hprod]; ring

/-- A normalized quotient of two square norms is itself a square quotient. -/
theorem normalizedOrbitNorm_isSquare
    {K : Type*} [Field K]
    (numerator denominator yQuery yGenerator : K)
    (hnumerator : numerator = yQuery ^ 2)
    (hdenominator : denominator = yGenerator ^ 2) :
    numerator / denominator = (yQuery / yGenerator) ^ 2 := by
  rw [hnumerator, hdenominator, div_pow]

/-- Squaring erases the distinction between opposite branches. -/
theorem oppositeBranches_sameSquare
    {R : Type*} [CommRing R]
    (value : R) :
    (-value) ^ 2 = value ^ 2 := by
  ring

/-- A generator-blind observable cannot equal targets that flip under generator negation. -/
theorem generatorBlind_cannot_select_flippedTarget
    {Generator Query Sign : Type*}
    (observable target : Generator → Query → Sign)
    (negateGenerator : Generator → Generator)
    (generator : Generator)
    (query : Query)
    (hobservable :
      observable (negateGenerator generator) query = observable generator query)
    (htarget :
      target (negateGenerator generator) query ≠ target generator query) :
    ¬ (
      observable generator query = target generator query ∧
      observable (negateGenerator generator) query =
        target (negateGenerator generator) query
    ) := by
  intro hboth
  apply htarget
  calc
    target (negateGenerator generator) query =
        observable (negateGenerator generator) query := hboth.2.symm
    _ = observable generator query := hobservable
    _ = target generator query := hboth.1

end Ecdlp.ParityLift
