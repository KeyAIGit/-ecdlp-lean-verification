# CM-QUARTIC-ANCHOR-001

Date: 2026-08-11
Status: bounded positive toy witness, non-executable intake

This note records the first positive witness found in `PARITY-LIFT-000` for an
absolute root-phase observable. It targets no external key or production-sized
discrete-log instance and makes no asymptotic claim.

## 1. Why this class was tested

`RELATIVE-RESIDUE-GAUGE-001` shows that ordinary fixed-rank elliptic-net
transport is invariant under quadratic net rescaling. It can produce relative
EDS-residue signs, but it cannot choose their remaining global sign.

The generalized division-polynomial theory for CM isogenies contains root
correction factors that are not ordinary net ratios. In the Gaussian CM case,
Ward's formulas use a factor `sqrt(x)` for endomorphism indices whose norm is
`2 mod 4`. Stange's arbitrary-isogeny framework explains these factors through
biased-isogeny correction functions.

This suggests testing a finite-field branch of the same root phase.

## 2. Quartic root phase on a j=1728 curve

Consider

```text
E_A: y^2 = x^3 + A*x
```

over a prime field with

```text
p = 1 mod 4.
```

The point `(0,0)` is rational 2-torsion. On an odd-order subgroup, every point
is divisible by two, so its x-coordinate is a square for the associated
2-descent class. Define the public quartic sign

```text
kappa(P) = x(P)^((p-1)/4) in {+1,-1}.
```

This is not the ordinary quadratic character of `x(P)`, which is constant on
the odd subgroup. It selects whether the square x-coordinate is a fourth power,
and therefore retains one root-phase bit.

The comparison target is

```text
rho_G([k]G) = chi(psi_k(G)).
```

## 3. Exact bounded positive witness

On the frozen curve

```text
p = 569,
E: y^2 = x^3 + x,
ord(G) = 17,
G = (562,315),
```

the screen evaluates every nonzero scalar and every generator `[u]G` of the
same order-17 subgroup.

For exactly the eight quadratic-residue multipliers

```text
u in {1,2,4,8,9,13,15,16} mod 17,
```

the identity

```text
kappa([k]([u]G)) = -rho_[u]G(k)
```

holds for all

```text
k = 1,...,16.
```

Thus one inexpensive coordinate-root phase exactly decodes the complete,
nonconstant EDS-residue sequence on these eight generator choices.

For the eight nonresidue generator multipliers, the best agreement is exactly
`8/16`, so the generator dependence is itself structured rather than a single
chosen-point fit.

This is a real positive mechanism witness on a toy CM subgroup. It is not a
secp256k1 result.

## 4. Larger frozen controls

The same observable was tested over every generator of three larger frozen
prime-order subgroups:

| field | curve | subgroup order | best agreement | exact generator |
|---:|---|---:|---:|---:|
| 953 | `y^2=x^3+4x` | 29 | 24/28 = 0.8571 | none |
| 2477 | `y^2=x^3+x` | 37 | 32/36 = 0.8889 | none |
| 569 | `y^2=x^3+3x` | 53 | 40/52 = 0.7692 | none |

The exact order-17 identity therefore does not currently show a scaling law.
It may be a finite-order CM resonance rather than a family-level decoder.

The reproducible implementation and frozen output are:

- `experiments/parity_lift_000/cm_quartic_anchor_screen.py`;
- `experiments/parity_lift_000/cm_quartic_anchor_results.json`.

## 5. What is genuinely positive

Before this screen, every concrete candidate in the parity line was either a
coordinate reparameterization, a relative sign, a balanced net expression, or
a bounded negative.

This witness establishes a narrower positive statement:

```text
An absolute algebraic root phase outside ordinary quadratic net equivalence can
encode the complete EDS-residue bit on a nontrivial prime-order CM subgroup.
```

It proves that the desired mechanism class is not logically empty. The root
phase is public, cheap, sign-valued, and absolute.

What it does not establish:

- persistence as subgroup order grows;
- a sub-square-root algorithm on a cryptographic curve;
- transfer from Gaussian CM to Eisenstein CM;
- transfer to secp256k1;
- any general ECDLP improvement.

## 6. Why this does not directly transfer to secp256k1

The positive toy construction uses three properties absent from secp256k1:

1. `j=1728` and Gaussian CM by `Z[i]`;
2. rational 2-torsion `(0,0)`;
3. `p=1 mod 4`, so a quartic residue sign exists in the base field.

secp256k1 instead has:

```text
j = 0,
CM by the Eisenstein order,
no nonzero rational 2-torsion,
p = 3 mod 4.
```

Therefore `x(P)^((p-1)/4)` is not even defined as a quartic sign on the target
field, and the relevant root divisor does not descend from rational 2-torsion.

## 7. The new focused hypothesis

The correct successor is not to fit more ordinary rational functions. It is to
seek the Eisenstein-CM analogue of the Gaussian `sqrt(x)` correction.

Name:

```text
EISENSTEIN-ROOT-PHASE-001
```

Question:

> For `E:y^2=x^3+7`, does a generalized division polynomial attached to a
> degree-3 Eisenstein endomorphism admit a canonically descended root phase
> whose quadratic or mixed character equals the secp256k1 EDS residue?

The candidate must specify:

1. the exact endomorphism or isogeny and its generalized division function;
2. the extension field in which the root exists;
3. a Frobenius-compatible branch or descent law;
4. an output in `{+1,-1}` defined from public `x(Q)`;
5. proof that norming or descent does not erase the phase;
6. a complete evaluation and recovery cost;
7. cross-order toy scaling before any secp256k1 claim.

The current expectation is uncertain. The Gaussian witness makes the class
worth testing, while the lack of rational 2-torsion and the unbiased-isogeny
boundary make direct transfer unlikely.

## 8. Current evidence score

These percentages measure completion of this package, not probability of an
ECDLP break.

| item | completion |
|---|---:|
| exact order-17 positive witness | 100% |
| three larger frozen controls | 100% |
| reproducible bounded screen | 100% |
| explanation through Gaussian CM root correction | about 60% |
| family-level scaling theorem | 0% |
| Eisenstein analogue for secp256k1 | about 10% |
| sub-square-root decoder | no evidence yet |

## Primary mathematical anchors

- Katherine E. Stange, *Division Polynomials for Arbitrary Isogenies*,
  especially the Gaussian CM comparison with Ward and the extra root factors
  for biased isogenies.
- Morgan Ward's Gaussian-indexed division-polynomial construction, as discussed
  in that comparison.
