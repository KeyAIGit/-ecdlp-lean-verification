# UNIFORM-ORIENTED-ROOT-CIRCUIT-056

## C13: compact line-bundle cocycle and the endpoint-gauge boundary

Date: 2026-08-14

Status: **the long translated C10 product has an exact constant-support normal form after passing from the C12 divisor primitive to its degree-zero line-bundle class. The entire length-`L` cocycle collapses to one four-point Miller quotient. The missing orientation is not in cocycle accumulation: it is exactly the endpoint ratio of a principal gauge function whose pole degree is `floor((n+1)/4)` or one larger. No short evaluator for that gauge is known.**

Only frozen toy curves, known toy generators, public generator replacements, and deterministic extension-field probes are used.

## 1. Input from C10-C12

Let

```text
E: y^2=F(x),
H=<G>, |H|=n=2m+1,
P_k=[k]G,
T=P_m,
S=P_2=[2]G.
```

Put

```text
g(P)=x(P-G)-x(T).
```

Then the C10 target is

```text
f_G(P)=product_(r=0)^(m-1) g(P-rS).              (C13.1)
```

C12 constructed the unique degree-zero coefficient vector

```text
D=sum_k d_k(P_k)
```

satisfying

```text
div(g)=D-tau_S(D),                               (C13.2)
```

where `tau_S` translates divisor points by `+S`. Its coefficients are

```text
d_k=-1  for odd 1<=k<=m,
d_k=+1  for even m<k<n,
d_k=0   otherwise.                               (C13.3)
```

Let

```text
r=floor((n+1)/4).
```

The positive and negative degrees of `D` are both `r`, but its Abel-Jacobi class is nonzero:

```text
[D]=A=[a]G != O.                                 (C13.4)
```

More explicitly,

```text
n=4r-1: a=r(2r-1) mod n,
n=4r+1: a=r(2r+1) mod n.                         (C13.5)
```

The nonzero class is why C12 found no rational one-state telescoper with divisor `D`.

## 2. Replace the divisor by its compact line-bundle representative

The degree-zero divisor

```text
D0=(A)-(O)                                       (C13.6)
```

has the same divisor class as `D`. Therefore

```text
E_G=D-D0                                         (C13.7)
```

is principal. Choose a rational function `h_G`, unique up to a nonzero scalar, such that

```text
div(h_G)=E_G.                                    (C13.8)
```

This is a change of meromorphic gauge. It does not assume that `D` itself is principal.

The pole degree of `h_G` is exact and linear:

```text
deg_poles(h_G)=r       if d_a=+1,
deg_poles(h_G)=r+1     if d_a in {0,-1}.          (C13.9)
```

Hence

```text
r <= deg_poles(h_G) <= r+1,
r=floor((n+1)/4).                                (C13.10)
```

For secp256k1, `n=1 mod 8`, so

```text
r=(n-1)/4,
a=(n-1)/8,
d_a=0,
deg_poles(h_G)=(n-1)/4+1.                       (C13.11)
```

This is a degree statement, not an unrestricted arithmetic-circuit lower bound.

## 3. The compact one-step cocycle

Let

```text
c_(A,S)(P)=ell_(A,S)(P)/v_(A+S)(P),              (C13.12)
```

where `ell_(A,S)` is the chord or tangent line through `A` and `S`, and `v_(A+S)` is the vertical line through `A+S`. Its divisor is

```text
div(c_(A,S))
 =(A)+(S)-(A+S)-(O)
 =D0-tau_S(D0).                                  (C13.13)
```

Combining `(C13.2)`, `(C13.7)`, and `(C13.13)` gives

```text
boxed:
g(P)=gamma*c_(A,S)(P)*h_G(P)/h_G(P-S),           (C13.14)
```

for one nonzero constant `gamma` independent of `P`.

Thus the translated factor is a compact line-bundle cocycle times a gauge coboundary.

## 4. Exact collapse of every length-L segment

Define

```text
F_L(P)=product_(j=0)^(L-1) g(P-jS).              (C13.15)
```

The compact factors telescope at the divisor level:

```text
sum_(j=0)^(L-1) tau_(jS)(D0-tau_S D0)
 =D0-tau_([L]S)D0.                               (C13.16)
```

The right side is the divisor of one Miller quotient

```text
c_(A,[L]S)(P)=ell_(A,[L]S)(P)/v_(A+[L]S)(P).
```

The gauge terms telescope in the ordinary scalar sense. Therefore

```text
boxed:
F_L(P)
 =gamma_L*c_(A,[L]S)(P)*h_G(P)/h_G(P-[L]S),      (C13.17)
```

where `gamma_L` is a nonzero public-instance constant independent of `P`.

