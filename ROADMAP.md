# ROADMAP — the one strategy document

> Replaces `WORK_SCOPE.md`, `ENVIRONMENT_PLAN.md`, `PLATFORM_STRATEGY.md`,
> `DIRECTOR_CHARTER.md`, and `notes/V0_COMPLETION_PLAN.md` (all preserved under
> `archive/docs/`). Those five files held four different north stars; drift between
> them was itself a defect. From here on: **one strategy file**. Live numbers stay in
> `STATUS.md`; the active queue stays in `tasks/NEXT.md`; this file is direction and
> structure only. Exact route and foundation decisions live in
> `repo/ECDLP_DECISION_SUBSTRATE.json`.

## 1. Position — what this repository actually is (auditor's honest read)

A whole-repository audit (2026-07, three independent inventory passes + gate runs +
CI history) found a project whose **object layer is stronger than its meta layer**:

- **Real and durable:** the Lean library. The current module count is generated in
  `STATUS.md`; the built surface has 0 `sorry` and 0 custom
  axioms, machine-enforced. Several results are first-in-Lean and externally
  valuable: the Semaev summation polynomials `S₃`/`S₄`, the division-polynomial /
  torsion-disjointness ladder, machine-checked Pratt certificates for `p`/`n`, the
  generic-group `Θ(√n)` core, and the strong point-counting keystone
  **`#E(𝔽_p) = n` proved without Hasse or Schoof** — with the full-group upgrade
  `E(𝔽_p) = ⟨G⟩ ≃+ ℤ/n` and the unconditional GLV eigenvalue on top.
- **Real but secondary:** the method — propose → the kernel judges → promote, with
  honesty gates — demonstrated across three live domains (secp256k1, P-256,
  elementary number theory) and disciplined negative-result experiments.
- **Overgrown:** the meta layer. 25 root-level prose documents with four competing
  strategy narratives; ten consistency gates whose main job is policing count
  duplication that a leaner structure would not produce; a scaffolded-but-undeployed
  Next.js platform inside a Lean repo; an autonomous-engine surface (6 workflows,
  ~10 scripts, 3 external prover models) whose model tier has **0 accepted proofs**;
  74 files of raw sympy trace in `notes/ward/`; cleanup frozen at "candidate" for
  months. Every extra prose file is another drift surface — the canonical-layer
  falsehoods fixed in this PR existed *because* the same facts lived in ten places.

**Verdict on the previous plans:** the truth-layer repair (generators recount the
ledger; STATUS no longer misstates the keystone) was correct and stands. The rest of
the earlier "complete v0 as designed" ladder is **retracted**: completing an
oversized shape preserves the disease. The correct move is consolidation — make
drift structurally impossible by having fewer places where truth can drift.

## 2. North star (single, long-term)

**A decision-capable, kernel-verified research substrate that a future strong
reasoner can use to evaluate every serious route toward the exact plain
single-target secp256k1 ECDLP, reject false shortcuts, and verify any genuine
progress end to end.** Recovering the discrete logarithm is the long-term
research objective; the repository makes no assumption that a classical
subgeneric route exists.

The formal library remains the durable core. Value also flows through three
external channels:

1. **Publications** — the three standalone units in `PUBLISHABLE_UNITS.md`
   (generic-group `Θ(√n)` core; Pratt certificates + the `#E = n` certificate;
   the Weil/Semaev first-in-Lean ladder).
2. **Mathlib upstreaming** — the general lemmas (coprimality/common-root bridge,
   division-polynomial facts, `normEDS` work) contributed upstream; this is the
   strongest form of external verification and the most durable artifact.
3. **The engine as a method** — the pipeline demonstrated on ≥2 unrelated domains,
   documented well enough that a third party could plug in a new corpus + verifier.

**Explicit non-goals:** claiming a break or a path to one without satisfying the
decision substrate's evidence gates; confusing toy measurements, constant
factors, implementation leakage, conditioned inputs, or quantum resource
estimates with a classical plain-input break; building a multi-tenant SaaS
platform ahead of evidence; investor-facing document growth.

## 3. Operating principles

1. **The kernel is the only judge of mathematics.** Green build = all proved. Never
   `sorry`/`admit`/axioms. (Unchanged, non-negotiable.)
