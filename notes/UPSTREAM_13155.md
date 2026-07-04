# Upstream package — help revive mathlib4 PR #13155 (normEDS is an elliptic sequence)

This is a hand-off package for a HUMAN to send. It offers to help land the stalled
upstream proof; it does NOT change anything in mathlib4 (we cannot push there).

- Upstream TODO: `Mathlib/NumberTheory/EllipticDivisibilitySequence.lean` — "prove that
  `normEDS` satisfies `IsEllDivSequence`" (still open on master).
- Existing proof (stalled, open): **PR #13155** (net relation from even/odd recursion) +
  **PR #13057** (normEDS is an EDS). Author: **Junyan Xu (`alreadydone`)** & **David Angdinata**.
- Blocker is logistical: reviewer asked to split the oversized PRs and resolve merge conflicts.
- We independently ported PR #13155's `EllSequence` block onto pinned Mathlib **v4.31.0**; it
  verifies (`normEDS_isEllSequence : IsEllSequence (normEDS b c d)`, `#print axioms =
  [propext, Classical.choice, Quot.sound]`). That gives a concrete, tested list of the
  2024→recent-Mathlib API changes needed to rebase — offered below to whoever revives it.

---

## Draft message (personalise, then send — e.g. as a comment on PR #13155, or Zulip DM to Junyan Xu)

> Hi Junyan (cc David) — I've been using `normEDS` in a downstream formalization and
> independently transcribed the `EllSequence` net-relation block from your PR #13155 onto a
> pinned Mathlib v4.31.0. It compiles cleanly and `IsEllSequence (normEDS b c d)` verifies with
> only the standard axioms. All credit is yours — I only adapted names.
>
> Since #13155/#13057 seem stalled on the "split + rebase" request, I'm happy to help get them
> landed if that's welcome: I already have the concrete API-drift diff from 2024 → current
> Mathlib (listed below), and I can take a pass at rebasing #13155 onto master and splitting it
> into the smaller pieces the review asked for. Would that be useful, or would you prefer to
> drive it yourself? Either way, thanks for the proof — it's exactly what the file's TODO needed.

---

## API-drift fixes (2024 base → recent Mathlib), from the actual port

Concrete changes that were required to compile the `EllSequence` block on v4.31.0. These are
the starting point for a rebase onto current master (master may differ slightly again):

1. **Section-variable auto-inclusion removed.** Prop hypotheses used only inside proof bodies
   are no longer auto-included; needed explicit `include … in` before the affected decls
   (~23 sites: `same`; `par le lt rel mem`; `neg` / `zero` / `one two oddRec evenRec`).
2. **`Int.div` (T-division) gone → `Int.tdiv`.** `Int.mul_div_cancel_left`→`Int.mul_tdiv_cancel_left`,
   `Int.zero_div`→`Int.zero_tdiv`, `Int.neg_div`→`Int.neg_tdiv`. (Two now-unused helpers
   `addMulSub_two_zero`, `addMulSub_three_one` were dropped.)
3. **`Submonoid.closure_induction` signature changed** (membership hypothesis last; motive may
   depend on it) → rewrote `perm` / `rel₄Fin4_perm` to `induction h using Submonoid.closure_induction with`.
4. **`nonZeroDivisors` is now `nzdLeft ⊓ nzdRight`** (a conjunction) → `mem _` becomes `mem.2 _`
   (the right-divisor component) where a single `mem` was used.
5. **Renames / dot-notation:** `Fin.castSucc_lt_succ` takes its index implicitly now;
   `Int.odd_iff_not_even` → `Int.not_even_iff_odd`; `lt_or_le` → `lt_or_ge`;
   `Function.comp.assoc` → `Function.comp_assoc`; `even_zero`/`odd_one` used as terms → inline
   `⟨0, by ring⟩` witnesses; a `(6 ≤ a).not_lt` dot-call broke on `Int.NonNeg` → `absurd … (by omega)`.
6. **Tactic behaviour:** the odd/even branches of `rel₄_of_anti_oddRec_evenRec` now pre-prove the
   index bound so `convert … using 2 <;> ring` leaves only ring goals; `rel₄_iff_evenRec` uses
   `show` instead of `convert_to` to pin the four `rel₄` indices (current `convert_to` spawned
   spurious side goals).

*Our local, attributed port lives at `Ecdlp/Proved/NormEDSIsElliptic.lean` for reference.*
