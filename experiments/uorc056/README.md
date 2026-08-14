# UORC-056 execution package 001

This directory implements milestones 01-22 of the frozen UORC-056
specification. It provides exact oriented-root ground truth, bounded circuit
synthesis, strict multi-curve transfer gates, exact divisor-aware screens and a
Fourier-to-divisor lower-bound reduction. It does not construct a fast
unknown-scalar evaluator and does not claim an ECDLP improvement.

The central target is unchanged:

```text
A(E,G,Q) = Y_G(x(Q))/y(Q) = (-1)^k,
Q = [k]G,
```

with every preprocessing, advice, representation, memory and online cost
charged.

## Canonical convention

For `H=<G>` of odd prime order `n`, let

```text
K_H(X) = product_{j=1}^{(n-1)/2} (X - x([j]G)).
```

The canonical oriented root is the unique polynomial of degree below
`(n-1)/2` such that

```text
Y_G(x([j]G)) = (-1)^j y([j]G).
```

Consequently

```text
Y_G(X)^2 = X^3 + aX + b mod K_H(X),
Y_G(x([k]G))/y([k]G) = (-1)^k,
Y_{-G} = -Y_G.
```

The last identity fixes the sign convention. In particular,
`Y_G(x(G))=-y(G)`. Combining `Y_G(x(G))=y(G)` with output `(-1)^k`
would mix opposite global-sign conventions.

## Exact ground truth

The factory uses the five frozen prime-order curves already present in
PARITY-LIFT-000. All have equation `y^2=x^3+7`.

| ID | Field | Generator | Prime order | Kernel degree |
|---|---:|---|---:|---:|
| `E7-P43-N31` | 43 | `(2,12)` | 31 | 15 |
| `E7-P67-N79` | 67 | `(2,22)` | 79 | 39 |
| `E7-P79-N67` | 79 | `(1,18)` | 67 | 33 |
| `E7-P127-N127` | 127 | `(1,32)` | 127 | 63 |
| `E7-P163-N139` | 163 | `(2,34)` | 139 | 69 |

For every nonzero marked generator `[u]G`, the factory constructs the exact
oriented root and verifies the square congruence, full parity ratio and
generator negation. This gives 438 checked roots. SymPy independently replays
all group arithmetic, kernels, roots and ratios. A SageMath 10.9 replay is also
supplied.

## Profile 1: finite affine-character synthesis

`circuit_grammar.json` and `uorc056_circuit_synth.py` search products of at most
four characters of projectively normalized affine forms

```text
chi(a*x(Q)+b*y(Q)+c).
```

On the smallest curve the synthesizer exactly rediscovers the minimum
weight-four finite identity

```text
chi(x+17) * chi(x+y+41) * chi(x+42*y+41) * chi(y).
```

The unchanged integer formula is undefined on the full nonzero orbit of each
of the other four curves. It is classified as a finite non-transfer seed, not
a uniform evaluator.

## Profile 2: structural small-multiple and GLV transfer

`structural_transfer_grammar.json` admits public coordinates

```text
x([u]Q), y([u]Q),  u in {1,2,3,4},
```

both canonical roots `beta_lo,beta_hi` of `z^2+z+1`, public generator-derived
coefficients, cross-source affine combinations, public phase characters and a
uniform output negation. Every group operation, coefficient construction,
quadratic character and sign multiplication is charged. Per-curve fitting,
per-curve output phases, target-indexed tables and GLV eigenvalues obtained by
discrete log are forbidden.

The exact screen generated 8,174 symbolic templates. On the five discovery
curves and all 438 nonzero points, 723 templates were defined everywhere and
collapsed to 605 semantic sign vectors. No product of at most four vectors
equalled canonical parity. The best one-factor and two-factor matches were
250/438 and 272/438.

The corpus was extended by thirteen disjoint prime-order toy curves. The full
gate covers 18 curves and 7,434 nonzero points. Only 163 templates remained
defined everywhere, giving 129 semantic vectors, and again no exact product of
weight at most four existed.

## Profiles V1-V4: divisor-aware local regularization

Ordinary atoms reject a formula whenever an individual factor vanishes. The
divisor-aware profiles instead compute local orders and exact leading
coefficients, admit only symbolic cancellation with equal orders and evaluate
the regularized value. No exceptional point is omitted or patched.

| Profile | Atom family | Discovery vectors | Full vectors | Exact circuit, weight <=4 |
|---|---|---:|---:|---|
| V1 | `L_num(Q)/L_den(Q)` | 103 | 21 | none |
| V2 | `L_num([u]Q)/L_den([u]Q)`, `u=1..4` | 406 | 78 | none |
| V3 | `L_num([u]Q)/L_den([v]Q)`, `u,v=1..4` | 1,693 | 354 | none |
| V4 | `(L1L2)(Q)/(L3L4)(Q)` with aggregate cancellation | 1,186 | 32 | none |

