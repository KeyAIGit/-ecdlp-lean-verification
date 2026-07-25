# Native run envelopes

Only actual Research Engine runs belong here. A terminal outcome points to one
`RER-YYYY-MM-DD-NNN.json` envelope and records its SHA-256. The envelope binds:

- the full frozen candidate-policy hash and its preregistration hash;
- the exact executed prefix of the registered matrix;
- a validated candidate-run manifest from this directory;
- one hashed result record for every executed matrix instance;
- one independently implemented, hashed validation record for every result;
- result artifacts and their hashes;
- independently implemented validation artifacts and their hashes.

Contract fixtures under `experiments/framework/fixtures/` are mechanically
inadmissible as native scientific validators; accepted entrypoints must live
under `experiments/engine/validators/`. A complete `proved`, `supported`, or
`bounded_negative` outcome must execute the entire frozen matrix. Early
stopping is retained as a strict matrix prefix and cannot be relabelled as a
complete result.

Per-instance files follow `instance_result.schema.json`,
`instance_validation.schema.json`, and `validator_request.schema.json`; replay
output follows `validator_output.schema.json`. The validation record binds the
exact result hash, names and hashes a pure Python validator present at the
source commit, declares that it does not share decisive logic with the
producer, and binds separately hashed request and output artifacts.

The fixed `python-pure-json-v3` protocol parses the validator before execution.
Its restricted language has no imports, object attributes, loops,
comprehensions, file/process/network access, dynamic code, or calls outside a
small pure-builtin allowlist. Inputs are size-bounded JSON documents from only
the artifact roles frozen in the candidate preregistration.

The request exposes instance metadata plus the preregistered classification
name, unit, and string type, but neither the producer's claimed value, terminal
outcome, supported value, nor result digest. Each validator returns one
canonical empirical outcome. The Engine applies the frozen exhaustive
precedence to derive the event label, binds the request SHA-256, and requires
the replay to match both the stored output and producer record. This is a
language-level capability boundary, not an operating-system sandbox. Updating
all outer hashes cannot hide a replay or outcome-classification mismatch.

The protocol cannot prove that a cited JSON input came from an independent
scientific implementation. That remains a provenance and source-review gate;
the Engine mechanically enforces distinct source-commit producer and validator
entrypoints, hashes, roles, and replay behavior.

For portability across Git checkouts, SHA-256 is computed over LF-normalized
UTF-8 bytes for text artifacts and raw bytes for non-UTF-8/binary artifacts.
