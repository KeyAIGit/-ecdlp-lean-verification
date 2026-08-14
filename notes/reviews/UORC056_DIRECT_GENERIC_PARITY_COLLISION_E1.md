# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track E1: direct generic parity collision boundary

Date: 2026-08-14

Status: **exact parity has a direct square-root generic-group lower bound. The
proof does not first recover the full discrete logarithm and therefore loses no
factor of `log n`. With `S` stored generic labels and `T` online labels, exact
parity requires `T(2S+T-1) >= n-1`; the total charged label count remains at
least the square-root scale. For secp256k1, without stored labels, the exact
integer threshold is `2^128`.**

No external point, private key, wallet, unknown scalar, or production-sized
discrete-log target is accepted. The executable replay uses only frozen small
prime fields and public secp256k1 integers.

## 1. Frozen target

Let

```text
H=<G>, |H|=n,
Q=[k]G,
1 <= k < n,
n an odd prime.
```

The central target remains

```text
A(E,G,Q)=Y_G(x(Q))/y(Q)=(-1)^k
```

with preprocessing, advice, representation, memory, branch work, and online
work charged inside `O(n^(1/2-epsilon))`.

The earlier package transferred a full-DLP generic lower bound through repeated
parity queries. E1 treats parity itself as the decision problem.

## 2. Declared generic model

The algorithm receives generic encodings of `G`, `Q=[k]G`, and `O`. It may use
public scalar multiplication, group addition and subtraction, preprocessed
generic group elements independent of `k`, equality tests, adaptive control
flow, and internal randomness.

On any fixed deterministic execution path, every represented group element has
a formal affine hidden-scalar label

```text
ell_i(k)=a_i*k+b_i mod n.                         (E1.1)
```

This is preserved by all generic group operations. Identical affine forms are
deduplicated. Preprocessed generic elements have slope zero.

Coordinate arithmetic, Frobenius formulas, CM identities, field encodings,
`j=0` rational functions, and other non-generic operations are outside this
model.

## 3. No-collision transcript

Fix the algorithm's random coins. Follow the symbolic path on which every
equality test between two distinct affine forms returns false. Suppose this
path materializes `L` distinct affine labels.

For two distinct labels

```text
ell_i(k)=a_i*k+b_i,
ell_j(k)=a_j*k+b_j,
```

a collision satisfies

```text
(a_i-a_j)k=b_j-b_i.                              (E1.2)
```

Because `n` is prime, distinct slopes give exactly one solution and equal
slopes with different intercepts give none. Therefore the set `C` of scalars
that cause any collision on the symbolic path satisfies

```text
|C| <= binom(L,2)=L(L-1)/2.                      (E1.3)
```

For every `k` outside `C`, the actual algorithm follows the same no-collision
path and returns the same output bit.

## 4. Direct exact parity bound

The nonzero canonical scalars `1,...,n-1` contain exactly `(n-1)/2` even values
and `(n-1)/2` odd values. If `|C|<(n-1)/2`, one even and one odd scalar remain
outside `C`; they have the same transcript but require opposite outputs.

Thus exact parity requires

```text
|C| >= (n-1)/2.                                  (E1.4)
```

Together with `(E1.3)`:

```text
boxed:
L(L-1) >= n-1.                                   (E1.5)
```

Hence an exact generic parity evaluator needs `Omega(sqrt(n))` distinct generic
labels or corresponding generic operations. No logarithmic parity-to-DLP loss
is needed.

For uniform nonzero `k`, a fixed random tape obeys

```text
success <= 1/2 + L(L-1)/(2(n-1)).                (E1.6)
```

Averaging over random coins preserves the same bound when every run has the
same label cap.

## 5. Preprocessing versus online tradeoff

Separate the no-collision labels into

```text
S stored labels, independent of k,
T online labels, possibly affine in k.
```

Pairs of two stored labels cannot create a hidden-scalar exception. At most
`S*T` stored-online pairs and `binom(T,2)` online-online pairs can do so. Exact
parity therefore requires

```text
S*T + T(T-1)/2 >= (n-1)/2,
```

or equivalently

```text
boxed:
T(2S+T-1) >= n-1.                                (E1.7)
```

