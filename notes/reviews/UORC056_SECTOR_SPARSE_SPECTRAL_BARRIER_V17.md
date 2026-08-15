# UORC-056 sector sparse spectral barrier V17

## Status

This package is stacked on V16. The central target remains

\[
\frac{Y_G(x([k]G))}{y([k]G)}=(-1)^k.
\]

V17 does not construct a public sector decoder, parity evaluator, or ECDLP
algorithm. It closes one explicit representation class:

```text
one exact linear combination of additive characters
with sub-square-root expanded support
```

The output considered here is the V15/V16 Kummer sector bit

\[
J_G(x([k]G))
=
\sigma_G([k]G)\,g_G([k]G)
\in\{+1,-1\}.
\]

The value at the identity scalar \(k=0\) is left free. This matters because the
central evaluator is only required on nonzero subgroup points.

## Model

Let \(n\) be the prime subgroup order and let

\[
\zeta_n=e^{2\pi i/n}.
\]

Consider a candidate

\[
F(k)
=
\sum_{r\in S} c_r\zeta_n^{rk},
\qquad
S\subseteq \mathbf Z/n\mathbf Z,
\qquad
c_r\ne0.
\]

Write

\[
m=|S|.
\]

The exact requirement is

\[
F(k)=J_G(x([k]G))
\quad
\text{for every }k\ne0.
\]

No condition is imposed on \(F(0)\).

The support \(S\) and all coefficients are charged. A representation that
implicitly materializes \(m\) distinct characters has cost at least \(m\) in
this model.

## Square residual

Define

\[
H(k)=F(k)^2-1.
\]

Because \(J_G(k)\in\{\pm1\}\),

\[
H(k)=0
\qquad
(k\ne0).
\]

Therefore exactly one of two cases occurs.

### Case 1: \(H=0\)

Then \(F(k)\in\{\pm1\}\) for every \(k\), including \(k=0\).

The sector bit is nonconstant. V16 gives both sign fibers explicitly:

\[
N_+>0,\qquad N_->0.
\]

For a prime \(n\), every nonconstant binary function on
\(\mathbf Z/n\mathbf Z\) has full additive Fourier support.

To see this, let

\[
P(X)=\sum_{k=0}^{n-1}F(k)X^k\in\mathbf Z[X].
\]

Suppose a nonzero Fourier coefficient vanished. Then

\[
P(\zeta_n^r)=0
\]

for some \(r\ne0\). Since \(n\) is prime, \(\zeta_n^r\) is primitive and its
minimal polynomial is

\[
\Phi_n(X)=1+X+\cdots+X^{n-1}.
\]

Both \(P\) and \(\Phi_n\) have degree at most \(n-1\). Hence

\[
P=c\Phi_n
\]

for some constant \(c\), so all values \(F(k)\) are equal. This contradicts
nonconstancy.

The zero-frequency coefficient is also nonzero because it is a sum of an odd
number \(n\) of values in \(\{\pm1\}\).

Thus

\[
\boxed{m=n}
\]

in Case 1.

### Case 2: \(H\ne0\)

Since \(H\) vanishes at every nonzero scalar,

\[
H=H(0)\,\delta_0.
\]

The Fourier transform of a nonzero point mass is nonzero at every frequency.

The Fourier support of \(F^2\) is contained in the sumset

\[
S+S=\{r+s:r,s\in S\}.
\]

At every nonzero frequency, the constant function \(1\) contributes zero.
Consequently

\[
(\mathbf Z/n\mathbf Z)\setminus\{0\}
\subseteq
S+S.
\]

Therefore

\[
|S+S|\ge n-1.
\]

Every element of \(S+S\) is produced by an unordered pair from \(S\), including
a repeated element. There are at most

\[
\binom{m+1}{2}
=
\frac{m(m+1)}2
\]

such pairs. Hence

\[
\boxed{
\frac{m(m+1)}2\ge n-1.
}
\]

Combining the two cases gives the universal bound

\[
\boxed{
m
\ge
\left\lceil
\frac{\sqrt{8n-7}-1}{2}
\right\rceil.
}
\]

The proof allows arbitrary complex coefficients and an arbitrary value at the
identity point.

## Exact secp256k1 value

For secp256k1,

\[
n=
115792089237316195423570985008687907852837564279074904382605163141518161494337.
\]

