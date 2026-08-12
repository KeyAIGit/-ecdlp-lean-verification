# CM-WEIL-TRACE-COMPRESSION-039

Date: 2026-08-12

Status: **the selector-free quadratic-Weil contraction compresses exactly to one hidden split-torus Weil-character value; standard generic CM/Frobenius computation of that hidden torus coordinate still has a square-root lower bound**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Input from package 038

Let

```text
H=<G>, |H|=n,
Q=[k]G,
```

with `n` an odd prime and, for the secp256k1 branch, `n=1 mod 12`.
Package 038 defined quadratic Weil values

```text
W_T(P)=sum_(a mod n) e_n([a^2]P,T)
```

on a complementary torsion line and proved the selector-free identity

```text
C_G(Q)=sum_(T != O) W_T(Q)W_T(G)=n(n-1)chi_n(k).      (C1)
```

It also identified the primal incidence count

```text
N_G(Q)=#{(a,b): [a^2]Q+[b^2]G=O},
```

which equals `2n-1` for square `k` and `1` for nonsquare `k`.

The present package asks whether the apparent `n`- or `n^2`-dimensional trace can be compressed by the split CM/Frobenius torus.

## 2. The hidden split-torus element

Over `F_n`, write the symplectic torsion space as

```text
V=H direct_sum H_dual.
```

Frobenius acts with distinct eigenvalues

```text
Frob|H=1,
Frob|H_dual=p mod n.
```

For every nonzero `Q=[k]G`, there is a unique symplectic automorphism `A_(G,Q)` satisfying

```text
A_(G,Q) commutes with Frobenius,
A_(G,Q)(G)=Q.
```

Indeed, commutation with Frobenius forces the matrix to be diagonal in the two eigenspaces, and the symplectic condition forces reciprocal eigenvalues. Thus

```text
A_(G,Q)=diag(k,k^(-1)).                            (C2)
```

The same element commutes with the diagonalized `j=0` CM action. It is the hidden element of the norm-one split CM torus corresponding to the scalar multiplier `k`.

The element is canonical as an abstract automorphism. Computing its scalar matrix entry from encoded points is precisely the missing hidden-torus-coordinate problem.

## 3. Compression to one Weil-character value

In the standard Schroedinger model of the finite Weil representation, the split-torus element

```text
d_k=diag(k,k^(-1))
```

acts, up to the standard fixed normalization, as

```text
rho(d_k)f(x)=chi_n(k) f(k^(-1)x).
```

For `k != 1`, multiplication by `k^(-1)` fixes only `x=0`, so

```text
Tr rho(d_k)=chi_n(k).                              (C3)
```

The case `k=1` is publicly recognizable from `Q=G`; the identity operator has trace `n`, while `chi_n(1)=1`.

Combining `(C1)` and `(C3)`, for `Q != G`,

```text
C_G(Q)=n(n-1) Tr rho(A_(G,Q)).                    (C4)
```

Thus the huge selector-free contraction is not intrinsically an `n^2`-term object. Abstractly it is one character value of one hidden split-torus element.

This is the principal positive result of the package.

## 4. Choice-free determinant and Maslov interpretation

For `k != 1`,

```text
det(A_(G,Q)-I)
 =(k-1)(k^(-1)-1)
 =-(k-1)^2/k.                                    (C5)
```

Since `n=1 mod 4` on secp256k1, `chi_n(-1)=1`, and therefore

```text
chi_n(det(A_(G,Q)-I))=chi_n(k).                  (C6)
```

Choice-free character formulae for finite Weil representations express their character through a Weil index or Maslov-type quadratic form attached to the graph of the symplectic transformation. In the present two-dimensional split-torus case, `(C5)` is the elementary square-class content of that formula.

This does not yet give an evaluator: the determinant is easy once the hidden torus element is represented, but deriving that representation from `(G,Q)` is the unresolved step.

## 5. The graph is canonical but its orientation is hidden

The rational-eigenline part of the graph of `A_(G,Q)` is the public line

```text
span((G,Q)) inside H direct_sum H.
```

Frobenius stability and the Lagrangian condition uniquely determine the complementary dual-eigenline part of the full graph. Hence the full graph is mathematically determined without selecting a dual point.

Nevertheless, evaluating its Maslov/Weil square class requires comparing the bases `G` and `Q` on the same one-dimensional `F_n`-line. That comparison scalar is `k`; its quadratic class is exactly the desired output.

So graph completion removes a choice but not the computational bottleneck.

## 6. Generic CM/Frobenius lower bound

Consider a classical generic-group computation starting from encodings of

```text
G  <->  1,
Q  <->  k,
```

and allowing:

```text
group addition and subtraction,
known scalar multiplication,
known GLV/CM endomorphisms,
Frobenius,
equality tests.
```

On the rational subgroup, every computed element has an affine scalar label

```text
ell_i(k)=a_i k+b_i.
```

