# UORC-056 C35: shifted Miller gauge and torus-collapse boundary

Date: 2026-08-15

Status: exact structural package with frozen replay. No parity evaluator or sub-square-root ECDLP algorithm is claimed.

## 1. Target inherited from C34

For

\[
Q=[k]G,
\qquad
\sigma_G(Q)=(-1)^k,
\]

C34 proved the constant-width identity

\[
\sigma_G(Q)
=
C_G(Q,A)C_G(A,B)C_G(-T,-B),
\]

where

\[
A=[2]Q,
\qquad
T=[-2^{-1}]Q,
\qquad
B=T-A.
\]

The remaining question is computational: can this three-carry product be represented by a public field value that genuinely depends on the marked generator and is cheaper than square root?

C35 tests the strongest natural one-field candidate available from standard elliptic arithmetic: a regularized, generator-sensitive Miller value evaluated after a quadratic-extension shift.

## 2. Public shifted Miller state

Let

\[
\operatorname{div}(f_G)=n[G]-n[O].
\]

The function is defined only up to a nonzero scalar, but the following ratio is independent of that scalar. Choose

\[
S\in E(\mathbb F_{p^2}),
\qquad
S^p=-S,
\]

and define

\[
\boxed{
M_S(P)=\frac{f_G(P+S)}{f_G(S)}.
}
\]

The shift removes the same-subgroup exceptional evaluations that can appear in a direct affine Miller loop. Both numerator and denominator can be evaluated by one ordinary Miller straight-line program of length \(O(\log n)\).

This is a genuine positive result:

\[
\boxed{
\text{a compact, marked-generator-sensitive field state exists and is quickly evaluable.}
}
\]

It is not yet a parity evaluator because a cheap decoder has not been found.

## 3. All shifts belong to one explicit gauge class

Let \(g_{G,-S}\) be the standard addition-line function with

\[
\operatorname{div}(g_{G,-S})
=
[G]+[-S]-[G-S]-[O].
\]

As a function of \(P\),

\[
\operatorname{div}(M_S)
=
n[G-S]-n[-S].
\]

The function

\[
f_G(P)g_{G,-S}(P)^{-n}
\]

has the same divisor. Hence they differ only by a shift-dependent nonzero constant. Eliminating that constant with a public reference point \(P_0\) gives

\[
\boxed{
\frac{M_S(P)}{M_S(P_0)}
=
\frac{f_G(P)}{f_G(P_0)}
\left(
\frac{g_{G,-S}(P_0)}{g_{G,-S}(P)}
\right)^n.
}
\]

This is the first main boundary of C35:

\[
\boxed{
\text{different twist shifts do not create independent orientation channels.}
}
\]

They are explicit public \(n\)-th-power line gauges of one underlying Miller potential.

Therefore trying many shifts cannot be counted as obtaining many independent hidden signs. Any gain must come from a decoder that exploits the common base potential itself.

## 4. Frobenius projection collapses to a public Kummer coordinate

Define the norm-one or torus component

\[
T_S(P)=M_S(P)^{p-1}.
\]

Because \(P\in E(\mathbb F_p)\), \(S^p=-S\), and \(f_G\) has base-field coefficients,

\[
T_S(P)
=
\frac{f_G(P-S)f_G(S)}
{f_G(P+S)f_G(-S)}.
\]

Let

\[
H=[2^{-1}]G
\]

and define the centered cross-ratio

\[
R_S(P)
=
\frac{x(P-H)-x(H+S)}
{x(P-H)-x(S-H)}.
\]

At \(P=H\), the value is interpreted by its regular limit, equal to 1.

Its divisor is

\[
[G+S]+[-S]-[S]-[G-S].
\]

The divisor of \(T_S\) is exactly \(n\) times this divisor. Therefore, after eliminating one constant at a public reference point,

\[
\boxed{
\frac{T_S(P)}{T_S(P_0)}
=
\left(
\frac{R_S(P)}{R_S(P_0)}
\right)^n.
}
\]

Moreover Frobenius swaps numerator and denominator:

\[
R_S(P)^p=R_S(P)^{-1}.
\]

Thus \(R_S(P)\) lies in the norm-one torus \(\mu_{p+1}\).

For secp256k1, exact arithmetic gives

\[
\gcd(n,p-1)
=
\gcd(n,p+1)
=
\gcd(n,p^2-1)
=1.
\]

Consequently, the \(n\)-th-power maps on

\[
\mathbb F_p^\times,
\qquad
\mu_{p+1},
\qquad
\mathbb F_{p^2}^\times
\]

are automorphisms with public inverse exponents.

Therefore the torus component does not hide an orientation bit:

\[
\boxed{
T_S(P)
\text{ is exactly equivalent to the public centered Kummer coordinate }
R_S(P),
}
\]

up to a public normalization constant.

## 5. Geometry of the torus fibres

The centered coordinate is invariant under

\[
P\longmapsto G-P.
\]

For \(P=[k]G\), this is

\[
k\longmapsto1-k\pmod n.
\]

The two representatives in a nontrivial fibre have the same ordinary parity because \(n+1\) is even:

\[
k
\equiv
n+1-k
\pmod 2.
\]

On every frozen curve, the torus state has exactly

\[
\frac{n+1}{2}
\]

values on the nonzero subgroup. Its fibres are

