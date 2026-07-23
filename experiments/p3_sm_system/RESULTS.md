# RESULTS — P3: custom Macaulay proxy for an explicit finite-set Semaev system

**Measured, not asserted.** Every relation counted below is re-verified by real
elliptic-curve addition (`P₁ + … + P_m = R`) inside the solver, and independently
re-derived by a brute-force EC enumeration in `validate.py` (which imports nothing from the
solver). `seed = 1`. Curves: `E_b : y² = x³ + b`, `p ≡ 1 (mod 3)`, `j = 0`, **cofactor 1**,
from `toy_curves.find_toy_curve(bits, seed=1, require_cofactor_one=True)`.

This experiment builds the explicit finite-set relation presentation
`{ S_{m+1}(X₁,…,X_m,x_R)=0, f_F(X_i)=0 }` and **solves it with a Gröbner engine**, then
measures a custom graded **Macaulay-matrix proxy** for solving degree.
It is *not* pair enumeration (P0) and *not* a single univariate solve (P1 `S₃`, P1-m3 `S₄`).

## Definitions used (so the numbers are unambiguous)

- **Reported solving-degree proxy** = the largest degree at which this custom graded routine
  observes a new minimal leading-term generator before its two-consecutive-empty-degree stop.
  That stopping rule is a heuristic: it has not been checked with an external F4/GB engine or
  justified by a Hilbert-series theorem, so the reported value is not a certified d_reg.
- **Degree expression** = `Σ deg(gᵢ) − n + 1`, shown only as a reference expression. Calling it
  a Macaulay upper bound requires hypotheses (for example, appropriate homogenization and
  regularity assumptions) that this experiment does not establish.
- **gb output degree** = max total degree of the *reduced* grevlex Gröbner basis. This is
  the degree of the *final* basis, which is SMALL (2–3) and is **NOT** the solving degree;
  it is shown only to make the distinction explicit and to avoid confusing the two.
- **quotient dim** = number of standard monomials = number of solutions with multiplicity
  over the algebraic closure (the m=2 consistent variety has the 2 ordered solutions
  `(x_a,x_b),(x_b,x_a)`, hence 2).

---

## 1. m = 2 (system `{S₃(X₁,X₂,x_R)=0, f_F(X₁)=0, f_F(X₂)=0}`), plain x-coordinates

Representative **consistent** target `R = P₀ + P₁` (a relation is present). `nvars = 2`.

| bits | p | \|F\| | solving degree | Macaulay bound | max Macaulay matrix (rows×cols) | quotient dim | rels | spurious | T_lin (s) |
|---|---|---|---|---|---|---|---|---|---|
| 16 | 65 539 | 4  | **9**  | 11 | 108×78   | 2 | 1 | 0 | 0.30 |
| 16 | 65 539 | 6  | **13** | 15 | 188×136  | 2 | 1 | 0 | 0.39 |
| 16 | 65 539 | 8  | **17** | 19 | 292×210  | 2 | 1 | 0 | 1.02 |
| 16 | 65 539 | 10 | **21** | 23 | 420×300  | 2 | 1 | 0 | 2.44 |
| 16 | 65 539 | 12 | **25** | 27 | 572×406  | 2 | 1 | 0 | 5.09 |
| 20 | 1 048 609 | 6  | **13** | 15 | 188×136 | 2 | 1 | 0 | 0.46 |
| 20 | 1 048 609 | 10 | **21** | 23 | 420×300 | 2 | 1 | 0 | 2.47 |

**Observed (DESCRIPTIVE-ONLY):** the proxy returns `2·|F| + 1` on every measured
point, and the two tested prime sizes agree at matched `|F|` (the 20-bit rows equal the 16-bit rows at
the same `|F|`). The Macaulay matrices grow as `Θ(|F|²)` (columns
`= C(solving_degree+2, 2) ≈ 2|F|²`). The reduced-basis *output* degree stays 2 throughout —
which is exactly why one must NOT read relation-generation cost off the output basis.

