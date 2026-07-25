# KeyAI product queue

This queue tests KeyAI as a product and control plane. Its KPIs are external
orientation, provenance completeness, state drift, completed pilot loops,
return sessions, and willingness-to-pay evidence. None of them counts as
progress toward solving ECDLP.

## Active tasks

### TASK-011 - Validate the external product pilot

Status: active
Kind: product | research | ops
Hypothesis: primary `CH-001`; secondary exploratory lens `CH-002` in
`repo/PRODUCT_MODEL.json`
Why it matters: The secp256k1 repository demonstrates an owner-operated
research-state loop. It does not establish that another team has the same pain,
can use the contracts, or will return.
Inputs:
- `repo/PRODUCT_MODEL.json`
- `repo/PILOT_PROTOCOL.json`
- the generated public workspace and route explorer
- one candidate external Lean or formalization team
Expected output:
- A dated pilot brief and observed onboarding session.
- One build, change, stop, or pending discovery disposition for `CH-001`.
- Any `CH-002` evidence remains separately labelled exploratory.
Exit criteria:
- A non-owner identifies current state, blockers, and next action in ten
  minutes or less as a usability diagnostic.
- The user names a repeated workflow painful enough to test on a second
  project.
- No customer, retention, or willingness-to-pay claim is published without
  direct evidence.
Files allowed to edit:
- `repo/PRODUCT_MODEL.json`
- `repo/PILOT_PROTOCOL.json`
- `.github/ISSUE_TEMPLATE/keyai-pilot.yml`
- product research notes and directly affected public generators
Files that must be regenerated:
- `index.html`
- `dashboard.html`
- `explore.html`
- `pilot.html`
How to verify:
- `python scripts/check_product_model.py`
- `python scripts/test_check_product_model.py`
- browser validation on desktop and mobile

### TASK-012 - Build configurable intake after a pilot contract

Status: blocked_on_task_011_build_disposition
Kind: product | data | ops
Hypothesis: a `build` discovery disposition for primary hypothesis `CH-001`
Why it matters: A hosted or multi-project platform is justified only after a
real team exposes the minimum adapter boundary.
Inputs:
- a completed `TASK-011` discovery record with a `build` disposition
- one permitted external repository or corpus
- a minimal claim, evidence, task, and verifier-adapter contract
Expected output:
- Pinned repository or corpus intake.
- A workspace generated without editing KeyAI's generator code.
- One candidate run with verifier output, decision history, export, and
  rollback.
Exit criteria:
- A non-owner completes the ingest -> structure -> decide -> execute -> verify
  -> retain loop on the second project.
- Authentication, billing, and extra verifier adapters remain out of scope
  unless the pilot requires them.
Files allowed to edit:
- only paths named by the future pilot implementation contract
Files that must be regenerated:
- every public and machine-readable view affected by the adapter
How to verify:
- adapter-specific tests
- product-model and repository gates
- an observed end-to-end pilot run
