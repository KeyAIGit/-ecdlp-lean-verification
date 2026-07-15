# V0_COMPLETION_PLAN — finishing the substrate (v0 → v0.1)

> Status: PROPOSED (plan, not a claim). Produced from a whole-repository audit
> (2026-07-15): three independent inventory passes (scripts/CI · platform/notes/
> experiments · proof-pipeline state), local runs of every consistency gate, and
> the GitHub Actions run history. Every defect below carries file:line evidence
> that was re-verified against the working tree before writing.
>
> Counts quoted here are *audit observations*, deliberately including where they
> disagree with the canonical layer — that disagreement is itself finding A2.
> After the Phase-1 PR lands, `STATUS.md` wins again, as always.

## 1. What the substrate is, and what "v0 complete" means

The substrate (per `ENVIRONMENT_PLAN.md`) is a verified, machine-navigable
research environment in five layers:

| Layer | Content | v0 goal |
|---|---|---|
| L1 Verified core | kernel-checked theorems (`Ecdlp/Proved/`, `ResearchOS/`, `VERIFIED.md`) | every built theorem proved; every proved theorem ledgered |
| L2 Frontier map | what is open/blocked and by which foundation | every corpus claim triaged; no stale "blocked" that is actually proved |
| L3 Navigable structure | machine-readable graph, stats, bundles, site | all derived views regenerate from machine sources; zero hand-maintained counts |
| L4 Formalized objects | GLV, torsion, division polynomials, keystones | object scope stated exactly (proved vs open), nowhere overshooting or *undershooting* |
| L5 Engine | generator → prover loop → kernel verifier, warm server, workflows | every workflow either works on dispatch or is explicitly retired; lifecycle has no side doors |

**Definition of v0-complete (the v0.1 bar).** v0.1 is a *trust release*, not a
feature release: the same mathematics, but a substrate that nowhere misstates
itself. Concretely:

1. **Zero known-false statements** in the canonical layer (`STATUS.md`,
   `README.md`, `tasks/NEXT.md`, `domains/registry.json`, `notes/ENGINE.md`).
2. **Counts are computed, never scraped**: the headline figures derive from the
   `VERIFIED.md` table itself, and a gate recounts them.
3. **Ledger completeness**: every module imported by `Ecdlp.lean` has a
   `VERIFIED.md` row (or a documented exclusion), machine-checked.
4. **One target lifecycle**: everything the engine attempts flows through
   `targets/*.json` + stems; no queue-only side channel.
5. **Engine honesty**: all 15 workflows function on dispatch or say why not;
   dead tiers (Featherless 403) are fixed or retired in prose.
6. **Cleanup executed**: the `repo/ARTIFACTS.yaml` cleanup candidates are
   archived or ratified in place — no permanent "candidate" state.
7. **Frontier completeness 100%**: all 486 corpus claims triaged (currently
   95 unassigned).
8. All gates + `lake build` green on `main`; README declares v0.1; git tag `v0.1`.

## 2. Where we actually are (audit summary)

