# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track B16: Hilbert-90 displacement and orbit-polynomial boundary

Date: 2026-08-14

Status: **a first-order cyclic recurrence and a low-sparsity cyclic bidiagonal
matrix do not by themselves compress the distinguished Hilbert-90 potential.
Every nonzero projective orbit vector admits such a recurrence. On every frozen
outside coset, the canonical oriented factor has full base-field linear
complexity and a dense orbit polynomial. Standard displacement-rank,
constant-coefficient recurrence, orbit-polynomial, and explicit adjugate routes
therefore remain linear-state mechanisms. No strict sub-square-root evaluator
is obtained.**

No external point, private key, wallet, unknown scalar, or production-sized
DLP target is accepted. Executable checks use only fixed toy curves and all
fixed public cosets outside their declared subgroups.

## 1. Central target is unchanged

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with preprocessing, advice, representation, memory, branch selection,
normalization, and online work charged inside

```text
O(n^(1/2-epsilon)).
```

B13-B15 give a compact local cocycle

```text
h_i=F_(i+1)/F_i
```

for the distinguished generator-oriented global potential `F`, but the standard
Hilbert-90 lift and endpoint/factorial representations contain `n` orbit
entries. B16 tests whether the sparse cyclic recurrence matrix, its low
structural description, a short constant-coefficient recurrence, or a sparse
orbit polynomial compresses the required vector.

## 2. A sparse first-order recurrence is universal

Let `K` be a field or commutative group and let

```text
v=(v_0,...,v_(n-1)) in (K^*)^n.
```

Define

```text
h_i=v_(i+1)/v_i,
```

with indices modulo `n`. Then

```text
v_(i+1)=h_i v_i,
product_i h_i=1.                                  (B16.1)
```

Conversely, every norm-one cocycle together with one nonzero anchor reconstructs
one projective vector by cumulative products.

Therefore the class of cyclic bidiagonal systems

```text
v_(i+1)-h_i v_i=0                                (B16.2)
```

contains every nonzero projective vector. The matrix has only `2n` nonzero
entries, but its one-dimensional kernel can be an arbitrary dense vector.
Low matrix sparsity or low displacement rank alone is not a compression theorem
for the kernel vector.

This is an exact abstract obstruction to arguments of the form

```text
sparse cyclic recurrence matrix
  => automatically short distinguished solution.
```

It does not exclude additional arithmetic structure in the particular Miller
cocycle.

## 3. Gauge and quotient-field ambiguity

If two nonzero potentials `F` and `G` have the same local cocycle, then

```text
F_(i+1)/G_(i+1)=F_i/G_i.                          (B16.3)
```

Hence their ratio is invariant along the translation orbit. On one coset this
is one scalar; globally it is a function pulled back from the quotient curve.
The local recurrence does not select the distinguished divisor normalization.

## 4. Full frozen linear complexity

For each fixed outside coset, let

```text
s_i=f_G(R+[2i]G),  0<=i<n,
```

where `f_G` is the exact B7A principal factor. The replay computes the minimal
constant-coefficient linear recurrence over the base field by
Berlekamp-Massey on repeated periods.

For every outside coset in the five frozen curves, the exact linear complexity
is

```text
boxed: L(s)=n.                                    (B16.4)
```

Thus no constant-coefficient base-field recurrence of order `<n` generates any
of these frozen potential sequences.

This is exhaustive for the declared toy cosets, not an asymptotic theorem for
secp256k1.

## 5. Dense orbit polynomial

For each coset form

```text
P_R(Z)=product_(i=0)^(n-1) (Z-s_i).               (B16.5)
```

Every coefficient of every frozen `P_R` is nonzero. Thus the direct
characteristic-polynomial/minimal-polynomial specialization is dense in all
retained cases.

A quotient-field orbit polynomial may still have a different symbolic
representation. B16 closes only explicit coefficient extraction and any claim
that sparsity is already visible in the standard specializations.

## 6. Exact recurrence matrix replay

The matrix of `(B16.2)` has rows

```text
-h_i at column i,
+1   at column i+1 mod n.
```

For every frozen outside coset the replay verifies:

1. cyclic norm one;
2. matrix nullity exactly one;
3. the kernel vector is proportional to the canonical factor-value vector;
4. every kernel coordinate is nonzero;
5. Berlekamp-Massey complexity exactly `n`;
6. all `n+1` orbit-polynomial coefficients are nonzero.

The corpus contains all `13` outside cosets and `285` outside-coset points from
five fixed curves.

## 7. Consequence for standard trace/circulant compression

The following mechanisms remain linear-state in the declared representation:

```text
explicit orbit vector,
explicit normal basis,
explicit trace row,
explicit cyclic adjugate/kernel vector,
constant-coefficient recurrence,
explicit orbit polynomial.
```

A fast algorithm must exploit a nonlinear identity specific to the Miller/CM
cocycle and must output the distinguished oriented value without materializing
any of these length-`n` states.

## 8. Formalization boundary

`Ecdlp/Proved/Hilbert90DisplacementBoundary.lean` kernel-checks:

1. every nonzero potential produces a first-order cocycle;
2. the cocycle recurrence holds identically;
3. constant rescaling leaves the cocycle unchanged;
4. equal cocycles imply an invariant pointwise ratio.

It does not formalize elliptic curves, Berlekamp-Massey, quotient fields,
Miller functions, secp256k1, parity recovery, or ECDLP.

## 9. Decision

```text
Compact first-order local recurrence                     yes
Does recurrence sparsity restrict the projective vector? no
Frozen base-field recurrence order                       n on all cosets
Frozen orbit-polynomial coefficients                     all nonzero
Standard linear/displacement compression                 linear state
Public parity oracle                                     absent
Strict sub-square-root evaluator                         absent
```

## 10. Immediate successor

The next nonduplicative B mechanism is the polynomial-Pell representation from
B7A. The symmetric equation has two conjugate oriented factors. A public
condition at the marked generator selects the correct sign. The next package
must determine whether half-gcd, subresultant, Padé, or rational-reconstruction
methods can evaluate only

```text
-y(Q) B(x(Q))/A(x(Q))
```

without materializing the degree-`Theta(n)` Pell solution, and must charge any
oriented modular-square-root seed supplied to those algorithms.