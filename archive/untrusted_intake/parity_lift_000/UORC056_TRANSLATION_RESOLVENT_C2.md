# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## Track C2: translation resolvent branch selector

Date: 2026-08-13

Status: exact new normal form; no evaluator is claimed.

Let `H=<G>` have odd prime order `n`, let `Q=[k]G`, and define

```text
s_G([k]G)=(-1)^k,
(tau_G f)(P)=f(P+G),
d_G=delta_(-G).
```

Then the unique odd-cycle defect gives

```text
(I+tau_G)s_G=2d_G,
(I+tau_G)^(-1)=(1/2) sum_(j=0)^(n-1)(-1)^j tau_G^j,
s_G=sum_(j=0)^(n-1)(-1)^j tau_G^j d_G.
```

The seed is publicly evaluable on affine points:

```text
d_G(P)=[1-(x(P)-x_G)^(p-1)]*[1-y(P)/y_G]/2.
```

For `p=3 mod 4`, define

```text
R_0(X)=(X^3+7)^((p+1)/4),
C_G=Y_G/R_0 mod K_H.
```

At `P=[k]G`,

```text
R_0(x(P))=y(P)chi(y(P)),
C_G(x(P))=(-1)^k chi(y(P)),
C_G^2=1 mod K_H,
e_G=(1-C_G)/2,
e_G^2=e_G,
C_(-G)=-C_G.
```

Thus the ordinary square root is cheap; the missing operation is the generator-selected Kummer branch.

Let `T_G` be the translation matrix in the point-idempotent basis and `ev_Q` evaluation at `Q`. Since `det(I+T_G)=2`, the matrix determinant lemma gives

```text
det(I+T_G+t*d_G*ev_Q)=2+t*(-1)^k.
```

This is an exact, generator-sensitive, nonmultiplicative determinant target. It is not an algorithm because its natural state dimension is `n`.

The executable replay checks on the six frozen toy subgroups:

```text
C_G^2=1,
e_G^2=e_G,
C_(-G)=-C_G,
(I+tau_G)s_G=2d_G,
the full alternating resolvent,
point-basis support n,
the Kummer doubling orientation cocycle,
117 explicit rank-one determinant identities.
```

The remaining question is exact:

```text
Can ev_Q (I+tau_G)^(-1)d_G,
or the equivalent rank-one determinant,
be evaluated uniformly below n^(1/2-epsilon)
without materializing an n-dimensional state?
```

Highest-priority routes:

1. constant-size resultant, norm, or scalar Fredholm reduction;
2. nonlinear partial-resolvent merge laws with bounded query fan-out;
3. oriented square-root-Velu style elliptic products with a strict exponent improvement;
4. coordinate-algebra modular composition without constructing the degree-n algebra;
5. a coordinate formula for the Kummer doubling orientation cocycle.

Reject explicit orbit sums, full Fourier states, degree-n bases, hidden large preprocessing, gauge-even two-endpoint products, and short operator DAGs whose application expands to `n` leaves.

No public parity evaluator or sub-square-root ECDLP algorithm is obtained by this package.