\[
\{1\},
\qquad
\{2^{-1}\},
\qquad
\{k,n+1-k\}.
\]

This explains why the torus state preserves parity while still failing to give a small explicit parity decoder. It is a centered Kummer quotient, not a new orientation lift.

## 6. Exact full-shift character scan

Every nonzero anti-rational twist shift was tested on all five frozen curves.

The total screen contains

```text
520 twist shifts
54,192 shift-query values
53,672 normalized shift-gauge identities
54,192 torus/Kummer identities
438 independent Miller-loop comparisons
```

For each shift, the complete \(\mathbb F_{p^2}^\times\) discrete-log table was constructed on the toy field only. The minimal multiplicative-character order whose output separates even and odd scalars was then determined exactly.

Results:

```text
p=43,  n=31:  {11:2, 22:12, 24:2, 28:4, 33:4, 42:2, 44:30}
p=67,  n=79:  {68:56}
p=79,  n=67:  {80:92}
p=127, n=127: {128:128}
p=163, n=139: {164:188}
```

No quadratic-character shift survived:

\[
\boxed{0\text{ survivors among }520\text{ shifts}.}
\]

On four of the five curves, every shift requires the full torus character order \(p+1\). Only the smallest curve has proper-quotient exceptions.

This is exact finite evidence, not an all-curves theorem.

## 7. The full Miller state is not automatically a cheap decoder

For one deterministic canonical shift on each frozen curve, the full values \(M_S([k]G)\) do determine parity. But they are nearly injective.

The numbers of distinct states are

```text
28, 76, 64, 124, 136
```

and the unique univariate polynomial interpolating parity from those states has degrees

```text
27, 75, 63, 123, 135.
```

Every coefficient of each interpolant is nonzero.

There is also a simple scoped rational-decoder lower bound. If

\[
D(Z)=\frac{A(Z)}{B(Z)}
\]

is defined on every observed state and equals \(+1\) on the even-state set and \(-1\) on the odd-state set, then

\[
A-B
\]

vanishes on every even state, while

\[
A+B
\]

vanishes on every odd state. Neither polynomial is identically zero. Hence

\[
\boxed{
\max(\deg A,\deg B)
\ge
\max(N_{\rm even},N_{\rm odd}).
}
\]

The frozen lower bounds are

```text
14, 38, 32, 62, 69.
```

This is a lower bound only for a univariate rational decoder in the declared full Miller coordinate. It is not an arithmetic-circuit lower bound.

## 8. Three-carry location grammars

For the seven C34 locations

\[
Q,
2Q,
3Q,
B,
T,
-T,
-B,
\]

C35 tested the canonical shifted Miller state in two exact grammars.

First, every nonempty subset product followed by the quadratic character was tested separately on every frozen curve. No exact parity formula survived.

Second, every exponent vector

\[
(e_1,\ldots,e_7)\in\{-1,0,1\}^7\setminus\{0\}
\]

was tested with character orders

\[
2,3,4,6,8,12,24.
\]

This gives

```text
2,186 exponent vectors
15,302 order/vector candidates
0 uniform survivors across all five curves.
```

The preliminary C35 screen is also retained. It tested arbitrary products of 196 generator-normalized division-polynomial quadratic-character atoms on the frozen \(p=43,n=31\) curve. The augmented binary system is inconsistent, so that declared grammar has zero exact survivors.

Again, these are finite exact grammar closures, not unrestricted impossibility results.

## 9. What C35 answers

C35 gives both a positive and a negative result.

Positive:

\[
\boxed{
M_S(P)=f_G(P+S)/f_G(S)
}
\]

is a compact, public, marked-generator-sensitive state with an \(O(\log n)\) Miller evaluation.

Negative:

1. changing the twist shift supplies only a public \(n\)-th-power line gauge;
2. the Frobenius or norm-one projection is exactly a centered public Kummer coordinate;
3. no quadratic shift character works on the full frozen shift corpus;
4. the declared low-order three-carry monomial grammars have no survivor;
5. the obvious univariate decoder is dense and root-count expensive on every toy curve.

Therefore the remaining unknown is no longer whether a compact Miller state exists. It does.

The remaining unknown is:

\[
\boxed{
\text{does a compact nonlinear multi-argument decoder exist for the common base Miller potential?}
}
\]

## 10. Successor contract

The next package is

```text
MULTI-ARGUMENT-MILLER-DECODER-C36
```

It should test functions of a constant number of marked Miller values

\[
M_S([u_1]Q),\ldots,M_S([u_r]Q)
\]

with all costs charged.

The first attack order is:

1. exact joint-state collision and rank classification;
2. low-degree multivariate rational interpolation;
3. determinant and resultant elimination across the three-carry geometry;
4. anchor-normalized elliptic-net identities not reducible to the shift gauge;
5. a lower bound for a precisely declared bounded-degree multi-argument grammar if no positive decoder survives.

## Decision flags

```text
marked_generator_source_used=true
canonical_y_anchor_scalar_used=false
compact_shifted_miller_state_found=true
independent_orientation_channels_from_twist_shifts_found=false
torus_component_collapses_to_centered_kummer=true
quadratic_shift_evaluator_found=false
low_order_three_carry_monomial_found=false
parity_oracle_found=false
sub_sqrt_evaluator_found=false
sub_sqrt_ecdlp_found=false
```
