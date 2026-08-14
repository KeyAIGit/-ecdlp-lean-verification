# UORC-056 FDB-1 Kummer-Lang proof V8

Status: **source-locked mathematical proof complete; Lean kernel formalization unavailable in the current library stack**.

The central UORC-056 target is unchanged:

\[
A(E,G,Q)=\frac{Y_G(x(Q))}{y(Q)}=(-1)^k,
\qquad Q=[k]G.
\]

This checkpoint proves an asymptotic obstruction for exact evaluators represented by a quadratic character of a rational function. It does not prove a lower bound for unrestricted arithmetic circuits.

## 1. Exact theorem

Let \(q\) be odd, let \(E/\mathbb F_q\) be an elliptic curve, and let

\[
\eta:E(\mathbb F_q)\longrightarrow \mathbb C^\times
\]

be a nontrivial character of odd order. Let

\[
R\in\mathbb F_q(E)^\times.
\]

Define the geometric odd-valuation support

\[
S_{\rm odd}(R)
=
\left\{
P\in E(\overline{\mathbb F}_q):
\operatorname{ord}_P(R)\equiv1\pmod2
\right\},
\qquad
s(R)=\#S_{\rm odd}(R).
\]

Let \(t_R(P)\) be the trace function of the quadratic Kummer middle extension associated with \(R\). Thus, at rational points outside \(S_{\rm odd}(R)\),

\[
t_R(P)=\chi(R(P)),
\]

and at a rational point in \(S_{\rm odd}(R)\),

\[
t_R(P)=0.
\]

Then

\[
\boxed{
\left|
\sum_{P\in E(\mathbb F_q)}
\eta(P)t_R(P)
\right|
\le
s(R)\sqrt q
}.
\tag{FDB-1}
\]

If \(s(R)=0\), the sum is exactly zero.

The constant is one. No degree surrogate is needed: the controlling invariant is the number of geometric points where the valuation of \(R\) is odd.

## 2. Source-locked ingredients

### 2.1 Character sheaf for \(\eta\)

For a smooth connected commutative group over a finite field, the function-sheaf dictionary identifies characters of the finite group of rational points with rank-one character sheaves. Applied to \(E\), it gives a rank-one lisse sheaf

\[
\mathcal L_\eta
\]

on all of \(E\), pure of weight zero, whose trace function is \(\eta\), up to the harmless inverse convention for geometric versus arithmetic Frobenius.

The precise source is Cunningham and Roe, *From the function-sheaf dictionary to quasicharacters of p-adic tori*, Theorem 3.6. Since \(E\) is connected, its component group is trivial, so the trace-of-Frobenius map is an isomorphism on isomorphism classes.

### 2.2 Quadratic Kummer sheaf for \(R\)

Pull back the quadratic Kummer local system on \(\mathbb G_m\) by \(R\). After extending across points with even valuation, one obtains a rank-one sheaf

\[
\mathcal K_R
\]

lisse on

\[
U=E\setminus S_{\rm odd}(R).
\]

It is tame at every point of \(S_{\rm odd}(R)\), has Swan conductor zero, and is pure of weight zero. Its local inertia action at every point of \(S_{\rm odd}(R)\) is the nontrivial quadratic character, so the middle-extension stalk has no inertia invariants and its trace there is zero.

This is the curve-pullback form of the Kummer construction in Fouvry, Kowalski and Michel, *Trace functions over finite fields and applications*, Theorem 2.3.1.

### 2.3 Euler characteristic and weights

For a rank-one lisse sheaf \(\mathcal F\) on an open curve \(U=C\setminus S\), the Grothendieck-Ogg-Shafarevich formula is

