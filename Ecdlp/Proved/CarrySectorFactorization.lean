import Mathlib

/-!
# UORC-056 carry/sector factorization algebra

This file kernel-checks the denominator-free algebra used by V15 after the
three canonical parity signs on a C3/GLV orbit have been isolated.

It does not formalize elliptic curves, the oriented-root interpolation,
the GLV endomorphism, or a public decoder.  Those instance-level statements
remain executable finite-field replay obligations.
-/

namespace Ecdlp.CarrySectorFactorization

variable {R : Type*} [CommRing R]

/-- If `s1` and `s2` are signs, the C3 orbit product times the complementary
pairwise sign recovers `s0`. -/
theorem carry_mul_sector
    (s0 s1 s2 : R)
    (h1 : s1 ^ 2 = 1)
    (h2 : s2 ^ 2 = 1) :
    (s0 * s1 * s2) * (s1 * s2) = s0 := by
  calc
    (s0 * s1 * s2) * (s1 * s2)
        = s0 * (s1 ^ 2) * (s2 ^ 2) := by ring
    _ = s0 := by rw [h1, h2]; ring

/-- The three complementary pairwise signs form a Klein-four state. -/
theorem sector_klein_product
    (s0 s1 s2 : R)
    (h0 : s0 ^ 2 = 1)
    (h1 : s1 ^ 2 = 1)
    (h2 : s2 ^ 2 = 1) :
    (s1 * s2) * (s2 * s0) * (s0 * s1) = 1 := by
  calc
    (s1 * s2) * (s2 * s0) * (s0 * s1)
        = (s0 ^ 2) * (s1 ^ 2) * (s2 ^ 2) := by ring
    _ = 1 := by rw [h0, h1, h2]; ring

/-- Simultaneous negation flips the three-sign carry. -/
theorem carry_negation
    (s0 s1 s2 : R) :
    (-s0) * (-s1) * (-s2) = -(s0 * s1 * s2) := by
  ring

/-- Simultaneous negation preserves each complementary sector bit. -/
theorem sector_negation
    (s1 s2 : R) :
    (-s1) * (-s2) = s1 * s2 := by
  ring

/-- Denominator-free square identity behind
`J = Y(alpha Q) Y(alpha^2 Q) / F(Q)`. -/
theorem kummer_sector_square
    (Y1 Y2 F : R)
    (h1 : Y1 ^ 2 = F)
    (h2 : Y2 ^ 2 = F) :
    (Y1 * Y2) ^ 2 = F ^ 2 := by
  calc
    (Y1 * Y2) ^ 2 = (Y1 ^ 2) * (Y2 ^ 2) := by ring
    _ = F ^ 2 := by rw [h1, h2]

/-- The three cyclic Kummer-sector numerators multiply to `F^3`. -/
theorem kummer_sector_orbit_product
    (Y0 Y1 Y2 F : R)
    (h0 : Y0 ^ 2 = F)
    (h1 : Y1 ^ 2 = F)
    (h2 : Y2 ^ 2 = F) :
    (Y1 * Y2) * (Y2 * Y0) * (Y0 * Y1) = F ^ 3 := by
  calc
    (Y1 * Y2) * (Y2 * Y0) * (Y0 * Y1)
        = (Y0 ^ 2) * (Y1 ^ 2) * (Y2 ^ 2) := by ring
    _ = F ^ 3 := by rw [h0, h1, h2]; ring

/-- The V15 binary sector polynomial before division by six. -/
def sectorNumerator (u : R) : R :=
  u ^ 3 + u ^ 2 - 2 * u + 6

theorem sectorNumerator_zero :
    sectorNumerator (0 : R) = 6 := by
  simp [sectorNumerator]

theorem sectorNumerator_neg_two :
    sectorNumerator (-2 : R) = 6 := by
  ring

/-- A nontrivial cube root and its square satisfy the same cyclotomic
quadratic relation. -/
theorem cube_root_square_relation
    (beta : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    (beta ^ 2) ^ 2 + beta ^ 2 + 1 = 0 := by
  calc
    (beta ^ 2) ^ 2 + beta ^ 2 + 1
        = (beta ^ 2 - beta + 1) * (beta ^ 2 + beta + 1) := by ring
    _ = 0 := by rw [hbeta]; ring

theorem sectorNumerator_neg_two_beta
    (beta : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    sectorNumerator (-2 * beta) = -6 := by
  unfold sectorNumerator
  linear_combination (-8 * (beta - 1) + 4) * hbeta

theorem sectorNumerator_neg_two_beta_sq
    (beta : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    sectorNumerator (-2 * beta ^ 2) = -6 := by
  exact sectorNumerator_neg_two_beta
    (beta := beta ^ 2)
    (cube_root_square_relation beta hbeta)

/-- The C3 Fourier selector of the three complementary pairwise signs. -/
def selectorOfSectorBits
    (beta kappa0 kappa1 kappa2 : R) : R :=
  -(kappa0 + beta ^ 2 * kappa1 + beta * kappa2)

theorem selector_uniform
    (beta : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    selectorOfSectorBits beta 1 1 1 = 0 := by
  unfold selectorOfSectorBits
  linear_combination -hbeta

theorem selector_minority_zero
    (beta : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    selectorOfSectorBits beta 1 (-1) (-1) = -2 := by
  unfold selectorOfSectorBits
  linear_combination hbeta

theorem selector_minority_one
    (beta : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    selectorOfSectorBits beta (-1) 1 (-1) = -2 * beta ^ 2 := by
  unfold selectorOfSectorBits
  linear_combination hbeta

theorem selector_minority_two
    (beta : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    selectorOfSectorBits beta (-1) (-1) 1 = -2 * beta := by
  unfold selectorOfSectorBits
  linear_combination hbeta

/-- On the four selector branches `u=0` or `u^3=-8`, the V14 direct
reconstruction factor and the V15 binary-sector numerator coincide after
clearing the denominators two and six. -/
theorem selector_reconstruction_collapse
    (u : R)
    (hselector : u * (u ^ 3 + 8) = 0) :
    (6 + u ^ 3) * (2 + 2 * u - u ^ 2)
      = 2 * sectorNumerator u := by
  unfold sectorNumerator
  linear_combination -(u - 2) * hselector

end Ecdlp.CarrySectorFactorization
