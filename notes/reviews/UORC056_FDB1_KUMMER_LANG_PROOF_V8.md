# UORC-056 FDB-1 Kummer-Lang source audit V8

Status: **source-lock audit complete; theorem remains provisional pending independent specialist review; Lean kernel formalization is unavailable in the current library stack**.

This note is a source and normalization audit for the subgroup-general theorem in
`UORC056_REGULARIZED_FOURIER_DIVISOR_BARRIER_V8.md`. It is not a second,
competing theorem statement.

The central UORC-056 target remains

\[
A(E,G,Q)=\frac{Y_G(x(Q))}{y(Q)}=(-1)^k,
\qquad Q=[k]G.
\]

The result below obstructs exact evaluators that collapse to a quadratic
character of a rational function. It is not a lower bound for unrestricted
arithmetic circuits.

## 1. Subgroup-general statement

Let \(q\) be odd, let \(E/\mathbb F_q\) be an elliptic curve, and let

\[
H=\langle G\rangle\subseteq E(\mathbb F_q)
\]

have odd order \(n\). Let

\[
f\in\mathbb F_q(E)^\times,
\]

and define

\[
S_{\rm odd}(f)
=
\left\{
P\in E(\overline{\mathbb F}_q):
\operatorname{ord}_P(f)\equiv1\pmod2
\right\},
\qquad
s(f)=\#S_{\rm odd}(f).
\]

Away from the divisor, let the evaluator equal \(\chi(f(P))\). At rational
odd-support points, allow any unit-modulus regularized value, including the
local-leading-coefficient convention used in the V1-V6 screens.

If

\[
\widetilde\chi_f([k]G)=(-1)^k,
\qquad 1\le k<n,
\]

then the provisional theorem is

\[
\boxed{
\cot\!\left(\frac{\pi}{2n}\right)
\le
s(f)\sqrt q+s(f)+1
}
\]

and hence

\[
\boxed{
 s(f)
\ge
\frac{
\cot\!\left(\frac{\pi}{2n}\right)-1
}{
\sqrt q+1
}
}.
\tag{FDB-2}
\]

For \(n\asymp q\), this gives

\[
s(f)=\Omega(\sqrt n).
\]

## 2. Exact Fourier input

For odd \(n\), put

\[
\sigma([k]G)=(-1)^k,
\qquad 1\le k<n.
\]

At the near-half frequency

\[
r_\star=\frac{n-1}{2},
\]

one has

\[
\sum_{k=1}^{n-1}(-1)^kz^k
=
\frac{1-z}{1+z},
\qquad
z=e^{-2\pi i r_\star/n},
\]

and therefore

\[
\boxed{
\left|
\sum_{k=1}^{n-1}(-1)^kz^k
\right|
=
\cot\!\left(\frac{\pi}{2n}\right)
}.
\]

Moreover,

\[
\gcd\!\left(\frac{n-1}{2},n\right)=1,
\]

so the peak character on \(H\) is faithful and has exact odd order \(n\).

This part is elementary and is independently replayed by the V7 and V8
scripts.

## 3. From the subgroup to complete elliptic sums

Let

\[
A=E(\mathbb F_q),
\qquad m=[A:H].
\]

Every character of a subgroup of a finite abelian group extends to the full
group. Extend the faithful peak character \(\eta\) of \(H\) to a character
\(\theta\) of \(A\). With

\[
H^\perp=
\{\psi\in\widehat A:\psi|_H=1\},
\]

orthogonality gives

\[
1_H(P)=\frac1m\sum_{\psi\in H^\perp}\psi(P).
\]

Thus every subgroup sum is the average of complete sums twisted by
\(\theta\psi\). Each twist still restricts to the faithful odd-order character
\(\eta\) on \(H\). This removes any cofactor-one assumption.

## 4. Source-locked sheaf inputs

For every complete twist \(\theta\psi\), use the rank-one Lang character sheaf

\[
\mathcal L_{\theta\psi}
\]

on \(E\). Its trace function is the corresponding finite-group character,
up to the standard inverse convention between arithmetic and geometric
Frobenius.

For \(f\), use the quadratic Kummer middle extension

\[
\mathcal K_f.
\]

It is rank one, lisse on

\[
U=E\setminus S_{\rm odd}(f),
\]

tame at every puncture, pure of weight zero, and has Swan conductor zero. At a
rational odd-support point its middle-extension trace is zero. Even-order
zeros and poles are not punctures for the square-free Kummer class.

The tensor

\[
\mathcal F_\psi
=
\mathcal L_{\theta\psi}\otimes\mathcal K_f
\]

is geometrically nontrivial. Its Lang factor restricts to an odd-order faithful
character on \(H\), while the Kummer factor has geometric order dividing two.
They cannot cancel.

## 5. Exact conductor constant

The sheaf \(\mathcal F_\psi\) is rank one, tame and geometrically nontrivial.
Consequently,

