# P1 — Semaev S₃ relation *solving* (not enumeration) for `HYP_GLV_SEMAEV_001`

Reproducible experiment package that closes the "REMAINING" gap left by P0 for the
**2-term** relation step: doing the real Semaev index-calculus step by **solving** the
third summation polynomial `S₃`, instead of enumerating every pair sum.

**Read the honest prior first.** Like P0, the expected outcome is a **negative / no-go**
signal, and this package does **not** claim any speedup or asymptotic result. It measures
a small, well-defined step and re-verifies every relation by real elliptic-curve addition.

## What P0 did, and the gap this closes

P0 (`experiments/p0_glv_semaev/`) found 2-term relations `R = e_i P_i + e_j P_j` by
**enumerating** all `P_i ± P_j` pair sums of the factor base and hashing their
x-coordinates into a dictionary — `Θ(|F|²)` group operations. That is a birthday table,
**not** an index-calculus relation step. P0's honest verdict was "constant-factor only,
hypothesis OPEN".

P1 does the **real** 2-term Semaev step. For a target `R` and each factor-base
x-coordinate `x_i`, it **solves**

```
S₃(x_i, X, x_R) = 0        (a quadratic in the unknown X over F_p)
```

for `X`. Each solve is O(1) field operations plus one modular square root
(Tonelli–Shanks). The relation search therefore costs **`O(|F|)` field-solves per
target**, not `O(|F|²)`. For every root `X` that is a factor-base x-coordinate, the
candidate relation is **confirmed by actual EC addition** (`e_i P_i + e_j P_j = R`,
`e ∈ {+1,−1}`). Only EC-confirmed relations are counted; S₃ roots whose sign-lift gives
no real EC relation are counted separately as **spurious**.

### The third summation polynomial (a = 0)

For `E : y² = x³ + b`, collected as a quadratic `A X² + B X + C` in the middle variable:

```
A = (x_i − x_R)²
B = −(2·x_i·x_R·(x_i + x_R) + 4b)
C = x_i²·x_R² − 4b·(x_i + x_R)
```

Semaev's theorem: `S₃(x₁,x₂,x₃) = 0` **iff** there exist `y_i` with `(x_i, y_i)` on `E`
and `P₁ + P₂ + P₃ = O` for some sign choice. Hence for on-curve x-coordinates a vanishing
`S₃` **always** lifts to a real EC relation, so the measured spurious rate is a direct
empirical check of that theorem — not an assumption.

## Curves

Reuses the **corrected cofactor-1** generator from P0 verbatim
(`experiments/p0_glv_semaev/toy_curves.py`, `find_toy_curve(bits, seed=1,
require_cofactor_one=True)`) — `E_b : y² = x³ + b` over `p ≡ 1 (mod 3)`, `j = 0`, with a
large prime subgroup `⟨G⟩`. No curve is rewritten here. Any curve that is not cofactor 1
is rejected by the generator; none reached this experiment.

## Factor bases compared (at matched effective size)

Both bases are compared at the **same number of distinct x-coordinates** `N` (the count
the S₃ solve iterates over):

- **plain** — the `N` on-curve points with the smallest x-coordinates.
- **glv-orbit** — `N/3` seed points, each closed under the order-3 GLV orbit
  `{x, βx, β²x}` (all on the curve since `(βx)³ + b = x³ + b`); the three orbit members
  share the invariant `u = x³`, so only **one** seed per orbit is stored.

## Files

- `semaev_solve.py` — Tonelli–Shanks (with `p ≡ 3 mod 4` fast path), `S₃` quadratic
  coefficients + root solver, EC re-verification, and both factor-base builders. Reuses
  P0 `ec_add` / `ec_mul` / `find_toy_curve`. Self-test cross-checks Tonelli–Shanks against
  `sympy.sqrt_mod` and checks that S₃-solving recovers every real pair-sum.
- `run.py` — driver; writes `runs/*.json` with `manifest.py`-style provenance (git commit,
  seed, params, tool versions, code hashes, output hash, UTC timestamp).
- `validate.py` — **independent** replay: re-checks manifest integrity and example
  relations by real EC addition, and cross-checks the S₃-solver against an independent
  brute-force EC enumeration (must find the identical relation set, spurious = 0).
- `RESULTS.md` — measured table and an explicit "what this does NOT establish" section.
- `runs/*.json` — run manifests.

## Reproduce

```
cd experiments/p1_petit
python3 semaev_solve.py     # self-test (Tonelli-Shanks vs sympy; S3 vs real pair-sums)
python3 run.py              # measurements -> runs/*.json
python3 validate.py         # independent replay + brute-force cross-check
```

Deterministic: fixed integer `seed = 1`; each run manifest records the actual UTC time,
git revision, command, code hashes, and an output hash.

## Scope

This tests **only** the 2-term `S₃` solve-and-confirm step. It does **not** touch `m ≥ 3`
Semaev systems, degree of regularity, Gröbner-basis cost, or a faithful Petit composed
rational-map construction. See `RESULTS.md` for the full list of what is out of scope and
why no asymptotic or "advantage" conclusion is drawn.
