# QUADRATIC-WEIL-ORIENTATION-038

Date: 2026-08-12

Status: **exact normalized Weil-ratio and selector-free contraction obtained; standard dual/metaplectic realizations do not meet the classical sub-square-root cost gate**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Exact question

Let

```text
H=<G>, |H|=n,
Q=[k]G,
```

where `n` is an odd prime and, for the secp256k1 branch,

```text
n = 1 mod 12.
```

Let `H_dual` be a complementary `n`-torsion line and choose a nonzero
`T in H_dual`. Normalize the Weil pairing by

```text
e_n(G,T)=zeta_n.
```

Define

```text
W_T(P)=sum_(a mod n) e_n([a^2]P,T).
```

For `Q=[k]G`, this is the classical quadratic Gauss sum

```text
W_T(Q)=sum_a zeta_n^(k*a^2).
```

The package asks whether Eisenstein CM, the principal polarization, Frobenius,
or the finite Weil/metaplectic representation can make the normalized ratio

```text
W_T(Q)/W_T(G)=chi_n(k)
```

publicly computable with complete classical cost

```text
O(n^(1/2-epsilon))
```

for some fixed `epsilon>0`, without constructing the huge pairing field,
materializing an `n`-dimensional state, enumerating `n` phases, or hiding the
same information in preprocessing or advice.

## 2. Exact quadratic Gauss identity

Choose a reference nonzero dual point `T0`. Every other nonzero point on the
dual line is `[u]T0` for a unique `u != 0 mod n`. Put

```text
W_u(k)=sum_(a mod n) zeta_n^(u*k*a^2).
```

For the quadratic character `chi_n`, the classical Gauss identity gives

```text
W_u(k)=chi_n(u) chi_n(k) W_1(1).                 (W1)
```

Because `n=1 mod 4` on secp256k1,

```text
W_1(1)^2=n.                                     (W2)
```

Therefore

```text
W_u(k)/W_u(1)=chi_n(k)                           (W3)
```

for every nonzero `u`.

### First positive conclusion

The normalized ratio is independent of the scale of the dual point.
Consequently, a *distinguished* nonzero dual point is not required. Any
nonzero element of the complementary line gives the same normalized answer.

This removes one orientation ambiguity from package 033. It does not yet
provide an efficient way to represent or evaluate any nonzero dual point.

## 3. Selector-free full-dual contraction

A stronger basis-free construction removes the choice of `T` altogether.
Define

```text
C_G(Q)=sum_(T in H_dual, T != O) W_T(Q) W_T(G).
```

Using `(W1)` and `(W2)`,

```text
W_[u]T0(Q) W_[u]T0(G)
 = chi_n(u)^2 chi_n(k) W_1(1)^2
 = n chi_n(k).
```

There are `n-1` nonzero dual points, hence

```text
C_G(Q)=n(n-1)chi_n(k).                           (W4)
```

Thus

```text
chi_n(k)=C_G(Q)/C_G(G).                          (W5)
```

This is an exact selector-free scalar-Legendre observable. It uses the public
generator `G` to orient the contraction, but it does not choose a basis of the
dual line.

The unweighted trace behaves differently:

```text
sum_(T != O) W_T(Q)=0.                           (W6)
```

Likewise squares, full norms, and even total character powers erase the
quadratic orientation. The bilinear contraction in `(W4)` is the simplest
symmetric expression found that preserves it.

## 4. Orthogonality and the primal square-orbit model

Include the zero dual point, for which `W_O(P)=n`. Pairing-character
orthogonality yields

```text
C0_G(Q)
 = sum_(T in H_dual) W_T(Q)W_T(G)
 = n * N_G(Q),                                   (W7)
```

where

```text
N_G(Q)=#{(a,b) in F_n^2 : [a^2]Q+[b^2]G=O}.
```

For `Q=[k]G`, this is the number of solutions to

```text
k*a^2+b^2=0 mod n.
```

Since `-1` is a square when `n=1 mod 4`,

```text
chi_n(k)=+1  ->  N_G(Q)=2n-1,
chi_n(k)=-1  ->  N_G(Q)=1.                       (W8)
```

Equations `(W7)` and `(W8)` show that the Weil construction is the Fourier
transform of a very concrete public-line object: the overlap of the two
square-scalar orbit vectors

```text
Theta(P)=sum_(a mod n) delta_([a^2]P).
```

The hidden bit asks whether the square orbit of `Q` equals the square orbit of
`G` or its complementary nonsquare coset.

This is a conceptual gain, but not an algorithmic one. Constructing either
`Theta(P)` or its Weil transform has linear support in `n`.

## 5. What the principal polarization and CM actually provide

The principal polarization identifies

```text
E[n]/H  ~= Hom(H,mu_n).
```

Frobenius separates the rational line `H`, on which it acts by `1`, from the
complementary line, on which it acts by `p mod n`.

Every base-field CM endomorphism maps `G` to a scalar multiple of `G`; it does
not manufacture an independent dual point from public points already in `H`.
The complementary eigenspace is canonical as a line, but a concrete nonzero
point on it lives in the pairing extension.

For secp256k1 the exact embedding degree is

```text
d=ord_n(p)=(n-1)/6,
p^(d/2)=-1 mod n.
```

Therefore an explicit nonzero dual point requires an extension of degree

```text
(n-1)/6 ~= 2^253.4.
```

The new contraction `(W4)` avoids choosing such a point, but standard
realizations still have to represent the entire dual line or an equivalent
state space.

## 6. Standard Weil/metaplectic realization

