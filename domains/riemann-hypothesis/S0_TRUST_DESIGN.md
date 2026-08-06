# S0-TRUST closure design: ResearchOS result ledger and axiom audit

**Status: PROPOSED design v2 (2026-08-05), adversarially reviewed once
(verdict `SOUND_WITH_FIXES`; all seven findings applied — Annex A). No file
in this design has been created or modified; implementation is NOT
authorized by this document (§5). This document is the ledger-contract
proposal that `domains/riemann-hypothesis/README.md:74-75` requires to
exist before `metrics_source` may ever become non-null.**

**Implementation addendum (2026-08-05): the design was implemented in
PR #298 and squash-merged as `d6e146fa`. The dedicated ledger, generated
audit, CI coverage, and isolation gate all passed. Pre-implementation wording
below is retained as design provenance, not as the current repository state.**

Barrier being closed: `S0-TRUST` — "non-ECDLP domain result ledger and
generated axiom audit do not yet exist", blocking "adding or counting any
RH Lean theorem"; exit evidence "dedicated ledger schema, generated audit,
CI coverage, and isolation test"
(`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:381`).

---

## 0. Verified current-state findings (basis for the design)

Every claim below was checked against the working tree on 2026-08-05, and
independently re-verified by an adversarial reviewer (26/26 material
citations confirmed; two line anchors corrected in this v2).

**F1 — The hand-curated axiom audit is not executed by CI.**
`Ecdlp/AxiomAudit.lean:8-10` claims "CI runs it standalone (`lake env lean
Ecdlp/AxiomAudit.lean`)", but the only audit CI actually elaborates is the
*generated* file: `.github/workflows/ci.yml:393-398` runs `lake env lean
Ecdlp/LedgerAxiomAudit.lean` and pipes to `scripts/check_axioms.py` with
`data/result_registry.json`. No workflow anywhere under
`.github/workflows/` invokes `Ecdlp/AxiomAudit.lean` (the only mentions are
ci.yml:339, a comment, and ci.yml:343, a grep-exclusion). Docs that still
describe `AxiomAudit.lean` as the CI gate (`SETUP.md:46`, `README.md:125`,
`AUTONOMY.md:57`, `ABSTRACT_SCOPE.md:18`, `Ecdlp/AxiomAudit.lean:8-10`
itself) are stale on this point. *Uncertainty: whether AxiomAudit.lean was
wired into an earlier ci.yml revision was not checked in git history.*

**F2 — The 12 built ResearchOS declarations have no CI-executed axiom audit
and no ledger row.** `Ecdlp/AxiomAudit.lean:234-245` lists
`ResearchOS.NumberTheory.prime_2017` … `prime_10009`, but per F1 that file
never runs. The generated `Ecdlp/LedgerAxiomAudit.lean` imports
`ResearchOS` (line 2) yet contains **zero** `ResearchOS.*` `#print axioms`
lines, because its contents come from `data/result_registry.json`'s
`ledger_declarations` (`scripts/gen_axiom_audit.py:15-17,31-32`), which are
derived exclusively from `VERIFIED.md` rows
(`scripts/gen_result_registry.py:139` → `ledger_utils.parse_ledger`, which
hardcodes `root / "VERIFIED.md"` at `scripts/ledger_utils.py:97`) — and
`VERIFIED.md` contains no ResearchOS row (grep: 0 matches; the registry's
`ledger_declarations` has 677 names, none `ResearchOS.*`, while its
`declarations` map contains all 12). Consequently `domains/registry.json:56`
("audited by `Ecdlp/AxiomAudit.lean`") and
`ResearchOS/NumberTheory/Elementary.lean:14-16` describe an audit that is
**documented but not machine-enforced**. This is precisely the S0-TRUST
gap, and it already affects the live `number-theory-elementary` domain, not
only future RH work.

