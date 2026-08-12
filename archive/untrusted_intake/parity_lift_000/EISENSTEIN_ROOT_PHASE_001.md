# EISENSTEIN-ROOT-PHASE-001

Date: 2026-08-11

Status: isolated, non-executable structural and toy-scaling result. This package
targets no external point, wallet, or production discrete-log instance. It
changes no canonical Research Engine state and makes no asymptotic-improvement
claim.

## Question

For the secp256k1-type curve

```text
E_b: y^2 = x^3 + b
```

with `j=0` and Eisenstein complex multiplication, does the degree-three
endomorphism related to `1-omega` carry a canonical Frobenius-compatible root
phase analogous to the Gaussian `sqrt(x)` correction, and can the resulting
public phase decode

```text
rho_G([k]G) = chi(psi_k(G))
```

with improving accuracy as the subgroup order grows?

The package separates the question into eight stages.

## 1. The Eisenstein endomorphism

Let `beta` be a primitive cube root of unity in the base field. The order-three
automorphism is

```text
[omega](x,y) = (beta*x,y).
```

The endomorphism

```text
phi = 1-omega
```

has degree

```text
Norm(1-omega)=3.
```

Over a field containing `c` with `c^2=b`, its kernel is

```text
{O, (0,c), (0,-c)}.
```

The two nonzero kernel points sum to `O`, so `phi` is unbiased. Up to the
normalizing scalar, its ordinary generalized division function is therefore

```text
Psi_(1-omega) = x,
```

because

```text
div(x) = (0,c) + (0,-c) - 2(O).
```

Thus the degree-three endomorphism itself produces the already public
x-coordinate, not an additional root phase.

## 2. Why the Gaussian `sqrt(x)` mechanism has no direct Eisenstein copy

For Gaussian integers, the norm of `1+i` is two. The corresponding cyclic
degree-two isogeny is biased, and the extra correction is the source of Ward's
`sqrt(x)` factor.

For Eisenstein integers,

```text
Norm(a+b*omega)=a^2-a*b+b^2.
```

Modulo two this norm vanishes only when both `a` and `b` are even. Consequently
every even Eisenstein norm is divisible by four. In particular:

```text
there is no Eisenstein element of norm 2,
there is no norm class congruent to 2 modulo 4.
```

Durst's equianharmonic classification is consistent with this arithmetic:
odd-norm terms are polynomial in the x-coordinate, while even-norm terms carry
the ordinary y-factor. There is no fractional `sqrt(x)` class analogous to
Ward's oddly-even Gaussian case.

**Disposition:** the literal Gaussian-to-Eisenstein root-factor transfer is
closed.

## 3. The next root divisor

The absence of a degree-two correction does not eliminate all root covers. Let

```text
T=(0,c),     c^2=b.
```

Then `T` has order three and

```text
div(y-c)=3(T)-3(O).
```

Therefore the natural Eisenstein candidate is not `sqrt(x)` but the cubic cover

```text
u^3 = y-c.
```

For secp256k1, `b=7` is a nonsquare in the base field, so `c` lives in
`F_(p^2)` and Frobenius sends

```text
c^p=-c.
```

## 4. Canonical evaluation of the cubic root

Assume

```text
p = 7 mod 9,
p = 1 mod 3,
c^2=b is nonsplit over F_p.
```

For a rational point `Q=(x,y)`, put

```text
A(Q)=y-c.
```

Its norm is

```text
A(Q)*A(Q)^p = (y-c)(y+c)=x^3.
```

The cubic character of `A(Q)^p` equals that of `A(Q)` because `p=1 mod 3`.
Since their product is a cube, `A(Q)` itself is a cube in `F_(p^2)`.

Moreover,

```text
v_3(p^2-1)=1.
```

Hence the cube subgroup has order prime to three and cubing is a bijection on
that subgroup. There is a unique root `u(Q)` inside it. It is directly
computable by exponentiation:

```text
M=(p^2-1)/3,
e=3^(-1) mod M,
u(Q)=A(Q)^e.
```

This removes the usual three-way branch ambiguity without knowing `k`.

For the fixed secp256k1 prime, the required public arithmetic conditions hold:

```text
p mod 36 = 7,
p mod 9  = 7,
7 is a quadratic nonresidue.
```

So the canonical lift exists on the target field extension. Existence of the
lift is not yet an EDS-residue decoder.

## 5. Frobenius and negation laws

Frobenius gives the canonical root of the conjugate divisor:

```text
u(Q)^p^3 = y+c.
```

For point negation,

```text
u(-Q) = -u(Q)^p.
```

Define descended base-field coordinates

