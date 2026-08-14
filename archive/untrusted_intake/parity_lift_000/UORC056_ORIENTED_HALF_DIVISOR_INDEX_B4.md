# UNIFORM-ORIENTED-ROOT-CIRCUIT-056 — ORIENTED HALF-DIVISOR INDEX B4

Date: 2026-08-14

Status: **the parity-oriented half-divisor has a nontrivial order-`n` Picard class, while its even and odd halves have the same Kummer image. Standard square-root Vélu/index-system evaluation is therefore both orientation-blind and, even after an external branch trivialization is supplied, constrained to the square-root work frontier.**

No external point, private key, wallet, unknown scalar, or production-sized discrete-log target is accepted.

## 1. Frozen central target

The target is unchanged:

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k,
Q=[k]G,
```

with total preprocessing, advice, representation, memory, precision, query, and online cost `O(n^(1/2-epsilon))`.

Let

```text
n=2M+1,
H=<G>.
```

The canonical even and odd point sets are

```text
E_G={ [2]G,[4]G,...,[2M]G },
O_G={ [1]G,[3]G,...,[2M-1]G }.
```

Each set contains exactly one point from every pair `{P,-P}`.

## 2. The oriented half-divisor is not principal

Define the degree-zero divisor

```text
Delta_G=sum_(j=1)^M ([2j]G)-sum_(j=1)^M ([(2j-1)]G).       (B4.1)
```

Under the standard identification `Pic^0(E) ~= E`, its class is the group sum of its support coefficients. The scalar sums are

```text
sum_(j=1)^M 2j       =M(M+1),
sum_(j=1)^M (2j-1)  =M^2.
```

Therefore

```text
boxed:
[Delta_G]=[M]G.                                               (B4.2)
```

Since `gcd(M,2M+1)=1`, `[M]G` has exact order `n`. Hence `Delta_G` is not the divisor of a rational function. It is naturally a section problem for the nontrivial order-`n` line bundle

```text
L_G=O_E(Delta_G).                                             (B4.3)
```

To turn `Delta_G` into a principal divisor one must add a compensating pair

```text
(R)-(R+[M]G),                                                 (B4.4)
```

or choose an equivalent trivialization of `L_G`. That choice is additional order-`n` branch data. The standard Miller function for `[M]G` trivializes only `L_G^tensor n`; package B2 shows that its quadratic character remains a relative two-endpoint EDS edge and does not select the absolute orientation.

Under generator replacement `G -> [u]G`, the class becomes `[Mu]G`. In particular `G -> -G` negates the class and the marked root.

## 3. Kummer projection erases the distinction exactly

Negation maps the even labels bijectively onto the odd labels:

```text
-(2j) mod n = 2(M-j)+1.
```

Consequently

```text
boxed:
{ x(P):P in E_G }={ x(P):P in O_G }.                         (B4.5)
```

Both oriented halves project to the same subgroup Kummer kernel

```text
K_H(X)=product_(one pair {P,-P})(X-x(P)).                    (B4.6)
```

This is why standard `x`-only kernel products, Vélu maps, `Frob-id`, resultants, and modular compositions can recover `K_H` or `Y_G^2` but cannot distinguish `Y_G` from `-Y_G`.

## 4. Standard square-root Vélu index systems

The square-root Vélu method evaluates the elliptic polynomial

```text
h_S(X)=product_(s in S)(X-x([s]G))
```

using an index system `(I,J)` and leftover set `K`. The maps

```text
(i,j) -> i+j,
(i,j) -> i-j
```

are injective with disjoint images, and

```text
S=(I+J) union (I-J) union K.
```

Write

```text
a=#I,
b=#J,
c=#K,
W=a+b+c.
```

For a target set of size `M`, coverage gives

```text
M <= 2ab+c.                                                   (B4.7)
```

A direct algebraic inequality gives

```text
2M+1 <= (a+b+c+1)^2.                                         (B4.8)
```

Since `n=2M+1`, every such two-set index architecture satisfies

```text
boxed:
W >= ceil(sqrt(n))-1.                                        (B4.9)
```

For secp256k1,

```text
ceil(sqrt(n))=2^128,
W >= 2^128-1.                                                 (B4.10)
```

Thus the standard square-root Vélu/index-system architecture reaches the generic square-root frontier but cannot satisfy `O(n^(1/2-epsilon))` for fixed positive `epsilon`, even before charging resultant arithmetic, product trees, coefficient representation, or branch extraction.

Primary algorithmic references: Bernstein–De Feo–Leroux–Smith, *Faster computation of isogenies of large prime degree* (ANTS 2020), and subsequent optimal/parallel index-system refinements. Their algorithms compute symmetric elliptic polynomials and isogeny evaluations in soft square-root time; this package applies only the exact index-coverage accounting and the orientation test above.

## 5. Why a signed modification does not evade the gate automatically

A proposed signed variant must solve two separate problems:

1. supply a public trivialization of the order-`n` line bundle `L_G`, rather than merely compute the shared Kummer kernel;
2. evaluate the resulting oriented section below the index-system lower bound.

Supplying one sign for every Kummer pair is a table of size `M`. Supplying a dual point or full order-`n` character re-enters the theta/pairing obstruction. Using the ordinary two-set index system retains the lower bound `(B4.9)`.

This does not exclude a genuinely different high-arity, transposed, or nonlinear circuit. It closes the standard two-set square-root Vélu/resultant representation and any claim that the oriented half is an ordinary principal kernel divisor.

## 6. Frozen exact replay

`uorc056_oriented_half_divisor_index.py` uses the ten frozen cofactor-one prime-order toy curves from B2. It verifies exactly:

1. the point-sum class of `Delta_G` equals `[M]G`;
2. this class is nonzero and has exact order `n`;
3. the even and odd `x`-coordinate multisets agree;
4. the oriented interpolation signature negates under `G -> -G`;
5. every relaxed two-set coverage triple obeys `n <= (W+1)^2`;
6. the optimized relaxed work remains above `ceil(sqrt(n))-1`.

The replay performs no unknown-target discrete-log computation.

## 7. Formalization boundary

`Ecdlp/Proved/OrientedHalfDivisorIndexBoundary.lean` kernel-checks:

```text
M(M+1)-M^2=M,
M<=2ab+c and n=2M+1 => n<=(a+b+c+1)^2.
```

It formalizes the scalar/Picard-class arithmetic and the index-coverage lower bound. It does not formalize Picard schemes, elliptic curves, Vélu resultants, secp256k1, parity recovery, or ECDLP.

## 8. Answer for this B-track class

```text
Is the parity half-divisor principal?                         no
Its Picard class                                               [M]G, exact order n
Do even and odd halves have different Kummer roots?           no; same x-multiset
Can standard x-only square-root Vélu select Y_G?               no
Minimum two-set index work on secp256k1                        2^128-1
Does this meet n^(1/2-epsilon)?                                no
Public parity / absolute EDS oracle                            absent
Sub-square-root ECDLP                                          absent
```

## 9. Remaining B-track mechanisms

The surviving B-track classes are now narrower:

1. a higher-arity index system with a genuinely new multivariate elliptic addition identity and complete sub-square-root resultant cost;
2. transposed modular composition/evaluation not representable by the two-set coverage model;
3. a direct short circuit for a value of the order-`n` line-bundle section without materializing its trivialization;
4. a nonmultiplicative generator-sensitive use of the compact CM endomorphism.

The immediate successor is `UORC056-HIGHER-ARITY-INDEX-B5`, beginning with the question whether a three-set decomposition actually lowers total resultant/intermediate representation cost or merely hides a linear-size multivariate object.
