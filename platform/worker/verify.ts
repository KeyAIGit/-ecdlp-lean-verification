// The verification worker loop (Step 3). Claims queued submissions, verifies each with a
// Verifier, writes the verdict back. Run it on a host that has the Lean repo + toolchain,
// INSIDE the sandbox described in README.md. Needs DATABASE_URL.
//
//   VERIFIER=local REPO_DIR=~/-ecdlp-lean-verification DATABASE_URL=... npx tsx worker/verify.ts
//
// Default VERIFIER=stub is safe (never claims "verified"); switch to local only in a jail.

import { claimNextQueued, writeVerdict } from "../lib/db/submissions";
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

  for (;;) {
    const job = await claimNextQueued();
    if (!job) {
      if (once) break;
      await sleep(5000);
      continue;
    }
    console.log(`verifying ${job.id}: ${job.statement}`);
    const { verdict, log } = await verifier.verify(job.leanSource ?? "");
    await writeVerdict(job.id, verdict, log);
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
