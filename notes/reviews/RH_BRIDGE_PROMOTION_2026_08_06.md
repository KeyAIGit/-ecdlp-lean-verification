# RH target-bridge promotion review record (RH-004)

Date: 2026-08-06

Scope: the review record cited by the `RH-BRIDGE-*` rows of
`VERIFIED_RESEARCHOS.md`, covering the promotion of the route-neutral
target bridge from the non-built draft
(`domains/riemann-hypothesis/drafts/RiemannTargetBridge.lean`) to the built
module `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/TargetBridge.lean`.

## Review basis

1. **Contract freeze and adversarial review.** The statements are
   character-identical to `domains/riemann-hypothesis/TARGET_BRIDGE_CONTRACT.md`
   (draft v2), which was adversarially reviewed (`SOUND_WITH_FIXES`, all
   findings applied; Annex B of the contract) with every one of its 30+
   pinned-API citations grep-verified twice at Mathlib
   `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.
2. **Draft elaboration audit.** The promoted file body is the drafts-lane
   file audited line-by-line (`LIKELY_ELABORATES`; the P1-c π-cancellation
   checked symbolically; division-by-zero audit clean; no Iff direction
   mixups; fallback alternates recorded inline for every low-confidence
   step) — see `domains/riemann-hypothesis/drafts/README.md`.
3. **RH-003 independent acceptance.** The external reviewer read the Stage 0
   package, tightened its claims (commit `38a70f0`), and merged PR #297
   (squash `8c70680`). Per the owner's instruction, review-and-merge is the
   acceptance step for this lane.
4. **Kernel check.** The Lean kernel's verdict is delivered by CI on the
   promotion PR itself: `lake build` compiles the module, the no-sorry gate
   scans it, and the generated `ResearchOS/LedgerAxiomAudit.lean` +
   `scripts/check_axioms.py` enforce the per-row `standard` axiom base. If
   any of these fail, the promotion PR is red and no row is counted —
   the kernel remains the sole judge.

## Claim boundary (applies to every RH-BRIDGE row)

These theorems locate nontrivial zeros in the open critical strip and prove
the equivalence of three classical *formulations* of RH for Mathlib's
totalized `riemannZeta`. They close the named barrier `S1-TARGET` and
assert **nothing** about the truth of the Riemann Hypothesis; no zero
multiplicity, growth, counting, or route research obligation is touched.

## Differences from the audited draft

Header comment only (draft disclaimer replaced by the built-module header);
imports, statements, and proof bodies are synchronized with the non-built
draft after the kernel-feedback repair below.

## Kernel-feedback repair

The first promotion build exposed the draft's least-mechanical registered
point in P1-d: the compact `push_cast [Int.toNat_of_nonneg ...]` closer left
`-(↑k * 2) = -2 - ↑(-1 + k).toNat * 2` unsolved. The built file, non-built
draft, and contract proof skeleton now use the audit-recorded alternate:
an explicit equality through `Int.cast_natCast` and `Int.toNat_of_nonneg`,
followed by `push_cast` and `ring`. No theorem statement or claim scope
changed. The repair therefore required a fresh promotion CI rerun before
merge; its result is recorded below.

## Completion note

The repaired final head passed `lake build`, the no-sorry gate, and both axiom
audits, and was squash-merged as PR #299 (`288d65b`).
