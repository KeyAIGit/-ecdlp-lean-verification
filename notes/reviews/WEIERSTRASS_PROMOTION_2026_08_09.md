# Weierstrass package promotion record

Date: 2026-08-09

Scope: RH-020 promotion of the independently accepted W1–W12 surface from
`domains/riemann-hypothesis/drafts/WeierstrassFactors.lean` to the built,
domain-neutral module `ResearchOS/Analysis/WeierstrassFactors.lean`. The 28
`WF-*` rows in `VERIFIED_RESEARCHOS.md` cite this record.

## Review basis

1. RH-018 corrected and re-verified the contract mechanisms before any code was
   transcribed.
2. RH-019 transcribed exactly 28 public declarations and received two
   independent static reviews at historical draft SHA-256
   `fe34390369b02dc0eea9f318ba60f971ff1fc6e170634ecdacbda9823160a810`.
3. Promotion replay finds exactly 28 declarations: 2 definitions, 19 lemmas and
   7 theorems. The deliberately omitted
   `analyticOrderAt_fun_finsetProd` is still absent.
4. The accepted statement-record surface replays 28 of 28 with normalized
   SHA-256
   `5c1bbe331f63ae63bb31c88d80e2af6442562091a1996f799e132d254d62d735`.
5. The earlier contract scan covered nine names. RH-020 promotion replay checked
   all 28 root-level names against both the existing built `ResearchOS/`
   declarations and the exact pinned Mathlib source. No collision was found.
6. The Lean kernel, full build and axiom audits remain the sole promotion judge.

## Comment-only registry repair

The registry parser scans declaration-looking line starts without first
removing comments. A W5 doc-comment ended with the prose `theorem at the pin`,
which the parser would misread as a 29th declaration named `at`. RH-020 changes
only that prose to `result at the pin` in both the draft and built copy.

This edit changes no declaration, statement or proof. The repaired draft has
SHA-256
`8bf33f6dabfb333802cf305617f00777a3a8bfdd987899635e15b8c73016b5ba`
and Git blob `2e0d9bdd4bb5101936af9284fed1869c1bee3f10`. The historical
`fe3439…` hash remains the RH-019 review provenance rather than being silently
rewritten.

## Draft synchronization

The built module has a promotion-specific leading header. From its first
`import` through the final declaration it is byte-identical to the repaired
draft. The shared suffix SHA-256 is
`f96f0377cf412701fdac8f1bd954f84a6042f85c23e6c2895a5a5994ccd18a87`.

Any proof-only kernel repair must be applied to both copies and recorded here.
A changed name, binder, hypothesis or conclusion stops promotion and returns
the surface to contract review.

## Review priorities before the kernel verdict

- W4 has the most fragile finite-sum reindex and cast normalization.
- W8 has the longest locally uniform product inference.
- W12 has the most delicate subtype, finite-product and cardinality coercions.

These are expected elaboration seams, not permission to weaken a statement.

## Ledger and trust boundary

The promotion registers `WF-` in the existing `analysis-generic` lane and
adds one ledger row for each public declaration. Every row uses the standard
axiom base. The generated ResearchOS registry must report 172 rows and 173
declarations with complete inverse coverage; the combined declaration registry
must report 1176 declarations. Both generated axiom-audit surfaces and the
one-pass generated fixpoint must agree on the exact final tree.

The package remains generic fixed-finite-genus analysis:

- W7's `weierstrassProduct` is a totalized definition, not by itself a
  convergence theorem.
- W12's `Nat.card` is the multiplicity of one finite fibre at one point, not
  a global zero count or enumeration.
- The final not-top corollary is consumed under the same analytic hypotheses;
  that inequality alone is not an analyticity certificate.
- No declaration mentions zeta or xi, proves growth, selects a genus, proves a
  Hadamard factorization, selects a route or moves a barrier.

Accordingly this promotion closes no RH barrier, advances no RH barrier,
partially closes no RH barrier, and provides no evidence for or against the
Riemann Hypothesis.

## Governance

RH-020 remains ACTIVE in this promotion change. Only after merge may an exact
merged-head replay support a separate closure change. This promotion does not
edit the task queue, status snapshot, bundle manifest, capability map, routes or
barriers.

## Current verification state

Static replay on the assembled local tree confirms suffix identity, 28 public
declarations, fresh statement anchors, complete intended ledger coverage,
absence of the omitted 29th declaration, and a clean whitespace diff.
Isolated elaboration, the full build and both axiom audits are pending the
kernel round and must not be inferred from this record.
