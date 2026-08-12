# FROBENIUS-ORIENTATION-OBSTRUCTION-030

Date: 2026-08-12

Status: **theorem-first scoped no-go for Frobenius-invariant descent of the GLV Gaussian-period orientation**.

No external point, private key, wallet, or production-sized discrete-log target is accepted. This package constructs no carry, R3, parity, or ECDLP decoder.

## 1. Input from package 029

For

```text
Q=[k]G,
z=zeta_n^k,
eta_G(Q)=z+z^lambda+z^(lambda^2),
```

the GLV carry satisfies

```text
g_G(Q)=-sign(Im eta_G(Q)).
```

The carry is the orientation of the conjugate pair

```text
{eta_G(Q), conjugate(eta_G(Q))}.
```

## 2. Frobenius action

Realize the order-`n` phase in a finite-field extension containing `mu_n`. Frobenius acts by

```text
zeta_n^k -> zeta_n^(p*k),
eta_k     -> eta_(p*k).
```

Let

```text
d=ord_n(p).
```

For secp256k1 the existing exact certificate gives

```text
d=(n-1)/6,
p^(d/2)=-1 mod n.
```

Therefore half-Frobenius sends

```text
eta_k -> eta_(-k)=conjugate(eta_k).
```

## 3. Exact obstruction

Let `D` be any predicate of the period data that is invariant under Frobenius:

```text
D(eta^p)=D(eta).
```

Iteration gives

```text
D(eta^(p^(d/2)))=D(eta).
```

Using the half-Frobenius certificate,

```text
D(conjugate(eta_k))=D(eta_k).
```

Equivalently, the induced scalar predicate satisfies

```text
D(-k)=D(k).
```

But the generator-relative GLV carry obeys

```text
g_G(-k)=-g_G(k).
```

Hence no Frobenius-invariant predicate can equal the carry on both members of a nonzero negation pair.

This is an exact logical contradiction. It closes every proposed decoder that first descends the Gaussian period through ordinary Frobenius-invariant operations and only then applies a binary test.

## 4. Covered constructions

The scoped obstruction covers any construction whose final state is obtained only from Frobenius-invariant combinations such as:

```text
trace;
norm;
elementary symmetric polynomials of a full Frobenius orbit;
minimal-polynomial coefficients;
polynomials in eta and conjugate(eta) invariant under their exchange;
the discriminant square (eta-conjugate(eta))^2;
any base-field rational expression in such invariants.
```

All of these determine at most the unordered conjugate pair. They cannot choose its orientation.

## 5. What remains open

A successful construction must include a Frobenius-anti-invariant orientation datum. Abstractly it needs an element or section `tau` satisfying

```text
tau^(p^(d/2))=-tau
```

and a public normalization relating the target resolvent

```text
A_G(Q)=eta_G(Q)-conjugate(eta_G(Q))
```

to that orientation.

Merely choosing an arbitrary basis element of the quadratic step

```text
F_(p^d) / F_(p^(d/2))
```

does not solve the problem. The choice must be tied canonically to the public generator `G` and to the complex/cyclotomic branch whose sign equals the carry. Otherwise it is a coordinate convention unrelated to `g_G`.

The ordinary explicit extension representation has degree `d`, far above the square-root scale for secp256k1. This package does not prove a circuit lower bound against an implicit or compressed anti-invariant seed.

## 6. Answer

```text
Can trace/norm or any Frobenius-invariant descent decode carry?   no
Can symmetric Gaussian-period data select the conjugate branch? no
What must a surviving construction contain?                     a public Frobenius-anti-invariant orientation
Is such a sub-sqrt orientation seed known?                       no
Public carry or hard-R3 decoder                                  absent
Unconditional sub-sqrt ECDLP algorithm                           absent
```

## 7. Next object

The successor is

```text
ANTI-FROBENIUS-ORIENTATION-SEED-031.
```

Its object is a public generator-sensitive seed or section

```text
tau_G,
tau_G^(p^(d/2))=-tau_G,
```

together with a compact rule that evaluates only the relative branch

```text
A_G(Q)/tau_G
```

or an equivalent binary orientation predicate.

Central question:

> Can a generator-sensitive anti-Frobenius seed be specified and evaluated with total time, memory, preprocessing, advice, and precision `O(n^(1/2-epsilon))`, while being canonically linked to `G` and not encoding a faithful order-`n` dual character or an `(n-1)/6`-entry orientation table?

The first obligations are:

1. classify anti-invariant elements under half-Frobenius as a one-dimensional module over the fixed subfield;
2. prove the generator-change law for any proposed seed;
3. identify whether its normalization ratio is again an order-`n` dual character;
4. count the representation and advice size;
5. obtain either a compact exact branch formula or a scoped lower bound for the proposed seed family.

No broad ML, lookup, or bounded rational-function search is admitted without a new exact identity.

## 8. Formalization boundary

`Ecdlp/Proved/FrobeniusOrientationObstruction.lean` formalizes the abstract fact that a decoder invariant under a map and all its iterates cannot decode a target that flips when one iterate equals negation.

Lean does not formalize cyclotomic finite fields, the secp256k1 multiplicative-order certificate, Gaussian periods, or the geometric link from a theta section to a Frobenius-invariant predicate. Those are explicit premises of this scoped result.
