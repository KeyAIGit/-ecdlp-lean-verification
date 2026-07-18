# Fail-closed promotion gate — design

**File:** `notes/reviews/PROMOTION_GATE_DESIGN.md`
**Scope:** the `candidates/ → Ecdlp/Proved/` promotion path (`scripts/promote_candidate.py`, `scripts/prover_loop.py`, `.github/workflows/prove.yml`, `targets/*.json`, `VERIFIED.md`).
**Driving requirement:** close every numbered gap in the #160 blocker comment. The blocker's thesis, verbatim: *"compilation of a candidate file is not sufficient evidence that the registered target was proved. The current promoter trusts only the filename and the first regex-matched declaration."* This document designs a gate under which a promotion can only happen when the promoted declaration is **cryptographically and kernel-level bound** to the registered target, and every ambiguous situation is a hard failure, never a silent default.

**Design principle (fail-closed):** the promoter's default answer is *no*. Promotion requires positive, machine-checkable evidence produced *in the same run*; absence of evidence, malformed evidence, or any unexpected content is an error (nonzero exit, workflow red), never a skip that leaves the pipeline green.

---

## 1. Current state — what the repo already enforces today

Be fair: the pipeline is not naive. The following gates exist on `main` today (worktree = merged base `ac1ec94` + this session's PR #174 changes):

**In the prover loop (`scripts/prover_loop.py` + `prover_target_attempt.py`):**
- A candidate file is written **only after** `lake env lean` accepts the full file (`run_lean`, exit code 0) in that run. The Lean kernel is the acceptance judge for the *loop path*.
- The model can only supply a **proof body**: `clean_candidate` strips fenced code, everything up to `:= by`, and any line starting with `import `, `theorem `, `example `, `namespace `, `end `. The checked file is always `stem + body` where the stem comes from the registry (`stem_file` / `lean_stem`), so on the loop path the model cannot alter the statement or the import list.
- Only targets with `status ∈ {todo, searching}` are attempted (`OPEN_STATUSES`).

**In the promoter (`scripts/promote_candidate.py`), including this session's additions:**
- `sorry`/`admit` substring rejection (fail-closed direction, even if crude).
- Anonymous `example` candidates (the smoke target) are never promoted.
- Refuses to clobber an existing `Ecdlp/Proved/<Module>.lean` (module-file name collision → skip).
- Idempotent on `status == "verified"`.
- **This session's stem-consumption fix:** promotion deletes the open stem from `Ecdlp/Targets/` and nulls `stem_file`, so `Ecdlp/Targets/` holds only open stems and the registry never carries dead pointers.

**In CI (`ci.yml`, runs on the promotion PR before any human merge):**
- Full `lake build` of the whole tree — the promoted module *is* imported from `Ecdlp.lean`, so it is elaborated in the full environment on the PR.
- The no-`sorry` grep over the built proof base, and the `import Ecdlp.Targets` prohibition.
- The axiom audit (`Ecdlp/AxiomAudit.lean` + `scripts/check_axioms.py`): `#print axioms` with allowed base `{propext, Classical.choice, Quot.sound}` + disclosed `native_decide` compiler-trust axioms; `sorryAx` and custom axioms fail the build — **but only for the hand-curated audited list**, which does not automatically include auto-promoted declarations.
- Registry hygiene (`scripts/check_targets.py`, extended this session): open targets must have live stems; non-open targets must not carry dead `stem_file` pointers (a dead pointer means a promotion bypassed the script); `queue.json` entries must name registered targets and must not reference already-verified ones.
- Ledger provenance (`scripts/gen_result_registry.py --check`): every `Ecdlp.*` name cited in `VERIFIED.md` must resolve to a real declaration in built source.
- Count/status/drift gates: `check_counts.py`, `check_status_consistency.py`, `check_semantic_drift.py`.

**In the workflow (`prove.yml`):**
- Promotion lands on the `prover/candidates` branch via a PR; `main` is never pushed directly; a human merges. The scheduled cron was removed for security (untrusted `native_decide` execution with live secrets).

**What is genuinely missing** is the *binding*: nothing verifies that the file sitting in `candidates/<id>.lean` at promotion time (a) is the file the loop verified *in this run*, (b) states the registered target, and (c) contains nothing beyond the one expected declaration. The promoter trusts the filename and `DECL_RE.search(text)` — the first regex match. Everything below exists to replace that trust with evidence.

---

## 2. Gap table — the seven numbered gaps of #160

| # | #160 gap (paraphrased from the verbatim comment) | Where it lives today | Concrete failure scenario | Closed by (§) |
|---|---|---|---|---|
| 1 | `if: always()` promotes every `candidates/*.lean` including stale files | `prove.yml` step "Promote accepted candidates": `if: always()`; promoter globs `CANDIDATES.glob("*.lean")` | The loop step crashes (or never runs after a `lake build` failure), yet promotion still runs. Worse: `add-paths` includes `candidates/` and the PR body says non-promotable leftovers are committed — if such a leftover ever merges to `main`, every future run re-globs and promotes it against a possibly changed tree, with **zero verification in that run**. | §3.2 manifest (current-run-only), §4 M0/M2 |
| 2 | Missing `targets/<id>.json` silently synthesized | `promote_candidate.py` line 134: `spec = json.loads(...) if spec_path.exists() else {"id": tid}` | Drop `anything.lean` into `candidates/` with no registry entry: it is promoted, imported, and ledgered with a fabricated spec — an unregistered claim enters the verified base. | §3.3 rule F2 |
| 3 | Any non-`verified` status promotable | `promote_one`: only `status == "verified"` is skipped | A target parked as `wontfix` / `blocked` / `duplicate` / `superseded` (or any typo status) is promotable. Only `{todo, searching}` are legitimately open. | §3.3 rule F3 |
| 4 | Only the first declaration recorded; extra declarations/dependencies unaudited | `DECL_RE.search(text)` → `m.group(2)` (first match only) | A candidate declaring `theorem expected ...` followed by `theorem smuggled ...` (or a helper `def` that shadows a Mathlib name) promotes under the expected name; the extra declarations enter the build graph unrecorded and un-ledgered. | §3.3 rule F5, §3.4 |
| 5 | Substring `sorry`/`admit` checks are not an axiom/trust audit — custom `axiom`, `unsafe`, unexpected imports not rejected | `promote_one`: `if "sorry" in text or "admit" in text` is the *entire* content audit | A stale/hand-placed candidate (gap 1 makes these reachable) containing `axiom helper : P` + `theorem expected ... := helper ...` passes: no `sorry` substring, and `AxiomAudit.lean` does not audit auto-promoted names, so PR CI's axiom gate never sees it. Similarly `unsafe`, `@[implemented_by]`, extra `import`s. | §3.3 rules F6–F8, §3.4 (kernel-level `#print axioms`) |
| 6 | "Excluded from headline count" is a prose label, not a parsed invariant; automated ledger mutation conflicts with the anti-inflation invariant unless the canonical counter derives from a typed registry | `append_ledger_row` string-splices a row into `VERIFIED.md`; the coverage/headline distinction lives in `LEDGER_INTRO` prose; `gen_result_registry.py` checks cited names exist but not classification or counts | Nothing machine-readable marks a promoted row as non-headline. A future edit (human or bot) moving a row across the prose boundary silently inflates the headline count; `check_counts.py` compares hand-maintained numbers, not a typed source of truth. | §3.6, §4 M4 |
| 7 | Promoted module not rebuilt in the full `Ecdlp.lean` environment before `status=verified` — CI happens after mutation | `prove.yml`: promotion mutates the branch; no `lake build` follows in that job; PR CI runs later | The candidate was checked *standalone* by `lake env lean` against the run's stem. After promotion the module is imported from `Ecdlp.lean`; a fully-qualified-name collision with an existing `Proved/` declaration, or an environment interaction, only surfaces in PR CI — *after* the registry already says `verified` on the branch. The status is asserted before the evidence exists. | §3.5 two-phase status, §4 M3 (post-promotion `lake build` in-job) |

---

## 3. Target design

### 3.1 Canonical target signature in the registry

Every promotable target's `targets/<id>.json` gains a mandatory `signature` block, written by the **generator** (Layer 3) at stem-creation time — never by the promoter:

```jsonc
"signature": {
  // Fully qualified expected declaration name. Exactly one; promotion binds to THIS name.
  "decl": "Ecdlp.Curve.secp256k1_preΨ₁₁_natDegree",
  // The statement (everything between the name+binders colon and `:= by`), as source text.
  "statement": "(secp256k1.preΨ' 11).natDegree = 60",
  // SHA-256 of the NORMALIZED stem source: the stem file's text up to and including `:= by`,
  // with comments stripped, whitespace runs collapsed to single spaces, and trailing space removed.
  // This is the syntactic anchor: the candidate MUST begin with this exact stem.
  "stem_sha256": "…64 hex…",
  // Exact import allowlist for the candidate/promoted module. Anything else is rejected.
  "imports": ["Mathlib", "Ecdlp.Proved.DivisionPolynomial", "Ecdlp.Proved.DivisionPolynomialDegree"],
  "namespace": "Ecdlp.Curve",
  "kind": "theorem"          // theorem | lemma; def/instance targets state kind explicitly
}
```

Rationale for **checked source hash + name + import list** as the registry-side canonical form (rather than storing an elaborated `Expr`): the elaborated type is environment-dependent (it changes meaning if `Ecdlp/Proved/` grows), is expensive to produce at generation time, and would make the registry unreadable. The source hash is the *syntactic* half of the binding; the *semantic* half (elaborated-type agreement in the real environment) is checked in Lean at promotion time (§3.4). Both are required; neither alone suffices — the hash alone doesn't survive environment drift, the defeq check alone accepts definitionally-equal-but-differently-stated theorems without a human noticing the restatement.

Migration note: existing `verified` targets keep their current schema; the `signature` block is required only for `status ∈ {todo, searching}` targets going forward, enforced by `check_targets.py` (§4 M1). A target without a `signature` block is **not promotable** — fail closed.

### 3.2 Acceptance manifest — current-run-only, no directory globbing

`prover_loop.py` becomes the *only* writer of promotion evidence. On each SOLVED target it appends an entry to a single run-scoped manifest, `candidates/ACCEPTANCE_MANIFEST.json` (git-ignored; artifact-uploaded):

```jsonc
{
  "schema": 1,
  "run": {
    "workflow": "prove.yml",
    "github_run_id": "…${{ github.run_id }}…",   // "" for local runs
    "git_head": "ac1ec94…",                       // rev the run checked out
    "lean_toolchain": "leanprover/lean4:v4.31.0", // literal content of lean-toolchain
    "lake_manifest_sha256": "…",                  // hash of lake-manifest.json (Mathlib pin)
    "started_utc": "2026-07-16T09:00:00Z"
  },
  "accepted": [
    {
      "target_id": "eleven_torsion_degree",
      "candidate_file": "candidates/eleven_torsion_degree.lean",
      "candidate_sha256": "…64 hex…",              // hash of the exact bytes written
      "stem_sha256": "…",                          // must equal registry signature.stem_sha256
      "command": "lake env lean ProverLoopAttempt.lean",
      "exit_status": 0,
      "verified_utc": "2026-07-16T09:14:03Z",
      "method": "tier0:decide"                      // or "model:<model-id>#<attempt>"
    }
  ]
}
```

`promote_candidate.py` changes from *glob-driven* to *manifest-driven*:

- New required argument `--manifest candidates/ACCEPTANCE_MANIFEST.json`. **No manifest → exit 1** (unless `--allow-empty` is passed and `candidates/` contains no `.lean` files at all, so a no-solve run stays green).
- The promoter iterates over `accepted[]` entries **only**. It never globs `candidates/*.lean`.
- For each entry it recomputes SHA-256 of `candidate_file` and requires equality with `candidate_sha256` — a candidate edited, replaced, or left over from any other run is a hard error, not a skip.
- Any `.lean` file present in `candidates/` that is **not** listed in the manifest is a hard error ("unmanifested candidate — stale or foreign file"). This inverts gap 1: stale files don't get promoted *and* they don't get silently ignored either; they turn the run red so a human deletes them.
- The manifest's `run.git_head` must equal the current checkout's `git rev-parse HEAD` (the promoter runs in the same job; a mismatch means the tree moved under us).
- `prove.yml` stops committing `candidates/` to the PR branch (drop it from `add-paths`): leftover non-promotable candidates are surfaced as workflow **artifacts** only, never as repo content. This removes the gap-1 replay reservoir entirely.

### 3.3 Fail-closed promotion rules (promoter-side, textual/structural tier)

The promoter accepts a manifest entry only when **all** of the following hold. Each rule's violation is `exit 1` with a named error code — never a skip. (The single legitimate no-op: the entry was already promoted by this same run before a crash-and-rerun, detected by `status == "verified"` **and** `verified_by_manifest_sha == candidate_sha256` recorded in the spec; anything else re-touching a verified target is an error.)

| Rule | Condition | Closes gap |
|---|---|---|
| F1 | Entry is listed in the current-run manifest with matching SHA-256 and `exit_status == 0` | 1 |
| F2 | `targets/<id>.json` exists, parses, and carries a `signature` block. **Never synthesize a spec.** | 2 |
| F3 | `spec.status ∈ {"todo", "searching"}` — exactly the loop's `OPEN_STATUSES`. `verified`, `wontfix`, unknown, or missing status → error | 3 |
| F4 | The candidate text, after the same normalization used for `signature.stem_sha256`, **begins with** the registered stem (recomputed hash equals `signature.stem_sha256`). The statement in the promoted file is byte-identical (mod normalization) to what the registry declares open | binding core |
| F5 | Parsing the candidate finds **exactly one** top-level declaration; its kind matches `signature.kind` and its qualified name (namespace-aware) equals `signature.decl`. Two or more declarations, zero named declarations, or a name mismatch → error | 4 |
| F6 | Token denylist anywhere in the candidate (word-boundary, comment-stripped): `axiom`, `unsafe`, `implemented_by`, `extern`, `opaque`, `partial`, `macro`, `macro_rules`, `elab`, `notation`, `set_option` with any `debug.`/`trust`-class option, `initialize`, `run_cmd`, `#eval`, `sorry`, `admit`, `sorryAx`, `ofReduceBool`, `trustCompiler`. This is deliberately over-broad — a legitimate proof needing one of these goes through a human PR, not the bot | 5 |
| F7 | The candidate's `import` lines are exactly `signature.imports` (set equality; order-insensitive). Any extra or missing import → error | 5 |
| F8 | `Ecdlp/Proved/<Module>.lean` does not already exist (kept from today), **and** `signature.decl` does not already occur in `data/result_registry.json` (declaration-level collision check, not just file-level) | 4/7 |

The textual tier is **not** the trust boundary — it is a cheap prefilter with named errors. The trust boundary is the kernel tier:

### 3.4 Kernel-level binding: elaborated-type check + axiom audit in the full environment

After the file is placed in `Ecdlp/Proved/` and the import added to `Ecdlp.lean` — but **before** any registry/ledger mutation — the promoter generates a throwaway check file and runs the kernel:

```lean
-- .promotion_check/eleven_torsion_degree.lean  (generated; never committed)
import Ecdlp    -- the FULL built environment, promoted module included

open Polynomial in
-- Elaborated-type binding: the promoted declaration's type must unify with the
-- registered statement, elaborated in the full environment. `example : σ := name`
-- succeeds iff the type of `name` is definitionally equal to σ here.
example : (Ecdlp.Curve.secp256k1.preΨ' 11).natDegree = 60 :=
  Ecdlp.Curve.secp256k1_preΨ₁₁_natDegree

-- Trust audit for the promoted name (piped through scripts/check_axioms.py, the
-- existing checker: sorryAx and any axiom outside the allowed base fail).
#print axioms Ecdlp.Curve.secp256k1_preΨ₁₁_natDegree
```

Executed as:

```
lake build                       # gap 7: full-environment rebuild, promoted module + Ecdlp.lean import graph
lake env lean .promotion_check/<id>.lean | tee out.txt
python3 scripts/check_axioms.py out.txt
```

Properties and honest caveats:

- The `example : σ := name` idiom checks type agreement **up to definitional equality**, not syntactic identity. That is the right direction of slack for a fail-closed gate (it can only accept a statement the kernel considers the same proposition-type); the syntactic anchor is already enforced by F4, so a defeq-but-restated theorem cannot arrive here anyway. Both checks together are the "exact elaborated-type comparison" requirement: F4 pins the source, the `example` pins the elaborated type in the real environment.
- `#print axioms` through the **existing** `check_axioms.py` is the real answer to gap 5: substring checks (F6) become defense-in-depth, while the kernel-reported axiom set is authoritative. A candidate that smuggled an `axiom` past every regex still dies here, because `sorryAx`/custom axioms appear in the closure. `native_decide`'s `Lean.ofReduceBool` / per-decl `._native.native_decide.ax_*` axioms remain allowed-but-flagged, exactly as today, and the flag is recorded in the promotion record (§3.6) as `trust: "native_decide"` vs `trust: "kernel"`.
- The `lake build` before the check closes gap 7's *in-job* half: name collisions and environment interactions surface **in the promoting run**, before any status mutation. If it fails, the promoter rolls back the file move + import line and exits 1. (`prove.yml` already builds the project before the loop, so this incremental rebuild is cheap — only the new module and `Ecdlp.lean` recompile.)
- Additionally, `Ecdlp/AxiomAudit.lean` stops being the only audit surface for promoted results: `gen_result_registry.py` (which already parses all built declarations) gains a `--emit-promoted-audit` mode generating `#print axioms` lines for every declaration under `Ecdlp/Proved/`, run in `ci.yml` next to the existing hand-curated audit. Auto-promoted declarations are then axiom-audited on every push forever, not just at promotion time.

### 3.5 Two-phase status flow — `verified` only after full CI

Registry status becomes a small state machine; the promoting run never writes `verified`:

```
todo/searching ──(promoter: all F-rules + kernel tier pass)──► kernel_accepted
kernel_accepted ──(promotion PR merges; post-merge CI on main green)──► verified
any failure at any point ──► run red; no state change (rollback in-job)
```

- **Phase 1 (in the promotion PR):** the promoter sets `status = "kernel_accepted"` and records the acceptance evidence in the spec: `{"acceptance": {"candidate_sha256": …, "run_id": …, "toolchain": …, "verified_utc": …, "method": …, "trust": "kernel"|"native_decide"}}`. The PR carries the moved file, the import, the consumed stem (unchanged from today's lifecycle fix), the typed promotion record (§3.6) — and a status that honestly says what is known: *the kernel accepted this in one run on one toolchain*.
- **Phase 2 (after merge):** a tiny post-merge workflow step on `main` (or the first `ci.yml` run on `main` containing the module) flips `kernel_accepted → verified` **only if** the full CI matrix is green, via a follow-up commit/PR (`scripts/finalize_promotions.py`, idempotent, no-op when nothing is pending). If phase 2 is judged too much process, the fallback variant keeps the flip manual-with-a-gate: `check_targets.py` refuses `status = "verified"` on any target whose spec lacks an `acceptance` block or whose `verified_in` module is absent from the build graph — making "verified on main" logically require the evidence even when a human performs the flip.
- Loop/queue semantics: `kernel_accepted` joins `verified` in every "not open, do not re-dispatch" check (`prover_loop.py` `OPEN_STATUSES` already excludes it by construction; `check_targets.py` queue rule extends its "already verified" error to `kernel_accepted`).

### 3.6 Typed promotion registry → generated ledger

Direct string-splicing into `VERIFIED.md` (`append_ledger_row`) is replaced by a typed record + generator, extending the existing `gen_result_registry.py` provenance pattern:

- The promoter appends one record to `data/promotions.json` (committed, schema-checked):

```jsonc
{
  "target_id": "eleven_torsion_degree",
  "decl": "Ecdlp.Curve.secp256k1_preΨ₁₁_natDegree",
  "file": "Ecdlp/Proved/ElevenTorsion.lean",
  "method": "tier0:decide",
  "trust": "native_decide",          // kernel | native_decide (from the #print axioms run)
  "class": "coverage",               // coverage | headline — promoter may ONLY write "coverage"
  "status": "kernel_accepted",       // mirrors the target spec state machine
  "acceptance": { "candidate_sha256": "…", "run_id": "…", "toolchain": "…", "verified_utc": "…" }
}
```

- A generator (`gen_promotion_ledger.py`, or a mode of `gen_result_registry.py`) renders the managed `VERIFIED.md` section **from this file** between explicit markers (`<!-- BEGIN AUTO-PROMOTED (generated; do not edit) -->` / `<!-- END -->`). Its `--check` mode fails CI when the rendered section and the committed markdown differ — the markdown becomes a *view*, never a source of truth.
- **Anti-inflation invariant, machine-enforced (gap 6):** the headline count is derived as `count(class == "headline")` over the union of the curated headline registry and `data/promotions.json`; `check_counts.py` compares the published number against this derived figure. The promoter is structurally incapable of inflating the headline count because `class: "headline"` from the promoter is a schema violation (`--check` rejects it); reclassifying a promoted result to headline is a human edit to `data/promotions.json` that is visible in diff, named in review, and re-counted by the gate.
- The existing `gen_result_registry.py --check` (cited names must exist in source) continues to run unchanged and now also covers every generated row, since rows cite fully-qualified `Ecdlp.*` names.

---

## 4. Migration steps, ordered by cost

Each step is independently landable and independently valuable; earlier steps do not depend on later ones.

| Step | Change | Closes | Effort (honest) |
|---|---|---|---|
| **M0** | `prove.yml`: `if: always()` → `if: success()` on the promote step; drop `candidates/` from `add-paths` (artifacts only). Two-line workflow diff. | gap 1 (worst half) | ~15 min + one dispatch run to confirm |
| **M1** | `promote_candidate.py`: rules F2, F3, F5 (full-file decl parse, single-decl, name = registry `name`/`signature.decl`), F6 denylist, F7 import allowlist vs the stem's imports; every rejection exits 1. `check_targets.py`: require `signature` on open targets (grandfather clause for pre-existing opens until regenerated). Pure Python, no Lean needed; testable offline with fixture candidates. | gaps 2, 3, 4, 5 (textual tier) | 0.5–1 day incl. adversarial fixtures (smuggled second decl, `axiom` in comment vs code, import reorder) |
| **M2** | Acceptance manifest: `prover_loop.py` writes `candidates/ACCEPTANCE_MANIFEST.json`; `promote_candidate.py --manifest` becomes manifest-driven, SHA-256-checked, unmanifested-file = error; `prove.yml` threads the flag. | gap 1 (completely) | 0.5–1 day; the loop and promoter share one JSON schema, plus a dry-run path for local use |
| **M3** | Kernel tier: generator writes `signature` (statement, `stem_sha256`, imports) into new target specs; promoter enforces F4 and, post-placement, runs `lake build` + generated `.promotion_check/<id>.lean` (`example : σ := name` + `#print axioms` through `check_axioms.py`), with rollback on failure. `gen_result_registry.py --emit-promoted-audit` added to `ci.yml`. Needs CI Lean time (~minutes incremental) and careful namespace/`open` handling when rendering σ into the check file — the fiddly part. | gaps 5 (kernel tier), 7 (in-job half), binding core | 1–2 days incl. a deliberately-broken end-to-end test (defeq-restated candidate must still be caught by F4; smuggled-axiom candidate must be caught by `check_axioms.py`) |
| **M4** | Typed promotion registry `data/promotions.json` + generated `VERIFIED.md` section + `--check` drift gate + derived headline counter wired into `check_counts.py`. One-time migration of the existing auto-promoted rows into records. | gap 6 | 1 day; the risk is markdown-migration churn, mitigated by the BEGIN/END markers |
| **M5** | Two-phase status: `kernel_accepted` state, spec `acceptance` block, `finalize_promotions.py` post-merge flip (or the manual-flip-with-gate fallback), `check_targets.py`/queue rules extended to the new state. Most process-sensitive step — touches human workflow, so land last, after M0–M4 have soaked. | gap 7 (fully) | 1–2 days incl. docs (`AGENTS.md` protocol update) and one full dispatch→PR→merge→flip rehearsal |

Total: roughly 4–7 working days spread over independently reviewable PRs. M0 should land immediately regardless of the rest.

## 5. Deliberately out of scope

- **Sandboxing untrusted `native_decide` execution.** The loop still elaborates model-generated Lean, which can execute code via `native_decide`. That is the runner-isolation problem tracked in `notes/EXECUTION_SECURITY.md` (secret-free, network-off, ephemeral sandbox) and is why the cron stays removed. This gate assumes the *content* may be adversarial but the *runner compromise* threat is handled elsewhere; the manifest's run-binding reduces, but does not eliminate, that surface.
- **Auto-merge or reviving scheduled runs.** A human merges every promotion PR; nothing here changes that.
- **`Expr`-level normalized signatures in the registry.** Rejected above (§3.1): source hash + in-environment defeq check achieves the binding at a fraction of the complexity of serializing elaborated terms. Revisit only if F4's normalization proves too brittle in practice.
- **Redesigning `queue.json` / `agent_day.py` scheduling.** The queue keeps its schema; only its interaction with the new statuses is touched (M5).
- **Reclassifying any promoted result as headline.** The gate makes promoter-side inflation impossible; the *policy* for when a coverage result may become headline remains a human decision recorded as a reviewed diff to `data/promotions.json`.
- **Disproof/refutation flow** (a target found false rather than proved) — a different lifecycle (`refuted` status, counterexample record) worth its own note; nothing here blocks it.
- **Retroactive re-audit of already-merged `Ecdlp/Proved/` modules beyond M3's `--emit-promoted-audit`** — that step already gives every existing promoted declaration a standing `#print axioms` check on each push, which is the durable guarantee we actually need.
