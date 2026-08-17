# UORC-056 C37: half-index Miller quadratic branch

Date: 2026-08-15

Status: positive structural reduction plus scoped negative decoder screens. No parity evaluator is claimed.

## 1. Why C37 exists

C36 settled the most natural regularized order-`n` Miller route. For `P,Q` in the same order-`n` subgroup and a regular public shift `S`,

\[
\frac{f_{n,P}(S+Q)}{f_{n,P}(S)}=h_{P,Q}(S)^n,
\]

so the full unreduced field value is only a public line gauge raised to the `n`-th power.

The next non-equivalent index is

\[
h=\frac{n-1}{2}.
\]

Unlike the order-`n` quotient, the shifted `h`-Miller value does not collapse to one rational line gauge. It leaves one exact square-root choice.

## 2. Exact half-index normal form

The standard Miller recursion is

\[
f_{a+b,P}=f_{a,P}f_{b,P}g_{aP,bP},
\qquad
g_{A,B}=\frac{\ell_{A,B}}{v_{A+B}}.
\]

Since

\[
2h=n-1,
\qquad
2hP=-P,
\]

we first double `h` and then add the final `P`:

\[
f_{2h,P}=f_{h,P}^2\frac{\ell_{hP,hP}}{v_{-P}},
\]

\[
f_{n,P}=f_{2h,P}g_{-P,P}.
\]

The final opposite-point line is the same vertical line:

\[
g_{-P,P}=v_P=v_{-P}.
\]

Therefore the vertical factors cancel exactly:

\[
\boxed{f_{n,P}=f_{h,P}^2\ell_{hP,hP}.}
\]

For

\[
M_m(P,Q,S)=\frac{f_{m,P}(S+Q)}{f_{m,P}(S)},
\]

this gives

\[
M_n(P,Q,S)
=M_h(P,Q,S)^2
\frac{\ell_{hP,hP}(S+Q)}{\ell_{hP,hP}(S)}.
\]

Substituting the C36 order-`n` identity yields the central C37 formula:

\[
\boxed{
M_h(P,Q,S)^2
=
\frac{h_{P,Q}(S)^n}
{\ell_{hP,hP}(S+Q)/\ell_{hP,hP}(S)}.
}
\]

Everything on the right is publicly computable. The exact Miller evaluator on the left selects one of the two square roots.

This must be interpreted carefully. `M_h` itself is a public rational function and is computable by a binary Miller chain in `O(log n)` operations. C37 is not introducing an algebraic extension that was absent before. It proves that relative to the C36 public line-gauge normal form, the only additional information retained by the half-index value is one square-root branch.

## 3. It is genuinely generator-sensitive

The negation automorphism gives, with the same normalized Miller conventions,

\[
f_{h,-P}(Z)=c_h f_{h,P}(-Z),
\qquad c_h\in\{+1,-1\}.
\]

The constant cancels in shifted quotients, so

\[
\boxed{M_h(-P,Q,S)=M_h(P,-Q,-S).}
\]

For a trace-zero twist `S^p=-S`, define

\[
U_h(P,Q)=\frac{M_h(P,Q,S)}{M_h(P,Q,-S)}.
\]

Then

\[
\boxed{U_h(-P,Q)=U_h(P,-Q)^{-1}.}
\]

Thus the half-index state is not generator-blind. It survives the basic covariance test that killed `Q`-only line, division-polynomial and order-`n` Miller constructions.

## 4. Norm-one square state

The trace-zero state lies in the norm-one torus:

\[
U_h(P,Q)^{p+1}=1.
\]

Its square is still completely public. If

\[
L(P,Q,S)=\frac{\ell_{hP,hP}(S+Q)}{\ell_{hP,hP}(S)},
\]

then

\[
\boxed{
U_h(P,Q)^2
=
\left(\frac{h_{P,Q}(S)}{h_{P,Q}(-S)}\right)^n
\frac{L(P,Q,-S)}{L(P,Q,S)}.
}
\]

For secp256k1,

\[
v_2(p+1)=4.
\]

Consequently the maximal constant-size 2-primary projection of the norm-one state has only sixteen possible values:

\[
\eta(U)=U^{(p+1)/16}\in\mu_{16}.
\]

This is the natural small phase in which one could hope the residual square-root branch becomes parity.

## 5. Exact decoder screens

The following screens are deliberately scoped. They do not claim a lower bound against arbitrary nonlinear field circuits.

### 5.1 Ordinary quadratic characters

The full extension-field quadratic character is insensitive to root sign because

\[
\chi_{p^2}(-x)=\chi_{p^2}(x).
\]