2. **One place per fact.** Counts: `VERIFIED.md` table → generators → everything
   else. Strategy: this file. Route decisions:
   `repo/ECDLP_DECISION_SUBSTRATE.json`. Queue: `tasks/NEXT.md`. Scope/trust wording:
   `TRUST_REPORT.md` + `ABSTRACT_SCOPE.md` + `notes/SECURITY_SCOPE.md`. A new prose
   document must displace an old one, not join it.
3. **Structure over gates.** Gates stay (they caught real drift), but the first fix
   for recurring drift is removing the duplicate surface, not adding a checker.
4. **Archive, never silently delete.** History moves to `archive/` in-tree (and git
   history keeps everything). Reviving anything is one `git mv` away.
5. **Human merges to `main`; agents work on branches and draft PRs.** (Unchanged.)

## 4. Repository structure — target state and rationale

Executed in this PR (tranche 1):

| Action | Paths | Why |
|---|---|---|
| **New** | `ROADMAP.md` | the one strategy doc (this file) |
| **Archive** | `WORK_SCOPE.md`, `ENVIRONMENT_PLAN.md`, `PLATFORM_STRATEGY.md`, `DIRECTOR_CHARTER.md`, `notes/V0_COMPLETION_PLAN.md` → `archive/docs/` | four competing strategy narratives collapsed into §2; content preserved |
| **Archive** | `REVIEW_DOSSIER.md`, `CLAUDE_REVIEW_PACKET.md` → `archive/docs/` | one-shot review artifacts; their accepted findings are already encoded in scope docs and gates |
| **Archive** | `notes/ward/` → `archive/ward/`, `scratch/` → `archive/scratch/`, `generator-report.md` → `archive/` | the manifest's own long-frozen cleanup candidates, executed |
| **Archive** | `platform/` → `archive/platform/` (+ retire `platform-ci.yml`) | undeployed Phase-2 scaffold in a Lean repo; its own README says it belongs in a separate repo; revive from archive or a new repo when Phase-2 becomes an evidence-based decision |

Tranche 2 (**executed** in the same PR):

| Action | Paths | Why |
|---|---|---|
| Merged ✅ | `ONE_PAGE_SUMMARY.md`, `READ_FIRST.md` → `README.md` | three overlapping entry points → one; README is the v0.1 front door (agents keep `AGENTS.md`); originals in `archive/docs/` |
| Moved ✅ | `RESEARCH_MAP.md` → `notes/RESEARCH_MAP.md` | the attack-registry intro is research memory, not a root entry point |
| Folded ✅ | `AGENT.md` → `AGENTS.md` §Prover-loop protocol | two agent docs → one; original in `archive/docs/` |
| Done ✅ | `AGENTS.md`, `README.md` truth pass | stale dev-branch name, pre-keystone GLV wording, engine wording — fixed |
| Indexed ✅ | `notes/` | `notes/INDEX.md` added; per-memo status curation continues incrementally |

Root prose after both tranches (~12 files): `README` · `STATUS`* · `VERIFIED` ·
`BARRIERS` · `TRUST_REPORT` · `ABSTRACT_SCOPE` · `COVERAGE`* · `ROADMAP` ·
`PUBLISHABLE_UNITS` · `AGENTS` · `CLAUDE` · `SETUP` · `REPOSITORY_ARCHITECTURE`
(* = generated).

## 5. Program

**Current phase — monitored candidate intake:**

1. Decision `RS-2026-07-22-001` evaluated all 17 registered routes and selected
   none. This is an evidence decision, not a claim that the ECDLP has no future
   solution.
2. Maintain the exact objective, threat models, route dispositions, promotion
   gates, stop conditions, and reconsideration triggers in
   `repo/ECDLP_DECISION_SUBSTRATE.json`.
3. Keep `data/attack_registry.json` as the detailed evidence encyclopedia and
   `repo/FORMAL_SUBSTRATE.json` as the Lean release map. Never collapse their
   distinct meanings into one priority number.
4. Route any new primary evidence or concrete proposal through
   `experiments/framework/`: explicit online/offline cost, provenance hashes,
   route/threat-model binding, and independent output validation. Intake alone
   does not activate a parked hypothesis.

**Selected-foundation phase — only after a superseding route decision:**

