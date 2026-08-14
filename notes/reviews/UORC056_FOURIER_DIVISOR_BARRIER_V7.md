# UORC-056 Fourier-to-divisor barrier V7

Status: **elementary spectral reduction proved; elliptic sheaf bound isolated as the next exact proof obligation**.

Central target remains unchanged:

\[
A(E,G,Q)=\frac{Y_G(x(Q))}{y(Q)}=(-1)^k,
\qquad Q=[k]G,
\]

with total evaluator cost below the square-root baseline. This checkpoint does not replace that target. It isolates a rigorous obstruction for one important candidate class: exact evaluators represented by a quadratic character of a rational function, including divisor-aware regularizations.

## 1. Why this checkpoint is different

Previous bounded screens excluded finite dictionaries of affine, pulled-line, reducible-conic and small Miller factors. A larger enumeration of the same type would only produce another bounded negative.

The present route asks for an asymptotic invariant shared by every exact rational-character evaluator:

\[
P\longmapsto \chi(R(P)).
\]

The invariant is the Fourier spectrum on the marked cyclic group. Canonical scalar parity has a Fourier coefficient of order \(n\), while a nondegenerate rational-character trace on an elliptic curve is expected to have square-root cancellation controlled by the odd divisor support of \(R\). Comparing the two produces an \(\Omega(\sqrt n)\) lower bound on that support.

This would be a genuine class theorem, not a grammar-specific screen.

## 2. Exact parity spectrum

Let \(H=\langle G\rangle\) have odd order \(n\). For the nonidentity points write

\[
\sigma([k]G)=(-1)^k,
\qquad 1\le k<n.
\]

Let

\[
\eta_r([k]G)=\zeta^{rk},
\qquad \zeta=e^{-2\pi i/n}.
\]

The nonidentity Fourier coefficient is

\[
\widehat\sigma^{\times}(r)
=
\sum_{k=1}^{n-1}(-1)^k\zeta^{rk}.
\]

Put \(z=\zeta^r\). Since \(n\) is odd and \(z^n=1\),

\[
\sum_{k=0}^{n-1}(-z)^k
=
\frac{1-(-z)^n}{1+z}
=
\frac{2}{1+z}.
\]

Removing the \(k=0\) term gives the exact identity

\[
\boxed{
\widehat\sigma^{\times}(r)
=
\frac{1-z}{1+z}
}.
\]

Choose the near-half frequency

\[
r_\star=\frac{n-1}{2}.
\]

Then \(z=-e^{\pi i/n}\), and therefore

\[
\boxed{
\left|\widehat\sigma^{\times}(r_\star)\right|
=
\cot\!\left(\frac{\pi}{2n}\right)
}.
\]

Consequently,

\[
\frac{1}{n}
\left|\widehat\sigma^{\times}(r_\star)\right|
\longrightarrow
\frac{2}{\pi}.
\]

Canonical parity is therefore spectrally rigid: one nontrivial group character correlates with it at asymptotic amplitude approximately \(0.63662n\).

This part is elementary and complete. The accompanying script independently replays the geometric-series formula on all five frozen odd orders.

## 3. The candidate rational-character class

Let \(E/\mathbb F_p\) be an elliptic curve and assume, as for secp256k1, that

\[
E(\mathbb F_p)=\langle G\rangle,
\qquad \#E(\mathbb F_p)=n,
\]

with odd prime \(n\).

Let \(\chi\) be the quadratic character of \(\mathbb F_p^\times\), and let

\[
R\in\mathbb F_p(E)^\times.
\]

Define the geometric odd-valuation support

\[
S_{\rm odd}(R)
=
\left\{
P\in E(\overline{\mathbb F}_p):
\operatorname{ord}_P(R)\equiv1\pmod2
\right\},
\]

and put

\[
s(R)=\#S_{\rm odd}(R).
\]

Only this square-free divisor part matters to a quadratic character. Multiplying \(R\) by a square changes neither the ordinary character values nor the Kummer sheaf.

