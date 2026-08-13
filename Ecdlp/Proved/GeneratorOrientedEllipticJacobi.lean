import Mathlib

/-!
# Generator-oriented elliptic Jacobi boundary

This file formalizes the elementary algebraic identities used by
`GENERATOR-ORIENTED-ELLIPTIC-JACOBI-037`.

A normalized sextic projector has an oriented cube equal to its quadratic
character component.  However, dividing that cube by a quadratic projector,
or forming a character-balanced cubic/quadratic/sextic Jacobi quotient,
cancels the generator character and produces an invariant.

The file does not formalize elliptic Gauss sums, Jacobi sums, complex
multiplication, Hecke characters, modular forms, secp256k1 nonvanishing, or
complexity.
-/

namespace Ecdlp.ParityLift

/-- Cubing the normalized sextic eigenprojector recovers the quadratic
character component. -/
theorem orientedSexticCubeRatio_recoversQuadratic
    {K : Type*} [Field K]
    (projected base psiInv quadratic : K)
    (hprojected : projected = psiInv * base)
    (hbase : base ≠ 0)
    (hcube : psiInv ^ 3 = quadratic) :
    projected ^ 3 / base ^ 3 = quadratic := by
  rw [hprojected, mul_pow, hcube]
  field_simp [hbase]

/-- Once a quadratic eigenprojector is divided out, the oriented sextic cube
becomes generator-blind. -/
theorem sexticCube_overQuadraticProjector_isInvariant
    {K : Type*} [Field K]
    (sexticProjected sexticBase quadraticProjected quadraticBase
      psiInv quadratic : K)
    (hsextic : sexticProjected = psiInv * sexticBase)
    (hquadratic : quadraticProjected = quadratic * quadraticBase)
    (hcube : psiInv ^ 3 = quadratic)
    (hquadratic_ne : quadratic ≠ 0)
    (hquadraticBase_ne : quadraticBase ≠ 0) :
    sexticProjected ^ 3 / quadraticProjected =
      sexticBase ^ 3 / quadraticBase := by
  rw [hsextic, hquadratic, mul_pow, hcube]
  field_simp [hquadratic_ne, hquadraticBase_ne]

/-- A product whose total character is trivial is a generator-blind Jacobi
ratio. -/
theorem balancedMixedJacobiRatio_isInvariant
    {K : Type*} [Field K]
    (cubicProjected cubicBase quadraticProjected quadraticBase
      sexticProjected sexticBase cubicInv quadraticInv psiInv : K)
    (hcubic : cubicProjected = cubicInv * cubicBase)
    (hquadratic : quadraticProjected = quadraticInv * quadraticBase)
    (hsextic : sexticProjected = psiInv * sexticBase)
    (hfactor : psiInv = cubicInv * quadraticInv)
    (hcubicInv_ne : cubicInv ≠ 0)
    (hquadraticInv_ne : quadraticInv ≠ 0)
    (hsexticBase_ne : sexticBase ≠ 0) :
    cubicProjected * quadraticProjected / sexticProjected =
      cubicBase * quadraticBase / sexticBase := by
  rw [hcubic, hquadratic, hsextic, hfactor]
  field_simp [hcubicInv_ne, hquadraticInv_ne, hsexticBase_ne]

/-- Opposite quadratic orientations have the same invariant square. -/
theorem orientedCube_opposite_sameSquare
    {K : Type*} [Ring K]
    (orientedCube : K) :
    (-orientedCube) ^ 2 = orientedCube ^ 2 := by
  noncomm_ring

end Ecdlp.ParityLift
