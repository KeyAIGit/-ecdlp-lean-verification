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
| `RiemannXi.lean` | `../XI_PACKAGE_CONTRACT.md` (X1-X11, twelve declarations, no `sorry`; imports the built bridge explicitly and is synchronized with the RH-007 built module from its first import onward) | kernel-verified through the synchronized built counterpart in merged PR #304 (`afdae08`): the first full build exposed the X11 composition-call risk, `DifferentiableAt.fun_comp' z` was synchronized into contract, draft, and built module, and the repaired head passed the full build plus both axiom audits; statements and claim boundaries are unchanged |
| `RiemannConj.lean` | `../CONJ_SYMMETRY_CONTRACT.md` (Z1-Z9, sixteen declarations, no `sorry`; imports the built bridge and the built xi module explicitly and is synchronized with the RH-008 built module from its first import onward) | statement surface accepted in merged PR #301 (`7bf13ab`, including the corrected F1 sign); re-reviewed under three independent lenses before promotion, then kernel-verified through the synchronized built counterpart on the green RH-008 promotion head; statements and claim boundaries are unchanged |
| `RiemannMult.lean` | `../MULTIPLICITY_CONTRACT.md` (M1-M17, thirty-four declarations, no `sorry`; imports the built bridge, xi, and conjugation modules — all three are now merged) | current static verdict `LIKELY_ELABORATES`, 2026-08-06: two-lens adversarial review (statement fidelity and API existence; mathematical soundness and elaboration mechanics) at the pin, zero S0/S1 findings, three S2 findings applied — the open-strip `IsOpen` witness switched to the kernel-green `.and` form used by the built xi module, and `Iff.rfl` fallbacks registered at three conjugation-stability sites; all thirty contract code-block statements verified character-identical by mechanical comparison, the remaining four being the `Set.univ`/strip instances the contract mandates in prose; **the contract itself has not yet been independently accepted and the kernel has not checked this file** — promotion is blocked on both |

Promotion invariant: after independent contract acceptance, a draft moves to
the built surface only together with its `RH-*` ledger rows, registry entries,
generated audit lines, and promotion review in the same PR; inverse coverage
fails CI otherwise. The bridge completed this path in PR #299. The xi package
has satisfied both its RH-006 source gate and its explicit independent
statement acceptance. Its separate built promotion completed in PR #304 with
the exact synchronized body, ledger coverage, full build, and both axiom
audits green.