For the two-dimensional symplectic space `E[n]` over `F_n`, the Heisenberg
representation with fixed central character has a Schrödinger model consisting
of functions on a one-dimensional Lagrangian quotient. That quotient contains
`n` elements, so the standard state space has dimension `n`.

The strong Stone-von Neumann construction gives canonical intertwiners between
oriented Lagrangian models. Canonicality is important, but it does not imply a
small arithmetic representation.

Within the standard explicit realization:

```text
one state vector                         n entries,
one dense Weil operator                  n^2 entries,
one literal quadratic Gauss vector       n phases,
selector-free contraction                n^2 raw terms,
standard FFT realization                 Theta(n log n) operations.
```

All of these are far above the Pollard scale `sqrt(n)`.

This is a scoped representation obstruction. It is not a proof that no short
arithmetic circuit, CM trace identity, or specialized straight-line program
can exist.

## 7. Full secp256k1 cost audit

For secp256k1:

```text
n approximately 2^256,
sqrt(n)=2^128,
embedding degree (n-1)/6 approximately 2^253.4,
square-orbit support (n+1)/2 approximately 2^255,
Schrodinger dimension n approximately 2^256,
dense metaplectic matrix n^2 approximately 2^512.
```

Consequently:

1. selecting and pairing with an explicit dual point fails because of the
   enormous extension degree;
2. avoiding the point through the canonical full-dual contraction still leaves
   an `n`-dimensional representation or an `n^2` raw contraction;
3. orthogonality reduces the contraction to the square-orbit incidence count,
   but computing that count is exactly the hidden scalar-Legendre decision;
4. the standard Weil/metaplectic route therefore does not meet
   `O(n^(1/2-epsilon))`.

No preprocessing or advice of size `Omega(sqrt(n))` is admitted as a hidden
solution.

## 8. Frozen exact replay

`quadratic_weil_orientation.py` uses auxiliary finite fields containing
`mu_n` and verifies on the six frozen prime orders

```text
397, 433, 1093, 1249, 3469, 4021
```

all satisfying `n=1 mod 12`:

1. the exact quadratic Gauss scaling law `(W1)`;
2. the square identity `(W2)`;
3. independence of the normalized ratio from every nonzero dual scale;
4. the selector-free contraction `(W4)`;
5. cancellation of the unweighted full-dual trace `(W6)`;
6. the orthogonality/incidence identity `(W7)`;
7. the two exact incidence counts `(W8)`.

The replay performs

```text
31,280,832 dual-scale ratio checks,
10,656 selector-free contraction checks,
10,656 full-dual trace-cancellation checks,
10,656 square-incidence checks.
```

The secp256k1 certificate independently verifies the embedding-degree and
half-Frobenius congruences.

## 9. Answer to the central question

```text
Does a nonzero dual point give an exact normalized Legendre ratio?      yes
Does the ratio depend on the scale of that dual point?                  no
Can the dual-point choice be removed entirely?                          yes
Exact selector-free object                                              C_G(Q)
What does it equal?                                                      n(n-1)chi_n(k)
Equivalent primal object                                                square-orbit incidence count
Does ordinary full trace retain the bit?                                no
Does the standard explicit Weil model pass the sub-sqrt cost gate?      no
Does CM produce an independent public dual point from G?                no
Public classical sub-square-root Legendre evaluator                     absent
Public carry / parity / hard-R3 decoder                                  absent
Unconditional classical sub-square-root ECDLP algorithm                 absent
```

The main positive result is that the dual selector is not the fundamental
obstruction: a canonical selector-free contraction exists. The remaining
obstruction is compact evaluation of that contraction.

## 10. Next object

The successor is

```text
CM-WEIL-TRACE-COMPRESSION-039.
```

Its exact object is

```text
C_G(Q)=sum_(T != O) W_T(Q)W_T(G)=n(n-1)chi_n(k),
```

or equivalently

```text
N_G(Q)=#{(a,b): [a^2]Q+[b^2]G=O}.
```

Central question:

> Does the `j=0` Eisenstein-CM structure provide a compact trace, norm,
> isogeny-kernel, theta, sigma, net, or recurrence formula for `C_G(Q)` or
> `N_G(Q)` with complete classical cost `O(n^(1/2-epsilon))`, without
> materializing the `n`-dimensional Heisenberg representation, enumerating the
> square orbit, constructing the pairing extension, or hiding an oriented table
> in preprocessing?

The theorem-first obligations are:

1. express `C_G(Q)` as a trace or matrix coefficient of the canonical
   Heisenberg-Weil representation;
2. derive its exact CM and Frobenius transformation law;
3. determine whether a sheaf-trace, endomorphism, or ray-class formula reduces
   to a small number of base-field operations;
4. prove nonvanishing and orientation preservation;
5. count representation size, extension degree, coefficient height,
   preprocessing, online operations, memory, and precision;
6. reject any formula that returns only the invariant square or restates the
   scalar-square membership decision;
7. after any compact Legendre oracle, separately establish a literal classical
   sub-square-root shifted-Legendre recovery before claiming an ECDLP
   improvement.

No broad statistical search is admitted without a new exact identity.

## 11. Formalization boundary

`Ecdlp/Proved/QuadraticWeilOrientation.lean` formalizes the elementary
normalization, square-invariance, and selector-free contraction identities. It
does not formalize elliptic curves, Weil pairings, quadratic Gauss sums,
Heisenberg representations, Stone-von Neumann theory, secp256k1 extension
fields, or arithmetic-circuit lower bounds.
