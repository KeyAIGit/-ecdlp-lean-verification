# P4 — composed low-degree map factor base (Petit-style), built on P3

Experiment for `HYP_GLV_SEMAEV_001`. Measures whether a **composed low-degree
(rational) map** factor base — the Petit / Weil-descent idea of cutting the factor base
out by *lower-degree* equations — gives a Semaev-system **degree of regularity below the
raw `2|F|+1`** that P3 measured for a raw x-coordinate factor base.

This builds directly on `experiments/p3_sm_system/` and **reuses its validated engine
verbatim** (summation polynomial `S3`, the graded-Macaulay degree-of-regularity engine,
the lex-Groebner variety solver, and the EC re-verifier are imported from
`p3_sm_system/semaev_system.py`). P4 adds only the composed-map factor-base construction
and the composed-map relation-system builders.

## Faithfulness (read this first)

This is **NOT** literally Petit's prime-field algorithm. Petit / Weil-descent obtain a
low-degree factor-base description from a genuine field structure (a subfield, or an
`F_2`-linear subspace under Weil restriction). Over a **prime field there is no Weil
descent**, so P4 builds the closest *honest approximation* the task requests: a factor
base that really is the image of a **composed low-degree polynomial map** from auxiliary
variables, whose defining **system** has lower per-equation degree than the raw
degree-`|F|` polynomial `f_F`. Two composed maps are measured:

- **`product_2aux`** — `X = ρ(σ(t1,t2))`, `σ(t1,t2) = t1 + κ·t2` (degree 1), `ρ(s) = s² + c`
  (degree 2): a genuinely composed map of **two** auxiliary variables. Factor base
  `= { X = ρ(σ(t1,t2)) : t1,t2 ∈ B }` restricted to on-curve `x`, so `|F| ≈ |B|²` while
  each defining equation has degree `≤ max(2, |B|) ≈ √|F|`. This is the candidate that
  *could* beat the raw degree-`|F|` description — the prime-field polynomial-map analogue
  of Weil descent's "small pieces". **An approximation, not the real thing.**
- **`single_aux_composed`** — `X = r2(r1(t))`, `r1(t)=t²+a1`, `r2(w)=w²+a2·w+a3` (composed
  degree 4), realised as the chained low-degree system `{X−r2(w)=0, w−r1(t)=0, g(t)=0}`.
  Here the auxiliary domain still needs `|T| ≥ |F|` points, so `g(t)` has degree `≈ |F|`:
  the high degree is **relocated**, not removed. This is the honest contrast showing that
  composition *alone* (without the product structure) does not lower the defining degree.

**What is NOT done:** no Weil restriction / subfield factor base (impossible over a prime
field); no true rational map with denominators; no `m ≥ 3` degree of regularity (already
intractable in P3); no non-toy primes. No asymptotic / advantage / no-go-proof conclusion
is drawn; every fit is descriptive-only.

## Files

| file | role |
|---|---|
| `semaev_petit.py` | composed-map factor base + relation-system builders + d_reg + EC verify (imports P3 engine) |
| `run.py` | grid; composed system vs raw P3 baseline at matched `|F|`; manifest provenance |
| `validate.py` | independent brute-force EC gate (no solver-derivation imports); prints `VALIDATION: PASS/FAIL` |
| `RESULTS.md` | measured table, faithfulness statement, P3 comparison, explicit "does NOT establish" |
| `runs/*.json` | manifest per run (git commit, seed, params, tool versions, code hashes, results hash) |

## Honesty rules (a prior experiment was retracted for breaking these)

1. Measured-only; descriptive-only fits; no asymptotic/advantage/no-go conclusion. The
   construction is an **approximation to Petit** and says so prominently.
2. Every relation re-verified by actual EC addition; spurious counted separately.
3. `validate.py` re-derives relations by brute-force EC enumeration and reconstructs the
   factor base independently, importing nothing from the solver derivation path.
4. `RESULTS.md` states exactly how faithful the construction is, what is not done, and
   whether the measured `d_reg` beats the P3 raw baseline (expected: **no net advantage**).
5. Cofactor-1 curves only; fixed `seed = 1`; Python only (sympy/galois); no Lean/VERIFIED
   files touched.

## Reproduce

```bash
cd experiments/p4_petit
python3 semaev_petit.py     # self-tests (composed solver == raw == brute-force EC)
python3 run.py              # writes runs/<id>.json  (6-variable systems: slow)
python3 validate.py         # independent brute-force EC cross-check -> VALIDATION: PASS
```
