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

## Kernel round 1 (rejected) — two errors, both in A2, both predicted

The record above said, before the verdict, that `A2` was the declaration most
likely to be rejected. It was: both errors landed there and nowhere else, and
the other four declarations drew none.

**1. `:549` — `unsolved goals` after the finprod-to-Finset rewrite.** The goal
left standing was

```
⊢ (fun a => ∏ c ∈ s, ((fun x => x - c) ^ D c) a)
    = fun y => ∏ u ∈ s, (y - u) ^ D u
```

so only the POINTWISE POWER application remained. The draft's comment predicted
this residue would close "because `Pi.pow_apply` is a `rfl` lemma", and that is
true — `Pi.pow_apply` (Algebra/Notation/Pi/Defs.lean:136) is `rfl` and is
generic over the `Pow` instance at :133, so it does cover this ℤ exponent. What
the comment missed is that `rw`'s trailing auto-`rfl` runs at REDUCIBLE
transparency and will not unfold the Pi power under a binder. An explicit `rfl`
tactic runs at default transparency and does.

Repaired with `first | rfl | (funext y; simp [Finset.prod_apply, Pi.pow_apply])`,
which keeps the drafter's recorded fallback as the second arm instead of
replacing it. The combinator matters for the same reason `field_simp <;> ring`
did in `W1`: neither arm can die with "no goals" if the other would have
sufficed.

**2. `:665` — `fun_prop` unable to prove `AnalyticAt ?m.1468 (HSub.hSub z) u`.**
Two things went wrong, and the second is caused by the first. The scalar FIELD
was an unassigned metavariable, because nothing in the expected type fixed it
before the tactic ran; Lean said so directly — "Failed to infer `?m.1468` when
applying `analyticAt_const`". With the field unknown the elaborator also
mis-associated the arguments and went hunting for `(z - ·)` analytic at `u`
instead of `(· - u)` analytic at `z`, which is why the reported goal looks
transposed.

Repaired by `show AnalyticAt ℂ (fun y : ℂ => y - u) z` before `fun_prop`, which
pins the field, the function shape and the point together. This is the same
hazard the drafter identified as its own risk #4 and hoisted at two other sites
— it simply missed this one. The drafter's recorded fallback
(`analyticAt_id.fun_sub analyticAt_const`) is also valid: `AnalyticAt.sub`
carries `@[to_fun]` at Constructions.lean:186, so `fun_sub` exists. The `show`
route was preferred because it fixes the CAUSE (the free metavariable) rather
than routing around it, and so protects the site against a future refactor.

No statement moved: 5 of 5 re-verified character-identical against the contract
afterwards, and every shifted ledger anchor kept its `sha256` digest.
