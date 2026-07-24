# Division-resultant scope for secp256k1

Status: `PARTIAL_COMPLETE`

The reduction and Bezout layer is formalized. A second, independent conditional route
from the arbitrary-index root-to-torsion theorem to the requested coprimality theorem is
also formalized. The universal integral support statement, its stronger exact resultant
formula, and the arbitrary-index root-to-torsion theorem are not proved in Mathlib
v4.31.0 or in this repository.
Consequently, this work does not yet close the requested unconditional theorem for every
pair of distinct odd primes.

## Kernel-proved without the missing formula

`Ecdlp/Proved/DivisionResultantTransport.lean` proves the following facts without `sorry`,
`admit`, or new axioms:

1. `secp256k1Z` is the integral Weierstrass model with coefficients
   `(0, 0, 0, 0, 7)`.
2. `secp256k1Z_discriminant` computes its discriminant as
   `-21168 = -2^4 * 3^3 * 7^2`.
3. `secp256k1Z_discriminant_pow_bad_prime_support` proves that every power of this
   discriminant has prime support contained in `{2,3,7}`.
4. `secp256k1Z_map` identifies its reduction modulo `Secp256k1.p` with the existing
   repository object `secp256k1`.
5. `natDegree_preΨ'_le_odd` supplies the fixed bound
   `D(n) = (n^2 - 1) / 2` for odd indices.
6. `isCoprime_of_isUnit_resultant` turns a unit fixed-size resultant into an explicit
   polynomial Bezout identity.
7. `secp256k1_resultant_eq_intCast` proves that fixed-size resultants commute with
   reduction from `ℤ` to `ZMod Secp256k1.p`.
8. `secp256k1_isCoprime_preΨ'_of_integral_resultant_bad_prime_support` proves field
   coprimality from bad-prime support of the corresponding integral resultant.
9. `secp256k1_isCoprime_preΨ'_odd_primes_of_integral_resultant_bad_prime_support`
   proves the requested universal field theorem from the exact universal support
   proposition.
10. The existing `Ecdlp.DivisionPoly.exists_common_root_of_not_isCoprime` is reused to
    obtain a common root of two non-coprime polynomials, including zero-polynomial edge
    cases. It is not duplicated in the new file.
11. `exists_nonsingular_y` proves that every x-coordinate over an algebraically closed
    field lifts to a nonsingular affine point of an elliptic Weierstrass curve.
12. `isCoprime_preΨ'_odd_primes_of_torsion_bridge` proves that the missing general
    root-to-torsion bridge implies coprimality for all distinct odd prime indices.
13. `isCoprime_preΨ'_odd_primes_of_algebraicClosure_torsion_bridge` descends that result
    from an algebraic closure to the original field.
14. `secp256k1_isCoprime_preΨ'_odd_primes_of_torsion_bridge` specializes the conditional
    theorem to secp256k1.
15. `secp256k1_isCoprime_preΨ'_odd_primes_of_integral_resultant_formula` proves the same
    conclusion from exactly one named integral resultant proposition.

The use of fixed sizes is essential. If the residue characteristic divides an index, a
division polynomial can lose degree after reduction. Mathlib's fixed-size Sylvester
resultant still obeys `resultant_map_map`, so the proof does not silently assume degree
preservation.

The secp256k1 specializations inherit `Lean.ofReduceBool` only from the repository's
already audited machine certificates for the field prime and ellipticity. The new
generic resultant, algebraic-closure, and torsion-order arguments introduce no custom
axioms.

## Deliverable 1: exact integral support frontier

The exact universal proposition requested in deliverable 1 is represented in Lean as
`Secp256k1IntegralResultantBadPrimeSupport`:

```lean
def Secp256k1IntegralResultantBadPrimeSupport : Prop :=
  ∀ {m n : ℕ}, Nat.Prime m → Nat.Prime n → Odd m → Odd n → m ≠ n →
    HasOnlySecp256k1BadPrimeDivisors
      ((secp256k1Z.preΨ' m).resultant (secp256k1Z.preΨ' n)
        (oddDivisionDegree m) (oddDivisionDegree n))
```

This proposition is not proved. Lean does prove that any proof of it implies the full
requested `IsCoprime` theorem.

A stronger candidate statement is represented by
`Secp256k1IntegralResultantFormula`. Expanded, its intended theorem is:

```lean
theorem secp256k1_integral_resultant_formula :
    ∀ {m n : ℕ}, Nat.Prime m → Nat.Prime n → Odd m → Odd n → m ≠ n →
      (secp256k1Z.preΨ' m).resultant (secp256k1Z.preΨ' n)
          (oddDivisionDegree m) (oddDivisionDegree n) =
        secp256k1Z.Δ ^ divisionResultantExponent m n
```

where

```text
oddDivisionDegree n           = (n^2 - 1) / 2
divisionResultantExponent m n = ((m^2 - 1) * (n^2 - 1)) / 24.
```

This statement immediately implies the requested bad-prime support assertion because
`secp256k1Z.Δ = -2^4 * 3^3 * 7^2`. It also implies the field-level theorem because the
characteristic `Secp256k1.p` is not a divisor of that discriminant.

Both missing propositions are `def : Prop`, not axioms, instances, or assumed global
theorems. Every consumer must supply a proof explicitly. Thus `#print axioms` cannot hide
the missing mathematics. The formula proposition is stronger than prime-support
containment, but the computational data consistently supports the exact identity.

The unconditional all-index bad-prime-support theorem requested as deliverable 1 is not
proved in this branch. The proved content is the full transport from such support, or
from the exact formula above, to `IsCoprime` modulo `Secp256k1.p`.

## Deliverable 2: exact root-to-torsion missing lemma

