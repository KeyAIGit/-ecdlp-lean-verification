# EVEN-PULLBACK-COLLAPSE-001

Date: 2026-08-11
Status: isolated, non-executable structural note

This note records a scoped no-go result inside `PARITY-LIFT-000`. It targets no
external point, wallet, or production discrete-log instance. It changes no
Research Engine state and claims no general lower bound.

## 1. Setup

Let `G` generate a cyclic subgroup of odd order `n`, let

```text
Q = [k]G,   0 < k < n,
```

and write

```text
W_G(t) = psi_t(G),
rho_G(Q) = chi(W_G(k)),
```

where `chi` is the quadratic character of the base field.

Let `m` be an even integer with `gcd(m,n)=1`. The public point

```text
R = [m^(-1) mod n] Q
```

has a unique canonical scalar `j` with `R=[j]G`. There is an integer `c >= 0`
such that

```text
m*j = k + c*n.
```

Because `m` is even and `n` is odd, reduction modulo two gives

```text
c mod 2 = k mod 2.                                    (1)
```

## 2. Division-polynomial transport

The multiplication identity is

```text
psi_m([j]G) = W_G(m*j) / W_G(j)^(m^2).
```

Since `m^2` is even, the denominator has quadratic character `+1`. Hence

```text
chi(psi_m(R)) = chi(W_G(k+c*n)).                       (2)
```

Let the raw public point function satisfy

```text
phi_raw([t]G) = phi_raw(G)^(t^2) W_G(t).
```

The scalars `k` and `k+c*n` represent the same point. Taking quadratic
characters and using odd `n` yields

```text
chi(W_G(k+c*n))
  = chi(phi_raw(G))^c rho_G(Q)
  = chi(phi_raw(G))^k rho_G(Q),                        (3)
```

where the last equality uses (1). The raw parity bridge gives

```text
chi(phi_raw(Q)) = chi(phi_raw(G))^k rho_G(Q).          (4)
```

Combining (2)--(4):

```text
boxed:
chi(psi_m([m^(-1)]Q)) = chi(phi_raw(Q))
```

for every admissible even `m`.

## 3. Consequence

The tempting procedure

```text
Q -> [m^(-1)]Q -> chi(psi_m(...))
```

does not produce a second independent equation for the hidden EDS residue. It
reconstructs exactly the already-public combined bit `chi(phi_raw(Q))`.

For secp256k1 the recorded fixed-public condition is

```text
chi(phi_raw(G)) = -1,
```

so the collapse reads

```text
chi(psi_m([m^(-1)]Q)) = (-1)^k rho_G(Q).
```

It therefore reveals neither scalar parity nor `rho_G(Q)` separately.

This includes:

- the direct halving attempt `m=2`;
- every fixed even division-polynomial pullback;
- using an even canonical scalar representing a public endomorphism, including
  an even GLV eigenvalue, unless an additional genuinely independent observable
  is introduced.

## 4. Why this matters

Before this check, halving and evaluating `psi_2`, or using a structured even
multiplier, looked like plausible ways to exploit the fact that the exponent
`m^2` becomes a square under `chi`. The wrap integer `c` carries exactly the
missing parity. Its contribution through the absolute EDS normalization restores
the public point-function character and cancels the apparent gain.

The obstruction is not merely "fixed-index quadratic balance". It also tracks
the canonical-representative carry across the period, which is essential for
an absolute residue bit.

## 5. Bounded replay

A frozen toy replay exhaustively checks the boxed identity for every nonzero
scalar `k` and every even `m` in `2 <= m < n` on the five existing prime-order
toy curves:

| field | order | checks |
|---:|---:|---:|
| 43 | 31 | 450 |
| 67 | 79 | 3042 |
| 79 | 67 | 2178 |
| 127 | 127 | 7938 |
| 163 | 139 | 9522 |
| **total** | | **23130** |

The replay is structural evidence only. The derivation above is the mechanism;
the finite checks detect implementation and sign-convention mistakes.

## 6. Remaining target

The surviving question remains

```text
Given x(Q), compute rho_G(Q)
without first recovering k and below square-root total cost.
```

`EVEN-PULLBACK-COLLAPSE-001` removes one broad family of local fixed-index
constructions. It does not close odd-index combinations, nonlocal relations,
unbalanced theta/sigma/net sections, exact p-adic observables, or other
non-generic coordinate mechanisms.