V1 closes ratios of declared affine lines. V2 closes common-multiplier
pullbacks. V3 closes mixed small-multiplier pullbacks. V4 adds aggregate
cross-factor cancellation between products of two unpulled lines, so it covers
reducible-conic numerator and denominator functions that cannot necessarily be
factored into individually admissible V1 atoms.

The V4 grammar contains 64,980 unordered line products. On the five discovery
curves it produces 31,375 valuation signatures, 48,204 semantic product
profiles, 104,855 admissible balanced ratios and 1,186 sign vectors. The exact
meet-in-the-middle search finds no parity circuit through character-product
weight four. On the full 18-curve corpus, the catalog collapses to 32 sign
vectors and again has no exact candidate.

## V5: global divisor balance for pulled lines

`UORC-056-GLOBAL-DIVISOR-BALANCE-V5` permits zeros and poles to cancel across
all four factors at once:

```text
chi((L1([u1]Q) * L2([u2]Q)) /
    (L3([u3]Q) * L4([u4]Q))).
```

It does not require either numerator-denominator pair to be individually
regular. The only admission rule is exact aggregate valuation equality at every
tested subgroup point.

The frozen discovery screen contains:

- 1,440 raw pulled-line templates;
- 1,280 unique exact local semantics;
- 819,840 unordered template pairs;
- 482,621 aggregate divisor signatures;
- 769,563 unique pair semantic states;
- 50,277 repeated states.

No exact two-numerator, two-denominator parity circuit exists in this declared
family. The best balanced one-by-one character matches 256/438 points.

This is strictly stronger than V4 with respect to small independent pullbacks,
but it remains a bounded four-line result.

## V6: small public Miller divisor circuits

`UORC-056-SMALL-MILLER-DIVISOR-BALANCE-V6` searches products and inverses of
canonical public Miller primitives

```text
g_(a,b)([u]Q)
 = ell_([a]G,[b]G)([u]Q) / v_([a+b]G)([u]Q),
```

with `a,b` in `{-4,-3,-2,-1,1,2,3,4}`, `a+b != 0`, pullbacks
`u in {1,2,3,4}`, exponents `+1,-1`, at most four primitive factors and one
fixed symbolic public phase.

The exact quotient contains:

- 128 Miller primitives;
- 256 signed semantic atoms;
- 33,152 enumerated pair states;
- 31,749 unique pair semantic states;
- 22,803 valuation buckets;
- 8 public phase vectors.

No aggregate-divisor-balanced parity circuit exists through four primitives.
The best regular result through two factors matches 237/438 points.

This closes only bounded small public Miller products. It does not close long
addition chains, index-growing Miller functions or compact global
normalization.

## V7: Fourier-to-divisor barrier

V7 replaces another finite coefficient sweep with a theorem-level route.
For odd `n`, define canonical parity on the nonidentity points by

```text
sigma([k]G)=(-1)^k,  1 <= k < n.
```

For `z^n=1`, `z!=1`, the exact nonidentity Fourier coefficient is

```text
sum_{k=1}^{n-1} (-1)^k z^k = (1-z)/(1+z).
```

At frequency

```text
r_star=(n-1)/2,
```

its magnitude is exactly

```text
cot(pi/(2n)) ~ (2/pi)n.
```

Thus parity has one nontrivial Fourier coefficient of linear size in `n`.
This elementary identity is complete and replayed on all five frozen orders.

### FDB-1 proof obligation

Let `R` be a rational function on the elliptic curve and let `s(R)` be the
number of geometric points where `ord_P(R)` is odd. V7 isolates the exact
hybrid trace theorem needed next:

```text
|sum_{P in E(F_p)} eta(P) Trace(Kummer(R))_P|
  <= C_sh * s(R) * sqrt(p).
```

Here `eta` is the nontrivial Lang character at the parity peak frequency. If
FDB-1 holds with the stated conductor normalization, divisor-aware
regularization changes at most `s(R)+1` terms, so every exact rational-character
parity evaluator satisfies

```text
s(R) >= (cot(pi/(2n))-1)/(C_sh*sqrt(p)+1).
```

For secp256k1, whose rational point group has cofactor one, the conditional
lower bounds are:

| `C_sh` | required odd geometric divisor support |
|---:|---:|
| 1 | 216630482969909636093804454941121895872 |
| 2 | 108315241484954818046902227470560947936 |
| 4 | 54157620742477409023451113735280473968 |
| 8 | 27078810371238704511725556867640236984 |

The Fourier reduction and numerical specialization are complete. FDB-1 is not
yet promoted to a verified theorem. The remaining checks are the Lang-sheaf
trace normalization, geometric nontriviality after tensoring with the quadratic
Kummer factor, even-divisor and unramified cases, middle-extension traces at
ramification points and the exact Grothendieck-Ogg-Shafarevich conductor
constant.

Even after FDB-1, this is a divisor-support lower bound, not a general
arithmetic-circuit lower bound. A short nonlinear circuit can define a
high-degree function with large divisor support.

