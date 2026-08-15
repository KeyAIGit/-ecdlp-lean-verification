# UORC-056 sparse rational spectral sector barrier V18

## Status

This package is stacked on V17. The central target remains

\[
\frac{Y_G(x([k]G))}{y([k]G)}=(-1)^k.
\]

V17 excluded a single sparse additive-character sum with sub-square-root
expanded support. V18 extends the same root barrier to a quotient of two sparse
additive-character sums.

No public sector decoder, parity evaluator, or ECDLP algorithm is constructed.

## Model

Let \(n\) be the prime subgroup order and let

\[
\zeta_n=e^{2\pi i/n}.
\]

Consider

\[
A(k)=\sum_{r\in S_A}a_r\zeta_n^{rk},
\qquad
B(k)=\sum_{r\in S_B}b_r\zeta_n^{rk}.
\]

The coefficients may be arbitrary complex numbers. Zero coefficients are
removed from the supports.

Define the shared frequency dictionary

\[
T=S_A\cup S_B,
\qquad
t=|T|.
\]

The exact requirement is

\[
B(k)\ne0,
\qquad
\frac{A(k)}{B(k)}
=
J_G(x([k]G))
\in\{+1,-1\}
\]

for every \(k\ne0\).

No condition is imposed at \(k=0\).

Charging \(T\) only once is favorable to the candidate. The theorem therefore
also applies when numerator and denominator coefficients are charged
separately.

## Square residual dichotomy

Set

\[
H(k)=A(k)^2-B(k)^2.
\]

For every nonzero scalar,

\[
A(k)=J_G(k)B(k)
\]

and \(J_G(k)^2=1\). Therefore

\[
H(k)=0
\qquad
(k\ne0).
\]

There are two cases.

## Case 1: \(H\ne0\)

Then

\[
H=H(0)\delta_0.
\]

The Fourier transform of a nonzero point mass is nonzero at every frequency.
Hence

\[
\operatorname{supp}\widehat H
=
\mathbf Z/n\mathbf Z.
\]

The pointwise square of a character sum adds frequencies:

\[
\operatorname{supp}\widehat{A^2}
\subseteq S_A+S_A,
\]

\[
\operatorname{supp}\widehat{B^2}
\subseteq S_B+S_B.
\]

Because both \(S_A\) and \(S_B\) are contained in \(T\),

\[
\operatorname{supp}\widehat H
\subseteq T+T.
\]

Thus

\[
T+T=\mathbf Z/n\mathbf Z
\]

and

\[
|T+T|=n.
\]

At most \(t(t+1)/2\) distinct sums are produced by unordered pairs from \(T\).
Consequently

\[
\boxed{
\frac{t(t+1)}2\ge n.
}
\]

This part of the proof is elementary and does not use prime-order Fourier
uncertainty.

## Case 2: \(H=0\)

Now

\[
A^2=B^2
\]

at every scalar. Put

\[
U=A-B,
\qquad
V=A+B.
\]

Then

\[
UV=0
\]

pointwise.

At a nonzero positive-sector scalar,

\[
J_G(k)=+1,
\qquad
A(k)=B(k),
\]

so

\[
U(k)=0,
\qquad
V(k)=2B(k)\ne0.
\]

At a nonzero negative-sector scalar,

\[
J_G(k)=-1,
\qquad
A(k)=-B(k),
\]

so

\[
U(k)=-2B(k)\ne0,
\qquad
V(k)=0.
\]

Therefore \(U\) is supported on the negative sector, plus possibly the identity,
and \(V\) is supported on the positive sector, plus possibly the identity.

Their Fourier supports satisfy

\[
\operatorname{supp}\widehat U\subseteq T,
\qquad
\operatorname{supp}\widehat V\subseteq T.
\]

For a nonzero complex function on the prime cyclic group,
the prime-order uncertainty principle gives

\[
|\operatorname{supp}f|
+
|\operatorname{supp}\widehat f|
\ge
n+1.
\]

The primary source used here is:

```text
Terence Tao,
An uncertainty principle for cyclic groups of prime order,
arXiv:math/0308286.
```

Let \(M_+\) and \(M_-\) be the numbers of positive and negative sector scalars
among \(1,\ldots,n-1\). Since the identity may add at most one support point,

\[
|\operatorname{supp}U|\le M_-+1,
\]

\[
|\operatorname{supp}V|\le M_++1.
\]

