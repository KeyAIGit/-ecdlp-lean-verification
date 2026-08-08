# Three-circles package promotion record (upstream pool item 3)

Date: 2026-08-08

Scope: promotion of the independently accepted TC1-TC11 statement surface of
`domains/riemann-hypothesis/THREE_CIRCLES_CONTRACT.md` into the built module
`ResearchOS/Analysis/ThreeCircles.lean`. This record is cited by the eleven
`TC-*` rows in `VERIFIED_RESEARCHOS.md`.

## Review basis

1. **Independent statement acceptance.** The contract's eleven-signature
   surface was accepted 2026-08-07 under owner-delegated review authority;
   record `notes/reviews/THREE_CIRCLES_ACCEPTANCE_2026_08_07.md` (FINAL,
   editorial fixes applied in place, zero signature changes).
2. **No prerequisites.** The package imports pinned Mathlib only. Nothing in
   the repository has to be merged first, and nothing in the repository
   depends on it.
3. **Draft review provenance.** The promoted body is the drafts-lane file
   reviewed 2026-08-07: all eleven signatures character-identical, every
   claimed locator confirmed by reading the pinned tree, verdict PASS with the
   file byte-unchanged.
4. **Statement identity re-verified at promotion time.** All eleven signatures
   were re-compared mechanically against the contract's canonical `### Statement`
   blocks immediately before this promotion — everything from the
   `theorem`/`def` keyword through the `:=` that opens the proof, byte-exact,
   whitespace not normalised. Eleven of eleven identical.
5. **Name-collision scan.** These eleven declarations are at the root level
   (the module opens no `namespace`), so a name already taken at the pin would
   be a build error rather than a shadow. All eleven were checked against the
   pinned Mathlib tree and against every declaration already built in
   `ResearchOS/`: no collision.
6. **Kernel check.** The verdict is delivered by CI on this promotion change:
   `lake build` compiles the module, the no-incomplete-proof gate scans it, the
   regenerated `ResearchOS/LedgerAxiomAudit.lean` + `check_axioms.py` enforce
   the per-row `standard` axiom base, and `gen_researchos_registry.py --check`
   enforces inverse coverage. If any gate is red, no row is counted.

## Load-bearing checks

- **The `def` is totalized, and every row says so.** `sSupNormCircle f r` is an
  `sSup`, so on a radius where `‖f‖` is unbounded on the circle — or where the
  circle is empty — the junk value stands. TC3 is exactly the hypothesis that
  takes it off that branch, and it is demanded explicitly by every statement
  that needs it. No row asserts that the supremum is attained.
- **Both boundary bounds are hypotheses.** TC8 and TC10 take `M₁` and `M₃` as
  given bounds on the two circles. Nothing in this package computes a maximum
  modulus, and no statement produces a bound for a specific function.
- **Sharpness is not claimed.** TC9 gives log-convexity of the circle maximum
  with the classical exponents; that the exponents are optimal, and the
  extremal functions that would witness it, are outside the surface.
- **The transport is stated as bookkeeping.** TC5-TC7 are about `exp` alone; no
  branch of the logarithm is selected anywhere, and TC7 is a bare existence
  statement.

## Draft synchronization

The built module and the drafts-lane copy
(`domains/riemann-hypothesis/drafts/ThreeCircles.lean`) are byte-identical from
the first `import` through end of file; they differ only in their leading
status header. Any proof-only kernel repair must be applied to both copies
before a new CI run; a statement change stops promotion and returns to contract
review.

## Claim boundary

Once and only once the exact merged head passes the full build, the
no-incomplete-proof gate, inverse ledger coverage, and both axiom audits: what
exists is eleven generic statements about an arbitrary `f : ℂ → E` on an
annulus. This package **closes no barrier, advances no barrier, and partially
closes no barrier**. In particular `S1-GROWTH` remains OPEN and untouched — a
convexity statement about the maximum modulus of an arbitrary function is not a
growth bound for ζ or ξ, and supplies none. The capability map records no
three-circles row and is not edited by this change; the effect is **inventory
only**, which lowers the cost of a future exit and never retires a row.