\[
\chi_c(U_{\overline{\mathbb F}_q},\mathcal F)
=
\operatorname{rank}(\mathcal F)(2-2g(C)-\#S)
-
\sum_{x\in S}\operatorname{Swan}_x(\mathcal F).
\]

The general curve formula is SGA 5, Expose X, formula 7.2. The genus-zero specialization and the cohomological trace-bound mechanism are presented in Fouvry, Kowalski and Michel, Theorems 4.1.7 and 4.1.9.

Deligne's weight theorem bounds every Frobenius eigenvalue on \(H_c^1\) by \(\sqrt q\) for a weight-zero sheaf.

## 3. Geometric nontriviality

Set

\[
\mathcal F
=
\mathcal L_\eta\otimes\mathcal K_R
\quad\text{on }U.
\]

The only possible obstruction to square-root cancellation would be geometric triviality of \(\mathcal F\).

The geometric order of \(\mathcal L_\eta\) equals the order of \(\eta\). Indeed, if a tensor power \(\mathcal L_\eta^{\otimes a}\) were geometrically trivial, its trace function would be a constant arithmetic twist. Evaluation at the identity gives that constant as one, so \(\eta^a=1\). The converse follows from the character-sheaf dictionary.

Therefore \(\mathcal L_\eta\) has odd geometric order greater than one. The geometric order of \(\mathcal K_R\) divides two. Hence

\[
\mathcal L_\eta\otimes\mathcal K_R
\not\simeq
\mathbf 1
\]

geometrically.

For the parity peak character on an odd cyclic group of order \(n\),

\[
r_\star=\frac{n-1}{2},
\qquad
\gcd(r_\star,n)=1,
\]

so the peak character has exact order \(n\). The required odd-order hypothesis is automatic.

## 4. Cohomological dimension

The sheaf \(\mathcal F\) is rank one, tame, and geometrically nontrivial.

First,

\[
H_c^0(U_{\overline{\mathbb F}_q},\mathcal F)=0.
\]

When \(S_{\rm odd}(R)\ne\varnothing\), the open curve is nonproper and a nonzero lisse section cannot have compact support. When the support is empty, geometric nontriviality removes global invariants.

Second, Poincare duality and geometric nontriviality give

\[
H_c^2(U_{\overline{\mathbb F}_q},\mathcal F)=0.
\]

Since \(E\) has genus one and all Swan conductors vanish, Grothendieck-Ogg-Shafarevich gives

\[
\chi_c(U,\mathcal F)
=2-2\cdot1-s(R)
=-s(R).
\]

Consequently,

\[
\boxed{
\dim H_c^1(U_{\overline{\mathbb F}_q},\mathcal F)=s(R)
}.
\]

This also covers \(s(R)=0\), where all three compactly supported cohomology groups vanish.

## 5. Trace estimate

The Grothendieck-Lefschetz trace formula gives

\[
\sum_{P\in E(\mathbb F_q)}
\eta(P)t_R(P)
=
-
\operatorname{Tr}
\left(
\operatorname{Frob}_q
\mid
H_c^1(U_{\overline{\mathbb F}_q},\mathcal F)
\right).
\]

The sheaf \(\mathcal F\) is pure of weight zero. Deligne's theorem therefore bounds each of the \(s(R)\) eigenvalues by \(\sqrt q\). The triangle inequality proves

\[
\left|
\sum_{P\in E(\mathbb F_q)}
\eta(P)t_R(P)
\right|
\le
s(R)\sqrt q.
\]

This proves FDB-1 with \(C_{\rm sh}=1\).

## 6. Divisor-aware regularization

Suppose an evaluator replaces the middle-extension value zero at a rational odd-support point by the quadratic character of a first nonzero local coefficient. Call the resulting function \(\widetilde\chi_R\).

At every rational point outside the odd support,

\[
\widetilde\chi_R(P)=t_R(P).
\]

At a rational point of odd support, the two values differ in absolute value by one. Therefore

\[
\left|
\sum_{P\in E(\mathbb F_q)}
\eta(P)\widetilde\chi_R(P)
\right|
\le
s(R)\sqrt q+s(R).
\]

If the target parity sequence is specified only on nonidentity points, adding or removing the identity changes the coefficient by at most one. Thus an exact rational-character parity evaluator satisfies

\[
\cot\!\left(\frac{\pi}{2n}\right)
\le
s(R)\sqrt q+s(R)+1,
\]

and hence

\[
\boxed{
 s(R)
\ge
\frac{
\cot\!\left(\frac{\pi}{2n}\right)-1
}{
\sqrt q+1
}
}.
\tag{FDB-2}
\]

For \(n\asymp q\), this is

\[
s(R)=\Omega(\sqrt n).
\]

## 7. secp256k1 consequence

For secp256k1, the cofactor is one and

\[
E(\mathbb F_p)=\langle G\rangle
\]

has odd prime order \(n\). The peak character therefore has exact odd order \(n\), and FDB-1 applies directly.

Using the fixed public values of \(p\) and \(n\), FDB-2 gives

\[
\boxed{
 s(R)
\ge
216630482969909636093804454941121895872
}.
\]

This is approximately \(2^{127.35}\) geometric odd-valuation points.

Accordingly, no exact divisor-aware evaluator of the form

\[
Q\longmapsto\chi(R(Q))
\]

can realize canonical parity when the square-free divisor support of \(R\) is \(o(\sqrt n)\).

## 8. Independent published cross-check

Kohel and Shparlinski, *On Exponential Sums and Group Generators for Elliptic Curves over Finite Fields*, prove a direct hybrid character-sum estimate of the form

\[
\left|
\sum_{P\in E(\mathbb F_q)}
\omega(P)\chi(f(P))
\right|
\le
2\deg(f)\sqrt q
\]

under the standard nontriviality condition. Their degree-based theorem is weaker than FDB-1 when large square factors are present, but it independently confirms the square-root cancellation mechanism for a group-character twist of a rational-character trace.

## 9. Exact scope

FDB-1 and FDB-2 close, asymptotically, all exact rational-character mechanisms whose geometric odd divisor support is \(o(\sqrt n)\), including any fixed-divisor-degree family and all bounded V1-V6 dictionaries.

They do not close:

1. high-degree rational functions represented by short nonlinear straight-line programs;
2. direct field-valued evaluation of \(Y_G(x(Q))/y(Q)\) without an outer quadratic character;
3. transposed or modular-composition representations that avoid materializing the divisor;
4. level-\(n\) theta or elliptic-unit formulas with compact evaluation;
5. index-growing EDS or Miller constructions with compact global normalization;
6. non-rational special-function representations.

A large divisor can be generated by a small circuit, so divisor support is not a circuit-size lower bound.

## 10. Formalization boundary

The elementary parity Fourier identity is suitable for Lean and should be kernel-checked separately.

The current Mathlib stack does not provide the full infrastructure required to formalize FDB-1 end to end: Lang character sheaves, quadratic Kummer middle extensions, compactly supported etale cohomology, Grothendieck-Ogg-Shafarevich and Deligne weights. For that reason the status is:

```text
mathematical proof: complete and source-locked
numerical consequence: reproducibly checked
Lean kernel proof: unavailable in the current library stack
```

This boundary is explicit. No `axiom`, `sorry`, or informal placeholder is being presented as a kernel-checked theorem.

## 11. Primary references

1. Clifton Cunningham and David Roe, *From the function-sheaf dictionary to quasicharacters of p-adic tori*, especially Theorem 3.6.
2. Etienne Fouvry, Emmanuel Kowalski and Philippe Michel, *Trace functions over finite fields and applications*, especially Theorems 2.3.1, 4.1.7 and 4.1.9.
3. Alexander Grothendieck et al., *Cohomologie l-adique et fonctions L*, SGA 5, Expose X, formula 7.2.
4. Pierre Deligne, *La conjecture de Weil II*, Publications Mathematiques de l'IHES 52 (1980), 137-252.
5. David Kohel and Igor Shparlinski, *On Exponential Sums and Group Generators for Elliptic Curves over Finite Fields*, ANTS-IV, LNCS 1838 (2000), 395-404.
