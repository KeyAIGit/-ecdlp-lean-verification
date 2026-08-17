# GENERATOR-ORIENTED-ELLIPTIC-JACOBI-037

Date: 2026-08-12

Status: **exact oriented-cube identity, exact character-balanced Jacobi cancellation, and full-cost audit; no public sub-square-root evaluator obtained**.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Exact task

Let

```text
H=<G>, |H|=n,
Q=[k]G,
```

on the `j=0` curve, and let `psi` be the GLV-adapted sextic scalar character from package 036. Define

```text
T_psi(P)=sum_(a=1..n-1) psi(a) x([a]P).
```

Then

```text
T_psi(Q)=psi(k)^(-1) T_psi(G),
(T_psi(Q)/T_psi(G))^3=chi_n(k).
```

The package asks whether the oriented cube

```text
J_G=T_psi(G)^3
```

or directly

```text
J_Q/J_G=T_psi(Q)^3/T_psi(G)^3=chi_n(k)
```

admits a compact Eisenstein-CM, elliptic-Jacobi, Hecke-character, ray-class, theta, sigma, or net expression with complete cost

```text
O(n^(1/2-epsilon))
```

for some fixed `epsilon>0`, including preprocessing, advice, representation size, memory, precision, and online work.

## 2. Character decomposition

Put

```text
c=psi^4,       cubic component,
q=psi^3=chi_n, quadratic component.
```

For the secp256k1 branch `v_3(n-1)=1`, the chosen sextic character satisfies

```text
psi(lambda)=beta^(-1),
c(lambda)=beta^(-1),
q(lambda)=1.
```

The following three projectors are therefore compatible with the `j=0` GLV action:

```text
T(P)=sum_a psi(a)x([a]P),
C(P)=sum_a c(a)x([a]P),
S(P)=sum_a q(a)x([a]P)^3.
```

For `Q=[k]G`, exact reindexing gives

```text
T(Q)=psi(k)^(-1)T(G),
C(Q)=c(k)^(-1)C(G),
S(Q)=q(k)^(-1)S(G).
```

Since `q` is quadratic, `q(k)^(-1)=q(k)`.

## 3. The oriented cube is exactly the quadratic projector orientation

Cubing the first transformation law gives

```text
T(Q)^3=q(k)T(G)^3.                              (J1)
```

The quadratic projector satisfies

```text
S(Q)=q(k)S(G).                                  (J2)
```

Dividing `(J1)` by `(J2)` yields the exact invariant

```text
K(P)=T(P)^3/S(P),
K([k]G)=K(G).                                   (J3)
```

Therefore

```text
T(P)^3=K(E,H) S(P).                             (J4)
```

This is the central result of the package.

A compact CM formula for the invariant coefficient `K` does not compute the scalar Legendre bit. The entire generator-oriented quadratic information remains in the original projector `S(P)`.

In particular, the sextic cube did not create an easier quadratic orientation. It factored the same orientation into

```text
oriented cube = generator-blind CM/Jacobi factor * quadratic projector.
```

## 4. Exact mixed Jacobi cancellation

The natural character-balanced quotient is

```text
J_mix(P)=C(P)S(P)/T(P).
```

Because `psi=c*q`, its generator multiplier is

```text
c(k)^(-1) q(k)^(-1) / psi(k)^(-1)=1.
```

Hence

```text
J_mix([k]G)=J_mix(G).                           (J5)
```

This is not an accident. If projectors `A_i` transform by characters `theta_i^(-1)`, then a monomial

```text
product_i A_i(P)^(e_i)
```

is generator-blind whenever

```text
product_i theta_i^(e_i)=1.
```

Standard elliptic Jacobi sums are deliberately character-balanced so that they become modular functions. That construction places them in the invariant layer and removes the very character required by `(J1)`.

Conversely, a monomial whose total character is `q` can carry the Legendre bit, but then it is itself a quadratic eigenprojector. The problem has been renamed rather than solved.

## 5. Relation to published universal elliptic Jacobi sums

Berghoff defines universal elliptic Jacobi sums by multiplying elliptic Gauss sums with inverse total character and correcting modular weight. The resulting object is a weight-zero modular function for `Gamma_0(ell)`.

This is structurally consistent with `(J5)`: the universal Jacobi object is useful precisely because its character phase has cancelled.

The present mixed quotient is not asserted to be identical to every universal elliptic Jacobi sum in that literature. The exact statement proved here is only the generator-change law. Any proposed identification must additionally match point functions, modular weight, normalization, and the parity convention for even characters.

## 6. What the Eisenstein cubic CM formula can and cannot do

Asai studies cubic-character elliptic Gauss sums on the Eisenstein lattice. A canonical cubic root `pi_tilde` is constructed and the corresponding cubic elliptic Gauss sum is expressed in the form

```text
G_pi(chi_pi,f)=alpha_pi*pi_tilde^2.
```

This is positive evidence that the cubic component `C(G)` may admit a strong CM normalization.

However:

1. Asai's sum uses specific CM elliptic functions selected by the congruence class of the prime; no equality with the present finite-field `x`-weighted projector is assumed.
2. The formula concerns the cubic character component.
3. Even an ideal compact formula for `C(G)` and for every character-balanced Jacobi invariant does not determine the independent quadratic orientation in `S(G)`.
4. There are nonsquare scalars in the kernel of the cubic character, so cubic data alone cannot determine `q(k)`.

Thus the canonical cubic root can potentially compress the cubic part, but equation `(J3)` proves that it does not remove the quadratic bottleneck.

## 7. Frozen exact replay

`generator_oriented_elliptic_jacobi.py` screens the four frozen toy groups with

