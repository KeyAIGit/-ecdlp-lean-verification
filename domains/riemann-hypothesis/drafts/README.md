# Non-built Lean drafts (RH lane)

Status: **drafts only — nothing here is built, imported, or claimed proved.**

Files in this directory are Lean source drafts of frozen RH-lane theorem
contracts, prepared so the eventual kernel-checked PR (RH-004) is a
mechanical promotion rather than fresh authoring. They are intentionally
outside every lake target (`lakefile.toml` builds only the `Ecdlp` and
`ResearchOS` roots), outside the no-sorry gate's scan surface, and outside
the result registries. The Lean kernel has NOT checked them.

| draft | implements | adversarial review |
|---|---|---|
| `RiemannTargetBridge.lean` | `../TARGET_BRIDGE_CONTRACT.md` (P1-P5, all obligations resolved, no `sorry`) | verdict `LIKELY_ELABORATES`, 2026-08-05: all 30 cited declarations verified at the pin with exact signatures and binder structure; the P1-c π-cancellation checked symbolically by hand (correct); division-by-zero audit clean; no Iff direction mixups; five S2 findings, all fallback-grade (the push_cast witness cast is the least mechanical step; verified alternates are recorded inline as comments) |

Promotion path: `S0-TRUST` closure (completed by PR #298, `d6e146fa`) →
RH-003 independent review of the contract → RH-004 built PR moves this file (or a reviewed
equivalent) into the built surface with its `RH-*` ledger row, registry
entry, and audit line in the same PR — the inverse-coverage gate fails CI
otherwise.
