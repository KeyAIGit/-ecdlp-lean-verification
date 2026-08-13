# ONE-ADDITION-EXECUTOR-GATE-OA1

Date: 2026-08-12

Status: **one exact one-addition EDS identity found; it does not decode GLV carry or hard R3. A complete bounded screen of the monomial-binomial grammar found no target decoder.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Target grammar

The first nonlinear square-class grammar isolated by the conductor pass is

```text
F(Q)=M0(Q)*(1+c*M1(Q)),
Mi(Q)=x(Q)^ai*y(Q)^bi,
```

where exponents may be represented by short addition chains and `c` is generated from public parameters.

The desired exact output is either

```text
chi_p(F(Q))=g_G(Q)
```

or

```text
chi_p(F(Q))=R3_G(Q),
```

for every nonzero point of the prime-order subgroup.

## 2. First exact executor identity

Let

```text
Q=[k]G,
phi(G)=[lambda]G,
z(Q)=x(Q)^3.
```

The GLV orbit of `G` has x-coordinates

```text
x(G), beta*x(G), beta^2*x(G),
beta^3=1.
```

Therefore

```text
x(Q)^3-x(G)^3
 = product_(j=0)^2 (x(Q)-x([lambda^j]G)).            (E1)
```

For division polynomials at the fixed generator, the Ward difference identity is

```text
x([m]G)-x([r]G)
 = -psi_(m+r)(G)*psi_(m-r)(G)
   /(psi_m(G)^2*psi_r(G)^2).                         (E2)
```

Put

```text
rho_psi(t)=chi_p(psi_t(G)),
psi_(-t)=-psi_t.
```

On secp256k1, and on the frozen j=0 family used here, `chi_p(-1)=-1`. Combining `(E1)` and `(E2)` gives the exact public identity

```text
chi_p(1-x(Q)^3/x(G)^3)
 = chi_p(x(G))
   * product_(j=0)^2 rho_psi(k-lambda^j)rho_psi(k+lambda^j).  (E3)
```

This is a genuine one-addition executor: the left side is evaluated directly from public coordinates and the right side is an exact six-factor EDS expression.

## 3. Why it is not the required executor

Identity `(E3)` has three decisive defects.

1. It contains six hidden residue factors, hence even EDS gauge weight.
2. It vanishes at the six public points

```text
+/-G, +/-phi(G), +/-phi^2(G).
```

3. It does not isolate either

```text
g_G(Q)
```

or

```text
R3_G(Q)=rho(k)rho(lambda*k)rho(lambda^2*k).
```

Multiplying `(E3)` by any square-class monomial prefactor `x^epsilon*y^delta` does not repair these defects.

Thus the first natural exact identity returns relative shifted EDS data, not the absolute odd GLV aggregate.

## 4. Exact bounded screen

The accompanying verifier performs two tasks.

### Identity replay

On all fifteen frozen prime-order `j=0` subgroups it checks:

```text
(E1),
(E2),
(E3),
exactly six zeros of the one-addition factor.
```

### Monomial-binomial decoder screen

For the nontrivial frozen cases listed in the output, the verifier exhausts:

```text
all nonzero constants c in F_p,
all exponent classes modulo p-1 in the selected scope,
all square-class prefactors x^epsilon*y^delta,
both global signs,
both carry and R3 targets.
```

On the two anchor cases `p=547` and `p=907`, the x-exponent is unrestricted, so exceptional character-level GLV compatibility is included. On the remaining cases the exact function-level GLV gate `a=0 mod 3` is imposed before the screen.

Result:

```text
exact carry decoders: 0
exact hard-R3 decoders: 0
```

This is a complete finite screen in the declared exponent and constant spaces. It is not a theorem excluding an n-dependent secp256k1-only choice.

## 5. Current answer

```text
First exact one-addition EDS executor                       found
Hidden expression                                          six shifted residues
Odd absolute EDS weight                                    no
Total on the subgroup                                      no, six zeros
Exact carry decoder                                        no
Exact R3 decoder                                           no
Complete bounded monomial-binomial screen                  no target hits
Sub-square-root ECDLP algorithm                            absent
```

## 6. Consequence

The one-addition grammar has produced its first exact identity, but the identity stays in the even relative-EDS layer. The next constructive escape must do at least one of the following:

```text
use two independent additive innovations;
use a transported point-function term rather than one coordinate monomial;
produce an odd residual factor after the public-factor quotient gate;
provide an n-dependent identity with an exact secp256k1 proof.
```

The recommended successor is a two-addition transported-coordinate grammar, not a broader statistical search.

## 7. Claim boundary

The package proves and replays only the stated algebraic identity and bounded finite screen. It does not prove a universal one-addition circuit lower bound, does not compute an unknown secp256k1 scalar, and does not claim an asymptotic improvement over Pollard rho.
