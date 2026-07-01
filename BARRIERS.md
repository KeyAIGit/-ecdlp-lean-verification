# Formalization-status registry (barriers & no-go map)

What of the ECDLP knowledge corpus (`data/KG_CLAIM_FORMALIZATION_v1.csv`, 486
atomic claims) can be machine-checked in Lean 4 + Mathlib today, and what cannot —
and *why*. The "cannot" rows are the contribution: they are a precise map of the
foundations that formal cryptography for ECDLP still lacks.

Categories below are grounded in the corpus's own `formal_status` / `mathlib_area`
annotations (the corpus authors' assessment), cross-checked against the verified
base. This is a living document; counts are for the v1 corpus.

## Summary

| Status | Count | Meaning |
|---|---|---|
| **Proved** | see `VERIFIED.md` (~106 distinct results / 116 rows) | accepted by the Lean kernel, no `sorry`, no custom axioms |
| **Tractable now** | ~55 | `GroupTheory.OrderOfElement / Subgroup` — structural group facts |
| **Barrier: no cost model** | ~55 | complexity claims; Lean has no "group-operation count" framework |
| **Barrier: not in Mathlib** | ~62 | 38 quantum-circuit cost model, 24 lattice reduction |
| **Partial: curve / polynomial depth** | ~33 | `EllipticCurve` (+Isogeny), `MvPolynomial` — Mathlib has the base, not the ECDLP constructions |
| **Informal / meta** | ~133 | survey/commentary; not a formal statement by nature |
| **Unassigned** | ~174 | needs human triage before a Lean area can be chosen |

(Counts overlap at the margins and are indicative, not a partition.)

## Proved (the tractable zone, realised)

All in `Ecdlp/` and listed in `VERIFIED.md`. The structural theorems live in the
group-theory zone and are the realised part of "Tractable now":

- secp256k1 parameters & GLV/β eigenvalue facts — `native_decide` (concrete).
- `order_dvd_card` (Lagrange), `cofactor_card_mul_index` (`#E = n·h` abstractly),
  `orderOf_eq_card_of_prime` (prime order ⇒ generator, no small subgroup),
  `cube_root_of_eigenvalue` (root of `x²+x+1` ⇒ `x³=1`) — Mathlib.

### Foundation formalized: the generic-group `Ω(√p)`/`Θ(√n)` results
Previously listed under B1 as blocked-by-missing-cost-model, the **Shoup/Nechaev
generic lower bound is now machine-checked** (`Ecdlp/Proved/GenericGroupBound.lean`,
`Secp256k1GenericSecurity.lean`, `BabyStepGiantStep.lean`, `PollardRho.lean`). The
key insight: its information-theoretic core needs no general cost model — the
algebraic data available to a generic algorithm is exactly the set of affine forms
`a + b·X` it has formed over `ZMod p`, and the bound is a collision count over that
set. Results: `generic_dlog_query_bound` (`p ≤ q·q`), `generic_dlog_sqrt_bound`
(`√p ≤ q`), `generic_success_le` (quantitative), `secp256k1_generic_security`
(`2^127 < q` — ≥128-bit generic security of secp256k1, conditional on the published
primality of `n`); matching `O(√n)` upper bounds `bsgs_decomp` / `pollard_rho_*`
(so generic DLP is `Θ(√n)`). This is the first Mathlib-checked generic-group lower
bound for the discrete log.

## Barriers (the contribution)

### B1. No cost model in Lean (~54 claims)
Remaining complexity statements — index calculus subexponential, distinguished-point
parallel speedups, exact `Θ` running times. Lean has no framework for "number of
group operations" / oracle-query cost, so these cannot be stated faithfully, only
their *structural* corollaries. (The generic `Ω(√p)` lower bound and `O(√n)` upper
bounds are now formalized — see above — because their cores sidestep the cost
model.) **Foundation still needed:** a general oracle / cost model in Mathlib for
exact `Θ` statements.

### B2. Not in Mathlib — missing theories (~62 claims)
- **Lattice reduction (24)** — HNP / biased-nonce ECDSA attacks (LLL/BKZ, CVP).
  Mathlib has no lattice-reduction theory.
- **Quantum circuit cost model (38)** — Shor-style ECDLP resource estimates.
  Out of scope for Mathlib.

### B3. Partial foundations — curve & polynomial depth (~33 claims)
- **Summation / Semaev polynomials** (`MvPolynomial`, partial) — Mathlib has
  multivariate polynomials but not the elliptic summation polynomials `Sₙ`.
- **Weil pairing / isogeny depth** (`EllipticCurve.Isogeny`, partial) — blocks
  *formalizing the MOV/FR transfer reduction itself*; the pairing is not in Mathlib.
- **Point counting** — `#E(𝔽ₚ) = n` for the concrete curve needs a computation
  Mathlib cannot do; the concrete fact is instead pinned via `native_decide`.

**Realized despite the barrier — the transfer *resistance* of secp256k1.** Although
the transfer attacks themselves cannot yet be formalized (no pairing), the
security-relevant boundary facts — that the attacks *cannot help against secp256k1* —
are now machine-checked, sidestepping the missing foundation the same way the
generic bound sidestepped the cost model:
- `secp256k1_embedding_degree_gt_100` (`EmbeddingDegree.lean`) — `p^k ≢ 1 (mod n)`
  for `1 ≤ k ≤ 100`, so the MOV/FR target field `𝔽_{p^k}` is intractably large.
- `secp256k1_trace_ordinary_nonanomalous` (`TraceOfFrobenius.lean`) — trace `t ≠ 0`
  (ordinary, not supersingular), `t ≠ 1` (not anomalous, so Smart/SSSA does not
  apply), and `t² ≤ 4p` (Hasse). With Pohlig–Hellman (`PohligHellman.lean`) and the
  generic `Θ(√n)` bound, **the tractable attack landscape is now saturated**: every
  classical ECDLP attack expressible without a missing Mathlib foundation has a
  verified node, and the rest are precisely the barriers above.

### B4. Informal / meta (~133 claims)
Survey scope, research-gap notes, applicability commentary — no formal statement
to verify. Correctly excluded.

## How to read this for research value
- **Levels 1–2 (the asset):** everything under *Proved* and the rest of *Tractable
  now* — a verified, reusable secp256k1 base and first formalizations.
- **No-go / barrier results:** B1–B3 are publishable in themselves — a formal-methods
  community needs to know exactly which foundations (cost model, lattice reduction,
  Semaev polynomials, Weil pairing) are missing to formalize ECDLP cryptanalysis.
- **Lottery (level 3):** a genuinely new structural / no-go result would come from
  the *Tractable now* zone, not from forcing a barrier.
