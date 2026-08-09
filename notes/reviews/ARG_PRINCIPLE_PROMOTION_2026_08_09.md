# Argument-principle package promotion record (upstream pool item 7)

Date: 2026-08-09

Scope: promotion of the independently accepted W1, A1-A4 statement surface of
`domains/riemann-hypothesis/ARG_PRINCIPLE_CONTRACT.md` into the built module
`ResearchOS/Analysis/ArgPrinciple.lean`. Cited by the five `AP-*` rows in
`VERIFIED_RESEARCHOS.md`.

## Review basis

1. **Stage-one acceptance.** Three independent lenses, 2026-08-08, zero blocking
   findings, no lens asking for a signature change; record
   `notes/reviews/ARG_PRINCIPLE_ACCEPTANCE_2026_08_08.md` (merged PR #323).
2. **Editorial fixes applied first.** `RH-015` (merged PR #327) applied 17
   findings to this contract, withdrew 2 and stopped 5 at the signature
   boundary. The draft was written against the CORRECTED contract, not the
   original — which matters, because the original mis-registered `A1` as the
   package's HIGH-severity gate.
3. **Draft and its review.** `RH-016` (merged PR #328) transcribed the surface
   into the drafts lane; two independent lenses returned PASS_WITH_FIXES with
   six findings, all applied.
4. **Statement identity re-verified at promotion time**, byte-exact: 5 of 5.
5. **Name-collision scan.** All five names checked against pinned Mathlib and
   against every declaration already built under `ResearchOS/`: no collision.
   The module opens no `namespace`; the names carry their prefixes literally.
6. **Kernel check.** Delivered by CI on this change, never by this record.

## What the review caught, and why it is recorded

- **`A1` was mis-priced.** The contract called it "the single genuinely new
  move" and registered `S1AP-BRIDGE` as HIGH. A pinned lemma the contract never
  cited has `A1`'s binder context character-for-character; the delta is the
  punctured-to-unpunctured bridge. Re-priced to LOW under `RH-015` and verified
  independently at the pin before the draft was written. The contract's own
  name-collision scan could not have caught this: it greps proposed NAMES, and a
  name-only scan cannot see a semantic duplicate under a different name. That
  limitation is now stated in the scan.
- **`0 < R` is load-bearing for TRUTH in `A2`, `A3` and `A4`.** The acceptance
  record had judged `A4`'s to be mere convenience, having tried witnesses that
  give nonnegative counts. `RH-015` found the counterexample: `∃ n : ℕ` also
  forbids a NEGATIVE count, and with `f = z⁻¹` at `R = -1` the integral is
  `-2πi`. All three statements carry the refutation in their docstrings.
- **A fallback that could never have fired** was found in the draft and
  corrected rather than deleted, on the ground that a fallback is consulted only
  in the emergency it exists for.
- **Two bare `field_simp` closers** became `field_simp <;> ring` — the same
  defect that cost the three-circles package a round on 2026-08-08, fixed in the
  form that is correct whether or not a residue remains.

## Honest expectation, recorded before the verdict

The drafter named `A2` — roughly 330 lines of assembly with several
higher-order unification points — as the declaration most likely to need a
repair round, and wrote its inline fallbacks most densely for that reason. A
rejection there is an ordinary round, not a surprise, and this record will be
extended with whatever the kernel says rather than quietly succeeding.

## Draft synchronization

The built module and `domains/riemann-hypothesis/drafts/ArgPrinciple.lean` are
byte-identical from the first `import` to end of file, differing only in their
leading status header. A proof-only repair must be applied to both before a new
CI run; a statement change stops promotion and returns to contract review.

## Claim boundary

Once and only once the exact merged head passes every gate: what exists is five
generic statements about an arbitrary `f`. This package **closes no barrier,
advances no barrier, and partially closes no barrier**.

`S1-GLOBAL-ZEROS` deserves the explicit sentence, since a divisor sum is the
closest this comes to counting. That row asks for global enumeration and
counting **for ζ or ξ**, with route-specific truncations among its exit items.
`A2` sums the divisor of an arbitrary `f` over an arbitrary open disc, names no
particular function, and chooses no truncation family. The row is OPEN and
untouched. The capability-map effect is inventory only; the map is not edited.

No route is selected. This promotion provides **no evidence for or against the
Riemann Hypothesis** in either direction. The RH queue's ACTIVE task is not this
one, and this record adds no queue entry.
