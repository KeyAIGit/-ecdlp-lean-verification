# UORC-056 C42: oriented transposed-resultant boundary

Date: 2026-08-16

Status: exact positive normal form plus scoped negative decoder boundary. The specialized Python, machine-readable, Lean, and artifact workflow is green. No cheap parity decoder, parity oracle, or sub-square-root ECDLP algorithm is claimed.

## 1. Central target

Let

\[
E:y^2=x^3+7,
\qquad
H=\langle G\rangle,
\qquad
|H|=n,
\]

and let

\[
Q=[k]G,
\qquad
1\le k<n.
\]

The target remains

\[
\sigma_G(Q)=(-1)^k.
\]

C37 supplies the compact public half-index Miller state

\[
F_G(Q)=M_h(G,Q,S),
\qquad
h=\frac{n-1}{2},
\]

where the shift \(S\in E(\mathbb F_{p^2})\) is public and the state is evaluated by a binary Miller chain.

C39 supplies the exact explicit decoder

\[
\sigma_G(Q)
=
\frac{P_{\rm odd}(F_G(Q))-P_{\rm even}(F_G(Q))}
     {P_{\rm odd}(F_G(Q))+P_{\rm even}(F_G(Q))}.
\]

The difficulty is that both orbit factors have degree \((n-1)/2\). C42 asks whether their values can be obtained on demand without constructing the factors or a comparable dense state.

## 2. Half-kernel algebra and query decomposition

Set

\[
m=\frac{n-1}{2}
\]

and define

\[
K_H(X)=\prod_{j=1}^{m}\bigl(X-x([j]G)\bigr).
\]

Let \(Y_G\) be the marked square root satisfying

\[
Y_G(x([j]G))=(-1)^j y([j]G).
\]

Write the Miller state on the half-kernel as

\[
F_G(P)=A(x(P))+y(P)B(x(P)).
\]

The exact interpolation replay verifies that \(B\) is nonzero on every half-kernel root in the declared corpus.

For a target value \(z=F_G(Q)\), define the two branch elements

\[
C_{\rm even}(X;z)=z-A(X)-Y_G(X)B(X),
\]

\[
C_{\rm odd}(X;z)=z-A(X)+Y_G(X)B(X).
\]

Their norms are the C39 orbit factors:

\[
P_{\rm even}(z)=\operatorname{Norm}(C_{\rm even}),
\qquad
P_{\rm odd}(z)=\operatorname{Norm}(C_{\rm odd}).
\]

## 3. Query-root localization theorem

At the known public root \(x_Q=x(Q)\), we have

\[
z=A(x_Q)+y_QB(x_Q)
\]

and

\[
Y_G(x_Q)=\sigma_G(Q)y_Q.
\]

Therefore

\[
C_{\rm even}(x_Q;z)
=(1-\sigma_G(Q))y_QB(x_Q),
\]

\[
C_{\rm odd}(x_Q;z)
=(1+\sigma_G(Q))y_QB(x_Q).
\]

Since \(y_QB(x_Q)\ne0\), exactly one branch vanishes and

\[
\boxed{
\frac{C_{\rm odd}(x_Q;z)-C_{\rm even}(x_Q;z)}
     {C_{\rm odd}(x_Q;z)+C_{\rm even}(x_Q;z)}
=
\frac{Y_G(x_Q)}{y_Q}
=
(-1)^k.
}
\]

This answers the first C42 question exactly:

```text
a transposed resultant that localizes the query root
reduces to the original oriented-root evaluation.
```

The localization is useful because it identifies the precise missing datum. It is not a cheap decoder, because the right side still requires the marked branch \(Y_G(x_Q)\).

## 4. Exact GLV cubic block factorization

For every declared \(j=0\) instance,

\[
n\equiv1\pmod6,
\qquad
m=3r,
\qquad
r=\frac{n-1}{6}.
\]

Let \(\beta\in\mathbb F_p\) be a nontrivial cube root of unity. The half-kernel root set is stable under

\[
X\longmapsto\beta X.
\]

Since \(3\mid m\), the monic kernel polynomial satisfies

\[
\boxed{K_H(X)=\kappa(X^3)}
\]

for one degree-\(r\) polynomial \(\kappa\).

Put

\[
T=X^3.
\]

Every residue class modulo \(K_H\) has the form

\[
C(X)=c_0(T)+Xc_1(T)+X^2c_2(T),
\]

where the \(c_i\) live in

\[
\mathcal K=\mathbb F_{p^2}[T]/(\kappa(T)).
\]

The relative norm over the cubic GLV block is

\[
\boxed{
N_3(C)
=
C(X)C(\beta X)C(\beta^2X)
=
c_0^3+Tc_1^3+T^2c_2^3-3Tc_0c_1c_2.
}
\]

Apply this to \(C_{\rm even}\) and \(C_{\rm odd}\):

\[
D_{\rm even}(T;z)=N_3(C_{\rm even}),
\qquad
D_{\rm odd}(T;z)=N_3(C_{\rm odd}).
\]

Then

\[
\boxed{
P_{\rm even}(z)
=
\operatorname{Norm}_{\mathcal K/\mathbb F_{p^2}}
D_{\rm even}(T;z),
}
\]

\[
\boxed{
P_{\rm odd}(z)
=
\operatorname{Norm}_{\mathcal K/\mathbb F_{p^2}}
D_{\rm odd}(T;z).
}
\]

Equivalently, each orbit factor is an outer resultant against \(\kappa\).

