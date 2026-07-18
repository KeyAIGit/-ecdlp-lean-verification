# WEIL_LADDER.md — the Weil pairing as an autonomous cycle queue

The Weil pairing `eₙ : E[n] × E[n] → μₙ` is a multi-month, kernel-verified build (Mathlib
v4.31 has **no** Weil pairing). Per the maintainer's directive it is done **autonomously,
one rung per cycle**: each cycle the loop takes the top un-done rung below, drafts it, lets
CI (the kernel) judge, and merges only on green — recording a precise no-go if a rung is a
genuine Mathlib gap and moving to the next independent rung.

This file is the granular, machine-followable decomposition of the high-level `W1…W5`
sub-ladder in `notes/FOUNDATIONS.md`. The high-level status there: **W1, W2, W3's
representative-independence half, and the divisor-evaluation rungs W3e-1 (multiplicativity)
and W3e-2 (Miller-representative scaling law + conditional representative-independence) are
landed**; the open frontier is **W3e-3/W3e-4 → W4 (Weil reciprocity, now a frozen no-go,
see below) → W5 (define `eₙ` + properties)**.

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

- **W3e-1 (S) — LANDED** (`Ecdlp/Proved/WeilDivisorEval.lean`, `divEval_mul`/`evalReg_mul`):
  for `f` regular at points `Q, O`, `divEval f ((Q)−(O)) := evalReg f Q / evalReg f O`, and
  `divEval (f·g) = divEval f · divEval g` via pointwise multiplicativity `evalReg_mul` +
  `evalFracAt_mul`.
- **W3e-2 (S) — LANDED** (`Ecdlp/Proved/WeilDivisorRepIndep.lean`,
  `divEval_smul_unit`/`divEval_smul_unit_eq`/`evalReg_smul_unit`): if `g = u·f` with `u` a unit
  of `F[E]` (two Miller functions, `secp256k1_miller_function_unique`) then
  `divEval g = (u(Q)/u(O)) · divEval f` (scaling law, unconditional); and `divEval g = divEval f`
  when `u(Q) = u(O)` (conditional representative-independence). **Honest residual:** the
  hypothesis `u(Q) = u(O)` — i.e. units of `F[E]` are constants — is absent from Mathlib v4.31
  (`secp256k1_miller_eval_scaling` gives only nonvanishing `u(P) ≠ 0`, not equality across
  points), so it is carried as an explicit hypothesis rather than proved.
- **W3e-3 (M)** — support disjointness hypothesis packaging: state `f_P(D_Q)` for `P, Q`
  with `{P,O} ∩ {Q,O}` off `supp(div f_P)`; the `n=3,5,7` closure instances give concrete
  witnesses. Produces `secp256k1_millerEval P Q : F` (the raw pairing value, pre-μₙ).
- **W3e-4 (M/G)** — `f_P(D_Q) ∈ μₙ`: `millerEval P Q ^ n = 1`. Needs `div(f_P)=n·(…)` fed
  through a reciprocity fragment; may partially depend on W4. If blocked, record the no-go.

### W4 — Weil reciprocity `f(div g) = g(div f)`

- **W4-1 (G) — BLOCKED (frozen no-go, 2026-07-18; see `BARRIERS.md` §B3 Weil reciprocity).**
  Reciprocity for a single pair of degree-0 divisors with disjoint support on `secp256k1`.
  Assessed as a genuine Mathlib gap with **no reachable non-vacuous special case**: the landed
  layer rides on `toClass`/`ClassGroup` (divisors mod principal), which forgets exactly the
  `F*`-valued data reciprocity equates; the three missing pieces (differential residue + residue
  theorem; tame symbol + product formula; `x:E→ℙ¹` pull-back + symbol norm-compatibility) are
  each an upstream-grade port absent at v4.31 and on master; and a concrete `native_decide`
  instance is blocked by the non-constructive Miller function (`ClassGroup.mk_eq_one_iff`). The
  loop routes to the independent rung **W3e-3** instead.
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
