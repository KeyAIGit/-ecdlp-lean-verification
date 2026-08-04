# RH source contracts

Status: **proposed source-contract package under independent review; no proof
or progress claim**

These contracts propose the source semantics for the Li/Weil and
Nyman-Beurling/Báez-Duarte screens. They become normative only after review.
They do not assert that any missing theorem has been proved or formalized.

Publishing this document does not complete `RH-001`, activate `RH-002`, or
close `S0-TRUST`. The unnamed direct explicit-formula route remains `PARKED`;
the explicit formula is admitted only as a dependency screen for the
Weil-first Li route.

## Contract rules

Every statement has one of four roles:

- `SOURCE`: specified by a pinned primary source;
- `DERIVED`: an elementary normalization or sign calculation that must be
  independently checked;
- `FORMAL-OBLIGATION`: a theorem needed to map a source statement to Mathlib;
- `RESEARCH-OBLIGATION`: a genuinely new bound needed to prove RH.

A condition equivalent to RH may be used inside an equivalence proof with RH
as an explicit hypothesis. It must not be imported as an unconditional
estimate.

A sum over zeros always counts analytic multiplicity. No source star-limit may
be replaced by `tsum`, reordered, or assigned a different cutoff without a
proved conversion theorem.

## Local pinned source table

These local IDs are document shorthand, not entries claimed to exist in the
generated source registry. The mapping column points back to the canonical
IDs in `corpus.md`; `LAG07` is an additional final-publication source supporting
the existing Li rows and needs a separate provenance change before it can
become a canonical registry row.

