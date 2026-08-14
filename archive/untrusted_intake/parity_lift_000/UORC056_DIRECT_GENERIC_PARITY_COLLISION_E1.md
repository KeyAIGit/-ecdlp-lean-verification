# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track E1: direct generic parity collision boundary

Date: 2026-08-14

Status: **an exact parity evaluator admits a direct generic-group lower bound at
the square-root frontier, without first reducing full DLP to repeated parity
queries. On a prime-order generic cyclic group, every computed element on the
no-collision path has an affine hidden-scalar label. A pair of distinct affine
labels can collide for at most one scalar. Exact parity on the balanced nonzero
scalar domain therefore requires at least `(n-1)/2` exceptional collision
scalars and hence at least `L` labels with `L(L-1) >= n-1`. For secp256k1 the
exact integer threshold is `L = 2^128`.**

No external point, private key, wallet, unknown scalar, or production-sized
discrete-log target is accepted. The executable replay uses only small frozen
prime fields and public secp256k1 integers.

## 1. Central target remains unchanged

Let

```text
H=<G>, |H|=n,
Q=[k]G,
1 <= k < n,
n an odd prime.
```

The target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k
```

with preprocessing, advice, representation, memory, branch work, and online
work all charged inside

```text
O(n^(1/2-epsilon)).
```

The previous generic-boundary package transferred the ordinary generic DLP
lower bound through logarithmically many parity calls. That gives a useful
`Omega(sqrt(n)/log n)` consequence, but it is not tight for the bit problem.
This package analyzes exact parity directly.

## 2. Declared generic model

The algorithm receives generic encodings of

```text
G,
Q=[k]G,
O,
```

and may use public scalar multiplication, group addition and subtraction,
preprocessed generic group elements independent of `k`, equality tests, and
ordinary control flow. It may be adaptive.

Every represented group element has a formal affine label

```text
ell_i(k)=a_i k+b_i mod n.                         (E1.1)
```

This follows inductively:

```text
G             -> 0*k+1,
Q             -> 1*k+0,
ell_i+ell_j   -> (a_i+a_j)k+(b_i+b_j),
-ell_i        -> (-a_i)k-b_i,
[c]ell_i      -> (c*a_i)k+c*b_i.
```

Identical affine forms are deduplicated. Preprocessed generic elements have
`a_i=0` and are included in the total label count.

The model deliberately excludes coordinate arithmetic, field encodings,
Frobenius formulas, CM identities, special `j=0` rational functions, and any
other operation that is absent from a generic cyclic group.

## 3. The no-collision transcript

Fix the internal randomness, if any. Run the algorithm symbolically along the
path where every equality test between two distinct affine forms returns
false, while tests of identical forms return true. Call this the
**no-collision path**.

Suppose this path materializes `L` distinct affine labels. Let `C` be the set of
nonzero scalars `k` for which some two distinct labels on this path evaluate to
the same group element.

For

```text
ell_i(k)=a_i k+b_i,
ell_j(k)=a_j k+b_j,
```

the equality is

```text
(a_i-a_j)k=b_j-b_i.                             (E1.2)
```

Because `n` is prime:

1. if `a_i != a_j`, equation `(E1.2)` has exactly one solution;
2. if `a_i=a_j` and the forms are distinct, it has no solution.

Therefore every unordered label pair contributes at most one exceptional
scalar and

```text
boxed:
|C| <= binom(L,2)=L(L-1)/2.                     (E1.3)
```

For every `k` outside `C`, all actual equality answers agree with the symbolic
no-collision answers. Adaptivity does not change this: the algorithm follows
the same path and returns the same output bit for every `k notin C`.

## 4. Exact parity forces half the scalars into collisions

The canonical nonzero domain

```text
{1,2,...,n-1}
```

contains exactly

```text
M=(n-1)/2 even scalars,
M=(n-1)/2 odd scalars.                            (E1.4)
```

Outside `C`, the no-collision transcript has one fixed output. If `|C|<M`,
then `C` cannot contain every even scalar and cannot contain every odd scalar.
There remain one even and one odd scalar with the same transcript but opposite
required outputs.

Hence exact correctness requires

```text
|C| >= M.                                        (E1.5)
```

Combining `(E1.3)` and `(E1.5)` gives the direct parity bound

```text
boxed:
L(L-1) >= n-1.                                   (E1.6)
```

In particular,

```text
L=Omega(sqrt(n)).                                (E1.7)
```

This bound does not lose the `log n` factor from bit peeling because it treats
parity itself as the decision problem.

## 5. Distributional and randomized corollary

For fixed random coins, let the no-collision path output one parity value.
Among the `n-1` nonzero inputs, at most all `M` inputs of that parity plus every
exceptional collision input can be correct. Thus

```text
Pr[correct]
 <= 1/2 + |C|/(n-1)
 <= 1/2 + L(L-1)/(2(n-1)).                       (E1.8)
