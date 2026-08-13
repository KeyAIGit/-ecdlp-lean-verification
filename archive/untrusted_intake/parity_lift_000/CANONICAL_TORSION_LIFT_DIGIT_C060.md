# CANONICAL-TORSION-LIFT-DIGIT-C060

Date: 2026-08-13

Status: **a new exact public polylogarithmic observable was constructed from the unique prime-to-p torsion lift modulo p^2. Its first natural quotient, translated, and GLV-cocycle readouts give no exact carry identity on the frozen medium corpus. This object is not a base-field rational function and survives the earlier coordinate-degree barriers.**

No external point, private key, wallet, or production-sized discrete-log target is accepted.

## 1. Unique torsion lift

Let

```text
E/F_p : y^2=x^3+7,
H=<G>, |H|=n,
p does not divide n.
```

Use the ordinary CM lift with the same Weierstrass equation over `Z/p^2 Z`. For every public point

```text
Q=(x,y) in H,
```

there is a unique lift

```text
Q_tor=(x_tor,y_tor) in E(Z/p^2 Z)
```

that reduces to `Q` and satisfies

```text
[n]Q_tor=O mod p^2.                              (L1)
```

An exact evaluator uses one arbitrary curve lift `Q_0`, computes `[n]Q_0` by a Jacobian addition chain, and applies one Newton correction in the formal kernel. Because `n` is a p-adic unit, the correction is unique. The total arithmetic cost is `O(log n)` modulo `p^2`.

## 2. Intrinsic first digits

For `a in F_p^*`, let

```text
omega(a)=a^p mod p^2
```

be its Teichmuller lift. Define

```text
u_x(Q)=((x_tor/omega(x))-1)/p mod p,
nu_y(Q)=((y_tor/omega(y))-1)/p mod p.             (L2)
```

These definitions are independent of ordinary integer representatives.

The CM automorphism lifts by the Teichmuller cube root. Hence

```text
u_x(phi Q)=u_x(Q),
nu_y(phi Q)=u_y(Q).                               (L3)
```

Negation changes both `y_tor` and `omega(y)` by the same sign, so

```text
u_x(-Q)=u_x(Q),
nu_y(-Q)=u_y(Q).                                  (L4)
```

Thus `(u_x,u_y)` is a genuine public function on the six-orbit quotient. It is outside the earlier class of rational functions over `F_p`, because it depends on the arithmetic lift modulo `p^2`.

## 3. Exact quotient screen

Targets use

```text
h_G(Q)=g_G(Q)*chi_p(y(Q)).
```

The exact screen includes

```text
u_x,
u_y,
u_x+nu_y,
u_x-nu_y,
u_x*nu_y,
nu_x^2+nu_y,
u_y^2+nu_x,1,
```

and every affine pencil between two declared features, every coefficient in `F_p`, and both global quadratic signs.

Frozen irreducible-CM toy groups:

```text
n=367,397,967,1093,1249,3469,4021.
```

Results:

```text
affine target-formula instances: 1,172,520
exact h_G decoders:              0
```

On every case the pair `(u_x,u_y)` separates all retained six-orbit points, but using that fact as a lookup requires linear quotient state and is not a succinct decoder.

## 4. Marked-generator finite differences

Define public translated digits

```text
Delta_x^G(Q)=u_x(Q+G)-u_x(Q),
Delta_y^G(Q)=u_y(Q+G)-u_y(Q),
```

and their second finite differences. These are generator-sensitive and remain computable with a constant number of torsion-lift evaluations.

The exact screen uses the raw digits, first and second differences, their basic products, every affine coefficient, and both global signs directly against `g_G`.

```text
affine target-formula instances: 1,791,350
exact carry decoders:            0
```

## 5. Reduction-section cocycle

Choose the CM-equivariant Teichmuller section

```text
s:E(F_p)->E(Z/p^2 Z)
```

by lifting `x` Teichmuller-wise and solving uniquely for the `y` lift with the prescribed reduction.

Its group-law defect is

```text
c(P,R)=t(s(P)+s(R)-s(P+R))/p mod p,               (L5)
```

where `t=-x/y` is the formal parameter at `O`.

For the three GLV directions `G,phi G,phi^2 G`, the successive defects around the translated triangle satisfy the exact additive relation

```text
c_0(Q)+c_1(Q)+c_2(Q)=0 mod p.                    (L6)
```

The direct CM orbit defect

```text
s(Q)+s(phi Q)+s(phi^2 Q)
```

is identically `O`, not merely zero modulo `p`: the three points are the intersections of one horizontal line with the lifted cubic. Hence the most obvious p-adic GLV carry cocycle collapses exactly.

The exact screen of `c_i`, their products, Vandermonde, and symmetric expressions gives

```text
target-formula instances: 2,931,300
exact g_G or h_G decoders: 0
```

## 6. Aggregate result

```text
exact target-formula instances: 5,895,170
exact decoders:                 0
```

The finite screens are bounded evidence. The positive result is the construction and polylogarithmic evaluation of the public arithmetic-lift coordinates `(u_x,u_y)`.

## 7. Why this object matters

C060 is not another large theta table or full dual character. It is:

```text
public,
exact,
constant-output-size,
computable modulo p^2 in O(log n) arithmetic,
CM/GLV compatible,
and genuinely arithmetic rather than rational over F_p.
```

Therefore it defines a new admissible mechanism class even though its first readouts fail.

## 8. Successor

```text
ARITHMETIC-DIVISION-JET-C061
```

The torsion correction is the first arithmetic derivative of the order-dependent division condition. The next pass must express `(u_x,u_y)` through the normalized value and derivative of `[n]`, or equivalently the p-derivative of the `n`-division section, then determine whether its quadratic residue separates the hidden EDS factor after the public first-jet normalization is removed.

## Claim boundary

No carry, hard-R3, parity, or scalar-recovery algorithm is obtained. The uniqueness and evaluation statements concern the fixed prime-to-p torsion lift modulo `p^2`; the finite screens are not a secp256k1 impossibility theorem.
