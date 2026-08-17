import Ecdlp.Proved.GlvNormalizationRigidity

/-!
# Residual-weight scope for GLV normalization rigidity

The geometric scope contract assigns a homogeneous section two binary pieces
of bookkeeping:

* `epsilon`: the exponent of the genuinely nonpublic residual EDS character
  after multiplication-law and public-normalization cancellations;
* `a+b`: the binary weight of its quadratic normalization exponent
  `a*k^2+b*k+c`.

The admitted algebraic category is characterized by their parity agreement.
This file formalizes the exact no-go consequence of that compatibility. It does
not formalize line bundles or prove that an arbitrary external construction is
admitted to the category.
-/

namespace Ecdlp.ParityLift

/-- A scoped homogeneous section is compatible when its residual EDS exponent
and its quadratic normalization weight have the same parity. -/
def residualWeightCompatible (epsilon a b : ℤ) : Prop :=
  Even (epsilon - (a + b))

/-- Compatibility plus odd residual EDS weight forces odd quadratic weight. -/
theorem compatibleOddResidual_forcesOddNormalization
    (epsilon a b : ℤ)
    (hcompat : residualWeightCompatible epsilon a b)
    (hodd : Even (epsilon - 1)) :
    Even ((a + b) - 1) := by
  rcases hcompat with ⟨r, hr⟩
  rcases hodd with ⟨s, hs⟩
  refine ⟨s - r, ?_⟩
  calc
    (a + b) - 1 = (epsilon - 1) - (epsilon - (a + b)) := by ring
    _ = (s - r) + (s - r) := by
      rw [hs, hr]
      ring

/-- **Scoped no-go.** A compatible section with an odd residual EDS factor has
the basic GLV carry multiplier, up to its fixed section constant. -/
theorem compatibleOddResidual_forcesBasicCarry
    (epsilon a b gamma c : ℤ)
    (hcompat : residualWeightCompatible epsilon a b)
    (hodd : Even (epsilon - 1)) :
    Even (((a + b) * gamma + c) - (gamma + c)) := by
  exact oddCarryWeight_forces_basicCarry
    (a + b) gamma c
    (compatibleOddResidual_forcesOddNormalization epsilon a b hcompat hodd)

/-- Conversely, a compatible section whose quadratic normalization is
carry-free has even residual EDS weight. It cannot contain a surviving odd
number of nonpublic residue factors. -/
theorem compatibleCarryFree_forcesEvenResidual
    (epsilon a b : ℤ)
    (hcompat : residualWeightCompatible epsilon a b)
    (hfree : Even (a + b)) :
    Even epsilon := by
  rcases hcompat with ⟨r, hr⟩
  rcases hfree with ⟨s, hs⟩
  refine ⟨r + s, ?_⟩
  calc
    epsilon = (epsilon - (a + b)) + (a + b) := by ring
    _ = (r + s) + (r + s) := by
      rw [hr, hs]
      ring

end Ecdlp.ParityLift
