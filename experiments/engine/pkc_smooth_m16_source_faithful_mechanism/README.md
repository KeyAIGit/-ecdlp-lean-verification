# PKC M16 source-faithful mechanism and recovery closure

This desk package binds the direct `p-1` construction in Petit, Kosters, and
Messeng (PKC 2016) to the exact secp256k1 M16 specialization.

It freezes four distinctions that are easy to lose in prose:

- the published source-factor chain is pointwise equivalent to
  `1 - x^564522 = 0`;
- an addition-chain circuit may encode the same pointwise membership predicate
  without having the same polynomial ideal or solving cost;
- Algorithm 1 prints a recovery check `sum_i P_i = O` even though its System
  (4) contains the sampled target coordinate `X`;
- the repository therefore supplies an explicit target-bound signed
  elliptic-curve check as a derived completion, not as a source quotation.

The package does not build `S17`, run a solver, estimate solving degree, or
authorize an experiment. Its terminal state is
`mechanism_specified_cost_unresolved`: the source map and relation-system input
are exact, while generalized-root solving, relation independence, rank,
recovery distribution, sparse linear algebra, and complete equal-success cost
remain unresolved.

Run:

```text
python3 experiments/engine/pkc_smooth_m16_source_faithful_mechanism/generate.py --check
python3 experiments/engine/pkc_smooth_m16_source_faithful_mechanism/validate.py
python3 experiments/engine/pkc_smooth_m16_source_faithful_mechanism/test_validate.py
sha256sum -c experiments/engine/pkc_smooth_m16_source_faithful_mechanism/artifact.sha256
```

Source independence is not established. The validator is path- and
artifact-independent from the producer, but both use the same curated primary
source extract.
