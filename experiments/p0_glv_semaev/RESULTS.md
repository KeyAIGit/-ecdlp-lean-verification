# PARTIAL RESULTS — `HYP_GLV_SEMAEV_001`: m=2 orbit-keyed pair enumeration

**Reproducible baseline note.** Measured, not asserted. Every counted relation is
re-verified by an actual `ec_add` group computation (`ec_verify_relation` recomputes
`e_i·P_i + e_j·P_j` and checks it equals `±R`); a claim is counted **only** if it
EC-verifies. In every setting reported here `hits == verified_relations` (zero spurious
dict lookups), because a point is determined by its `x`-coordinate up to sign.

- **Curves:** `E_b : y² = x³ + b` over `p ≡ 1 (mod 3)`, `j = 0`, from
  `toy_curves.find_toy_curve(bits, seed=1)` (16 / 20 / 24 bits).
- **Relation model:** `m = 2` Semaev, `R = e_i·P_i + e_j·P_j`, `e ∈ {+1,−1}`,
  `R = k·G` a known multiple (`k` recorded). Detection via a precomputed dict
  `x(P_i ± P_j) → (i,j,sign)`; a relation exists iff `x(R)` is a key.
- **Quantity of interest:** the relation-yield law `yield = verified/trials` as a
  function of base size `B` and field size `p`.
- **Determinism:** `seed=1`; every run recorded by `manifest.py` with a fixed
  timestamp `2026-07-11T00:00:00Z`, code hashes, and an output hash. Manifests in
  `runs/`.

> **Scope boundary:** these programs enumerate `P_i ± P_j` with the EC group law and
> store the results in a dictionary. They do **not** construct or solve an `S_m`
> polynomial system, measure degree of regularity or Gröbner matrices, test `m ≥ 3`,
> or implement Petit's composed rational maps. The data therefore tests a narrow
> pair-count/orbit-keying baseline, not the full registered GLV-Semaev hypothesis and
> not the complexity of prime-field index-calculus relation generation.
>
> The 24-bit legacy rows use a curve with cofactor 3 while the factor base was sampled
> from all of `E(F_p)`. Their EC equalities are valid, but individual factor-base
> logarithms relative to `G` need not exist. Those rows are ambient-group yield sanity
> data, not valid subgroup index-calculus evidence.

## Bottom line for the measured lookup model

All three configurations obey the **same law**

```
yield  ≈  c · B_eff² / p        (exponent 2 in B, exponent −1 in p)
```

Within direct `m=2` pair enumeration, the GLV automorphism `φ(x,y) = (βx, y)` and
the orbit key `u = x³` move only the constant `c`. They do not change the measured
`B²/p` occupancy law. This is the expected combinatorics of hashing `Θ(B²)` pair
sums into `Θ(p)` possible targets.

This does not establish a time bound `T(p)`: constructing the dictionary itself costs
`Θ(B²)`, which is `Θ(p)` at `B = Θ(√p)`, and no polynomial-system solver was measured.
**Verdict: PARTIAL NEGATIVE.** Close the finite-orbit pair-lookup sub-hypothesis;
keep the invariant-polynomial relation-generation hypothesis open.

---

## 1. Plain baseline (`semaev_core.py`) — the reference law

Direct pair enumeration over an `x` factor base. This is a sanity baseline every
variant is measured against, not an implementation of Semaev polynomial solving.

Fitted constant `c = yield·p/B²`:

| bits | p | B | pairs | trials | verified | yield | c = y·p/B² | regime |
|---|---|---|---|---|---|---|---|---|
| 16 | 65 539 | 64 | 2 016 | 4000 | 478 | 0.1195 | **1.91** | unsaturated |
| 20 | 1 048 609 | 256 | 32 640 | 4000 | 463 | 0.1158 | **1.85** | unsaturated |
| 24 | 16 777 291 | 1024 | 523 776 | 4000 | 499 | 0.1247 | **2.00** | unsaturated |
| 24 | 16 777 291 | 2000 | 1 999 000 | 4000 | 1545 | 0.3862 | 1.62 | mild sat. |
| 20 | 1 048 609 | 512 | 130 816 | 4000 | 1537 | 0.3842 | 1.54 | saturating |
| 16 | 65 539 | 256 | 32 640 | 4000 | 3478 | 0.8695 | 0.87 | saturated |
| 20 | 1 048 609 | 1024 | 523 776 | 4000 | 3510 | 0.8775 | 0.88 | saturated |
| 20 | 1 048 609 | 2048 | 2 096 128 | 4000 | 3999 | 0.9998 | — | saturated |

