# ECDLP Research Map — secp256k1 attack-family frontier

A machine-readable research map of known ECDLP attack families and exactly where each known no-go ends and an unexplored zone begins. It is grounded in the Lean 4 + Mathlib substrate at this repository (secp256k1: `y² = x³ + 7` over `F_p`, `p = 2²⁵⁶ − 2³² − 977`, prime order `n`, cofactor 1).

> This note renders the detailed evidence encyclopedia in
> `data/attack_registry.json`. It does **not** select work. Canonical route
> applicability, threat models, promotion gates, and foundation priority live
> in `repo/ECDLP_DECISION_SUBSTRATE.json`.

**This substrate does NOT break secp256k1, and this map must never be read to imply it does.** Prime-field ECDLP hardness is an **OPEN CONJECTURE**. Every object here is one of four honest verdicts — `resistant`, `not-applicable`, `open-zone`, or `blocked-foundation` — and never "broken". Every satisfied/failed property cites a real Lean theorem (grep-verified in `Ecdlp/Proved/*.lean`) or a documented experiment; genuine unknowns are marked `unknown`, never guessed.

## The five layers

1. **keystone-foundations** — the anchor facts everything builds on: `secp256k1_card_point_eq_n` (#E(F_p)=n, cofactor 1, *no Hasse/Schoof* — now landed in the built tree), `secp256k1_n_prime` (prime order, Pratt), `secp256k1_p_prime` (prime base field, Pratt).
2. **attack-models** — generic/black-box and abstract cost-model families: the generic Ω(√n) lower bound, BSGS/Pollard-rho, multi-target/preprocessing/Cheon, lattice-HNP nonce attacks, and quantum/Shor. Bounded from below by the generic wall, or blocked on a missing Mathlib foundation.
3. **secp256k1-structural** — attacks neutralized or scoped by secp256k1's own algebra: the CM/GLV endomorphism (constant-factor only) and Pohlig-Hellman (killed by prime order).
4. **no-go-barriers** — transfer attacks blocked by machine-checked no-gos: pairing transfer (MOV/Frey-Ruck + Tate, one embedding-degree obstruction), Weil descent (prime field), and p-adic/anomalous lifting (non-anomalous trace).
5. **experiments-scaling** — the reproducible prime-field index-calculus experiments (P0–P4): Semaev summation systems, GLV-symmetric factor bases, Petit composed maps. All partial negatives (~3× constant only); the mathematical question remains open, but `HYP_GLV_SEMAEV_001` is **PARKED**. This is retained evidence, not authorized work.

## How to read an attack object

Each attack carries: `id`, `family`, `layer`, `verdict_class` (one of the four honest verdicts), `one_line`, `required_properties` (what the attack needs to work), `secp256k1_status` (per-property, each with a real Lean identifier or a documented experiment), `asymptotic_complexity`, `memory`, `secp256k1_constants`, `lean_evidence` (grep-verified theorem list), `experimental_evidence`, `kill_criterion` (what would make it viable — its logical negation is why it fails), `open_escape_routes` (exactly where the known no-go ends and unexplored territory begins), `verdict`, `blocked_on`, and `disclosure`. Read `kill_criterion` together with `secp256k1_status`: the attack is defeated precisely when a required property provably fails (a `not-applicable`/`resistant` no-go) or is neutralized by magnitude (Θ(√n) ~ 2¹²⁸), and it is *open* precisely where a property's status is `unknown`/`OPEN`.

**`verdict_class` legend.** `resistant` = machine-checked no-go or magnitude wall bounds the attack (generic Ω(√n), BSGS/rho Θ(√n), GLV constant-factor, MOV/Tate k>100). `not-applicable` = precondition provably absent (Pohlig-Hellman needs composite n; anomalous needs #E=p; Weil descent needs a proper subfield; Cheon/lattice need non-standard input). `open-zone` = no known advantage, but non-existence is unproven — the prime-field index-calculus families, the honest open frontier. `blocked-foundation` = the mechanism cannot even be stated in Mathlib (quantum cost model, lattice reduction, Weil/Tate pairing).

## Deduplication

Sixteen source objects were consolidated to fourteen: **MOV/Frey-Ruck + Tate** were merged (one embedding-degree obstruction, `secp256k1_embedding_degree_gt_100`), and **anomalous SSSA + p-adic/xedni lifting** were merged (shared non-anomalous trace anchors). GLV appears twice by design — as a rho/scalar-mult speedup (`GEN-GLV-003`, structural layer) and as an index-calculus factor-base symmetry (`IC-3`, experiments layer) — kept distinct because they act on different attack surfaces, linked by a `shared-structure` edge. The `edges` array records every merge, the keystone resolution edges, matching lower/upper bounds, framework-to-engine dependencies, the open-boundary between the Weil-descent no-go and the prime-field index-calculus zone, and the shared cost-model/lattice/quantum blockers.

## Historical evidence-priority heuristic

`Priority(H) = P(H) · Impact(H) · InfoGain(H) / (ProofCost + ExperimentCost + SecurityRisk)`. Higher ⇒ work it sooner. A rigorous **no-go scores as high on InfoGain as a speedup would** — closing a tested window is a result. Priors for prime-field subgeneric routes are deliberately low (~0.05 for `HYP_GLV_SEMAEV_001`). Formalize in Lean **only** on a positive explained result or a clean barrier statement; numerically confirming known structure triggers no formalization. Prefer routes that sidestep a missing foundation via an information-theoretic core (how the generic Ω(√n) bound and the MOV/Smart facts were reached) over routes that require building the full missing foundation (cost model, lattice reduction, pairing).

## Responsible-disclosure gate

This map is **public**: it contains **no new attack technique**. Every no-go is defensive; every open-zone object is a partial negative with an honest "expected outcome: negative". `SecurityRisk` in the priority function is near-zero by design and only ever *raises the denominator* — it never raises priority. Should any concrete practical speedup against secp256k1 ever emerge from the open zone (e.g. a genuine sub-√n prime-field relation-generation subroutine), it trips the disclosure gate: it moves to a **closed contour** for private handling, not a public race. Nothing in this substrate reduces single-target secp256k1 ECDLP below Θ(√n) ~ 2¹²⁸, and the registry must not be represented as if it did.

---

## Priority function (not experiment authorization)

```
Priority(H) = P(H) * Impact(H) * InfoGain(H) / (ProofCost + ExperimentCost + SecurityRisk)
```

- **P(H)** — Calibrated prior that H yields a genuine, explained result - either a real speedup OR a rigorous no-go; deliberately LOW for prime-field subgeneric routes (~0.05 for HYP_GLV_SEMAEV_001, per its honest_prior).
- **Impact(H)** — Magnitude if resolved: a prime-field ECDLP exponent change = paradigm-shifting; a machine-checked barrier/no-go or scope boundary = publishable unit; a constant-factor speedup = negligible.
- **InfoGain(H)** — Reduction in frontier uncertainty per run, INCLUDING negative results that CLOSE a tested window - a no-go scores high on InfoGain even when P(speedup) ~ 0.
- **ProofCost** — Lean/Mathlib effort to state and kernel-verify (weeks per rung; MONTHS for a missing foundation such as the Weil pairing, lattice reduction, or a cost model).
- **ExperimentCost** — Compute + engineering to run a reproducible benchmark with an INDEPENDENT validator (toy primes cheap; msolve/Sage/F4-scale or m>=4 systems expensive).
- **SecurityRisk** — Penalty for routes that could actually threaten secp256k1 before responsible disclosure; near-zero here by design (honest-scope, no-break), but any nonzero-break route trips a DISCLOSURE GATE (private handling) instead of a public race - it raises the denominator, it does not raise Priority.

See `data/attack_registry.json` (the evidence map),
`repo/ECDLP_DECISION_SUBSTRATE.json` (the canonical project decisions),
`data/research_decisions.md` (the append-only decision log),
`BARRIERS.md` (the no-go/blocked map), `experiments/HYPOTHESES.yaml` (open tests), and `STATUS.md`
(the canonical ledger snapshot). This document and the registry invent no new attack; secp256k1 is not broken.
