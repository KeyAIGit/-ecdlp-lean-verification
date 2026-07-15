# ROADMAP — the one strategy document

> Replaces `WORK_SCOPE.md`, `ENVIRONMENT_PLAN.md`, `PLATFORM_STRATEGY.md`,
> `DIRECTOR_CHARTER.md`, and `notes/V0_COMPLETION_PLAN.md` (all preserved under
> `archive/docs/`). Those five files held four different north stars; drift between
> them was itself a defect. From here on: **one strategy file**. Live numbers stay in
> `STATUS.md`; the active queue stays in `tasks/NEXT.md`; this file is direction and
> structure only.

## 1. Position — what this repository actually is (auditor's honest read)

A whole-repository audit (2026-07, three independent inventory passes + gate runs +
CI history) found a project whose **object layer is stronger than its meta layer**:

- **Real and durable:** the Lean library. ~110 proved modules, 0 `sorry`, 0 custom
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

**A kernel-verified formal library of elliptic-curve / discrete-log cryptography,
grown by a propose-and-judge engine, packaged honestly.** Value flows through three
external channels, in priority order:

1. **Publications** — the three standalone units in `PUBLISHABLE_UNITS.md`
   (generic-group `Θ(√n)` core; Pratt certificates + the `#E = n` certificate;
   the Weil/Semaev first-in-Lean ladder).
2. **Mathlib upstreaming** — the general lemmas (coprimality/common-root bridge,
   division-polynomial facts, `normEDS` work) contributed upstream; this is the
   strongest form of external verification and the most durable artifact.
3. **The engine as a method** — the pipeline demonstrated on ≥2 unrelated domains,
   documented well enough that a third party could plug in a new corpus + verifier.

**Explicit non-goals (unchanged, permanent):** breaking secp256k1 or claiming any
path to it (the moonshot framing of the old charter is retired — the honest odds
statement lives in `BARRIERS.md` / `notes/SECURITY_SCOPE.md`); building a
multi-tenant SaaS platform ahead of evidence; investor-facing document growth.

## 3. Operating principles

1. **The kernel is the only judge of mathematics.** Green build = all proved. Never
   `sorry`/`admit`/axioms. (Unchanged, non-negotiable.)
2. **One place per fact.** Counts: `VERIFIED.md` table → generators → everything
   else. Strategy: this file. Queue: `tasks/NEXT.md`. Scope/trust wording:
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

**Near (finish v0.1 — a trust release, weeks):**
- Tranche-2 consolidation above; then a README rewrite that states v0.1 plainly.
- Engine hygiene: root `Ecdlp.lean` covered by the no-sorry gate; the per-push
  prover attempt removed from `ci.yml` (it re-proved a solved target on every push;
  the standalone dispatch workflow remains); target lifecycle unified (queue entries
  must have registry JSONs; promotion nulls dead `stem_file` pointers).
- **Featherless verdict, empirical (2026-07-15 smoke run):** with the key set as a
  repo secret, every model call from a GitHub Actions runner fails with
  `HTTP 403: error code 1010` — a Cloudflare bot-block of the runner's signature,
  not a key problem. **The Featherless tier is dead from CI.** Resolution: the
  per-push attempt is already removed from `ci.yml`; the dispatch workflows and
  scripts stay (they may work from the warm server, whose IP is not a GitHub
  runner); prose must not present the tier as operational. The honest record
  stands: 0 model-prover proofs accepted to date; the tactic ladder +
  human/Claude loop is what lands theorems.
- Tag `v0.1` when: gates green, no known-false statement in canonical docs,
  structure = the table above.

**Mid (the mathematics, months — the real work):**
- **E[n] geometric torsion structure** `E[n] ≅ (ℤ/n)²` — extension-field points;
  the genuine Mathlib gap feeding the Weil pairing.
- **Weil ladder W4/W5** — reciprocity, then bilinear non-degenerate `eₙ`.
- **P-256 `#E = n`** — no `j = 0` shortcut; Hasse or a new certificate route.
- **Upstream candidates** to Mathlib: common-root/coprimality bridge, explicit
  division-polynomial forms, `IsEllSequence` work.
- Publication unit 1 (generic-group core) drafted to submission quality.

**Long (only on evidence):**
- A fourth domain (Curve25519 ontology) when a concrete consumer exists.
- Hosted verification / platform: **go/no-go criterion** — an external user actually
  asking to submit claims against the pipeline. Until then the archived scaffold
  waits; login-and-database work is cheap to restart and expensive to maintain idle.

## 6. Standing decision rights (compressed from the old charter)

Agents decide autonomously: which theorem/rung next, formalization routes, doc/gate
maintenance, branch commits + draft PRs, retries. Humans decide: merges to `main`,
anything public-facing (site, publications, external posts), positioning changes,
spend beyond an agreed budget, and any security-relevant finding (freeze + escalate
before any external mention). Honesty rules are absolute: never overclaim, state
limits plainly, verify model output independently before believing it.

## 7. Backlog (audit defect register, post-PR state)

Fixed in this PR: truth-layer drift (stale keystone bottleneck, 228-vs-239 count,
three unledgered modules, stale TASK-005/P-256 note/ENGINE schedule wording) and the
structural cleanup of tranche 1. Remaining, in order:

1. ~~Tranche-2 merges + README v0.1 rewrite~~ (done; remaining: tag v0.1 on main after merge).
2. `ci.yml`: root-file no-sorry coverage; drop the per-push prover step;
   `docs-sync.yml` remediation message lists all 8 generators. *(done in this PR if
   present in the diff; else next)*
3. Target lifecycle: registry JSONs for `queue.json` entries; `promote_candidate.py`
   nulls `stem_file` on promotion; `check_targets.py` validates queue entries.
4. `hypothesis-explore.yml` PR step `git add` fix (backport from explore-pipeline).
5. `foundation_map.py` docstring vs behavior; `prover_daemon.sh` parameterized
   branch; server workflows' clone assumptions reconciled.
6. Frontier triage of the 95 unassigned corpus claims (valuable for the map, not
   blocking v0.1).
7. `explore.html`: fold its hardcoded data into the dashboard generator or retire
   it — it must not remain an ungated public surface.
