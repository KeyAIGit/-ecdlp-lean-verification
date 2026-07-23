# P1 RESULTS — Semaev S₃ *solving* for the 2-term relation step (`HYP_GLV_SEMAEV_001`)

**Measured, not asserted.** Every counted relation is re-verified by an actual `ec_add`
group computation; S₃ roots that do not lift to a real EC relation are counted separately
as spurious. Numbers below are for the sizes actually run only. **No growth fit is used to
draw any asymptotic or "advantage / no-advantage" conclusion** — the one derived column
`c = yield·p/N²` is **descriptive only** and labeled so.

- **Method:** for target `R = k·G` and each factor-base x-coordinate `x_i`, solve the
  Semaev third summation polynomial `S₃(x_i, X, x_R) = 0` (a quadratic in `X` over `F_p`,
  via Tonelli–Shanks), then confirm each root by real EC addition. `O(N)` field-solves per
  target — **not** `O(N²)` pair enumeration.
- **Curves:** corrected cofactor-1 `E_b : y² = x³ + b` from
  `experiments/p0_glv_semaev/toy_curves.py`, `find_toy_curve(bits, seed=1,
  require_cofactor_one=True)`: 16-bit `p=65539`, 20-bit `p=1048609`, 24-bit `p=16777333`
  (all cofactor 1).
- **Determinism:** `seed = 1`, `T = 2000` targets per setting. Manifest:
  `runs/HYP_GLV_SEMAEV_001_p1-semaev-solve_a7d1cbfe1597.json`.
- **Bases compared at matched effective size** `N` = distinct x-coordinates: **plain**
  (smallest-x points) vs **glv-orbit** (`N/3` seeds closed under the GLV orbit
  `{x, βx, β²x}`, one seed stored per orbit).

## Measured table

| variant | bits | p | N (distinct x) | orbits (=distinct u) | stored | T | field-solves | confirmed rel. | spurious | roots-in-base | yield/target | solves/rel | `c=y·p/N²` *(descriptive)* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| plain     | 16 | 65 539 | 48 | 48 | 48 | 2000 | 96 000 | 136 | **0** | 272 | 0.0680 | 706 | 1.93 |
| glv-orbit | 16 | 65 539 | 48 | 16 | 16 | 2000 | 96 000 | 150 | **0** | 300 | 0.0750 | 640 | 2.13 |
| plain     | 16 | 65 539 | 96 | 96 | 96 | 2000 | 192 000 | 556 | **0** | 1112 | 0.2780 | 345 | 1.98 |
| glv-orbit | 16 | 65 539 | 96 | 32 | 32 | 2000 | 192 000 | 617 | **0** | 1234 | 0.3085 | 311 | 2.19 |
| plain     | 20 | 1 048 609 | 192 | 192 | 192 | 2000 | 384 000 | 134 | **0** | 268 | 0.0670 | 2866 | 1.91 |
| glv-orbit | 20 | 1 048 609 | 192 | 64 | 64 | 2000 | 384 000 | 132 | **0** | 264 | 0.0660 | 2909 | 1.88 |
| plain     | 20 | 1 048 609 | 384 | 384 | 384 | 2000 | 768 000 | 594 | **0** | 1188 | 0.2970 | 1293 | 2.11 |
| glv-orbit | 20 | 1 048 609 | 384 | 128 | 128 | 2000 | 768 000 | 567 | **0** | 1134 | 0.2835 | 1355 | 2.02 |
| plain     | 24 | 16 777 333 | 384 | 384 | 384 | 2000 | 768 000 | 35 | **0** | 70 | 0.0175 | 21 943 | 1.99 |
| glv-orbit | 24 | 16 777 333 | 384 | 128 | 128 | 2000 | 768 000 | 30 | **0** | 60 | 0.0150 | 25 600 | 1.71 |
| plain     | 24 | 16 777 333 | 768 | 768 | 768 | 2000 | 1 536 000 | 145 | **0** | 290 | 0.0725 | 10 593 | 2.06 |
| glv-orbit | 24 | 16 777 333 | 768 | 256 | 256 | 2000 | 1 536 000 | 132 | **0** | 264 | 0.0660 | 11 636 | 1.88 |