**F3 — The no-sorry gate ALREADY scans ResearchOS.**
`.github/workflows/ci.yml:343` greps `Ecdlp.lean Ecdlp/ ResearchOS/
ResearchOS.lean` (excluding `Targets/` and `*AxiomAudit.lean`). The
CLAUDE.md directory map ("scans `*.lean` under `Ecdlp/` excluding
`Targets/`") is narrower than the actual gate. So S0-TRUST's CI-coverage
exit item needs no no-sorry change — only audit, registry, and isolation
steps. (But see §3.5/§4.6: the `*AxiomAudit.lean` exclusion glob itself is
a hole that this design closes.)

**F4 — ResearchOS is a built default target.** `lakefile.toml:2`
(`defaultTargets = ["Ecdlp", "ResearchOS"]`) and `lakefile.toml:13-14`;
`lake build` at ci.yml:387 therefore kernel-checks the import closure of
`ResearchOS.lean`. `Ecdlp.lean` does not import `ResearchOS` (grep: 0
matches), and `ResearchOS.lean:5-6` imports only its two NumberTheory
modules. *Caveat (review finding ADV-3): "built" means the import closure,
not every file under `ResearchOS/` — §4.5 adds the import-closure check
that makes the two coincide.*

**F5 — The checker enforces exact-set equality against a registry key.**
`scripts/check_axioms.py:79-92` fails on any `missing`/`unexpected` name
relative to `registry["ledger_declarations"]`; the allowed base is
`{propext, Classical.choice, Quot.sound}` (line 23) plus native_decide
compiler-trust axioms, which are allowed-but-individually-disclosed (lines
28-35, 105-117), and `sorryAx`/`Lean.guardMsgsAx` always fail (line 30).
Elaboration errors also fail (lines 62-65). The checker takes the registry
path as `argv[2]`, so it is registry-file-agnostic and reusable for a
second registry. *Caveat (review finding ADV-1): its native_decide
detection is name-substring-based and spoofable — §4.7 closes this.*

**F6 — The registry generator already parses ResearchOS source.**
`scripts/gen_result_registry.py:33-39` scans both `ROOT/Ecdlp` and
`ROOT/ResearchOS` (Targets excluded), so ResearchOS declarations already
appear in `data/result_registry.json`'s `declarations` map — they merely
have no ledger row citing them. The resolution machinery (exact /
unique-source-match / wildcard / anonymous-instance, lines 99-124, 160-251)
is directly reusable. *Caveats: `_candidate_declarations` line 112 falls
back to a repo-wide unique simple-name match ignoring file scope (the §4.2
isolation assertion closes cross-lane leakage), and `parse_declarations`
uses `dict.setdefault` (lines 71-80) so duplicate qualified names silently
keep the first-seen anchor — §4.5 makes duplicates a failure.*

**F7 — The ECDLP headline count is structurally isolated from any new
ledger file.** `scripts/gen_stats.py` binds its headline figures to
`VERIFIED.md` only (`VERIFIED = ROOT / "VERIFIED.md"` at gen_stats.py:38;
main-table rows recounted above the `### Coverage restatements` cutoff,
`HEADLINE_END` at :48), writing `data/stats.json` (`ledger_rows: 307`
today). It additionally globs `Ecdlp/Proved/*.lean` for the
`proved_modules` field (lines 110-111) — a module list, not a result count.
A new ledger file cannot leak into the headline figures unless someone
edits VERIFIED.md — which is what the isolation test (§4) pins.

**F8 — Generated-view bookkeeping surfaces that must list any new generated
file:** `repo/ARTIFACTS.yaml` `generated_views` block (paths incl.
`Ecdlp/LedgerAxiomAudit.lean` at line 128; `hand_edit: false`,
`generated: true`), `scripts/check_generated_fixpoint.py:49`,
`.github/workflows/docs-sync.yml:25,125` (`DERIVED_PURE`),
`REPOSITORY_ARCHITECTURE.md:85,99,136`.

**F9 — Governing contracts.** RH-004 requires "a domain-specific result
record and axiom-audit coverage designed **before** the theorem is counted"
(`tasks/RIEMANN_HYPOTHESIS.md`, RH-004 expected output); RH modules belong
under `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/` with `RH-` ids
(`domains/riemann-hypothesis/README.md:69-71`); `metrics_source` stays null
until a ledger contract exists (README.md:74-75), enforced for exploratory
domains by `scripts/check_domains.py` rule 3. RH task lanes may edit only
`domains/riemann-hypothesis/`, `notes/reviews/`,
`tasks/RIEMANN_HYPOTHESIS.md` — for `notes/reviews/` the covering
files-allowed clause is RH-002/RH-003's (this document cites that lane, not
RH-001's narrower "one curated review" clause; review finding ADV-6).

---

## 1. Dedicated result ledger: `VERIFIED_RESEARCHOS.md` (ResearchOS-wide, repo root)

### 1.1 Location decision

**Chosen: a single ResearchOS-wide ledger `VERIFIED_RESEARCHOS.md` at the
repository root, next to `VERIFIED.md` — not a per-domain
`domains/riemann-hypothesis/RESULTS.md`.** Rationale, argued against the
existing machinery:

1. **The barrier is lane-wide, not RH-specific.** S0-TRUST names a
   "non-ECDLP domain result ledger" (singular), and finding F2 shows the
   hole already swallows the 12 live `ResearchOS.NumberTheory`
   declarations. One ledger closes both; a RH-only file would leave the
   existing live domain unledgered and force a second closure later.
2. **Maximal generator/parser reuse.** `ledger_utils.parse_ledger` reads a
   root-relative file (ledger_utils.py:97) and `extract_files` resolves
   basenames via `root.rglob` (ledger_utils.py:47);
   `gen_result_registry.py` already indexes ResearchOS declarations (F6).
   Parameterizing the ledger path + the registry output path is a minimal
   diff; per-domain ledgers would multiply parser instances, registries,
   audit files, and CI steps per domain.
3. **Headline isolation by construction.** `gen_stats.py` binds its
   headline figures to `VERIFIED.md` only (F7); a sibling root file is
   invisible to the ECDLP counters, the frozen metrics, and
   `badges/theorems.json`.
4. **Domain scoping is a column, not a file.** Claim-id prefixes already
   exist: `RH-` (README.md:69) and `nt-`
   (`domains/number-theory/corpus.md:16-26`). Per-domain views can be
   generated from the one ledger if ever needed.
5. The location does not change the authorization story: the accompanying
   scripts/CI changes are outside the RH lane either way (§5).

### 1.2 Schema

Header (one table, one row per claim; the first row of the file states the
parsing contract):

```
| claim_id | domain | declaration | file | statement_anchor | source_contract | review_record | axiom_base | method | date | status | claim_scope |
```

Column semantics (mapping the required set: module, declaration, statement
hash/anchor, source contract ID, review record, axiom base, date, claim
scope):

| column | contract |
|---|---|
| `claim_id` | unique; must start with a registered domain prefix (`RH-`, `nt-`, …) — the prefix set is the machine-readable domain whitelist |
| `domain` | id from `domains/registry.json` (`riemann-hypothesis`, `number-theory-elementary`) — checked to exist |
| `declaration` | fully qualified Lean name(s) in backticks, same conventions VERIFIED.md rows use (brace-expansion and wildcards supported by `ledger_utils.expand_braces`/`extract_name_patterns`, ledger_utils.py:55-91); **must resolve** to a public declaration parsed from built ResearchOS source |
| `file` | repo-relative path; **must be under `ResearchOS/`** (machine-enforced; RH rows additionally under `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/` per README.md:70-71) |
| `statement_anchor` | `file:line@sha256:<first-12-hex>` — the registry generator records the declaration's `file`/`line` (it already does: gen_result_registry.py:74-79) and the sha256 of the declaration's source statement slice; the `--check` mode fails if the anchor is stale. *Flagged limitation: this hashes source text, not the elaborated statement; a kernel-level statement hash would need a Lean-side tool that does not exist in this repo today. Upgrade path noted, not required for closure.* |
| `source_contract` | contract id binding the row to its reviewed mathematical statement: `TARGET_BRIDGE_CONTRACT.md#P1/P2/P3` or an `SC-*` id from `SOURCE_CONTRACTS.md`; `—` allowed only for elementary self-evident facts (the nt- backfill rows) |
| `review_record` | path to the independent-review record under `notes/reviews/` (RH rows: mandatory per README.md:57-59; nt- backfill rows: the dated backfill review) |
| `axiom_base` | `standard` (exactly ⊆ {propext, Classical.choice, Quot.sound}) or `standard+native_decide`; cross-checked against actual audit output (§2.3) |
| `method` | as in VERIFIED.md (`Mathlib`, `norm_num`, `native_decide`, …) |
| `date` | ISO date the row was added (promotion date) |
| `status` | `proved` only; unlike VERIFIED.md there is no footnote-marker convention unless carried over deliberately |
| `claim_scope` | one-sentence claim boundary (what the theorem does **not** say), the structured analogue of VERIFIED.md's bolded scope prose (cf. VERIFIED.md:26,30) |

**Parser contract (v2, review finding ADV-4):** `ledger_utils.ROW_RE`
(ledger_utils.py:7) is a fixed 5-cell pattern with greedy `(.+)` groups;
fed a 12-column row it would greedily **mis-assign** cells rather than
fail. The design therefore adds `parse_researchos_ledger(root)` to
`scripts/ledger_utils.py` — a `|`-split N-column parser that **reuses**
`strip_md`, `extract_files`, `extract_name_patterns`, and `expand_braces`
unchanged, with these hard rules: every data row must split into exactly 12
cells or the parse fails; a literal `|` inside any cell is forbidden (no
escape mechanism — reword the cell); a fixture test includes a
`|`-containing cell and asserts failure. `parse_ledger` for VERIFIED.md is
untouched, and the isolation checker asserts no existing consumer ever
feeds `VERIFIED_RESEARCHOS.md` to `parse_ledger`.

### 1.3 The kernel-checked-only rule

**A row may exist only for a kernel-checked declaration.** Machine-enforced
as the conjunction of, on every push:

1. `scripts/gen_researchos_registry.py --check` (new; a thin
   parameterization of `gen_result_registry.py`'s existing resolution
   machinery, writing `data/researchos_result_registry.json` with the same
   `ledger_declarations` key shape) fails on any unresolved name, missing
   cited file, row-without-evidence, or **duplicate qualified declaration
   name across files** (v2, ADV-3) — mirroring
   gen_result_registry.py:299-310.
2. `lake build` kernel-checks the `ResearchOS.lean` import closure (F4;
   ci.yml:387), and §4.5's import-closure check makes "under `ResearchOS/`"
   coincide with "built".
3. The no-sorry grep already covers `ResearchOS/` (F3; ci.yml:343), with
   the exclusion tightened per §3.5/§4.6.
4. The generated audit (§2) `#print axioms` every ledger declaration;
   `check_axioms.py` fails on `sorryAx`, non-whitelisted axioms, and any
   set mismatch with the registry (F5), plus the §4.7 provenance check.
5. **Inverse coverage (new, closes F2 permanently):** the registry
   `--check` additionally fails if any public declaration in built
   ResearchOS source has **no** ledger row — "built ⇒ ledgered ⇒ audited".
   The only exempt files are the two exact audit paths of §2.1 (no glob;
   v2, ADV-2). On first run this intentionally fails until the 12
   `ResearchOS.NumberTheory` declarations are backfilled as `nt-*` rows.

---

## 2. Generated axiom audit for ResearchOS

### 2.1 Artifact

New generated file **`ResearchOS/LedgerAxiomAudit.lean`**, mirroring
`Ecdlp/LedgerAxiomAudit.lean`:

- header `import ResearchOS` **only** (no `import Ecdlp` — the audit of the
  non-ECDLP lane must not elaborate ECDLP code; contrast
  Ecdlp/LedgerAxiomAudit.lean:1-2 which imports both);
- docstring stating it is generated by `scripts/gen_axiom_audit.py` from
  `data/researchos_result_registry.json`, never imported from
  `ResearchOS.lean`, elaborated standalone by CI (mirror of
  Ecdlp/LedgerAxiomAudit.lean:4-11);
- one `#print axioms <name>` per entry of
  `researchos_result_registry.json["ledger_declarations"]`, sorted.

**Audit-file exemption policy (v2, review finding ADV-2 — S1).** The
current gates exempt the glob `*AxiomAudit.lean` (no-sorry grep at
ci.yml:343; knowledge-graph glob at build_knowledge_graph.py:98). A
hand-created `ResearchOS/AnythingAxiomAudit.lean` imported into the build
would be exempt from the no-sorry grep, the inverse-coverage rule, and the
cross-import guard — an invisible channel for adding a sorry'd or unaudited
built declaration. The design therefore replaces glob-based exemptions with
the **exact path set** `{Ecdlp/AxiomAudit.lean, Ecdlp/LedgerAxiomAudit.lean,
ResearchOS/LedgerAxiomAudit.lean}` wherever it controls a gate, and the
isolation checker (§4.6) fails on any *other* file matching
`*AxiomAudit.lean` under `Ecdlp/` or `ResearchOS/`.

### 2.2 Generator

Extend `scripts/gen_axiom_audit.py` (currently hardcoding `REGISTRY`/`OUT`,
gen_axiom_audit.py:10-11) to iterate over a table of
`(registry, out, imports)` pairs:

- `(data/result_registry.json, Ecdlp/LedgerAxiomAudit.lean, ["Ecdlp", "ResearchOS"])`
  — unchanged output for the existing pair (byte-stability required so
  `check_generated_fixpoint.py` and docs-sync stay green);
- `(data/researchos_result_registry.json, ResearchOS/LedgerAxiomAudit.lean, ["ResearchOS"])`.

`--check` covers both (staleness semantics as gen_axiom_audit.py:38-45).
Register the new file everywhere F8 lists: `repo/ARTIFACTS.yaml`
`generated_views.paths`, `scripts/check_generated_fixpoint.py:49` list,
`docs-sync.yml` header comment and `DERIVED_PURE`,
`REPOSITORY_ARCHITECTURE.md` tables (lines 85, 99, 136).

### 2.3 Axiom whitelist and native_decide policy

`scripts/check_axioms.py` is reused with its base semantics: allowed base
`{propext, Classical.choice, Quot.sound}` (check_axioms.py:23);
native_decide axioms (`Lean.ofReduceBool`, `Lean.trustCompiler`, per-decl
`._native.native_decide.ax_*`, lines 28-35) allowed but individually
disclosed in output (lines 105-117); `sorryAx`/`Lean.guardMsgsAx` always
fatal (line 30). That *is* what the repo's audit actually enforces —
native_decide is not banned, it is a disclosed TCB extension
(`Ecdlp/AxiomAudit.lean:15-17`, `TRUST_REPORT.md:12-14`).

**Strengthening 1 — per-row declared base.** When the registry carries a
per-declaration `axiom_base` map (emitted by `gen_researchos_registry.py`
from the ledger column), the checker fails any declaration whose observed
axioms exceed its declared base. Effect: a row declared `standard` that
surfaces `Lean.ofReduceBool` fails CI. This makes native_decide "explicitly
whitelisted per row" for ResearchOS, strictly stronger than the ECDLP-side
blanket disclosure, and preserves the corpus promise that all NumberTheory
facts are norm_num-only (`domains/number-theory/corpus.md:11-12`).
Semantics (v2, ADV-7): the map is keyed by **canonical declaration name
after brace/wildcard expansion**; if two rows cite the same declaration
with different bases, `--check` fails; a `nodep` declaration ("does not
depend on any axioms", check_axioms.py:45-49) trivially satisfies any base.
*Flag: whether future RH proofs will need native_decide is unknown; the
per-row column keeps that decision explicit and reviewable instead of
pre-banning it.*

**Strengthening 2 — native-axiom provenance (v2, review finding ADV-1 —
S1).** `is_native_decide` (check_axioms.py:33-35) classifies ANY axiom
whose name matches the `*._native.native_decide.ax_*` shape as
compiler-trust. Nothing today bans the `axiom` keyword in built source, and
the registry's `DECL_RE` (gen_result_registry.py:16-21) does not index
`axiom` declarations, so a hand-declared
`axiom Evil._native.native_decide.ax_1_0 : <RH statement>` would be
invisible to inverse coverage and classified as compiler trust — a counted
false theorem. Two machine checks close this:
(a) the isolation checker (§4.7) fails on any `axiom` keyword declaration
in `ResearchOS/**.lean` source (audit files included — they contain only
`#print`);
(b) `check_axioms.py`, in per-row mode, accepts a
`<decl>._native.native_decide.ax_*` axiom only when `<decl>` resolves to a
declaration present in the registry's `declarations` map (i.e. the aux
axiom was compiler-generated for a real built declaration, not
hand-declared).
*The same spoofing hole exists today on the Ecdlp side; extending fix (a)
to `Ecdlp/**.lean` is recorded as a line item for the Phase-1 ops task,
outside this design's lane.*

---

## 3. CI coverage: exact `ci.yml` additions

1. **No-sorry scan of ResearchOS/: already present** at ci.yml:343 (finding
   F3) — no new step; but the `--exclude='*AxiomAudit.lean'` glob is
   replaced by the exact path set of §2.1 (v2, ADV-2).
2. **Next to the existing registry/audit `--check` steps (ci.yml:274-278),
   add:**
   ```yaml
   - name: Check ResearchOS result registry (VERIFIED_RESEARCHOS.md ↔ ResearchOS source)
     run: python3 scripts/gen_researchos_registry.py --check
   ```
   (`gen_axiom_audit.py --check` at ci.yml:278 now covers both audit files
   after §2.2.)
3. **After the ECDLP audit step (ci.yml:393-398), add:**
   ```yaml
   - name: ResearchOS axiom audit (no sorryAx, no custom axioms, per-row base)
     run: |
       lake env lean ResearchOS/LedgerAxiomAudit.lean > researchos_axiom_audit.txt 2>&1 \
         || { echo "::error::ResearchOS axiom audit failed to elaborate"; cat researchos_axiom_audit.txt; exit 1; }
       cat researchos_axiom_audit.txt
       python3 scripts/check_axioms.py researchos_axiom_audit.txt data/researchos_result_registry.json
   ```
   The exact-set check (check_axioms.py:79-92) then guarantees audit ↔
   ledger ↔ source coherence for the lane.
4. **Ledger consistency / isolation step (new, §4):**
   ```yaml
   - name: Check ECDLP/ResearchOS ledger isolation
     run: |
       python3 scripts/check_ledger_isolation.py
       python3 scripts/test_check_ledger_isolation.py
   ```
5. **Cross-import guard**, mirroring the Targets-import guard at
   ci.yml:352-358: fail if any built file under `Ecdlp/` imports
   `ResearchOS` or any file under `ResearchOS/` imports `Ecdlp` — excluding
   only the exact audit paths of §2.1 (`Ecdlp/LedgerAxiomAudit.lean:1-2`
   legitimately imports both), never the glob. This freezes the build-graph
   separation that makes per-lane auditing meaningful.

---

## 4. Isolation test: `scripts/check_ledger_isolation.py` (+ fixture test)

Machine-checked assertions, all pure-Python, zero-toolchain (runnable in
the cheap pre-build phase):

1. **VERIFIED.md is ECDLP-only:** no main-table row cites a file under
   `ResearchOS/` and no `claim_id` carries a registered non-ECDLP prefix
   (`RH-`, `nt-`) — parsed via `ledger_utils.parse_ledger`.
2. **Headline counters untouched:**
   `data/result_registry.json["ledger_declarations"]` contains no
   `ResearchOS.`-prefixed name, and `data/stats.json` figures equal the
   VERIFIED.md-only recount (delegating to the existing `gen_stats.py`
   `--check` semantics, F7). Combined with (1), no ResearchOS/RH row can
   ever feed `ledger_rows`/`distinct_results` or `badges/theorems.json`.
3. **Frozen-metrics guard:** the `number-theory-elementary` note's promise
   ("does not feed the ECDLP headline count, which stays frozen",
   `domains/registry.json:56`) becomes a checked invariant instead of
   prose.
4. **`metrics_source` contract:** while `riemann-hypothesis` has status
   `exploratory`, its `metrics_source` and `frontier_source` must be null
   (re-asserting `check_domains.py` rule 3 at the lane level);
   additionally, **no** domain's `metrics_source` may ever be
   `data/stats.json` except `ecdlp-secp256k1` (registry.json:23 — note
   `p256-nist`, live, uses `VERIFIED.md` at registry.json:38, consistent
   with this invariant), and a future non-null ResearchOS-domain
   `metrics_source` must reference `VERIFIED_RESEARCHOS.md` or a view
   derived from `data/researchos_result_registry.json` — never the ECDLP
   stats. This is the "stays null until the ledger contract exists" clause
   of README.md:74-75; this document is that contract's proposal, and
   flipping `metrics_source` still requires a dated review after
   implementation.
5. **Import-closure and homonym check (v2, ADV-3):** every non-audit
   `ResearchOS/**.lean` module is transitively imported from
   `ResearchOS.lean` (mirror of the Targets-import guard), so
   "source-scanned" and "kernel-checked" coincide; and the registry
   generators fail on duplicate qualified declaration names across files,
   so a `#print` line can never audit a homonym of the anchored
   declaration.
6. **Audit-file whitelist (v2, ADV-2):** no file matching
   `*AxiomAudit.lean` exists under `Ecdlp/` or `ResearchOS/` other than the
   exact three of §2.1; `Ecdlp/LedgerAxiomAudit.lean` contains no
   `#print axioms ResearchOS.` line and `ResearchOS/LedgerAxiomAudit.lean`
   contains no `#print axioms` for a non-ResearchOS namespace.
   *Amendment 2026-08-06 (RH-004 promotion):* lane membership is decided by
   the lane **registry**, not the namespace string — contract-frozen RH
   declarations (e.g. `riemannZeta_zero_mem_critical_strip`) legitimately
   live in the root namespace while being defined in ResearchOS source. The
   implemented check accepts a printed name iff it is `ResearchOS.*` or a
   `researchos_result_registry.json` ledger declaration, and rejects
   `Ecdlp.*` in the ResearchOS audit and ResearchOS-lane names in the Ecdlp
   audit.
7. **Axiom-keyword ban (v2, ADV-1):** no `axiom` declaration appears
   anywhere in `ResearchOS/**.lean` source. (Extending to `Ecdlp/` is a
   Phase-1 ops line item.)
8. Fixture test `scripts/test_check_ledger_isolation.py` (repo convention,
   cf. `test_check_axioms.py` run at ci.yml:269): synthetic fixtures
   proving the checker fails on each injected violation — an RH row
   smuggled into VERIFIED.md; a ResearchOS name in `ledger_declarations`; a
   non-null RH `metrics_source`; a `|`-containing ledger cell (§1.2); a
   hand-declared `*._native.native_decide.ax_*` axiom; a rogue
   `FooAxiomAudit.lean`; an unimported ResearchOS module.

---

## 5. Rollout plan and authorization boundary

**Ordering (each phase lands as a PR, per the promotion policy in CLAUDE.md
— PRs, never direct pushes to `main`):**

- **Phase 0 (now, RH lane — authorized):** this design document is
  committed under `domains/riemann-hypothesis/` (unambiguously inside the
  RH lane's files-allowed) and reviewed. RH-004 explicitly expects the
  ledger/audit "designed before the theorem is counted" — this document is
  that deliverable.
- **Phase 1 (implementation — NOT authorized by any RH task):** touches
  `scripts/ledger_utils.py`, new `scripts/gen_researchos_registry.py`,
  `scripts/gen_axiom_audit.py`, `scripts/check_axioms.py`, new
  `scripts/check_ledger_isolation.py` + fixture test,
  `.github/workflows/ci.yml`, `.github/workflows/docs-sync.yml`,
  `repo/ARTIFACTS.yaml`, `scripts/check_generated_fixpoint.py`,
  `REPOSITORY_ARCHITECTURE.md`, new `VERIFIED_RESEARCHOS.md` (with the 12
  backfilled `nt-*` rows and their dated backfill review), generated
  `ResearchOS/LedgerAxiomAudit.lean`, plus stale-doc corrections
  (`domains/registry.json:56` note,
  `ResearchOS/NumberTheory/Elementary.lean:14-16` comment, `SETUP.md:46`,
  `README.md:125`, `AUTONOMY.md:57`) and the Ecdlp-side axiom-keyword scan
  (§2.3). **Every one of these paths is outside the RH lane's
  files-allowed, and several are in the RH tasks' must-not-edit lists.
  Implementation therefore requires its own dated task/PR under the
  repository's ops lane or direct maintainer action, with the independent
  gates and rollback point recorded per the promotion policy.** Suggested
  landing order inside the PR: parser + registry generator → ledger file
  with backfill rows → audit generator + generated file → bookkeeping
  registrations (ARTIFACTS.yaml, fixpoint, docs-sync) → ci.yml steps →
  isolation checker + fixtures.
- **Phase 2 (barrier closure — RH lane):** after Phase 1 is merged and
  green, record a dated S0-TRUST closure addendum in
  `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` citing the four
  evidence items of §6, and update the RH queue. Only then may RH-004
  (still gated on RH-003 review) produce a built RH module — which must
  arrive with its `RH-*` ledger row, registry entry, and audit line in the
  same PR, or the inverse-coverage check (§1.3.5) fails CI.

*Flag:* the promotion bot (`prove.yml` Stage B, per CLAUDE.md) and
`AUTONOMY.md:57` promotion instructions only know the ECDLP promotion path
(Ecdlp.lean import + VERIFIED.md row + AxiomAudit line); whether they need
a ResearchOS-aware branch is out of this design's scope and should be an
explicit line item in the Phase-1 ops task.

## 6. Acceptance criteria — one-to-one against the S0-TRUST exit-evidence string

Exit evidence (MATHLIB_CAPABILITY_MAP.md:381): "**dedicated ledger schema,
generated audit, CI coverage, and isolation test**".

| exit-evidence item | acceptance criterion (all machine-checked on every push) |
|---|---|
| **dedicated ledger schema** | `VERIFIED_RESEARCHOS.md` exists with the §1.2 twelve-column schema and strict 12-cell parse; `scripts/gen_researchos_registry.py --check` passes: every row resolves to a built public ResearchOS declaration (kernel-checked-only rule §1.3), every anchor/contract/review path exists, no duplicate qualified names, and inverse coverage holds (every built public ResearchOS declaration — today the 12 NumberTheory facts — has a row) |
| **generated audit** | `ResearchOS/LedgerAxiomAudit.lean` is generated (`hand_edit: false` in `repo/ARTIFACTS.yaml` generated_views; listed in `check_generated_fixpoint.py` and docs-sync `DERIVED_PURE`); `gen_axiom_audit.py --check` proves it byte-fresh from the registry; `check_axioms.py` passes on its elaboration output with exact-set equality to `ledger_declarations`, no `sorryAx`, no axiom outside `{propext, Classical.choice, Quot.sound}` + per-row-declared native_decide with provenance-checked aux-axiom names (§2.3) |
| **CI coverage** | ci.yml contains and passes: the ResearchOS registry `--check` step, the ResearchOS audit elaboration + `check_axioms.py` step, the extended `gen_axiom_audit.py --check`, the cross-import guard with exact-path audit exemptions — alongside the pre-existing ResearchOS-covering no-sorry grep (ci.yml:343, exclusion tightened to exact paths) and `lake build` of the ResearchOS default target (lakefile.toml:2) |
| **isolation test** | `scripts/check_ledger_isolation.py` + `test_check_ledger_isolation.py` pass all §4 assertions: no RH/ResearchOS row can reach `VERIFIED.md`, `data/stats.json`, `badges/theorems.json`, or `data/result_registry.json`'s `ledger_declarations`; `domains/registry.json` keeps `metrics_source: null` for `riemann-hypothesis`; no hand-declared axiom, rogue audit file, or unimported module can enter the lane |

Residual uncertainties carried into review: (a) statement-anchor hashes
source text, not elaborated statements (§1.2); (b) native_decide need for
RH proofs unknown (§2.3); (c) historical CI wiring of
`Ecdlp/AxiomAudit.lean` unverified (F1); (d) promotion-bot impact unscoped
(§5).

---

## Annex A: adversarial review record (2026-08-05)

An independent adversarial reviewer verified all 26 material file:line
citations of draft v1 (26/26 confirmed; two anchors imprecise by a few
lines, corrected in this v2) and confirmed the three load-bearing empirical
findings F1, F2, F3. Verdict: **`SOUND_WITH_FIXES`**. Findings, all applied
in v2:

- **ADV-1 (S1):** name-substring native_decide detection is spoofable by a
  hand-declared axiom named `*._native.native_decide.ax_*`, which — with no
  source-level `axiom` ban and `DECL_RE` not indexing axiom declarations —
  could carry a counted false theorem through every proposed gate. Fixed by
  §4.7 (axiom-keyword ban) + §2.3 Strengthening 2 (provenance check); the
  same hole on the Ecdlp side is recorded as a Phase-1 line item.
- **ADV-2 (S1):** the `*AxiomAudit.lean` exclusion glob exempts any
  hand-added file with that suffix from the no-sorry grep, inverse
  coverage, and the cross-import guard. Fixed by exact-path exemptions
  (§2.1, §3.1, §3.5) + the §4.6 whitelist assertion.
- **ADV-3 (S2):** "built" ≠ "under `ResearchOS/`" (import closure), and
  duplicate qualified names could split anchor vs audited declaration.
  Fixed by §4.5 + §1.3.1.
- **ADV-4 (S2):** the 12-column parser needed a strict cell-count contract
  and a `|`-in-cell rule. Fixed in §1.2.
- **ADV-5 (S2):** two line anchors corrected (gen_stats.py:38;
  ci.yml:339 is a comment, :343 the actual exclusion; TRUST_REPORT.md:12-14),
  and F7 now notes the `Ecdlp/Proved` glob for `proved_modules`.
- **ADV-6 (S2):** `notes/reviews/` files-allowed is cited from the
  RH-002/RH-003 lane, and this document lands under
  `domains/riemann-hypothesis/`.
- **ADV-7 (S2):** per-declaration base-map semantics specified (canonical
  names after expansion; cross-row conflicts fail; `nodep` note).
