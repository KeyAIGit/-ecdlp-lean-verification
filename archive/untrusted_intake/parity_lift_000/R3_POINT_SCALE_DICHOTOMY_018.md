# R3-POINT-SCALE-DICHOTOMY-018

Date: 2026-08-12

Status: exact identity and corrected interpretation of `TRACE-CM-INDEX-SECTIONS-015`.

This package uses only the frozen toy family.

## 1. Public normalized character

The normalization-aware point character is

```text
C(k) = s^k * rho(k),
```

where `rho(k)=chi(psi_k(G))` and the public scale sign is `s in {+1,-1}`.
For the canonical GLV representatives

```text
k0 = k,
k1 = [lambda*k]_n,
k2 = [lambda^2*k]_n,
k0+k1+k2 = gamma*n,
gamma in {1,2},
```

the subgroup order `n` is odd.

Define

```text
R3(k) = rho(k0)rho(k1)rho(k2),
P3(k) = C(k0)C(k1)C(k2).
```

Then exactly

```text
P3(k) = s^(k0+k1+k2) R3(k)
      = s^gamma R3(k).                              (1)
```

## 2. Complete dichotomy

For `s=+1`, equation (1) becomes

```text
P3(k) = R3(k).
```

Thus `R3` is already the public C3 orbit norm. An exact section matching it is
another expression for a public function, not an independent carry equation.

For `s=-1`, the GLV carry sign is `g(k)=(-1)^gamma`, and

```text
R3(k) = g(k) P3(k).                                 (2)
```

Since `P3` is public, an independent `R3` formula in this branch would recover
the carry sign. Only this branch is a positive research gate.

## 3. Reclassification of package 015

The frozen replay gives:

```text
point-scale +1 cases                  7
point-scale -1 cases                  8
exact R3 matches reported by 015      7
exact matches with s=+1               7
exact matches with s=-1               0
```

All seven exact matches, including `psi_1812` at order `4021`, are therefore
public tautologies under equation (1). No carry-equivalent exact `R3` formula
was found in the `s=-1` branch.

## 4. Exact replay and Lean core

`experiments/parity_lift_000/r3_point_scale_dichotomy.py` recomputes the scale
sign, public point character, carry, raw `R3`, and public orbit norm for every
nonzero scalar in all fifteen frozen groups. It then classifies each package-015
match as:

```text
none,
public_tautology,
carry_equivalent_nontrivial.
```

`Ecdlp/Proved/R3PointScaleDichotomy.lean` proves the same bookkeeping in
`ZMod 2`:

```text
publicNormBit = gammaBit*pointScaleBit + r3Bit.
```

The two scale choices reduce respectively to `publicNormBit=r3Bit` and
`r3Bit+publicNormBit=gammaBit`.

## 5. Corrected automated gate

The condition

```text
exact_r3_decoders > 0
```

is not sufficient. The corrected condition is:

```text
an exact R3 match exists in a point-scale s=-1 case.
```

A future screen should quotient out the maximal public normalized factor before
calling an exact match progress.

## 6. Consequence

The trace and CM-index family currently has:

```text
no admitted exact carry formula at large order,
no exact hard-branch R3 formula,
no large carry correlation above its matched null envelope,
no repeated inverse-log-heavy spectrum.
```

The next package is `PUBLIC-FACTOR-QUOTIENT-SCREEN-019`, which will compare only
the residual part of each candidate after removing known public factors.

## Artifacts

```text
experiments/parity_lift_000/r3_point_scale_dichotomy.py
Ecdlp/Proved/R3PointScaleDichotomy.lean
.github/workflows/r3-point-scale-dichotomy.yml
```

## Claim boundary

The point-scale C3 identity and frozen classification are exact. This corrects
the interpretation of package 015 but does not classify every possible
order-dependent section.
