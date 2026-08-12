# DYADIC-BRANCH-COMPRESSION-043

Date: 2026-08-12

Status: **exact branch-count lower bound for public-halving segment recursions; explicit branch retention reaches the Pollard frontier at depth 128 on secp256k1**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from package 042

Package 042 showed that, on the secp256k1 point-function normalization,

```text
absolute EDS segment primitive
=
public endpoint factor times scalar parity.
```

Therefore a binary divide-and-conquer segment algorithm must solve the same branch problem as canonical scalar halving.

## 2. Exact d-level decomposition

Let

```text
Q=[k]G,
0<=k<n,
```

with `n` odd. For an integer `d>=1`, write

```text
k=2^d q+r,
0<=r<2^d.                                         (D1)
```

Let

```text
u_d=2^(-d) mod n.
```

The point obtained by `d` public group halvings is

```text
H_d=[u_d]Q.
```

Using `(D1)`, its scalar label is

```text
u_d k = q+u_d r mod n.                            (D2)
```

The canonical quotient point is

```text
M_d=[q]G
   =H_d-[u_d r]G.                                 (D3)
```

Thus the only missing information after public halving is exactly

```text
r=k mod 2^d.
```

## 3. The correction branches are distinct

Assume

```text
2^d<n.
```

For residues `0<=r,s<2^d`, if

```text
[u_d r]G=[u_d s]G,
```

then invertibility of `u_d` modulo `n` gives

```text
r=s mod n.
```

The range bound `|r-s|<n` then gives `r=s` as integers.

Therefore the candidate corrections

```text
{[u_d r]G : 0<=r<2^d}
```

are pairwise distinct.

## 4. Exact branch-state lower bound

Consider a declared recursion model in which every state at depth `d` stores one explicit affine correction branch

```text
H_d-[u_d r]G.
```

To be exact for every canonical scalar, the state family must contain the branch for every residue `r mod 2^d`. Since the corrections are distinct, any exact branch encoding is injective on `Fin(2^d)`.

Consequently

```text
number of branch states >= 2^d.                   (D4)
```

This is an exact cardinality theorem. It does not assume randomness or an EDS distribution.

## 5. secp256k1 frontier

For secp256k1:

```text
sqrt(n) ceiling = 2^128.
```

Therefore:

```text
d=64   -> 2^64 explicit branches,
d=96   -> 2^96 explicit branches,
d=128  -> 2^128 explicit branches,
d=129  -> 2^129 explicit branches.
```

An explicit branch-enumerating recursion reaches the Pollard scale at depth 128 and exceeds it immediately afterwards.

This remains true if the states share all branch-independent computation: the lower bound concerns distinct surviving correction labels, not duplicated arithmetic inside each branch.

## 6. Relation to checkpoint and midpoint bounds

`STRUCTURED-SEGMENT-PRIMITIVE-004` proved a checkpoint/walk tradeoff

```text
space * online range >= n.
```

`CANONICAL-MIDPOINT-CIRCULARITY-005` proved that choosing the first correction branch is already parity.

The present package extends those results to all depths:

```text
one bit per level,
2^d exact low-bit branches after d levels.
```

It closes the mechanism class in which uncertainty is represented by an explicit list of affine scalar corrections.

## 7. What the theorem does not close

The result does not exclude a nonlinear compressed state that represents all correction branches without listing them. Examples of possible escape formats include:

1. a high-degree polynomial represented by a short recurrence;
2. a theta/sigma transfer matrix with bounded state dimension;
3. a determinant or resultant whose sign selects the correct branch;
4. a p-adic analytic state with a canonical precision-stable cut;
5. an arithmetic circuit exploiting special `j=0` coordinates.

Such an escape must provide an explicit update law and an extraction theorem for the correct residue. Merely naming the set of branches as one polynomial is not enough; factor selection and total evaluation cost are charged.

## 8. Frozen replay

`dyadic_branch_compression.py` verifies for every odd order from `5` through `127`, every valid depth `d` with `2^d<n`, and every scalar `0<=k<n`:

1. the quotient/remainder decomposition `(D1)`;
2. the public-half correction identity `(D2)`-`(D3)`;
3. pairwise distinctness of all `2^d` corrections;
4. exact recovery of the canonical quotient from the correct residue;
5. failure of every incorrect residue branch;
6. the secp256k1 depth/cost certificate.

## 9. Answer

```text
What remains after d public halvings?                 k mod 2^d
How many explicit corrections are possible?           2^d
Can two corrections merge when 2^d<n?                 no
Explicit branch states required                        at least 2^d
secp depth reaching Pollard scale                       128
Does this exclude nonlinear compression?               no
Public parity / EDS-residue decoder                     absent
Unconditional classical sub-sqrt ECDLP                 absent
```

## 10. Next object

The only surviving version of binary segment recursion is

```text
NONLINEAR-DYADIC-SELECTOR-044.
```

Its central question is:

> Is there an `n`-dependent but succinct polynomial, theta, sigma, determinant, transfer-matrix, or p-adic state that represents the `2^d` dyadic correction branches and extracts the correct residue `k mod 2^d` in total `O(n^(1/2-epsilon))` cost without materializing the branches or importing a parity oracle?

The first theorem-first target should be the smallest nontrivial case `d=1`: classify bounded-state algebraic selectors that distinguish the two public half candidates. Any construction that cannot beat the one-bit case cannot scale to deeper branch compression.

## 11. Formalization boundary

`Ecdlp/Proved/DyadicBranchCompression.lean` formalizes the affine correction identity, injectivity of nonzero scaling, and the branch-cardinality lower bound. It does not formalize elliptic curves, canonical integer representatives modulo `n`, arbitrary shared circuits, secp256k1 point arithmetic, or ECDLP.
