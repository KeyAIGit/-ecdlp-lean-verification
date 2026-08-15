# UORC-056 direct shared parity Cauchy barrier V19

## Status

The central target remains

\[
\sigma_G(Q)=\frac{Y_G(x(Q))}{y(Q)}=g_G(Q)J_G(x(Q))=(-1)^k,
\qquad Q=[k]G.
\]

V19 implements the proposed direct-product direction. It does not try to decode
\(g_G\) and \(J_G\) separately. It asks whether their product can be represented
by one small shared spectral mechanism.

The result is negative for two precise models:

1. one bilinear product of two sparse additive-character sums;
2. one quotient of two sparse additive-character sums.

No public parity evaluator or ECDLP shortcut is constructed. The bounds concern
expanded spectral support, not unrestricted arithmetic circuits.

## Exact parity spectrum

Let \(n\) be odd, \(\zeta^n=1\), and

\[
\sigma(k)=(-1)^k,
\qquad
\widehat f(r)=\sum_{k=0}^{n-1}f(k)\zeta^{-rk}.
\]

A geometric sum gives

\[
\boxed{
\widehat\sigma(r)=\frac{2}{1+\zeta^{-r}}.
}
\]

The denominator never vanishes because an odd-order group contains no element
of order two. The values are also pairwise distinct, since
\(z\mapsto2/(1+z)\) is injective away from \(-1\). Thus canonical parity has all
\(n\) frequencies.

Suppose only the nonzero values are prescribed:

\[
F(k)=(-1)^k\quad(k\ne0),
\]

while \(F(0)\) is free. Then \(F=\sigma+d\delta_0\), so

\[
\widehat F(r)=\frac{2}{1+\zeta^{-r}}+d.
\]

A common constant can cancel at most one of the distinct values. Therefore

\[
\boxed{|\operatorname{supp}\widehat F|\ge n-1.}
\]

This is exact: choose \(F(0)=0\). Then exactly the zero frequency disappears.

## One bilinear shared gate

Let

\[
A(k)=\sum_{a\in S_A}u_a\zeta^{ak},
\qquad
B(k)=\sum_{b\in S_B}v_b\zeta^{bk},
\]

and suppose \(F=A B\) agrees with parity for every nonzero scalar. Pointwise
multiplication becomes spectral convolution, hence

\[
\operatorname{supp}\widehat F\subseteq S_A+S_B.
\]

Since \(|\operatorname{supp}\widehat F|\ge n-1\),

\[
\boxed{|S_A||S_B|\ge n-1.}
\]

Consequently

\[
\boxed{|S_A|+|S_B|\ge\lceil2\sqrt{n-1}\rceil.}
\]

If both leaves use one shared dictionary \(T=S_A\cup S_B\), unordered pair
capacity gives

\[
\boxed{\frac{|T|(|T|+1)}2\ge n-1.}
\]

Thus one multiplication gate cannot turn sub-root expanded spectral input into
exact parity.

## Direct rational evaluator

Now allow

\[
\frac{A(k)}{B(k)}=(-1)^k,
\qquad B(k)\ne0,
\qquad k\ne0.
\]

There is one unconstrained defect at the identity:

\[
A=\sigma B+d\delta_0.
\]

After Fourier transformation,

\[
\widehat A(r)
=
\frac1n\sum_{s\in S_B}
\frac{2\widehat B(s)}{1+\zeta^{s-r}}
+d.
\]

For rows \(r\notin S_A\), this is a homogeneous linear system in the active
\(B\)-coefficients and the defect \(d\). Its matrix has entries

\[
\frac1{1+x_r y_s},
\qquad x_r=\zeta^{-r},
\qquad y_s=\zeta^s,
\]

plus the defect column \(y=0\).

Every square minor is nonzero by the Cauchy double-alternant identity

\[
\det\left(\frac1{1+x_i y_j}\right)
=
\frac{
\prod_{i<j}(x_i-x_j)(y_j-y_i)
}{
\prod_{i,j}(1+x_i y_j)
}.
\]

The nodes are distinct and no denominator vanishes for odd \(n\). Therefore the
system is full spark. If \(|S_A|+|S_B|<n\), there are enough zero rows to force
all unknowns to zero, contradicting \(B\ne0\). Hence

\[
\boxed{|S_A|+|S_B|\ge n.}
\]

This bound is exact. Take \(B=1\), set \(A(0)=0\), and set
\(A(k)=(-1)^k\) for \(k\ne0\). Their support sizes are \(1\) and \(n-1\).
If the canonical value at zero is also required, the exact lower bound becomes
\(n+1\).

Charging a shared frequency dictionary only once gives

\[
\boxed{|S_A\cup S_B|\ge\left\lceil\frac n2\right\rceil.}
\]

So the direct quotient has a linear expanded-support barrier, stronger than the
root barrier for the one-product model.

## Exact secp256k1 values

For the secp256k1 subgroup order

\[
n=
115792089237316195423570985008687907852837564279074904382605163141518161494337,
\]

V19 obtains:

\[
|S_A|+|S_B|\ge n
\]

for the free-identity quotient model, and

\[
|S_A\cup S_B|\ge
57896044618658097711785492504343953926418782139537452191302581570759080747169.
\]

For one bilinear gate, the separately charged leaf-sum bound is

\[
680564733841876926926749214863536422911=2^{129}-1,
\]

and the shared-dictionary bound is

\[
481231938336009023090067544955250113853.
\]

## Replay and formal boundary

The executable package checks:

- the exact parity DFT formula on five frozen orders;
- the canonical support \(n\) and free-identity support \(n-1\);
- exact extremal rational witnesses;
- 6,895 exhaustive Cauchy minors for orders 5 and 7;
- 160 deterministic minors on the five frozen orders;
- exact secp256k1 integer bounds;
- six unit tests.

All finite checks pass with zero failures.

The Lean file kernel-checks the one-point defect decomposition and the fixed
secp256k1 arithmetic. It does not formalize Fourier transforms or the Cauchy
determinant. The determinant identity is classical; a modern reference is
Wenchang Chu, *The Cauchy double alternant and divided differences*, Electronic
Journal of Linear Algebra 15 (2006), DOI 10.13001/1081-3810.1218.

## Decision

V19 closes these direct shared classes:

- one bilinear product with sub-root expanded leaf support;
- one sparse additive-character quotient with sublinear separate or shared
  support.

The surviving route must leave this expanded one-layer spectral model. Useful
frontiers are deeper nonlinear circuits with implicit dense spectra, modular
composition, transposed evaluation, recurrence-compressed GLV-Kummer objects,
and p-adic, theta, or elliptic-unit representations.
