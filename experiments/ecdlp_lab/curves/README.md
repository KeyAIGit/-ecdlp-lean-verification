# ECDLP lab curve catalogs

This package owns deterministic synthetic curve fixtures only. It does not
accept arbitrary curves, external targets, secp256k1-sized groups, scientific
hypotheses, or Research Engine records.

`p1_adapter.py` projects the immutable 40-curve legacy P1 catalog only after a
repository registry supplies and verifies its exact raw digest. The legacy
file contains observational timing data, so the adapter authenticates its raw
bytes first, parses duplicate and non-finite values safely, and drops all
observational fields from the projected model.

`generate_ci_catalog.py` owns three counters per fixture. Prime candidates,
curve candidates, and point attempts are global within that fixture and never
reset in a nested loop. Their fixed ceilings are 4096, 4096, and 1024. The
generator deliberately does not import the legacy `search_curve` or
`deterministic_point` routines.

The committed catalog contains exactly the Cartesian product of 11/13 field
bits and these three families:

- `j0_glv_like`, with independently checkable beta/lambda;
- `random_generic_j_prime_subgroup`, with `j` outside 0 and 1728;
- `j0_no_fp_glv_control`, whose claim is limited to the absence of a
  nontrivial cube root in the base field.

The catalog excludes wall time, platform, source commit, and dirty-tree state.
Its raw digest and the raw spec digest are bound by
`fixtures/curves/catalog_registry_v1.json`. Regeneration is read-only:

```bash
python3 -m experiments.ecdlp_lab.curves.generate_ci_catalog --check
```

`validate_catalog.py` is the independent arithmetic path. It imports
`experiments.framework.ec_oracle`, never the P1 producer arithmetic or the lab
generator. Every fixture first passes prime-field, nonsingularity, canonical
coordinate, prime-subgroup, point-order, cofactor-product, and Hasse checks.
The certificate dispatcher then applies exactly one of:

- `prime_order_hasse_unique_v1`, with cofactor one and Hasse uniqueness;
- `exact_legendre_sum_v1`, restricted to registry-authorized CI fields of at
  most 16 bits;
- `j0_p_plus_one_v1`, with `p mod 3 = 2` and an additional exact CI count.

The same oracle validates the 40 frozen legacy curves through prime-order
Hasse uniqueness and their endomorphism eigenpair relations. It never exact-counts the legacy
20/24-bit fields. The full fail-closed registry, generation fixpoint, six CI
fixtures, and 40 legacy fixtures are replayed by:

```bash
python3 -m experiments.ecdlp_lab.core.validate --offline
```