Likewise, on every frozen curve and secp256k1, `(p+1)/2` is even, so the ordinary quadratic character of the norm-one torus also identifies `U` and `-U`.

Direct exact evaluation confirms that neither normalized character equals parity on any frozen curve.

### 5.2 One maximal 2-primary state

For each frozen curve, the maximal 2-primary phase

\[
\eta(U_h(Q))
\]

has an exact collision between an even and an odd scalar. Therefore no decoder depending only on this one constant-size phase can return parity on the full nonzero subgroup.

This is stronger than saying a particular formula failed: the same projected field value occurs in both parity classes.

### 5.3 Seven C34 locations

Use the seven public locations from the three-carry geometry:

```text
Q,
A=2Q,
T=-Q/2,
B=T-A,
-T,
-B,
U=Q+A.
```

At every location retain the complete maximal 2-primary phase of the half-index norm-one state. The grammar allows

\[
\prod_{j=1}^{7}\eta(U_h([u_j]Q))^{c_j},
\qquad c_j\in\mathbb Z/2^s\mathbb Z,
\]

with normalization at `Q=G`. This contains every multiplicative monomial in the seven full states after projection to the only component capable of producing the target element `-1`.

The resulting modular linear systems are decided exactly with an integer Smith decomposition. All five frozen curves are inconsistent with normalized parity:

\[
\boxed{\text{seven-location monomial survivors}=0.}
\]

Therefore no full-field monomial in these seven fixed-source half-index cells can equal parity: any such equality would survive projection to the 2-primary torus.

## 6. A new rational-decoder lower bound for a single state

The full half-index field state is injective on every nonzero frozen subgroup. Hence a set-theoretic decoder exists, but a small lookup-free rational decoder does not.

Let `S_k` be any field-valued state. Suppose the `+1` parity class contains `r` distinct state values and the `-1` class contains `r` distinct state values. Assume

\[
D(X)=\frac{A(X)}{B(X)}
\]

is regular at every sampled state and satisfies

\[
D(S_k)=+1\quad(k\text{ even}),
\qquad
D(S_k)=-1\quad(k\text{ odd}).
\]

Then `A-B` vanishes at all `+1` states and `A+B` vanishes at all `-1` states. If

\[
\deg A<r,
\qquad
\deg B<r,
\]

both polynomials must be identically zero. In odd characteristic this forces `A=B=0`, which is not a decoder. Therefore

\[
\boxed{
\max(\deg A,\deg B)\ge r.
}
\]

On every frozen curve the half-index state is injective on all `n-1` nonzero scalars, and each parity class has

\[
r=\frac{n-1}{2}
\]

distinct values. Thus every single-state balanced rational decoder has degree at least

\[
\boxed{\frac{n-1}{2}.}
\]

This is a rational-degree boundary, not an arithmetic-circuit lower bound. A high-degree decoder could still have a short addition chain.

## 7. Replay totals

The executable package verifies:

```text
curves                                      5
marked generators                         438
public marked-query cases              46,260
base half-index factorizations             438
shifted square identities              46,260
norm-one square identities             46,260
generator-reversal covariance checks   46,260
full-state injectivity curves                5
maximal 2-primary collision curves           5
seven-location monomial survivors            0
ordinary quadratic-character survivors       0
errors                                        0
```

The exact finite screens use only the frozen public curves and known scalars.

## 8. Decision

C37 produces the strongest concrete compact-state candidate found so far:

\[
\boxed{S_G(Q)=M_{(n-1)/2}(G,Q,S).}
\]

Its builder is public and has Miller-chain cost `O(log n)`. Relative to an explicit public radicand, it contains exactly one square-root choice and has the correct generator-sensitive covariance.

But the required decoder is still missing:

- ordinary quadratic characters are branch-blind;
- the maximal sixteen-state secp phase is insufficient by itself on every toy curve;
- no fixed multiplicative monomial over the seven C34 positions works;
- every one-variable rational decoder on the frozen corpus has degree at least `(n-1)/2`.

So C37 does not produce parity. It changes the frontier from

```text
find an arbitrary public field state
```

to

```text
understand the one residual branch of the half-index Miller state,
or mix several generator-sensitive source directions nonlinearly.
```

The successor is

```text
MIXED-SOURCE-ELLIPTIC-NET-C38
```

with the first source set

```text
G, -G, 2G, ((n-1)/2)G, lambda G, lambda^2 G
```

and the same seven C34 target locations. Any positive candidate must use the full field values or a nonlinear net/resultant relation; a fixed monomial in their 2-primary projections is already the first class to screen.
