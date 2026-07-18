# WEIL_LADDER.md — the Weil pairing as an autonomous cycle queue

The Weil pairing `eₙ : E[n] × E[n] → μₙ` is a multi-month, kernel-verified build (Mathlib
v4.31 has **no** Weil pairing). Per the maintainer's directive it is done **autonomously,
one rung per cycle**: each cycle the loop takes the top un-done rung below, drafts it, lets
CI (the kernel) judge, and merges only on green — recording a precise no-go if a rung is a
genuine Mathlib gap and moving to the next independent rung.

This file is the granular, machine-followable decomposition of the high-level `W1…W5`
sub-ladder in `notes/FOUNDATIONS.md`. The high-level status there: **W1, W2, and W3's
representative-independence half are landed**; the open frontier is **W3's evaluation half
(`f_P(D_Q)`) → W4 (Weil reciprocity) → W5 (define `eₙ` + properties)**.

## Landed substrate the ladder builds on (do not re-prove)

- `secp256k1_torsion_iff_principal` (W1) — `n•P=O ⟺ n·([P]−[O])` principal.
- `secp256k1_miller_function_exists` (W2) — the Miller function `f_P` with `div f_P =
  n·([P]−[O])`.
- `secp256k1_miller_function_unique` (W2) — two Miller functions differ by a unit of `F[E]`.
- `evalReg` / `RegularAt` / `regularAt_eval_unique` / `evalReg_eq` / `evalRatAt_eq_evalReg`
  (W3 eval layer, `FunctionFieldRegular.lean`, landed #186) — the value at `P` of a
  function-field element regular at `P`, well-defined.
- `evalFracAt` / `functionField_exists_num_den` / `secp256k1_miller_eval_scaling`
  (`FunctionFieldEval.lean`, `FunctionFieldRepr.lean`) — fraction evaluation + the global
  nonvanishing unit factor.
- `μₙ`: Mathlib `rootsOfUnity` / `IsPrimitiveRoot` (available).

## The cycle queue (ordered; one rung ≈ one cycle; each is a target stem)

Difficulty: **S** small (build on landed API, likely one cycle) · **M** medium (a few
cycles) · **G** genuine Mathlib gap (may need new upstream-style infrastructure; record
the no-go if it resists).

### W3-eval — evaluate `f_P` at the divisor `D_Q = (Q) − (O)`

- **W3e-1 (S)** — `divEval`: for `f` regular at points `Q, O` with `Q ≠ O`, define
  `divEval f ((Q)−(O)) := evalReg f Q / evalReg f O` and its basic algebra
  (`divEval (f·g) = divEval f · divEval g`, `divEval 1 = 1`). Builds on `evalReg` +
  `evalFracAt_mul`. Target stem: `Ecdlp/Targets/weil_w3eval_divEval.lean`.
- **W3e-2 (S)** — `divEval` representative-independence: if `f' = u·f` with `u` a unit of
  `F[E]` (i.e. `f, f'` two Miller functions, `secp256k1_miller_function_unique`), then
  `divEval f' D = divEval f D` (the unit's value cancels in the ratio, via
  `secp256k1_miller_eval_scaling`: `u` nonvanishing at every rational point).
- **W3e-3 (M)** — support disjointness hypothesis packaging: state `f_P(D_Q)` for `P, Q`
  with `{P,O} ∩ {Q,O}` off `supp(div f_P)`; the `n=3,5,7` closure instances give concrete
  witnesses. Produces `secp256k1_millerEval P Q : F` (the raw pairing value, pre-μₙ).
- **W3e-4 (M/G)** — `f_P(D_Q) ∈ μₙ`: `millerEval P Q ^ n = 1`. Needs `div(f_P)=n·(…)` fed
  through a reciprocity fragment; may partially depend on W4. If blocked, record the no-go.

### W4 — Weil reciprocity `f(div g) = g(div f)`

- **W4-1 (G)** — reciprocity for a **single pair of degree-0 divisors with disjoint
  support** on `secp256k1` (the crux identity). Genuine Mathlib gap; likely needs the
  local-symbol / tame-symbol machinery or a direct residue computation. Attempt a special
  case first (e.g. both divisors `(A)−(B)`); if it resists, freeze a precise blocker memo
  naming the missing lemma.
- **W4-2 (G)** — general Weil reciprocity from W4-1 by bilinear extension over divisors.

### W5 — define `eₙ` and prove its properties

- **W5-1 (M)** — `def eₙ P Q := millerEval P Q / millerEval Q P` (or the standard
  `f_P(D_Q)/f_Q(D_P)`), landing in `μₙ` by W3e-4.
- **W5-2 (M)** — **bilinearity** `eₙ(P₁+P₂, Q) = eₙ(P₁,Q)·eₙ(P₂,Q)` (uses W4 + the
  divisor algebra).
- **W5-3 (S/M)** — **alternating** `eₙ(P,P) = 1` and antisymmetry `eₙ(P,Q)=eₙ(Q,P)⁻¹`.
- **W5-4 (G)** — **non-degeneracy**: `eₙ(P,·)=1 ⟹ P=O`. The hard, high-value half.
- **W5-5 (M)** — **Galois-equivariance** → the MOV/Frey–Rück transfer statement (embeds
  `⟨P⟩ ↪ 𝔽_{p^k}^×`), connecting to `EmbeddingDegree.lean`.

## Rules for the grind (per `AUTONOMY.md`)

- One rung per cycle: draft the stem's theorem → CI judges → adversarially verify → merge
  on green; promote the stem (consume it, add a **pure-fact** VERIFIED row, no novelty
  claims).
- A rung marked **G** that resists a full cycle's honest attempt → freeze a precise
  blocker memo (the exact missing Mathlib lemma / the failing step) in `BARRIERS.md`, mark
  the target `blocked`, and move to the next **independent** rung (later rungs that don't
  depend on it).
- Never weaken the invariant; the kernel (CI) is the sole judge; no `sorry` in the built
  base (open rungs live as excluded `Ecdlp/Targets/*.lean` stems until proved).
