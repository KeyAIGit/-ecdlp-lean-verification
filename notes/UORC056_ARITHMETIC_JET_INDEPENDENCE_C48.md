# UORC-056 C48: the arithmetic jet gives a compact high-degree state

Date: 2026-08-17

Status: positive compact-state construction plus scoped negative decoder screens. No ordered-sector evaluator, parity oracle, or sub-square-root ECDLP algorithm is claimed.

## 1. What is the arithmetic jet?

The arithmetic jet `epsilon_n(Q)` is the first error that appears when the public point `Q` is lifted from arithmetic modulo `p` to arithmetic modulo `p^2`, and the public multiplication `[n]` is evaluated there.

In simpler words, `[n]Q` is exactly the identity modulo `p`. After lifting one numerical layer higher, the result is usually not exactly the identity. The first normalized remainder is `epsilon_n(Q)`.

It is publicly computable:

1. lift the public x-coordinate to its Teichmueller representative modulo `p^2`;
2. recover the unique y-coordinate reducing to the public y-coordinate;
3. calculate `[n]` with a binary addition chain;
4. extract the first formal-kernel coefficient.

This requires `O(log n)` curve operations modulo `p^2`.

The replay independently reconstructs the same value from the canonical torsion-lift x-digit `u_x(Q)` and verifies

\[
x(Q)u_x(Q)=-2y(Q)n^{-1}\epsilon_n(Q).
\]

## 2. Comparison with the C45 raw state

C45 constructed the public field state

\[
\Phi_{\rm raw}(Q).
\]

Both states obey the same two transformation laws:

\[
\epsilon_n(-Q)=-\epsilon_n(Q),
\qquad
\Phi_{\rm raw}(-Q)=-\Phi_{\rm raw}(Q),
\]

and under the public order-three GLV rotation `alpha`,

\[
\epsilon_n(\alpha Q)=\beta\epsilon_n(Q),
\qquad
\Phi_{\rm raw}(\alpha Q)=\beta\Phi_{\rm raw}(Q).
\]

Therefore their quotient

\[
\boxed{
R_{\rm arith}(Q)=\frac{\epsilon_n(Q)}{\Phi_{\rm raw}(Q)}
}
\]

is unchanged by both operations:

\[
R_{\rm arith}(-Q)=R_{\rm arith}(Q),
\qquad
R_{\rm arith}(\alpha Q)=R_{\rm arith}(Q).
\]

For the marked `j=0` subgroup, the six points obtained from negation and the three GLV rotations have one common public coordinate

\[
T=x(Q)^3.
\]

Consequently `R_arith` is a function of `T` on the subgroup.

## 3. Why this is a positive result

The function `R_arith(T)` is computed by two logarithmic-depth public evaluations and one division. It is therefore a short algorithmic state.

However, when the same function is represented as an ordinary polynomial on the finite GLV/negation quotient, all eight toy curves give the largest possible degree and every coefficient is nonzero.

```text
8 curves
8 maximal-degree interpolants
8 dense interpolants
```

This is the concrete phenomenon we were searching for:

```text
algebraically enormous function
computed by a short uniform procedure
```

It also demonstrates why polynomial degree alone cannot prove that a function needs a large arithmetic circuit.

The result is finite representation evidence, not a theorem that the production secp256k1 interpolant is dense or that every alternative representation is large.

## 4. Does it already give parity?

No.

`R_arith` is unchanged by the GLV rotation, while the ordered Kummer-sector sign rotates among three sector positions. Therefore `R_arith` cannot directly equal that sector sign.

The two binary signs

\[
\chi(\Phi_{\rm raw}(Q)),
\qquad
\chi(\epsilon_n(Q))
\]

also fail to determine parity uniformly on the eight curves. The same two-bit state occurs with both parity labels.

Complete affine-character searches on the three smallest fields do find many exact formulas fitted to individual tiny curves. They do not transfer. The unchanged integer-offset family from `-512` through `512`, and ten public coefficient families including `beta`, `beta^2`, `n`, `n^{-1}`, `7`, and their simple signs, produce zero exact carry decoders across all eight curves.

Thus the tiny formulas are finite interpolation effects, not a uniform algorithm.

## 5. Exact replay

```text
8 toy curves
10,086 nonzero scalar rows
10,086 public arithmetic-jet evaluations
10,086 independent torsion-digit reconstructions
1,681 GLV/negation quotient points
8 dense maximal-degree interpolants
819 complete tiny-field affine-character candidates
118 tiny-curve exact fits
0 transferable affine-character decoders
0 arithmetic errors
```

No unknown secp256k1 target is used.

## 6. Decision

```text
Public arithmetic jet                     constructed
Evaluation cost                           O(log n) modulo p^2
Nonconstant quotient state R_arith        constructed
High-degree low-size phenomenon           observed on all eight toys
Direct ordered-sector value               no
Uniform carry decoder in declared screen  no
Parity oracle                             no
```

## 7. Successor

The next package is

```text
ARITHMETIC-JET-NONLINEAR-DECODER-C49
```

It should use the complete field values

\[
\Phi_{\rm raw}(Q),
\qquad
\epsilon_n(Q),
\qquad
R_{\rm arith}(Q),
\qquad
T=x(Q)^3
\]

inside a charged nonlinear decoder for the GLV carry or ordered sector.

A valid result must not store the dense interpolating polynomial, use a table indexed by the hidden scalar, or infer circuit complexity from degree alone. The strongest next mechanisms are a short recurrence for `R_arith`, a modular-composition rule, a higher p-adic jet coupled to the first jet, or a mixed theta/elliptic-unit relation.

## Claim boundary

C48 proves the exact public evaluation and exact finite toy identities stated above. It does not prove production-size density, a circuit lower bound, pseudorandomness, a parity oracle, or a sub-square-root ECDLP algorithm.