Interpretation (measured, no asymptotic claim): this encoding represents the enumerated set `F`
by `f_F=∏_{a∈F}(X-a)`, whose degree is `|F|` by construction. The observed linear proxy pattern
therefore applies to this presentation; it does not rule out other algebraic factor-base
descriptions or establish `d_reg = Θ(|F|)`.

## 2. m = 2, invariant `u = x³` coordinates (coupled system, `nvars = 2m = 4`)

Faithful invariant system `{S₃(X₁,X₂,x_R)=0, U_i − X_i³=0, f_{F,u}(U_i)=0}`. `f_{F,u}` has
degree `|F|/3` (orbit collapse), but the extra variables `U_i` and the cubing coupling raise
the ring dimension. Representative consistent target.

| bits | \|F\| | #orbits (u) | fb poly deg | solving degree | max Macaulay matrix | quotient dim | rels | spurious | T_lin (s) |
|---|---|---|---|---|---|---|---|---|---|
| 16 | 3 | 1 | 1 | **7** | 1536×715  | 2 | 1 | 0 | 8.1 |
| 16 | 6 | 2 | 2 | **9** | 2750×1365 | 2 | 1 | 0 | 32.5 |
| 16 | 9 | 3 | 3 | **11** | 4719×2380 | 2 | 1 | 0 | 130.3 (probe) |

**Plain vs invariant (the `HYP_GLV_SEMAEV_001` comparison), measured:**

- The invariant coordinate **lowers the solving-degree number** (≈ `2·(|F|/3) + 5` vs the
  plain `2·|F| + 1`) because the factor-base polynomial degree drops from `|F|` to `|F|/3`.
- **But this is not a cost win.** Rewriting in `u = x³` requires coupling `U_i = X_i³`, so
  the system lives in a `2m`-variable ring. At the SAME `|F| = 6` the invariant Macaulay
  matrix is `2750×1365` vs the plain `188×136` (≈ 15–20× larger) and the linear algebra is
  `32.5 s` vs `0.39 s` (≈ 80× slower). The lower degree is measured in a much larger
  polynomial ring; the **actual linear-algebra cost is larger, not smaller.**
- Because `f_F(X) = f_{F,u}(X³)` for an orbit-closed base, the plain and invariant systems
  define the **same relation variety** (validated: identical EC-confirmed relation sets,
  spurious = 0). The `u`-coordinate is a re-description of the same problem, matching the
  P0/P1 finding that GLV symmetry was a constant-factor effect in those tested models. This
  comparison concerns this redundant auxiliary-variable presentation only.

## 3. m = 3 (system `{S₄(X₁,X₂,X₃,x_R)=0, f_F(X_i)=0}`), plain, `nvars = 3`

`S₄ = Res_Y(S₃(X₁,X₂,Y), S₃(X₃,x_R,Y))` has **total degree 12**, so the Macaulay degree
bound jumps to `12 + 3|F| − 3 + 1`. The graded Macaulay reduction to the solving degree is
**not reachable in pure Python** at these sizes; the measurement is reported as a **capped
lower bound**.

| bits | \|F\| | fb poly deg | Macaulay bound | solving degree | quotient dim @cap | rels found | spurious |
|---|---|---|---|---|---|---|---|
| 16 | 5 | 5 | 25 | **> 15 (capped)** | 105 (not stabilised) | 1 | 0 |
| 16 | 6 | 6 | 28 | **> 15 (capped)** | 195 (not stabilised) | 1 | 0 |

At the cap `D = 15` the quotient dimension has **not** stabilised to the true (small) value,
i.e. the Gröbner basis is not yet complete. The proxy did not stabilize by the cap.
This demonstrates a limitation of this pure-Python engine, not a lower bound on the true
relation-generation cost. The system is nonetheless **built and Gröbner-solved
for relations** (lex elimination + `GF(p)` roots): every constructed target's relation is
recovered and EC-verified (§4), independently cross-checked by brute force (§5).

## 4. Relations found and relation probability

`relation_probability` = fraction of random targets `R = k·G` that decompose over `F`
(the P0 birthday regime, `≈ C(|F|,m)/(p/2)`, hence tiny at toy sizes). Constructed targets
`R = Σ ±P_i` are guaranteed-decomposable and exercise "relations found".

