# P2 — Ward elliptic divisibility sequences: apparition & torsion recon (`HYP_WARD_EDS_001`)

Reproducible experiment that **measures** the Ward normalized elliptic divisibility sequence
(EDS) `W_n(P) = psi_n(P)` on cofactor-1 toy curves and **numerically confirms** the classical
torsion / rank-of-apparition law

```
W_n(P) ≡ 0 (mod p)   ⟺   [n]P = O   on E
```

against an **independent** `ec_mul` computation. The least such `n>0` — the *rank of apparition*
`rho(P)` — equals `ord(P)`, and the full zero set equals the multiples of `ord(P)`.

**Read the scope first.** This rung MEASURES known structure. It draws **no** asymptotic or
complexity conclusion and gives **no** EDS-based ECDLP handle. EDS re-encode point arithmetic;
there is no known prime-field DLP advantage from them (see `RESULTS.md`). A prior experiment was
retracted for over-claiming from equality replays — every torsion claim here is re-verified by
real `ec_mul`.

## What is computed, and how it is cross-checked

`W_n mod p` is built **two mutually reinforcing ways** and reconciled:

1. **Closed forms** for `W_0..W_4` (`W_0=0, W_1=1, W_2=2y, W_3=3x⁴+6ax²+12bx−a², W_4=4y(...)`),
   then the **Ward doubling recurrence** to extend to any `n`:
   - `W_{2k+1} = W_{k+2}W_k³ − W_{k-1}W_{k+1}³` (division-free),
   - `W_{2k} = W_k(W_{k+2}W_{k-1}² − W_{k-2}W_{k+1}²)/W_2`.
   A fast `O(log n)` single-term variant (`eds_term`) computes `W_n` at a large index (e.g.
   `n = ord(P)`) without materializing the whole sequence.
2. Correctness is triangulated (in `eds.py`'s self-test) against: the closed forms; Ward's **full
   master recurrence** `W_{m+n}W_{m-n}W_1² = W_{m+1}W_{m-1}W_n² − W_{n+1}W_{n-1}W_m²` at random
   `(m,n)` (an identity NOT used to generate the sequence); the `n=2` **Somos-4 slice** proved in
   `Ecdlp/Proved/NormEDSSomos4.lean`; and — the decisive tie — the group law itself, both through
   the torsion equivalence and through the multiplication identity
   `x([n]P) = x_P − W_{n-1}W_{n+1}/W_n²` verified against `ec_mul` coordinates.

## Curves

Reuses the **corrected cofactor-1** curves from P0 verbatim
(`experiments/p0_glv_semaev/toy_curves.py`, `find_toy_curve(bits, seed=1,
require_cofactor_one=True)`): `E_b : y² = x³ + b` over `p ≡ 1 (mod 3)`, `j = 0`, with the whole
group `E(F_p) = ⟨G⟩` of **prime** order `ell` (cofactor 1). No `.lean` file and no curve code is
modified. Because the group has prime order, **every** non-identity point has order exactly `ell`;
there are no small-order points, so the apparition of every point is `ell` and the informative
zero cases sit at `n ∈ {ell, 2ell, ...}`.

## Files

- `eds.py` — closed forms, the mod-`p` doubling recurrence (`eds_sequence`), the `O(log n)`
  single-term `eds_term`, an exact integer EDS (`eds_sequence_Z`) for the growth demo, and the
  recurrence cross-checks. Self-test: `python3 eds.py`.
- `run.py` — measures rank of apparition, the zero set, random-point apparition (full-scan and a
  divisor argument), a broad `(P,n)` torsion sample, the recurrence cross-checks, and a small
  periodicity/growth probe; writes `runs/*.json` with `manifest.py`-style provenance.
- `validate.py` — **independent** replay: manifest integrity, P0 curve re-audit, and a fresh
  `(P,n)` recomputation asserting `W_n ≡ 0 ⟺ [n]P = O` plus the coordinate identity, all against
  `ec_mul`. Prints `VALIDATION: PASS/FAIL`.
- `RESULTS.md` — measured table and an explicit "what this does NOT establish" section.
- `runs/*.json` — run manifests.

## Reproduce

```
cd experiments/p2_ward_eds
python3 eds.py         # self-test: closed forms, Ward master recurrence, Somos-4, torsion, growth
python3 run.py         # measurements -> runs/*.json  (24-bit takes ~35s; see scaling note)
python3 validate.py    # independent replay + ec_mul cross-check -> VALIDATION: PASS/FAIL
```

Deterministic: fixed integer `seed = 1`. The 24-bit apparition/zero-set scan is scaled down
(zero set to `2·ell` rather than `3·ell`, one full-scan random point) purely for wall-time; this
is stated in `RESULTS.md`. Python + sympy only; the Lean kernel is untouched.

## Scope

This tests **only** the EDS apparition/torsion structure and confirms the known `psi_n`-torsion
equivalence numerically. It does **not** test, and makes no claim about, any EDS-based attack,
`p`-adic/anomalous method, or DLP speedup. See `RESULTS.md`.
