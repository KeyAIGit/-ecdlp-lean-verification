# KeyAI Portability Rehearsal 001

Status: FINAL

Decision: **CHANGE**

- Date: 2026-07-23
- Task: `TASK-011`
- Contract: `repo/PORTABILITY_REHEARSAL.json`

## Executive finding

KeyAI can now represent and inspect a second, independently maintained Lean 4
repository through a small declarative adapter. The source snapshot is
deterministic and Git-object-backed. The compiled probe enumerates Lean's
exported environment, but its launcher and output channel are not independent
of the inspected project. Evidence boundaries and this limitation are enforced
by CI.

The correct decision is `CHANGE`, not `BUILD` and not `STOP`.

- Not `BUILD`: this Windows host has no OS-enforced filesystem or network
  isolation for executing arbitrary external Lean projects, and the current
  `lake env lean` launcher cannot independently authenticate the loaded probe
  module or `KEYAI_*` output.
- Not `STOP`: the pinned Cedar repository builds and passes its lint under
  upstream LF semantics, the generic representation works without a
  project-specific branch, and the remaining failures belong to the generic
  execution runner rather than requiring Cedar-specific generator logic.

The next bounded architecture change, owned by `architecture_validation`, is a
trusted external-execution runner. Its first hostile fixture must attempt to
read a secret, write outside its workspace, modify source, use the network,
forge `KEYAI_*` output, and shadow the probe module. No arbitrary untrusted
intake is authorized before both failed gates pass.

`TASK-012` remains locked. No ECDLP hypothesis was created or tested. Nothing
from this rehearsal enters customer discovery, pilot evidence, or the public
site.

## Evidence boundary

Evidence class: `internal_technical_rehearsal`.

This rehearsal establishes only that:

- a pinned public Lean repository in another domain can be represented without
  changing the generic adapter between deterministic runs;
- tracked source inventory and compiled-environment evidence can be separated
  and cross-checked;
- every source-inventoried public heading in the selected compiled closure
  resolves to a public Lean constant;
- current project-specific coupling and execution limits are explicit.

It does not establish user pain, workflow value, retention, willingness to pay,
external pilot completion, semantic correctness of Cedar, private-repository
support, hosted-workspace safety, or platform-market fit.

The baseline and run records are internal execution attestations. Their
self-digests protect committed content integrity; they are not independent
third-party attestations and ordinary KeyAI CI intentionally does not repeat
the networked external build.

## Selected source

Eight public Lean 4 repositories were scored with the fixed rubric in the
contract. The selected source is:

- repository: `https://github.com/cedar-policy/cedar-spec`
- commit: `3f093947b8ae789e9497772815c3a37309ea5566`
- Git tree: `9ec0e7ea90d98241935620711bf9568c169ef8b7`
- license: Apache-2.0, `LICENSE`
- license SHA-256:
  `09e8a9bcec8067104652c168685ab0931e7868f9c8284b66f5ae6edae5f1130b`
- toolchain: `leanprover/lean4:v4.31.0`
- project root: `cedar-lean`
- score: 98/100

The reserve is `leanprover-community/physlib` at
`c48433678e8fb6306ebcd48453300c8e16058a62`, score 92/100.

Cedar changes the owner, mathematical domain, repository layout, build
topology, and conventions while holding Lean 4 fixed. Its nested
Lean/Rust/protobuf/FFI layout is a stronger first architecture rehearsal than a
single-root Mathlib library.

## Independent baseline

The canonical source checkout remained clean. Build work occurred in a
separate disposable checkout; no external source was copied into KeyAI and no
upstream repository was modified, forked, contacted, or published.

Environment:

- Windows x86_64, 5.7 GiB physical memory
- elan 4.2.3
- Lean 4.31.0
- Lake 5.0.0
- `LEAN_NUM_THREADS=1`

Observed sequence:

1. `lake -R -Kenv=dev update` resolved the pinned dependency graph.
2. An unconstrained build exhausted host memory; this negative result is
   retained in `baseline.json`.
3. `LEAN_NUM_THREADS=1 lake build Cedar SymCC` completed 571 jobs.
4. Upstream `lake lint` produced 119 false missing-import diagnostics in the
   Windows CRLF checkout because the linter searches for LF-terminated import
   text.
5. The same pinned tree in a disposable LF checkout passed `lake lint`.
6. The compiled probe ran against 273 built project `.olean` files and retained
   their aggregate manifest hash.

