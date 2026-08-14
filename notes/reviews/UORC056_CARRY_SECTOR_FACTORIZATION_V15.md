# UORC-056 carry/sector factorization V15

## Status

This package continues the exact `UNIFORM-ORIENTED-ROOT-CIRCUIT-056` line
after V12, V13 and V14.

It does not construct the central evaluator

\[
A(E,G,Q)=\frac{Y_G(x(Q))}{y(Q)}=(-1)^k,\qquad Q=[k]G,
\]

and it makes no sub-square-root complexity claim.  It gives a sharper exact
normal form for the two unresolved orientation channels exposed by the
threefold CM decomposition.

## Why the earlier multi-decimation plan is obsolete on secp256k1

V13 proves, in the declared secp256k1 scope, that every quadratic-character
atom

\[
Q\longmapsto \chi(\psi_m([u]Q))
\]

is invariant under the order-three GLV automorphism

\[
\alpha(x,y)=(\beta x,y).
\]

Products, quotients, scalar pullbacks and one global phase preserve that
invariance.  Canonical scalar parity is not GLV-invariant.  Therefore the
entire finite multiplicative division-polynomial character class is already
closed for arbitrary factor count on secp256k1.

A meet-in-the-middle search through products of weight two through six is
still a possible transfer-corpus experiment, but it is no longer the main
secp256k1 frontier and cannot overturn the exact V13 symmetry mismatch.

## V14 input

On every frozen `j=0` instance, V14 writes

\[
K_H(X)=\kappa(X^3)
\]

and decomposes the oriented root as

\[
Y_G(X)=A(T)+XB(T)+X^2C(T),\qquad T=X^3.
\]

For the public C3 orbit

\[
Q,\quad \alpha Q,\quad \alpha^2Q
\]

let

\[
s_0=\sigma(Q),\qquad
s_1=\sigma(\alpha Q),\qquad
s_2=\sigma(\alpha^2Q),
\qquad \sigma(P)\in\{\pm1\}.
\]

The exact V14 projectors are

\[
\frac{3A}{y}=s_0+s_1+s_2,
\]

\[
\frac{3xB}{y}=s_0+\beta^2s_1+\beta s_2,
\]

\[
\frac{3x^2C}{y}=s_0+\beta s_1+\beta^2s_2.
\]

The four-branch selector is

\[
u=\frac{xB}{A}
\in\{0,-2,-2\beta,-2\beta^2\}.
\]

## V15 exact two-bit normal form

Define the GLV carry and the three complementary sector bits by

\[
c=s_0s_1s_2,
\]

\[
\kappa_0=s_1s_2,\qquad
\kappa_1=s_2s_0,\qquad
\kappa_2=s_0s_1.
\]

Then

\[
\boxed{\sigma(Q)=c\,\kappa_0}
\]

and

\[
\boxed{\kappa_0\kappa_1\kappa_2=1}.
\]

Thus the sector state is not an arbitrary three-bit state.  It is one of the
four elements

\[
(+,+,+),\quad (+,-,-),\quad (-,+,-),\quad (-,-,+).
\]

This is the Klein-four quotient of the three orbit signs after the common
orientation bit has been removed.

## Exact relation to the V14 selector

The V14 field selector is the C3 Fourier transform of the sector bits:

\[
\boxed{
u=
-\left(
\kappa_0+\beta^2\kappa_1+\beta\kappa_2
\right).
}
\]

The branch table is

| orbit type | \((\kappa_0,\kappa_1,\kappa_2)\) | \(u\) |
|---|---:|---:|
| uniform | \((+,+,+)\) | \(0\) |
| \(Q\) is minority | \((+,-,-)\) | \(-2\) |
| \(\alpha Q\) is minority | \((-,+,-)\) | \(-2\beta^2\) |
| \(\alpha^2Q\) is minority | \((-,-,+)\) | \(-2\beta\) |

Conversely, define

\[
h(U)=\frac{U^3+U^2-2U+6}{6}.
\]

On the four selector branches,

\[
\boxed{
\kappa_0=h(u),\qquad
\kappa_1=h(\beta u),\qquad
\kappa_2=h(\beta^2u).
}
\]

Therefore a public evaluator for one binary sector bit, called on the three
public GLV rotations, reconstructs the full four-state selector with three
calls.  Conversely the field selector immediately gives all three sector
bits.  The binary sector formulation and the V14 four-state selector are
constant-call equivalent.

## The invariant A-mode is not a third independent observable

The V14 quantity \(A/y\) collapses exactly to carry and selector:

\[
\boxed{
\frac{A}{y}
=
c\left(1+\frac{u^3}{6}\right).
}
\]

For a uniform orbit, \(u=0\), so \(A/y=c\).  For a mixed orbit,
\(u^3=-8\), so \(A/y=-c/3\).

Combining this with

\[
\sigma(Q)
=
\frac{A}{y}
\left(1+u-\frac{u^2}{2}\right)
\]

