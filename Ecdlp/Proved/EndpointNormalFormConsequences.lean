import Ecdlp.Proved.EndpointCocycleNormalForm
import Ecdlp.Proved.ConjugatedProductNormalForm

namespace Ecdlp.EndpointNormalForm

section Additive

open Ecdlp.EndpointSegment

variable {A : Type*} [AddCommGroup A]

/-- A map that sees only the two endpoint potential values and works uniformly
for every potential and every segment length forces the constant defect to
vanish. -/
theorem endpointOnly_map_forces_zero_defect
    (defect : A)
    (endpointMap : A → A → A)
    (hmap :
      ∀ (potential : ℕ → A) (start length : ℕ),
        endpointMap (potential start) (potential (start + length))
          = segmentSum defect potential start length) :
    defect = 0 := by
  let potential : ℕ → A := fun _ => 0
  have hzero := hmap potential 0 0
  have hone := hmap potential 0 1
  simp [segmentSum, edgeCocycle, potential] at hzero hone
  exact hone.symm.trans hzero

/-- Therefore no uniform endpoint-only map exists for a nonzero defect in the
declared additive grammar. -/
theorem no_endpointOnly_map_of_nonzero_defect
    (defect : A) (hdefect : defect ≠ 0) :
    ¬ ∃ endpointMap : A → A → A,
      ∀ (potential : ℕ → A) (start length : ℕ),
        endpointMap (potential start) (potential (start + length))
          = segmentSum defect potential start length := by
  rintro ⟨endpointMap, hmap⟩
  exact hdefect
    (endpointOnly_map_forces_zero_defect defect endpointMap hmap)

/-- With binary coefficients and unit defect, the normalized endpoint residual
is exactly the segment length reduced modulo two. -/
theorem binary_endpointResidual_eq_length
    (potential : ℕ → ZMod 2) (start length : ℕ) :
    endpointResidual (1 : ZMod 2) potential start length
      = (length : ZMod 2) := by
  simp [endpointResidual_eq_length_smul]

end Additive

section Multiplicative

open Ecdlp.ConjugatedProduct

variable {M : Type*} [Group M]

/-- A map that sees only the two endpoint basis values and works uniformly for
every basis and length forces the constant transition to be the identity. -/
theorem endpointOnly_product_map_forces_identity
    (constant : M)
    (endpointMap : M → M → M)
    (hmap :
      ∀ (basis : ℕ → M) (start length : ℕ),
        endpointMap (basis start) (basis (start + length))
          = productFrom constant basis start length) :
    constant = 1 := by
  let basis : ℕ → M := fun _ => 1
  have hzero := hmap basis 0 0
  have hone := hmap basis 0 1
  simp [productFrom, step, basis] at hzero hone
  exact hone.symm.trans hzero

/-- Therefore no uniform endpoint-only product map exists for a nonidentity
constant transition in the declared conjugated-product grammar. -/
theorem no_endpointOnly_product_map_of_nonidentity
    (constant : M) (hconstant : constant ≠ 1) :
    ¬ ∃ endpointMap : M → M → M,
      ∀ (basis : ℕ → M) (start length : ℕ),
        endpointMap (basis start) (basis (start + length))
          = productFrom constant basis start length := by
  rintro ⟨endpointMap, hmap⟩
  exact hconstant
    (endpointOnly_product_map_forces_identity constant endpointMap hmap)

end Multiplicative

end Ecdlp.EndpointNormalForm