```

Averaging over the algorithm's random coins preserves the bound whenever every
run materializes at most `L` labels. Therefore success probability `epsilon`
under a uniform nonzero hidden scalar requires

```text
boxed:
L(L-1) >= (2*epsilon-1)(n-1).                    (E1.9)
```

Equation `(E1.9)` is a distributional consequence in the declared generic
model. The exact lower bound `(E1.6)` is the main result.

## 6. Full-cost interpretation

A new generic label must be present in at least one charged place:

```text
preprocessed generic storage,
advice containing generic encodings,
represented memory,
or an online group-operation result.
```

Sequentially discarding labels does not avoid the operation count needed to
create them. Retaining many labels moves the same burden into memory or advice.
Thus, when the 056 full-cost ledger charges all generic labels and operations,
`(E1.6)` gives

```text
boxed:
C_preprocessing+C_advice+C_memory+C_online
 =Omega(sqrt(n))                                 (E1.10)
```

for this generic mechanism class.

The theorem does not claim that an arbitrary advice bit is a group label. It
claims only that advice independent of `Q` cannot make the no-collision
transcript depend on `k`; any generic encodings it supplies must be included in
`L`. Advice exploiting concrete encoding bits is non-generic and outside the
model.

## 7. Exact secp256k1 certificate

For

```text
n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
```

the least integer `L` satisfying `(E1.6)` is exactly

```text
boxed:
L=2^128
 =340282366920938463463374607431768211456.        (E1.11)
```

The executable certificate checks both sides:

```text
(2^128-1)(2^128-2) < n-1,
2^128(2^128-1)     >= n-1.                       (E1.12)
```

Therefore an exact generic parity evaluator reaches the ordinary 128-bit
collision frontier directly. No additional factor of 256 is hidden in this
statement.

## 8. Cross-track integration

### Track A

An endpoint-segment primitive that uses only generic group operations and local
edge equality information cannot beat `(E1.6)`. A positive endpoint primitive
must exploit coordinate structure not present in affine labels.

### Track B

B13-B15 reduce the alternating Miller edge, cyclic elliptic factorial, and
Hilbert-90 lift to one distinguished global integration problem. E1 shows that
integrating this object by a generic collision strategy cannot improve the
square-root exponent. The compact local Miller cocycle is useful only if its
coordinate/function-field structure enables a non-generic global operation.

### Track C

Track C correctly leaves high-degree nonlinear coordinate circuits open.
E1 does not touch them. In particular, the translated quarter-kernel,
polynomial-Pell factor, finite-etale branch, and any direct field-coordinate
circuit remain outside the generic model.

The navigation consequence is exact:

```text
another generic Pollard/BSGS/checkpoint/collision reformulation is closed;
the surviving route must use genuinely non-generic secp256k1 structure.       (E1.13)
```

## 9. Frozen exact replay

The executable

```text
experiments/parity_lift_000/uorc056_direct_generic_parity_collision.py
```

uses frozen prime orders

```text
7,11,13,17,19,23,31.
```

For every order it exhausts every unordered pair among all affine forms
`a*k+b` and verifies exactly:

1. distinct slopes give one and only one collision scalar;
2. equal slopes with distinct intercepts never collide;
3. nonzero canonical parity classes are balanced;
4. the least integer `L` satisfying `(E1.6)` is minimal.

Aggregate replay totals:

```text
frozen orders                                  7
affine forms                               2,479
unordered distinct form pairs            730,164
unique collision solutions verified      702,603
all exact checks                              true
```

The same executable records the exact public secp256k1 threshold `(E1.11)`.
It performs no elliptic-curve discrete-log computation.

## 10. Formalization boundary

The Lean file

```text
Ecdlp/Proved/DirectGenericParityCollisionBoundary.lean
```

kernel-checks:

1. uniqueness of an affine collision over a field when the slopes differ;
2. the elementary implication from collision coverage to a square label bound;
3. the odd-order arithmetic reduction;
4. the exact secp256k1 threshold inequalities by native decision.

Lean does not formalize an oracle machine, adaptive generic encodings, the
no-collision transcript, randomized algorithms, coordinate circuits, or ECDLP.
Those model connections are stated explicitly in this memo.

## 11. Decision

```text
Direct exact generic parity lower bound                    Omega(sqrt(n))
Logarithmic parity-to-DLP loss needed?                     no
Exact secp256k1 generic label threshold                    2^128
Generic endpoint/global integration below sqrt(n)         excluded
Coordinate/CM/function-field evaluator excluded?          no
Public parity oracle                                      absent
Classical sub-square-root ECDLP                            absent
```

## 12. Next admitted constructive target

The generic boundary is now tight enough for navigation. The next useful work
must attack one concrete non-generic operation, not another collision schedule.
The highest-value surviving target is:

```text
DISTINGUISHED-PELL-FACTOR-SINGLE-VALUE-EVALUATION-E2
```

Given the public compact norm data and one public query `Q`, evaluate only

```text
A(x(Q)):B(x(Q))
```

for the distinguished generator-oriented solution of

```text
A^2-(X^3+7)B^2=c_G K_H(X)(X-x(S_G)),
```

without constructing `K_H`, `A`, `B`, an order-`n` orbit state, a square-root
width product, or a hidden dual character. Any positive mechanism must identify
the precise coordinate/CM resource that invalidates the affine-label model
above.
