# Non-built Lean drafts (RH lane)

Status: **drafts only — nothing here is built, imported, or claimed proved.**

Files in this directory are Lean source drafts of frozen RH-lane theorem
contracts, prepared so each eventual kernel-checked promotion change is a
mechanical promotion rather than fresh authoring. They are intentionally
outside every lake target (`lakefile.toml` builds only the `Ecdlp` and
`ResearchOS` roots), outside the no-sorry gate's scan surface, and outside
the result registries. The Lean kernel has NOT checked them.

| draft | implements | adversarial review |
|---|---|---|
| `RiemannTargetBridge.lean` | `../TARGET_BRIDGE_CONTRACT.md` (P1-P5, no `sorry`; synchronized with the RH-004 built module) | kernel-verified through its synchronized built counterpart in merged PR #299 (`288d65b`): the first round exposed the registered P1-d witness-cast risk, the explicit `Int.cast_natCast` repair was synchronized into contract, draft, and built module, and the final full build plus both axiom audits passed; statements and claim boundaries are unchanged |
| `RiemannXi.lean` | `../XI_PACKAGE_CONTRACT.md` (X1-X11, twelve declarations, no `sorry`; imports the built bridge explicitly and is synchronized with the RH-007 promotion candidate from its first import onward) | statement surface independently accepted 2026-08-06 (`notes/reviews/RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`); static verdict remains `LIKELY_ELABORATES`: ~40 cited declarations verified at the pin, sign chain independently re-derived, X6 zero-set split exact, X11 factorization restricted to the open strip; registered elaboration risks remain pending the promotion PR's kernel and axiom CI |

Promotion invariant: after independent contract acceptance, a draft moves to
the built surface only together with its `RH-*` ledger rows, registry entries,
generated audit lines, and promotion review in the same PR; inverse coverage
fails CI otherwise. The bridge completed this path in PR #299. The xi package
has satisfied both its RH-006 source gate and its explicit independent
statement acceptance. Its separate built promotion is in progress and is not
counted unless the exact synchronized body passes kernel and axiom CI.
