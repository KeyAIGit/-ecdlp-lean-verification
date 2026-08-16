# UORC-056 C39: inversion spectral factor and quotient-root transport

Status: exact structural reduction plus scoped negative decoder results. No parity oracle or sub-square-root ECDLP algorithm is claimed.

For `h=(n-1)/2`, define

\[
U_P(Q)=M_h(P,Q,S)/M_h(P,Q,-S),
\qquad
W_G(Q)=U_G(Q)U_{-G}(Q).
\]

The source-negation covariance gives

\[
W_G(-Q)=W_G(Q)^{-1}.
\]

Therefore

\[
Z_G(Q)=W_G(Q)+W_G(Q)^{-1}\in\mathbb F_p,
\qquad
A_G(Q)=W_G(Q)-W_G(Q)^{-1}\in\omega\mathbb F_p,
\]

with `Z_G(-Q)=Z_G(Q)` and `A_G(-Q)=-A_G(Q)`.

Every inversion-compatible rational parity decoder has the form

\[
\sigma_G(Q)=A_G(Q)R_G(Z_G(Q)).
\]

On the five frozen curves, the `r=(n-1)/2` pair values of `Z_G` are distinct. The least polynomial correction has degree exactly `r-1`, all `r` coefficients are nonzero, its Dickson/Laurent expansion is also fully dense, and coefficient Berlekamp-Massey complexity reaches the generic half-length scale.

| n | r | degree R | nonzero coefficients | first rational relation degree |
|---:|---:|---:|---:|---:|
| 31 | 15 | 14 | 15 | 7 |
| 79 | 39 | 38 | 39 | 19 |
| 67 | 33 | 32 | 33 | 16 |
| 127 | 63 | 62 | 63 | 31 |
| 139 | 69 | 68 | 69 | 34 |

Canonical square-root branch bits, using both lexicographic-half and LSB conventions at the seven C34 locations, have parity-mixed collisions on every frozen curve. Hence no Boolean function of those seven bits can decode parity. The combined fourteen `G/-G` bits also have mixed collisions.

Let

\[
K_Z(Z)=\prod_{i=1}^{r}(Z-z_i).
\]

Since `A_G(Q)^2=Z_G(Q)^2-4`, the exact correction satisfies

\[
\boxed{(Z^2-4)R_G(Z)^2\equiv1\pmod{K_Z(Z)}.}
\]

This was checked exactly on all five frozen curves and all 438 nonzero base-generator rows. Because `K_Z` splits into `r` base-field components, the public square equation has exactly `2^r` componentwise roots. The generator orientation selects one sign in every component.

Thus the even/odd spectral-factor route transports the original oriented-root problem rather than eliminating it:

\[
Y_G^2=F\pmod{K_H}
\longrightarrow
R_G^2=(Z^2-4)^{-1}\pmod{K_Z}.
\]

The odd orbit factor is reciprocal to the even orbit factor, but the public full reciprocal polynomial does not select the oriented factor. A short resultant for the chosen factor would already be an oriented-root evaluator.

Closed in C39:

- direct normalized character/sign decoders of `A_G`;
- products of the seven normalized Legendre atoms;
- every Boolean function of the seven canonical root bits, by mixed collisions;
- low-degree Boolean decoders of the fourteen `G/-G` bits;
- low-degree inversion-odd polynomial/rational corrections;
- sparse monomial and Dickson/Laurent corrections;
- low-order coefficient recurrences;
- public reciprocal-orbit factorization without an oriented coherence law.

The next valid frontier is a public low-cost coherence law coupling the component signs: a GLV-equivariant nonlinear relation, an anchor-normalized recursive norm/resultant, or a theta/elliptic-net constraint placing the selected root in a low-dimensional subvariety.