This is a genuine exact compression of the determinant dimension by a factor of three:

\[
\frac{n-1}{2}
\longrightarrow
\frac{n-1}{6}.
\]

It is not an asymptotic exponent improvement.

## 5. What the GLV block does not solve

The relative factors \(D_{\rm even}\) and \(D_{\rm odd}\) still contain \(Y_GB\). Thus the cubic norm does not remove the marked branch before the outer norm.

In the explicit coefficient grammar, the remaining objects have \(r+1\) coefficients. Exact replay finds \(\kappa\) dense on all five frozen curves and on the held-out curve. The target-dependent relative factors are also dense in essentially every declared row.

This density result is finite evidence for the declared representation. It is not an unrestricted arithmetic-circuit lower bound.

A multiplication-matrix determinant computes the outer norm exactly, but constructing the declared matrix or its coefficient generator still consumes linear-scale representation in \(r\). Merely naming a generic resultant, determinant, or modular-composition routine therefore does not satisfy the C42 gate.

## 6. secp256k1 cost frontier

For secp256k1,

\[
n=
115792089237316195423570985008687907852837564279074904382605163141518161494337.
\]

The explicit orbit degree is

\[
m=\frac{n-1}{2}
=
57896044618658097711785492504343953926418782139537452191302581570759080747168.
\]

The GLV block degree is

\[
r=\frac{n-1}{6}
=
19298681539552699237261830834781317975472927379845817397100860523586360249056.
\]

It has 254 bits. Its ceiling square root is

\[
138919694570470098040331481282401564370,
\]

which has 127 bits.

For the ordinary two-level product model, the exact minimum of

\[
b+\left\lceil\frac rb\right\rceil
\]

is

\[
277839389140940196080662962564803128739.
\]

Thus the GLV grouping improves constants, but the standard product frontier remains

\[
\Theta(\sqrt n),
\]

not

\[
O(n^{1/2-\varepsilon})
\]

for any fixed \(\varepsilon>0\).

This is a boundary for the declared explicit or two-level product mechanisms, not a theorem against every possible transposed resultant.

## 7. Anti-Frobenius 2 by 2 minor

C42 also tests a genuinely unsquared constant-width candidate.

Let

\[
f=F_G(Q),
\qquad
g=F_G(-Q).
\]

Define

\[
D(Q)=f\,g^p-g\,f^p,
\]

\[
S(Q)=f\,g^p+g\,f^p.
\]

The first value lies in the anti-Frobenius line and changes sign under \(Q\mapsto-Q\). The second lies in the base field and is symmetric. This candidate uses complete branch-sensitive field values and is not merely a square or norm.

The complete declared decoder grammar is

\[
\chi_p\bigl(aD_0(Q)+bS_0(Q)+c\bigr),
\qquad
(a:b:c)\in\mathbf P^2(\mathbb F_p),
\]

where \(D_0,S_0\in\mathbb F_p\) are the corresponding basis coefficients.

Across five frozen curves and one held-out curve, the exact screen covers

```text
59,544 projective affine character candidates,
0 exact survivors.
```

Canonical least-significant-bit and lower-half selectors of both coefficients also fail on every curve.

This closes only the stated anti-Frobenius minor grammar. Higher nonlinear functions of the two coefficients remain outside the claim.

## 8. Held-out validation

The held-out instance was not one of the five C39 frozen curves:

```text
p       61
n       61
G       (2,25)
beta    13
lambda  47
```

It is another prime-order \(j=0\) curve of the same structural family.

The combined exact replay covers

```text
6 curves,
498 target-root localization checks,
498 GLV relative-norm and outer-norm checks,
59,544 anti-Frobenius character candidates,
0 anti-Frobenius survivors,
0 arithmetic errors.
```

The specialized GitHub Actions run passes Python compilation, exact unit replay, machine-readable decision gates, Lean kernel checks, and artifact upload.

## 9. Decision

C42 establishes:

```text
Exact target-root localization                         found
Exact GLV cubic relative norm                          found
Outer determinant dimension                            (n-1)/6
Asymptotic exponent improvement                        no
Explicit quotient representation below square root     no
Anti-Frobenius affine-character decoder                no
Cheap parity decoder                                   not found
Parity oracle                                          not found
Sub-square-root ECDLP                                   not found
```

The most important conclusion is

\[
\boxed{
\text{the target-dependent resultant does not eliminate the branch;}\\
\text{at the query root it becomes exactly }Y_G(x_Q)/y_Q.
}
\]

## 10. Successor

The next package is

```text
LOCAL-GLV-GAUGE-BREAKING-C43.
```

It must act before the outer norm. The central target is an unsquared, anchor-normalized relation coupling the three local GLV branch values

\[
R(Q),
\qquad
R(\phi Q),
\qquad
R(\phi^2Q),
\]

such that independent component sign changes no longer preserve the relation.

A candidate depending only on branch squares, symmetric cubic norms, full orbit products, or a dense quotient table is already excluded by C39-C42 and is not a new mechanism.

## 11. Claim boundary

C42 does not claim:

1. an unrestricted resultant lower bound;
2. an unrestricted arithmetic-circuit lower bound;
3. production-size coefficient density for secp256k1;
4. optimality of every low-displacement determinant algorithm;
5. a parity oracle;
6. a sub-square-root ECDLP algorithm.

It gives an exact algebraic reduction, an exact finite replay, one held-out validation, a complete anti-Frobenius character closure, and a precise cost boundary for the declared explicit and two-level product mechanisms.
