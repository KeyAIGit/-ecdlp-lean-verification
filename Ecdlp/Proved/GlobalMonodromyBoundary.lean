import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# Arithmetic boundary for global GLV/theta monodromy

This file records the exact elementary facts used by
`GLOBAL-MONODROMY-SECTION-009`.

It does not formalize analytic theta functions, line bundles, group cohomology,
or a public EDS-residue decoder.  It proves the cyclic parity identities and
kernel-checks the finite-field order certificate that constrains any
root-of-unity-valued monodromy construction on the secp256k1 subgroup.
-/

namespace Ecdlp.ParityLift

/-- On an odd cycle, the binary wrap carry is a coboundary.  If `a+b` is
reduced to `r` with integer carry `c`, then the parity of `c` equals the parity
change between the unreduced and reduced integer representatives.  Evaluating
the corresponding splitting function is exactly evaluating canonical scalar
parity; the carry is not a free additional character. -/
theorem oddCycleCarryParity_isCoboundary
    (n a b r c : ℤ)
    (hn : Even (n - 1))
    (hwrap : a + b = r + c * n) :
    Even (((a + b - r) - c)) := by
  rcases hn with ⟨t, ht⟩
  refine ⟨c * t, ?_⟩
  calc
    (a + b - r) - c = c * (n - 1) := by
      linear_combination hwrap
    _ = (c * t) + (c * t) := by
      rw [ht]
      ring

/-- A binary phase whose value on a cyclic generator is annihilated by an odd
cycle length is trivial.  This is the additive parity form of the fact that an
odd-order cyclic group has no nontrivial homomorphism to `mu_2`. -/
theorem oddOrderBinaryPhase_trivial
    (n z : ℤ)
    (hn : Even (n - 1))
    (hcycle : Even (n * z)) :
    Even z := by
  rcases hn with ⟨r, hr⟩
  rcases hcycle with ⟨s, hs⟩
  refine ⟨s - r * z, ?_⟩
  calc
    z = n * z - (n - 1) * z := by ring
    _ = (s - r * z) + (s - r * z) := by
      rw [hs, hr]
      ring

/-- Bezout form of the same obstruction for any finite phase order `m`.
If `n` and `m` admit a Bezout identity and `m` divides `n*z`, then `m` already
divides `z`.  Thus a phase of order coprime to the subgroup order cannot carry
a nontrivial character of that cyclic subgroup. -/
theorem coprimeFinitePhase_trivial
    (n m z u v : ℤ)
    (hbezout : u * n + v * m = 1)
    (hcycle : m ∣ n * z) :
    m ∣ z := by
  rcases hcycle with ⟨q, hq⟩
  refine ⟨u * q + v * z, ?_⟩
  calc
    z = (u * n + v * m) * z := by rw [hbezout]; ring
    _ = u * (n * z) + v * (m * z) := by ring
    _ = u * (m * q) + v * (m * z) := by rw [hq]
    _ = m * (u * q + v * z) := by ring

/-- Candidate exact embedding degree for the secp256k1 prime-order subgroup. -/
def secp256k1MonodromyEmbeddingDegree : ℕ :=
  (Secp256k1.n - 1) / 6

/-- The candidate has the explicit 254-bit value used by the independent
Python certificate. -/
theorem secp256k1MonodromyEmbeddingDegree_value :
    secp256k1MonodromyEmbeddingDegree =
      19298681539552699237261830834781317975472927379845817397100860523586360249056 := by
  native_decide

/-- Complete prime factorization of `(n-1)/6`. -/
theorem secp256k1MonodromyEmbeddingDegree_factorization :
    secp256k1MonodromyEmbeddingDegree =
      2 ^ 5 * 149 * 631 * 107361793816595537 *
        174723607534414371449 * 341948486974166000522343609283189 := by
  native_decide

/-- There is no nontrivial order-`n` multiplicative character already valued
in the base field: `n` is coprime to `p-1`. -/
theorem secp256k1_noBaseFieldOrderNPhase :
    Nat.gcd Secp256k1.n (Secp256k1.p - 1) = 1 := by
  native_decide

/-- The secp256k1 field prime has order dividing the stated candidate modulo
the subgroup order. -/
theorem secp256k1_p_pow_monodromyEmbeddingDegree :
    ((Secp256k1.p : ZMod Secp256k1.n) ^
      secp256k1MonodromyEmbeddingDegree) = 1 := by
  native_decide

/-- Removing the prime factor `2` from the candidate destroys the order
relation. -/
theorem secp256k1_p_pow_monodromyEmbeddingDegree_div_two_ne_one :
    ((Secp256k1.p : ZMod Secp256k1.n) ^
      (secp256k1MonodromyEmbeddingDegree / 2)) ≠ 1 := by
  native_decide

/-- Removing the prime factor `149` destroys the order relation. -/
theorem secp256k1_p_pow_monodromyEmbeddingDegree_div_149_ne_one :
    ((Secp256k1.p : ZMod Secp256k1.n) ^
      (secp256k1MonodromyEmbeddingDegree / 149)) ≠ 1 := by
  native_decide

/-- Removing the prime factor `631` destroys the order relation. -/
theorem secp256k1_p_pow_monodromyEmbeddingDegree_div_631_ne_one :
    ((Secp256k1.p : ZMod Secp256k1.n) ^
      (secp256k1MonodromyEmbeddingDegree / 631)) ≠ 1 := by
  native_decide

/-- Removing the 57-bit prime factor destroys the order relation. -/
theorem secp256k1_p_pow_monodromyEmbeddingDegree_div_q1_ne_one :
    ((Secp256k1.p : ZMod Secp256k1.n) ^
      (secp256k1MonodromyEmbeddingDegree / 107361793816595537)) ≠ 1 := by
  native_decide

/-- Removing the 68-bit prime factor destroys the order relation. -/
theorem secp256k1_p_pow_monodromyEmbeddingDegree_div_q2_ne_one :
    ((Secp256k1.p : ZMod Secp256k1.n) ^
      (secp256k1MonodromyEmbeddingDegree / 174723607534414371449)) ≠ 1 := by
  native_decide

/-- Removing the largest prime factor destroys the order relation. -/
theorem secp256k1_p_pow_monodromyEmbeddingDegree_div_q3_ne_one :
    ((Secp256k1.p : ZMod Secp256k1.n) ^
      (secp256k1MonodromyEmbeddingDegree /
        341948486974166000522343609283189)) ≠ 1 := by
  native_decide

end Ecdlp.ParityLift