gives the same two-bit factorization.  After clearing denominators, the
identity is

\[
(6+u^3)(2+2u-u^2)
=
2(u^3+u^2-2u+6)
\]

under the selector equation \(u(u^3+8)=0\).

The practical consequence is that future searches should not treat
`A/y`, carry and sector as three independent targets.  There are exactly two
orientation channels in this normal form.

## Kummer-sector involution

The sector bit has a direct x-only expression in the oriented root:

\[
\boxed{
J_G(x)
=
\frac{
Y_G(\beta x)Y_G(\beta^2x)
}{
x^3+7
}
=
\kappa_0.
}
\]

On the subgroup half-kernel,

\[
\boxed{J_G(x)^2=1}
\]

and its three GLV rotations satisfy

\[
\boxed{
J_G(x)J_G(\beta x)J_G(\beta^2x)=1.
}
\]

The denominator-free identities kernel-checked in Lean are

\[
\bigl(Y_1Y_2\bigr)^2=F^2
\]

and

\[
(Y_1Y_2)(Y_2Y_0)(Y_0Y_1)=F^3
\]

whenever \(Y_i^2=F\).

This isolates a precise surviving Kummer problem:

\[
\boxed{
x(Q)\longmapsto J_G(x(Q))\in\{\pm1\}.
}
\]

## Symmetry separation

The two factors occupy complementary symmetry channels.

| target | \(Q\mapsto -Q\) | \(Q\mapsto\alpha Q\) |
|---|---:|---:|
| carry \(c\) | changes sign | invariant |
| sector \(J_G=\kappa_0\) | invariant | rotates to \(\kappa_1\) |
| parity \(\sigma\) | changes sign | generally non-invariant |

This explains why neither a Kummer-only invariant nor a GLV-invariant
division-polynomial character can by itself return parity.

It also gives an immediate V13 corollary: finite multiplicative
division-polynomial character monomials cannot equal the sector bit, because
they are GLV-invariant while \(J_G\) is not.

## Exact replay

The executable V15 replay uses all five frozen curves, every marked generator
and every nonzero scalar.

It verifies:

* 438 oriented roots;
* 46,260 scalar evaluations;
* the carry-sector factorization;
* the Klein-four state law;
* the selector Fourier transform;
* the inverse sector polynomial;
* the collapse of \(A/y\);
* the V14 direct reconstruction;
* the Kummer involution and its orbit product.

Frozen aggregate counts are

\[
\begin{aligned}
\text{uniform}&=12096,\\
\text{minority}_0&=11388,\\
\text{minority}_1&=11388,\\
\text{minority}_2&=11388,
\end{aligned}
\]

\[
c=+1:23130,\qquad c=-1:23130,
\]

\[
J_G=+1:23484,\qquad J_G=-1:22776.
\]

These counts are regression anchors, not statistical evidence for a
production-size decoder.

## Revised frontier

The next primary tasks are now narrower.

1. Carry channel

   Seek a compact public decoder or a scoped lower bound for

   \[
   c(Q)=\sigma(Q)\sigma(\alpha Q)\sigma(\alpha^2Q).
   \]

   This is the already-localized GLV carry from the R3 line.  Its exact
   definition is known, but no public `Q`-only decoder is known.

2. Kummer sector channel

   Seek a compact evaluator or lower bound for

   \[
   J_G(x)=
   \frac{Y_G(\beta x)Y_G(\beta^2x)}{x^3+7}.
   \]

   Direct dense construction is still linear in \(n\).  The useful question is
   whether `J_G` admits a short recurrence, modular-composition
   representation, elliptic-unit formula, transposed evaluation or another
   generator-sensitive compression.

3. Shared evaluation

   Do not independently materialize dense `A` and `B`.  Search for a shared
   circuit that returns \(c\) and \(J_G\), or parity directly, while charging
   preprocessing, advice, memory, representation construction, public GLV
   calls and online evaluation.

4. Additive CM-weight mixing

   V13 closes multiplicative division-polynomial character monomials.
   The remaining algebraic-character frontier must mix different CM weights
   additively, use a field-valued output, carry a nontrivial GLV
   representation, or branch adaptively.

5. Formalization

   The present Lean file proves only the denominator-free sign, selector and
   Kummer algebra.  A later package should formalize the all-index V13
   CM-weight induction and connect the V15 quotient identities to the
   repository's elliptic-curve and kernel-polynomial definitions.

## Scientific boundary

V15 is a genuine structural reduction, but not an algorithmic breakthrough.

It replaces the V14 description

\[
\text{invariant A-mode plus four-state sector}
\]

by the sharper statement

\[
\boxed{
\text{canonical parity}
=
\text{one GLV carry bit}
\times
\text{one Kummer sector bit}.
}
\]

Neither bit currently has a public sub-square-root decoder.  The central
UORC-056 evaluator therefore remains open.
