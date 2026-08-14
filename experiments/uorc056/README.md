# UORC-056 execution package 001

This directory implements execution milestones 01-15 of the frozen UORC-056
specification. It provides exact oriented-root ground truth, two bounded circuit
synthesis profiles, strict transfer gates and reproducible negative results. It
does not construct a fast unknown-scalar evaluator and does not claim an ECDLP
improvement.

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
would mix two opposite global-sign conventions.

## Exact ground truth

The factory uses exactly the five frozen prime-order curves already present in
PARITY-LIFT-000. All have equation `y^2=x^3+7`.

| ID | Field | Generator | Prime order | Kernel degree |
|---|---:|---|---:|---:|
| `E7-P43-N31` | 43 | `(2,12)` | 31 | 15 |
| `E7-P67-N79` | 67 | `(2,22)` | 79 | 39 |
| `E7-P79-N67` | 79 | `(1,18)` | 67 | 33 |
| `E7-P127-N127` | 127 | `(1,32)` | 127 | 63 |
| `E7-P163-N139` | 163 | `(2,34)` | 139 | 69 |

For every nonzero marked generator `[u]G`, the factory constructs the exact
oriented root and verifies the square congruence, the full parity ratio and
generator negation. This gives 438 checked roots. SymPy independently replays
all group arithmetic, kernels, roots and ratios. A SageMath 10.9 replay is also
supplied.

## Circuit profile 1: finite affine-character synthesis

`circuit_grammar.json` and `uorc056_circuit_synth.py` search products of at most
four characters of projectively normalized affine forms

```text
chi(a*x(Q)+b*y(Q)+c).
```

On the smallest curve the synthesizer exactly rediscovers the known minimum
weight-four finite identity

```text
chi(x+17) * chi(x+y+41) * chi(x+42*y+41) * chi(y).
```

The unchanged integer formula is undefined on the full nonzero orbit of each
of the other four curves. It is therefore classified as a finite non-transfer
seed, not a uniform evaluator.

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
curves and all 438 nonzero points:

- 723 templates were defined everywhere;
- they collapsed to 605 distinct semantic sign vectors;
- no product of at most four vectors equalled canonical parity, even up to one
  uniform output negation;
- the best one-factor candidate matched 250/438 points;
- the best two-factor candidate matched 272/438 points.

The corpus was then extended by thirteen disjoint prime-order toy curves. The
full gate covers 18 curves and 7,434 nonzero points. Only 163 templates remained
defined everywhere, giving 129 semantic vectors, and again no exact product of
weight at most four existed.

This is a complete finite negative for the declared AST grammar. It is not an
asymptotic lower bound and does not cover symbolic cancellation of exceptional
zeros, index-growing EDS constructions or unrestricted high-degree
straight-line programs.

## Files

- `uorc056_contract.json`: frozen target, covariance, all-in cost and forbidden advice.
- `closed_classes.json`: scoped no-go and normal-form registry.
- `execution_status.json`: machine-readable milestone state and next frontier.
- `expected_fixture_manifest.json`: deterministic fixture hashes.
- `circuit_grammar.json`, `circuit_synth_results.json`: first synthesis profile.
- `structural_transfer_grammar.json`, `structural_transfer_results.json`: second profile and 18-curve gate.
- `../../scripts/uorc056_toy_factory.py`: exact root producer and checker.
- `../../scripts/uorc056_sympy_replay.py`: independent polynomial and group replay.
- `../../scripts/uorc056_circuit_synth.py`: bounded finite affine synthesizer.
- `../../scripts/uorc056_structural_transfer.py`: structural multi-curve transfer screen.
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
  scripts/test_uorc056_structural_transfer.py

python3 scripts/uorc056_sympy_replay.py /tmp/uorc056-fixtures
python3 scripts/uorc056_circuit_synth.py --check
python3 scripts/uorc056_structural_transfer.py --check
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

The next useful grammar is not another larger collection of ordinary affine
atoms. It must represent rational circuits whose numerator and denominator may
vanish separately but cancel symbolically before the quadratic character is
applied. Such a profile needs divisor bookkeeping, exact regularization at
exceptional subgroup points and a charged rule for constructing the canceled
representation. Without those controls, `0/0` values would silently smuggle an
orientation table into the evaluator.

## Scientific boundary

Finite interpolation materializes the answer with linear representation cost.
The present fixtures and bounded screens are therefore instrumentation for
circuit archaeology, not a candidate sub-square-root algorithm.
