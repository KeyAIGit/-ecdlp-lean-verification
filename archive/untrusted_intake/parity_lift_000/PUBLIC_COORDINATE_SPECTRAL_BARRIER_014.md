# PUBLIC-COORDINATE-SPECTRAL-BARRIER-014

Date: 2026-08-12

Status: **scoped analytic boundary plus frozen toy replay**.

No external point, key, wallet, or production-sized discrete-log target is
accepted. This package constructs no carry oracle, no EDS-residue decoder, and
no unconditional sub-square-root secp256k1 algorithm.

## 1. Why this package exists

`GLV-CARRY-FOURIER-REDUCTION-007` established that an exact carry oracle on
chosen scalar multiples is algorithmically decisive. The carry has a known
constant-heavy spectrum, and hidden multiplication permutes that spectrum.

The remaining constructive question was whether a simple public point
predicate already has a large enough Fourier coefficient to enter the same
local-SFT pipeline.

`PUBLIC-SPECTRAL-DECODER-011-V2` tested a normalization-aware family including
coordinate signs, field GLV carry, field permutation orientation, fixed-index
division characters, and small products. On the six largest frozen orders, the
best coefficient decreased from approximately `0.12597` at order `967` to
`0.06262` at order `4021`. Multiplication by `sqrt(n)` kept the values in a
small constant range, while multiplication by `log(n)` decreased. No candidate
was repeatedly at least `1/log(n)`.

This package explains rigorously why two central x-coordinate candidates have
that square-root scale:

```text
half_x
field_carry_x
```

## 2. Field-to-group Fourier transfer

Let `E/F_p` be an ordinary elliptic curve and let `G` generate a cyclic subgroup
of order `n`. For a function `F : F_p -> C`, define the public point observable

```text
h_F(0) = 0,
h_F(k) = F(x([k]G)) for k != 0.
```

Use normalized Fourier transforms

```text
Fhat(a) = (1/p) * sum_x F(x) e_p(-a*x),
hhat(j) = (1/n) * sum_k h_F(k) e_n(-j*k).
```

Fourier inversion over `F_p` gives

```text
hhat(j)
  = sum_a Fhat(a)
      * (1/n) sum_k e_p(a*x([k]G)) e_n(-j*k),
```

up to the harmless convention at the point at infinity. For `j != 0`, the
constant field-frequency term contributes only `O(1/n)`.

The inner sum is a twisted elliptic Gaussian sum. The standard estimate is

```text
sum_k e_p(a*x([k]G)) e_n(-j*k) = O(sqrt(p))
```

for `a != 0`, uniformly in the nontrivial group character. Consequently,

```text
|hhat(j)|
  <= O(sqrt(p)/n) * ||Fhat||_1 + O(1/n).              (T)
```

For a cofactor-one curve with `n = #E(F_p)`, Hasse gives `n = p + O(sqrt(p))`.
Thus

```text
|hhat(j)| <= O(||Fhat||_1 / sqrt(p)).                 (C1)
```

### Source note

Ahmadi and Shparlinski, *Exponential Sums over Points of Elliptic Curves*,
recall the `O(q^(1/2))` twisted single-sum estimate as Lemma 1 and use it in the
proof of their Theorem 3. The displayed Lemma 1 in the PDF prints the factor as
`chi(G)`, which is constant and is evidently a source-level typographical
error. The proof uses the varying group character `chi(S)`, and the intended
specialization is `chi([k]G)`.

## 3. Half-interval x-coordinate predicate

For odd `p`, let

```text
H_p(0) = 0,
H_p(x) = +1 for 1 <= [x]_p <= (p-1)/2,
H_p(x) = -1 for (p+1)/2 <= [x]_p <= p-1.
```

The mean is zero. A geometric-series estimate gives, for nonzero field
frequency `a`,

```text
|Hhat_p(a)|
  <= 1/(p*|sin(pi*a/p)|) + 1/p.
```

Using symmetry and

```text
sin(pi*a/p) >= 2a/p,
1 <= a <= (p-1)/2,
```