The geometric route uses one standard missing lemma, represented by
`OddDivisionPolynomialTorsionBridge W`:

```lean
def OddDivisionPolynomialTorsionBridge
    {K : Type*} [Field K] [IsAlgClosed K] [DecidableEq K]
    (W : WeierstrassCurve K) [W.IsElliptic] : Prop :=
  ∀ (r : ℕ), Odd r → ∀ (x y : K) (hxy : W.toAffine.Nonsingular x y),
      (W.preΨ' r).eval x = 0 ↔
        r • (WeierstrassCurve.Affine.Point.some x y hxy) = 0
```

The secp256k1-specialized proposition consumed by the final conditional theorem is:

```lean
noncomputable def Secp256k1OddDivisionPolynomialTorsionBridge : Prop := by
  letI : DecidableEq (AlgebraicClosure (ZMod Secp256k1.p)) := Classical.decEq _
  exact OddDivisionPolynomialTorsionBridge
    (secp256k1.map (algebraMap (ZMod Secp256k1.p)
      (AlgebraicClosure (ZMod Secp256k1.p))))
```

The `DecidableEq` argument is an implementation requirement of Mathlib's computable
affine group law, not an additional mathematical hypothesis. For secp256k1 the bridge
is assumed only after base change to
`AlgebraicClosure (ZMod Secp256k1.p)`.

From precisely this proposition, Lean proves the requested theorem for all distinct
odd primes. The kernel-checked deduction is:

1. Non-coprime polynomials over the algebraic closure have a common root `x`, including
   zero-polynomial edge cases.
2. Algebraic closedness supplies `y` on the Weierstrass equation; ellipticity makes the
   resulting affine point nonsingular.
3. The bridge makes the same nonzero point both `m`-torsion and `n`-torsion.
4. Its additive order divides `gcd(m,n)=1`, a contradiction.
5. `Polynomial.isCoprime_map` descends coprimality to `ZMod Secp256k1.p`.

This conditional theorem does not assume the integral resultant formula.

## Independent computation

`scripts/certs/division_resultant_formula.py` rebuilds the integral division polynomials
from their recurrence. It does not import Lean output. Sympy checks exact resultants for

```text
(3,5), (3,7), (5,7), (3,11), (5,11), (7,11).
```

For every pair it verifies both the exact discriminant-power identity and prime support
contained in `{2,3,7}`. A successful run ends with `CERT_OK`.

These computations are independent evidence and regression certificates. They are not a
proof of the universally quantified Lean proposition.

## Mathematical proof route for the integral formula

A standard paper proof can proceed over the universal smooth Weierstrass base with the
discriminant inverted.

1. Establish the arbitrary-index divisor or root theorem for division polynomials. For
   odd `r`, the finite roots of `ψ_r` are the nonidentity geometric points killed by
   multiplication by `r`, with the correct multiplicities in characteristics dividing
   `r`.
2. For coprime `m,n`, the two torsion subgroup schemes intersect only in the identity.
   The finite root divisors are therefore disjoint on every smooth fiber. Their universal
   resultant is a unit after the discriminant is inverted.
3. Descend the unit statement to the integral coefficient ring. Homogeneity under
   Weierstrass changes of variables shows that the only nonconstant factor is a power of
   the discriminant. The weights give exponent
   `((m^2 - 1)(n^2 - 1))/24`; normalization determines the unit and sign.
4. Specialize the universal identity to `(a1,a2,a3,a4,a6) = (0,0,0,0,7)` and then reduce
   modulo `Secp256k1.p` using `secp256k1_resultant_eq_intCast`.

References for the torsion, multiplication, division-polynomial, and separability
ingredients include Joseph Silverman, *The Arithmetic of Elliptic Curves*, Chapter III
([Springer, DOI 10.1007/978-0-387-09494-6](https://doi.org/10.1007/978-0-387-09494-6));
Lawrence Washington, *Elliptic Curves: Number Theory and Cryptography*, sections on
division polynomials and torsion
([CRC, DOI 10.1201/9781420071474](https://doi.org/10.1201/9781420071474)); Morgan Ward,
*Memoir on Elliptic Divisibility Sequences*, *American Journal of Mathematics* 70
(1948), 31-74; and van der Poorten and Swart,
[*Recurrence Relations for Elliptic Sequences*](https://arxiv.org/abs/math/0412293).

These references support the route and its classical ingredients. This note does not
claim that any one of them states the exact fixed-size Mathlib resultant identity above.

## What blocks Mathlib v4.31.0

Mathlib supplies the recursive division polynomials, their map theorem, degree bounds,
and the Sylvester-resultant API. It does not supply the arbitrary-index theorem
identifying `ψ_r = 0` with nonidentity `r`-torsion in every relevant characteristic.
The repository contains verified per-index bridges for prime `r in {2,3,5,7}`, plus a
separate even composite bridge at `r = 4`. The conditional arbitrary-index theorem
isolates the remaining absence exactly, rather than assuming the desired coprimality
or resultant statement itself.

The repository also proves that Mathlib's normalized EDS satisfies Ward's elliptic
recurrence. That recurrence alone is not a formal strong-divisibility theorem for these
polynomials and does not determine the exact universal resultant or its valuation at the
discriminant. The missing work is genuine universal-curve, finite-flat torsion,
inseparability, and normalization machinery, rather than a theorem-name lookup.

## Honest conclusion

Unconditional bad-prime support for all distinct odd primes remains open in this Lean
snapshot. The reduction from that support, or from the stronger exact formula, to the
desired secp256k1 `IsCoprime` theorem is kernel-proved. Independently, the desired theorem
is kernel-proved conditional on the exact arbitrary-index root-to-torsion bridge. No claim
in this branch implies a cryptanalytic break or an algorithm for solving secp256k1
discrete logarithms.
