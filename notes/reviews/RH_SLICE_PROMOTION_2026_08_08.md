# RH zero-set slice package promotion record (RH-012)

Date: 2026-08-08

Scope: promotion of the independently accepted 23-signature statement surface
of `domains/riemann-hypothesis/ZERO_SET_SLICE_CONTRACT.md` into the built
module `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/ZeroSetSlice.lean`.
This record is cited by the twenty-three `RH-SLICE-*` rows in
`VERIFIED_RESEARCHOS.md`.

## What this is NOT, first

This is the RH-lane package a reader is most likely to over-read, so the limits
go before the content.

- **No zero is located.** Nothing here exhibits a zero of ξ, or of ζ, anywhere.
- **No zero is counted.** There is no counting function, no `N(T)`, no
  zero-density estimate, and no asymptotic of any kind.
- **Nothing asserts that the zero set is infinite, or even nonempty.** Every
  one of the twenty-three statements is satisfied by a function with no zeros
  at all. "Countable" and "meets every compact in a finite set" are UPPER
  bounds on how many zeros there can be, not lower bounds. An earlier review of
  this lane caught exactly this overclaim in a different artifact; it must not
  return through this one.
- **No zero-free region, and nothing about the critical line.** The composite
  map `s ↦ 1 − conj s` appears, and its fixed-point set is the critical line,
  but no statement here says anything about that line.
- **No route is selected.** The divisor sums are over an ARBITRARY compact `K`
  and an ARBITRARY region `U`. No cutoff shape, contour, window family, or test
  function is chosen, so nothing here presupposes or nudges toward Route A, B
  or C — all three of whose `PARK` dispositions remain CONFIRMED.

## Review basis

1. **Independent statement acceptance (RH-011).** The 23-signature surface was
   accepted 2026-08-07 by a three-lens panel with zero blocking items; record
   `notes/reviews/RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`.
2. **Prerequisites merged and kernel-checked on `main`.** The target bridge
   (PR #299), the xi package (PR #304), the conjugation package (PR #307), and
   the multiplicity/divisor package (PR #313). Block N consumes M9-M15 from the
   last of these directly; the module imports the xi and multiplicity modules.
3. **Draft review provenance.** The promoted body is the drafts-lane file
   reviewed 2026-08-07: all 23 statements character-identical by mechanical
   diff, every consumed `M`-signature checked against the built merged
   `Mult.lean`, verdict ACCEPT with one comment-only fix.
4. **Statement identity re-verified at promotion time**, byte-exact against the
   contract's canonical blocks with whitespace not normalised: 23 of 23.
5. **Name-collision scan.** All 23 checked against pinned Mathlib and against
   every declaration already built under `ResearchOS/`: no collision.
6. **Kernel check.** Delivered by CI on this promotion change: `lake build`,
   the no-incomplete-proof gate, the regenerated
   `ResearchOS/LedgerAxiomAudit.lean` + `check_axioms.py` at axiom base
   `standard`, and `gen_researchos_registry.py --check` for inverse coverage.

## Load-bearing checks

- **Well-definedness lands before the sums.** `N1.2` (`RH-SLICE-N12`) proves
  the `finsum` over a compact equals the honest finite `Finset` sum over the
  finite intersection from `RH-SLICE-D8`. Every later Block N row is therefore
  about a real value and not about a totalization junk value.
- **The divisor carrier is Mathlib's own.** `MeromorphicOn.divisor`, untop-zero
  totalized. The discreteness and finiteness rows (D7A-D9) are statements about
  that carrier, and the support identifications inherited from the merged
  multiplicity package are what connect it to the zero set — in that order, so
  "not a zero" can never be conflated with "identically zero nearby".
- **The symmetry rows transport, they do not discover.** Each of `N1.6`-`N1.8`
  assumes `U` is symmetric under the relevant map and concludes the divisor sum
  is unchanged. The symmetry of the divisor itself is the merged multiplicity
  and conjugation packages' result, already ledgered; nothing new about the
  zeros is proved here.
- **Block E is pure set theory.** The three `image_*_of_symm` identities
  mention no ξ, no ζ and no divisor.

## Barrier effect

On a green merge this **advances the `S1-GLOBAL-ZEROS` bookkeeping and does NOT
close it**, exactly as `RH-012`'s exit criteria state. That barrier asks for
global zero counting; compact-by-compact finiteness is not global counting. No
other barrier moves. **This promotion change does not edit the capability map
and does not touch the RH queue**: `RH-012` is not complete until the full gate
battery passes on the exact merged head, so recording its completion, the dated
capability-map addendum, and the successor ACTIVE task all belong to a separate
follow-up change — the pattern the RH-010 promotion (PR #313) followed.

## Draft synchronization

The built module and `domains/riemann-hypothesis/drafts/ZeroSetSlice.lean` are
byte-identical from the first `import` through end of file, differing only in
their leading status header. A proof-only kernel repair must be applied to both
copies before a new CI run; a statement change stops promotion and returns the
surface to contract review.

## Claim boundary

Once and only once the exact merged head passes every gate: what exists is
twenty-three statements about the topology of the ξ zero set and about divisor
sums over arbitrary compacts. This proves, disproves, advances, and evidences
**nothing about the truth of the Riemann Hypothesis**, in either direction.
