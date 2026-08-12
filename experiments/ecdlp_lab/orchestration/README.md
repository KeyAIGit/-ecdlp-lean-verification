# P04 orchestration boundary

This package runs the fixed engineering-only smoke campaign. It is a bounded,
resumable coordinator, not an Engine route, submission path, scientific writer,
or general-purpose job runner.

## Stable command

```bash
python3 -m experiments.ecdlp_lab.orchestration.run_smoke \
  --config experiments/ecdlp_lab/fixtures/smoke.json \
  --output /tmp/ecdlp-lab-smoke
```

The configuration argument must be exactly the committed smoke locator. The
output must be an absolute, nonsymlink child beneath the host temporary
directory. The lower-level `run_campaign` API also rejects every artifact root
inside the repository. Neither interface accepts an executable, command, argv,
worker module, import path, or parallelism override.

P04 requires Linux/WSL2 POSIX primitives. It fails closed if hard `RLIMIT_AS`,
process groups, no-follow file operations, or advisory writer locks are not
available. The smoke campaign fixes `max_parallel=1`; each method and validator
runs in its own child process with a scrubbed allowlist environment, hard memory
limit, monotonic timeout, bounded stdin/stdout/stderr, and process-tree cleanup.

## Data flow and independence

The coordinator expands the P01 campaign through `records.expand_campaign` and
resolves method identifiers through the committed data-only allowlist. Code
owns the only two worker locators:

- `experiments.ecdlp_lab.orchestration.method_worker`
- `experiments.ecdlp_lab.orchestration.validator_worker`

Children receive one exact canonical JSON object on stdin and must return one
exact canonical JSON object on stdout. The method projection contains only the
public P01 request. The validator projection contains only `p`, `a`, `b`, `G`,
`Q`, `ell`, and the candidate scalar. The validator imports the independent
framework oracle through `core.candidate_validation`; it imports no solver or
method implementation.

Private target material is opened only by the trusted coordinator while it
constructs the final P01 `validation_receipt_v1`. It is never sent to the
method or validator worker and never appears in an event payload or the public
analysis index.

## Retained layout

All paths below are fixed by coordinator code and resolved beneath one
`ArtifactStore` root:

```text
campaign.json
events.jsonl
work_units/<work_unit_id>.json
attempts/<work_unit_id>/<attempt_id>/method_request.json
attempts/<work_unit_id>/<attempt_id>/method_result.json
attempts/<work_unit_id>/<attempt_id>/validator_request.json
attempts/<work_unit_id>/<attempt_id>/validator_output.json
receipts/<work_unit_id>.json
public_analysis_index.json
```

Immutable JSON artifacts are canonical and create-only. A successful work
identity has exactly one final `receipts/<work_unit_id>.json`; that file is the
P01 validation receipt itself, not an orchestration wrapper. Failed validator
receipts may be retained only below their attempt directory and cannot enter
the public index.

`public_analysis_index.json` contains only the campaign ID and sorted tuples of
work-unit ID, validation ID, and final receipt digest. P05 may use this index as
its public trust handoff. It contains no private target ID, digest, locator, or
payload and imports no future analysis code.

## Event replay and retry

`events.jsonl` is a canonical, contiguous SHA-256 chain. Every event binds the
previous event digest and the frozen source-snapshot digest. Replay rejects a
torn line, noncanonical JSON, duplicate finalization, a broken digest/sequence,
or stale source bytes. This is tamper-evident structure; it is not a claim that
a normal filesystem is physically append-only.

The campaign writer lock serializes coordinators. An interrupted scheduled
attempt is never reused: replay derives the next deterministic retry ordinal
and attempt ID. A receipt created immediately before interruption is fully
reconstructed and validated from its retained request, result, validator
request, validator output, target authority, and current implementation bytes
before its single final event is recovered. A late output observed after a
timeout is discarded and cannot produce a result or receipt.

Once `campaign_finished` is present, it must be the unique terminal event.
Subsequent invocations are read-only verification: event bytes, index bytes,
receipt bytes, event head, and semantic CLI summary remain identical. Missing,
changed, linked, noncanonical, or digest-drifted artifacts fail closed rather
than being repaired.

P04 records bounded failures with fixed public codes and retries at most once
by default. Exhaustion, validator disagreement, unavailable resource
enforcement, concurrent writers, storage corruption, and provenance drift make
the command nonzero; no failing attempt is published as a final receipt.