- Build the smallest theorem or tool stack needed by the selected route's next
  falsifiable decision. Missing Mathlib objects are inputs to that decision, not
  an automatic backlog.
- Promote exactly one hypothesis only when its proposal satisfies the common
  acceptance gate. Keep all competing routes parked so costs and evidence stay
  attributable.
- Move a positive mathematical mechanism into Lean only after independent
  computational validation; preserve rigorous negative boundaries as first-class
  results.

**Final integration and review:**

- Regenerate all views, pass the full Python/Lean/CI gate battery, and prepare
  one whole-program adversarial review packet for Claude/Opus.
- Do not merge before that final review. Destructive archive or branch cleanup
  remains a separate post-review decision.
- Publication and upstreaming consume the reviewed state; they do not race the
  research loop.

**Long term, only on evidence:** add domains or hosted verification when a
concrete consumer exists. The archived platform waits until then.

## 6. Standing decision rights (compressed from the old charter)

Agents decide autonomously within the active task and decision-substrate
constraints: formalization routes, doc/gate maintenance, branch commits, and
retries. A new theorem/rung or experiment requires an explicit selected route.
Humans decide: merges to `main`,
anything public-facing (site, publications, external posts), positioning changes,
spend beyond an agreed budget, and any security-relevant finding (freeze + escalate
before any external mention). Honesty rules are absolute: never overclaim, state
limits plainly, verify model output independently before believing it.

## 7. Backlog (audit defect register, post-PR state)

Fixed in this PR: truth-layer drift (stale keystone bottleneck, 228-vs-239 count,
three unledgered modules, stale TASK-005/P-256 note/ENGINE schedule wording) and the
structural cleanup of tranche 1. Remaining, in order:

1. ~~Tranche-2 merges + README v0.1 rewrite~~ (done; remaining: tag v0.1 on main after merge).
2. ~~`ci.yml`: root-file no-sorry coverage; drop the per-push prover step;
   `docs-sync.yml` remediation message lists all 8 generators.~~ (done on `main`:
   the no-sorry gate scans `Ecdlp.lean` + `Ecdlp/` + `ResearchOS/`, the per-push
   prover step is removed, the remediation message lists all 8 generators.)
3. ~~Target lifecycle: registry JSONs for `queue.json` entries; `promote_candidate.py`
   nulls `stem_file` on promotion; `check_targets.py` validates queue entries.~~
   (done: `queue.json` seeds have registry JSONs + open stems
   (`eleven_torsion_degree`, `thirteen_torsion_degree`); promotion consumes the
   stem and nulls `stem_file`; `check_targets.py` fails on unregistered/solved
   queue entries and on dead `stem_file` pointers — the 16 legacy dead pointers
   are nulled.)
4. ~~`hypothesis-explore.yml` PR step `git add` fix (backport from explore-pipeline).~~
   (done: PR step stages `notes/` wholesale, so a 0-lead run without
   `HYPOTHESIS_LEADS.md` no longer breaks `git add`.)
5. ~~`foundation_map.py` docstring vs behavior; `prover_daemon.sh` parameterized
   branch; server workflows' clone assumptions reconciled.~~ (done: docstring now
   states the script prints to stdout and `notes/FOUNDATION_ROADMAP.md` is the
   hand-maintained memo; daemon takes `DEV_BRANCH`/`RESULTS_BRANCH`/`REPO_URL`
   from env (default `main`) instead of a stale hardcoded session branch;
   bootstrap-rsync vs server-clone comments now state the real credential
   precondition instead of contradicting each other.)
6. ~~Frontier triage of the 95 unassigned corpus claims (valuable for the map, not
   blocking v0.1).~~ (done: conservative adversarial triage — all 95 resolved to
   `blocked` (25, a genuine math statement needing a missing foundation) or
   `informal` (70, prose/heuristic/attack-assessment); `data/corpus_triage.json`,
   applied only to the unassigned gap; frontier completeness now 100%.)
7. ~~`explore.html`: fold its hardcoded data into the dashboard generator or retire
   it — it must not remain an ungated public surface.~~ (done: folded — its two KPI
   counters are stamped from `data/stats.json` by `build_dashboard.py`
   (`sync_explore_html`) and gated by `check_status_consistency.py`; the stale
   hardcoded KPI that escaped every gate is now regenerated + drift-checked.)