**Constant:** in the unsaturated regime (`yield < ~0.6`) the measured `c = y·p/B²`
clusters at **1.85–2.00** across all three field sizes. This matches the analytic
`c = 2` (~2 distinct combination `x`-values per pair, over ~`p/2` point-bearing
`x`-coordinates).

**Exponent:** the fixed-bits log-log `B`-slope over a full sweep reads **1.69–1.73**,
but this is a *birthday-saturation artifact* — the larger `B` in each sweep is already
approaching `yield → 1`. An independent skeptic re-run pushed deep into the unsaturated
regime (24-bit, `yield < 0.03`) and measured pairwise `B`-exponents **2.000 → 1.948 →
1.899 → 1.824** (128→256→512→1024→2048), monotonically decaying toward the saturation
limit, and `c = 2.048, 2.048, 1.976, 1.842, 1.631`. **The true exponent is 2**; the
low fitted slope is entirely saturation.

**Independent ground-truth check (skeptic, not trusting the module's own verifier):**
counts reproduced *exactly* (20b B256→463, B512→1537, B1024→3510; 16b B64→478,
B256→3478; 24b B1024→499). Published example: `k=462515`,
`P_i=(216,422690)`, `P_j=(408,132932)`, `e=(−1,+1)` → `−P_i+P_j = (828645,83214) =
k·G` exactly, both on `E_b`.

> **Plain verdict:** relations real; `yield_form_matches_B²/p = true`;
> improvement over generic = **none** (it *is* the generic baseline);
> `measured_constant_ratio = 1.0`.

---

## 2. `glv-base` — GLV-orbit-closed factor base

The base is closed under `φ` (order 3) and `±`. Because `φ` is a homomorphism,
`φˢ(P_i ± P_j) = φˢ(P_i) ± φˢ(P_j)`, so **one** stored base-pair sum witnesses its whole
`φ`-orbit `{x, βx, β²x}` for free. Pair work stays at plain's `store_B²/2` (**not**
`(3·store_B)²`) — this is the "free orbit". The yield law is measured against the
effective base `B_eff = distinct x in the orbit closure`.

**Measured `B_eff = 3.000 · store_B` in every row** (no orbit collisions — confirmed
independently).

| bits | p | B_eff (=3·store_B) | trials | verified | yield | c_eff = y·p/B_eff² |
|---|---|---|---|---|---|---|
| 16 | 65 539 | 192 | 4000 | 1282 | 0.3205 | 0.570 |
| 16 | 65 539 | 759 | 4000 | 3985 | 0.99625 | (sat.) |
| 20 | 1 048 609 | 768 | 4000 | 1270 | 0.3175 | 0.564 |
| 20 | 1 048 609 | 1536 | 4000 | 3102 | 0.7755 | 0.570 |
| 20 | 1 048 609 | 3066 | 4000 | 3989 | 0.99725 | (sat.) |
| 24 | 16 777 291 | 3070 | 4000 | 1280 | 0.3200 | 0.568 |
| 24 | 16 777 291 | 5998 | 4000 | 3018 | 0.7545 | (sat.) |

- **Stable law:** `c_eff = 0.564 / 0.570 / 0.568` across `p` spanning `65539 → 16.7M`
  (256×) and `B_eff` spanning `192 → 3070` (16×). Fitted `B_eff`-exponent `= 1.93 ≈ 2`;
  log(yield) vs log(B_eff²/p) slope `= 0.965 ≈ 1`. **Same exponents as plain in both `B`
  and `p`.**
- **Two honest framings of the constant, both pure constant factors:**
  - *Per effective base element:* `c_eff = 0.568` vs plain `c = 1.78`, ratio
    `0.568/1.78 ≈ 0.32`. This looks like a 3× *degradation* but is a **bookkeeping
    artifact**: the 3 extra dict keys per pair are correlated `φ`-images, not
    independent random points, so `B_eff` over-counts independent capacity by exactly
    the orbit factor 3.
  - *Per physical storage:* `c_store/c_plain ≈ 2.89 ≈ 3`; at fixed storage GLV yields
    **~2.4–2.7× more** verified relations (least-saturated points), approaching the
    theoretical 3× before saturation.
