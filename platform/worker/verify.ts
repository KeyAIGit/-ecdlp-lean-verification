// The verification worker loop (Step 3). Claims queued submissions, verifies each with a
// Verifier, writes the verdict back. Run it on a host that has the Lean repo + toolchain,
// INSIDE the sandbox described in README.md. Needs DATABASE_URL.
//
//   VERIFIER=local REPO_DIR=~/-ecdlp-lean-verification DATABASE_URL=... npx tsx worker/verify.ts
//
// Default VERIFIER=stub is safe (never claims "verified"); switch to local only in a jail.

import { randomUUID } from "node:crypto";
import { claimNextQueued, writeVerdict, failExhausted } from "../lib/db/submissions";
import { stubVerifier, localVerifier, Verifier } from "./verifier";

function chooseVerifier(): Verifier {
  if (process.env.VERIFIER === "local") {
    const repoDir = process.env.REPO_DIR;
    if (!repoDir) throw new Error("VERIFIER=local needs REPO_DIR (path to the Lean repo checkout)");
    return localVerifier({ repoDir, timeoutMs: Number(process.env.VERIFY_TIMEOUT_MS ?? 120000) });
  }
  return stubVerifier;
}

async function main() {
  if (!process.env.DATABASE_URL) throw new Error("DATABASE_URL is required");
  const verifier = chooseVerifier();
  const once = process.argv.includes("--once");
  // Stable per-process claim token, so a worker can only finalize jobs it still holds.
  const workerId = randomUUID();
  const claimOpts = {
    leaseMs: Number(process.env.LEASE_MS ?? 600_000),
    maxAttempts: Number(process.env.MAX_ATTEMPTS ?? 3),
  };
  // A claim's lease MUST outlast a single verification, else a still-running job is re-claimed
  // and verified twice (no corruption — the worker_id guard blocks the stale write — but wasted
  // work). Warn loudly instead of silently mis-configuring.
  const verifyTimeoutMs = Number(process.env.VERIFY_TIMEOUT_MS ?? 120_000);
  if (claimOpts.leaseMs <= verifyTimeoutMs) {
    console.warn(
      `WARNING: LEASE_MS (${claimOpts.leaseMs}) <= VERIFY_TIMEOUT_MS (${verifyTimeoutMs}); ` +
        "a long verification can be re-claimed and run twice. Set LEASE_MS > VERIFY_TIMEOUT_MS.",
    );
  }

  // Sweep exhausted stale claims periodically, not only when the queue drains — otherwise a
  // permanently-busy queue would leave dead rows in `running` indefinitely.
  let iters = 0;
  const SWEEP_EVERY = 25;

  for (;;) {
    if (++iters % SWEEP_EVERY === 0) await failExhausted(claimOpts);
    const job = (await claimNextQueued(workerId, claimOpts)) as
      | { id: string; statement: string; lean_source?: string }
      | null;
    if (!job) {
      await failExhausted(claimOpts); // move retry-exhausted stuck jobs to `failed`
      if (once) break;
      await sleep(5000);
      continue;
    }
    console.log(`verifying ${job.id}: ${job.statement}`);
    const { verdict, log } = await verifier.verify(job.lean_source ?? "");
    await writeVerdict(job.id, workerId, verdict, log);
    console.log(`  -> ${verdict}`);
    if (once) break;
  }
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

main().then(
  () => process.exit(0),
  (e) => {
    console.error(e);
    process.exit(1);
  },
);
