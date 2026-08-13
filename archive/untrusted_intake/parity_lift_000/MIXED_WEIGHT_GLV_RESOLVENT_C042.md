# MIXED-WEIGHT-GLV-RESOLVENT-C042

Date: 2026-08-12

Status: **the first translated-characteristic mixed-weight determinant factors by the C3 Fourier decomposition and its anti-Kummer part collapses to a low-degree direct coordinate square class. A complete two-pullback additive-pencil search on two medium toy groups finds no exact carry decoder.**

No external point, private key, wallet, or production-sized discrete-log target is accepted. No public carry, hard-R3, parity, or ECDLP decoder is constructed.

## 1. Target

Let

```text
E/F_p : y^2=x^3+B,
phi(x,y)=(beta*x,y),
beta^2+beta+1=0,
H=<G>, |H|=n,
Q=[k]G.
```

The target remains the exact GLV carry bit `g_G(Q)`, or the equivalent quotient label

```text
h_G(x(Q)^3)=g_G(Q)*chi_p(y(Q)).
```

Packages 040 and 041 reject the declared one-addition and nested two-addition monomial classes. The next proposed escape is a determinant or resolvent that genuinely mixes different C3/CM weights.

## 2. First translated-characteristic determinant

Fix a public point

```text
R=(X,Y),
A=X^3,
Q=(x,y),
Z=x^3,
W=Y*y.
```

Let `R_j=phi^j R` and define

```text
M^+_ij(Q,R)=x(phi^i Q + phi^j R).
```

After factoring `beta^i` from row `i`, the matrix is C3-circulant. If

```text
q_j=x(Q+phi^j R),
```

its determinant is the product of the three C3 Fourier components

```text
qhat_0=q_0+q_1+q_2,
qhat_1=q_0+beta*q_1+beta^2*q_2,
qhat_2=q_0+beta^2*q_1+beta*q_2.
```

The exact component formulas are

```text
qhat_0 =
 -3*x*P_(A,Z)(W)/(Z-A)^2,

qhat_1 =
 (3*X*x*(y-Y)/(Z-A))^2,

qhat_2 =
 -3*X*P_(Z,A)(W)/(Z-A)^2,
```

where

```text
P_(A,Z)(W)
 = -A^2-4*A*B+4*A*W-5*A*Z-2*B*Z+2*W*Z.
```

One Fourier component is already an exact square. Therefore

```text
Delta_+(Q,R)=det M^+
 = 81*A*Z*(A+Z+2*B-2*W)
   *P_(A,Z)(W)*P_(Z,A)(W)/(Z-A)^6.             (R1)
```

The minus characteristic `Delta_-` is obtained by replacing `R` with `-R`, equivalently `W` with `-W`.

## 3. Exact anti/symmetric collapse

Using

```text
W^2=(A+B)(Z+B),
```

the anti-characteristic part of the determinant is

```text
Delta_+-Delta_-
 = -324*A*Z*W*R4(A,Z;B)/(Z-A)^6,              (R2)
```

where

```text
R4 =
 A^4+20*A^3*B+31*A^3*Z
 +32*A^2*B^2+124*A^2*B*Z+80*A^2*Z^2
 +80*A*B^2*Z+124*A*B*Z^2+31*A*Z^3
 +32*B^2*Z^2+20*B*Z^3+Z^4.
```

The symmetric part is

```text
Delta_++Delta_-
 = 162*A*Z*S5(A,Z;B)/(Z-A)^6,                 (R3)
```

with

```text
S5 =
 14*A^4*B+17*A^4*Z
 +72*A^3*B^2+202*A^3*B*Z+127*A^3*Z^2
 +64*A^2*B^3+360*A^2*B^2*Z+432*A^2*B*Z^2+127*A^2*Z^3
 +160*A*B^3*Z+360*A*B^2*Z^2+202*A*B*Z^3+17*A*Z^4
 +64*B^3*Z^2+72*B^2*Z^3+14*B*Z^4.
```

The denominator in `(R2)` is a square. Up to a public nonzero constant, its quadratic square class is therefore represented by

```text
y(Q)*Z*R4(A,Z;B).
```

This is a direct rational coordinate function of pole degree at most 33. The apparently new translated determinant has not escaped the direct-coordinate class; it has only provided a structured low-degree member of it.

The other anti-Kummer DFT combinations reduce similarly to the public polynomial representatives

```text
x*y*(2*A+Z),
y*(A+2*Z),
x*y*(A^3+8*A^2*B+17*A^2*Z+20*A*B*Z
     +17*A*Z^2+8*B*Z^2+Z^3).
```