## Files

- `uorc056_contract.json`: frozen target, covariance, all-in cost and forbidden advice.
- `closed_classes.json`: scoped no-go and normal-form registry.
- `execution_status.json`: machine-readable milestone state and next frontier.
- `expected_fixture_manifest.json`: deterministic fixture hashes.
- `circuit_grammar.json`, `circuit_synth_results.json`: finite affine profile.
- `structural_transfer_grammar.json`, `structural_transfer_results.json`: structural transfer profile.
- `divisor_aware_rational_*`: V1 exact line-ratio screen.
- `divisor_aware_pullback_*`: V2 common-pullback screen.
- `divisor_aware_mixed_pullback_*`: V3 mixed-pullback screen.
- `divisor_aware_balanced_product_*`: V4 unpulled balanced products.
- `global_divisor_balance_*`: V5 independently pulled global balance.
- `small_miller_balance_*`: V6 small Miller divisor circuits.
- `fourier_divisor_barrier_*`: V7 exact spectrum and conditional support reduction.
- `../../scripts/uorc056_divisor_common.py`: shared exact local divisor arithmetic.
- `../../scripts/uorc056_toy_factory.py`: exact root producer and checker.
- `../../scripts/uorc056_sympy_replay.py`: independent polynomial and group replay.
- `../../notes/reviews/UORC056_FOURIER_DIVISOR_BARRIER_V7.md`: theorem statement and proof obligations.
- `sage/uorc056_replay.sage`: optional Sage replay.
- `environment/environment.yml`: pinned SageMath discovery environment.

## Reproduce

From the repository root:

```bash
rm -rf /tmp/uorc056-fixtures
python3 scripts/uorc056_toy_factory.py --output-dir /tmp/uorc056-fixtures
python3 scripts/uorc056_toy_factory.py --output-dir /tmp/uorc056-fixtures --check
cmp /tmp/uorc056-fixtures/manifest.json experiments/uorc056/expected_fixture_manifest.json

PYTHONPATH=scripts python3 -m unittest -v \
  scripts/test_uorc056_toy_factory.py \
  scripts/test_uorc056_circuit_synth.py \
  scripts/test_uorc056_structural_transfer.py \
  scripts/test_uorc056_divisor_aware_rational.py \
  scripts/test_uorc056_divisor_aware_pullback.py \
  scripts/test_uorc056_divisor_aware_mixed_pullback.py \
  scripts/test_uorc056_divisor_aware_balanced_product.py \
  scripts/test_uorc056_global_divisor_balance.py \
  scripts/test_uorc056_small_miller_balance.py \
  scripts/test_uorc056_fourier_divisor_barrier.py

python3 scripts/uorc056_sympy_replay.py /tmp/uorc056-fixtures
python3 scripts/uorc056_circuit_synth.py --check
python3 scripts/uorc056_structural_transfer.py --check
python3 scripts/uorc056_divisor_aware_rational.py --check
python3 scripts/uorc056_divisor_aware_pullback.py --check
python3 scripts/uorc056_divisor_aware_mixed_pullback.py --check
python3 scripts/uorc056_divisor_aware_balanced_product.py --check
python3 scripts/uorc056_global_divisor_balance.py --check
python3 scripts/uorc056_small_miller_balance.py --check
python3 scripts/uorc056_fourier_divisor_barrier.py --check
```

Optional Sage replay:

```bash
mamba env create -f experiments/uorc056/environment/environment.yml
mamba activate uorc056-sage
python3 scripts/uorc056_toy_factory.py --output-dir experiments/uorc056/fixtures
sage experiments/uorc056/sage/uorc056_replay.sage
```

Generated fixture bodies are uploaded by CI rather than committed. Their
canonical SHA-256 manifest remains in Git.

## Current frontier

The primary task is no longer another bounded rational grammar. It is FDB-1:
source-lock and prove or refute the elliptic Kummer-Lang hybrid trace bound with
an exact conductor constant and exact treatment of divisor-aware values.

If FDB-1 is established, every exact rational-character mechanism with
`o(sqrt(n))` odd divisor support is closed at once. Constructive attention then
moves to the genuinely surviving classes:

1. high-degree, low-size straight-line programs;
2. direct field-valued evaluation of `Y_G(x(Q))/y(Q)` without an outer
   quadratic character;
3. transposed or modular-composition representations that do not materialize
   the divisor;
4. level-`n` theta, elliptic-unit or CM reciprocity formulas with compact
   evaluation;
5. index-growing EDS or Miller constructions with compact distinguished global
   normalization.

## Scientific boundary

Finite interpolation materializes the answer with linear representation cost.
The present fixtures and bounded screens are instrumentation for circuit
archaeology and lower-bound discovery. V7 proves an exact spectral reduction
and isolates one explicit sheaf-theoretic theorem. It does not yet provide a
general circuit lower bound, a parity evaluator or a sub-square-root ECDLP
algorithm.
