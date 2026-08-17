# UORC-056 C52 contract: nonhorizontal deformation gauge

Date: 2026-08-17

Status: successor research contract. No parity evaluator is claimed.

## 1. Input from C51

C51 proves that differentiation only in the elliptic point coordinate does not expose the canonical scalar lift. The quasiperiod term cancels, the first derivative reduces to periodic regularized torsion jets, and the second and third derivatives reduce to public coordinates.

Therefore a surviving differential mechanism must vary the gauge itself.

## 2. Exact question

Construct a public one-parameter family

\[
(E_t,G_t,Q_t,\nabla_t)
\]

such that

\[
Q_t=[k]G_t
\]

for the same hidden canonical scalar, without supplying \(k\), its digits, a dual phase, or an oriented root as deformation data.

Determine whether a derivative of an elliptic-net, sigma, theta, Miller, or Kummer section in this nonhorizontal direction yields a field state from which

\[
(-1)^k
\]

is decoded in complete \(O(n^{1/2-\varepsilon})\) cost.

## 3. Mandatory separation of cases

C52 must distinguish:

1. horizontal torsion transport, where prime-to-characteristic torsion is locally constant and C51 applies;
2. arbitrary motion of \(G\), where preserving \(Q=[k]G\) may require tangent data multiplied by the hidden \(k\);
3. curve or moduli deformation with a specified Gauss-Manin or p-adic connection;
4. change of sigma or theta trivialization, where the derivative may only report a chosen gauge;
5. genuine functorial deformation whose input is computable from \((E,G,Q)\) alone.

## 4. Rejection gates

Reject a candidate if:

```text
its tangent input explicitly contains k or [k] acting on a hidden vector;
its connection is selected by an uncharged period or dual basis;
its derivative is another ordinary elliptic function of public points;
its result is invariant under the component sign gauge;
its branch is fixed by advice;
its p-adic or extension precision reaches square-root-scale representation;
it is validated only on the fitting corpus.
```

## 5. Positive gate

A positive package must provide:

```text
a literal deformation compiler from public E,G,Q;
a complete transformation law under G -> -G;
a proof that the output is endpoint-charged;
all-point frozen and held-out correctness;
independent replay;
formal algebraic certificates;
a full preprocessing, advice, memory, precision and online cost ledger.
```

## 6. First attack order

```text
1. derive the tangent constraint for Q_t=[k]G_t;
2. classify which public deformations are horizontal on the n-torsion local system;
3. compute the gauge derivative for a universal Weierstrass or CM parameter;
4. test whether the k-dependent tangent coefficient cancels or is unavailable publicly;
5. only then screen finite-field or p-adic specializations.
```