## 4. Scalar pullback does not amplify the spectrum

For a scalar-domain function `f` and a nonzero public multiplier `m`, put

```text
f_m(k)=f(m*k mod n).
```

Its additive Fourier transform satisfies

```text
fhat_m(j)=fhat(j*m^(-1)).
```

Thus a scalar pullback only permutes Fourier magnitudes. A fixed low-degree translated resolvent with square-root-scale Fourier coefficients cannot acquire the constant-heavy spectrum of carry merely by composing it with `[m]`.

This closes the misleading high-degree-looking form

```text
Q -> F([m]Q)
```

for one fixed base resolvent: scalar multiplication may make its formal coordinate degree enormous, but it does not change its scalar-domain spectral content.

## 5. Stronger exact two-pullback pencil

The first genuinely stronger construction is an addition of two independently pulled-back weight components:

```text
D_(m,l,c)(Q)=F([m]Q)+c*G([l]Q),
```

followed by `chi_p`, with

```text
m,l in (Z/nZ)^*,
c in F_p,
```

and either global quadratic square class.

For each `(m,l)`, all `c` are tested simultaneously by exact bitset intersection. Zeros are rejected. There is no sampling, optimization score, statistical threshold, or fitted model.

The declared anti-Kummer base components are

```text
det_anti,
x0_anti,
x2_anti,
x0x2_anti,
```

represented by the polynomial square classes in section 3.

### `(p,n)=(1087,271)`

Five base-component pairs are exhaustively tested.

```text
multiplier pairs per component pair: 72,900
coefficients per pair:               1,087
nominal formula instances:           396,211,500
exact carry decoders:                0
DFT identity checks:                 264
```

### `(p,n)=(1663,433)`

Four base-component pairs are exhaustively tested.

```text
multiplier pairs per component pair: 186,624
coefficients per pair:               1,663
nominal formula instances:           1,241,422,848
exact carry decoders:                0
DFT identity checks:                 426
```

Aggregate:

```text
nominal exact formula instances: 1,637,634,348
exact carry decoders:            0
```

## 6. Answer

```text
Does the translated C3 determinant genuinely mix weights?       yes
Does its C3 Fourier decomposition contain a square component?   yes
Does its anti-Kummer determinant remain a new high object?      no
Exact square-class normal form                                  low-degree y*R(x^3)
Can one scalar pullback create carry's heavy spectrum?           no; it permutes frequencies
Can two independently pulled-back components plus any c decode? no on the complete declared medium gates
Public carry / hard-R3 decoder                                  absent
Sub-square-root ECDLP algorithm                                 absent
```

The finite searches do not prove a secp256k1 impossibility theorem. They reject the first natural translated-coordinate mixed-weight mechanism and its complete two-pullback additive pencils on the declared toy groups.

## 7. Relation to the parallel theta line

Packages 050 and 051 in the parent branch already show:

```text
one common theta basis -> multiplicative net ratio;
independent scalar row rescaling -> product of the supplied row factors.
```

The present package closes the most natural bounded-pole translated-coordinate realization of a twisted characteristic: after C3 diagonalization it returns to low-degree coordinate square classes.

A genuinely new survivor must therefore use data not represented by translated `x/y` sections of one bounded pole space, for example a true Heisenberg/metaplectic intertwiner between distinct theta characteristics.

## 8. Successor

The coordinate line should not proceed by adding a third arbitrary pulled-back term without an exact structural reason. The theorem-first successor aligns with the parent line:

```text
TWISTED-THETA-CHARACTERISTIC / HEISENBERG-INTERTWINER.
```

Its obligation is to produce an anti-invariant generator-sensitive quantity whose normalization is not:

```text
a common-basis net ratio,
a product of supplied row factors,
a faithful order-n character in disguise,
or a bounded-pole translated-coordinate square class.
```

Any positive formula must include a public evaluator and complete preprocessing, representation, memory, extension-field, precision, online-query, and recovery cost.

## 9. Reproducibility and formalization boundary

- `mixed_weight_glv_resolvent.py` verifies the C3 DFT identities and performs the complete two-pullback searches.
- `mixed_weight_glv_resolvent_results.json` freezes the exact counts.
- `Ecdlp/Proved/MixedWeightGlvResolvent.lean` formalizes the C3 Fourier product identity and the anti/symmetric polynomial collapses.

The Lean file does not formalize elliptic curves, Fourier analysis, character-sum bounds, carry correctness, or ECDLP.
