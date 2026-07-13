# P3 — explicit finite-set Semaev system, Gröbner-solved (`HYP_GLV_SEMAEV_001`)

This package closes the central "REMAINING" gap that P0/P1/P1-m3 explicitly left open:
it **builds and solves an explicit finite-set relation presentation** for point decomposition
and records a custom Macaulay proxy / Gröbner behaviour, in two coordinate systems
(plain `x` vs the GLV-invariant `u = x³`). It does *not* enumerate pairs (P0), and it does
*not* solve a single low-degree univariate per factor-base element (P1 `S₃`, P1-m3 `S₄`).

This package draws **no** asymptotic, exact-d_reg, or general advantage/no-advantage conclusion.
It reports only measured
numbers for the (small) sizes actually run, and every relation is re-verified by real
elliptic-curve addition.

## Exact presentation tested here

For a factor base `F` (a set of x-coordinates) and a target `R`, an `m`-term decomposition
`R = P₁ + … + P_m` corresponds to a common solution of the polynomial **system**

```
{ S_{m+1}(X₁, …, X_m, x_R) = 0,  f_F(X₁) = 0,  …,  f_F(X_m) = 0 }
```

where `S_{m+1}` is the (m+1)-th summation (Semaev) polynomial and
`f_F(X) = ∏_{a∈F}(X − a)` is the factor-base polynomial encoding `X_i ∈ F`. **Finding
relations in this presentation = solving this system.** We solve it with SymPy over
`GF(p)` (lex elimination + `galois` root finding) and record a custom degree-graded
**Macaulay-matrix proxy**. Its stopping rule is heuristic and is not an externally certified
degree of regularity.

- `S₃` for `E : y² = x³ + b` (a = 0) is reused/cross-checked against P1.
- `S₄ = Res_Y(S₃(X₁,X₂,Y), S₃(X₃,x_R,Y))`, `S₅` analogously (Semaev's resultant recursion).
- `S₄` built here is checked to vanish exactly on real 3-term EC relations (self-test) and
  the m=3 system solve is checked against a brute-force EC enumeration.

### Two coordinate systems (the `HYP_GLV_SEMAEV_001` question)

- **plain** — variables `X₁…X_m`, factor-base polynomial of degree `|F|`.
- **invariant** — the order-3 GLV automorphism `φ(x,y) = (βx, y)` has invariant `u = x³`
  (for `E : y² = x³ + b` the curve is `y² = u + b`, so a `φ`-orbit `{x, βx, β²x}` collapses
  to one `u`). The factor base becomes `|F|/3` `u`-values, but `S_{m+1}` genuinely lives in
  `x`, so `u` is coupled back by `U_i = X_i³`. The faithful invariant system is
  `{ S_{m+1}(X,x_R)=0, U_i − X_i³ = 0, f_{F,u}(U_i)=0 }` (2m variables). Since
  `f_F(X) = f_{F,u}(X³)` for an orbit-closed base, this defines the **same variety** in the
  `X_i`; the measurement asks whether the `u`-description nonetheless changes the degree of
  regularity or the Gröbner/Macaulay matrix sizes.

## Measured per (p, |F|, m, coordinate system)

Solving degree (degree of regularity), Macaulay matrix dimensions, quotient dimension,
`#relations` found, relation probability, wall-time split
`T_relations + T_solve + T_linear_algebra`, plus (secondary, clearly labelled) the reduced
grevlex Gröbner-basis *output* degree and the Macaulay degree bound. See `RESULTS.md` for
the tables and the explicit **"what this does NOT establish"** section.

## Curves

Reuses the corrected **cofactor-1** generator from P0 verbatim
(`experiments/p0_glv_semaev/toy_curves.py`, `find_toy_curve(bits, seed=1,
require_cofactor_one=True)`): `E_b : y² = x³ + b` over `p ≡ 1 (mod 3)`, `j = 0`, large prime
subgroup. Factor-base builders (`build_plain_base`, `build_glv_base`) are reused verbatim
from P1 (`experiments/p1_petit/semaev_solve.py`).

## Files

| File | Role |
|---|---|
| `semaev_system.py` | Summation polynomials `S₃/S₄/S₅`; factor-base polynomials; plain & invariant system builders; **lex-Gröbner variety solver**; independent **graded Macaulay degree-of-regularity engine**; general `m`-term **EC re-verification**. Self-test cross-checks `S₄` (vanishes on real relations), m=2 vs P1, m=3 vs brute force, invariant vs plain, and the d_reg engine. |
| `run.py` | Driver: degree-of-regularity block + relation-probability block; writes `runs/*.json` with P0 `manifest.py` provenance (git commit, seed, params, tool versions, code hashes, output hash, UTC timestamp). |
| `validate.py` | **Mandatory anti-overclaim gate.** Re-derives relations by pure brute-force EC enumeration (imports nothing from the solver module) and asserts the Gröbner-system relation set is identical, spurious = 0; replays manifest integrity + example relations. Prints `VALIDATION: PASS/FAIL`. |
| `RESULTS.md` | Measured tables (solving degree, matrices, timings), plain-vs-invariant comparison, and the explicit scope/"not done" section. |
| `runs/*.json` | Run manifests. |

## Reproduce

```bash
cd experiments/p3_sm_system
python3 semaev_system.py     # self-tests (S4 vs brute force; m=2 vs P1; invariant vs plain; d_reg engine)
python3 run.py               # measurements -> runs/*.json
python3 validate.py          # independent brute-force EC cross-check -> VALIDATION: PASS/FAIL
```

Deterministic given the fixed integer `seed = 1`. Python + sympy + galois only; no Lean
toolchain; no modification to `Ecdlp/`, `VERIFIED.md`, or any `.lean` file.

## Scope / honesty

This measures the **relation-generation cost as the degree of regularity of the real
`S_{m+1}` system** at *toy* sizes. It draws **no** asymptotic, complexity, or advantage
conclusion; any exponent mentioned in `RESULTS.md` is **descriptive-only** and labelled as
such. It does **not** implement a faithful Petit composed-rational-map construction, does
**not** reach `m ≥ 4` or non-toy primes, and does **not** claim to beat generic `√n`. See
`RESULTS.md` for the full list.
