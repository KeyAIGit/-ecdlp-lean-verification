# RESULTS — P4: degree of regularity of a COMPOSED low-degree map factor base

**Measured, not asserted.** Every relation counted below is re-verified by real
elliptic-curve addition (`sum_i e_i P_i = R`) inside the solver, and independently
re-derived by a brute-force EC enumeration in `validate.py` (which imports nothing from
the solver's derivation path and reconstructs the factor base itself). `seed = 1`.
Curves: `E_b : y² = x³ + b`, `p ≡ 1 (mod 3)`, `j = 0`, **cofactor 1**, from
`toy_curves.find_toy_curve(bits, seed=1, require_cofactor_one=True)`.

This experiment builds a factor base that is the **image of a COMPOSED low-degree
polynomial map** and solves/measures the Semaev relation system in those coordinates
with the **same P3-validated Gröbner + graded-Macaulay engine**, then compares the
degree of regularity directly against P3's **raw baseline `2|F|+1`** at matched `|F|`.

## 1. Faithfulness to real Petit — read this first (honesty rule 1)

**This is NOT literally Petit's prime-field algorithm; it is an HONEST APPROXIMATION.**
Petit / Weil-descent obtain a low-degree factor-base description from genuine field
structure (a subfield, or an `F_2`-linear subspace under Weil restriction). **Over a
prime field there is no Weil descent**, so no `F_p`-linear-subspace factor base exists to
imitate. P4 therefore builds the closest honest thing the task asks for: a factor base
that really is the image of a **composed low-degree polynomial map** from auxiliary
variables, whose defining **system** has lower per-equation degree than the raw
degree-`|F|` polynomial `f_F(X) = ∏_{a∈F}(X−a)`.

Two composed maps are measured (definitions in `semaev_petit.py`):

- **`product_2aux`** — `X = ρ(σ(t1,t2))`, `σ(t1,t2)=t1+κ·t2` (degree 1),
  `ρ(s)=s²+c` (degree 2): a genuinely composed map of **two** auxiliary variables.
  Factor base `= { ρ(σ(t1,t2)) : t1,t2 ∈ B={0..b0−1} }` restricted to on-curve `x`, so
  `|F| ≈ |B|²` while **every defining equation has degree `≤ max(2, b0) ≈ √|F|`**. This
  is the degree-REDUCING candidate — the prime-field polynomial-map analogue of Weil
  descent's "large base from small pieces". **An approximation, not the real thing.**
- **`single_aux_composed`** — `X = r2(r1(t))`, `r1=t²+a1`, `r2=w²+a2·w+a3` (composed
  degree 4), realised as the chained low-degree system `{X−r2(w)=0, w−r1(t)=0, g(t)=0}`.
  The auxiliary domain still needs `|T| ≥ |F|` points, so `g(t)` has degree `≈ |F|`: the
  high degree is **RELOCATED to `g`, not removed.** This is the honest contrast showing
  that composition *alone* (without the product structure) does not lower the degree.

**What is explicitly NOT done:** no Weil restriction / subfield factor base (impossible
over a prime field); no true rational map with denominators; no `m ≥ 3` degree of
regularity (already intractable in P3); no non-toy primes; the `product_2aux` composition
is degree 2, not a monomial substitution `u=x³` (that P3 already did) — but it is **not**
the structural object real Petit uses.

## 2. Degree of regularity: composed map vs P3 raw baseline (m=2)

Representative **consistent** target `R = P₀ + P₁` (a relation is present). Both systems
built on the **same on-curve factor base**; the raw baseline is P3's
`{S₃=0, f_F(X_i)=0}` built via `p3_sm_system.build_plain_system` (verbatim). Solving
degree = degree of regularity in the Lazard graded-Macaulay sense (largest degree at
which a new leading term appears before the quotient dimension stabilises). `quot` =
quotient dimension (# solutions with multiplicity).

| variant | map | `|F|` | composed nvars | **composed d_reg** | composed max Macaulay (r×c) | composed quot | **raw d_reg = 2\|F\|+1** | raw nvars | raw max Macaulay | raw quot | composed Tlin | raw Tlin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| product_2aux | `X=(t1+κt2)²+c` | 4 | 6 | **7** | **10758×5005** | 2 | **9** | 2 | 108×78 | 2 | 619.07 s | 0.14 s |
| single_aux_composed | `X=r2(r1(t))` | 4 | 6 | **9 (capped)** | **8250×5005** | 2 | **9** | 2 | 108×78 | 2 | 375.70 s | 0.14 s |

**Observed (DESCRIPTIVE-ONLY), the P4 vs P3 decision:**
- **`product_2aux` (the degree-REDUCING map, defining degree `≈√|F|`):** the composed
  d_reg **number drops below the raw baseline — 7 vs `2|F|+1 = 9`** at `|F|=4`. But the
  quotient dimension is the **same (2)**, the relation set is the **same** (validated,
  spurious 0), and the drop is bought in a **6-variable** ring: the Macaulay matrix is
  `10758×5005` vs the raw `108×78` (**≈100× the rows, ≈64× the columns**) and the linear
  algebra is **619 s vs 0.14 s (≈4300× slower)**. The lower degree number is **not** a
  lower cost — the same negative pattern P3 reported for `u=x³`.
- **`single_aux_composed` (composition ALONE, degree relocated to `g(t)`):** the composed
  d_reg is **9 (capped ≥9) — NOT below** the raw baseline of 9. Composition without the
  product structure does not even lower the degree *number*; it only enlarges the ring
  (`8250×5005` matrix, 376 s). This is the honest contrast confirming that the reduction,
  where it appears at all, comes from the multi-variable product structure of
  `product_2aux`, not from composition per se.

**Net:** neither composed map lowers the actual relation-generation cost below the raw
baseline; the degree-reducing one lowers only the d_reg *number*, at a large matrix/time
penalty. **No net advantage** over the P3 raw factor base.

The pattern is the **same as P3's `u=x³` invariant coordinate**: any drop in the
degree-of-regularity *number* is bought by moving to a larger polynomial ring (here `3m`
variables instead of P3's `m`), so the Macaulay matrices and the linear-algebra wall time
are **larger, not smaller**. The composed variety has the **same quotient dimension** and
(validated) the **same EC-confirmed relation set** as the raw baseline: it is a
re-description of the same problem, not a cheaper one.

## 3. Relations found / relation probability (larger `|F|`, d_reg skipped)

`relation_probability` = fraction of random targets `R = k·G` that decompose over `F`
(the P0 birthday regime, tiny at toy sizes). Constructed targets `R = ±P_i ± P_j` are
guaranteed-decomposable and exercise "relations found". Composed-map solver and raw
baseline are both run; every relation EC-re-verified; spurious counted separately.

| variant | `|F|` | random T | relation prob | composed rand rels (spur) | raw rand rels (spur) | constructed recovered | constructed spurious |
|---|---|---|---|---|---|---|---|
| product_2aux (b0=3) | 9 | 40 | 0.000 | 0 (0) | 0 (0) | 20/20 | 0 |
| single_aux_composed (nt=6) | 6 | 40 | 0.000 | 0 (0) | 0 (0) | 15/15 | 0 |

Random targets `R = k·G` decompose over a size-`≤9` toy factor base with birthday
probability `≈ C(|F|,2)/(p/2) ≈ 10⁻³`, so 0/40 random relations is expected (the P0/P3
yield regime — P4 measures the *system/degree*, not yield). All constructed targets are
recovered by the composed-map solver, with **0 spurious**.

## 4. Independent validation (anti-overclaim gate)

`validate.py` reconstructs each composed factor base **independently** from the recorded
map parameters (own map evaluation + own modular sqrt, no solver imports), re-derives
every relation by pure brute-force EC enumeration, and asserts the composed-map solver
AND the raw baseline both equal that ground truth with **spurious = 0**. It also replays
manifest integrity (`results_hash`, provenance), checks every raw-baseline row reproduces
`2|F|+1`, and replays each example relation by real `ec_add`.

```
[HYP_GLV_SEMAEV_001_p4-petit-factorbase_bd3ad7a34ae8.json] errors=0 warnings=0
cross-check: 80 targets over 4 (bits,kind,size,m) configs; 32 relations; composed-map solver == raw baseline == brute-force EC enumeration, spurious=0

VALIDATION: PASS
```

(The independent reconstruction compares the factor base by **x-coordinate set**: the
factor base is a set of x-coordinates, `y` is determined on-curve up to sign, and the
`±1` relation lift is sign-agnostic — the validator additionally checks every
reconstructed `y` is on the curve.)

## 5. What this does NOT establish (explicit scope)

1. **No asymptotic / complexity / advantage conclusion.** The measured `d_reg` values are
   DESCRIPTIVE-ONLY over the tiny `|F|` actually run; no growth law is claimed and none is
   implied to beat generic `√n`.
2. **Not real Petit.** The construction is an APPROXIMATION (prime field, no Weil descent,
   polynomial not rational map). It demonstrates the *mechanism* (factor base as image of a
   composed low-degree map, defining system of lower per-equation degree) but is **not** the
   structural object Petit uses; see §1.
3. **The composed map is not a speedup.** Any drop in the degree-of-regularity *number* is
   accompanied by a `3m`-variable ring, larger Macaulay matrices, and larger wall time — the
   same negative pattern P3 found for `u=x³`.
4. **`single_aux_composed` does not even lower the defining degree** — composition alone
   relocates the degree `|F|` to the auxiliary polynomial `g(t)`.
5. **d_reg measured only at `|F|=4`, m=2** (the `3m=6`-variable Macaulay reductions cost
   ~6–10 min each in pure Python; `single_aux` was capped at `D=9`). `m ≥ 3` is not
   measured (intractable already in P3); the larger `|F|` (9, 6) configs are measured for
   relations only, not d_reg. A single `|F|` point is **not** a growth law.
6. **Toy sizes only** (16-bit prime, `|F| ≤ 9`, cofactor 1). Nothing transfers to
   cryptographic `p`. No break of secp256k1 is observed or implied.
7. **Peak memory is not separately instrumented**; the dominant object is the Macaulay
   matrix, whose measured dimensions are the memory proxy.

## 6. Bottom line (measured)

For prime-field `j=0` toy curves, replacing the raw x-coordinate factor base by the image
of a **composed low-degree map** **can** lower the degree-of-regularity *number* below the
raw `2|F|+1` (measured: `product_2aux` gives `d_reg = 7` vs `9` at `|F|=4`), but **does
not** lower the actual relation-generation cost: the composed system lives in a
`3m`-variable ring, so its Macaulay matrices are ~100× larger and its linear algebra
~4300× slower, at the **same quotient dimension** and the **same (EC-validated) relation
set**. Composition *without* the product structure (`single_aux_composed`) does not lower
the number at all (`d_reg = 9`, not below 9). This is a **negative / no-go signal**,
consistent with P3's `u=x³` result and the honest prior. It **does NOT establish** any asymptotic advantage or barrier, and
it is **not** a faithful reproduction of Petit's prime-field method — only the closest
honest approximation buildable in pure Python over a prime field. Hypothesis
`HYP_GLV_SEMAEV_001` stays **ACTIVE**.

## Reproduce

```bash
cd experiments/p4_petit
python3 semaev_petit.py     # self-tests (composed solver == raw == brute-force EC)
python3 run.py              # writes runs/<id>.json  (6-variable systems: ~20-30 min)
python3 validate.py         # independent brute-force EC cross-check -> VALIDATION: PASS
```
