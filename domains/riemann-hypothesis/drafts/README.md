# Non-built Lean drafts (RH lane)

Status: **drafts only — nothing here is built, imported, or claimed proved.**

Files in this directory are Lean source drafts of frozen RH-lane theorem
contracts, prepared so each eventual kernel-checked promotion change is a
mechanical promotion rather than fresh authoring. They are intentionally
outside every lake target (`lakefile.toml` declares
`defaultTargets = ["Ecdlp", "ResearchOS"]` and the two `lean_lib` roots of the
same names; no file in this directory is under either), outside the no-sorry
gate's scan surface, and outside the result registries. **CI does not elaborate
the files in this directory as they stand** — no workflow builds or typechecks
this path, so the Lean kernel has NOT checked them and no future CI run will
check them until a promoted copy is placed under a lake target by a separate
promotion change. Any review verdict recorded below is static reading, never
CI evidence.

Authority for this lane is the RH queue `../../../tasks/RIEMANN_HYPOTHESIS.md`,
whose current dated decision keeps `RH-002` as the sole ACTIVE task with no
route selected; `repo/ECDLP_DECISION_SUBSTRATE.json` governs the ECDLP lane and
is not the authority here. A draft in this directory is an offered artifact
prepared for later independent review — never an active task, and never
authorization to work a route.

| draft | implements | adversarial review |
|---|---|---|
| `RiemannTargetBridge.lean` | `../TARGET_BRIDGE_CONTRACT.md` (P1-P5, no `sorry`; synchronized with the RH-004 built module) | kernel-verified through its synchronized built counterpart in merged PR #299 (`288d65b`): the first round exposed the registered P1-d witness-cast risk, the explicit `Int.cast_natCast` repair was synchronized into contract, draft, and built module, and the final full build plus both axiom audits passed; statements and claim boundaries are unchanged |
| `RiemannXi.lean` | `../XI_PACKAGE_CONTRACT.md` (X1-X11, twelve declarations, no `sorry`; imports the built bridge explicitly and is synchronized with the RH-007 built module from its first import onward) | kernel-verified through the synchronized built counterpart in merged PR #304 (`afdae08`): the first full build exposed the X11 composition-call risk, `DifferentiableAt.fun_comp' z` was synchronized into contract, draft, and built module, and the repaired head passed the full build plus both axiom audits; statements and claim boundaries are unchanged |
| `RiemannConj.lean` | `../CONJ_SYMMETRY_CONTRACT.md` (Z1-Z9, sixteen declarations, no `sorry`; imports the built bridge and the built xi module explicitly and is synchronized with the RH-008 built module from its first import onward) | statement surface accepted in merged PR #301 (`7bf13ab`, including the corrected F1 sign); re-reviewed under three independent lenses before promotion, then kernel-verified through the synchronized built counterpart promoted in merged PR #307 (`c277b86`), which is on `main` and imported from `ResearchOS.lean`; statements and claim boundaries are unchanged |
| `RiemannMult.lean` | `../MULTIPLICITY_CONTRACT.md` (M1-M17, thirty-four declarations, no `sorry`; imports the built bridge (RH-004, PR #299), the built xi module (RH-007, PR #304) and the built conjugation module (RH-008, PR #307, `c277b86`) — all three are merged and on `main`, so no statement here waits on an unmerged PR) | current static verdict `LIKELY_ELABORATES`, 2026-08-06: two-lens adversarial review (statement fidelity and API existence; mathematical soundness and elaboration mechanics) at the pin, zero S0/S1 findings, three S2 findings applied — the open-strip `IsOpen` witness switched to the kernel-green `.and` form used by the built xi module, and `Iff.rfl` fallbacks registered at four conjugation-stability sites
(`riemannXi_divisor_strip_conj`, `riemannXi_divisor_strip_one_sub_conj`,
`riemannZeta_divisor_strip_conj`, `riemannZeta_divisor_strip_one_sub_conj`); all thirty-four contract code-block statements — including the four M15 `Set.univ`/strip specializations the contract now spells explicitly rather than in prose — verified character-identical by mechanical comparison (34 on each side, zero mismatches); that verdict is static reading only — **CI does not elaborate this file, the kernel has not checked it, and the contract itself has not yet been independently accepted**. This draft is an offered artifact, not an active task |

Promotion invariant: independent acceptance of a contract's statement surface
and the later kernel promotion of its draft are SEPARATE steps carried by
SEPARATE pull requests, and acceptance never implies promotion. Acceptance is a
review step with no kernel content; only afterwards may a draft move to the
built surface, and then only together with its `RH-*` ledger rows, registry
entries, generated audit lines, and promotion review in the same PR — inverse
coverage fails CI otherwise. The bridge completed this path in PR #299. The xi
package has satisfied both its RH-006 source gate and its explicit independent
statement acceptance. Its separate built promotion completed in PR #304 with
the exact synchronized body, ledger coverage, full build, and both axiom
audits green. The conjugation package took its statement acceptance in PR #301
and its separate built promotion in PR #307 (`c277b86`), now on `main`.
