# Ecdlp/Targets/

Open conjecture **stems**: one file per candidate statement, ending in `:= by
sorry` (or `:= sorry`). These files are **not imported by `Ecdlp.lean`** and are
therefore **not part of `lake build`** and **excluded from the no-`sorry` CI
gate**. This keeps the project invariant intact: *a green build means every built
theorem is fully proved.*

CI typechecks these stems in a separate **non-blocking** step (`sorry` allowed) so
generator output is guaranteed to be well-formed Lean.

Lifecycle: generated/added here → prover loop attempts it → on a Lean-accepted
proof the file is promoted to `../Proved/`, imported into `Ecdlp.lean`, and
recorded in `../../VERIFIED.md`; its `targets/<id>.json` status becomes `verified`.