\[
H_c^0(U_{\overline{\mathbb F}_q},\mathcal F_\psi)=0,
\qquad
H_c^2(U_{\overline{\mathbb F}_q},\mathcal F_\psi)=0.
\]

Since \(E\) has genus one, Grothendieck-Ogg-Shafarevich gives

\[
\chi_c(U_{\overline{\mathbb F}_q},\mathcal F_\psi)
=2-2\cdot1-s(f)
=-s(f).
\]

Hence

\[
\boxed{
\dim H_c^1(U_{\overline{\mathbb F}_q},\mathcal F_\psi)=s(f)
}.
\]

The Grothendieck-Lefschetz trace formula and Deligne's weight theorem then give

\[
\boxed{
\left|
\sum_{P\in E(\mathbb F_q)}
(\theta\psi)(P)t_f(P)
\right|
\le
s(f)\sqrt q
}.
\tag{FDB-1}
\]

Averaging over \(H^\perp\) preserves the same upper bound for the subgroup
sum. Under these conventions the sheaf constant is exactly one.

## 6. Divisor-aware regularization

At a rational odd-support point, the middle-extension trace is zero, while the
evaluator may return a unit-modulus regularized value. Each replacement changes
the sum by at most one. There are at most \(s(f)\) such rational points.
Adding or removing the identity changes the nonidentity Fourier coefficient by
at most one more term.

Therefore

\[
\cot\!\left(\frac{\pi}{2n}\right)
\le
s(f)\sqrt q+s(f)+1,
\]

which proves the transfer from FDB-1 to FDB-2.

Products and quotients of quadratic-character atoms collapse to one rational
function. Local orders add and local leading units multiply. Thus the theorem
covers the aggregate regularization used by V1-V6, not only a single primitive
atom.

## 7. Certified secp256k1 consequence

For secp256k1, the public parameters have cofactor one. The executable V8
certificate avoids trusting a floating-point cotangent by proving an explicit
rational lower bound for \(\cot(\pi/(2n))\) and using exact integer square
comparisons for the radical denominator.

It certifies

\[
\boxed{
 s(f)
\ge
216543324404233567658511113820216134562
}
\]

and therefore

\[
\boxed{
\deg(f:E\to\mathbb P^1)
\ge
108271662202116783829255556910108067281
}.
\]

The certified support bound has binary size 127. A separate high-precision
calculation gives a slightly larger analytic estimate, but that estimate is not
used as the rigorous integer certificate.

## 8. Independent published cross-check

Kohel and Shparlinski prove a direct hybrid estimate of the form

\[
\left|
\sum_{P\in E(\mathbb F_q)}
\omega(P)\chi(f(P))
\right|
\le
2\deg(f)\sqrt q
\]

under their standard nontriviality condition. This degree-based result is
weaker when large square factors are present, but independently confirms the
same complete-sum square-root cancellation mechanism.

## 9. Exact scope

The provisional theorem closes exact rational-character mechanisms with

\[
s(f)=o\!\left(\frac{n}{\sqrt q}\right).
\]

For secp256k1 this means every such mechanism with odd divisor support below
square-root scale. It subsumes the bounded affine, pulled-line, reducible-conic,
global-balance and small-Miller character dictionaries.

It does not close:

1. high-degree rational functions represented by short nonlinear
   straight-line programs;
2. direct field-valued evaluation of \(Y_G(x(Q))/y(Q)\) without an outer
   quadratic character;
3. transposed or modular-composition representations that avoid materializing
   the divisor;
4. level-\(n\) theta or elliptic-unit formulas with compact evaluation;
5. index-growing EDS or Miller recurrences with compact global normalization;
6. non-rational special-function representations;
7. adaptive branching or general arithmetic circuits.

Large divisor support is not by itself a circuit-size lower bound.

## 10. Verification boundary

The status is deliberately split:

```text
source-lock and normalization audit: complete
arithmetic specialization: reproducibly certified
independent specialist review: pending
peer review: absent
Lean kernel proof of the sheaf theorem: unavailable in the current stack
```

The current Mathlib environment does not jointly provide Lang character
sheaves, quadratic Kummer middle extensions, compactly supported etale
cohomology, Grothendieck-Ogg-Shafarevich and Deligne weights. No `axiom`,
`sorry`, or informal placeholder is presented as a kernel-checked theorem.

## 11. Primary references

1. Clifton Cunningham and David Roe, *From the function-sheaf dictionary to
   quasicharacters of p-adic tori*, especially Theorem 3.6.
2. Etienne Fouvry, Emmanuel Kowalski and Philippe Michel, *Trace functions over
   finite fields and applications*, especially Theorems 2.3.1, 4.1.7 and
   4.1.9.
3. SGA 5, Expose X, formula 7.2.
4. Pierre Deligne, *La conjecture de Weil II*, Publications Mathematiques de
   l'IHES 52 (1980), 137-252.
5. David Kohel and Igor Shparlinski, *On Exponential Sums and Group Generators
   for Elliptic Curves over Finite Fields*, ANTS-IV, LNCS 1838 (2000),
   395-404.