The smallest integer satisfying

\[
\frac{m(m+1)}2\ge n-1
\]

is

\[
\boxed{
m_{\min,\mathrm{bound}}
=
481231938336009023090067544955250113853.
}
\]

It satisfies

\[
2^{128}
<
m_{\min,\mathrm{bound}}
<
2^{129}.
\]

The preceding integer fails:

\[
\frac{(m_{\min,\mathrm{bound}}-1)m_{\min,\mathrm{bound}}}{2}
<
n-1.
\]

The stated integer succeeds:

\[
\frac{m_{\min,\mathrm{bound}}
(m_{\min,\mathrm{bound}}+1)}2
\ge
n-1.
\]

Thus an exact sparse additive-character sector formula cannot have

\[
O(n^{1/2-\varepsilon})
\]

expanded frequency support for any fixed \(\varepsilon>0\).

## Canonical extension

For the canonical extension

\[
J_G(0)=+1,
\]

V16 gives

\[
\sum_{k=1}^{n-1}J_G(k)=208.
\]

Therefore the full-cycle DC sum is

\[
\sum_{k=0}^{n-1}J_G(k)=209.
\]

The extension is nonconstant and binary on the entire prime cycle. The
prime-cyclotomic argument gives the stronger statement

\[
\boxed{
|\operatorname{supp}\widehat{J_G}|=n.
}
\]

So the canonical exact linear character expansion uses every frequency.

The root-scale bound is needed only because a candidate for the nonzero-domain
problem may choose a nonbinary value at \(k=0\).

## Why the exponent cannot be improved by this support argument alone

Let

\[
b=\lceil\sqrt n\rceil.
\]

Define

\[
S_0
=
\{0,1,\ldots,b-1\}
\cup
\{0,b,2b,\ldots,(b-1)b\}
\pmod n.
\]

Every integer \(x\in\{0,\ldots,n-1\}\) has a decomposition

\[
x=qb+r,
\qquad
0\le q,r<b.
\]

Hence

\[
S_0+S_0=\mathbf Z/n\mathbf Z
\]

and

\[
|S_0|\le2\lceil\sqrt n\rceil-1.
\]

For secp256k1,

\[
b=2^{128},
\]

so this support-only upper construction has size at most

\[
2^{129}-1.
\]

This does not construct coefficients that evaluate \(J_G\). It only shows that
the necessary sumset-coverage condition is itself tight at exponent \(1/2\).
Any stronger obstruction must use coefficient equations, circuit structure,
CM covariance, or another property beyond support cardinality.

## Frozen replay

The executable package checks the five frozen prime-order curves:

```text
orders:             31, 79, 67, 127, 139
nonzero scalars:    438
failures:             0
```

For every curve it verifies:

- the sector sequence is binary;
- the sector sequence is nonconstant;
- the sector sequence is Kummer-even;
- the exact sector sum agrees with the V16 floor-sum certificate;
- both sign fibers are nonempty;
- the canonical binary extension has a full-rank circulant certificate modulo
  the prime \(1000003\);
- the pair-cover lower-bound integer is minimal;
- the deterministic order-two additive basis covers the full cyclic group.

The modular circulant check is an independent finite certificate. If the
sequence polynomial is coprime to \(X^n-1\) modulo one prime, its integer
circulant determinant is nonzero. The general complex full-support proof is the
prime-cyclotomic argument above.

## Closed class

V17 closes:

```text
exact one-layer additive-character sum
+ arbitrary complex coefficients
+ exact values on every nonzero scalar
+ free value at the identity
+ expanded support o(sqrt(n))
```

For secp256k1 the support must contain at least the exact 129-bit number above.

## Boundary

V17 does not close:

- arithmetic circuits whose multiplication gates generate large frequency
  sumsets from a short description;
- modular composition;
- transposed multipoint evaluation;
- recurrence-compressed high-degree objects;
- p-adic or theta representations;
- sparse rational character quotients with separately represented numerator
  and denominator;
- a shared nonlinear circuit for \(g_G\) and \(J_G\).

The main surviving question is no longer whether a short direct spectral sum
exists. It is whether an exponentially large spectral object can be evaluated
from a genuinely small nonlinear representation without hiding its size in
advice, memory, preprocessing, or representation cost.
