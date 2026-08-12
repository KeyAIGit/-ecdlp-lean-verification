# FIELD-PERMUTATION-CARRY-IDENTITY-017

Date: 2026-08-12

Status: **exact finite identity, exact field-Fourier decimation, conditional mixed-y consequence**.

No external point, key, wallet, or production-sized discrete-log target is
accepted. This package constructs no carry oracle, no EDS-residue decoder, and
no unconditional sub-square-root secp256k1 algorithm.

## 1. The apparent exception

The normalization-aware public spectral census contained a non-algebraic field
ordering predicate:

```text
field_permutation(x)
  = sign((x0-x1)(x1-x2)(x2-x0)),
```

where

```text
x0 = [x]_p,
x1 = [beta*x]_p,
x2 = [beta^2*x]_p
```

are canonical integer representatives and `beta` is a nontrivial cube root of
unity modulo `p`.

Numerically, this predicate had:

```text
field Fourier L1 approximately 1.6 log(p),
maximum field Fourier coefficient approximately 1/pi,
cyclic GLV invariance,
oddness under x -> -x.
```

It initially looked like a new low-complexity observable outside the field-carry
boundary.

## 2. Directed gaps form a scaled GLV orbit

Define the positive directed gaps around the canonical circle:

```text
d0 = [x1-x0]_p,
d1 = [x2-x1]_p,
d2 = [x0-x2]_p.
```

Put

```text
u = (beta-1)*x mod p.
```

Then exactly:

```text
d0 = u,
d1 = beta*u,
d2 = beta^2*u.
```

Indeed,

```text
beta*(beta-1) = beta^2-beta,
beta^2*(beta-1) = 1-beta^2
```

because `beta^3=1`.

Thus the directed gaps are not a new triple. They are the ordinary order-three
field GLV orbit of a public invertible scaling of `x`.

## 3. Cyclic orientation is negative carry

For any three distinct canonical representatives, the three positive directed
gaps sum to:

```text
p   if the labeled order is cyclically positive,
2p  if the labeled order is cyclically negative.
```

Let

```text
C_beta(u) = -1 when u+[beta*u]_p+[beta^2*u]_p = p,
C_beta(u) = +1 when the sum is 2p.
```

The permutation orientation uses the opposite convention:

```text
O_beta(x) = +1 for directed-gap sum p,
O_beta(x) = -1 for directed-gap sum 2p.
```

Therefore the exact pointwise identity is

```text
O_beta(x) = -C_beta((beta-1)*x).                      (1)
```

This holds for every nonzero `x` in every field `F_p` with the stated
order-three root, not merely statistically.

## 4. Exact field-Fourier consequence

Use the normalized additive Fourier transform

```text
hat_F(a) = (1/p) sum_x F(x) e_p(-a*x).
```

Since `beta-1` is invertible,

```text
hat_O_beta(a)
  = -hat_C_beta(a*(beta-1)^(-1)).                    (2)
```

Equation (2) means that multiplication by `beta-1` merely permutes the field
frequencies. Consequently:

```text
||hat_O_beta||_1 = ||hat_C_beta||_1,
max_a |hat_O_beta(a)| = max_a |hat_C_beta(a)|.
```

The centered-sawtooth decomposition of the field carry already gives

```text
||hat_C_beta||_1 <= 3 H_((p-1)/2) = O(log p).
```

Hence

```text
||hat_O_beta||_1 = O(log p).                         (3)
```

The principal coefficient approaching `1/pi` is now explained: it is one of the
six heavy carry coefficients after the frequency permutation in (2).

## 5. Frozen exact replay

`experiments/parity_lift_000/field_permutation_carry_identity.py` verifies for
all nonzero field elements in fifteen frozen fields:

```text
O_beta(x) = -C_beta((beta-1)*x),
the directed-gap orbit identities,
the p or 2p directed-gap sum,
the exact Fourier decimation identity,
field Fourier L1 equality,
maximum Fourier coefficient equality,
product-to-convolution Fourier identity.
```

