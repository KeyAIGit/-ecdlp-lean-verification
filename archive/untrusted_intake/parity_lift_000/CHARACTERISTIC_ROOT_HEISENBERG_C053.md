# CHARACTERISTIC-ROOT-HEISENBERG-C053

Date: 2026-08-13

Status: a concrete public degree-three theta-characteristic lift and a marked-generator Heisenberg minor were constructed. Their natural affine and multiplicative readouts produced no exact binary-orientation identity on the frozen toy corpus.

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## Object

Let

```text
E/F_p : y^2=x^3+B,
alpha_j=beta^j alpha,
alpha^3=-B,
beta^2+beta+1=0.
```

For a public toy point `Q=(x,y)`, define canonical roots in `F_(p^3)`:

```text
r_j(Q)=(x(Q)-alpha_j)^((p^3+1)/4).
```

The three C3 Fourier components are

```text
Theta_a(Q)=sum_(j=0)^2 beta^(a*j) r_j(Q),  a=0,1,2.
```

Frobenius acts on each component through a cube root of unity, so

```text
A_a(Q)=Theta_a(Q)^3 in F_p.
```

With

```text
D(Q)=(r_0-r_1)(r_1-r_2)(r_2-r_0),
```

the exact relation is

```text
A_1(Q)-A_2(Q)=-3*(beta-beta^2)*D(Q).
```

This proves that the first anti-Fourier difference is exactly the characteristic-root Vandermonde.

## Marked-generator intertwiner

To insert the ordered generator, define

```text
M_(a,b),G(Q)
 =Theta_a(Q)Theta_b(Q+G)-Theta_b(Q)Theta_a(Q+G),

N_(a,b),G(Q)
 =(M_(a,b),G(Q)/(x(Q+G)-x(Q)))^3 in F_p.
```

This is a constant-degree public toy construction over `F_(p^3)`, not a symmetric norm. It depends on the ordered generator through the translation `Q -> Q+G`.

Exactly two subgroup points are exceptional:

```text
Q=-G,
2Q=-G.
```

Both are publicly recognizable. On every other point of the retained corpus, `N_01,N_02,N_12` are nonzero.

## Exact frozen results

Eight irreducible-characteristic toy cases were retained:

```text
(p,n)=(547,547),(907,967),(1051,1093),(1303,1249),
      (2671,367),(2851,397),(3571,3469),(3931,4021).
```

Unshifted base-field resolvents:

```text
features: A0,A1,A2,B,D,1
affine formula instances: 706,944
exact matches: 0
```

Marked-generator Heisenberg minors:

```text
features: N01,N02,N12,1
targets: g, h=g*chi(y), and the adjacent edge label
affine formula instances: 1,009,920
exact matches: 0
multiplicative-subset exact matches: 0
```

On the two largest subgroups, the best `g` and `h` accuracies remain near random scale.

## Conclusion

The nonrational theta characteristics can be kept separate and coupled by a public marked translation without materializing a large theta representation. This creates a genuine new object, but its first natural readouts do not choose the required binary orientation.

The theorem-first successor is:

```text
MASLOV-WEIL-COCYCLE-C054.
```

The next pass derives the projective composition phase obtained by composing Heisenberg intertwiners around the GLV triangle and classifies it under Frobenius, negation, GLV, and generator reversal before any further screen.

## Claim boundary

This package uses only frozen toy groups. It does not provide a secp256k1 scalar-recovery algorithm and does not prove that every nonlinear readout of the Heisenberg object fails.
