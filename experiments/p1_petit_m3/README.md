# P1-m3 — Measured S4 (3-term) Semaev relation reconnaissance

Experiment under `HYP_GLV_SEMAEV_001`. Extends the m=2 S3-solving experiment
(`experiments/p1_petit/`) to the **m=3** relation

```
R = P_i + P_j + P_k          <=>          S4(x_i, x_j, x_k, x_R) = 0
```

where `S4` is the fourth summation polynomial for `E : y^2 = x^3 + b` (a = 0), defined
here — matching this repo's Lean layer — as a **resultant of two third summation
polynomials**:

```
S4(x1, x2, x3, x4) = Res_Y( S3(x1, x2, Y),  S3(x3, x4, Y) ).
```

This is a **measurement**, not an attack and not an index-calculus algorithm. See
`RESULTS.md` for the "what this does NOT establish" section.

## Method (honest cost)

For a target `R = k*G` and each unordered **distinct-index** factor-base pair `(x_i, x_j)`:

1. Build `S4(x_i, x_j, X, x_R)` as a polynomial of degree `<= 4` in the unknown `X = x_k`.
   `S3(x_i, x_j, Y)` is a quadratic in `Y` with constant coefficients; `S3(X, x_R, Y)` is a
   quadratic in `Y` whose coefficients are degree-2 polynomials in `X`. The resultant of two
   quadratics has the closed form `(A1 C2 - C1 A2)^2 - (A1 B2 - B1 A2)(B1 C2 - C1 B2)`,
   evaluated with polynomial arithmetic in `X`.
2. Find the **exact** `F_p` roots of that quartic (custom degree-`<=4` root finder:
   `gcd(f, X^p - X)` for the distinct-root part, then Cantor–Zassenhaus splitting into
   linear factors; cross-checked against sympy and brute-force evaluation).
3. For every root that is a factor-base coordinate `x_k` (distinct index from `i, j`),
   **confirm by actual `ec_add`** that some sign choice `e_i P_i + e_j P_j + e_k P_k = R`
   (the 8 = 2^3 sign patterns). Only EC-confirmed relations are counted; in-base roots that
   lift to no EC relation are counted separately as **spurious**.

Cost is **`O(|F|^2` pair-solves `.` one degree-4 solve`)`** per target, reported as measured
wall time and `solves_per_confirmed_relation`. This is **not** subexponential and **not** a
Gröbner relation step; it is a controlled reconnaissance whose relation set is measured, by a
brute-force path independent of `S4`, to equal the distinct-index 3-term relation set on the tested toy instances. Relations with repeated indices are outside both searches.

## Factor bases compared (matched effective size)

- **plain**: the `N` on-curve points with the smallest x-coordinates.
- **glv-orbit**: `N` x-coordinates closed under the order-3 GLV orbit
  `{x, beta x, beta^2 x}` (all on the curve since `(beta x)^3 + b = x^3 + b`), so only `N/3`
  are stored; the effective size the solve iterates over is matched at `N`.

Both builders are reused verbatim from `experiments/p1_petit/semaev_solve.py`.

## Files

| File | Role |
|---|---|
| `semaev4_solve.py` | `S4` resultant (closed form + Sylvester) with its unit test, degree-`<=4` `F_p` root finder, 8-sign EC confirmation, per-target `search_relations3`. Reuses `s3_coeffs`, `solve_quadratic`, `tonelli_shanks`, `build_plain_base`, `build_glv_base` from P1 and `ec_add`, `ec_mul`, `find_toy_curve` from P0. |
| `run.py` | Driver; writes `runs/*.json` with P0 `manifest.py` provenance. |
| `validate.py` | **Mandatory** validator: replays the manifest and runs an `O(|F|^3)` brute-force triple-EC-addition cross-check independent of `S4`, asserting identical distinct-index relation sets on the tested instances (prints PASS/FAIL). It reuses `confirm_relation3`, so it is not a separately implemented EC oracle. |
| `RESULTS.md` | Measured table + explicit "NOT tested" / "does NOT establish" section. |

## Reproduce

```bash
cd experiments/p1_petit_m3
python3 semaev4_solve.py     # S4 resultant + root-finder unit tests
python3 run.py               # writes runs/<id>.json
python3 validate.py          # replay + O(|F|^3) brute-force cross-check -> PASS/FAIL
```

Deterministic given the fixed integer seed (`SEED = 1`). Python + sympy only; no Lean
toolchain and no modification to `Ecdlp/`, `VERIFIED.md`, or any `.lean` file.

## Dependency note

This experiment imports `s3_coeffs`, `solve_quadratic`, `tonelli_shanks`, `neg`,
`build_plain_base`, `build_glv_base`, `FactorBase` from `experiments/p1_petit/semaev_solve.py`
(the m=2 experiment it extends) and the EC/curve layer from
`experiments/p0_glv_semaev/toy_curves.py`. Nothing is rewritten.
