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
| **Proved** | see `VERIFIED.md` (~160 distinct results / 182 rows) | accepted by the Lean kernel, no `sorry`, no custom axioms |
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

**Scope of this bound (read `notes/SECURITY_SCOPE.md`).** It is a *real theorem* but a
narrow one: it bounds only **classical, generic** (black-box) algorithms. It is **not**
unconditional — it says nothing about non-generic attacks that read the point encoding
(for `𝔽_p^×`, index calculus provably beats `Ω(√p)`; for EC over a prime field no such
algorithm is known but its non-existence is unproven), and it is **classical-only** —
Shor solves ECDLP in quantum polynomial time. secp256k1's resistance to all *known*
non-generic classical attacks is separately machine-checked (anti-MOV/anti-Smart, below).

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
  multivariate polynomials but not the elliptic summation polynomials `Sₙ`. **Base case
  broken open:** the 3rd Semaev polynomial `S₃` and its *forward* direction
  (`P₁+P₂+P₃ = O ⇒ S₃(x₁,x₂,x₃) = 0`) are now machine-checked in **both** nondegenerate
  cases — chord (`S₃_eq_zero_of_chord`) and tangent/doubling (`S₃_eq_zero_of_tangent`), each
  with a secp256k1 corollary (`Ecdlp/Proved/SemaevThree.lean`) — the first Semaev
  formalization in Lean, and now **connected to Mathlib's formalized elliptic-curve group
  law** in every nondegenerate case (`secp256k1_semaev_three_point` for the chord case and
  `secp256k1_semaev_three_point_double` for tangent/doubling: the hypothesis is the actual
  group relation `P₁+P₂+P₃ = O` on `secp256k1.toAffine.Point`, not a coordinate equation).
  The **full `S₃` characterization is now closed** — `S₃_eq_zero_iff` /
  `secp256k1_semaev_three_iff` prove `S₃(x₁,x₂,x₃) = 0 ⟺ x₃ = x(P₁+P₂) or x(P₁−P₂)` (both
  directions), via a sympy-certified two-root master factorization. And **`S₄` is now started**
  (`Ecdlp/Proved/SemaevFour.lean`): `S₄ = Res_X(S₃(x₁,x₂,X), S₃(x₃,x₄,X))` built on Mathlib's
  `Polynomial.resultant`, with **both directions**: the forward `S₄_eq_zero_of_common_root` (a shared root of the two
  `S₃` slices ⟹ `S₄ = 0`) and the reverse/meaning `S₄_common_root_of_eq_zero` (`S₄ = 0` ⟹ the
  two slices share a root **in the field**, since `S₃`'s slice splits with the known roots
  `x(P₁±P₂)` — via `resultant_eq_prod_eval`), plus symmetries — the first `S₄` in Lean, and the
  recursion index calculus over `𝔽_{p^k}` actually uses. Still open: `Sₙ` for `n ≥ 5`.
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

## Upstream-existence check (machine-assisted, evidence-backed)
An automated multi-agent scan of mathlib4 (master + open PRs + Zulip) — see
`notes/UPSTREAM_SCAN.md` — confirms the barrier map above against the live upstream, and
sharpens it: the **generic scaffolding is already upstream** (Weierstrass group law in three
models, division polynomials `ψₙ/φₙ/ωₙ`, rank-1 `normEDS`/`IsEllSequence`, `ZLattice`/Minkowski,
`MvPolynomial`+resultants — all free by import on the pinned v4.31), while the
**cryptographically load-bearing superstructure is a green field**, absent from master, every
surfaced PR, and wider-GitHub Lean search:
- **Weil pairing** `e_n : E[n]×E[n]→μ_n` and the structure theorem `E[n] ≅ (ℤ/n)²` — nothing.
- **Division-polynomial torsion bridge** `ψₙ(P)=0 ⟺ P ∈ E[n]` — the keystone; `ψₙ` is free but
  the link to the point group / mul-by-`n` lives only in stalled PR #13782. **Highest-ROI next port.**
- **Semaev summation polynomials** `S_n` — zero hits upstream (master, PRs, GitHub-wide);
  the `S₃` base case + forward direction is now formalized **in this repo**
  (`Ecdlp/Proved/SemaevThree.lean`), still the only Lean Semaev formalization anywhere.
- **General multi-index elliptic nets** (rank ≥ 2, subnet functoriality) — only rank-1 exists
  (master + stalled PR #25989).
- **EC isogenies / endomorphisms / Frobenius** as point-group homs — no module.
- **Other standard curves** (P-256, Curve25519/ed25519) + **point counting** — no Montgomery /
  twisted-Edwards model, no Schoof; group orders only assertable.
- **Generic-group cost model** and **lattice reduction (LLL/BKZ, SVP/CVP, HNP)** — no Lean
  formalization anywhere (prior art is Isabelle/HOL only).

The scanner itself is a reusable engine capability (upstream-dedup): before building or
re-deriving, it detects whether a target is already proved upstream — which is how the L4
net-relation proof (PR #13155) was found and ported (`Ecdlp/Proved/NormEDSIsElliptic.lean`).
