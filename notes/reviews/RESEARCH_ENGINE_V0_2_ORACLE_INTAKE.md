# Research Engine v0.2 independent-oracle intake

Date: 2026-07-25

This note records how the implementation-independent review packet was
used. It is an adoption record, not a replacement for repository validators.

## Bound review artifact

- Artifact name: `RE_V0_2_ORACLE_PACKET.md`.
- SHA-256:
  `0305d148e5afdb99dafdb79b09d38c6666188455960fb516a1ce9c56b416b9f3`.
- Reviewed baseline: protected `main` at
  `fed55d84675fd96e5f40204b9f5f49baa8c01172` and the then-remote PR #248
  head `7acd78fb263d640538e8f29aa6b63a4820fd20b6`.
- Boundary: the packet did not review the later implementation diff and
  authorizes no experiment, route promotion, or exact-target work.

## Findings adopted

1. Historical provenance has two different invariants. The canonical JSON
   review root remains
   `d9de2351a499d395d09005199aac73744c1bf212ff9759ceed5d229d076ca7a3`;
   each of the eight files also has a separately pinned raw-byte digest.
2. `claim_disposition` and `assurance` are independent. The GLV covariance
   package is kernel-checked; exhaustive coordinatewise classification is
   certificate-replayed; the independent-cube child is bounded negative; the
   parent route remains `open_parked`.
3. Faithful prime-field Petit is not Weil descent. Historical P4 implemented
   neither PKC 2016 construction and remains an inconclusive toy result.
4. Kudo et al. CANS 2018 remains `full_text_unread`. An abstract or secondary
   account cannot decide its exact symmetry or support a novelty claim.
5. Fixed curve-automorphism order is not the correct cost discriminator. A
   cost contract must study the coordinatewise subgroup that preserves the
   relation as a function of arity, while pricing recovery and every non-orbit
   lever separately.
6. Quality clearance, recommendation, and dated owner authorization are
   separate lifecycle states. Zero retention is a successful cycle.
7. Silent truncation is forbidden. Seed and portfolio overflows produce
   deterministic coverage artifacts.
8. Proposal fluency is not a mechanism check. The generation plane now
   requires structured mechanism, prediction, full-cost, and validator-design
   contracts in addition to its human-readable explanation.
9. Validator independence is split into path, artifact, and source axes.
   A ready validator must bind registered evidence for all three; the source
   axis requires a third-party human attester. A design-only validator cannot
   claim independence or clear the lifecycle gate.
10. Five passing reviews produce a digest-bound, non-executable draft. A
    mechanism, validator, or bounded-experiment candidate must bind that exact
    registered draft before lifecycle evaluation; the binding still does not
    authorize execution.

## Reconciliation with the owner contract

The packet stated that the owner's nineteen cases were unavailable in the
reviewed Git trees. They were supplied in the owner task, outside those
baseline commits. The authoritative implementation mapping is therefore
`repo/RESEARCH_ENGINE_V0_2_ACCEPTANCE.json`, which records the exact nineteen
owner cases and retains the packet's additional oracles as supplements.

The packet's literature tables remain evidence-typed:

- `CONFIRMED_PRIOR_ART` requires inspected primary text.
- `COULD_NOT_VERIFY` and `NOT_FOUND_IN_SOURCES_CHECKED` are not novelty.
- conflicting access reports for PKC 2016 were resolved by the official IACR
  archive PDF; failure through Springer or an aggregator is not source
  unavailability.

## Deliberately not adopted as an automatic rule

- No model-authored prose clears a scientific gate merely because it is
  nonempty.
- No lexical fingerprint is treated as semantic deduplication.
- No finite-group-order heuristic is treated as a solving-degree theorem.
- No certificate-backed exhaustiveness claim is relabelled `lean_kernel`.
- No absence from the current corpus is treated as a new mechanism.

The implementation remains subject to final diff review, generated-fixpoint
replay, Lean verification, and current CI. This intake note is not itself a
review verdict.