Applying the uncertainty principle gives

\[
t\ge n-M_-=M_++1,
\]

\[
t\ge n-M_+=M_-+1.
\]

Hence

\[
\boxed{
t\ge\max(M_+,M_-)+1.
}
\]

This is a linear-size lower bound in the square-exact branch.

## Exact secp256k1 values

V16 gives the sector correlation

\[
M_+-M_-=208
\]

and

\[
M_++M_-=n-1.
\]

Therefore

\[
M_+
=
57896044618658097711785492504343953926418782139537452191302581570759080747272,
\]

\[
M_-
=
57896044618658097711785492504343953926418782139537452191302581570759080747064.
\]

### Nonzero square residual

The smallest integer satisfying

\[
\frac{t(t+1)}2\ge n
\]

is

\[
\boxed{
t_{\mathrm{root}}
=
481231938336009023090067544955250113853.
}
\]

It satisfies

\[
2^{128}
<
t_{\mathrm{root}}
<
2^{129}.
\]

The preceding integer fails the inequality, so this integer is exact.

### Square-exact residual

The uncertainty transfer gives

\[
\boxed{
t_{\mathrm{square}}
\ge
M_++1
=
57896044618658097711785492504343953926418782139537452191302581570759080747273.
}
\]

This branch requires essentially half of all frequencies.

### Universal quotient bound

Every candidate belongs to one of the two cases. Since the square-exact branch
has the stronger lower bound,

\[
\boxed{
t
\ge
481231938336009023090067544955250113853.
}
\]

Thus a quotient of two sparse additive-character sums cannot evaluate the
sector bit on every nonzero secp256k1 scalar with

\[
O(n^{1/2-\varepsilon})
\]

distinct expanded frequencies.

## Why V18 is stronger than V17

V17 studied

\[
F(k)=\sum_{r\in S}c_r\zeta_n^{rk}.
\]

V18 allows a denominator:

\[
F(k)=\frac{A(k)}{B(k)}.
\]

The numerator and denominator may share frequencies, and the union \(T\) is
charged only once. The same 129-bit lower bound survives.

The denominator therefore does not bypass the root support barrier in this
expanded spectral model.

## Frozen arithmetic replay

The executable package reuses the five frozen prime-order curves:

```text
orders: 31, 79, 67, 127, 139
curves: 5
failures: 0
```

For every curve it checks:

- the exact V16 sector correlation;
- the positive and negative scalar counts;
- minimality of the Case 1 pair-cover bound;
- the two Case 2 uncertainty transfers;
- that the square-exact branch is strictly stronger than the root branch.

The exact toy bounds are:

```text
n=31:  root 8,  square-exact 19
n=79:  root 13, square-exact 43
n=67:  root 12, square-exact 35
n=127: root 16, square-exact 67
n=139: root 17, square-exact 73
```

The replay verifies arithmetic and model transfer. It does not reprove the
prime-order uncertainty theorem.

## Formalization boundary

The Lean file kernel-checks:

- \(A=JB\) and \(J^2=1\) imply \(A^2-B^2=0\);
- the plus/minus factor identities;
- the exact secp256k1 scalar counts;
- minimality of the root pair-cover integer;
- the exact square-exact lower bound;
- the 128/129-bit interval.

Lean does not formalize:

- finite Fourier transforms;
- support of convolution;
- the prime-order uncertainty theorem;
- the transfer from character supports to \(T+T\).

Those obligations are stated explicitly rather than hidden behind a
kernel-checked label.

## Closed class

V18 closes:

```text
sparse additive-character numerator
divided by sparse additive-character denominator
+ arbitrary complex coefficients
+ denominator nonzero on every nonzero scalar
+ exact sector output on every nonzero scalar
+ identity value unrestricted
+ union support o(sqrt(n))
```

## Remaining frontier

The surviving options must avoid expanded sparse spectral storage. The main
open classes are:

- nonlinear circuits that create dense spectra through repeated multiplication;
- modular composition;
- transposed or batched evaluation;
- recurrence-compressed high-degree representations;
- p-adic, theta, or algebraic-function representations;
- shared carry-sector circuits;
- model-specific low-size circuits with exponentially large implicit support.

The next useful step is to select one of those compact representation models,
write its complete preprocessing/advice/memory/online cost contract, and test
whether it actually evaluates \(J_G\) without materializing a root-size
frequency set.
