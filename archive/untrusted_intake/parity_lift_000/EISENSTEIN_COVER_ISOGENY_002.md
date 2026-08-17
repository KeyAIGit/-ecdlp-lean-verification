# EISENSTEIN-COVER-ISOGENY-002

Date: 2026-08-11

Status: isolated, non-executable structural closure. No external point, wallet,
or production discrete-log instance is targeted. This result does not claim a
general non-generic ECDLP lower bound.

## 1. Correction to the raw cube-subgroup root

Let

```text
E_b: y^2=x^3+b,
c^2=b,
u^3=y-c.
```

Choose `u` as the unique root in the cube subgroup of `F_(p^2)^*`. Its
Frobenius conjugate satisfies

```text
(u^p)^3=y+c.
```

The product is not automatically `x`. It has the form

```text
u*u^p = delta(Q)*x,
delta(Q)^3=1.
```

The public value

```text
delta(Q)=u^(p+1)/x
```

is an order-three GLV phase. This explains why the uncorrected cubic cover can
map `Q` to one of the three points

```text
(x,y), (beta*x,y), (beta^2*x,y).
```

Set

```text
w=delta(Q)*u.
```

Then `w^3=y-c` still holds, while

```text
w*w^p=x.
```

Because every element of order three in `F_p^*` is a square for `p=1 mod 6`,
multiplication by `delta^j` does not change any quadratic-character candidate
tested in `EISENSTEIN-ROOT-PHASE-001`.

## 2. Descent to a plane cubic

Put

```text
s=w+w^p,
d=(w-w^p)/c.
```

Then

```text
w=(s+c*d)/2,
w^p=(s-c*d)/2.
```

Using `(w^p)^3-w^3=2c` gives the exact descended equation

```text
b*d^3+3*s^2*d+8=0.                     (C)
```

The original point is recovered by

```text
x=(s^2-b*d^2)/4,
y=(s^3+3*b*s*d^2)/8.
```

Thus the canonical extension-field branch already descends to a genus-one
curve over the base field.

## 3. Weierstrass form

On the affine locus `d != 0`, define

```text
X=-6/d,
Y=9*s/d.
```

Equation (C) becomes

```text
E'_b: Y^2=X^3-27*b.
```

The map from the lifted curve to the original curve is

```text
pi(X,Y) = (
  (X^3-108*b)/(9*X^2),
  -Y*(X^3+216*b)/(27*X^3)
).
```

Direct substitution proves

```text
pi(X,Y) in E_b.
```

This is the normalized degree-three isogeny associated with the cubic cover.

## 4. Public inverse through the dual isogeny

Define the standard dual-direction map

```text
pi_hat(x,y) = (
  (x^3+4*b)/x^2,
  y*(x^3-8*b)/x^3
)
```

from `E_b` to `E'_b`. With the displayed normalization,

```text
pi o pi_hat = -[3].
```

Let `Q` lie in a subgroup of prime order `r` with `r != 3`. Then three is
invertible modulo `r`, and the unique subgroup preimage is

```text
R = [-3^(-1) mod r] pi_hat(Q).
```

The corrected cube-root/Frobenius construction produces exactly this `R`.

Therefore the apparently new lift can be evaluated without extracting any
extension-field root at all. It is a fixed rational isogeny followed by a
known scalar multiplication.

## 5. Consequence for the parity program

The canonical cubic root lift is real, nontrivial, and Frobenius compatible,
but it does not add hidden information. It is a structured reparameterization:

```text
Q in E_b[r]  <->  R in E'_b[r].
```

Every rational function of the corrected lift is consequently a public
rational/isogeny observable of `Q`. The root cover by itself cannot supply the
missing absolute EDS-residue gauge.

This does not prove that no function on the isogenous curve can equal
`rho_G(Q)`. It proves that such a function would be a genuine new decoder on an
isomorphic prime-order group, not information created by the cubic root or by
Frobenius descent.

## 6. Exact replay

The verifier checks every nonzero point in fifteen frozen `j=0` prime-order
subgroups:

```text
subgroup orders: 19 through 4021
total nonzero points: 14298
```

For every point it verifies:

1. `delta^3=1`;
2. the corrected root has norm `x`;
3. the descended cubic equation;
4. the `E'` equation;
5. `pi(R)=Q`;
6. `R=[-3^(-1)]pi_hat(Q)`;
7. `pi(pi_hat(Q))=-[3]Q`.

All checks pass.

Artifacts:

- `experiments/parity_lift_000/eisenstein_cover_isogeny.py`;
- `experiments/parity_lift_000/eisenstein_cover_isogeny_results.json`.

## 7. Updated disposition

The eight-stage Eisenstein investigation now has a stronger answer:

```text
direct Gaussian sqrt(x) analogue:       absent
canonical Eisenstein cubic root:         exists
Frobenius-compatible descent:            exists
new independent phase information:       no
identity of the lift:                     inverse 3-isogeny
natural binary-character scaling:        negative
sub-square-root rho_G decoder:            absent
```

The next positive mechanism must not be merely a rational function on this
degree-three cover produced by bounded isogeny transport. It must introduce an
absolute section or relation not equivalent to a fixed isogeny
reparameterization and not invariant under the existing quadratic EDS gauge.