we obtain

```text
||Hhat_p||_1 <= H_((p-1)/2) + 1 = O(log p).          (H)
```

Substitution into (C1) yields

```text
max_(j != 0) |hhat_H(j)| = O(log(p)/sqrt(p)).         (HX)
```

So `half_x` cannot retain an inverse-polylogarithmic group-Fourier coefficient
on increasing cofactor-one curves.

## 4. Public field GLV carry is three centered sawtooths

Assume `p = 1 mod 3`, and let `beta` be a nontrivial cube root of unity in
`F_p`. For nonzero `x`, choose canonical representatives

```text
x0 = [x]_p,
x1 = [beta*x]_p,
x2 = [beta^2*x]_p.
```

Since `1 + beta + beta^2 = 0 mod p`,

```text
x0 + x1 + x2 = gamma_p(x) * p,
gamma_p(x) in {1,2}.
```

Define the public field carry sign

```text
C_beta(x) = 2*gamma_p(x) - 3 in {-1,+1},
C_beta(0) = 0.
```

Let the centered sawtooth be

```text
B_p(0) = 0,
B_p(u) = [u]_p/p - 1/2 for u != 0.
```

Then the exact integer identity is

```text
C_beta(x)
  = 2 * (B_p(x) + B_p(beta*x) + B_p(beta^2*x)).       (S)
```

The verifier checks the numerator form of (S) without floating-point
arithmetic:

```text
(2*x0-p) + (2*x1-p) + (2*x2-p)
  = C_beta(x) * p.
```

For every nonzero field frequency,

```text
|Bhat_p(a)| = |cot(pi*a/p)|/(2p).
```

Hence

```text
||Bhat_p||_1 <= (1/2) H_((p-1)/2),
||Chat_beta||_1 <= 3 H_((p-1)/2) = O(log p).          (L1)
```

Combining (L1) with (C1),

```text
max_(j != 0) |widehat(C_beta(x([k]G)))(j)|
  = O(log(p)/sqrt(p)).                                (FC)
```

This closes the direct `field_carry_x` local-SFT route for cofactor-one curves.

## 5. Complexity consequence

Akavia's deterministic local-SFT theorem runs in time polynomial in

```text
log |G|, 1/tau, and Fourier-L1.
```

For the scalar GLV carry itself, `tau` can be a constant because its principal
coefficient approaches `1/pi`.

For `half_x` and `field_carry_x`, equations (HX) and (FC) give at best

```text
tau = O(log(p)/sqrt(p)).
```

Therefore

```text
1/tau = Omega(sqrt(p)/log(p)),
```

which is exponential in the bit length `log p`. A local-SFT invocation on these
public predicates does not yield a polynomial-time ECDLP reduction.

## 6. Corrected frozen census

The normalization-aware replay used

```text
C_G(k) = s^k * rho_G(k),
```

where the point-scale character `s` is derived independently on each frozen
curve. This supersedes the earlier secp-specialized assumption `s=-1`.

The corrected large-order summary is:

| order | best public observable | max coefficient | coefficient*sqrt(n) | coefficient*log(n) |
|---:|---|---:|---:|---:|
| 811 | `half_x` | 0.11370261 | 3.238030 | 0.761611 |
| 967 | `field_carry_x*chi_y` | 0.12597097 | 3.917272 | 0.865949 |
| 1093 | `field_carry_x*field_permutation*half_y` | 0.12470277 | 4.122742 | 0.872506 |
| 1249 | `field_permutation*half_y` | 0.09630846 | 3.403656 | 0.686689 |
| 3469 | `chi_psi_7_C3` | 0.06400354 | 3.769694 | 0.521733 |
| 4021 | `field_carry_x*half_y` | 0.06262487 | 3.971128 | 0.519742 |

No tested candidate was repeatedly at least `1/log(n)` on the large frozen
orders. The finite data are compatible with square-root-scale character sums.
The data alone are not a lower bound, but they agree with the analytic x-only
boundary above.

## 7. Statistical gate correction

