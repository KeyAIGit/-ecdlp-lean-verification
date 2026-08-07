# DRAFT queue entries for the multiplicity/divisor package — NOT INSTALLED

Prepared 2026-08-07. This file is a **draft only**. Nothing here is installed in
`tasks/RIEMANN_HYPOTHESIS.md`; that file is out of scope for this round and is
not edited by this slab. When these entries are eventually installed, they go
**after `RH-008` and before `RH-005`**, matching the file's existing section
order (`RH-001`…`RH-004`, `RH-006`, `RH-007`, `RH-008`, then the parked
`RH-005`). Installing them also requires a dated line in the **Current
decision** block; that line must not move the ACTIVE slot.

Numbering continues the queue: the last used identifier is `RH-008`, so the
acceptance task is `RH-009` and the promotion task is `RH-010`.

**Queue invariant respected:** `RH-002` currently holds the single ACTIVE slot
(`tasks/RIEMANN_HYPOTHESIS.md:28`, status line `:122`), so **neither entry below
is marked ACTIVE**. Neither entry selects, unparks, or advances a route, and
neither makes or implies any claim about the truth of the Riemann Hypothesis.

Provenance used throughout: bridge PR #299 (`288d65b`), xi PR #304 (`afdae08`),
conjugation PR #307 (`c277b86`) — all merged and on current `main`. **PR #306
and PR #308 are CLOSED and UNMERGED and are never cited as provenance.**

Locators below were verified this session at Mathlib pin
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (`git -C
/workspace/leanprover-community/mathlib4 rev-parse HEAD`) and against the
repository working tree.

---

<!-- BEGIN RH-009 ENTRY (verbatim) -->

## RH-009: independent acceptance of the multiplicity/divisor statement surface

ID: `RH-009`

Status: **NOT ACTIVE — queued behind `RH-002`; acceptance-only, produces no
built module and no kernel verdict**

Kind: review

Blocking basis (2026-08-07): the RH queue — not
`repo/ECDLP_DECISION_SUBSTRATE.json`, which governs the ECDLP lane — is the
authority for this lane, and `RH-002` holds the sole ACTIVE slot for its
independent `PARK`/`PARK`/`PARK` disposition review with no route execution
authorized (`tasks/RIEMANN_HYPOTHESIS.md:28`, `:122`). The earlier pull request
carrying `MULTIPLICITY_CONTRACT.md` and `drafts/RiemannMult.lean` was blocked by
an independent reviewer and closed unmerged; the reviewer's ordering is that the
corrected contract returns as an **acceptance-only** change after `RH-002`
closes, with kernel promotion held back as a separate change (`RH-010`).
Activation of this task requires a dated queue decision at that point; this
entry is not that decision.

Provenance: every prerequisite of the surface is kernel-checked on current
`main` — the target bridge (PR #299, `288d65b`), the xi package (PR #304,
`afdae08`, supplying `riemannXi` and X11
`analyticOrderAt_riemannXi_eq_riemannZeta`,
repo:`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean:248`), and the
conjugation package (PR #307, `c277b86`, supplying
`analyticOrderAt_riemannZeta_conj` repo:`…/Conj.lean:440` and
`analyticOrderAt_riemannXi_conj` repo:`…/Conj.lean:452`). No statement waits on
an unmerged PR. PR #306 and PR #308 are CLOSED and UNMERGED and must not be
cited as provenance in the contract, the draft, the PR description, commit
metadata, or any review record.

Hypothesis: the corrected statement surface M1–M17 of
`domains/riemann-hypothesis/MULTIPLICITY_CONTRACT.md` — **exactly thirty-four
public signatures, each spelled explicitly in a `lean` block**, mirrored by the
thirty-four declarations of `domains/riemann-hypothesis/drafts/RiemannMult.lean`
— can be independently accepted at the pin without weakening, dropping, or
inventing a statement, with every dependency either pinned Mathlib or a
kernel-checked theorem on `main`.

Why it matters: acceptance of a statement surface is the only reviewable gate
that exists before elaboration. Static review is not a kernel verdict, and the
drafts lane is invisible to CI, so a package that is promoted without a prior
accepted surface has never been checked by anyone against anything. Separating
acceptance from promotion also keeps a statement change cheap: it is repaired in
review rather than discovered mid-promotion.

Inputs:

- `domains/riemann-hypothesis/MULTIPLICITY_CONTRACT.md` (draft v2)
- `domains/riemann-hypothesis/drafts/RiemannMult.lean` (non-built; its
  `drafts/README.md:30` row)
- `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:386`
  (`S1-MULTIPLICITY`) and `:389` (`S1-CONJ`)
- built modules on `main`: `…/RiemannHypothesis/TargetBridge.lean`,
  `…/Xi.lean`, `…/Conj.lean`
- pinned Mathlib at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0)

Expected output:

- one acceptance record under `notes/reviews/` (sibling precedents:
  `notes/reviews/RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`, and the
  `Acceptance note 2026-08-06` of `CONJ_SYMMETRY_CONTRACT.md`), carrying an
  explicit `ACCEPT`, `ACCEPT WITH APPLIED EDITORIAL FIXES`, or `REJECT`;
- a per-signature disposition covering all thirty-four signatures, including the
  four M15 specializations that a previous revision mandated in prose only and
  that are now spelled at `MULTIPLICITY_CONTRACT.md:1147`, `:1151`, `:1161`,
  `:1165` (`riemannXi_divisor_univ_conj`, `riemannXi_divisor_strip_conj`,
  `riemannXi_divisor_univ_one_sub_conj`, `riemannXi_divisor_strip_one_sub_conj`);
- corrections applied in place to the contract, the drafts mirror, and the
  `drafts/README.md` row;
- **by construction: no built module, no import added to `ResearchOS.lean`, no
  ledger row, no entry in `data/researchos_result_registry.json` or
  `data/result_registry.json`, no `VERIFIED_RESEARCHOS.md` line, no regenerated
  axiom audit, and no kernel verdict.**

Exit criteria:

- an independent reviewer records a disposition for every one of the
  thirty-four signatures; no signature is mandated in prose only;
- every `file:line` locator in the contract and the draft is replayed at the pin
  and against current `main`, and every mismatch is corrected or flagged;
- provenance cites only merged work (#299 `288d65b`, #304 `afdae08`, #307
  `c277b86`) and current `main`; no reference to PR #306 or PR #308 survives
  anywhere in the contract, the draft, the review record, the PR description, or
  commit metadata;
- no model identifier appears in the PR description, commit metadata, or any
  repository artifact touched by the change;
- `AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero` is cited with its true
  namespace and hypotheses — `Mathlib/Analysis/Analytic/Order.lean:687`, inside
  `namespace AnalyticOnNhd` (`:575`–`:700`), signature
  `[PreconnectedSpace 𝕜] {f : 𝕜 → E} (z : 𝕜) (hf : ∀ z₀, AnalyticAt 𝕜 f z₀) :
  analyticOrderAt f z = ⊤ ↔ f = 0` — so the analyticity hypothesis is
  everywhere-pointwise and the conclusion is global vanishing of `f`, not
  vanishing on a set; the unqualified spelling is rejected;
- every occurrence of "finite order" is replaced by **finite local analytic
  order** (`analyticOrderAt … ≠ ⊤`, M12) or **finite local meromorphic order**
  (`meromorphicOrderAt … ≠ ⊤`, the hypothesis consumed by
  `MeromorphicNFOn.zero_set_eq_divisor_support`); no phrasing may be read as a
  growth order of an entire function;
- the accepted surface claims only pointwise local finiteness (M12, M16′) and
  divisor-support/zero-set equality (M13, M16″); **no statement, note, or annex
  claims that the ξ or ζ divisor support is infinite**, and none claims local
  finiteness of the zero set beyond what the pinned lemmas give;
- the record states in terms that cannot be misread that it is **not** a kernel
  verdict: `drafts/RiemannMult.lean` lies outside every lake target
  (`lakefile.toml:2` declares `defaultTargets = ["Ecdlp", "ResearchOS"]`), the
  build step `.github/workflows/ci.yml:420` runs `lake build` over those targets
  only, and the no-incomplete-proof scan at `:359` covers only `Ecdlp.lean`,
  `Ecdlp/`, `ResearchOS/`, `ResearchOS.lean`; therefore a green CI run on this
  change says nothing about the draft;
- no barrier row is changed: acceptance of a statement surface closes neither
  `S1-MULTIPLICITY` nor the divisor-invariance half of `S1-CONJ`, and the
  capability map is not edited to suggest otherwise;
