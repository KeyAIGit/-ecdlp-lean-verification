# SELF-001 applicability audit against frozen PR #248

**Date:** 2026-07-25
**Frozen source:** `79295c0919d9d7605721495ad6d1e7ed274bafba`
**Scope:** read-only classification first, followed by an isolated hardening
branch. PR #248 itself was not changed while its independent review was running.

## Executive result

`SELF_001_RESULTS.md` falsified the implementation-independent oracle packet,
not the code in PR #248. Applying its attacks to the frozen implementation
produced a mixed result:

- portfolio enumeration, lifecycle immutability, terminal slot release,
  prerequisite completion, all-axis validator checks, and all-value positivity
  checks already resist the corresponding scratch-model attacks;
- three cross-layer defects reproduced against the real v0.2 implementation;
- generated fixpoint remained necessary but insufficient until canonical input
  digests were checked independently.

The defects did not authorize an experiment on the frozen branch because the
production lifecycle has zero candidates and zero owner decisions. They could,
however, admit or recommend a future malformed candidate once intake becomes
nonempty.

## Finding disposition

| SELF-001 finding | Frozen #248 disposition | Evidence |
|---|---|---|
| P0-1 / broken A-09 portfolio oracle | Not applicable to implementation | `optimize_portfolio` exhaustively compares feasible subsets; the 45% greedy-loss fixture returns the optimal portfolio. |
| P0-2 / crashes counted as detection | Scratch harness only | Repository tests use `unittest`; unexpected exceptions are errors and fail the suite. |
| P0-3 / global fixture contamination | Scratch harness only | Fixture constructors return fresh objects; `run_engine` deep-copies policy and snapshots. Forward and reverse test order both pass. |
| P0-4 / declared single-target with multi-target amortization | **Confirmed** | A reviewed-looking snapshot with `amortization.class=multi_target`, `target_count=1000000` had no gate and became `admissible` and `recommended`. |
| P0-5 / empty or partial independence accepted | Original bypass already prevented | All three axes must be true, all three evidence records must resolve, and source independence needs a separate human attester. Policy remains the explicit trust root. |
| P0-6 / candidate-id cache survives retargeting | Not reproduced | Lifecycle, decisions, calibration, and events bind candidate id, version, and snapshot digest. The engine has no gate cache keyed only by candidate id. |
| A-17 / idempotent or no-op generator | **Partially confirmed** | Fixpoint alone cannot prove source consumption. Existing ledger fidelity tests cover the prior superscript incident, but v0.2 canonical-input hashes were not independently checked by the acceptance gate. |
| A-19 / only first matrix size checked | **Confirmed across layers** | `[8, 2048]` passed lifecycle validation under a 16-bit toy ceiling and became `recommended`; the generation plane checked the list, but the reviewed constraint was discarded before lifecycle. |

## Root cause

The generation plane already emitted a quality-cleared draft containing:

- `cell_id`;
- typed-evidence digest;
- route and threat model;
- toy scope;
- mechanism, prediction, cost, and validator-design digests.

`build_research_engine_v02_state.py` copied only draft/proposal identities,
source commit, and five review digests into the lifecycle trust registry. It
dropped the scientific scope and all four contract digests.

That allowed a clean reviewed proposal to be reused as the wrapper around a
different lifecycle mechanism, cost model, route, or tested-size matrix.

## Isolated hardening

The follow-up branch binds lifecycle snapshots to the reviewed scientific
payload:

1. Preserve cell, typed evidence, route, threat model, toy scope, and contract
   digests in the quality-cleared binding.
2. Hash full mechanism, prediction, and cost contracts.
3. Hash the immutable validator design projection separately, allowing later
   implementation and independence evidence without changing the reviewed
   decisive claim or artifact contract.
4. Reject post-review payload drift.
5. Derive threat-model drift from any non-single-target amortization.
6. Check every declared tested size against the reviewed and lane toy ceiling.
7. Keep `specified_unproved` mechanisms out of lifecycle admissibility while
   still allowing them in non-executable proposal development.
8. Independently recompute lifecycle-policy and generation-state hashes in the
   acceptance checker, so a no-op generator cannot conceal canonical input
   changes.
9. Bind every `recommended` lifecycle event to a deterministic replay of the
   base portfolio under the frozen policy and immutable candidate snapshots.
   Merely declaring `actor_class: engine` is not recommendation evidence.
10. Reject a contradictory faithful-Petit/Weil statement even when the
    canonical corrective phrases remain elsewhere in the same registry.

## New mutation controls

- post-review cost-contract mutation;
- reviewed multi-target laundering under a single-target label;
- non-first tested size above the toy ceiling;
- schema-complete but unproved prose mechanism;
- route retargeting after review;
- no-op generated state after either canonical input changes;
- constant or self-referential snapshot digest;
- unsuccessful prerequisite and nonterminal outcome spoofing;
- shared-setup double charging and additive treatment of peak resources;
- constant expected-information-gain scoring;
- invalid canonical claim-disposition enum;
- a fabricated recommendation for a candidate outside the replayed portfolio;
- an appended claim that faithful Petit fails because Weil descent is absent.

## Final adversarial review integration

The independent read-only packet `RE-V0.2-FINAL-ADV-001` froze:

- main at `fed55d84675fd96e5f40204b9f5f49baa8c01172`;
- PR #248 at `79295c0919d9d7605721495ad6d1e7ed274bafba`;
- PR #249 at `3392a77c93a95fbd9bc40bceb1138f9485459e5e`.

It found no P0 implementation defect. Its three P1 findings were missing
mutation oracles around otherwise-correct code. This hardening branch closes
those oracle gaps without changing either frozen PR:

1. Two committed SHA-256 fixtures were calculated with a separate Node.js
   canonicalizer. Both the unit suite and the acceptance gate rederive them.
   Distinct anchors make a constant digest implementation fail.
2. Valid terminal `falsified` and `inconclusive` events cannot satisfy a
   `completed` dependency. A successful-looking outcome attached to a
   nonterminal event also cannot satisfy it.
3. Shared setup is asserted to be charged once per portfolio, while wall time,
   peak memory, and worker count are asserted to aggregate by maximum.
4. A numerical EIG anchor fails if scoring becomes constant.
5. The acceptance command now says that it validates references but does not
   execute the referenced tests.
6. The canonical claim enum is checked by the committed semantic and
   acceptance gates, not only by a unit test.
7. The final two agent audits identified bounded trust gaps beyond the packet:
   phrase-presence alone did not reject a simultaneously appended Petit/Weil
   contradiction, and a lifecycle event could self-label as an engine
   recommendation. Both now have deterministic negative controls.

The review judged PR #249 ready for an owner merge decision and recommended
landing it before rebasing #248. This branch records that recommendation but
does not merge, close, or rewrite either PR.

These controls test subtle variants of the invariant. They do not count a crash
as detection and do not claim that structural validation proves the truth of a
mathematical mechanism.

## Scientific boundary

This work changes research governance only.

- Experiments authorized: **0**
- Routes promoted: **0**
- Exact-target runs: **0**
- Historical outcome files changed: **0**
- Claim of ECDLP progress: **none**

The remaining semantic limit is explicit: hashes prove identity and review
continuity, not scientific truth. Scientific truth still requires the named
review roles, source inspection, independent replay where applicable, and the
Lean kernel for formal claims.