The baseline commands inherited the host environment and were limited to
reviewed public source. The compiled probe later used a fixed environment
allowlist and disposable HOME/TEMP. Neither mode had OS-enforced network or
filesystem isolation. Lake was found through the parent host PATH or elan
fallback; the selected launcher digest and whether `ELAN_HOME` was inherited
are recorded. The compiled command still passed through the inspected
project's `lake env`, so the output channel is not independently authenticated.
These are two separate required failed metrics behind `CHANGE`.

## Source snapshot

Snapshot SHA-256:
`a96d1f1a13508d0165f9463e79cd92333ac9f140a4942fec447f7206894585fb`

- 828/828 tracked files classified
- 351 Lean modules mapped
- 5,276 source declaration headings inventoried
- 4,215 public source declaration headings
- 250 anonymous instances represented separately
- 0 `sorry` tokens
- 0 `admit` tokens
- 0 source `axiom` or `constant` declarations
- 0 generator-reported unsupported Lean files
- 3 Git symlinks represented and never followed

Two clean runs, one write and one independent `--check`, produced the same
snapshot digest and retained the same commit, tree, empty Git-status digest,
and generator hash.

Adversarial review found that the first parser version missed exactly 255
declarations inside attributed `@[expose] public section` blocks across 14
compiled files. The parser now models attributed public/private context
commands, `Cedar.SymCC.compilePrim` is correctly public, and a regression
fixture preserves this case. The corrected public count is 4,215 rather than
3,960.

The source parser remains a lexical inventory, not an elaboration oracle. Its
limitations are explicit in the snapshot and cannot support theorem-validity
or complete Lean-syntax claims.

## Compiled probe

Compiled-probe SHA-256:
`633707c75a16e412eb82f53126392d46dcd697497a133ff8524459fa2baf0729`

Compiled `.olean` manifest SHA-256:
`18fe92cac750ac8b6490fb99b47c884071a9b3d50bf12152eb450cac2709d289`

- 273 modules in the actual Lean import closure
- 273 modules in the independent lexical closure
- 0 compiled-only or lexical-only module differences
- 3,423 source-public headings in that closure
- 12,296 public constants enumerated from Lean's exported environment
- 12,296 per-declaration records retained
- 3,423/3,423 source-public headings resolved
- 0 missing source declarations
- 0 `sorryAx`
- 0 forbidden axioms
- 0 unexpected custom axioms

The artifact retains each public declaration, defining module, transitive axiom
set, every axiom's declaration kind/module/privacy provenance, and a
deterministic dependency grouping. The checker independently reconstructs the
source target set, compiled declaration set, module closure, dependency groups,
and axiom partition instead of trusting summary counters.

Allowed base axioms are accepted only with exact provenance:
`Classical.choice` as a public axiom from `Init.Prelude`, and `Quot.sound` plus
`propext` as public axioms from `Init.Core`. Nine private Lean 4.31
`native_decide` axioms are accepted only by exact pinned names, the exact
`lean-native-decide-generated` group and
`compiler_generated_native_decide` trust class, and provenance saying
`axiom`, private, and inside the actual compiled closure. Wrong base-axiom
module provenance and a matching non-private generated fake are rejected by
regression tests. These nine declarations extend compiler trust and are never
described as kernel-only or axiom-free evidence.

## Architecture audit

Portable in this rehearsal:

- immutable Git commit, tree, license, toolchain, blob, symlink, and gitlink
  provenance;
- exhaustive tracked-file classification;
- declarative module roots, entrypoints, and ownership prefixes;
- deterministic source inventory with explicit parser limits;
- actual Lean-environment declaration and axiom enumeration;
- exact output ownership, no-follow path checks, and atomic successful writes;
- fixed compiled-probe environment allowlist and disposable HOME/TEMP;
- normalized cross-platform generator digests and canonical compact JSON;
- final-status, artifact-digest, provenance, evidence-boundary, and public-leak
  CI gates.

Still intentionally domain-coupled:

- the ECDLP verified ledger and result registry;
- status, statistics, frontier, knowledge-graph, and decision views;
- proof-root and generated axiom-audit wiring;
- research task, hypothesis, and target registries;
- product/domain registry and public-site generation;
- prover-loop and discovery automation.

