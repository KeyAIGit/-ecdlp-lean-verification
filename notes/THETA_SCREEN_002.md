# Theta route screen 002

Date: 2026-08-11

Scope: bounded structural and synthetic-toy analysis. No secp256k1 discrete-log
instance is targeted, and no route promotion is claimed.

## 1. Exact collapse of the split Kummer plus GLV mechanism

Let

```text
E/F_p: y^2 = x^3 + 7
```

be secp256k1 and let the standard GLV constant satisfy

```text
beta^2 + beta + 1 = 0.
```

Let `alpha^3 = -7` in `K = F_{p^3}`. For the secp256k1 choice of `beta`,

```text
alpha^p = beta*alpha.
```

Define

```text
z = (x-alpha)/((beta-1)*alpha).
```

For `x in F_p`,

```text
z^p = beta^2*(z-1),
z^(p^2) = 1 + beta*z.
```

The GLV map `x -> beta*x` acts in the same coordinate by

```text
z(beta*x) = 1 + beta*z.
```

Therefore GLV equals inverse Frobenius on this split Kummer coordinate:

```text
z o GLV = z^(p^2).
```

It is not an independent second `C3` action.

The affine action `z -> 1 + beta*z` has fixed point

```text
z0 = 1/(1-beta).
```

With `w = z-z0`,

```text
w = x/((beta-1)*alpha),
w -> beta*w,
```

so

```text
w^3 = x^3/(((beta-1)*alpha)^3).
```

Thus the cubic orbit invariant is an invertible scalar multiple of `x^3`.
The proposed theta/Kummer plus GLV quotient reproduces the already studied
coordinatewise `u=x^3` quotient rather than defining a new quotient.

**Status:** closed as a new mechanism.

## 2. Full-point Jacobi extended formulation

The Jacobi intersection

```text
s^2 + c^2 = 1,
a*s^2 + d^2 = 1
```

is a genuine theta-compatible model with strongly-unified low-degree addition
formulas. A projective chain has much lower input degree and fewer input
monomials than direct `S4`, but many more variables.

A six-field distinct-point SymPy screen gave:

- direct Semaev lex: approximately 0.037 to 0.040 seconds;
- direct Semaev grlex: approximately 0.193 to 0.206 seconds;
- projective Jacobi grlex: approximately 1.78 to 2.05 seconds.

The projective representation was about 45 times slower than direct lex and
about 9 times slower than direct grlex in this screen, despite a lower final
Groebner degree.

**Status:** negative at the current toy scale, but not an asymptotic closure.

## 3. Factor-base degree compression

A Jacobi-native factor base formed from `h` allowed values of `s^2` represents
`4h` Weierstrass x-values. Its factor polynomial has degree `2h`, whereas the
direct x-factor polynomial has degree `4h`.

This is the strongest surviving algebraic mechanism.

SymPy results over `F_43`:

| h | x-base size | direct lex | direct grlex | projective grlex |
|---:|---:|---:|---:|---:|
| 1 | 4 | 0.042 s | 0.205 s | 1.74 s |
| 2 | 8 | 1.58 s | over 20 s | over 20 s |
| 3 | 12 | 14.63 s | not continued | over 20 s |

These timings are implementation-specific. At `h >= 2`, SymPy no longer
distinguishes whether the degree compression is useful because both grlex
computations exceed the bounded screen. SageMath/Singular is therefore the
proper independent next test.

**Status:** open only as a solver-specific scaling question.

## 4. p-adic canonical-theta boundary

Canonical theta structures on canonical lifts of ordinary abelian varieties
are mathematically real. However, they do not by themselves linearize the
prime-to-p torsion subgroup.

Let `Ehat` be the formal group of a good lift over a p-adic complete discrete
valuation ring. For `n` prime to `p`,

```text
[n](T) = n*T + O(T^2)
```

has unit linear coefficient. It is therefore an invertible formal power series.
Consequently,

```text
Ehat[n] = 0.
```

The secp256k1 subgroup has prime order `n != p`, so no nonzero group element
can be moved into the formal kernel while preserving its n-torsion structure.
The ordinary formal logarithm and a canonical lift therefore provide no direct
linearization of the requested discrete logarithm.

A p-adic theta route remains meaningful only if it supplies a different,
explicit observable whose precision and evaluation cost scale favorably and
whose value determines the scalar. No such observable is currently specified.

**Status:** direct formal-log interpretation closed; unspecified analytic
mechanism remains unformulated.

## Current route disposition

| Subroute | Result |
|---|---|
| x-only theta/Kummer coordinate change | closed: Mobius reparameterization |
| theta/Kummer plus GLV or Frobenius | closed: exactly the existing x-cubing mechanism |
| full-point Jacobi low-degree chain | toy negative |
| Jacobi-native factor-base compression | bounded open question for Singular |
| canonical-lift formal logarithm | closed on prime-to-p torsion |
| other p-adic theta observable | not testable until an explicit map and precision model are supplied |

The only scientific next step proposed by this note is a bounded, synthetic,
independently reproducible Singular screen of factor-base scaling. It must not
target secp256k1 and must not be interpreted as route promotion or as execution
authorization under the repository decision substrate.

## Sources and relation to existing repository evidence

- Robert Carls, *Canonical coordinates on the canonical lift*, proves the
  existence of a canonical theta structure for the canonical lift of an
  ordinary abelian variety.
- Luca Cesarano, *Biquadratic addition laws on elliptic curves in P3*, studies
  biquadratic addition laws on the Jacobi model as a complete intersection of
  two quadrics.
- The Explicit-Formulas Database supplies the strongly-unified Jacobi formulas
  used by the synthetic system.
- `notes/GLV_SEMAEV_ITERATION_001.md` and
  `experiments/glv_diagonal_obstruction/README.md` already establish that the
  coordinatewise `x_i^3` quotient is not the exact diagonal GLV quotient and
  loses relative phase. This screen shows that the split Kummer construction
  reduces to that same coordinatewise cubic mechanism up to invertible scaling.
