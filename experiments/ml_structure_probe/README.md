# ML structure probe P0

This package qualifies a route-neutral machine-learning measurement layer for
KeyAI.  It does not attempt to recover a real key and it does not register a
cryptanalytic result.  P0 answers four engineering questions:

1. Can the repository generate and independently replay one million uniformly
   sampled synthetic secp256k1 `(d, Q=[d]G)` pairs?
2. Can a streaming baseline distinguish deliberate canaries from a permutation
   null without loading the full dataset into memory?
3. Can every apparent scalar signal be retained as an untrusted observation,
   rather than silently promoted to an ECDLP hypothesis?
4. Can a bounded AutoML controller compare model and representation families
   without adaptively reusing the final test split?

The package sits before the existing hypothesis and candidate gates:

```text
synthetic pairs + nulls + canaries
    -> preregistered representation probe
    -> replicated signal, or bounded null
    -> explicit algebraic/program hypothesis
    -> typed cell + adversarial proposal review
    -> immutable candidate + independent validator
    -> toy scaling
    -> only then any target-specific decision
```

## Scientific prior

Plain supervised inversion is not the favored route.  Takhanov et al.,
*Intractability of Learning the Discrete Logarithm with Gradient-Based
Methods*, prove a gradient-concentration result for learning discrete-log
parity over prime-order cyclic groups and report worsening empirical learning
as the group size grows.  The theorem is about a class indexed by the base and
does not by itself prove that every fixed-base, representation-aware secp256k1
model must fail.  It is still a strong reason to treat gradient-based
`public-key -> secret-bit` regression as a diagnostic baseline, not the main
discovery engine.

The main discovery route planned after P0 is verifier-guided program search:
models propose short programs in a typed DSL of field operations, group
operations, endomorphisms, relations, and bounded memory.  Candidate programs
are executed on held-out curves, compared with generic baselines, minimized,
and translated into explicit mathematical hypotheses.  Gradient-free search,
symbolic regression, evolutionary search, and language-model program proposal
are all eligible.  The verifier, not the model, controls acceptance.

## Budgeted AutoML controller

`automl.py` implements successive halving rather than an unrestricted
hyperparameter search.  It:

- screens every configured recipe on a small train/validation budget;
- preserves model-family diversity through the first cut;
- confirms survivors on successively larger budgets;
- selects recipes using validation information gain;
- evaluates exactly one selected model per scientific task on test;
- runs fixed positive and negative controls separately;
- appends every success, failure, warning, parameter set, metric, record budget,
  and timing to a JSONL ledger;
- emits a machine-readable result and a Markdown report.

The one-million configuration covers 21 recipes from six estimator families:
averaged logistic SGD, Bernoulli naive Bayes, extremely randomized trees,
histogram gradient boosting, shallow multilayer perceptrons, and random Fourier
features followed by logistic SGD.  It compares compressed bits, normalized
bytes, 16-bit x-coordinate limbs, and per-byte popcounts.  Expensive nonlinear
recipes have explicit training caps, which are recorded in the ledger.

The controller learns better parameters only from validation.  It does not
keep launching recipes after observing test.  Otherwise the test set would
become another training set and the reported result would be optimistically
biased.

## Is one million pairs enough?

It is enough for:

- a reproducible throughput and storage qualification;
- gross distribution, duplicate, and split-isolation checks;
- streaming linear and shallow nonlinear screens;
- detecting a balanced binary accuracy difference on the order of a few
  tenths of a percentage point on a 200,000-record held-out split;
- proving that canaries and permutation nulls behave as expected.

It is not enough to:

- cover a meaningful fraction of the roughly `2^256` key space;
- establish that no learnable structure exists;
- justify an extrapolation from one curve, one representation, or one model;
- turn a positive classifier into a discrete-log algorithm;
- distinguish a genuine asymptotic mechanism from a fixed-size artifact.

The million records are split before generation:

| split | records | role |
|---|---:|---|
| train | 600,000 | model fitting only |
| validation | 200,000 | preregistered replication |
| test | 200,000 | final untouched replication |

Every split has a separate derivation domain.  Random pair-level reshuffling is
not used as the trust boundary.

## Data contract

Each fixed-width record is 65 bytes:

```text
scalar d:               32 bytes, big endian
compressed Q = [d]G:    33 bytes, SEC 1 form
```

Scalars are deterministic synthetic rejection samples in `[1,n-1]` from
domain-separated SHA-256.  They never come from wallets.  Public points are
produced by OpenSSL through `cryptography`.

The committed configuration contains the synthetic seed so any reviewer can
reproduce the bytes.  Raw shards live under ignored `artifacts/`.  The manifest
records every shard hash, code hash, configuration hash, Git state, runtime,
OpenSSL version, throughput, and a dataset-root hash.

`validate_dataset.py` does not import the producer.  It checks all shard hashes,
all scalar ranges, all duplicates, split counts, gross bit and residue
distributions, and thousands of deterministic spot records.  Spot public keys
are recomputed with separate pure-Python Jacobian arithmetic.  This establishes
path and artifact replay for data engineering.  It is not source-independent
scientific validation.

