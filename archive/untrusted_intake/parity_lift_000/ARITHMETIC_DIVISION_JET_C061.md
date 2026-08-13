# ARITHMETIC-DIVISION-JET-C061

Date: 2026-08-13

Status: **the canonical torsion-lift digit from C060 is exactly the first p-arithmetic jet of the order-n division condition. It is public, polylogarithmically evaluable, has the correct nontrivial CM weight, and is not covered by base-field rational degree barriers. Its first quadratic and full additive-phase readouts show no exact decoder or heavy Fourier signal on the frozen corpus.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Arithmetic jet

Let `s(Q)` be the CM-equivariant Teichmuller section from C060 and put

```text
R_Q=[n]s(Q) in E_1(Z/p^2 Z).
```

With the formal parameter `t=-x/y`, define

```text
epsilon_n(Q)=t(R_Q)/p mod p.                     (J1)
```

This is the first arithmetic derivative of the statement `[n]Q=O`: the ordinary reduction vanishes, while the normalized first p-adic failure is `epsilon_n(Q)`.

Computing `[n]s(Q)` uses one public addition chain and therefore costs `O(log n)` arithmetic modulo `p^2`.

## 2. Exact relation to the torsion-lift digit

Let `u_x(Q)` be the Teichmuller-normalized x-coordinate digit of the unique torsion lift from C060. First-order translation by the formal correction gives

```text
boxed:
x(Q) u_x(Q)
 =-2 y(Q) n^(-1) epsilon_n(Q) mod p.             (J2)
```

Thus `epsilon_n` and `u_x` are publicly interconvertible away from the publicly recognizable coordinate zeros. C061 is a structural normal form of C060, not a second independent observable.

## 3. CM and negation laws

The lifted CM automorphism satisfies

```text
t(phi P)=beta t(P).
```

Since `[n]` commutes with `phi` and the Teichmuller section is CM-equivariant,

```text
epsilon_n(phi Q)=beta epsilon_n(Q).              (J3)
```

Negation gives

```text
epsilon_n(-Q)=-epsilon_n(Q).                     (J4)
```

For the retained `p=1 mod 3` fields, `beta` is a square. Hence the quadratic character of `epsilon_n` is GLV-invariant and, when `chi_p(-1)=-1`, anti-Kummer. It has exactly the transformation type required of a direct carry candidate.

## 4. Division-polynomial interpretation

In the standard multiplication-map convention

```text
x([n]P)=phi_n(P)/psi_n(P)^2,
y([n]P)=omega_n(P)/psi_n(P)^3,
```

one has

```text
t([n]P)=-phi_n(P) psi_n(P)/omega_n(P).           (J5)
```

Since `psi_n(s(Q))` is divisible by `p`, `(J1)` is, up to the public nonzero factor in `(J5)`, the arithmetic quotient

```text
psi_n(s(Q))/p mod p.                             (J6)
```

This is an arithmetic jet of the full order-dependent division section. It is distinct from the ordinary geometric first jet `D psi_n(Q)` studied in package 003.

## 5. Exact binary gates

On the seven frozen medium groups from C060:

```text
chi_p(epsilon_n(Q))
```

and every declared affine combination with the torsion-lift digits, translated finite differences, and reduction-section cocycles produced no exact `g_G` or `h_G` identity.

The direct character accuracy on the two largest groups is approximately

```text
n=3469: 0.5104,
n=4021: 0.5134.
```

These finite values are evidence only, not a theorem.

## 6. Full additive-phase spectrum

A stronger use of the jet is the complete public phase

```text
f_a(k)=exp(2*pi*i*a*epsilon_n([k]G)/p).
```

For an unknown `Q=[k]G`, public multiplier queries satisfy an exact decimation law

```text
f_(Q,a)(t)=f_(G,a)(t*k mod n).                   (J7)
```

Thus a constant-heavy additive Fourier spectrum would give a direct spectral scalar-recovery route without first converting the jet to carry.

The powers

```text
a=1,2,3,5,7,11,13,17
```

were checked on `n=3469` and `n=4021`. Across all checked powers:

```text
maximum Fourier magnitude = O(1/sqrt(n)),
sqrt(n)*maximum           between about 3.05 and 4.28 for epsilon_n,
Fourier L1                about 47 to 51, i.e. sqrt(n)-scale.
```

No coefficient reaches `1/log(n)`, and no constant-heavy spectral family appears in the declared screen.

## 7. Result

```text
Exact public arithmetic jet                       constructed
Evaluation cost                                   O(log n) mod p^2
Correct GLV/negation transformation law           yes
Equivalent to C060 x-digit                        yes
Exact simple carry or quotient identity           absent
Constant-heavy additive spectrum                  absent in frozen powers
Public carry, hard-R3, or scalar-recovery method  absent
```

## 8. Successor

The arithmetic jet itself is not exhausted by linear phases. The next nonredundant object is its **section-defect cohomology under marked translations**:

```text
ARITHMETIC-JET-CUP-PRODUCT-C062.
```

It must combine two independently weighted arithmetic jets or section defects so that the resulting class is generator-sensitive and not merely a coboundary, a scalar pullback, or a low-degree base-field character already screened in C060.

## Claim boundary

The spectral checks are bounded toy evidence. This package does not prove pseudorandomness, does not rule out nonlinear arithmetic-jet identities, and does not construct a carry or scalar-recovery algorithm.