```text
D_j(Q) = (u(Q)^j-u(Q)^(j*p))/c,
T_j(Q) =  u(Q)^j+u(Q)^(j*p).
```

Both lie in `F_p`. Their negation laws are

```text
D_j(-Q)=(-1)^(j+1) D_j(Q),
T_j(-Q)=(-1)^j     T_j(Q).
```

Therefore:

```text
D_j is Kummer invariant for odd j,
T_j is Kummer invariant for even j.
```

These are canonical, public, nonlinear Frobenius-descended observables of
`x(Q)`. This is a positive structural result: the candidate class is
well-defined and efficiently evaluable.

## 6. Binary phase family

The bounded screen tests the natural binary characters

```text
chi(D_j(Q))  for odd j,
chi(T_j(Q))  for even j,
```

for `1 <= j <= 24`, both alone and multiplied by `chi(x(Q))`.

A direct multiplicative character of the cube root does not create the desired
new bit:

- the quadratic character is unchanged by taking an odd cube root;
- the cubic character is trivial on the chosen cube subgroup;
- passing to an extension where further cubic roots exist does not by itself
  provide a canonical binary output.

The trace and anti-trace coordinates above are the smallest nonmultiplicative
Frobenius descents that can retain information beyond those collapses.

## 7. Scaling screen

The frozen protocol uses fifteen prime-order `j=0` toy subgroups on

```text
y^2=x^3+7
```

with orders from `19` to `4021`. Per case it tests at most sixty
Kummer-invariant generators and the complete retained candidate family. A
global public sign is allowed.

To account for candidate and generator selection, each result is compared with
300 random Kummer-invariant target sequences scored against the identical
candidate pool.

Results:

```text
exact decoders found:                  0
cases above their matched 95% null:    0
maximum empirical null percentile:     0.91
```

For the two largest subgroups:

| order | observed best | matched null median | matched null 95% |
|---:|---:|---:|---:|
| 3469 | 0.53460 | 0.54268 | 0.54960 |
| 4021 | 0.53881 | 0.54080 | 0.54876 |

The best excess over one half remains approximately a constant multiple of
`1/sqrt(order)`:

```text
order 3469: (accuracy-1/2)*sqrt(order) = 2.04
order 4021: (accuracy-1/2)*sqrt(order) = 2.46
```

That is the behaviour expected from selecting the largest accidental
correlation from a fixed finite family, not from a decoder converging toward
accuracy one.

The exact script and frozen output are:

- `experiments/parity_lift_000/eisenstein_root_phase_screen.py`;
- `experiments/parity_lift_000/eisenstein_root_phase_results.json`.

**Disposition:** negative scaling evidence for this natural canonical
cube-root/Frobenius-character family.

## 8. secp256k1 boundary

The field and divisor construction applies algebraically to secp256k1, but the
cross-order toy gate failed. Therefore this package does not run the candidate
against an unknown secp256k1 target and does not promote a fixed-public scalar
screen as evidence.

The current answer is:

```text
A canonical Frobenius-compatible Eisenstein cubic-root lift exists.
The direct Gaussian sqrt(x) analogue does not exist.
The first natural descended binary-character family does not scale.
No sub-square-root EDS-residue decoder has been obtained.
```

## What remains open

This package closes only the most direct root-phase transfer. A future positive
candidate must leave at least one of the tested constraints:

1. a different theta section whose divisor is not generated solely by
   `3(T)-3(O)`;
2. a nonmultiplicative relation involving several Frobenius-conjugate root
   covers;
3. a 3-adic or analytic normalization with an exact precision and cost theorem;
4. an extension-field phase whose descent is not reduced to a fixed rational
   trace or anti-trace character;
5. an odd absolute EDS-residue relation outside quadratic net gauge.

The next useful theorem package should classify low-degree Frobenius-equivariant
functions on the cubic cover and determine whether every quadratic-character
output descends to the tested trace/anti-trace algebra. That would turn the
present empirical closure into a scoped algebraic no-go theorem.

## Primary anchors

- Katherine E. Stange, *Division Polynomials for Arbitrary Isogenies*, for
  biased versus unbiased isogenies, correction functions, and the Gaussian
  comparison.
- Lincoln K. Durst, *Apparition and Periodicity Properties of Equianharmonic
  Divisibility Sequences*, for Eisenstein norms and the polynomial/y-factor
  form of equianharmonic division terms.
- Repository anchors: `Ecdlp/Proved/SevenNonResidue.lean`,
  `Ecdlp/Proved/RelativeResidueGauge.lean`, and the `PARITY-LIFT-000` notes.
