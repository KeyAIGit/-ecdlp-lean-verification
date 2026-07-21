# N7 `even_x_algebra` — reduction to two curve-generic scalar cores (grind reference)

Status of the N7-uniform `even_x_algebra` wall (node S3b, `BARRIERS.md §B3`; the doubling x-rung of
`Ecdlp/Targets/n7_uniform_carrier_induction.lean`). This note records the **precise, CAS-validated
reduction** produced by the ultracode workflow `n7-even-x-doubling` so the grind can resume from it.
It is a *plan + validated reduction*, **not** a closed proof.

## The two doubling identities (the wall)
For secp256k1 (`y²=x³+7`), with `A := (Φ k).eval x`, `B := (ΨSq k).eval x`:
```
(I)  (ΨSq (2k)).eval x = 4·B·(A³ + 7·B³)
(II) (Φ  (2k)).eval x = A⁴ − 56·A·B³
```
CAS-certified TRUE for `k = 1..8` (degrees to 255/256) in `scripts/certs/division_doubling_secp.py`
(`CERT_OK`). **No finite `linear_combination` exists** (a Somos-4 substitution leaves an unbounded
`w(k±2)²` remainder) → a **strong induction over the elliptic net** is required.

## Reduction via the landed eval bridge
`w := normEDS β c d`, with `β² = Ψ₂Sq.eval x = 4x³+28`, `c = Ψ₃.eval x = 3x⁴+84x`,
`d = preΨ₄.eval x = 2x⁶+280x³−784`. From `DivisionPolynomialEvalBridge.lean`:
`(ΨSq n).eval x = w n²`, `(Φ n).eval x = x·w n² − w(n+1)w(n−1)`. With `normEDS_mul_complEDS₂`
(`w(2k)=w(k)·complEDS₂(k)`) and `complEDS₂_mul_b` (`β·complEDS₂(k)=w(k−1)²w(k+2)−w(k−2)w(k+1)²=:Q(k)`),
targets (I)/(II) reduce (finite algebra + `β≠0` cancellation) to two **curve-generic scalar cores**:
```
CORE-I  : Q(k)²          = 4·β²·(A(k)³ + 7·B(k)³)          [A=x·w k²−w(k+1)w(k−1), B=w k²]
CORE-II : w(2k+1)·w(2k−1) = 3A⁴ + 4P·A³ + 84A·B³ + 28P·B³   [P=w(k+1)w(k−1)=x·B−A]
```
Both have the **same index window as `normEDS_somos4`** (`Q`: k±2; `A,B,P`: k±1), so the seven-case
`WeierstrassCurve.normEDSRec'` skeleton and index bookkeeping port **verbatim** from `somos4_dom`
(`Ecdlp/Proved/NormEDSSomos4.lean:74-159`). CORE-II is a *separate* window-k±2 induction (its
`normEDS_odd` expansion leaves a `+`-companion `w(k−1)²w(k+2)+w(k−2)w(k+1)²` not in the k±1 window).

## What is done vs. the residual
- **Done / CAS-validated end-to-end:** the reduction above; that (I)/(II) and CORE-I/CORE-II hold on
  the *actual* `normEDS` sequence (numeric x=5 + symbolic k=6,7,8); that **all 10 base cases**
  (both cores, k=0..4) lie in the curve ideal `⟨β²−4x³−28, c−3x⁴−84x, d−2x⁶−280x³+784⟩` (remainder 0).
- **Residual = 4 step certificates + 2 finite base cases:** `coreI_even_step`, `coreI_odd_step`,
  `coreII_even_step`, `coreII_odd_step` (each a single `linear_combination (norm:=ring1) …` over the
  free sequence `W` with the b-scaled `normEDS_even/odd` recurrences + 3 IH instances + 3
  `normEDS_somos4` instances as hypotheses — see `coreI_even_step`'s 12-hyp signature in the draft
  skeleton), plus the emitted `k=3,4` base cases (deg 63/64). The **cofactor bundles must be
  machine-generated** (sympy Groebner / linear-solve over `ℤ[β,c,d,x]`) and kernel-judged — exactly as
  `somos4_odd_step`/`somos4_even_step_scaled` were. The even branch is "scaled" (carries a `β` from
  `complEDS₂_mul_b`; clear via `mul_left_cancel₀ (pow_ne_zero 2 hβ)`).

## Assembly
CORE-I, CORE-II over an integral-domain carrier where `β` exists and `β≠0` (rank-2 extension
`(ZMod p)[X][β]/(β²−4X³−28)`) → multiply/substitute → (I),(II) as `(ZMod p)[X]` identities (pull back
along the injective `(ZMod p)[X] ↪ S'`; LHS/RHS are β-free) → `Polynomial.eq_zero_of_infinite_isRoot`
→ `.eval` at every `x : ZMod p`. Then `even_x_algebra` closes via the eval-bridge assembly already in
the induction file. Named targets: `secp256k1_ΨSq_two_mul_eval`, `secp256k1_Φ_two_mul_eval`, cores
`complEDS₂_sq_eq` (CORE-I), `normEDS_odd_prod_eq` (CORE-II).