No route is selected, opened, or advanced. This promotion provides **no
evidence for or against the Riemann Hypothesis**, and makes no claim of
progress on it in either direction. The RH queue is untouched: `RH-012` remains
the single ACTIVE task, and this promotion neither is that task nor competes
with it. This record adds no queue entry of any status.

## Files changed by this promotion

- `ResearchOS/Analysis/ThreeCircles.lean` — new built module (promoted body).
- `ResearchOS.lean` — import added in the domain-neutral analysis-shelf group.
- `VERIFIED_RESEARCHOS.md` — eleven `TC-*` rows; header prefix sentence
  extended to document `TC-` alongside `MB-`, `HK-` and `PL-`.
- `scripts/gen_researchos_registry.py` — `TC-` added to `PREFIX_DOMAINS`,
  mapped to the existing `analysis-generic` lane.
- `domains/riemann-hypothesis/drafts/README.md` — the `ThreeCircles.lean` row
  updated to record the promotion.
- `notes/reviews/THREE_CIRCLES_PROMOTION_2026_08_08.md` — this record.

The generated `data/researchos_result_registry.json`,
`data/result_registry.json` and `ResearchOS/LedgerAxiomAudit.lean` are
regenerated by the repository-wide generator pass, not by this record.

## Kernel round 1 (rejected) — a packaging defect, not a proof defect

The first CI run of this promotion (PR #319, run 31241...) rejected this module
with a single error:

```
error: ResearchOS/Analysis/ThreeCircles.lean:57:0: unknown module prefix 'below'
```

This was **not** a defect in the reviewed Lean. It was introduced by the
promotion tooling. The built module is assembled as `new header + draft body`,
and the script that located the body took the first line beginning with
`import `. The drafts-lane header contains the prose sentence

> "...every `import` below is pinned Mathlib; nothing here mentions ζ, ξ, ..."

wrapped so that a line literally begins with `import below is pinned Mathlib;`.
The splitter cut there, so the promoted file was the new header followed by the
tail of the OLD header, and Lean read that sentence as an import declaration.
The reviewed proof text was never reached.

Two things are worth recording about this, because the failure mode is worse
than the error.

1. The byte-identity check that was supposed to catch it did not, because it
   used the same splitter on both sides of the comparison. Two files spliced
   identically wrongly compare identical. The splitter is now comment-aware and
   additionally requires a real module path (`^import [A-Z]...$`), and the
   check was re-run against all five analysis-shelf modules.
2. Nothing about the statements or the proofs changed in the repair. The
   correctly assembled module has the same body the drafts-lane review passed,
   and the eleven signatures were re-verified character-identical against the
   contract afterwards.

The kernel verdict on the correctly assembled head is again delivered by CI,
not by this record.

## Kernel round 2 (rejected) — one proof gap, closed by the contract's own fallback

With the packaging defect fixed, the module elaborated for the first time and
the kernel reached the proofs. It rejected exactly one:

```
error: ResearchOS/Analysis/ThreeCircles.lean:402:73: unsolved goals
  ⊢ Real.log r₃ - Real.log r₂ = Real.log r₃ - Real.log r₁ - (Real.log r₂ - Real.log r₁)
```

This is the `e₁` step of TC10, where `field_simp` clears the denominators of
`(u - m)/(u - l) = 1 - (m - l)/(u - l)` and leaves a purely ring-shaped
residue. The contract had registered this exact risk as obligation TC-ALG and
recorded the fix in advance — "if `field_simp` leaves a `ring`-shaped residue,
append `ring`" — so the repair is that recorded fallback applied verbatim, and
the inline note now records that CI confirmed the residue rather than leaving
it as a hypothetical.

Ten of the eleven declarations drew no error, which is the first direct kernel
evidence about this package's proofs. No statement moved.
