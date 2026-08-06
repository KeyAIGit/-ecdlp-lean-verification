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
| `RiemannXi.lean` | `../XI_PACKAGE_CONTRACT.md` (X1-X11, all theorem bodies present and no `sorry`, but kernel-unchecked; depends on the sibling bridge draft — X10 uses bridge P2, so it can elaborate only with the bridge module in scope, as the header states) | current static verdict `LIKELY_ELABORATES`, 2026-08-06: ~40 cited declarations verified at the pin, no hallucinated names, sign chain independently re-derived (correct), X6 zero-set split exact, X11 factorization asserted only on the open strip; the initial `NEEDS_FIXES` findings were applied (the leaked transmission-preamble line was stripped, the misleading X5 placeholder removed, and X11 `Gammaℝ` differentiability now exposes the product via `suffices` in the pin's own idiom); remaining findings are registered fallback-grade obligations, and built promotion remains blocked until actual elaboration |

Promotion path: `S0-TRUST` closure (completed by PR #298, `d6e146fa`) →
RH-003 independent review of the contract → RH-004 built PR moves this file (or a reviewed
equivalent) into the built surface with its `RH-*` ledger row, registry
entry, and audit line in the same PR — the inverse-coverage gate fails CI
otherwise.
