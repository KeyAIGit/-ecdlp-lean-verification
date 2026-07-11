# EXECUTION_SECURITY.md — running model-generated code safely

**Status: open risk, partially mitigated (2026-07).** This note records a real security gap found
in an external audit, the immediate mitigation applied, and what a proper fix requires. It is the
authoritative reference for the SECURITY comments in the affected workflows.

## The risk

Several workflows execute **model-generated code** — which is **untrusted, arbitrary code**:

- **Lean** handed to `lake` / `lake env lean`. Elaborating Lean is not inert: `native_decide`
  compiles and *runs* native code; `#eval`, `IO`, `initialize`, and adversarial elaboration all
  execute during type-checking. A malicious proof candidate can run arbitrary code.
- **Python / SymPy** run via `subprocess` — ordinary arbitrary code.
- **SSH to the warm server** (`server-run.yml` and the engines), executing commands there.

These ran with **live secrets in the runner/host environment**: `FEATHERLESS_API_KEY`,
`ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `GITHUB_TOKEN` (contents/PR write), `SSH_PRIVATE_KEY`,
and reach to a persistent Hetzner server. A hostile generation could exfiltrate any of these,
push to the repo, or pivot to the server. A `timeout` + a `mkdtemp` dir is **not** a sandbox.

## Immediate mitigation (applied)

The **scheduled (cron) triggers were removed** from the workflows that execute model output:

| workflow | was | now |
|---|---|---|
| `prove.yml` | `workflow_dispatch` + daily cron | **`workflow_dispatch` only** |
| `autonomous-engine.yml` | `workflow_dispatch` + weekly cron | **`workflow_dispatch` only** |
| `explore-pipeline.yml` | `workflow_dispatch` + weekly cron | **`workflow_dispatch` only** |
| `hypothesis-explore.yml` | `workflow_dispatch` + weekly cron | **`workflow_dispatch` only** |

`agent-prove.yml` and `agent-day.yml` were already manual-only. Capability is preserved — every
workflow can still be launched by hand — but nothing runs **unattended**. This bounds the risk to
runs a human explicitly starts; it does **not** make a run safe.

**Credential rotation (owner action).** If risky unattended runs already executed, rotating
`FEATHERLESS_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, the fine-grained `GITHUB_TOKEN`/PAT,
and the server `SSH_PRIVATE_KEY` is a reasonable precaution. This is **not** an assertion of a known
compromise — only that these secrets were reachable by executed model code, so rotation is cheap
insurance. Only the repository owner can rotate them; the agent never handles secret values.

## What a real fix requires (before re-enabling any schedule)

Run every piece of untrusted (model-generated) code in a **disposable jail**:

- **No secrets in the environment** (allowlist only the toolchain vars; the platform worker's
  `scrubbedEnv` in `platform/worker/verifier.ts` is the pattern, but that alone is *not* isolation).
- **Network off** (no egress → no exfiltration, no C2).
- **Read-only** repo checkout; write only to a throwaway scratch dir.
- **No SSH agent / no server credentials** in scope.
- **Separate UID**, plus PID/mount/network **namespaces**, `seccomp`, and `cgroup` CPU/RAM/PID/
  file-size limits.
- **Ephemeral**: destroy the container/microVM after each job.

Until that jail exists, treat manual runs as trusted-input only (proof candidates you have read),
and do **not** re-add cron or expose the verifier to outside submissions.

## Related

- `platform/worker/README.md` — the same security model for the Phase-2 hosted verifier (Step 3).
- `platform/worker/verifier.ts` — `scrubbedEnv` removes *direct* secret inheritance (necessary,
  not sufficient — see the note in that file).