## What the measurements say (measured facts only)

1. **Spurious-root rate = 0 in every one of the 12 settings.** In each row
   `roots-in-base = 2 × confirmed relations` exactly: each real relation `{i,j}` is found
   twice (once solving from `x_i`, once from `x_j`), and **every** S₃ root that lands in
   the factor base lifts to a real EC relation. This is the direct empirical signature of
   Semaev's S₃ iff-theorem for on-curve x-coordinates — measured here, not assumed. A
   separate internal counter confirms every solved root actually zeroes `S₃`
   (`s3_nonzero_roots = 0` everywhere).

2. **The S₃ solver is complete and sound vs the P0 enumeration.** `validate.py`
   independently brute-forces every 2-term relation by `O(N²)` EC addition on fresh small
   curves (750 targets across 5 configs) and finds the S₃-solve relation set to be
   **identical** in every case, with zero spurious roots. So the `O(N)` field-solve step
   genuinely replaces the `O(N²)` enumeration for this 2-term relation search — it invents
   no relations and misses none.

3. **At matched effective size `N`, plain and glv-orbit give the same yield per target**
   (within sampling noise; glv is slightly higher at 16-bit, slightly lower at 20/24-bit).
   The glv-orbit base reaches that same effective size while **storing only `N/3` seeds**
   (the other two orbit members are recovered by multiplying by `β`), i.e. a **3× storage
   reduction** at equal relation yield — a constant factor, matching P0. The
   `field-solves per target` count is `N` for both bases.

4. **Descriptive-only** `c = yield·p/N²` clusters at **1.7–2.2** across all field sizes and
   both bases. This is the same occupancy constant P0 measured for the enumeration model
   (analytic `c ≈ 2`), which is expected precisely because the solver finds the identical
   relation set. **This is a description of the sizes run; it is not an asymptotic law and
   no complexity conclusion is drawn from it.**

## What this does NOT establish

This experiment measures a single narrow step and supports **no** ECDLP complexity claim.
In particular it does **not** test, and nothing here should be read as evidence about:

- **`m ≥ 3` Semaev systems.** Only the 3-variable `S₃` with one variable fixed to the
  target (a 2-term relation) is solved. Higher-arity decompositions `R = ΣP_i`, `m ≥ 3`,
  which are where prime-field index calculus actually lives, are untouched.
- **Degree of regularity** of any `S_m` system.
- **Gröbner-basis cost** (macaulay/matrix size, memory, solving time). The 2-term step is a
  single univariate quadratic; no multivariate elimination is performed.
- **A faithful Petit composed low-degree rational-map construction.** No such map is built;
  "P1_petit" here names the experiment slot, not an implementation of Petit's algorithm.
- **Asymptotics / scaling in `p`.** Three field sizes are far too few, and the point of the
  run is correctness of the solve-and-confirm step, not a growth exponent. No `T(p)`, no
  `p^{1/2−ε}`, no "advantage" or "no advantage" verdict is asserted.
- **Any statement about secp256k1.** Toy curves only. No break is observed or implied.

## Honest verdict

The **2-term Semaev relation step is now performed by actually solving `S₃`** (not by
enumerating pair sums), every reported relation is EC-verified, the spurious-root rate is a
measured **0**, and an independent brute-force cross-check confirms completeness and
soundness. Within this step, the GLV/`u = x³` orbit structure again buys only a **constant
factor** (≈3× storage at matched effective size), consistent with P0. This does **not**
address the open, decisive parts of `HYP_GLV_SEMAEV_001` (higher-arity systems, degree of
regularity, Gröbner cost, Petit maps), so the question remains open while the hypothesis
is **parked** and no Lean formalization is triggered.