There are 55 existing script files containing ECDLP, secp256k1, ResearchOS, or
`VERIFIED.md` coupling. They were not generalized here. Generalizing them
without a second domain's canonical result/task semantics would invent a
platform ontology before evidence requires one.

Both generic portability scripts contain zero selected repository, owner,
Cedar/SymCC, ECDLP, secp256k1, or ResearchOS tokens and no project-name branch.
Project knowledge lives in the declarative adapter.

## Adversarial corrections

Three independent adversarial reviews returned `CHANGE` during implementation.
Their actionable findings led to:

- `--require-final` in merge-blocking CI;
- a fixed metric set where every gate remains required;
- validation of existing artifacts even during implementation;
- run-to-generator-to-snapshot and baseline-to-probe provenance binding;
- corrected attributed public-section visibility;
- actual environment-based closure and declaration enumeration;
- exact axiom names plus declaration provenance instead of a broad regex;
- full per-declaration evidence and independent checker reconstruction;
- duplicate module-root rejection;
- fixed environment allowlist for the compiled probe;
- source revision/workspace checks before and after execution;
- exact dependency revisions, baseline commands, and documented manifest
  workspace effect;
- generated `.olean` manifest hashing;
- no-follow output containment and atomic policy-pass-only writes;
- separate generated and hand-reviewed artifact ownership;
- expanded negative leak scans across public site/trust, pilot, product, and
  task surfaces, including every candidate ID/repository/commit, selected tree
  and license hashes, evidence digests, and the plain selected-project token;
- independent reconstruction of file ordering, classifications, module/file
  bijection, exact Git mode/type/classification matrix, path-derived module
  names, import partitions, declarations, unsupported files, and trust counters;
- exact provenance for all three allowed base axioms;
- structured write/check records for both compiled-probe runs, bound to the
  probe's actual observed workspace state;
- fail-closed mutation tests for final status, required metrics, source binding,
  evidence-boundary tampering, duplicate paths, baseline-command substitution,
  base-axiom provenance forgery, and trust-class weakening.

The two execution findings are not papered over. Environment sanitation reduces
accidental credential exposure but is not a sandbox. More subtly, OS isolation
alone would not authenticate output from a probe launched through project
configuration. Both `external-execution-isolation` and
`compiled-evidence-authenticity` remain required `FAIL` metrics.

Residual technical risks are explicit:

- the reviewed-source runner has no wall-time, child-process, or output-size
  cap;
- output containment has a local path-check/write TOCTOU window even though
  ownership, no-follow traversal, and atomic replacement are enforced;
- lexical declaration extraction intentionally covers the observed syntax, not
  all future Lean grammar;
- baseline and compiled-run records are internal attestations, not independent
  execution certificates;
- exact `native_decide` identity and provenance expose compiler trust but do
  not remove it.

## Non-regression

Completed locally:

- all existing pure-Python CI gates;
- generated-artifact fixpoint for 16 artifacts;
- exhaustive repository classification for 603 files;
- result registry: 296 ledger rows, 442 named declarations, 7 anonymous
  instance records, 100% resolved;
- versioned corpus manifest: 56 sources, 55 current versions, 1 retained
  superseded version, and 11 quantum sources;
- source registry: 17 works and 181 citations across 85 scanned documents;
- product, pilot, task, branch, automation, and domain boundaries;
- 44 generic portability and fail-closed gate regression tests;
- two deterministic source runs and two deterministic compiled-probe runs.
- full KeyAI `lake build` with `LEAN_NUM_THREADS=1`: 8,731 jobs completed,
  exit code 0;
- full ledger axiom audit: 442 results checked, 241 transitively using the
  compiler-trusted `native_decide` axiom, with no `sorryAx` or custom axiom.

The pull request must still pass the latest-head GitHub Actions workflow before
merge. GitHub's workflow record, rather than this internal report, is the
canonical evidence for that remote execution.

## Decision matrix

| Required criterion | Result | Evidence |
| --- | --- | --- |
| Tracked-file classification | PASS | `snapshot.json` |
| Lean module coverage | PASS | `snapshot.json` |
| Deterministic snapshot | PASS | two bound run records |
| Source worktree drift | PASS | `baseline.json` |
| Project-specific core branches | PASS | adapter scan and tests |
| Silent unsupported loss | PASS | snapshot limits and compiled cross-check |
| External baseline | PASS | `baseline.json` |
| KeyAI non-regression | PASS | 23 offline gates, 44 portability tests, full Lean build and ledger axiom audit |
| Compiled declaration trust | PASS | `compiled-probe.json` |
| External execution isolation | FAIL | no OS sandbox on this host |
| Compiled evidence authenticity | FAIL | project-controlled `lake env` launcher/output |
| Manual generator edits between runs | PASS | bound generator hashes |