`CM-COORDINATE-CARRY-010` originally marked a positive follow-up because it
found one exact decoder and one nominal 95th-percentile exceedance.

The exact decoder occurs only at order `19`. There is no exact decoder at the
predeclared scaling floor `n >= 271`.

One nominal 95th-percentile exceedance among 15 independent case-level tests is
not surprising:

```text
Pr(at least one exceedance) = 1 - 0.95^15
                            = 0.5367087698...
```

Among the 12 scale-qualified cases the corresponding probability is about
`0.45964`. The sole large exceedance is at order `1249`, with add-one strict-tail
estimate approximately `0.00748`; it does not pass Holm-Bonferroni correction.
No `R3` case passes either.

The corrected gate is therefore:

```text
no scale-qualified exact decoder,
no multiple-testing-corrected carry correlation,
no multiple-testing-corrected R3 correlation.
```

The order-19 identity remains recorded as a finite resonance, not promoted as a
scaling signal.

## 8. What this closes

The theorem closes the following class on cofactor-one ordinary curves:

```text
h(P) = F(x(P)),
||Fhat||_1 = polylog(p).
```

In this class every nonzero scalar-domain Fourier coefficient is at most

```text
polylog(p)/sqrt(p)
```

up to the constant in the elliptic Gaussian-sum theorem.

Concrete closed predicates include:

```text
half_x
field_carry_x
any fixed linear combination or bounded product whose field-Fourier L1
remains polylogarithmic and whose required hybrid sum has the same square-root
bound
```

The last line is conditional on proving the corresponding hybrid sum and must
not be silently generalized.

## 9. What remains open

This package does not close:

```text
y-dependent interval predicates,
products mixing additive coordinate order with multiplicative characters,
high-complexity field circuits with large Fourier L1,
non-coordinate analytic or p-adic monodromy,
a direct public R3 decoder,
a direct public cyclotomic carry section.
```

The next useful mathematical target is not another x-coordinate threshold. It
is a genuinely mixed additive-multiplicative observable for which one can prove
one of two outcomes:

```text
1. an inverse-polylogarithmic scalar-domain Fourier coefficient; or
2. a square-root hybrid character-sum bound closing the whole family.
```

A natural next package is:

```text
MIXED-Y-HYBRID-SUM-BOUNDARY-015
```

focused on `half_y`, `chi_y`, and products with `field_carry_x` and field
permutation orientation.

## 10. Frozen artifacts

```text
experiments/parity_lift_000/public_coordinate_spectral_barrier.py
Ecdlp/Proved/PublicCoordinateSpectralBoundary.lean
.github/workflows/public-coordinate-spectral-barrier.yml
```

The workflow reruns:

```text
CM-COORDINATE-CARRY-010
PUBLIC-SPECTRAL-DECODER-011-V2
PUBLIC-COORDINATE-SPECTRAL-BARRIER-014
```

and uploads all three result files.

## Primary anchors

1. Omran Ahmadi and Igor E. Shparlinski, *Exponential Sums over Points of
   Elliptic Curves*, arXiv:1302.4210, especially the `O(q^(1/2))` single-sum
   estimate recalled in Section 2.1 and used in Theorem 3.
2. Adi Akavia, *Finding Significant Fourier Transform Coefficients
   Deterministically and Locally*, ECCC TR08-102, for local SFT over arbitrary
   finite abelian groups and runtime polynomial in `log|G|`, `1/tau`, and
   Fourier `L1`.
3. Kristin Lauter and Katherine Stange, *The Elliptic Curve Discrete Logarithm
   Problem and Equivalent Hard Problems for Elliptic Divisibility Sequences*,
   for the EDS-residue and parity-oracle reductions.

## Claim boundary

The field carry decomposition, cotangent magnitudes, harmonic `L1` estimates,
and finite statistical audit are replayed directly. The elliptic Gaussian-sum
input is external and source-pinned. The result is a scoped no-go theorem for
low-field-Fourier-`L1` x-coordinate observables, not a universal lower bound for
all public predicates or all ECDLP algorithms.