**The core is finished and clean.** 0 `sorry` / 0 `admit` / 0 custom axioms in
everything built; exact 110↔110 bijection between `Ecdlp/Proved/*.lean` and
`Ecdlp.lean` imports; registry/stem lifecycle coherent (16 of 17 targets
`verified`, 1 intentional smoke stem); experiments carry validation scripts and
CI replay; the site is generated and served (keyai.org); the strong keystone
**`#E(𝔽_p) = n` is proved and merged** (`Ecdlp/Proved/CurveCardinalityExact.lean`,
`CurveFullGroup.lean`, `VERIFIED.md:245-247`, PR #152) — including the full-group
upgrade `E(𝔽_p) = ⟨G⟩`, cyclicity, and the unconditional GLV eigenvalue.

**What is not finished is the truth layer about that core** — ironically the
layer this repo exists to keep honest — plus engine hygiene and deferred
cleanup. Three clusters:

### Cluster A — truth-layer drift (highest severity)

| # | Defect | Evidence |
|---|---|---|
| A1 | `STATUS.md` "Main current bottleneck" still says `#E(𝔽_p)=n` "needs Hasse — absent from Mathlib" — **false since PR #152**. Root cause: hardcoded prose in the generator | `scripts/gen_status.py:81-82` → `STATUS.md:50`; contradicted by `VERIFIED.md:246` |
| A2 | Headline count stale: canonical prose says **228 rows / ~192 distinct** while the ledger table holds **239 data rows**. `gen_stats.py` regex-scrapes the prose figure instead of counting the table, so the error replicates into `data/stats.json`, `badges/theorems.json`, `COVERAGE.md`, `data/frontier_map.json`, site counters | `VERIFIED.md:274` vs table rows; `scripts/gen_stats.py:36-50` |
| A3 | Three built+imported modules have **no ledger row**: `CoprimePsi2Psi5`, `CoprimePsi3Psi5`, `CoprimePsi3Psi7` (siblings are ledgered at `VERIFIED.md:172-174`) | `Ecdlp.lean:57-59`; grep count 0 in `VERIFIED.md` |
| A4 | `tasks/NEXT.md` TASK-005 still frames scoping `#E=n` as open work resting on Hasse | `tasks/NEXT.md:128-156` |
| A5 | `domains/registry.json` P-256 note claims the strong keystone is "the remaining gap … same as secp256k1" — now true only for P-256 | registry `p256-nist.notes` |
| A6 | `explore.html` (3D map, added #150) sits outside all governance: not in `repo/ARTIFACTS.yaml`, not regenerated/gated by `docs-sync.yml`, theorem data hardcoded inline — the exact drift pattern the gates exist to prevent | grep "explore" in both files: 0 hits |
| A7 | `notes/ENGINE.md` says the autonomous engine "runs on a weekly schedule"; all crons were removed in the 2026-07 security audit — the whole autonomous layer is dispatch-only | `notes/ENGINE.md:8,64` vs `autonomous-engine.yml:41` |
| A8 | Cosmetic: `VERIFIED.md:206` "closes the last open `Targets/` stem" (the smoke stem remains open by design) | `VERIFIED.md:206` |

### Cluster B — engine & gate hygiene

| # | Defect | Evidence |
|---|---|---|
| B1 | The no-sorry grep scans `Ecdlp/ ResearchOS/ ResearchOS.lean` but **not root `Ecdlp.lean`** — and `agent-prove.yml` appends imports there. A `sorry`-bearing decl added to the root file would pass the gate | `.github/workflows/ci.yml:122` |
| B2 | `hypothesis-explore.yml` PR step does `git add` on `notes/HYPOTHESIS_LEADS.md`, which the script writes only when leads exist → pathspec error kills the PR step. The fix already exists in the sibling (`explore-pipeline.yml:123`), never backported | `hypothesis-explore.yml:102`; `scripts/hypothesis_explorer.py:280-283` |
| B3 | `targets/queue.json` carries two pending targets (`ElevenTorsionDegree`, `ThirteenTorsionDegree`) with no registry JSON, no stem — a side door around the documented lifecycle | `targets/queue.json` |
| B4 | All 15 promoted registry JSONs keep dead `stem_file` pointers to deleted stems | e.g. `targets/001_zmod_from_mod_zero.json` |
| B5 | CI re-attempts the already-`verified` smoke target on every push (spends Featherless budget on a solved problem) | `ci.yml:203-206` |
| B6 | `docs-sync.yml` drift-gate error message lists 5 of 8 required generators — a contributor following it still fails the gate | `docs-sync.yml:186-189` vs `107-117` |
| B7 | `scripts/foundation_map.py` docstring claims it writes `notes/FOUNDATION_ROADMAP.md`; it only prints to stdout, so the committed file is silently hand-maintained | `scripts/foundation_map.py:4-9,31-53` |
| B8 | `scripts/prover_daemon.sh` hardcodes a dead ephemeral branch (`claude/admiring-darwin-uouep1`); if absent the daemon retry-loops forever | `prover_daemon.sh:23,40` |
| B9 | `server-run.yml` and `server-bootstrap.yml` embed contradictory assumptions about whether the repo can be cloned on the server | `server-run.yml:87-89` vs `server-bootstrap.yml:47` |
| B10 | `explore-pipeline.yml` title/docstring describe a DeepSeek tier the defaults no longer use | `explore-pipeline.yml:1`; `explore_pipeline.py:5,52-53` |
| B11 | The Featherless prover tier is idle (HTTP 403, acknowledged in `requirements.txt`); model-provers remain 0-for-N. Decision needed: restore the key or retire the tier in prose | `requirements.txt` note; `STATUS.md:46-47` |

### Cluster C — closure & curation

| # | Item | Evidence |
|---|---|---|
| C1 | Cleanup stalled at Phase 0: `notes/ward/` (74 files, flagged high-priority), `scratch/`, `generator-report.md` (no owner/generator policy) all still in place | `repo/ARTIFACTS.yaml:239-271`; `repo/CLEANUP_PLAN.md` |
| C2 | 95 corpus claims `unassigned` — frontier completeness 80.5%, target 100% | `STATUS.md` corpus table |
| C3 | `docs/ENGINE_PORTFOLIO.md`: 8 challenges, 7 verified only by sympy, no per-row Lean-promotion status | `docs/ENGINE_PORTFOLIO.md` |
| C4 | `notes/` (30 top-level files + ward/) has no index; discovery leans on `RESEARCH_MAP.md` and dashboard auto-nav | — |
| C5 | `README.md` is the v0 text: engine described as scheduled (now dispatch-only), keystone narrative pre-#152 ("only the full geometric `E[n]` version stays open" wording predates the full-group upgrade), no version bar | `README.md:70-78,36` |

Out of scope for v0.1 (explicitly deferred, per `PLATFORM_STRATEGY.md` go/no-go
discipline): deploying `platform/` (Phase 2 backend/auth/hosted verification),
new mathematics campaigns (E[n] ≅ (ℤ/n)² full torsion, Weil W4/W5, Curve25519
ontology), and improving model-prover hit rate. v0.1 finishes the *substrate*;
those run on top of it.

## 3. Strategy

Three principles, then three phases:

- **Truth before features.** The product is a substrate an agent can trust
  without re-checking. A stale "main bottleneck" in the canonical snapshot is
  worse than a missing feature — fix the honesty layer first, at the root
  (generators), never by hand-editing generated files.
- **Fix generators, then regenerate.** Every Cluster-A fix lands as a generator
  change (or a gate extension) so the same drift cannot recur. Where a check is
  missing (table recount, ledger completeness, root-file no-sorry), add the
  check in the same PR as the fix.
- **One risk class per PR** (per `REPOSITORY_ARCHITECTURE.md` PR discipline),
  human merges to `main` (per `DIRECTOR_CHARTER.md` §4).

**Phase 1 — Truth reconciliation (Cluster A).** One generator/gate PR + one
ledger PR. Highest leverage: after it, `STATUS.md` is true again and the
headline count is machine-derived.

**Phase 2 — Engine hygiene (Cluster B).** Two small PRs: CI-gate fixes, then
automation/lifecycle fixes. After it, every seam either works or is gated.

**Phase 3 — Closure and the v0.1 declaration (Cluster C).** Archive PR
(human-reviewed, per charter §4.6 no irreversible deletion without approval),
frontier-triage PR, then the README v0.1 rewrite + tag.

## 4. Tactics — the PR ladder

Each PR lists exit criteria; "gates" means the full local battery:
`check_counts` · `check_status_consistency` · `check_repo_artifacts` ·
`check_targets` · `check_domains` · `gen_stats --check` · `check_semantic_drift`
· CI's `lake build` + no-sorry + axiom audit.

**PR-1 (ledger + generators): "truth-layer reconciliation"** — fixes A1–A5, A7, A8.
1. Add the three missing `VERIFIED.md` rows (A3) with honest scope wording
   mirroring the sibling rows at `VERIFIED.md:172-174`.
2. `gen_stats.py`: count the ledger table (data rows of the main table), stop
   scraping the prose figure; update the `VERIFIED.md` prose line from the
   count; extend `check_counts.py` to recount and fail on mismatch (A2).
3. `gen_status.py`: replace the hardcoded "Main current bottleneck" block —
   `#E=n` moves to "proved" narrative; the honest next bottlenecks become the
   full torsion structure `E[n] ≅ (ℤ/n)²` and the Weil ladder (A1).
4. Refresh `tasks/NEXT.md` TASK-005 (close or re-scope to the *new* frontier),
   the P-256 registry note, `notes/ENGINE.md` schedule wording, and the
   `VERIFIED.md:206` cosmetic (A4, A5, A7, A8).
5. Regenerate all derived artifacts in `docs-sync` dependency order.
   Exit: gates green; no doc anywhere claims `#E=n` open for secp256k1; badge
   shows the recounted figure.

**PR-2 (site governance): explore.html** — fixes A6. Either generate its data
block from `data/knowledge_graph.json` via `build_dashboard.py`, or classify it
hand-maintained in `ARTIFACTS.yaml` with a counter-sync check. Exit:
`check_repo_artifacts` covers it; its numbers cannot silently drift.

**PR-3 (CI gates)** — fixes B1, B5, B6: add `Ecdlp.lean` to the no-sorry grep;
point the per-push prover attempt at an open target or make it opt-in; correct
the drift-gate remediation message. Exit: a `sorry` planted in `Ecdlp.lean`
fails CI in a test run.

**PR-4 (automation lifecycle)** — fixes B2–B4, B7–B10: backport the `git add`
fix; give the two queue-only targets registry JSONs + stems (or drop them);
null out dead `stem_file` pointers on promotion (and teach
`promote_candidate.py` to do it); align `foundation_map.py` with its docstring;
parameterize the daemon branch; reconcile the two server workflows' assumptions;
fix the explore-pipeline title. Exit: `check_targets.py` extended to validate
`queue.json` entries against the registry.

**PR-5 (Featherless decision)** — B11: restore the key and demonstrate one
accepted tier-attempt, or retire the tier in `README`/`ENGINE.md`/`prompts/`
prose ("attempted, 0 accepted, idle") — either outcome is honest; the current
half-state is not. Human input needed (the key is an Actions secret).

**PR-6 (archive)** — C1: move `notes/ward/` and `scratch/` to an `archive/`
namespace (provenance preserved), give `generator-report.md` an owner or a
generator stamp. Human merges; nothing deleted.

**PR-7 (frontier completeness)** — C2: triage the 95 unassigned claims to
statuses with named blocking foundations; frontier completeness → 100%.

**PR-8 (v0.1 declaration)** — C3–C5: `README.md` rewrite (current keystone
narrative, dispatch-only engine, version header), a `notes/INDEX.md`, a
promotion-status column in `ENGINE_PORTFOLIO.md`, then tag `v0.1`.

Sequencing: PR-1 → PR-2/3/4 in any order (independent) → PR-5/6/7 → PR-8 last.
PR-1 through PR-4 are bounded engineering (days). PR-5/6 need one human
decision each. PR-7 is the only judgment-heavy item (days of careful triage).

## 5. After v0.1 (so the direction is explicit)

With the substrate trustworthy end-to-end, the standing priorities from
`DIRECTOR_CHARTER.md` resume on top of it: the full torsion structure
`E[n] ≅ (ℤ/n)²`, the Weil ladder W4/W5, a Curve25519 ontology (first `planned`
domain to go live), and — separately gated by its own go/no-go — the Phase-2
platform decision. None of that belongs in v0; all of it is easier the moment
every sentence in the canonical layer is true again.