## P0 model

The baseline is deliberately simple:

- input: 264 bits of the compressed public point;
- learner: streaming logistic `SGDClassifier`;
- optimizer: averaged constant-step SGD (`eta0 = 0.01`) with explicit
  finite-probability checks;
- memory: bounded by batch size;
- secret targets: `d mod 2`, scalar bit 127, and `d mod 3`;
- positive controls: public-point parity and a deliberately appended scalar-bit
  leak;
- negative control: deterministic labels independent of the point;
- primary metric: held-out cross-entropy gain in bits per record;
- secondary metrics: accuracy lift and standardized accuracy lift.

A signal flag requires all three preregistered thresholds on both validation
and test:

```text
information gain >= 0.01 bit / record
accuracy lift    >= 0.002
accuracy z       >= 6
```

Crossing the threshold does not authorize a new experiment.  It creates only
an observation requiring a second implementation, new curve and generator
splits, symbolic extraction, and the normal Research Engine candidate gates.

## Full ML program

### Phase 0: engineering qualification

Implemented here:

- deterministic one-million-pair generation;
- independent-path arithmetic replay;
- duplicate and distribution checks;
- canary, permutation-null, and linear scalar probes.

Exit: the pipeline passes even if every scientific target is null.

### Phase 1: toy-curve scaling ladder

Use multiple prime-order curves and generators at 12, 16, 20, 24, 28, and 32
bits.  Hold out complete curves and complete generators.  Include:

- affine coordinates and compressed encodings;
- random opaque relabeling as the generic-group control;
- weak-generator and injected-coordinate canaries;
- direct scalar bits and residues;
- relational triples `(P,Q,P+Q)`;
- algorithm traces from BSGS, Pollard rho, and GLV-accelerated rho.

Exit: measure whether a signal is representation-specific, generator-specific,
or merely memorization.  No secp256k1 inference is allowed.

### Phase 2: model families

Run models in increasing scientific cost:

1. linear and regularized generalized-linear probes;
2. tree and shallow MLP probes;
3. byte/limb mixers with modular arithmetic features;
4. group-relation contrastive models;
5. typed program synthesis over field and group operations;
6. gradient-free evolutionary and Monte Carlo program search;
7. language-model proposal of programs, with zero trust in generated claims.

The program-synthesis lane is more important than making a larger direct
regressor.  Its output is an explicit executable candidate rather than a weight
matrix with unexplained accuracy.

### Phase 3: mechanism extraction

For every replicated signal:

- identify the smallest input feature set that preserves it;
- fit symbolic expressions or extract a short DSL program;
- test invariance under generator changes and coordinate randomization;
- enumerate exceptional loci;
- state recovery semantics and all preprocessing;
- compare actual group operations and memory with BSGS and Pollard rho.

Exit: either a concrete mechanism proposal enters the Research Engine, or the
signal is retained as artifact, leakage, memorization, or inconclusive.

### Phase 4: scaling decision

Fit cost against curve bit length only after the mechanism is explicit.  A
possible asymptotic candidate must survive fresh curves and show a stable law
better than generic square-root work.  A fixed-size accuracy improvement, a
constant factor, or an information-gain signal is not an ECDLP shortcut.

### Phase 5: exact-curve representation assay

Only after Phases 1 through 4 pass:

- generate fresh synthetic secp256k1 pairs after model and thresholds freeze;
- run the exact extracted mechanism, not an open-ended hyperparameter search;
- retain preprocessing, inference cost, memory, success probability, and every
  negative outcome;
- require a new dated owner decision for any work that goes beyond a
  representation assay.

## Reproduce P0

Install only the experiment dependencies:

```text
python -m pip install -r experiments/ml_structure_probe/requirements.txt
```

Smoke test:

```text
cd experiments/ml_structure_probe
python test_probe.py
```

One-million-pair data and probe:

```text
cd experiments/ml_structure_probe
python generate_dataset.py \
  --config config/p0_million.json \
  --output-dir artifacts/p0_million
python validate_dataset.py \
  --config config/p0_million.json \
  --manifest artifacts/p0_million/dataset_manifest.json \
  --output runs/p0_million_validation.json
python probe.py \
  --config config/p0_million.json \
  --manifest artifacts/p0_million/dataset_manifest.json \
  --output runs/p0_million_probe.json
python automl.py \
  --config config/automl_million.json \
  --manifest artifacts/p0_million/dataset_manifest.json \
  --output-dir runs/p0_million_automl
```

The raw dataset and model outputs are ignored by Git.  A clean source commit
must be used before retaining a compact AutoML ledger, JSON result, and
Markdown report in a later evidence PR.  Model binaries and raw pairs remain
regenerable and are not committed.

## Exact scope

P0 is a route-neutral engineering foundation.  It does not:

- solve or attempt to solve a real wallet key;
- estimate secp256k1 recovery complexity;
- authorize a cryptanalytic hypothesis;
- enter native Research Engine calibration;
- promote any route;
- weaken the generic-group guardrail;
- treat model accuracy as mathematical evidence.
