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
| `RiemannMult.lean` | `../MULTIPLICITY_CONTRACT.md` (M1-M17, thirty-four declarations, no `sorry`; imports the built bridge, xi, and conjugation modules, all merged; synchronized with the RH-010 built module from its first import onward) | statement surface accepted 2026-08-07 (RH-009, `notes/reviews/RH009_MULT_CONTRACT_ACCEPTANCE_2026_08_07.md`, ACCEPT WITH APPLIED EDITORIAL FIXES, zero blocking); pre-kernel hardening pass walked all 34 proofs against the pin (zero WILL-FAIL verdicts, comment-only fallback upgrades, statements byte-frozen); the kernel verdict is delivered by CI on the RH-010 promotion change and is not claimed here |
| `MellinBound.lean` | `../MELLIN_BOUND_CONTRACT.md` (MB1-MB4, five declarations, no `sorry`; generic Mellin norm bounds, zero repo prerequisites) | reviewed 2026-08-07: statements verified character-identical by mechanical diff; every invoked API grep-verified at the pin; all nine registered obligations carried as inline fallbacks; verdict `LIKELY_ELABORATES` with zero fixes needed — the kernel verdict awaits a separate promotion change |
| `HarnackDisc.lean` | `../HARNACK_CONTRACT.md` (H1-H5, five declarations, no `sorry`; Harnack double inequality from the pinned Poisson representation) | reviewed 2026-08-07: statements character-identical; the root-level-vs-namespace mean-value trap the contract audit found is correctly handled in the draft; verdict `LIKELY_ELABORATES` with zero fixes needed — kernel verdict awaits a separate promotion change |
| `PolyLiouville.lean` | `../POLY_LIOUVILLE_CONTRACT.md` (L1-L5, five declarations, no `sorry`; polynomial-growth Liouville via the pinned n-indexed Cauchy estimate) | reviewed 2026-08-07: statements character-identical by mechanical diff; all eleven registered obligations carried as inline fallbacks including the HasSum/SummationFilter seam; verdict PASS with one comment-only locator fix — kernel verdict awaits a separate promotion change |
| `ThreeCircles.lean` | `../THREE_CIRCLES_CONTRACT.md` (TC1-TC11, one def and ten theorems, no `sorry`; annulus log-convexity via exp transport of the pinned three-lines endpoint form) | reviewed 2026-08-07: all eleven signatures character-identical; every claimed locator confirmed by reading the tree; verdict PASS with the file byte-unchanged — kernel verdict awaits a separate promotion change |
| `ZeroSetSlice.lean` | `../ZERO_SET_SLICE_CONTRACT.md` (23 declarations, no `sorry`; xi zero-set topology, finite divisor sums over an arbitrary compact, symmetry invariance — no cutoff shape anywhere) | statement surface accepted 2026-08-07 (RH-011); draft reviewed the same day: all 23 statements character-identical by mechanical diff, every consumed M-signature checked against the built merged `Mult.lean`, verdict ACCEPT with one comment-only fix; the kernel verdict awaits the RH-012 promotion change |
| `RiemannGrowthOrder.lean` | `../ENTIRE_ORDER_CONTRACT.md` (G0-G2 definitions plus L1-L6, nine declarations, no `sorry`) | the design-bearing definition was accepted 2026-08-07 (`notes/reviews/ENTIRE_ORDER_ACCEPTANCE_2026_08_07.md`), which unlocks exactly this transcription; draft reviewed: all nine blocks character-identical including docstrings, both HIGH obligations (polynomial order zero, order of a product) assembled in full from pinned ingredients rather than split, verdict `LIKELY_ELABORATES` with one comment-only fix; the kernel has not checked this file |


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
