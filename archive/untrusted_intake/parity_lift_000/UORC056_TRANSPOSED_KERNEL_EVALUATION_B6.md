# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — TRANSPOSED KERNEL EVALUATION B6

Date: 2026-08-14

Status: **transposed evaluation does not remove the orientation input. In the public translation algebra, canonical parity is the unique solution of one sparse cyclic equation, but the inverse of that equation is the dense alternating polynomial with all `n` translation powers. Sparse Krylov/translation-polynomial and explicit transposed interpolation representations therefore do not yield a sub-square-root evaluator.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Frozen central target

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with all-in cost `O(n^(1/2-epsilon))`.

Packages B4-B5 close explicit square-root Vélu and hierarchical index/resultant representations. B6 asks whether transposition or black-box linear evaluation can compute one value without constructing the large oriented polynomial.

## 2. Translation-operator formulation

Extend canonical parity to the full scalar cycle by

```text
a(k)=(-1)^k,
0<=k<n.
```

Let `T` be the forward translation operator on functions on `Z/nZ`:

```text
(Tf)(k)=f(k+1 mod n).
```

For `0<=k<n-1`, parity flips:

```text
a(k+1)+a(k)=0.
```

At the single wrap point, since `n-1` is even,

```text
a(0)+a(n-1)=2.
```

Therefore

```text
boxed:
(I+T)a=2 delta_(n-1).                                      (B6.1)
```

This is the exact linear form of the generator-oriented branch cut.

## 3. The inverse is dense

For every `n`, the geometric identity is

```text
(1+X) sum_(j=0)^(n-1) (-X)^j = 1-(-X)^n.                  (B6.2)
```

When `n` is odd and `T^n=I`, this becomes

```text
(I+T) sum_(j=0)^(n-1) (-T)^j = 2I.                        (B6.3)
```

Hence

```text
boxed:
a=sum_(j=0)^(n-1) (-T)^j delta_(n-1).                     (B6.4)
```

All `n` coefficients are nonzero. Moreover the vectors

```text
T^j delta_(n-1), 0<=j<n,
```

are the standard basis of the regular permutation representation. Therefore the coefficient vector in `(B6.4)` is unique and has exact support `n`.

A sparse polynomial in the public translation operator cannot represent parity. Ordinary Krylov, sparse companion, or transposed algorithms that materialize this translation-polynomial coefficient vector require linear state.

## 4. Relation to transposed interpolation of Y_G

The interpolation data for `Y_G` consists of the `M=(n-1)/2` pairs

```text
x_j=x([j]G),
y_j^or=(-1)^j y([j]G).
```

A transposed multipoint algorithm can accelerate a known linear map between:

```text
oriented sample values,
coefficient vector of Y_G,
one evaluation functional.
```

It does not construct the oriented sample vector. Replacing `G` by `-G` keeps `K_H` and every interpolation node `x_j` fixed while negating every `y_j^or` and the requested output.

Thus an algorithm whose preprocessing contains only

```text
K_H,
K_H derivatives,
Frob-id,
generator-blind product/remainder trees,
```

has identical input state for `G` and `-G` and cannot output both values correctly.

If the oriented sample vector or the coefficients of `Y_G` are supplied, their representation has `M` field elements. Transposition changes evaluation direction, not the amount of branch information supplied.

## 5. Why fast geometric-series syntax is not yet an algorithm

Formula `(B6.4)` can be written recursively by doubling geometric sums. But a recursive expression such as

```text
S_(2m)=S_m+(-T)^m S_m
```

only helps if the segment state `S_m delta` has a compact public representation and can be evaluated without expanding its support. Constructing such a state is exactly the endpoint-segment problem assigned to track A.

Consequently B6 does not claim a lower bound against every shared segment circuit. It proves that ordinary sparse/transposed linearization alone is not the missing compression.

## 6. Frozen exact replay

`uorc056_transposed_kernel_evaluation.py` checks the frozen odd prime orders from B4-B5. For every order it verifies:

1. `(I+T)a` has exactly one nonzero coordinate, equal to `2`;
2. the dense alternating inverse reconstructs every parity value;
3. all `n` translation powers occur with nonzero coefficient;
4. shifted delta vectors are distinct basis vectors;
5. deleting any one coefficient changes the reconstructed function.

The secp256k1 certificate records support size `n`, coefficient bit length, and the distinction between dense linear inversion and an unproved compressed segment circuit.

## 7. Formalization boundary

`Ecdlp/Proved/TransposedKernelEvaluationBoundary.lean` kernel-checks the alternating geometric identity and the ordinary non-wrap parity flip. It does not formalize elliptic curves, quotient algebras, transposition algorithms, secp256k1, parity-to-DLP recovery, or ECDLP.

## 8. Answer for this B-track class

```text
Does parity satisfy a sparse public linear equation?             yes
Equation                                                         (I+T)a=2 delta_cut
Is the inverse translation polynomial sparse?                    no; support n
Does transposition create the oriented sample vector?            no
Does generator-blind modular composition distinguish G,-G?       no
Public parity / absolute EDS oracle                               absent
Sub-square-root ECDLP                                             absent
```

## 9. Remaining B-track mechanisms

The B track is now reduced to mechanisms that are not ordinary kernel products, explicit resultants, or sparse translation-polynomial evaluation:

1. a genuinely compact endpoint-segment state shared with track A;
2. a nonlinear CM recurrence whose state does not expand with the divisor support;
3. direct black-box evaluation of the order-`n` line-bundle section with a new public orientation invariant;
4. a special sparse multivariate resultant with proved sub-square-root evaluation and no hidden large state.

The immediate B successor is `UORC056-CM-RECURRENCE-STATE-B7`: classify whether the compact Eisenstein endomorphism gives a finite-state recurrence for the oriented section rather than for its generator-blind norm.
