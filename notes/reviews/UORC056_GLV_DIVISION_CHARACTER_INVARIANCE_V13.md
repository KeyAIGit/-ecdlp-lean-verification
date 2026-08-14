# UORC-056 GLV division-character invariance V13

Date: 2026-08-14

Status: **on secp256k1, every quadratic character of a multiplicative monomial in classical division polynomials evaluated at arbitrary public scalar pullbacks is GLV-invariant. Canonical scalar parity is not GLV-invariant. Therefore the entire multiplicative division-polynomial character class is excluded, including products and quotients of arbitrarily many high-index factors.**

Central target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G.
```

V13 is a representation-class closure. It does not close field-valued sums/differences or the central evaluator.

## 1. The order-three curve automorphism

For

```text
E: y^2=x^3+7
```

over a field containing a nontrivial cube root `beta`, define

```text
alpha(x,y)=(beta*x,y),
beta^2+beta+1=0.
```

Then `alpha` is an order-three elliptic-curve automorphism and commutes with every scalar multiplication `[s]`.

For the public secp256k1 constants in the repository,

```text
alpha(G)=[lambda]G,
lambda^2+lambda+1=0 mod n.
```

The executable replay checks the coordinate equality directly. The fixed public `lambda` is even and lies in `1,...,n-1`.

## 2. CM weight of every classical division polynomial

Let `psi_m` denote the standard short-Weierstrass division polynomials. Define

```text
e_m = 1  if 3 divides m,
      0  otherwise.
```

Then for every positive integer `m`,

```text
boxed:
psi_m(alpha(Q))=beta^(e_m) psi_m(Q).             (V13.1)
```

### Base cases

On `y^2=x^3+7`,

```text
psi_1=1,
psi_2=2y,
psi_3=3x^4+84x,
psi_4=4y(x^6+140x^3-392).
```

Thus `psi_1,psi_2,psi_4` are invariant and `psi_3(beta*x,y)=beta psi_3(x,y)`.

### Recurrence induction

For `m=2r+1`,

```text
psi_(2r+1)=psi_(r+2) psi_r^3 - psi_(r-1) psi_(r+1)^3.
```

Modulo the order-three weight, cubes contribute weight zero. The two terms have weights

```text
e_(r+2), e_(r-1),
```

which agree because `r+2 == r-1 mod 3`. This common weight is one exactly when `3 | (2r+1)`.

For `m=2r`,

```text
psi_(2r)=psi_r/psi_2 *
 (psi_(r+2) psi_(r-1)^2 - psi_(r-2) psi_(r+1)^2).
```

Checking `r mod 3` shows both inner terms have the same weight and, after the outer `psi_r`, the total weight is one exactly when `3 | r`, equivalently `3 | 2r`.

This proves `(V13.1)` for all indices, not merely a bounded list.

## 3. The beta factor is invisible to the quadratic character

secp256k1 has

```text
p == 1 mod 6.
```

Therefore every element of order three in `F_p^*` lies in the subgroup of squares. In particular

```text
chi(beta)=+1.                                    (V13.2)
```

Taking the quadratic character of `(V13.1)` gives the all-index identity

```text
boxed:
chi(psi_m(alpha(Q)))=chi(psi_m(Q)).              (V13.3)
```

whenever the factor is nonzero.

## 4. Arbitrary public scalar pullbacks

Because `alpha` is a group endomorphism,

```text
alpha([s]Q)=[s]alpha(Q).
```

Hence for every public integer pair `(m,s)`,

```text
chi(psi_m([s]alpha(Q)))
 =chi(psi_m(alpha([s]Q)))
 =chi(psi_m([s]Q)).                              (V13.4)
```

The size of `m` and `s` is irrelevant. They may depend on the public curve order and may have hundreds of bits.

## 5. Closure under products and quotients

Consider any everywhere-defined evaluator of the form

```text
C(Q)=chi(
  c * product_i psi_(m_i)([s_i]Q)^(e_i)
),
```

where `c` is a public nonzero constant and `e_i` are arbitrary integers. Equivalently this covers finite products/quotients of the individual quadratic-character atoms.

Every factor in `(V13.4)` is invariant under `alpha`; inverses and products preserve invariance. Therefore

```text
boxed:
C(alpha(Q))=C(Q) for all admitted Q.             (V13.5)
```

This remains true for arbitrarily many factors. There is no bounded-weight qualification.

## 6. Canonical parity violates GLV invariance

For the fixed secp256k1 pairing of the public constants,

```text
alpha(G)=[lambda]G.
```

The canonical integer representative `lambda` is even. Therefore

```text
sigma_G(G)=-1,
sigma_G(alpha(G))=(-1)^lambda=+1.                (V13.6)
```

So parity is not `alpha`-invariant. Equations `(V13.5)` and `(V13.6)` are incompatible.

Consequently no evaluator in the entire declared multiplicative division-polynomial character class can be the UORC-056 parity evaluator.

## 7. The public ratio-root character is also GLV-invariant

The public point function satisfies

```text
phi_raw(Q)^(n^2)=psi_(p-1)(Q)/psi_(p-1+n)(Q).
```

For secp256k1,

```text
3 | (p-1),
3 does not divide (p-1+n),
n == 1 mod 3.
```

Thus `(V13.1)` makes the ratio scale by `beta`. The unique `n^2`-th root also scales by `beta`, because `(n^2)^(-1)==1 mod 3`. Hence

```text
phi_raw(alpha(Q))=beta phi_raw(Q),
chi(phi_raw(alpha(Q)))=chi(phi_raw(Q)).          (V13.7)
```

This independently explains the low GLV-orbit rank observed in the toy screens and strengthens V12: products of the public point-scale character at arbitrary public scalar multiples are also GLV-invariant and cannot equal parity.

## 8. Relation to V9--V11

V11 already closed one atom `chi(psi_m(Q))` at every index through a large-order character-sum argument. V13 gives a simpler secp-specific CM reason and strictly broadens the closure to:

```text
any finite product or quotient,
any public scalar pullbacks,
any public high indices,
any multiplicative monomial before the outer quadratic character.
```

The small V10 examples do not contradict V13: their curves/orders do not share the fixed secp256k1 GLV/parity mismatch required by `(V13.6)`.

## 9. What V13 does not close

The automorphism-weight argument does **not** exclude expressions where different CM weights are added or subtracted before the final decision. For example

```text
psi_a(Q)+c psi_b(Q)
```

with `3|a` and `3 not|b` is not GLV-invariant. Nor does V13 exclude:

1. direct field-valued evaluation of `Y_G(x(Q))/y(Q)`;
2. the oriented Pell factor `A(x)+yB(x)`;
3. compact global integration of the oriented Miller cocycle;
4. theta or elliptic-unit expressions carrying a nontrivial GLV representation;
5. adaptive branching;
6. general arithmetic circuits mixing CM weights additively.

These non-invariant mixtures are now the relevant place to search.

## 10. Decision

```text
single chi(psi_m) family                              closed
finite products/quotients of chi(psi_m([s]Q))        closed
arbitrary public high indices m,s                     closed
public phi_raw character products                     closed
reason                                                 exact GLV invariance
central field-valued/additive-weight-mixing circuit   open
```

## 11. Claim boundary

V13 is an exact secp256k1 representation-class no-go. It is not a lower bound for arbitrary arithmetic circuits and does not construct or rule out the central oriented-root evaluator itself.
