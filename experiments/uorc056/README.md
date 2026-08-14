# UORC-056 execution package 001

This directory implements Tasks 01-08 of the frozen UORC-056 technical
specification. It builds exact ground truth for the marked-generator oriented
Kummer root on small odd prime-order subgroups. It does not construct a fast
unknown-scalar evaluator and does not claim an ECDLP improvement.

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
`Y_G(x(G))=-y(G)`. Any document that combines `Y_G(x(G))=y(G)` with output
`(-1)^k` is using two opposite global-sign conventions at once.

## Files

- `uorc056_contract.json`: frozen target, covariance, all-in cost and forbidden advice.
- `closed_classes.json`: scoped no-go and normal-form registry from PRs 365, 383, 384 and 385.
- `expected_fixture_manifest.json`: locked hashes for all generated fixtures.
- `../../scripts/uorc056_toy_factory.py`: dependency-free producer and exact checker.
- `../../scripts/uorc056_sympy_replay.py`: independent SymPy replay.
- `sage/uorc056_replay.sage`: independent Sage replay, including EC group arithmetic.
- `environment/environment.yml`: optional pinned SageMath discovery environment.

## Reproduce

From the repository root:

```bash
rm -rf /tmp/uorc056-fixtures
python3 scripts/uorc056_toy_factory.py --output-dir /tmp/uorc056-fixtures
python3 scripts/uorc056_toy_factory.py --output-dir /tmp/uorc056-fixtures --check
cmp /tmp/uorc056-fixtures/manifest.json experiments/uorc056/expected_fixture_manifest.json
PYTHONPATH=scripts python3 -m unittest scripts/test_uorc056_toy_factory.py
python3 scripts/uorc056_sympy_replay.py /tmp/uorc056-fixtures
```

Optional Sage replay:

```bash
mamba env create -f experiments/uorc056/environment/environment.yml
mamba activate uorc056-sage
python3 scripts/uorc056_toy_factory.py --output-dir experiments/uorc056/fixtures
sage experiments/uorc056/sage/uorc056_replay.sage
```

SageMath is not vendored into Git. The environment specification is small; the
large CAS packages are installed only on a runner or research machine. The
required second-backend gate is SymPy, while Sage is a stronger optional replay.
Generated fixture bodies are uploaded by CI as an artifact rather than committed;
their deterministic SHA-256 manifest is committed.

## Frozen toy family

The fixture set is exactly the five frozen prime-order curves already used by
`experiments/parity_lift_000/char_parity_toy_screen.py`. All use the fixed
secp256k1-shaped equation `y^2=x^3+7`.

| ID | Field | Generator | Prime order | Kernel degree |
|---|---:|---|---:|---:|
| `E7-P43-N31` | 43 | `(2,12)` | 31 | 15 |
| `E7-P67-N79` | 67 | `(2,22)` | 79 | 39 |
| `E7-P79-N67` | 79 | `(1,18)` | 67 | 33 |
| `E7-P127-N127` | 127 | `(1,32)` | 127 | 63 |
| `E7-P163-N139` | 163 | `(2,34)` | 139 | 69 |

Each fixture records a checked nontrivial cube root `beta` and the matching GLV
eigenvalue `lambda` on the declared generator. The factory exports all `n-1`
marked-generator roots, not only `G` and `-G`.

## Scientific boundary

Finite interpolation materializes the answer and costs linear space in the
kernel degree. These fixtures are therefore an oracle for circuit archaeology,
not a candidate circuit. The next authorized engineering step is to define the
first exact circuit grammar and search only the smallest fixtures, while charging
all constants, tables, advice and representation construction.
