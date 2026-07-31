# PKC nonsplit-torus desk screen

This directory independently audits the arithmetic and mechanism boundary in
draft PR #270, `HYP-TORUS-001`. It is a deterministic desk calculation, not a
solver run or experiment authorization.

## Result

The norm-one torus over `F_p` has order `p+1`, and inversion identifies
`alpha` with `alpha^-1` under the trace coordinate

```text
t(alpha) = alpha + alpha^-1.
```

For a cyclic subgroup `H`, the number of distinct trace coordinates is

```text
(|H| + gcd(|H|, 2)) / 2.
```

That structural observation survives, but it is not new: Yokota, Kudo and
Yasuda already published the `p+1` root-of-unity trace construction at WCC
2017. Their low-degree experimental form uses `N=2^r` and `m=2`. The submitted
attack candidate does not supply a source-checked extension. Its `m=6,7` rows use

```text
|H| = 45422601869677,
```

which is itself a 46-bit prime. In the exact factor-chain construction of
Petit, Kosters and Messeng, every prime factor becomes the degree of one local
map. The claimed factor chain therefore contains a degree-45422601869677 step;
the memo did not supply or price a low-degree replacement.

The submitted arity table is also not exhaustive. Exact enumeration of all 20
divisors formed from `2^4`, `7322137`, and `45422601869677`, using the memo's
own yield predicate and a conservative exact linear-algebra cap, retains
arities `6..20`, not only `6,7`. All retained rows require either the 46-bit or
23-bit prime-degree step.

## Important boundary

The Dickson identity

```text
D_d(alpha + alpha^-1, 1) = alpha^d + alpha^-d
```

does provide a compact mathematical description of the trace root set. But
`D_d(x,1)-2` has degree `d` and only
`(d+gcd(d,2))/2` distinct roots; the interior roots are repeated. A faithful
low-degree radical presentation, saturation rules, inverse recovery and a full
cost bridge are still missing.

Accordingly:

- the submitted candidate is `rejected_missing_exact_low_degree_mechanism`;
- its claim that the size leg was cleared is retracted;
- the broader arity-specific application is known prior art with an
  `inconclusive` large-prime extension, and remains non-executable;
- `R-PETIT-COMPOSED-MAPS` remains `open_parked`;
- no experiment or route promotion is authorized.

This does not claim that all future torus-based mechanisms are impossible and
does not claim novelty.

## Reproduce

```bash
python3 experiments/engine/pkc_nonsplit_torus_desk_screen/generate.py --check
python3 experiments/engine/pkc_nonsplit_torus_desk_screen/validate.py
python3 experiments/engine/pkc_nonsplit_torus_desk_screen/test_validate.py
python3 -m py_compile \
  experiments/engine/pkc_nonsplit_torus_desk_screen/generate.py \
  experiments/engine/pkc_nonsplit_torus_desk_screen/validate.py \
  experiments/engine/pkc_nonsplit_torus_desk_screen/test_validate.py
```

The validator imports neither the producer nor its functions. It uses a
different integer-root implementation, independently enumerates the divisors,
recomputes the trace cardinalities and decisive dispositions, and verifies the
artifact digest. The mutation suite checks eight load-bearing fields.

## Primary source

The source contract is Petit, Kosters and Messeng, *Algebraic Approaches for
the Elliptic Curve Discrete Logarithm Problem over Prime Fields*, PKC 2016,
Sections 3.1-3.3. The paper requires a large root set and a composition of
small-degree maps; in its direct `p-1` construction, the subgroup-order prime
factors are precisely the local map degrees.

The direct prior-art anchor is Yokota, Kudo and Yasuda, *A Practical Limit of
the Algebraic Approach for ECDLP over Prime Fields*, WCC 2017, Section 4.1,
equations (9)-(10), Section 4.2 and Section 5. The full-text claim extract is
`data/source_claim_extracts/yokota_kudo_yasuda2017_wcc.json`.