The support of the compact factor has at most four points, independently of `L` and `n`. Computing `[L]S` takes logarithmic group operations. Consequently, the length of the cocycle is not the remaining source of square-root complexity.

## 5. Target specialization

For the target length `L=m`,

```text
[m]S=[2m]G=[n-1]G=-G.
```

Equation `(C13.17)` becomes

```text
boxed:
f_G(P)
 =gamma_m*c_(A,-G)(P)*h_G(P)/h_G(P+G).           (C13.18)
```

The compact factor has divisor

```text
(A)+(-G)-(A-G)-(O).                              (C13.19)
```

Therefore it is a unit at every subgroup point except the four public indices

```text
0, a, n-1, a-1.
```

Away from those points, the entire alternating zero-versus-pole pattern is the endpoint finite difference of the gauge divisor:

```text
ord_(P_k)(f_G)=e_k-e_(k+1),                      (C13.20)
```

where `e_k` are the coefficients of `E_G`. The four compact exceptions are corrected explicitly by `(C13.19)`.

This gives a sharper localization than C10:

```text
not hard: accumulating m translated factors,
not hard: the nonprincipal divisor class A,
remaining hard object: the scalar endpoint gauge h_G(P)/h_G(P+G).
```

## 6. Semiabelian interpretation

The class `A in Pic^0(E)` defines a degree-zero line bundle, equivalently a `G_m`-extension of the elliptic curve. The quotient `c_(A,S)` is the compact translation law in that extension. Fast repeated group addition compresses its entire length-`L` action to `c_(A,[L]S)`.

However, the original C10 scalar normalization lives in the meromorphic gauge represented by `D`, not the compact gauge represented by `(A)-(O)`. Comparing the two fibre coordinates is exactly the function `h_G`. Reading the parity bit as a base-field scalar therefore reintroduces `(C13.18)`.

This explains why an abstract compact group extension is not by itself a parity evaluator.

## 7. Replay

The deterministic executable constructs `h_G` on every frozen toy curve by a generalized Miller reduction of the explicit principal divisor `E_G`. It checks values only at generic deterministic `F_(p^2)` points.

For every base generator it verifies:

```text
all L=0,...,n divisor decompositions,
one-step scalar normal form on four probes,
compact length-L collapse for seven public lengths,
full endpoint-gauge normal form for the same lengths,
exact agreement with the C10 target at L=m.
```

It repeats the scalar and divisor checks for 129 public generator replacements.

Aggregate counters:

```text
base all-L divisor checks                    1224
base one-step gauge checks                     24
base compact-cocycle checks                   168
base endpoint-gauge checks                    168
base target-segment checks                     24
generator replacements                        129
replacement all-L divisor checks            11328
replacement one-step gauge checks             258
replacement compact-cocycle checks           1806
replacement endpoint-gauge checks            1806
replacement target-segment checks             258
```

Result SHA-256:

```text
72e1812dc28dae3d3f1a2f28736b8548aaf451c9fc16759a91b812c7c59b674a
```

Two independent executions are byte-identical.

## 8. Answer

```text
Compact representative of the C12 divisor class          yes
One-step compact cocycle                                  four-point Miller quotient
Length-L compact cocycle                                  one four-point Miller quotient
Long-product accumulation remains the bottleneck          no
Exact target normal form                                  compact factor * endpoint gauge
Endpoint-gauge pole degree                                r or r+1, about n/4
Short endpoint-gauge circuit                              not found
Strictly sub-square-root evaluator                        absent
Parity oracle below square root                           absent
Sub-square-root ECDLP                                     absent
```

## 9. Strategic successor

The next central package is

```text
ENDPOINT-GAUGE-TRANSPOSED-EVALUATION-064.
```

Its target is no longer a three-way product over all translated factors. It is the single ratio

```text
boxed:
Z_G(Q)=h_G(Q)/h_G(Q+G),
div(h_G)=D-(A)+(O).                               (C13.21)
```

A valid positive result must compute the regularized local value or valuation of `Z_G(Q)` from public `(E,G,Q)` with complete cost `O(n^(1/2-epsilon))`, without constructing `h_G` densely, enumerating its linear support, supplying a fibre trivialization that already contains the branch, or hiding square-root advice.

The highest-value mechanisms are:

```text
1. transposed evaluation of the endpoint difference without evaluating h_G twice;
2. a compact generalized-Jacobian coordinate whose scalar readout is proved not to contain hidden gauge advice;
3. a direct addition-enabled circuit for the principal divisor E_G;
4. a restricted lower bound for fibre-coordinate extraction from the compact extension;
5. only after these, a true multilinear resultant for the endpoint gauge support.
```

A direct three-way contraction of the original C10 factors is now lower priority, because `(C13.17)` proves that factor accumulation already has an abstract constant-support compression. The unresolved cost is gauge extraction.