```text
n=1 mod 12,
v_3(n-1)=1,
```

matching the secp256k1 3-primary branch.

On all four:

```text
T(G), C(G), S(G) are nonzero;
all three character scaling laws hold for every k!=0;
T([k]G)^3/T(G)^3=q(k);
T(P)^3/S(P) is constant over all generators;
C(P)S(P)/T(P) is constant over all generators;
T(P)^6, C(P)^3, and S(P)^2 are generator-blind.
```

The replay performs `9,828` exact checks for each identity family.

Frozen nonvanishing is bounded evidence only. It is not a nonvanishing theorem for secp256k1.

## 8. Full-cost audit

### 8.1 Direct finite-field sums

Each literal projector has `n-1` summands. Even after quotienting by the visible `C6` symmetry, the quadratic projector has `(n-1)/6` orbit terms.

For secp256k1:

```text
n-1 approximately 2^256,
(n-1)/6 approximately 2^253.4,
ceil(sqrt(n))=2^128.
```

Direct evaluation is far above the required square-root boundary.

### 8.2 Generic universal modular representation

At prime level `ell`, the standard modular parameter has degree

```text
(ell-1)/gcd(ell-1,12).
```

For `ell=n` and secp256k1 this equals `(n-1)/12`, the same degree already seen in the oriented quadratic factor.

Berghoff's published generic algorithm represents elliptic Gauss and Jacobi invariants through level-dependent rational expressions. In its notation the required precision is proportional to

```text
(v+e_Delta+1)*ell,
```

with `v=Theta(ell)` asymptotically, yielding an asymptotic run time of order

```text
O(ell^2 M(r))
```

for fixed character order `r`.

Setting `ell=n` and `r=6` is therefore much larger than `n^(1/2-epsilon)`. The precomputed rational representation is also level-sized or larger. This route fails the full-cost criterion before online specialization.

### 8.3 CM specialization

The special value `j=0` may compress some invariant CM quantities dramatically, so generic modular degree is not a universal circuit lower bound.

Nevertheless any acceptable CM specialization must output the oriented value, not only

```text
T(G)^6,
T(G)^3/S(G),
C(G)S(G)/T(G),
```

because all three are generator-blind. No such compact oriented specialization was obtained.

## 9. Scoped answer

```text
Exact oriented cube ratio                                  chi_n(k)
Exact cubic/quadratic/sextic decomposition                 yes
Is T^3/S generator-oriented?                               no, invariant
Is C*S/T generator-oriented?                               no, invariant
Can a standard character-balanced Jacobi sum expose q(k)? no
Can Asai's canonical cubic root settle the quadratic bit?  no by itself
Direct cost                                                 Theta(n)
Generic universal modular/Jacobi cost                       level-quadratic scale
Public o(sqrt(n)) scalar-Legendre evaluator                 absent
Public carry / parity / hard-R3 decoder                     absent
Classical sub-square-root ECDLP algorithm                   absent
```

The standard elliptic-Jacobi/Hecke invariant route is therefore closed in the following scoped sense:

> Character balancing is exactly the operation that makes the object modular and compactly invariant, but it also cancels the generator character. Cubic CM normalization may compress the cubic component, while the independent quadratic orientation remains the original hard projector.

This is not a lower bound against every nonlinear arithmetic circuit or every generator-sensitive metaplectic construction.

## 10. Next object

The successor is

```text
QUADRATIC-WEIL-ORIENTATION-038.
```

Instead of obtaining the quadratic character as the residual cube of a sextic projector, it targets it natively through a quadratic Gauss/Weil sum.

Let `T` be a faithful independent dual `n`-torsion direction with

```text
e_n(G,T)=zeta_n.
```

Define formally

```text
W_T(P)=sum_(a mod n) e_n([a^2]P,T).
```

For `Q=[k]G`, the classical quadratic Gauss identity suggests

```text
W_T(Q)/W_T(G)=chi_n(k),  k!=0.
```

This gives the quadratic orientation directly rather than through a balanced Jacobi invariant.

The next theorem-first obligations are:

1. prove the exact normalized Weil-sum identity in the elliptic pairing notation;
2. determine the precise dual-direction and metaplectic-splitting data required;
3. test whether the Eisenstein CM polarization canonically supplies that data implicitly;
4. prove whether Frobenius-symmetric aggregation again reduces only to an unoriented square;
5. count extension degree, preprocessing, advice, precision, memory, and online operations;
6. obtain either a public `O(n^(1/2-epsilon))` evaluator or a scoped no-go for the standard Weil/metaplectic realization;
7. even if a compact Legendre oracle results, separately prove a classical sub-square-root shifted-Legendre recovery before claiming an ECDLP improvement.

No broad statistical search is admitted without a new exact identity.

## 11. Formalization boundary

`Ecdlp/Proved/GeneratorOrientedEllipticJacobi.lean` formalizes:

```text
normalized sextic cube -> quadratic character;
T^3/S generator invariance;
character-balanced mixed Jacobi invariance;
opposite oriented cubes have the same square.
```

It does not formalize elliptic Gauss sums, universal elliptic Jacobi sums, CM, Hecke characters, modular forms, Asai's formula, secp256k1 nonvanishing, or arithmetic-circuit complexity.

## 12. Primary references used for the scope audit

- T. Asai, `Elliptic Gauss Sums and Hecke L-values at s=1`, arXiv:0707.3711.
- C. J. Berghoff, `Universal elliptic Gauss sums and applications`, arXiv:1707.08075.
- C. J. Berghoff, `Efficient computation of universal elliptic Gauss sums`, arXiv:1707.08610.
- K. E. Stange, `Elliptic Nets and Elliptic Curves`, arXiv:0710.1316.