At a rational zero or pole, a divisor-aware evaluator may assign the character of the first nonzero local coefficient rather than the ordinary extended value \(\chi(0)=0\). This is allowed in the transfer below, but every changed rational support point is charged.

## 4. The exact hybrid-sum lemma to prove

The needed theorem is the following.

### FDB-1: elliptic Kummer-Lang trace bound

Let \(\eta\) be a nontrivial character of the finite group \(E(\mathbb F_p)\). For a rational function \(R\), let \(\mathcal K_R\) be the quadratic Kummer middle-extension sheaf associated with \(R\), and let \(\mathcal L_\eta\) be the rank-one Lang character sheaf whose trace on rational points is \(\eta\). Then

\[
\boxed{
\left|
\sum_{P\in E(\mathbb F_p)}
\eta(P)\operatorname{Tr}(\mathcal K_R)_P
\right|
\le
C_{\rm sh}\,s(R)\sqrt p
}
\]

for an absolute normalization constant \(C_{\rm sh}\). The expected sharp normalization is \(C_{\rm sh}=1\).

### Proof architecture

The intended proof has four standard components.

1. The Lang isogeny \(F-1:E\to E\) has kernel \(E(\mathbb F_p)\). A character \(\eta\) of that kernel produces a lisse rank-one sheaf \(\mathcal L_\eta\) with trace function \(\eta(P)\).

2. On

   \[
   U=E\setminus S_{\rm odd}(R),
   \]

   the quadratic Kummer sheaf \(\mathcal K_R\) is lisse, rank one, tame and pure of weight zero.

3. The tensor

   \[
   \mathcal F=\mathcal L_\eta\otimes\mathcal K_R
   \]

   is geometrically nontrivial at the peak frequency. Here \(\eta\) has odd order \(n\), whereas the Kummer factor has order dividing two, so they cannot cancel to the trivial geometric character.

4. For genus one, Grothendieck-Ogg-Shafarevich gives

   \[
   \dim H_c^1(U_{\overline{\mathbb F}_p},\mathcal F)
   =s(R)
   \]

   when \(H_c^0\) and \(H_c^2\) vanish and the ramification is tame. Deligne's weight bound then gives the claimed \(s(R)\sqrt p\) trace estimate.

This proof architecture is mathematically coherent, but this checkpoint does not yet promote FDB-1 to a verified theorem. The following details must be source-locked and checked without handwaving:

- the precise Lang-sheaf trace normalization;
- geometric nontriviality after tensoring;
- treatment of even divisors and unramified quadratic Kummer classes;
- middle-extension traces at rational ramification points;
- the exact conductor constant in Grothendieck-Ogg-Shafarevich;
- compatibility with the chosen complex embedding of the character values.

## 5. Transfer from FDB-1 to a divisor-support lower bound

Assume an exact evaluator satisfies

\[
\widetilde\chi_R([k]G)=(-1)^k,
\qquad 1\le k<n,
\]

where \(\widetilde\chi_R\) agrees with the Kummer trace away from divisor support and may regularize rational support points by local leading coefficients.

Choose \(\eta=\eta_{r_\star}\). The exact parity side has magnitude

\[
\cot\!\left(\frac{\pi}{2n}\right).
\]

Replacing middle-extension values by regularized values changes at most \(s(R)\) rational terms, each by magnitude at most one. Omitting or assigning the identity changes at most one additional term. Therefore FDB-1 implies

\[
\cot\!\left(\frac{\pi}{2n}\right)
\le
C_{\rm sh}s(R)\sqrt p+s(R)+1.
\]

Hence

\[
\boxed{
 s(R)
\ge
\frac{
\cot\!\left(\frac{\pi}{2n}\right)-1
}{
C_{\rm sh}\sqrt p+1
}
}.
\]

When \(n\asymp p\),

\[
\boxed{s(R)=\Omega(\sqrt n)}.
\]

This reduction is elementary once FDB-1 is available.

## 6. secp256k1 specialization

For secp256k1,

\[
p=2^{256}-2^{32}-977,
\]

\[
n=
\texttt{FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141}_{16},
\]

