# UORC-056 execution package 001

This directory implements milestones 01-19 of the frozen UORC-056
specification. It provides exact oriented-root ground truth, bounded circuit
synthesis, strict multi-curve transfer gates and four divisor-aware screens.
It does not construct a fast unknown-scalar evaluator and does not claim an
ECDLP improvement.

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

## Circuit profile 1: finite affine-character synthesis

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

## Circuit profile 2: structural small-multiple and GLV transfer

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

## Divisor-aware screens

Ordinary atoms reject a formula whenever an individual factor vanishes. The
divisor-aware profiles instead compute local orders and exact leading
coefficients, admit only symbolic cancellation with equal orders and evaluate
the regularized value. No exceptional point is omitted or patched.

| Profile | Atom family | Discovery semantic vectors | Full semantic vectors | Exact circuit, weight <=4 |
|---|---|---:|---:|---|
| V1 | `L_num(Q)/L_den(Q)` | 103 | 21 | none |
| V2 | `L_num([u]Q)/L_den([u]Q)`, `u=1..4` | 406 | 78 | none |
| V3 | `L_num([u]Q)/L_den([v]Q)`, `u,v=1..4` | 1,693 | 354 | none |
| V4 | `(L1L2)(Q)/(L3L4)(Q)` with aggregate cancellation | 1,186 | 32 | none |

V1 closes ratios of declared affine lines. V2 closes common-multiplier
pullbacks. V3 closes mixed small-multiplier pullbacks. V4 adds aggregate
cross-factor cancellation between products of two lines, so it covers
reducible-conic numerator and denominator functions that cannot necessarily be
factored into individually admissible V1 atoms.

### V4 balanced line-product result

The V4 grammar contains 64,980 unordered line products. On the five discovery
curves it produces:

- 31,375 aggregate valuation signatures;
- 48,204 semantic product profiles;
- 104,855 admissible balanced product ratios;
- 1,186 distinct sign vectors;
- 429 exceptional vectors not present in the nonexceptional catalog;
- no exact parity circuit through character-product weight four.

The exhaustive meet-in-the-middle index contains 702,705 pairs in 13,874 xor
classes. The best one-atom and two-atom candidates match 254/438 and 260/438
points.

On the full 18-curve corpus, the catalog collapses to 32 sign vectors. None of
the exceptional vectors remains novel, no exact circuit exists through weight
four and the best one-atom or two-atom result is 3,790/7,434.

This is a bounded negative for ratios of products of two declared affine lines.
It does not cover irreducible conics, pulled line products, higher-degree
functions, EDS factors or unrestricted straight-line programs.

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
- `divisor_aware_balanced_product_*`: V4 reducible-conic balanced-product screen.
- `../../scripts/uorc056_toy_factory.py`: exact root producer and checker.
- `../../scripts/uorc056_sympy_replay.py`: independent polynomial and group replay.
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
  scripts/test_uorc056_divisor_aware_balanced_product.py

python3 scripts/uorc056_sympy_replay.py /tmp/uorc056-fixtures
python3 scripts/uorc056_circuit_synth.py --check
python3 scripts/uorc056_structural_transfer.py --check
python3 scripts/uorc056_divisor_aware_rational.py --check
python3 scripts/uorc056_divisor_aware_pullback.py --check
python3 scripts/uorc056_divisor_aware_mixed_pullback.py --check
python3 scripts/uorc056_divisor_aware_balanced_product.py --check
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

## Next frontier

The experimental frontier is now one of the following structurally new
families rather than another larger affine coefficient sweep:

1. irreducible conic and general low-divisor-degree rational functions with
   exact local regularization;
2. pulled products of lines with independent small multipliers;
3. EDS or Miller-style factors whose construction cost grows uniformly with
   an index rather than with the target table;
4. a theorem-level character-sum degree barrier that converts the alternating
   parity spectrum into a lower bound on divisor degree.

The fourth route has the highest leverage because it could close every bounded
low-degree rational grammar at once instead of one template family at a time.

## Scientific boundary

Finite interpolation materializes the answer with linear representation cost.
The present fixtures and bounded screens are instrumentation for circuit
archaeology and lower-bound discovery, not a candidate sub-square-root
algorithm.