- **Ground truth:** independent reimplementation (only `ec_add/ec_mul/find_toy_curve`
  reused) reproduces every yield to the digit with **zero false positives**. Example
  EC-verified GLV relation: `φ²(P_i=(148,315555)) = (844265,315555)`,
  `φ²(P_j=(515,340607)) = (876022,340607)`, `ec_add(φ²P_i, −φ²P_j) = (386276,771641) =
  k·G`, `k=215561`.

> **glv-base verdict:** relations real; `yield_form_matches_B²/p = true`;
> improvement = **constant-factor**; `measured_constant_ratio = 0.321` per `B_eff`
> (`≈ 2.9` per storage). Exponent unchanged — still need `B_eff = Θ(√p)`, i.e.
> `store_B = Θ(√p)/3`.
> Manifest: `runs/HYP_GLV_SEMAEV_001_glv-base_bc9066a58ada.json`.

---

## 3. `invariant-u` — pair-sum dictionary keyed by the invariant `u = x³`

Here the pair-sum dictionary is keyed by the GLV-orbit invariant `u = x³`.
The Semaev relation polynomial itself is not rewritten or solved in this experiment.
`B_eff = number of distinct orbits = number of distinct u`. Direct demonstration of the
orbit collapse: a GLV-closed base of `3N` points has **exactly `N` distinct `u`-values**
(measured ratio `= 3.0` for `N = 8, 32` at 16 and 20 bits).

Fitted constant `c = y·p/B_eff²`:

| bits | p | B_eff (distinct u) | trials | verified | yield | c = y·p/B_eff² | regime |
|---|---|---|---|---|---|---|---|
| 24 | 16 777 291 | 128 | 8000 | 48 | 0.00600 | **6.14** | deep unsat. |
| 24 | 16 777 291 | 256 | 8000 | 190 | 0.02375 | **6.08** | deep unsat. |
| 24 | 16 777 291 | 512 | 8000 | 695 | 0.086875 | **5.56** | unsat. |
| 24 | 16 777 291 | 1024 | 8000 | 2530 | 0.31625 | **5.06** | unsat. |
| 16 | 65 539 | 64 | 4000 | 1282 | 0.3205 | 5.13 | unsat. |
| 20 | 1 048 609 | 256 | 4000 | 1270 | 0.3175 | 5.08 | unsat. |
| 20 | 1 048 609 | 512 | 4000 | 3102 | 0.7755 | 3.10 | saturating |

- **Constant:** `c ≈ 5.45` (law fit over 7 unsaturated points), clustering 5.0–6.1 deep
  in the unsaturated regime. Fitted `B_eff`-exponent `= 1.90 ≈ 2`.
- **Improvement vs plain:** the invariant coordinate raises the constant by
  `c/c_plain ≈ 5.45/2 ≈ 2.7` — an *independent skeptic* re-check measured
  `measured_constant_ratio = 2.77`. This is a genuine **constant-factor** gain in `c`
  (the `u`-coordinate resolves more distinct combination values per orbit pair), but the
  `B_eff`-exponent stays 2 and the field exponent stays `−1`.
- **Ground truth:** `hits == verified_relations` in all rows. Example EC-verified:
  `k=215561`, `P_i=(148,315555)`, `P_j=(515,340607)`,
  `φ²P_i=(844265,315555)`, `φ²P_j=(876022,340607)`, `R=(386276,771641)`.

> **invariant-u verdict:** relations real; `yield_form_matches_B²/p = true`;
> improvement = **constant-factor**; `measured_constant_ratio ≈ 2.77`. Exponent
> unchanged.
> Manifest: `runs/HYP_GLV_SEMAEV_001_invariant-u_95decc4378f5.json`.

---

## 4. Summary of the yield law across configurations