| bits | \|F\| | m | coord | random T | random relation prob | random rels (spur) | constructed recovered | constructed spurious |
|---|---|---|---|---|---|---|---|---|
| 16 | 8  | 2 | plain     | 120 | 0.008 | 1 (0) | 8/8   | 0 |
| 16 | 12 | 2 | plain     | 120 | 0.008 | 1 (0) | 12/12 | 0 |
| 16 | 12 | 2 | invariant | 60  | 0.000 | 0 (0) | 12/12 | 0 |
| 16 | 12 | 3 | plain     | 40  | 0.050 | 3 (0) | 12/12 | 0 |

Every EC-confirmed relation verifies; **zero spurious** solver outputs across all blocks
(a solver output that did not EC-verify would be counted separately — none occurred). The
low random-target probability is the expected birthday combinatorics already characterised
in P0/P1; P3's contribution is the **system/degree-of-regularity** measurement, not yield.

## 5. Independent validation (anti-overclaim gate)

`validate.py` re-derives every m-term relation by pure brute-force EC enumeration (uses only
`ec_add`; imports nothing from the Gröbner solver module), and asserts the Gröbner-system
solver's relation set is **identical** on fresh `(bits, |F|, m, coord)` configs and both
random and constructed targets, with **spurious = 0**. It also replays manifest integrity
(`results_hash`, provenance) and every recorded example relation by real `ec_add`.

Actual console output:

```
[HYP_GLV_SEMAEV_001_p3-sm-system_fa4fed78efc9.json] errors=0 warnings=0
cross-check: 100 targets over 5 (bits,N,m,coord) configs; 40 relations; Groebner-system solver == brute-force EC enumeration, spurious=0

VALIDATION: PASS
```

---

## What this does NOT establish (explicit scope)

1. **No asymptotic / complexity / advantage conclusion.** The `d_reg = 2|F|+1` (m=2 plain)
   and `≈ 2|F|/3 + 5` (m=2 invariant) relations are **DESCRIPTIVE-ONLY** fits over the small
   `|F|` actually run (4–12), not proven growth laws. No claim is made that any measured cost
   beats generic `√n`; the data does **not** show a stable sub-generic exponent, and none is
   expected.
2. **The tested coupled `u=x³` presentation is not a speedup on these instances.** Its proxy
   number is lower but its measured matrices and wall time are larger. This does not rule out
   nonredundant quotient or elimination formulations.
3. **m = 3 degree of regularity is only a capped lower bound**; the full graded reduction to
   the solving degree (~Macaulay bound 25–28) is intractable in this pure-Python engine.
   `m ≥ 4` (the `S₅` system) is **not** measured for degree of regularity at all.
4. **No faithful Petit construction.** No composed low-degree rational-map / Weil-descent
   factor base is built; the prime-field factor base here is a raw set of x-coordinates,
   whose degree-`|F|` defining polynomial is precisely what drives `d_reg` up.
5. **Toy sizes only** (16/20-bit primes, `|F| ≤ 12`, cofactor 1). Nothing here transfers to
   cryptographic `p`. No break of secp256k1 is observed or implied.
6. **Peak memory is not separately instrumented** (no `tracemalloc`); the dominant memory
   object is the Macaulay matrix, whose measured dimensions (rows×cols over `GF(p)`) are
   reported as the memory proxy.
7. The `S₄`/`S₅` resultant summation polynomials are used only to define the relation
   variety; their off-variety normalisation differs from P1-m3's `S₄` (a constant multiple),
   which is irrelevant to the variety and was verified by matching the *relation sets*, not
   the polynomials.

## Bottom line (measured)

For this explicit finite-set presentation on the tested toy instances, the custom proxy returned
`2|F|+1`; the tested coupled `u=x³` presentation used larger matrices and more time. These are
reproducible partial-negative measurements, not an exact degree-of-regularity law or a general
GLV/Semaev complexity no-go. The hypothesis is **PARKED**; external GB validation,
nonredundant invariant formulations, m≥3 full solving degree, and faithful Petit remain open.

## Reproduce

