# CANONICAL-PADIC-GLV-HOLONOMY-C058

Date: 2026-08-13

Status: **canonical additive p-adic holonomy on the prime-to-p GLV subgroup is zero. The standard p-adic logarithm, holomorphic Coleman integrals, and bilinear p-adic heights cannot supply the missing generator-oriented bit. Nonzero logarithmic phases require extra branch/level data and are deferred to C059.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Canonical lift setting

For secp256k1,

```text
E/F_p : y^2=x^3+7,
p mod 3 = 1,
p does not divide n,
H=<G>, |H|=n prime.
```

The `j=0` reduction is ordinary. Prime-to-`p` torsion on the Frobenius-fixed subgroup line has a canonical torsion lift to the ordinary p-adic lift.

Let

```text
Q=[k]G in H.
```

The p-adic elliptic logarithm is an additive homomorphism into a characteristic-zero additive group. Since

```text
[n]Q=O
```

and `n` is invertible p-adically,

```text
boxed:
log_E(Q)=0.                                      (P1)
```

The same holds for `phi(Q)` and `phi^2(Q)`.

## 2. GLV triangle holonomy

Let `omega` be an invariant holomorphic differential and define the Coleman/abelian integral

```text
I(P,R)=integral_P^R omega.
```

Its value is the difference of elliptic logarithms. Therefore every edge integral between lifted subgroup torsion points vanishes:

```text
I(P,R)=log_E(R)-log_E(P)=0.                      (P2)
```

In particular, for the GLV triangle

```text
Q,
phi(Q),
phi^2(Q),
Q+phi(Q)+phi^2(Q)=O,
```

the additive holonomy is exactly zero:

```text
boxed:
I(Q,phi Q)+I(phi Q,phi^2 Q)+I(phi^2 Q,Q)=0.      (P3)
```

This is stronger than failure to correlate: the canonical additive observable is identically trivial on the whole prime-to-p torsion subgroup.

## 3. Heights do not restore the bit

A bilinear p-adic height pairing vanishes when either input is torsion. Its associated quadratic height therefore vanishes on torsion as well:

```text
h_p(Q)=0.                                        (P4)
```

Local p-adic Neron functions and sigma descriptions require normalization and auxiliary choices. Their canonical global pairing still kills torsion. A nonzero local component can only be meaningful together with the compensating choices/components; it is not automatically a canonical binary orientation.

Moreover, every ordinary quadratic height is even under

```text
Q -> -Q.
```

It cannot directly equal the anti-Kummer carry `g_G(Q)`. Targeting the even quotient label `h_G=g_G*chi_p(y)` would still require a nontrivial torsion value, which `(P4)` does not provide in the canonical pairing.

## 4. Why the formal sigma series is not a global decoder

The Mazur-Tate p-adic sigma function is naturally defined on the kernel of reduction/formal neighbourhood of `O`.

A nonzero point of `H` has order prime to `p` and is not in that formal kernel. No nonzero multiple `[m]Q`, with `m` invertible modulo `n`, enters the kernel; `[n]Q=O` is the first zero multiple and erases the target.

Thus direct evaluation of the formal sigma series on arbitrary `Q in H` is unavailable. Any global continuation must specify a splitting, logarithm branch, tangential basepoint, or equivalent auxiliary data and must prove that this data does not encode the missing scalar orientation.

## 5. Closed class

Closed by this package:

```text
p-adic elliptic logarithm on the lifted subgroup,
holomorphic Coleman integrals between subgroup points,
closed additive Coleman holonomy around the GLV triangle,
bilinear or quadratic canonical p-adic heights on torsion,
direct formal-sigma evaluation on nonzero prime-to-p subgroup points.
```

## 6. What remains open

Not closed:

1. Coleman integrals of third-kind/logarithmic differentials whose residues create a multiplicative tame symbol;
2. a tangential or branch-normalized continuation with a proved public normalization;
3. nonlinear p-adic functions not factoring through the elliptic logarithm or a torsion-vanishing height;
4. a p-adic theta/Heisenberg construction carrying an explicitly costed level structure.

## 7. Successor

```text
PADIC-TAME-SYMBOL-ORIENTATION-C059
```

Central question:

> Can a third-kind Coleman integral or p-adic sigma quotient around the GLV orbit retain a nontrivial multiplicative torsion phase whose binary residue is public, without reducing to a full order-n Weil-pairing character or importing a logarithm/branch choice?

## Claim boundary

This is a scoped structural no-go for canonical additive p-adic constructions. It is not a universal lower bound for all p-adic analytic circuits and does not construct a carry or scalar-recovery algorithm.