Known CM and Frobenius operations only change the known coefficients; they do not create nonlinear dependence on `k`.

For two distinct affine labels, a collision

```text
ell_i(k)=ell_j(k)
```

occurs for at most one value of `k`. If `m` distinct affine labels have been produced, the union of all possible collision values has size at most

```text
binom(m,2).                                       (C7)
```

Away from this collision set, the generic encoding transcript is identical up to a random relabeling and therefore cannot depend on the quadratic class of `k`.

The nonzero squares and nonsquares each have size `(n-1)/2`. An exact generic decoder must force at least one whole class into the exceptional collision set, so

```text
binom(m,2) >= (n-1)/2,

m(m-1) >= n-1.                                   (C8)
```

Consequently

```text
m=Omega(sqrt(n)).                                 (C9)
```

For secp256k1 the smallest integer satisfying `(C8)` is exactly

```text
2^128.
```

This is a scoped Shoup-style bound for the generic CM/Frobenius model. It does not apply to an encoding-sensitive coordinate, ray-class, theta, sigma, or arithmetic-circuit identity that exploits special `j=0` structure beyond generic group operations.

## 7. What CM trace compression does and does not accomplish

```text
Huge contraction C_G(Q)                         compressed exactly
Compressed object                               Weil character of A_(G,Q)
Hidden information                              chi_n(k)
Trace evaluation given matrix of A_(G,Q)        constant-size
Construction of A_(G,Q) from G,Q generically    Omega(sqrt(n))
Kernel-only CM data                              independent of Q orientation
Public sub-square-root Legendre evaluator        absent
Public carry / parity / hard-R3 decoder          absent
Classical sub-square-root ECDLP algorithm        absent
```

The trace formula changes the location of the bottleneck. It does not remove it.

## 8. Frozen replay

`cm_weil_trace_compression.py` verifies on the frozen prime orders

```text
397, 433, 1093, 1249, 3469, 4021
```

all satisfying `n=1 mod 12`:

1. the exact split-torus Schroedinger trace law;
2. the determinant square-class identity `(C5)`-`(C6)`;
3. commutation with the order-three GLV action;
4. equality between the normalized selector-free contraction and the reduced Weil character;
5. the affine-collision union bound on frozen deterministic transcript families;
6. the exact secp256k1 threshold `m=2^128` from `(C8)`;
7. the previously certified embedding-degree obstruction.

The replay is a scalar-model certificate. It is not an implementation of a production-size Weil representation or an attack on any external point.

## 9. Answer to the central question

```text
Can C_G(Q) be compressed abstractly?                         yes
Exact compressed object                                     Tr rho(A_(G,Q))
Does the full dual-line selector remain necessary?           no
Is A_(G,Q) uniquely determined by G,Q,Frobenius?             yes
Can its character be read from det(A-I)?                     yes, once A is represented
Does generic CM/Frobenius arithmetic construct A sub-sqrt?   no, scoped Omega(sqrt(n)) bound
Does a nongeneric j=0 coordinate/ray-class formula remain?   open
Public classical sub-sqrt Legendre evaluator                 absent
Public parity / carry / hard-R3 decoder                      absent
Unconditional classical sub-sqrt ECDLP                       absent
```

## 10. Next object

The successor is

```text
CM-RAY-CLASS-TORUS-ORIENTATION-040.
```

Its exact target is the quadratic character of the hidden norm-one CM torus element

```text
A_(G,Q)=diag(k,k^(-1)).
```

Central question:

> Can the `j=0` CM coordinate encoding of the marked torsion points `(G,Q)` evaluate the quadratic character of the hidden norm-one torus element through an explicit ray-class symbol, elliptic unit, Weber/Siegel function, theta quotient, or reciprocity law with complete classical cost `O(n^(1/2-epsilon))`, thereby escaping the generic affine-label lower bound?

The theorem-first obligations are:

1. identify the split CM algebra `O_K/n ~= F_n x F_n` and its norm-one torus;
2. express the marked-point change `G -> Q` as an Artin/ray-class action without assuming `k`;
3. find a coordinate function whose transformation character is the quadratic character of that torus;
4. reject every function that depends only on the unmarked kernel or returns an invariant square/norm;
5. count ray-class degree, modular degree, coefficient height, preprocessing, memory, precision, and online work;
6. prove a literal sub-square-root evaluation algorithm or a scoped representation obstruction;
7. even after a Legendre oracle, separately analyse classical shifted-Legendre recovery before making an ECDLP claim.

No broad statistical search is admitted without a new exact reciprocity identity.

## 11. Formalization boundary

`Ecdlp/Proved/CmWeilTraceCompression.lean` formalizes the split-torus determinant identity, uniqueness ingredients for the Frobenius-diagonal completion, affine-collision uniqueness, and normalized contraction algebra. It does not formalize the full Weil representation, the generic-group probability space, Maslov indices, CM ray class fields, secp256k1 coordinates, or arithmetic-circuit lower bounds.