- no `sorry`, `admit`, custom axiom, new `def`, or unreviewed assumption appears
  in the accepted surface; the package remains free of enumeration, counting,
  growth, Hadamard products, Li coefficients, and zero-simplicity claims;
- the change carries no promotion; if the reviewer's fixes alter any statement,
  the altered statement is re-accepted here rather than carried into `RH-010`;
- rejection or partial acceptance is retained as a scoped negative result (for
  example the M12 death condition: if the S1M-FIN obligation resists every
  recorded route, M13 is dropped and the divisor block is reduced, never
  hypothesis-floated to the caller and called an exit);
- no route is selected or unparked, and no claim about the truth of RH is made
  or implied.

Files allowed to edit:

- `domains/riemann-hypothesis/MULTIPLICITY_CONTRACT.md`
- `domains/riemann-hypothesis/drafts/RiemannMult.lean` and
  `domains/riemann-hypothesis/drafts/README.md`
- a new curated record under `notes/reviews/`
- `tasks/RIEMANN_HYPOTHESIS.md`

Files that must not be edited:

- `ResearchOS/`, `ResearchOS.lean`, `Ecdlp/`, `Ecdlp.lean`
- `data/researchos_result_registry.json`, `data/result_registry.json`,
  `VERIFIED.md`, `VERIFIED_RESEARCHOS.md`, and generated views
- `lakefile.toml`, `lake-manifest.json`, `.github/workflows/`
- `repo/ECDLP_DECISION_SUBSTRATE.json` and ECDLP experiment authorizations

How to verify:

- independent mathematical review of all thirty-four signatures against the pin;
- replay every locator with `rg` at
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` and on current `main`;
- run `python3 scripts/check_domains.py` and
  `python3 scripts/check_repo_artifacts.py`;
- confirm the diff adds no file under a lake target, changes no registry, ledger
  or audit artifact, and leaves `ResearchOS.lean` untouched;
- confirm the diff and its commit metadata contain no model identifier and no
  reference to PR #306 or PR #308.

<!-- END RH-009 ENTRY -->

---

<!-- BEGIN RH-010 ENTRY (verbatim) -->

## RH-010: multiplicity/divisor package promotion after contract acceptance

ID: `RH-010`

Status: **NOT ACTIVE — BLOCKED on `RH-009` acceptance; kernel promotion only,
opened as its own change**

Kind: theorem

Blocking basis (2026-08-07): the reviewer requires independent acceptance of the
statement surface and the built promotion to be **two separate changes**, in
that order — the path the bridge took (acceptance-free foundation, PR #299
`288d65b`), the xi package took (acceptance PR #303 `202eba0`, then promotion PR
#304 `afdae08`), and the conjugation package took (acceptance PR #301 `7bf13ab`,
then promotion PR #307 `c277b86`). This task is blocked until `RH-009` records
an acceptance, and it may only be activated by a dated queue decision at that
point; `RH-002` holds the sole ACTIVE slot until it closes
(`tasks/RIEMANN_HYPOTHESIS.md:28`, `:122`). An acceptance change must not carry
this promotion, and this task must not re-open statement questions: any needed
statement change returns to `RH-009`.

Hypothesis: the surface accepted under `RH-009` can be represented in Lean and
kernel-checked **without changing a single accepted statement** and without
expanding the trusted base — module plus one ledger row per public declaration
plus regenerated registry and axiom audit plus promotion review in one change,
with the verdict delivered by CI.

Why it matters: static review of the drafts lane is source reading only; CI does
not elaborate `drafts/RiemannMult.lean`. Until a built promotion is green, no
statement of this package counts as proved under the one invariant, and neither
the `S1-MULTIPLICITY` exit evidence nor the divisor half of `S1-CONJ` has any
kernel support.

Inputs:

- the `RH-009` acceptance record and the accepted
  `MULTIPLICITY_CONTRACT.md` surface (M1–M17, thirty-four signatures)
- `domains/riemann-hypothesis/drafts/RiemannMult.lean`
- built `…/RiemannHypothesis/TargetBridge.lean`, `…/Xi.lean`, `…/Conj.lean` on
  `main`
- pinned Mathlib at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0)

Expected output:

- one built module
  `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean` importing the
  built xi and conjugation modules directly, plus its import line in
  `ResearchOS.lean`;
- a drafts-lane mirror byte-identical from its first `import` to end of file;
- one `RH-MULT-*` ledger row per public declaration with its declared axiom
  base, complete inverse registry coverage, and regenerated
  `ResearchOS/LedgerAxiomAudit.lean`, `data/researchos_result_registry.json`,
  and `VERIFIED_RESEARCHOS.md`;
- a promotion review record under `notes/reviews/`;
- only those capability-map and RH-queue updates the kernel outcome actually
  supports.

Exit criteria:

- on the exact merged head: `lake build` is green
  (`.github/workflows/ci.yml:420`), the no-incomplete-proof scan is green
  (`:359`), and both axiom audits are green (`:428` ECDLP lane, `:438`
  ResearchOS per-row lane);
- no `sorry`, `admit`, custom axiom, or `native_decide` extension of the trusted
  base; every ledger row carries axiom base `standard`;
- every public declaration of the module has a ledger row and inverse registry
  coverage; the counts agree with the accepted surface;
- **no statement deviates from the accepted surface.** A weakened hypothesis, an
  added or dropped signature, a renamed carrier, a new `def`, or a changed
  carrier set stops promotion and returns the change to `RH-009` for
  re-acceptance; proof-only repairs (term shapes, tactic choices, elaboration
  order) stay inside this task and are recorded in the promotion review;
- the promotion review records what the kernel outcome supports and no more:
  whether the ζ/ξ divisor interface and the multiplicity-preserving divisor
  symmetries named as remaining `S1-MULTIPLICITY` exit evidence
  (`MATHLIB_CAPABILITY_MAP.md:386`) are now kernel-checked, and whether the
  divisor-invariance half of `S1-CONJ` (`:389`) is discharged. This entry
  asserts no barrier closure in advance; a barrier row moves only on the
  reviewed evidence of the merged head, and generic pinned Mathlib never retires
  a row on its own;
- the established content is stated exactly: pointwise local finiteness of the
  analytic/meromorphic order (M12, M16′) and equality of divisor support with
  the zero set (M13, M16″). No record claims that the ξ or ζ divisor support is
  infinite, and no phrase reads as a growth order;
- failure of any gate is retained as a scoped negative result, with the blocking
  obligation named; a clean blocker is preferable to a promotion that quietly
  edits what was accepted;
- no route is selected or unparked; the promotion changes named-blocker
  bookkeeping only, and makes no claim about the truth of RH.

Files allowed to edit:

- `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean` (new),
  `ResearchOS.lean`, `ResearchOS/LedgerAxiomAudit.lean`
- `data/researchos_result_registry.json`, `VERIFIED_RESEARCHOS.md`
- `domains/riemann-hypothesis/drafts/RiemannMult.lean`,
  `domains/riemann-hypothesis/drafts/README.md`,
  `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md`
- a new curated record under `notes/reviews/`
- `tasks/RIEMANN_HYPOTHESIS.md`

Files that must not be edited:

- `MULTIPLICITY_CONTRACT.md`'s accepted statement blocks (a needed change sends
  the work back to `RH-009`)
- `Ecdlp/`, `Ecdlp.lean`, `data/result_registry.json`, `VERIFIED.md`
- `lakefile.toml`, `lake-manifest.json` (no Mathlib bump), `.github/workflows/`
- `repo/ECDLP_DECISION_SUBSTRATE.json` and ECDLP experiment authorizations

How to verify:

- CI on the exact merged head: full build, no-incomplete-proof scan, ECDLP axiom
  audit, ResearchOS per-row axiom audit;
- `python3 scripts/check_axioms.py researchos_axiom_audit.txt
  data/researchos_result_registry.json`, plus
  `python3 scripts/check_domains.py` and
  `python3 scripts/check_repo_artifacts.py`;
- an independent reviewer diffs every promoted signature against the accepted
  contract text and confirms character-level agreement;
- confirm the drafts mirror is byte-identical to the built module from the first
  `import` to end of file;
- confirm the diff and its commit metadata contain no model identifier and no
  reference to PR #306 or PR #308.

<!-- END RH-010 ENTRY -->

---

## Why neither entry is ACTIVE

`RH-002` still holds the queue's single ACTIVE slot for its independent
disposition review (`tasks/RIEMANN_HYPOTHESIS.md:28`, `:122`), so `RH-009` is
queued behind its closure and `RH-010` is blocked behind `RH-009`; marking
either ACTIVE would break the one-ACTIVE-task invariant and would read as
authorization this queue has not given.