## Key lemmas (grep-confirmed)
`normEDSRec'` (Mathlib EllipticDivisibilitySequence.lean:358); `complEDS₂`/`_mul_b`/`_zero.._four`/`_neg`
(:246/:329/:251-267/:272); `normEDS_mul_complEDS₂` (:321); `normEDS_even`/`_odd`/`_neg` (:336/:342/:318);
`map_normEDS`/`map_complEDS₂` (:530/:526); repo `normEDS_somos4` + `somos4_odd_step`/`somos4_even_step_scaled`/
`somos4_dom`/`somos4_dom_int` (NormEDSSomos4.lean:183/35/53/74/162); `eval_ΨSq_eq_normEDS_sq`/`eval_Φ_eq_normEDS`
(DivisionPolynomialEvalBridge.lean:66/78); `φ_ψ_diff` (DivisionPolynomialEllSequence.lean:46).

## Feasibility note (honest)
Closing this needs (a) a sympy cofactor generator for the 4 step certificates + `k=3,4` bases (heavy
Groebner/linear-solve over ~15 free-`W` variables — this exceeded the workflow agents' sandbox compute
budget), and (b) assembling the ~300-line `normEDSRec'` induction and iterating it against the kernel.
Without a local Lean toolchain the (b) loop is server-round-trip-only. It is *mechanical, no
mathematical unknown remains* — but it is a multi-cycle CAS+kernel effort comparable to (and larger
than) the original `NormEDSSomos4` development.

## Tooling update (2026-07-21): cofactor generation is unblocked in-container

Part (a) above — "machine-generating the ~4 cofactor bundles exceeded the sandbox compute
budget" — no longer holds. `sympy` (1.14.0) is available in-container and
`scripts/certs/eds_cofactor_gen.py` generates Lean-ready cofactor bundles:

- `solve_cofactors(goal, hyps, gens)` runs multivariate division (`sympy.reduced`) of the
  step goal by the **original** hypothesis list (recurrences + IH + somos4 instances), with the
  doubled-index `W(2M±i)` variables ordered first so the triangular recurrences eliminate them.
  When the remainder is 0 the returned quotients are exactly the cofactors a Lean
  `linear_combination (norm := ring1) …` cites — no Groebner-basis change-of-variables needed.
- `self_test()` validates the encoding + solver end-to-end: it reproduces the proven
  `somos4_odd_step` bundle (residual 0) **and** re-derives a valid bundle from scratch
  (`python3 scripts/certs/eds_cofactor_gen.py` → `self_test OK`).

Residual is now purely (b): set up the CORE-I/CORE-II even/odd step goals + hypothesis lists,
run `solve_cofactors`, transcribe the four bundles + the two finite base cases into the Lean
step lemmas, assemble the two `normEDSRec'` inductions (porting the `somos4_dom` skeleton), and
kernel-judge via `n7-stem-check` / `build`. The kernel remains the sole judge — a generated
bundle is trusted only once `lake` accepts it.

## CORE-II residual pinned (2026-07-21): the exact "+companion" identity

Running the `sympy` reduction of CORE-II by `{normEDS_odd(2k+1), normEDS_odd(2k-1), somos4(k),
curve}` leaves a residual that factors as `w(k)³ w(k+1) w(k-1) · [ … ]`, and the surviving bracket
is a genuine 5-term EDS relation — the **"+companion"** (the `+` twin of the `ω`-numerator). It is
pinned to an EXACT identity, numerically certified for secp256k1 by
`scripts/certs/core_companion_check.py` (`CERT_OK`, k=1..11):

```
w(k-1)² w(k+2) + w(k-2) w(k+1)²  =  6 x² w(k) w(k+1) w(k-1) − (4x³+28) w(k)³
```

Because it carries **individual** `w(k±2)` (not the somos4 *product* `w(k+2)w(k-2)`), it is not a
finite consequence of the somos4 slice + the `r=1` net relation — it needs its **own** `normEDSRec'`
induction (same skeleton as `somos4_dom`, cofactor via `eds_cofactor_gen.py`). Once this companion
lemma lands, CORE-II closes as a finite `linear_combination` over
`{normEDS_odd×2, somos4, companion, curve}`. This is the precise, verified next brick for CORE-II
(and, with the analogous `−`-form already in hand as the `ω`-numerator, sharpens CORE-I too).

## Honest caveat on the cofactor generator (2026-07-21)

Follow-up probing shows the `eds_cofactor_gen.solve_cofactors` (`sympy.reduced`) path is **not**
a turn-key solver for every step. It cleanly extracts a bundle only when the divisor set reduces
**triangularly** (as in `somos4_odd_step`, where the doubled-index recurrences eliminate in one
pass — validated, residual 0). For the harder steps it does **not** terminate at remainder 0 under
plain multivariate division:

- CORE-I even-step: 186-term residual;
- CORE-II "+companion" even-step: 33-term residual.

These residuals are an artifact of `reduced()` being order-dependent and incomplete for a
non-Groebner divisor set — **not** proof the identity is outside the ideal. But they mean the
Lean-ready cofactor bundle for these steps needs a stronger extraction than a single `reduced`
call: a Groebner basis of the M-window ideal **with change-of-basis tracking** back to the
original hypotheses (the reduced-vs-original-generator gap), or a degree-bounded linear solve
(dense ansatz is combinatorially infeasible at the required ~degree 6 over ~12 vars). This is
almost certainly how the original `NormEDSSomos4` cofactors were produced, and is the real
remaining cost — consistent with this note's "larger than the original NormEDSSomos4 development"
estimate. The generator's `self_test` (somos4) remains a valid, working reference; the CORE /
companion steps are the harder cases it does not yet dispatch automatically.
