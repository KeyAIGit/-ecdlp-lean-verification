# B1 tractability map — which sub-lemmas are reachable now, and what the L4 crux really costs

Companion to `notes/B1_COPRIMALITY_PLAN.md`. Produced by an **adversarially-verified proof-design
workflow** (14 agents: independent designs → adversarial verifiers → L4 scoping → synthesis), run
over the *exact* Mathlib v4.31 division-polynomial / `EllipticDivisibilitySequence` API read off the
pinned toolchain. Provenance: designs drafted by AI agents, cross-checked against the live Mathlib
survey; every kernel claim below is either already merged (L1/L5/L6/L6b) or an explicit *design*, not
a proof. The kernel is the only judge of the designs not yet built.

## Status of the low-index certificate leaves (DONE — merged, kernel-verified)
Proved directly by explicit CAS Bézout certificates + `native_decide`, **bypassing L1–L4** for the
specific pairs (they cannot reach general `n`):
- **L5** `IsCoprime Ψ₂Sq Ψ₃` — 2- vs 3-torsion.
- **L6** `IsCoprime Ψ₃ preΨ₄` — 3- vs primitive-4-torsion.
- **L6b** `IsCoprime Ψ₂Sq preΨ₄` — 2- vs primitive-4-torsion. *(pairwise triangle complete)*

## Status of the structural leaves (reachable NOW, independent of L4)
- **L1** `¬IsCoprime f g ⇒ ∃ common root in k̄` (+ easy converse) — **DONE, merged**
  (`Ecdlp/Proved/CoprimeCommonRoot.lean`). Field↔algebraic-closure dictionary; gcd non-unit ⇒
  `degree ≠ 0` ⇒ alg-closed root divides both. Curve-agnostic, upstreamable. *CONFIRMED, one-shot.*
- **L2** `eval`-compatibility: specialize `ΨSq n`, `Φ n` at `x₀` to a scalar EDS
  `w := normEDS β (Ψ₃.eval x₀) (preΨ₄.eval x₀)` with `β² = Ψ₂Sq.eval x₀`; then
  `(ΨSq n).eval x₀ = w(n)²` and `(Φ n).eval x₀ = x₀·w(n)² − w(n+1)·w(n−1)`. **Reachable now** — the
  linchpin `map_normEDS` (ring-hom compatibility of `normEDS`) already exists in Mathlib; the only
  fixes are tactic-level (`simp_rw` not `rw` for the `ite`-condition parity rewrites `Even (n±1)`,
  mirroring Mathlib's own `mk_φ` proof). *CONFIRMED / PLAUSIBLE, multi-lemma.*
- **L3** both-vanish ⇒ two consecutive `w` vanish (`w(n)=0 ∧ (w(n−1)=0 ∨ w(n+1)=0)`) — pure field
  algebra given L2. **Reachable now.** Caveat: L3's statement must be spelled to match exactly what
  L2 delivers (sign, product order, no residual `β`/unit factor), and the neighbour-product bridge
  needs one small extra identity beyond L2's *square* bridge. *CONFIRMED / PLAUSIBLE.*

**So the whole "local structure at a single root" layer (L1, L2, L3) is closeable now, in days,
without touching L4.** What it does *not* do: propagate across indices.

## The gate: general-`n` B1 needs L4

Closing `gcd(Φₙ, ψₙ²) = 1` for **arbitrary `n`** needs the three-term elliptic identity to relate
non-adjacent indices:
```
IsEllSequence W  :=  ∀ m n r, W(m+n)·W(m−n)·W(r)² = W(m+r)·W(m−r)·W(n)² − W(n+r)·W(n−r)·W(m)²
```
for `W = normEDS b c d`. This is the **open Mathlib v4.31 TODO** (`EllipticDivisibilitySequence.lean`
line 44: "prove that `normEDS` satisfies `IsEllDivSequence`"). Only the two-index doubling recurrences
(`preNormEDS_even/odd`) are proven. **No shortcut via the curve `ψₙ`:** for a fixed curve `ψ₂,Ψ₃,preΨ₄`
are algebraically *dependent* (transcendence degree 1), whereas the abstract theorem needs `b,c,d`
independent (degree 3) — so `map_normEDS` cannot transfer a curve-only proof to generic parameters,
and the curve's three-term identity is not in Mathlib either.

## What L4 really costs (scoping)

**The single most valuable structural fact:** the `r`-general identity is a *pure `ring` consequence*
of the `r = 1` master recurrence `(★₁)` — no induction, no fraction field, no non-vanishing lemma:
```
theorem isEllSequence_of_rec_one {W : ℤ → R} (h1 : W 1 = 1)
    (hrec : ∀ m n, W(m+n)·W(m−n) = W(m+1)·W(m−1)·W(n)² − W(n+1)·W(n−1)·W(m)²) :
    IsEllSequence W                       -- ~30–60 lines, pure algebra, PR-able immediately
```
This isolates 100% of the remaining math into `(★₁) = normEDS_rec_one`, whose proof is Ward's
double induction (prove over the universal domain `ℤ[b,c,d]`, invert only `b = W 2`, strong-induct on
`m+n` splitting parities, discharge each case by a `linear_combination` certificate).

**Honest estimate:** ~700–1300 Lean lines; **6–10 person-weeks expected, tail to 12–16 weeks** — a
quarter-scale, single-interlocking-induction effort. Dominant cost centres: (1) discovering the
per-case `linear_combination` certificates (the identity is true; exhibiting the witnesses is the
multi-week part); (2) possible IH-strengthening into a *coupled* induction carrying a companion
identity (the Somos-4 slice `(★₁)(m,2)`); (3) two-sided `ℤ` well-founded induction boilerplate.

## Independently PR-able stepping stones (land these before the big induction)
1. **`isEllSequence_of_rec_one`** — the `r`-general ← `r=1` reduction. Pure algebra, correct today,
   generally useful. *Strongest first move — de-risks the whole project by proving all remaining
   work is `(★₁)`.*
2. **`IsEllSequence` API** — `neg`, index-shift, oddness helpers (closure under `smul` exists).
3. **Universal-ring transfer helper** — "prove an EDS identity over `ℤ[b,c,d]`, get it over all `R`"
   via `map_normEDS` + `IsFractionRing.injective`.
4. **Somos-4 slice `(★₁)(m,2)`** = `W(m+2)W(m−2) = b²·W(m+1)W(m−1) − c·W(m)²` — a 1–2 week warm-up
   that tests the induction machinery and is very likely the companion identity the main crux needs.

## Fork recommendation (workflow synthesis): **A now, staged B, reject C**
- **A — close L1/L2/L3 now.** All verified-correct today; banks the reachable leaves. *(L1 done.)*
- **B — stage the L4 contribution:** PR stepping stones 1–3 (days) → Somos-4 warm-up (1–2 wk) → then
  **gate the full `normEDS_rec_one` induction on the warm-up's go/no-go signal.** Don't authorize the
  quarter-scale spend blind. The stepping stones have standalone upstream value regardless.
- **Reject C** (abandon): the leaves are genuinely closeable and the stones are useful independently.
