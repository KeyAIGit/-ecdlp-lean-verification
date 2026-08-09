# TASK-029 proposal provenance context

Proposal: `HGP-M16-SOLVER-SLOPE-002`

Current seed: `HGS-3266E42A729C`

Typed evidence digest:
`602d93c115099c81f02b8a8ac531e33036e6988d5d3ddf2ec257b1118e5cd75d`

Protected-main source commit:
`bc2f04a71d168b34bce3d68c1d7cef33b4af9e4e`

Canonical generation instruction:

> Follow the KeyAI ECDLP research contracts. Formulate and review the
> current-seed HYP-M16-SOLVER-SLOPE-001 desk proposal using the exact TASK-028
> source mechanism and recovery boundary. Preserve the previously declared
> mechanism identity when it has not changed, expose duplicate and novelty
> failures, and return an exact symbolic size and cost bridge or a scoped
> blocker. Do not execute a solver, request compute, rerun a prior experiment,
> target secp256k1, move a route, or claim a complexity improvement.

The proposal `prompt_sha256` is the SHA-256 of the UTF-8 bytes inside the
blockquote after removing the Markdown quote prefixes and joining the lines
with one ASCII space.

The proposal `context_sha256` is the SHA-256 of the UTF-8 string formed by
sorting its `evidence_manifest` by path and joining `path + ":" + sha256`
records with a newline.

The baseline `implementation_digest` is the SHA-256 of the literal UTF-8
sentinel
`UNIMPLEMENTED-DESIGN-ONLY:source-system4-literal-chain-and-matched-plain-controls`.
It identifies no executable bytes.

## Intake boundary

This package answers only the current seed. It does not supersede or alter the
immutable historical proposal `HGP-M16-SOLVER-SLOPE-001`.

The old and current packages intentionally declare the same seven-field
mechanism identity because TASK-028 refined the evidence and recovery boundary,
not the proposed cost-changing mechanism. Duplicate-mechanism detection and
any lexical near-duplicate finding are therefore expected scientific blockers,
not defects to evade by renaming fields.

The proposal is a zero-compute desk abstention. Its evidence manifest is
restricted to files present at the repository's frozen scientific-provenance
anchor. The current seed and TASK-028 refinements come from the current typed
state and design review; the newer TASK-028 files are deliberately not
misrepresented as source-commit-bound evidence. This directory is design
provenance and is not itself evidence for the mechanism.