| local ID | canonical corpus mapping | pinned source | normative locators | audited PDF SHA-256 |
|---|---|---|---|---|
| `LAG07` | supports `RH-SRC-003` and `RH-SRC-004`; not yet a canonical row | Jeffrey C. Lagarias, [final Numdam PDF](https://www.numdam.org/item/10.5802/aif.2311.pdf), *Li Coefficients for Automorphic L-Functions*, Ann. Inst. Fourier 57 (2007), DOI [10.5802/aif.2311](https://doi.org/10.5802/aif.2311) | §1, (1.1)-(1.8); §2, Theorem 2.1, Lemmas 2.2-2.3, Theorem 2.4, (2.16)-(2.22); §3, (3.1)-(3.4), Theorem 3.1; §4, Lemma 4.1; Appendix A, (A.1)-(A.7) | `d1c3175591daff6a7f7503c8452eee0ce2536280cb9ce468a6c0a159be4d9f9b` |
| `BOM-CLAY` | `RH-SRC-001` | E. Bombieri, [*Problems of the Millennium: The Riemann Hypothesis*](https://www.claymath.org/wp-content/uploads/2022/05/riemann.pdf), Clay official description, 11-page PDF created 2000-08-30 | §V, printed pp. 8-9 | `1454b2909f99271726ffb68b056aef45b7d3e6893a66282cad596339d69bafa9` |
| `BD02-v2` | `RH-SRC-005` | Luis Báez-Duarte, [*A strengthening of the Nyman-Beurling criterion*, arXiv v2](https://arxiv.org/pdf/math/0202141v2), 2002-02-18 | Theorem 1.1; (1.1)-(1.3); Lemmas 2.1-2.2; (2.1)-(2.9); Corollary 3.1 | `3ce4aff466443c71094affc1f8b6f5f0dd36cb4377dc5d2ceddbd2537c1d1819` |
| `MATHLIB-PIN` | pinned code is authoritative for `RH-SRC-008` | Mathlib revision `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` | locators in `MATHLIB_CAPABILITY_MAP.md`; `Analysis/Analytic/Order.lean:61` for `analyticOrderNatAt` | Git commit pin above |

The final published `LAG07` numbering is normative. Earlier arXiv versions use
different theorem numbers.

## Shared notation and target mapping

`SOURCE`: where all raw pointwise factors are regular, the classical
expression is

```text
xi_classical(s) =
  (1/2) * s * (s - 1) * pi^(-s/2) * Gamma(s/2) * zeta(s).
```

The source `xi` is the unique entire continuation of this expression across
`s = 0`, `s = 1`, and the negative even gamma-pole points. The raw product is
not a valid global definition using Mathlib's totalized `riemannZeta` and
`Gamma` values.

For the trivial `GL(1)` representation, `LAG07` (2.7) uses the normalization
`xi(s, pi_triv) = 2 * xi_classical(s)`. This constant does not change its
zeros, analytic multiplicities, logarithmic derivative, or Li coefficients.
The global `riemannXi` interface below retains the classical endpoint value
`1/2`.

`FORMAL-OBLIGATION`: define the global entire candidate from the proved
pole-removed completion by

```text
riemannXi(s) =
  (1 + s * (s - 1) * completedRiemannZeta₀(s)) / 2.
```

Prove, under `s != 0` and `s != 1`, equality with
`s * (s - 1) * completedRiemannZeta(s) / 2`. Prove equality with the raw
`xi_classical` product only after additionally excluding
`s = -2 * (k + 1)` for every `k : ℕ`. Derive values at all excluded points
from the entire formula and symmetry, not from totalized pointwise products.

Let `S_xi` be the set of distinct zeros of `riemannXi`, and define the
analytic multiplicity weight

```text
m(rho) = ord_rho(riemannXi).
```

The pinned natural-number representation is
`analyticOrderNatAt riemannXi rho`, derived from `analyticOrderAt` after
proving analyticity and that the order is not `top`. The zero support and this
weight must be packaged as a locally finite divisor. A Lean `Multiset` cannot
represent the infinite divisor.

Every displayed zero sum below ranges over `S_xi` and multiplies by `m(rho)`
exactly once. This weighted-support model represents the source multiset
without double-counting multiplicity.

Required properties:

1. `riemannXi` is entire of order one.
2. `riemannXi(0) = riemannXi(1) = 1/2`.
3. Its zeros are exactly the nontrivial zeta zeros.
4. `S_xi` omits `0` and `1`.
5. The following symmetries preserve multiplicity:

   ```text
   rho |-> 1 - rho
   rho |-> conj(rho)
   rho |-> 1 - conj(rho).
   ```

`FORMAL-OBLIGATION`:

- prove the off-endpoint equality above without copying the conflicting
  Mathlib module-header signs;
- construct `S_xi` and `m` from `analyticOrderAt` and package them as a
  locally finite divisor;
- prove, under `s != 0`, `s != 1`, and
  `not exists k : ℕ, s = -2 * (k + 1)`, the exact bridge

  ```text
  riemannXi(s) = 0 <-> riemannZeta(s) = 0;
  ```

  the reverse direction depends on `Gammaℝ_eq_zero_iff`, not field algebra
  alone;
- prove `riemannXi` is nonzero at every negative even point by reflection to
  the positive half-plane and `riemannZeta_ne_zero_of_one_le_re`, before using
  critical-strip localization;
- prove at every nontrivial zero `rho` the multiplicity theorem

  ```text
  analyticOrderNatAt riemannXi rho
    = analyticOrderNatAt riemannZeta rho;
  ```

  set-level zero equality is not enough for residue or divisor sums;
- prove exact equivalence between each source RH formulation and
  `_root_.RiemannHypothesis`;
- do not introduce a competing canonical RH proposition.

### `SC-XI-01`: growth, zero counting, and normalized Hadamard product

`SOURCE`: specialized to the trivial `GL(1)` representation, `LAG07`
Theorem 2.1(3), (4), and (6), Lemma 2.2, and Lemma 4.1 give critical-strip
localization, the two-sided zero-counting asymptotic (2.11), entire order one,
the power-sum convergence, and a genus-one Hadamard factorization. The
factor-of-two normalization noted above leaves these statements unchanged
except for the product's leading constant.

`FORMAL-OBLIGATION`: freeze and prove all of the following before defining a
global Li zero sum:

1. an unconditional entire-growth theorem strong enough for order at most
   one, with its exact Mathlib predicate or an explicit equivalent bound;
2. for `T : ℝ` with `2 <= T`, a multiplicity-aware counting function

   ```text
   N_xi(T) = sum_{rho in S_xi, |rho| <= T} m(rho)
   ```

   and constants `C > 0` and `T0 >= 2` such that
   `N_xi(T) <= C * T * log T` for every `T >= T0`, derived from the
   source asymptotic rather than admitted as a new hypothesis;
3. convergence of `sum m(rho) / |rho|^2` and existence of the radial
   star-limit of `sum m(rho) / rho`;
4. locally uniform convergence of the genus-one canonical product and the
   exact exponential factor

   ```text
   riemannXi(s) = riemannXi(0) * exp(A_xi*s)
     * product_{rho in S_xi}
         ((1 - s/rho) * exp(s/rho)) ^ m(rho);
   ```

5. equality between the logarithmic derivative of this normalized product on
   a zero-free neighborhood and the source radial star-sum, including

   ```text
   A_xi = riemannXi'(0) / riemannXi(0)
        = -starSum_{rho in S_xi} m(rho) / rho.
   ```

The product uses the weighted support exactly once and one declared radial
cutoff. The constant `A_xi`, the `n = 1` coefficient, and the local logarithm
normalization must be identified rather than absorbed by an unspecified
entire factor. `analyticOrderAt` is a local zero-order API; it is not an
entire-growth theorem.

## Li coefficient contracts

### `SC-LI-01`: zero-sum admissibility

Variables:

- `n : ℤ`;
- `rho : ℂ` in `S_xi`;
- `T : ℝ` with `0 < T`.

`SOURCE`: the abstract multiset theorem in `LAG07` assumes

```text
sum_{rho in S_xi} m(rho) * re(rho) / (1 + |rho|)^2 < infinity
```

from `LAG07` (1.6), and star convergence of

```text
sum'_{rho in S_xi} m(rho) / rho.
```

This is a hypothesis of the general Lagarias criterion, not yet a proved fact
about `S_xi` in pinned Mathlib. Critical-strip localization would make its
terms nonnegative, but nonnegativity alone does not prove convergence.

`FORMAL-OBLIGATION`:

- derive weighted summability and star convergence from a
  multiplicity-aware zero-counting theorem;
- prove absolute convergence of `sum m(rho) * rho^(-j)` for `j >= 2`;
- preserve the source radial cutoff.

### `SC-LI-02`: global Li coefficients

Let `n : ℤ` and `T : ℝ` with `0 < T`.

Define the finite cutoff

```text
lambda_n(T) =
  sum_{rho in S_xi, |rho| <= T}
    m(rho) * (1 - (1 - 1/rho)^n).
```

The Li coefficient is

```text
lambda_n = lim_{T -> infinity} lambda_n(T).
```

This is the star-limit in `LAG07` (1.1) and (1.8). Its contract is:

- cutoff: `|rho| <= T`;
- multiplicity: mandatory;
- convergence: star convergence, not absolute termwise convergence;
- `lambda_0 = 0`;
- positive and negative integer indices are both admitted.

The source occasionally uses `< T` inside proofs. The formal definition should
use `<= T` and prove boundary-insensitivity where needed.

### `SC-LI-03`: local derivative coefficients

For `n : ℕ` with `1 <= n`, let `L` be an analytic logarithm of `riemannXi`
on a neighborhood of `1`. Define

```text
localLambda_n =
  (1 / (n - 1)!) *
    (d^n / ds^n) [s^(n - 1) * L(s)] at s = 1.
```

This is `LAG07` (1.3). The required branch contract is:

1. prove `riemannXi(1) = 1/2`;
2. exhibit a neighborhood on which `riemannXi != 0`;
3. construct `L` with `exp L = riemannXi`;
4. prove the derivative is independent of the chosen local branch;
5. reject a global `Complex.log ∘ riemannXi`.

The source relation is

```text
localLambda_n = lambda_(-n).
```

It may be replaced by `lambda_n` only after proving the Riemann-xi symmetry
that makes the relevant coefficients real.

The local-global equality requires the normalized Hadamard product and the
exact star-sum convention. It must not be proved by a formal rearrangement of
conditionally convergent sums.

### `SC-LI-04`: one-sided Li criterion

After proving multiplicity-preserving invariance under

```text
rho |-> 1 - conj(rho),
```

the target source contract is

```text
RH <-> for every integer n >= 1, re(lambda_n) >= 0.
```

This is `LAG07`, Theorem 2.4.

`FORMAL-OBLIGATION`:

```text
_root_.RiemannHypothesis
  <-> for every positive natural n, re(liCoeff n) >= 0.
```

Finite positivity, finite PSD blocks, and numerical values do not satisfy this
contract.

## Lagarias Weil contracts

### `SC-WEIL-01`: Mellin-side test class

Let `A` contain functions `F` holomorphic on

```text
0 < re(s) < 1
```

and satisfying uniformly

```text
F(s) = O(1 / |s|) for |im(s)| >= 1.
```

Define the involution

```text
tilde(G)(s) = conj(G(1 - conj(s))).
```

For `F, G` in `A`, define

```text
<F, G>_W =
  sum_{rho in S_xi}
    m(rho) * F(rho) * conj(G(1 - conj(rho))).
```

This is `LAG07` (3.1). The combined sum is absolutely convergent. It is
linear in the first argument and conjugate-linear in the second.

### `SC-WEIL-02`: Li test class and Gram identity

The Li class `L` consists of rational functions that vanish at infinity and
have poles only at `0` or `1`. Define

```text
G_n(s) = 1 - (1 - 1/s)^n,  n : ℤ.
```

This is `LAG07` (3.2). For `n, m : ℤ`, Theorem 3.1 gives

```text
<G_n, G_m>_W = lambda_n + lambda_(-m) - lambda_(n-m)
```

and

```text
||G_n||_W^2 = lambda_n + lambda_(-n) = 2 * re(lambda_n).
```

All terms must be obtained from one common finite cutoff before taking limits.
Splitting three conditionally convergent sums and rearranging them independently
is forbidden.

## Bombieri explicit-formula contracts

### `SC-BOMB-01`: test class `W`

Let `f : ℝ_{>0} -> ℂ`. Require:

- continuity and `C^1` regularity except at finitely many points;
- first-kind discontinuities for `f` and `f'`, with midpoint values assigned;
- some `delta > 0` such that

  ```text
  f(x) = O(x^delta)       as x -> 0+
  f(x) = O(x^(-1-delta)) as x -> infinity.
  ```

Use the Mellin convention

```text
Mellin(f)(s) = integral_0^infinity f(x) * x^s * dx/x,
```

which is analytic for

```text
-delta < re(s) < 1 + delta.
```

### `SC-BOMB-02`: trace explicit formula

For `n : ℕ`, let `Lambda_vM(n) = log p` when there are a prime `p` and
`a : ℕ` with `1 <= a` and `n = p^a`, and let it be `0` otherwise. For
`f` in `W`, `BOM-CLAY` §V states

```text
Mellin(f)(0) - sum_rho Mellin(f)(rho) + Mellin(f)(1)
  = sum_{n >= 1} Lambda_vM(n) * (f(n) + (1/n) * f(1/n))
    + (log(4*pi) + EulerGamma) * f(1)
    + integral_1^infinity
        (f(x) + (1/x) * f(1/x) - (2/x) * f(1))
        * dx / (x - x^(-1)).
```

The zero sum means

```text
lim_{T -> infinity}
  sum_{rho nontrivial, |im(rho)| < T}
    m(rho) * Mellin(f)(rho).
```

Here `T : ℝ` tends through positive values.

Its contract is:

- cutoff: strict imaginary-height cutoff;
- multiplicity: required by the residue theorem, although §V leaves it
  implicit;
- endpoint terms: `Mellin(f)(0)` and `Mellin(f)(1)` remain on the spectral
  side;
- sign: the zero contribution has a minus sign.

### `SC-BOMB-03`: autocorrelation and negativity

Let `g : ℝ_{>0} -> ℂ` belong to `W`. Define using ordinary `dy`

```text
f_g(x) = integral_0^infinity g(x*y) * conj(g(y)) dy.
```

Do not replace `dy` by `dy/y`. Require

```text
integral_0^infinity g(x) dx/x = 0
integral_0^infinity g(x) dx   = 0.
```

Equivalently, `Mellin(g)(0) = Mellin(g)(1) = 0`.

Define `BombieriAdmissible(g)` to mean exactly that `g` belongs to `W` and
satisfies these two moment conditions. Do not silently shrink the source test
class by adding a stronger hypothesis.

`FORMAL-OBLIGATION`: the source does not prove that this weak piecewise-`C^1`
class is closed under autocorrelation. Do not assume that step. Use one of two
audited paths:

1. prove from `BombieriAdmissible(g)` that the autocorrelation exists, `f_g`
   belongs to `W` with both endpoint bounds, and absolute integrability permits
   Fubini on the stated Mellin strip; or
2. formalize Bombieri's covariance criterion directly on the autocorrelation
   class, with explicit convergence hypotheses and the same arithmetic
   functional.

A smoother core may be used for construction, but the RH equivalence may be
claimed for it only after a density and continuity theorem extends the result to
the full source class. Until one of these paths is proved, this regularity bridge
is a formalization blocker rather than an implicit premise.

`DERIVED`, after the required integral and interchange justifications:

```text
Mellin(f_g)(s) =
  Mellin(g)(s) * conj(Mellin(g)(1 - conj(s))).
```

Thus the endpoint terms vanish. If `Q_B(f)` denotes the arithmetic right-hand
side, the Bombieri criterion is

```text
RH <-> for every BombieriAdmissible g, Q_B(f_g) <= 0.
```

The sign is negative semidefinite, not strictly negative.

## Bombieri-Lagarias bridge and regularization

### `SC-BRIDGE-01`: trace-to-covariance sign

For `T : ℝ` tending to infinity through positive values, Lagarias
Appendix A defines

```text
W[f] = lim_{T -> infinity}
  sum_{rho in S_xi, |rho| <= T} m(rho) * Mellin(f)(rho),
```

in (A.3), and

```text
Trace[f] = Mellin(f)(0) - W[f] + Mellin(f)(1)
```

in (A.4), with

```text
Trace[f] = sum_nu W_nu(f)
```

in (A.5). The covariance rearrangement (A.6) is

```text
W[f] = -sum_nu W_nu(f) + W_0(f) + W_1(f).
```

When both endpoint moments vanish,

```text
Q_B(f) = sum_nu W_nu(f) = -W[f].
```

Bombieri negativity and Lagarias positivity therefore differ by exactly one
sign.

### `SC-BRIDGE-02`: cutoff conversion

Bombieri uses

```text
|im(rho)| < T,
```

while Lagarias uses

```text
|rho| <= T.
```

A formal bridge must prove equality of the resulting limits for the admitted
test function. Sharing the symbol `T` is not a proof.

### `SC-BRIDGE-03`: Li functions are not Bombieri trace-class tests

The `G_n` have poles at `0` or `1`. Consequently:

- they are not directly admissible in Bombieri's trace-class `W`;
- the trace functional is undefined for every nonzero Li test function;
- direct substitution of `G_n` into the §V trace formula is invalid.

Lagarias Appendix A permits the Li class only in an extended covariance
formulation.

### `SC-BRIDGE-04`: common regularization

The extended covariance contract must use one common parameter
`T : ℝ`, with `T -> infinity` through positive values:

- spectral cutoff: `|rho| <= T`;
- local cutoff: `x = 1/T` near zero and `x = T` near infinity;
- endpoint and finite-prime contributions are combined before taking the
  limit.

For Li inverse-Mellin functions, the endpoint divergence is cancelled by a
corresponding finite-prime divergence. Neither divergent component may be
assigned a separate infinite value.

`FORMAL-OBLIGATION`:

1. define the combined finite-`T` regularized expression;
2. prove its limit exists;
3. prove it equals the zero-side Weil form;
4. only then derive the arithmetic prime/archimedean representation of
   `2 * re(lambda_n)`.

`RESEARCH-OBLIGATION`:

```text
Prove a uniform arithmetic lower bound strong enough to give
re(lambda_n) >= 0 for every n : ℕ with 1 <= n.
```

## Báez-Duarte Nyman contracts

### `SC-NB-01`: Hilbert space and natural span

Use the real Hilbert space

```text
H = L2((0, infinity), dx).
```

Define

```text
rho(x)   = x - floor(x)
rho_a(x) = rho(1 / (a*x)),  a : real with 1 <= a
chi      = 1_(0,1].
```

Let

```text
B     = realSpan {rho_a | a : real, 1 <= a}
B_nat = realSpan {rho_a | a : positive natural}.
```

The `BD02-v2` abstract writes `(0,1)` while the body uses `(0,1]`; these
indicators agree almost everywhere.

Required object lemmas:

- measurability;
- membership in `L2`;
- dilation identities;
- finite-span membership;
- the inclusion `B_nat <= B` and monotonicity of closure;
- equivalence of real closure and the relevant complexification.

### `SC-NB-02`: closure criterion

Theorem 1.1 states

```text
RH <-> chi is in closure(B_nat).
```

`FORMAL-OBLIGATION`:

```text
_root_.RiemannHypothesis <-> chi is in closure(B_nat).
```

The formal theorem must prove both implications and map the source RH
statement through the canonical target bridge.

The reverse implication has an explicit source dependency:

```text
chi in closure(B_nat)
  -> chi in closure(B)
  -> RH by the classical Nyman-Beurling criterion.
```

The second arrow is the classical criterion quoted in the introduction of
`BD02-v2`; it must either be formalized as a pinned source edge or replaced by
a complete direct Mellin-functional proof. The RH-to-closure direction is the
new natural-span argument whose conditional inputs are recorded below.

### `SC-NB-03`: Mellin identity

For `0 < re(s) < 1`, the source identity is

```text
-zeta(s) / s = integral_0^infinity x^(s-1) * rho_1(x) dx.
```

Consequently,

```text
integral_0^infinity x^(s-1) * rho_a(x) dx
  = -a^(-s) * zeta(s) / s.
```

Do not substitute the classical `(0,1)` generator convention without a
separate affine correction and side condition.

### `SC-NB-04`: Fourier-Mellin isometry

Let `H_C` be the complexification of `H`. On the explicit dense core

```text
D = {f in H_C |
  u |-> exp(u/2) * f(exp(u)) has an L1 and L2 representative},
```

define

```text
M0(f)(tau) =
  integral_0^infinity x^(-1/2 + i*tau) * f(x) dx.
```

`FORMAL-OBLIGATION`:

1. prove `D` is dense in `H_C`;
2. prove the norm identity for `M0` after `x = exp(u)`;
3. extend `M0` uniquely by continuity to a complex-linear unitary map with
   inverse

```text
M : L2_C((0, infinity), dx)
      <->unitary L2_C(R, d tau/(2*pi)).
```

The pointwise integral formula is asserted only on `D`, not on every `L2`
equivalence class. `DERIVED`: the norm identity follows from the substitution
`x = exp(u)` and unnormalized Fourier Plancherel.

Source errata:

- `BD02-v2` typesets the target interval as `(infinity, infinity)`;
- `BD02-v2` typesets the measure as `(2*pi)^(-1/2) d tau`.

The formal contract uses `R` and `d tau/(2*pi)`, with the derivation recorded
rather than attributed literally to the typeset formula.

### `SC-NB-05`: proof dependency ledger

The Báez-Duarte RH-to-closure proof uses:

- Littlewood convergence of

  ```text
  sum mu(a) * a^(-s) = 1/zeta(s) for re(s) > 1/2;
  ```

- Lemma 2.1 specialized with zero-freeness in `re(s) > 1/2`;
- Lindelöf estimates derived from RH.

These inputs are `RH-DEPENDENT`. They may occur only below an explicit RH
hypothesis.

Lemma 2.2's zeta-ratio estimate is unconditional, but its quotient notation is
not zero-safe off RH. The formal contract is the cross-multiplied inequality

```text
|zeta(1/2 - epsilon + i*tau)|
  <= C * (1 + |tau|)^epsilon
       * |zeta(1/2 + epsilon + i*tau)|,
```

for `tau : ℝ` and `0 <= epsilon <= epsilon0 < 1/4`, where `C > 0` depends
only on `epsilon0`, with a corrected gamma-factor ratio derived from the
pinned functional equation. Do not copy the repeated-gamma-factor typesetting
error in the v2 proof, and do not form a quotient at a zero of the denominator.
This unconditional estimate does not remove the RH dependence of the
preceding construction.

The final unconditional limit `f_epsilon -> -chi` cannot be combined with
RH-dependent membership `f_epsilon in closure(B_nat)` to create an
unconditional proof.

### `SC-NB-06`: pilot-family admissibility

For a general finite Beurling combination with `r : ℕ`, `1 <= r`, coefficients
`c_k : ℝ`, and indices `a_k : ℝ` satisfying `1 <= a_k`,

```text
F = sum_{k=1}^r c_k * rho_(a_k),
```

define its scale by `N(F) = max_k a_k`; it is not the number of summands.
The source lower bound (1.2) uses this real-valued scale. Pilot families below
add the stronger requirement that every `a_k` is a positive natural number.

The raw family

```text
F_N = sum_{1 <= a <= N} mu(a) * rho_a
```

from `BD02-v2` (1.1) diverges in `H` and is rejected.

Any admitted family must provide:

1. explicit finite coefficients and positive-natural indices, with the
   parameter `N` declared as the maximum index/scale rather than an implicit
   term count;
2. a complete identity for `||chi - F_N||_H^2`;
3. an unconditional bound `B(N)`;
4. explicit constants and range;
5. a proof that `B(N) -> 0`;
6. no RH-equivalent zero-free, Littlewood, or Lindelöf premise.

The required source rate check for the general `F` above is

```text
||F - chi||_H >= C / sqrt(log N(F)).
```

Here `C > 0` is absolute and the formula is asserted only when `N(F) > 1`,
so its denominator is defined. This is `BD02-v2` (1.2).

An iterated limit `n -> infinity` followed by `epsilon -> 0+` does not
automatically provide a single explicit diagonal family. Quantitative
diagonalization must be proved.

## Anti-circularity rejection matrix

| attempted step | disposition |
|---|---|
| replace a star-limit by `tsum` | reject |
| change `|rho| <= T` to `|im(rho)| < T` without proof | reject |
| erase multiplicity | reject |
| use zero-set symmetry without multiplicity preservation | reject |
| use a global logarithm of `riemannXi` | reject |
| substitute `G_n` directly into Bombieri `W` | reject |
| separate divergent endpoint and prime terms | reject |
| flip Bombieri negativity to Lagarias positivity without endpoint and sign derivation | reject |
| use raw Nyman Möbius approximants | reject |
| use Littlewood, Lindelöf, or zero-free `re(s) > 1/2` unconditionally | reject |
| infer a diagonal Nyman family from unquantified iterated limits | reject |
| infer a universal theorem from finite coefficients, Gram blocks, or zeros | reject |

## Required formal theorem map

| source contract | required formal endpoint |
|---|---|
| Li | `_root_.RiemannHypothesis <-> for every n : ℕ, 1 <= n -> 0 <= re(liCoeff n)` |
| Weil | `for every n : ℤ, weilNormSq (G n) = 2 * re(liCoeff n)` |
| Bombieri | `_root_.RiemannHypothesis <-> for every BombieriAdmissible g, bombieriQ g <= 0` |
| regularized bridge | `for every n : ℤ, arithmeticWeil n = 2 * re(liCoeff n)` |
| Nyman | `_root_.RiemannHypothesis <-> chi is in closure(B_nat)` |

All names above are proposed interfaces, not declarations claimed to exist.

## Package acceptance checklist

- source version and locator pinned;
- variables, domains, measures, and scalar fields explicit;
- exceptional points explicit;
- multiplicity preserved;
- cutoff shape and boundary convention explicit;
- conditional and absolute convergence distinguished;
- transform exponent and normalization explicit;
- sign and conjugation conventions replayed independently;
- every RH-dependent lemma tagged;
- target maps to `_root_.RiemannHypothesis`;
- research bounds separated from source equivalences;
- no finite computation presented as universal evidence.