This is the direct generic preprocessing-online tradeoff for this decision
problem. It allows online work to decrease only by paying for stored generic
encodings. Moreover `(E1.7)` implies

```text
boxed:
(S+T)^2 >= n-1.                                  (E1.8)
```

Thus the complete charged label count remains on the square-root scale even
when preprocessing and online work are separated.

Representative secp256k1 points on the exact tradeoff curve are recorded by the
frozen certificate. For example:

```text
S=0       requires T=2^128,
S=2^128   still requires about 0.4142*2^128 online labels,
S=2^192   requires T=2^63,
S=2^224   requires T=2^31,
S=2^255   can reduce T to 1, but storage is already enormous.
```

## 6. Exact secp256k1 threshold

For

```text
n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
```

the least `L` satisfying `(E1.5)` is exactly

```text
L=2^128
 =340282366920938463463374607431768211456.        (E1.9)
```

The public integer certificate verifies

```text
(2^128-1)(2^128-2) < n-1,
2^128(2^128-1)     >= n-1.                       (E1.10)
```

So exact generic parity reaches the ordinary 128-bit collision frontier
directly.

## 7. Cross-track consequence

Track A endpoint integration cannot improve the exponent if it uses only
generic group labels, equality transcripts, or checkpoint collisions.

Track B packages B13-B15 identify alternating Miller integration, cyclic
elliptic factorial evaluation, and the Hilbert-90 lift as the same global
orientation problem. E1 closes a generic collision implementation of that
integration, but not a function-field or coordinate-specific one.

Track C remains open exactly where it should: translated quarter-kernel
formulas, polynomial-Pell factors, finite-etale branch extraction, Frobenius,
CM, and nonlinear field-coordinate circuits are not represented by affine
generic labels.

The navigation result is therefore:

```text
Pollard, BSGS, checkpoint, and generic collision reformulations are closed;
a positive route must use genuine non-generic secp256k1 structure.            (E1.11)
```

## 8. Frozen replay

The executable

```text
experiments/parity_lift_000/uorc056_direct_generic_parity_collision.py
```

uses prime orders `7,11,13,17,19,23,31`. It verifies:

1. every distinct-slope affine pair has exactly one collision;
2. every parallel distinct pair has none;
3. nonzero parity classes are balanced;
4. the exact label threshold is minimal;
5. forty frozen preprocessing-online thresholds are minimal;
6. every tested tradeoff point satisfies the total square bound;
7. the exact secp256k1 threshold and representative preprocessing examples.

Aggregate frozen totals:

```text
orders                                          7
affine forms                                2,479
unordered distinct form pairs             730,164
unique collision solutions                702,603
preprocessing-online checks                    40
all exact checks                              true
```

No elliptic-curve discrete-log computation is performed.

## 9. Formalization boundary

`Ecdlp/Proved/DirectGenericParityCollisionBoundary.lean` kernel-checks:

1. uniqueness of an affine collision over a field;
2. collision coverage implies a square label bound;
3. preprocessing-online coverage implies a total square bound;
4. the odd-order arithmetic specialization;
5. the exact secp256k1 threshold inequalities.

Lean does not formalize adaptive oracle machines, randomized transcripts,
coordinate circuits, or ECDLP. Those model connections remain explicit premises
of this scoped theorem.

## 10. Decision

```text
Direct exact generic parity lower bound                    Omega(sqrt(n))
Logarithmic bit-peeling loss needed?                       no
Preprocessing-online condition                             T(2S+T-1)>=n-1
Full charged label condition                               (S+T)^2>=n-1
Exact secp256k1 no-preprocessing threshold                 2^128
Coordinate/CM/function-field evaluator excluded?           no
Public parity oracle                                      absent
Classical sub-square-root ECDLP                            absent
```

## 11. Next constructive target

The next admitted target is not another generic collision schedule. It is
single-value evaluation of the distinguished generator-oriented Pell factor:

```text
A^2-(X^3+7)B^2=c_G*K_H(X)*(X-x(S_G)).
```

Given public `(E,G,Q)`, evaluate only `A(x(Q)):B(x(Q))` without constructing
`K_H`, `A`, `B`, an order-`n` translation state, a square-root-width product,
or a hidden dual character. A successful mechanism must identify the concrete
coordinate or CM resource that invalidates the affine-label model above.
