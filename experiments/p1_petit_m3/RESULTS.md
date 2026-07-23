# P1-m3 results — Semaev S₄ (3-term) relation SOLVING

Measured extension of P1 (`experiments/p1_petit/`, the 2-term S₃ solve) to the **3-term**
relation step, done by SOLVING the 4th summation polynomial rather than enumerating triples.

## Method (measured, honestly bounded)
- Toy curves `E_b: y²=x³+b` over `p≡1 (mod 3)`, cofactor 1 (prime subgroup), from the corrected
  P0 generator.
- For a target `R` and each **unordered distinct-index pair** `(x_i, x_j)` of factor-base x-coordinates, form
  `S₄(x_i, x_j, X, x_R) = Res_Y( S₃(x_i,x_j,Y), S₃(X,x_R,Y) )` — a polynomial of degree ≤4 in the
  unknown `x_k` — and find its `F_p` roots. Each root `x_k` in the base is CONFIRMED by actual
  `ec_add` over the 8 sign patterns `±P_i ± P_j ± P_k = R`. Cost is **O(|F|²·deg-4-solve)** per
  target — reported as measured; this is **not** a subexponential index-calculus algorithm.
- The `S₄`-as-resultant construction is unit-tested four ways (closed-form == Sylvester == sympy
  == root-product on 3000 randoms) and every real signed 3-term sum is checked to zero `S₄` and be
  recovered by the solve (5760 sums).

## Measured table (`seed=1`, `T` = targets/setting; spurious = 0 in every setting)

| variant | bits | p | N (distinct x) | orbits | stored | pair-solves | confirmed rel. | spurious | roots-in-base | yield/target |
|---|---|---|---|---|---|---|---|---|---|---|
| plain | 16 | 65 539 | 18 | 18 | 18 | 45 900 | 26 | **0** | 78 | 0.0867 |
| glv-orbit | 16 | 65 539 | 18 | 6 | 6 | 45 900 | 33 | **0** | 99 | 0.1100 |
| plain | 16 | 65 539 | 36 | 36 | 36 | 94 500 | 111 | **0** | 333 | 0.7400 |
| glv-orbit | 16 | 65 539 | 36 | 12 | 12 | 94 500 | 153 | **0** | 459 | 1.0200 |
| plain | 20 | 1 048 609 | 24 | 24 | 24 | 55 200 | 0 | **0** | 0 | 0.0000 |
| glv-orbit | 20 | 1 048 609 | 24 | 8 | 8 | 55 200 | 4 | **0** | 12 | 0.0200 |
| plain | 20 | 1 048 609 | 48 | 48 | 48 | 112 800 | 14 | **0** | 42 | 0.1400 |
| glv-orbit | 20 | 1 048 609 | 48 | 16 | 16 | 112 800 | 12 | **0** | 36 | 0.1200 |
| plain | 24 | 16 777 333 | 48 | 48 | 48 | 67 680 | 0 | **0** | 0 | 0.0000 |
| glv-orbit | 24 | 16 777 333 | 48 | 16 | 16 | 67 680 | 0 | **0** | 0 | 0.0000 |

Reading (measured facts only): the `u=x³`/GLV-orbit base stores **N/3** seeds for the same `N`
distinct x-coordinates (a **constant** ~3× storage factor, exactly as in P0/P1); at these small
`N`/`p` the 3-term yield is comparable between plain and orbit variants within the small counts
observed. `spurious_roots = 0` and `s4_nonzero_roots = 0` in every setting — the direct empirical
signature that a factor-base `S₄` root always lifts to a real EC 3-term relation.

## Independent cross-check (the anti-overclaim gate)
`validate.py` re-derives distinct-index 3-term relations by an **O(|F|³) brute-force** triple
`ec_add` enumeration independent of `S₄` and asserts the `S₄`-solve set is identical: **600 targets
across 5 configs, 105 relations, S4-solve == brute-force, spurious=0, s4_nonzero=0 → VALIDATION:
PASS.** Thus the two paths agree on the tested toy instances for relations using three distinct
factor-base indices. Repeated-index decompositions were excluded from both paths. The brute-force
path reuses `confirm_relation3`, so this is not a separately implemented EC oracle.

## What this does NOT establish
- It does **not** establish completeness for decompositions with repeated factor-base indices.
- It does **not** test m ≥ 4 systems, the **degree of regularity**, or any **Gröbner-basis**
  relation-collection cost — no polynomial system is built or reduced; roots are found directly.
- It does **not** implement a faithful **Petit composed low-degree rational-map** construction.
- The `O(|F|²·deg-4)` pair-loop is **not** a subexponential index-calculus algorithm and no such
  claim is made.
- **No asymptotic, complexity, or advantage/no-advantage conclusion** is drawn; the table is raw
  measured counts at fixed small sizes.
- No statement about secp256k1. `HYP_GLV_SEMAEV_001` is **PARKED**.

## Reproduce
`python3 run.py` (writes `runs/*.json` with provenance) then `python3 validate.py` (must print
`VALIDATION: PASS`). `python3 semaev4_solve.py` runs the S₄ unit tests.