```bash
cd experiments/p3_sm_system
python3 semaev_system.py     # self-tests
python3 run.py               # writes runs/<id>.json  (m=3 block is slow: ~10 min)
python3 validate.py          # independent brute-force EC cross-check -> VALIDATION: PASS
```

### Actual `run.py` console output (seed = 1)

```
== degree-of-regularity block ==
[dreg plain     16b m=2 N= 4] fbdeg= 4 nvars=2 solvedeg=9  (macaulay_bound=11, gb_out_deg=2) macaulay=108x78   quot=2 rels=1 spur=0 | Trel=0.034s Tsolve=2.283s Tlin=0.303s
[dreg plain     16b m=2 N= 6] fbdeg= 6 nvars=2 solvedeg=13 (macaulay_bound=15, gb_out_deg=2) macaulay=188x136  quot=2 rels=1 spur=0 | Trel=0.010s Tsolve=0.007s Tlin=0.377s
[dreg plain     16b m=2 N= 8] fbdeg= 8 nvars=2 solvedeg=17 (macaulay_bound=19, gb_out_deg=2) macaulay=292x210  quot=2 rels=1 spur=0 | Trel=0.014s Tsolve=0.009s Tlin=1.011s
[dreg plain     16b m=2 N=10] fbdeg=10 nvars=2 solvedeg=21 (macaulay_bound=23, gb_out_deg=2) macaulay=420x300  quot=2 rels=1 spur=0 | Trel=0.019s Tsolve=0.009s Tlin=2.572s
[dreg plain     16b m=2 N=12] fbdeg=12 nvars=2 solvedeg=25 (macaulay_bound=27, gb_out_deg=2) macaulay=572x406  quot=2 rels=1 spur=0 | Trel=0.022s Tsolve=0.011s Tlin=5.362s
[dreg plain     20b m=2 N= 6] fbdeg= 6 nvars=2 solvedeg=13 (macaulay_bound=15, gb_out_deg=2) macaulay=188x136  quot=2 rels=1 spur=0 | Trel=0.012s Tsolve=1.705s Tlin=0.474s
[dreg plain     20b m=2 N=10] fbdeg=10 nvars=2 solvedeg=21 (macaulay_bound=23, gb_out_deg=2) macaulay=420x300  quot=2 rels=1 spur=0 | Trel=0.021s Tsolve=0.025s Tlin=2.501s
[dreg invariant 16b m=2 N= 3] fbdeg= 1 nvars=4 solvedeg=7  (macaulay_bound=9,  gb_out_deg=2) macaulay=1536x715 quot=2 rels=1 spur=0 | Trel=0.007s Tsolve=0.013s Tlin=8.587s
[dreg invariant 16b m=2 N= 6] fbdeg= 2 nvars=4 solvedeg=9  (macaulay_bound=11, gb_out_deg=2) macaulay=2750x1365 quot=2 rels=1 spur=0 | Trel=0.004s Tsolve=0.011s Tlin=34.179s
[dreg plain     16b m=3 N= 5] fbdeg= 5 nvars=3 solvedeg=15(capped) (macaulay_bound=25, gb_out_deg=3) macaulay=878x816 quot=105 rels=1 spur=0 | Trel=0.119s Tsolve=0.195s Tlin=6.055s
[dreg plain     16b m=3 N= 6] fbdeg= 6 nvars=3 solvedeg=15(capped) (macaulay_bound=28, gb_out_deg=3) macaulay=680x816 quot=195 rels=1 spur=0 | Trel=0.067s Tsolve=0.335s Tlin=3.538s
== relation-probability block ==
[prob plain     16b m=2 N= 8] Trand=120 relprob=0.008 conf_rand=1 spur_rand=0 | constructed=8/8   recovered spur=0
[prob plain     16b m=2 N=12] Trand=120 relprob=0.008 conf_rand=1 spur_rand=0 | constructed=12/12 recovered spur=0
[prob invariant 16b m=2 N=12] Trand=60  relprob=0.000 conf_rand=0 spur_rand=0 | constructed=12/12 recovered spur=0
[prob plain     16b m=3 N=12] Trand=40  relprob=0.050 conf_rand=3 spur_rand=0 | constructed=12/12 recovered spur=0
```