All metrics are complete. The two required execution-boundary failures force
`CHANGE`.

## Smallest next change

Owner: `architecture_validation`.

Implement one trusted external-execution boundary, not a broader platform
rewrite:

1. Pin an execution image or VM and an absolute trusted Lean executable.
2. Mount source read-only and provide separate writable build/cache paths.
3. Disable network after explicitly pinned dependency acquisition.
4. Pass a fixed environment allowlist with no host credentials.
5. Enforce CPU, memory, process, and wall-time limits.
6. Control the Lean module search path and bind every loaded project `.olean` to
   the committed artifact manifest.
7. Authenticate the probe module and output independently of project Lake
   configuration.
8. Run the smallest hostile fixture: source mutation, path escape, secret
   reads, process spawning, network access, forged `KEYAI_*` records, and a
   shadowed probe module.
9. Re-run this exact Cedar rehearsal and then the reserve repository.

Stop portability expansion if any isolation fixture escapes containment, or if
the runner cannot reject forged output and shadowed probe modules without
project-specific logic or modifying the inspected repository. Passing both
gaps permits a new portability rehearsal; it still does not unlock customer
claims or `TASK-012`.

## Reproduction

Source snapshot:

```text
python scripts/lean_portability.py --source <clean-pinned-checkout>
python scripts/lean_portability.py --source <clean-pinned-checkout> --check
```

Compiled probe after the declared external baseline build:

```text
python scripts/lean_compiled_probe.py --source <disposable-built-checkout>
python scripts/lean_compiled_probe.py --source <disposable-built-checkout> --check
```

Offline KeyAI validation:

```text
python scripts/check_portability_rehearsal.py --require-final
python -m unittest scripts.test_lean_portability scripts.test_lean_compiled_probe scripts.test_check_portability_rehearsal
python scripts/check_repo_artifacts.py
```

Ordinary KeyAI CI validates committed evidence and fixtures without cloning or
executing the external repository.

## Pull request

Branch: `agent/task-011-portability-rehearsal`

Merge policy: the latest branch head must pass the repository's GitHub Actions
workflow. The pull-request URL is bound in the first metadata commit after PR
creation.

## Adversarial review packet

Claude/Opus should review the final PR once, after implementation and CI are
complete. Attempt to falsify `CHANGE` in both directions: find evidence that
requires `STOP`, or evidence that every required metric actually supports
`BUILD`.

Review these questions:

1. Can any artifact, report phrase, or public/control surface convert internal
   technical evidence into customer, pilot, or product proof?
2. Can any tracked file, Lean module, source-public heading, compiled public
   constant, or transitive axiom disappear while all gates remain green?
3. Does the checker independently reconstruct every important counter and
   partition, or does it trust a self-reported boolean?
4. Can a rehashed artifact break commit/tree/snapshot/generator/probe/baseline
   provenance without CI noticing?
5. Can a fake axiom satisfy the exact compiler-trust policy without the required
   allowed-base or private generated-axiom provenance?
6. Can output paths escape rehearsal ownership through symlinks, races, or
   platform-specific path behavior?
7. Can inspected Lake configuration forge `KEYAI_*` output, shadow the trusted
   probe module, alter module search, or load an `.olean` outside the committed
   manifest while all gates remain green?
8. Are both failed execution metrics sufficient to prevent `BUILD`, arbitrary
   untrusted intake, public promotion, and `TASK-012` unlock?
9. Did this change generalize any ECDLP surface without a second-domain semantic
   contract, or leave a necessary thin boundary project-specific?
10. Are baseline self-attestation, ordinary-CI non-reproduction, parser limits,
   and compiler trust described without overclaim?

Requested output:

- findings first, ordered by severity, with file and line references;
- explicit verdict: `ACCEPT CHANGE`, `REQUIRE STOP`, or `ALLOW BUILD`;
- missing tests and residual risks;
- no merge action and no new cryptanalytic hypothesis.
