# PADIC-TAME-SYMBOL-ORIENTATION-C059

Date: 2026-08-13

Status: **the logarithmic escape from C058 reduces to a Weil-pairing/tame-symbol phase. Its p-adic logarithm vanishes on prime-to-p roots of unity; retaining the multiplicative value requires a complementary dual torsion point and exposes a full faithful order-n character rather than a compressed binary orientation.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Third-kind differentials and multiplicative holonomy

Let `P` be an `n`-torsion point and choose a Miller function

```text
div(f_P)=n(P)-n(O).
```

A differential of the third kind built from `dlog(f_P)` has logarithmic Coleman integrals whose exponentiated endpoint ratio is represented by values of `f_P`.

For two independent `n`-torsion directions, the corresponding tame-symbol/reciprocity quotient is the Weil pairing

```text
e_n(P,T) in mu_n.                                (T1)
```

Thus the only nontrivial multiplicative torsion phase naturally surviving the additive holonomy collapse of C058 is an order-`n` pairing phase.

## 2. Same-line pairing is trivial

For the public cyclic subgroup

```text
H=<G>,
Q=[k]G,
```

alternation of the Weil pairing gives

```text
e_n(G,Q)=e_n(G,[k]G)=1.                         (T2)
```

Therefore no third-kind construction using only the public subgroup line produces a nontrivial phase.

A nontrivial phase requires a complementary torsion point `T` on the dual line:

```text
eta_T(Q)=e_n(Q,T).
```

After orienting `T` so that `e_n(G,T)=zeta_n`,

```text
boxed:
eta_T([k]G)=zeta_n^k.                            (T3)
```

This is the full faithful scalar character, not one binary bit.

## 3. The p-adic logarithm destroys the phase

Every element of `mu_n`, with `p` not dividing `n`, is a prime-to-p Teichmuller root of unity. The standard p-adic logarithm vanishes on it:

```text
boxed:
log_p(e_n(P,T))=0.                               (T4)
```

Consequently an additive Coleman integral obtained by applying the chosen p-adic logarithm to the tame symbol again gives zero on the torsion phase.

To preserve information one must retain the multiplicative root of unity itself.

## 4. Retaining the root of unity reintroduces the dual selector

The complementary point `T` is not part of the public base-field subgroup data. Choosing `T` versus `[u]T` changes

```text
eta_T(Q) -> eta_T(Q)^u.
```

In particular `T` and `-T` give inverse phases. The choice is exactly an orientation of the dual torsion line.

On the fixed secp256k1 parameters, the nonzero complementary torsion and the order-`n` roots of unity require the previously certified large extension/dual-orbit state. A Frobenius-symmetric norm removes the phase, while a nonsymmetric branch imports the missing orientation.

Thus `(T3)` is not a compact decoder. It is an exact encoding of the full scalar after supplying the hidden dual level structure.

## 5. GLV orbit products

Multiplying the three phases over the GLV orbit gives

```text
eta_T(Q) eta_T(phi Q) eta_T(phi^2 Q)
 =zeta_n^(k+lambda*k+lambda^2*k)
 =1.                                             (T5)
```

The multiplicative phase sees the congruence

```text
1+lambda+lambda^2=0 mod n,
```

but not whether the canonical integer representatives sum to `n` or `2n`. The desired carry is precisely the information lost by reducing the sum modulo `n`.

## 6. Closed class

Closed by this package:

```text
third-kind/tame-symbol phases using only the public subgroup line,
additive p-adic logarithms of prime-to-p torsion symbols,
GLV orbit products of one faithful pairing phase,
Frobenius-symmetric norm descent of the pairing phase,
claims that a Miller/Weil phase is already a binary carry compression.
```

## 7. What remains open

Not closed:

1. a nonlinear p-adic branch functional on the three individual phases that does not require materializing the faithful character;
2. a public compact construction of a dual orientation from special `j=0` CM data;
3. a tangential basepoint rule whose dependence on `G` is proved public and sub-square-root;
4. a non-logarithmic p-adic period invariant not factoring through `(T1)`.

## 8. Successor

The most concrete remaining p-adic object is

```text
PADIC-CANONICAL-LIFT-BRANCH-C060.
```

It asks whether the ordinary canonical lift supplies a distinguished tangential/Serre-Tate coordinate that can compare the three canonical scalar representatives before reduction modulo `n`, rather than merely returning the torsion logarithm or faithful pairing phase.

## Claim boundary

This package classifies the standard logarithmic/tame-symbol mechanism. It does not prove that every nonlinear p-adic function is impossible and does not construct a carry or scalar-recovery algorithm.
