# MASLOV-WEIL-COCYCLE-C054

Date: 2026-08-13

Status: toy-only structural and exact finite-field study. No external point or production target is accepted.

For the C053 theta vectors and the oriented GLV triangle

```text
P0=Q,
P1=Q+G,
P2=Q+G+phi(G),
```

define

```text
Mu_ab(Q)=det(v_ab(P0),v_ab(P1))
         *det(v_ab(P1),v_ab(P2))
         *det(v_ab(P2),v_ab(P0)).
```

The square class of `Mu_ab` is invariant under independent rescaling of the three projective theta vectors. It changes sign under an odd permutation of the vertices and descends exactly to `F_p` because the three Frobenius weights add to zero.

For four vectors, with `mu_ijk=[i,j][j,k][k,i]`,

```text
mu_012*mu_023/(mu_013*mu_123)=([0,2]/[1,3])^2.
```

Thus the associated square classes obey the exact Maslov two-cocycle identity.

If `N_ab(P,R)=(det(v_ab(P),v_ab(R))/(x(R)-x(P)))^3`, then

```text
chi(Mu_ab)=chi(Dx)*chi(N_ab(P0,P1)N_ab(P1,P2)N_ab(P2,P0)),
```

where `Dx` is the product of the three oriented x-coordinate differences. Hence this cocycle composes the C053 edge data but does not supply an independent hidden input.

Eight frozen toy cases were screened using the three Maslov values, their normalized loop products, the full 3x3 theta volume, the coordinate orientation and all affine pencils/multiplicative subsets.

```text
affine formula instances: 3,029,760
exact target identities:  0
```

The genuine canonically normalized Heisenberg intertwiners between oriented Lagrangian models satisfy exact multiplicativity, so their closed-loop monodromy is trivial. A useful state-dependent phase must therefore come from Q-dependent projective data rather than the standard Weil multiplier.

Successor:

```text
HEISENBERG-PROJECTIVE-CROSS-RATIO-C055.
```

Claim boundary: finite toy evidence is not a universal impossibility theorem, and no scalar-recovery construction is claimed.
