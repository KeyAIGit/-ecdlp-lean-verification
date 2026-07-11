// The verifier: turn an untrusted Lean source into a kernel verdict. This is the moat AND the
// main risk — elaborating/compiling arbitrary Lean is arbitrary code execution (native_decide
// compiles and RUNS code; #eval, IO, and adversarial elaboration all execute). Therefore the
// real defense is the SANDBOX the worker runs in (ephemeral, network-off, resource-capped, no
// secrets — see README.md). The source pre-check below is only a cheap first line, not the
// security boundary.
//
// Verdict contract:
//   "verified" — lake accepted the file AND it contains no `sorry`/`admit` (0 exit, clean).
//   "rejected" — lake reported an error, or the source is disallowed.
//   "error"    — infrastructure failure (couldn't run); NOT a statement about the math.

import { spawn } from "node:child_process";
import { writeFile, rm } from "node:fs/promises";
import { randomUUID } from "node:crypto";
import { join } from "node:path";

// The jailed runner must NOT inherit orchestrator secrets (DATABASE_URL, Clerk keys, etc.) —
// elaborating untrusted Lean is arbitrary code execution, so it gets an allowlisted env only.
// Keeps just what the Lean/lake toolchain needs; everything else (secrets included) is dropped.
const ALLOWED_ENV = [
  "PATH", "HOME", "LANG", "LC_ALL", "TERM", "SHELL",
  "ELAN_HOME", "ELAN_TOOLCHAIN", "LAKE_HOME", "LEAN_PATH", "LEAN_SYSROOT",
  "XDG_CACHE_HOME", "TMPDIR",
];

function scrubbedEnv(base: NodeJS.ProcessEnv): NodeJS.ProcessEnv {
  const out: NodeJS.ProcessEnv = {};
  for (const k of ALLOWED_ENV) if (base[k] !== undefined) out[k] = base[k];
  return out;
}

export type Verdict = "verified" | "rejected" | "error";
export type Result = { verdict: Verdict; log: string };

export interface Verifier {
  verify(leanSource: string): Promise<Result>;
}

// Cheap first-line source checks. NOT the security boundary — the sandbox is. Rejects the most
// obvious escape hatches and enforces `import Mathlib` + no incomplete proofs.
const FORBIDDEN = [
  /\bunsafe\b/,
  /\b#eval\b/,
  /\bIO\./,
  /\brunCmd\b/,
  /\bimplemented_by\b/,
  /\bextern\b/,
  /\binitialize\b/,
];

export function precheck(src: string): string | null {
  if (!/^\s*import\s+Mathlib/m.test(src)) return "must `import Mathlib`";
  if (/\b(sorry|admit)\b/.test(src)) return "contains sorry/admit (incomplete proof)";
  for (const re of FORBIDDEN) if (re.test(src)) return `disallowed construct: ${re}`;
  return null;
}

/** Dev/no-infra default: never claims anything is verified. Swap for `localVerifier` on a host
 *  that has the Lean repo + toolchain, running inside the sandbox described in README.md. */
export const stubVerifier: Verifier = {
  async verify(src) {
    const bad = precheck(src);
    if (bad) return { verdict: "rejected", log: `precheck: ${bad}` };
    return {
      verdict: "error",
      log: "stub verifier: no Lean toolchain configured. Deploy the sandboxed worker (README.md) to get real verdicts.",
    };
  },
};

/** Runs `lake env lean` on the submission inside a repo checkout at REPO_DIR. MUST itself be
 *  run inside a hardened sandbox (network off, cgroup limits, ephemeral) — this function does
 *  NOT provide isolation; it assumes the process is already jailed. */
export function localVerifier(opts: {
  repoDir: string;
  timeoutMs?: number;
}): Verifier {
  const timeoutMs = opts.timeoutMs ?? 120_000;
  return {
    async verify(src) {
      const bad = precheck(src);
      if (bad) return { verdict: "rejected", log: `precheck: ${bad}` };

      // UNIQUE per submission — under Ecdlp/Targets/ (excluded from the repo's no-sorry gate and
      // not in the build graph, so it can never affect the Lean CI). A per-call UUID module name
      // means concurrent workers never share or overwrite each other's file. Removed in `finally`.
      const mod = `Sandbox_${randomUUID().replace(/-/g, "")}`;
      const file = join(opts.repoDir, "Ecdlp", "Targets", `${mod}.lean`);
      try {
        await writeFile(file, src, "utf-8");
        const { code, out } = await run(
          "lake", ["env", "lean", file], opts.repoDir, timeoutMs, scrubbedEnv(process.env),
        );
        if (code === 0) return { verdict: "verified", log: out.slice(-4000) || "lake: ok" };
        return { verdict: "rejected", log: out.slice(-4000) };
      } catch (e) {
        return { verdict: "error", log: String(e) };
      } finally {
        await rm(file, { force: true });
      }
    },
  };
}

function run(
  cmd: string,
  args: string[],
  cwd: string,
  timeoutMs: number,
  env: NodeJS.ProcessEnv,
): Promise<{ code: number; out: string }> {
  return new Promise((resolve) => {
    const p = spawn(cmd, args, { cwd, env });
    let out = "";
    const cap = (b: Buffer) => {
      out += b.toString();
      if (out.length > 200_000) out = out.slice(-200_000);
    };
    p.stdout.on("data", cap);
    p.stderr.on("data", cap);
    const t = setTimeout(() => {
      p.kill("SIGKILL");
      out += "\n[killed: timeout]";
    }, timeoutMs);
    p.on("close", (code) => {
      clearTimeout(t);
      resolve({ code: code ?? -1, out });
    });
    p.on("error", (e) => {
      clearTimeout(t);
      resolve({ code: -1, out: out + "\n" + String(e) });
    });
  });
}
