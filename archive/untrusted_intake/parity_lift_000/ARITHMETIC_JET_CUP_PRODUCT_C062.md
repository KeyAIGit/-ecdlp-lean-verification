# ARITHMETIC-JET-CUP-PRODUCT-C062

Date: 2026-08-13

Status: **the reduction-section defect underlying C060 is a uniquely split coboundary on the prime-to-p subgroup. Its cup/Maslov-style cohomology classes vanish because the subgroup order is invertible in the formal-kernel coefficient module. Exact CM-weighted defect resolvents produce no carry identity on the frozen corpus.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Reduction extension

Modulo `p^2`, reduction gives an exact sequence on the retained subgroup preimage

```text
0 -> K -> E(Z/p^2 Z)|_H -> H -> 0,
```

where the formal kernel is

```text
K ~= (F_p,+).
```

Since

```text
|H|=n,
gcd(n,p)=1,
```

multiplication by `n` is an automorphism of `K`.

Therefore the extension restricted to `H` has a unique group-homomorphic torsion splitting

```text
tau:H->E(Z/p^2 Z),                               (C1)
```

namely the unique torsion lift from C060. Uniqueness follows because every difference of two splittings is a homomorphism `H->K`, and no nonzero such homomorphism exists between groups of coprime orders.

## 2. Section defect is a coboundary

Let `s` be the public CM-equivariant Teichmuller section and write the unique splitting as

```text
tau(P)=s(P)+b(P),
b(P) in K.
```

The group-law defect

```text
c(P,R)=s(P)+s(R)-s(P+R) in K                    (C2)
```

satisfies

```text
boxed:
c(P,R)=b(P+R)-b(P)-b(R).                        (C3)
```

Thus `c` is an exact coboundary, not a nontrivial extension class.

More generally, because `n` is invertible on `K`, positive-degree group cohomology of the finite cyclic group with these coefficients vanishes. Ordinary cup, Massey, or loop classes constructed only from `(C2)` cannot create a new topological orientation class.

## 3. CM-weighted defect vector

For the three marked directions define

```text
d_j(Q)=c(Q,phi^j G),  j=0,1,2.                  (C4)
```

CM equivariance gives

```text
d_0(phi Q)=beta d_2(Q),
d_1(phi Q)=beta d_0(Q),
d_2(phi Q)=beta d_1(Q).                          (C5)
```

The C3 Fourier components

```text
f_a(Q)=sum_j beta^(a*j)d_j(Q)                    (C6)
```

therefore have exact known CM weights. Their cubes, products, discriminants, and Vandermonde descend to base-field scalar functions.

But by `(C3)` every such value is a fixed nonlinear expression in translated copies of the already public splitting cochain `b`; it is not a new cohomology class.

## 4. Exact frozen gate

The declared feature family contains

```text
d0,d1,d2,
f0,f1,f2,
d0*d1*d2,
(d0-d1)(d1-d2)(d2-d0),
f1*f2,
f1^3,f2^3,f1^3-f2^3,
1.
```

Every affine pencil, every coefficient in `F_p`, both global signs, and both targets `g_G,h_G` were checked on the seven medium C060 groups.

```text
target-formula instances: 5,927,740
exact identities:         0
```

On the two largest groups, the best declared accuracies remain below about `0.563` after scanning all coefficients. These values are bounded evidence only.

## 5. Closed class

Closed by this package:

```text
claims that the mod-p^2 reduction extension itself carries a nontrivial class on H,
ordinary cup/Massey invariants of the section-defect cocycle,
CM Fourier resolvents of one defect vector as independent cohomology data,
GLV triangle holonomy formed only from the additive section defect.
```

## 6. What remains open

The splitting cochain `b(Q)`, equivalently the canonical torsion-lift digits, remains a nontrivial public nonlinear coordinate. Vanishing cohomology does not prove that every nonlinear function of its values is useless.

Higher p-adic precision may introduce new arithmetic digits not determined by one base-field square class. This is the next controlled test.

## 7. Successor

```text
SECOND-WITT-TORSION-JET-C063
```

Compute the unique torsion lift modulo `p^3`, extract the second Teichmuller/Witt digits, derive their exact CM and negation laws, and test whether a genuinely new normalized combination survives after removing all functions of the first digit.

## Claim boundary

The cohomology statement is scoped to the finite prime-to-p subgroup with formal-kernel coefficients modulo `p^2`. It is not a lower bound for arbitrary nonlinear p-adic circuits and does not construct a carry or scalar-recovery algorithm.