| config | law | `B`-exponent | `p`-exponent | constant `c` | net effect vs plain |
|---|---|---|---|---|---|
| plain | `y ≈ c·B²/p` | **2** (2.00–1.82 unsat.) | −1 | ~1.9 (analytic 2) | baseline |
| glv-base | `y ≈ c·B_eff²/p`, `B_eff=3·store_B` | **1.93 ≈ 2** | −1 | `c_eff ≈ 0.57` | storage/precompute `÷3–6` |
| invariant-u | `y ≈ c·B_eff²/p`, `B_eff=distinct u` | **1.90 ≈ 2** | −1 | `c ≈ 5.45` | `c` up `≈2.77×` |

Every row has the same measured occupancy law in this finite lookup experiment. Only
the constant and storage↔`B_eff` accounting move. This statement does not extrapolate
to the cost of solving higher-arity summation-polynomial systems.

---

## 5. Verdict against the decision criteria

From the hypothesis registry / README §"Decision criteria":

- **BREAKTHROUGH** requires a time/cost result for relation generation, including the
  polynomial-solving step. This experiment measures only lookup occupancy after
  `Θ(B²)` EC pair enumeration, so it cannot satisfy or refute that criterion.
- **NARROW CLOSE:** finite GLV-orbit keying changes only constants in this `m=2`
  dictionary model. This sub-hypothesis is resolved negatively.
- **REMAINING:** build actual plain and invariant `S_m` systems for `m ≥ 3`; measure
  degree of regularity, Gröbner matrices, time, memory and complete precomputation;
  implement a faithful Petit construction rather than an integer-bit filter.

### **RECOMMENDED STATUS: ACTIVE, WITH A PARTIAL NEGATIVE RESULT.**

The reported equalities are real and EC-verified. That validates the equality replay
harness, not a prime-field ECDLP complexity conclusion. No Lean formalization is
triggered. The next experiment must address the original polynomial-system claim.

---

## 6. Properly scoped draft entry for `BARRIERS.md`

> **Finite GLV-orbit keying does not change the `m=2` pair-enumeration occupancy exponent.**
> For `E_b : y² = x³ + b` over `p ≡ 1 (mod 3)` (CM by `ℤ[ζ₃]`, order-3 automorphism
> `φ(x,y)=(βx,y)`, `φ`-invariants `y` and `u=x³`), the `m=2` Semaev relation yield obeys
> `yield ≈ c·B_eff²/p` with **`B`-exponent 2 and `p`-exponent −1** in every measured
> configuration (16/20/24-bit toy curves, EC-verified relations, `seed=1`).
> Closing the factor base under the GLV orbit (`glv-base`) reproduces the law with
> `B_eff = 3·store_B` exactly and `c_eff ≈ 0.57`, giving a **constant** `3–6×` reduction
> in storage/precompute to reach a fixed `B_eff` (≈2.4–2.7× more relations per unit
> storage, approaching the theoretical 3×). Keying the pair-sum dictionary by the
> invariant `u = x³` (`invariant-u`) collapses each 3-point orbit to one `u`-value
> (measured ratio exactly 3.0) and raises the constant to `c ≈ 5.45`
> (`c/c_plain ≈ 2.77`). In neither case does the measured occupancy exponent change.
> This result is limited to a dictionary built by explicitly enumerating
> `P_i ± P_j`; it is not a lower bound for Semaev polynomial solving, higher-arity
> decompositions, invariant-theory Gröbner systems, or prime-field ECDLP. No break of
> secp256k1 is observed.
> Measured constants: plain `c ≈ 1.9` (analytic 2); glv-base `c_eff ≈ 0.57`
> (`≈2.9×` per storage); invariant-u `c ≈ 5.45` (`≈2.77×`). Ref:
> `experiments/p0_glv_semaev/RESULTS.md` and manifests in `runs/`.

---

## 7. Reproduction

```
cd experiments/p0_glv_semaev
python3 semaev_core.py        # plain baseline
python3 variant_glv-base.py   # GLV-orbit-closed base
python3 variant_invariant.py  # u = x^3 invariant coordinate
```

Same legacy grid `settings=[(20,256),(20,512),(20,1024),(20,2048),(16,256),(24,2000),(16,64),
(24,1024)]`, `T=4000`, `seed=1`. The committed legacy manifests use a fixed timestamp;
new schema-v1 runs record the actual UTC time, git revision, command, code hashes and
an output hash. Ground truth: every
counted relation re-verified by `ec_add`; `hits == verified_relations` in all rows
(zero false positives).