The replay covers `25,506` nonzero field elements and `76,518` scaled orbit
coordinates.

On the largest frozen field `p=3931`:

```text
||hat_O_beta||_1 approximately 13.4397,
||hat_O_beta||_1 / log(p) approximately 1.6238,
max |hat_O_beta| approximately 0.3183107,
max |hat_O_beta| - 1/pi approximately 8.9e-7.
```

These numerical values support the exact decimation identity; they are not
needed to prove it.

## 6. x-only analytic boundary

Because `O_beta(x)` has logarithmic field Fourier `L1`, the field-to-group
transfer from `PUBLIC-COORDINATE-SPECTRAL-BARRIER-014` applies directly:

```text
max_(j != 0)
  |widehat(O_beta(x([k]G)))(j)|
    = O(log(p)/sqrt(p))
```

for cofactor-one ordinary curves, under the source-pinned twisted elliptic
Gaussian-sum theorem.

Thus `field_permutation(x(P))` is not a new inverse-polylogarithmic scalar
observable.

## 7. Mixed-y consequences

Package `MIXED-Y-HYBRID-TRANSFER-016` isolates the required complete mixed
character sums. Combining that package with (3) gives the conditional bounds:

```text
field_permutation * half_y
  = O(log(p)^2/sqrt(p)),

field_permutation * chi_y
  = O(log(p)/sqrt(p)).
```

For the product of the original field carry and permutation orientation, the
physical-domain product corresponds to field-Fourier convolution. Therefore

```text
||widehat(C_beta * O_beta)||_1
  <= ||hat_C_beta||_1 ||hat_O_beta||_1
  = O(log(p)^2).
```

Adding `half_y` gives

```text
field_carry_x * field_permutation * half_y
  = O(log(p)^3/sqrt(p))
```

under the same two-coordinate complete hybrid-sum theorem.

## 8. Frozen scalar-domain evidence

For all frozen cases with group order at least `500`, none of the following
reached `1/log(n)`:

```text
field_permutation*half_y,
field_permutation*chi_y,
field_carry_x*field_permutation*half_y.
```

Their maximum coefficients multiplied by `sqrt(n)` remain in a small constant
range. This is consistent with the conditional square-root bounds and gives no
separate scaling signal.

## 9. Formalized core

`Ecdlp/Proved/FieldPermutationCarryIdentity.lean` proves:

```text
the directed-gap cyclic-order identity,
the scaled difference-orbit ring identities,
the telescoping sum of difference coefficients,
orientation sign = negative carry sign.
```

Lean does not formalize finite-field canonical representatives or the discrete
Fourier decimation in this package. Those are exhaustively replayed on the
frozen fields by Python.

## 10. Research consequence

The public coordinate shortlist is now substantially smaller. The following
seemingly distinct predicates are the same low-field-Fourier-L1 family:

```text
field_carry_x,
field_permutation_x,
public invertible field scalings of either,
bounded products of these with half-y or chi-y under the mixed hybrid theorem.
```

The next constructive search should not spend additional cycles on integer
ordering of the three field GLV representatives. That route has collapsed to a
known carry under a public change of variable.

The remaining frontier is now:

```text
high-field-Fourier-L1 but compactly evaluable circuits,
order-dependent sections whose conductor grows with n,
non-coordinate analytic or p-adic monodromy,
a direct public cyclotomic carry or R3 decoder,
proof or formalization of the complete mixed character-sum bounds.
```

## 11. Frozen artifacts

```text
experiments/parity_lift_000/field_permutation_carry_identity.py
Ecdlp/Proved/FieldPermutationCarryIdentity.lean
.github/workflows/field-permutation-carry-identity.yml
```

## Claim boundary

The pointwise identity, directed-gap arithmetic, field Fourier frequency
permutation, and finite convolution identities are exact. The x-only
square-root transfer uses the external elliptic Gaussian-sum theorem from
package 014. The mixed-y complexity conclusions use the external hybrid-sum
inputs isolated in package 016. No universal lower bound for arbitrary public
predicates or ECDLP algorithms is claimed.
