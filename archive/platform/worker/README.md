# worker/ — the verification worker (Phase 2, Step 3)

Turns an untrusted user submission into a **kernel verdict**: pull a queued `submission`, run
`lake` on its Lean source, write back `verified` / `rejected` / `error`. This is the platform's
**moat** — "submit a claim, get a machine-checked verdict, on the record" — and its **biggest
risk**, because elaborating arbitrary Lean is arbitrary code execution.

> **This directory is a scaffold, not a hardened deployment.** The default verifier is a stub
> that never returns `verified`. Do **not** point it at `VERIFIER=local` outside a real jail.

## Why this is dangerous (read before deploying)

Running a submitted `.lean` file is **not** a pure, sandboxed computation:

- `native_decide` **compiles and runs** native code during elaboration.
- `#eval`, `IO`, `initialize`, `implemented_by`, `extern`, `unsafe` all execute code.
- Adversarial elaboration/`macro`s can loop, allocate, or probe the host.

So a submission can attempt to read secrets, exfiltrate over the network, burn CPU/RAM, or
escape. The `precheck()` in `verifier.ts` rejects the obvious hatches, but **the security
boundary is the sandbox, not the source filter.**

## Required sandbox (non-negotiable for `VERIFIER=local`)

Each verification MUST run in an **ephemeral, isolated** environment:

1. **No network.** Drop egress entirely (the toolchain + Mathlib cache are pre-installed; a
   verification needs no network).
2. **No secrets.** No `DATABASE_URL`, no SSH keys, no cloud creds in the jail. The worker
   process that talks to the DB is **separate** from the process that runs `lake` — pass only
   the source in and the log out.
3. **Resource caps.** cgroup CPU + memory limits; a hard wall-clock timeout (`VERIFY_TIMEOUT_MS`,
   default 120 s); process/file-descriptor limits.
4. **Ephemeral + read-only base.** A fresh container (or microVM: gVisor / Firecracker / Docker
   `--network=none --read-only` + a small writable tmpfs) per submission; destroyed after.
5. **Unprivileged user**, seccomp default-deny-ish, no host mounts beyond the read-only repo.

A pragmatic first implementation: the existing warm-server bridge
(`../../.github/workflows/server-run.yml`) already runs `lake env lean` on a dedicated box — but
that box holds secrets and is **not** yet network-isolated per job, so it is **not** safe for
untrusted input as-is. Step 3 hardens it (or moves verification to per-job Firecracker/gVisor
microVMs) before any external submission is accepted.

## Verdict contract

| verdict | meaning |
|---|---|
| `verified` | `lake env lean` exited 0 **and** the source has no `sorry`/`admit` |
| `rejected` | Lean reported an error, or `precheck` disallowed the source |
| `error` | infrastructure failure (couldn't run) — says nothing about the math |

`native_decide` results additionally trust the Lean compiler (as everywhere in this repo —
`../../TRUST_REPORT.md`); a hardened deployment may choose to reject `native_decide` from
untrusted input and require pure-kernel proofs.

## Run it

```bash
# safe default (no toolchain needed): never returns "verified"
DATABASE_URL=... npx tsx worker/verify.ts --once

# real verdicts — ONLY inside the sandbox above:
VERIFIER=local REPO_DIR=/path/to/-ecdlp-lean-verification DATABASE_URL=... \
  npx tsx worker/verify.ts
```

The web app (`/submit`, `/api/submissions`) only ever CREATES queued rows; the `verdict` column
is writable solely by this worker. The client cannot self-certify.
