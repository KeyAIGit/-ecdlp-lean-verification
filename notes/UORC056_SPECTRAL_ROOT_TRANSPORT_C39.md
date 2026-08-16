# UORC-056 C39: inversion spectral factor and quotient-root transport

Status: exact structural reduction plus scoped negative decoder results. No parity oracle or sub-square-root ECDLP algorithm is claimed.

## Starting state

Let

\[
h=(n-1)/2,
\qquad
M_h(P,Q,S)=f_{h,P}(S+Q)/f_{h,P}(S),
\]

where `S` is a public trace-zero regularizing point over `F_(p^2)`. Define

\[
U_P(Q)=\frac{M_h(P,Q,S)}{M_h(P,Q,-S)},
\qquad
W_G(Q)=U_G(Q)U_{-G}(Q).
\]

The source-negation covariance gives

\[
\boxed{W_G(-Q)=W_G(Q)^{-1}.}
\]

Put

\[
Z_G(Q)=W_G(Q)+W_G(Q)^{-1}\in\mathbb F_p,
\]

\[
A_G(Q)=W_G(Q)-W_G(Q)^{-1}\in \omega\mathbb F_p.
\]

Then `Z_G(-Q)=Z_G(Q)` and `A_G(-Q)=-A_G(Q)`.

## Inversion-odd decoder normal form

The invariant field of `W -> W^-1` is `F(Z)`, with `Z=W+W^-1`. Every inversion-odd Laurent expression is divisible by `W-W^-1`; after division it is invariant. Thus every inversion-compatible rational parity decoder has the form

\[
\boxed{D_G(Q)=A_G(Q)R_G(Z_G(Q)).}
\]

On the five frozen curves, the `r=(n-1)/2` values of `Z_G` on the pairs `{Q,-Q}` are distinct. The least polynomial correction has degree exactly `r-1`, every coefficient is nonzero, and the first rational relation appears only at the generic dimension threshold `floor(r/2)`.

| n | r | degree R | nonzero coefficients | first rational relation degree |
|---:|---:|---:|---:|---:|
| 31 | 15 | 14 | 15 | 7 |
| 79 | 39 | 38 | 39 | 19 |
| 67 | 33 | 32 | 33 | 16 |
| 127 | 63 | 62 | 63 | 31 |
| 139 | 69 | 68 | 69 | 34 |

The correction is also dense in the Dickson basis

\[
D_j(W+W^{-1})=W^j+W^{-j}.
\]

Berlekamp-Massey complexity of both monomial and Dickson coefficient sequences reaches the generic ceiling `ceil(r/2)` on every frozen curve. Hence no sparse symmetric Laurent/trace-power representation or low-order coefficient recurrence appears in the declared classes.

## Canonical square-root bits

Two cheap root-selection conventions were tested:

- lexicographic half-field sign;
- least-significant-bit sign.

The residual root bits were evaluated at the seven C34 public locations. On every frozen curve, the seven-bit tuple has collisions between even and odd scalars. Therefore no Boolean function whatsoever of those seven bits can decode parity, even curve-by-curve. Combining the `G` and `-G` source tuples into fourteen bits still leaves parity-mixed collisions; low-degree Boolean ANF screens also have no survivor.

## Reciprocal orbit factors

Because `n` is odd, exactly one scalar in every pair `{k,n-k}` is even. Since `W(-Q)=W(Q)^-1`, the odd-state orbit polynomial is reciprocal to the even-state orbit polynomial:

\[
P_{\rm odd}(X)
=
\frac{(-1)^r}{\prod_i w_i}
X^rP_{\rm even}(X^{-1}).
\]

Both factors are fully dense on every frozen curve. The full product is reciprocal and base-field defined, but it does not select which member of every inverse pair is the even one.

## Quotient-algebra root identity

Let

\[
K_Z(Z)=\prod_{i=1}^{r}(Z-z_i)
\]

be the public pair kernel. Since

\[
A_G(Q)^2=Z_G(Q)^2-4
\]

and

\[
\sigma_G(Q)=A_G(Q)R_G(Z_G(Q)),
\]

we obtain

\[
\boxed{(Z^2-4)R_G(Z)^2\equiv1\pmod{K_Z(Z)}.}
\]

This congruence was checked exactly on all five frozen curves and all 438 nonzero base-generator rows.

The algebra `F_p[Z]/(K_Z)` splits into `r` base-field components. Consequently the public square equation has exactly

\[
\boxed{2^r}
\]

componentwise roots. The generator orientation selects one sign in every component. A single public anchor fixes only one component sign; without an additional coherence law, `2^(r-1)` component choices remain.

Thus the spectral-factor route transports the original oriented-root problem rather than eliminating it:

\[
Y_G^2=F\pmod{K_H}
\quad\longrightarrow\quad
R_G^2=(Z^2-4)^{-1}\pmod{K_Z}.
\]

The interpolation maps between the old pair coordinate `x` and the new coordinate `Z` have degree `r-1` and full support on every frozen curve.

## Decision

No cheap exact parity decoder was found.

Closed in this package:

- normalized quadratic-character, LSB and half-field signs of the inversion-odd coordinate;
- every product of the seven normalized Legendre atoms;
- every Boolean function of the seven canonical root bits, by mixed collisions;
- low-degree Boolean functions of the fourteen `G/-G` root bits;
- low-degree inversion-odd polynomial/rational corrections;
- sparse monomial and sparse Dickson/Laurent corrections;
- low-order coefficient recurrences;
- the claim that the public reciprocal orbit polynomial alone selects the parity factor.

The key conclusion is

\[
\boxed{
\text{a short resultant for the chosen spectral factor would already be an oriented-root evaluator.}
}
\]

The next valid frontier is a public low-cost coherence law coupling the component signs: a GLV-equivariant nonlinear relation, an anchor-normalized recursive norm/resultant, or a theta/elliptic-net constraint proving that the selected root lies in a low-dimensional subvariety.