and the cofactor is one, so the marked subgroup is the whole rational point group.

The peak is

\[
\left|\widehat\sigma^{\times}(r_\star)\right|
\approx
7.37155334922269019018\times10^{76}.
\]

The ratio to \(n\) agrees with \(2/\pi\) to the displayed precision.

Under the conditional FDB-1 normalization, the resulting lower bounds for the geometric odd divisor support are approximately:

| \(C_{\rm sh}\) | required \(s(R)\), rounded upward |
|---:|---:|
| 1 | 216630482969909636093804454941121895872 |
| 2 | 108315241484954818046902227470560947936 |
| 4 | 54157620742477409023451113735280473968 |
| 8 | 27078810371238704511725556867640236984 |

Even allowing a substantial constant, the required support remains on the order of \(2^{124}\) to \(2^{127}\).

These numbers are conditional consequences of FDB-1, not a completed lower bound until its sheaf statement is fully verified.

## 7. What this would close

After FDB-1 is proved, the following exact mechanisms are asymptotically excluded unless their square-free divisor support reaches square-root scale:

- a single bounded-degree rational character;
- a bounded product or quotient of affine-line characters;
- bounded pulled-line products with exact zero-pole cancellation;
- bounded products of small Miller primitives;
- any fixed divisor-degree family independent of \(n\);
- any family with \(s(R)=o(\sqrt n)\).

This subsumes the finite V1-V6 screens at the level of an asymptotic class theorem.

## 8. What this does not close

The result is not an arithmetic-circuit lower bound.

A short nonlinear straight-line program can define a rational function of enormous degree and potentially enormous square-free divisor support. Therefore

\[
s(R)=\Omega(\sqrt n)
\]

does not by itself imply that evaluating \(R(Q)\) costs \(\Omega(\sqrt n)\).

The following remain open even after FDB-1:

- high-degree, low-size straight-line programs;
- direct field-valued evaluation of \(Y_G(x(Q))/y(Q)\) without a quadratic character;
- transposed or multipoint representations that do not materialize the divisor;
- level-\(n\) theta or elliptic-unit formulas with compact evaluation;
- index-growing EDS or Miller constructions;
- non-rational special-function representations.

Thus the barrier is strong but correctly scoped.

## 9. Immediate execution sequence

1. Source-lock FDB-1 against primary references on Lang sheaves, Kummer sheaves, Grothendieck-Ogg-Shafarevich and Deligne weights.
2. Write the theorem with exact conventions for zeros, poles and middle-extension traces.
3. Prove the odd-order noncancellation lemma for the Lang and quadratic Kummer factors.
4. Kernel-check the elementary geometric-series identity separately from the sheaf theorem.
5. Promote the support bound only after the exact conductor constant is verified.
6. If FDB-1 fails in the stated form, construct the smallest counterexample and identify whether the defect is normalization, geometric triviality or rational ramification.
7. After closure, redirect constructive search toward high-degree low-size circuits rather than more bounded divisor dictionaries.

## 10. References to source-lock

- P. Deligne, *La conjecture de Weil II*, Publications Mathématiques de l'IHÉS 52 (1980).
- Grothendieck-Ogg-Shafarevich Euler characteristic formula for lisse sheaves on curves.
- N. Katz, treatments of Kummer sheaves, trace functions and rank-one character sheaves.
- D. R. Kohel and I. E. Shparlinski, *On Exponential Sums and Group Generators for Elliptic Curves over Finite Fields*, ANTS-IV, LNCS 1838 (2000), 395-404.
- I. E. Shparlinski and K. E. Stange, *Character Sums with Division Polynomials*, Canadian Mathematical Bulletin 55 (2012), 850-857.

## 11. Claim boundary

This checkpoint proves the exact parity Fourier identity and its large peak. It supplies a complete reduction from an elliptic hybrid character-sum bound to an odd-divisor-support lower bound. It does not yet claim that the sheaf bound has been kernel-checked, and it does not claim a general circuit lower bound or a sub-square-root ECDLP algorithm.
