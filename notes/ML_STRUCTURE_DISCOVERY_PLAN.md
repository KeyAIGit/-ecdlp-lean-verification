# ML-guided structure discovery for ECDLP

## Decision

Machine learning should augment, not replace, explicit hypothesis testing.
Direct regression from a public point to a private scalar is retained as a
diagnostic screen.  The primary ML role is to search for representation-specific
signals and short executable mechanisms that the existing verification system
can falsify, minimize, and convert into mathematics.

The first implementation is
`experiments/ml_structure_probe/`.  Its P0 package qualifies deterministic
one-million-pair generation, independent-path replay, canaries, permutation
nulls, streaming linear probes, and validation-only adaptive AutoML.  P0 is
engineering evidence only.

## Why the hybrid is stronger

Manual hypothesis work has high interpretability and low search width.  A
learned search has high width but is vulnerable to leakage, memorization,
unstable optimization, and proxy objectives.  KeyAI can combine them:

| stage | ML contribution | verification contribution |
|---|---|---|
| signal search | scan many features, encodings, and relational tasks | nulls, canaries, split isolation |
| mechanism proposal | propose short programs and invariants | type checking, exact execution, minimization |
| scaling | prioritize promising families | fresh curves, generators, generic baselines |
| mathematical extraction | suggest expressions and lemmas | symbolic replay, counterexamples, Lean |
| retention | rank unresolved observations | immutable artifacts and scoped outcomes |

The project should never train one large model, observe above-chance bit
accuracy, and call it progress.  Progress begins when an effect survives fresh
curves and becomes an explicit mechanism with a recovery map and cost account.

## Data hierarchy

1. Nulls and canaries:
   opaque relabeling, permuted labels, weak PRNGs, injected leaks.
2. Exhaustive tiny groups:
   every scalar-point pair when the group is small enough.
3. Toy elliptic curves:
   multiple curves and generators at increasing bit lengths.
4. Relational traces:
   additions, doubles, collisions, random walks, endomorphism orbits, and
   solver traces.
5. Exact secp256k1 synthetic pairs:
   representation assay only, after model and thresholds freeze.
6. Mathematical corpus:
   definitions, known algorithms, failed mechanisms, counterexamples, and
   proof traces from this repository.

Raw pair volume is the least valuable durable asset because it can be generated
on demand.  Durable storage should favor configurations, hashes, traces,
observations, extracted mechanisms, counterexamples, and terminal decisions.

## Model hierarchy

1. Linear probes establish a calibrated null.
2. Trees and shallow MLPs test simple nonlinear coordinate effects.
3. Byte and limb mixers test representation-local effects.
4. Relation-aware models consume group-operation triples.
5. Typed program synthesis searches expressions in an auditable DSL.
6. Gradient-free search avoids relying on one optimization regime.
7. Language models propose programs and lemmas, never trusted conclusions.

The P0 AutoML implementation is intentionally limited to the first four
families plus random Fourier features.  It uses successive halving so failed or
weak parameterizations lose compute after a small validation-only screen.
Exactly one selected model per scalar task is exposed to test.  This makes the
search repeatable and prevents an endless test-guided tuning loop.  Its JSONL
ledger can be committed without committing raw pairs or model binaries.

The typed DSL should begin with:

- field add, subtract, multiply, inverse, power, and equality;
- point add, negate, double, scalar multiply by public constants;
- coordinate extraction and compression parity;
- the proved GLV map and public constants;
- bounded tables, hashes, branches, and collision tests;
- cost counters for field operations, group operations, memory, and
  preprocessing.

Every generated program must have an explicit input and output type, terminate
under a fixed budget, and run under the candidate-neutral evaluator.

## Promotion standard

An ML observation can become a research proposal only when it states:

- the exact representation-specific information it exploits;
- the task and threat model;
- fresh-curve and fresh-generator replication;
- a null model and competing explanation;
- an executable mechanism or a bounded extraction plan;
- recovery semantics;
- online and offline costs;
- an independent validator plan;
- a falsification and stop rule.

No accuracy number alone satisfies this standard.

## Next implementation after P0

Build `P1-toy-scaling` as a frozen candidate only after P0 source code is clean
and reviewed.  Its dataset should contain roughly one million records in total
across the curve-size ladder, not one million examples from one tiny curve.
The decisive comparison is:

```text
affine coordinates vs compressed bytes vs opaque random labels
```

If a model performs only on affine or compressed representations, the effect is
potentially non-generic and worth extraction.  If it performs on opaque labels
without using group-operation traces, the most likely explanation is leakage or
memorization.  If performance disappears under generator and curve holdout, it
does not support a transferable mechanism.
