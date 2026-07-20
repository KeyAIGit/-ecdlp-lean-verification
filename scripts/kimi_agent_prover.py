#!/usr/bin/env python3
"""Kimi agent-prover — give Kimi (kimi-k3) real hands on the repo.

Instead of blind single-shot drafting, Kimi runs as a TOOL-CALLING agent: it can
`grep` the repository for lemmas, `read_file` to study them, and `run_lean` to
compile its own candidate proof with `lake env lean` and see the kernel's verdict.
It loops (search → write → verify → repair) until the kernel accepts a proof or the
iteration/token budget runs out.

Kimi is still a DRAFTER: the Lean kernel (the `run_lean` tool, and final CI) is the
sole verifier. This harness only executes the tools Kimi asks for; it never trusts
Kimi's text and never commits model output to `main` (artifact-only).

Dispatch via .github/workflows/kimi-agent-prover.yml (needs KIMI_API_KEY + lake).
No key ⇒ clean no-op.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

# Reuse the target registry + Lean plumbing from the single-shot prover.
from prover_target_attempt import TARGETS, WORK_FILE, close_namespace_if_needed

ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = Path("kimi-agent-report.md")
SUCCESS_FILE = Path("kimi-agent-success.lean")

MAX_TOOL_OUTPUT = 6000       # chars of any tool result fed back to Kimi
LEAN_TIMEOUT = 900           # N7's expanded `ring` under a raised maxHeartbeats can run long


# ─────────────────────────────── tools ───────────────────────────────

def _safe_path(rel: str) -> Path | None:
    """Resolve rel under ROOT; reject traversal / absolute escapes."""
    try:
        p = (ROOT / rel).resolve()
    except Exception:
        return None
    if ROOT not in p.parents and p != ROOT:
        return None
    return p


def _grep_root(scope: str) -> str:
    """Where grep searches. 'mathlib' points at the installed Mathlib elliptic-curve source so
    Kimi can read the REAL WeierstrassCurve.Ψ₂Sq/ΨSq/Φ/preΨ' definitions it must unfold (the repo
    only re-exports them). Falls back gracefully if the expected path isn't present."""
    if scope == "mathlib":
        for cand in (".lake/packages/mathlib/Mathlib/AlgebraicGeometry/EllipticCurve",
                     ".lake/packages/mathlib/Mathlib"):
            if (ROOT / cand).is_dir():
                return cand
    return "Ecdlp/"


def tool_grep(pattern: str, glob: str | None = None, scope: str = "ecdlp") -> str:
    root = _grep_root(scope)
    cmd = ["grep", "-rInE", "--", pattern, root]
    if glob:
        cmd = ["grep", "-rInE", f"--include={glob}", "--", pattern, root]
    try:
        out = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=60).stdout
    except Exception as e:  # noqa: BLE001
        return f"grep error: {e}"
    lines = out.splitlines()
    if len(lines) > 120:
        lines = lines[:120] + [f"... ({len(out.splitlines())} matches, truncated)"]
    return "\n".join(lines)[:MAX_TOOL_OUTPUT] or "(no matches)"


def tool_read_file(path: str, start: int = 1, count: int = 200) -> str:
    p = _safe_path(path)
    if not p or not p.is_file():
        return f"read_file error: no such file under repo: {path}"
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, start)
    chunk = lines[start - 1: start - 1 + max(1, count)]
    body = "\n".join(f"{start + i}: {ln}" for i, ln in enumerate(chunk))
    return body[:MAX_TOOL_OUTPUT]


def tool_run_lean(target, proof_body: str) -> tuple[bool, str]:
    WORK_FILE.write_text(
        target.stem + proof_body + close_namespace_if_needed(target.stem),
        encoding="utf-8",
    )
    try:
        proc = subprocess.run(["lake", "env", "lean", str(WORK_FILE)], cwd=ROOT,
                              text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=LEAN_TIMEOUT)
    except subprocess.TimeoutExpired:
        return False, "lake env lean timed out (240s)."
    low = proc.stdout.lower()
    # ok ONLY if the kernel fully accepts it: exit 0, no error, and NO sorry/admit (which are just
    # warnings — 'declaration uses sorry' — so an error-only check would pass a stubbed proof).
    ok = (proc.returncode == 0 and "error" not in low
          and "sorry" not in low and "declaration uses" not in low)
    return ok, (proc.stdout or "(no output)")[-MAX_TOOL_OUTPUT:]


TOOLS = [
    {"type": "function", "function": {
        "name": "grep",
        "description": "Search source for a regex (grep -rInE). scope='ecdlp' (default) searches "
                       "this repo's Ecdlp/. scope='mathlib' searches the INSTALLED Mathlib "
                       "elliptic-curve source, where WeierstrassCurve.Ψ₂Sq / ΨSq / Φ / preΨ' are "
                       "actually DEFINED — read those to know exactly what `unfold`/`rw` produce. "
                       "Use to FIND exact lemma/def names before you build on them.",
        "parameters": {"type": "object", "properties": {
            "pattern": {"type": "string", "description": "extended regex"},
            "glob": {"type": "string", "description": "optional include glob e.g. *.lean"},
            "scope": {"type": "string", "enum": ["ecdlp", "mathlib"],
                      "description": "search this repo (ecdlp, default) or Mathlib source (mathlib)"},
        }, "required": ["pattern"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a repo file (path under the repo root), a line window.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "start": {"type": "integer", "description": "1-based start line"},
            "count": {"type": "integer", "description": "number of lines (<=400)"},
        }, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "run_lean",
        "description": "Write your tactic block after the target's `by` and run `lake env lean`. "
                       "Returns ok=true ONLY if the kernel fully accepts it (no sorry, no error). "
                       "This is the sole judge — you are done only when it returns ok=true.",
        "parameters": {"type": "object", "properties": {
            "proof_body": {"type": "string", "description": "the full Lean proof after `by`"},
        }, "required": ["proof_body"]}}},
]


# ─────────────────────────────── agent loop ───────────────────────────────

def report(text: str) -> None:
    with REPORT_FILE.open("a", encoding="utf-8") as f:
        f.write(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=sorted(TARGETS), default="n7_even_x_psisq")
    ap.add_argument("--max-iters", type=int, default=30, help="tool-call rounds")
    ap.add_argument("--max-tokens", type=int, default=4000,
                    help="per-turn output cap; kimi-k3 spends this on hidden reasoning too, so keep "
                         "it high enough to reason AND still emit a tool call (truncation mid-reason "
                         "= an empty turn)")
    ap.add_argument("--verify-only", action="store_true",
                    help="compile scripts/seeds/<target>.lean via `lake env lean` and report ok+error; "
                         "no API call, no key needed. A fast kernel check for a hand-edited candidate.")
    args = ap.parse_args()

    # ── verify-only: compile the seed candidate on the kernel and report. No model in the loop.
    if args.verify_only:
        target = TARGETS[args.target]
        seed_path = ROOT / "scripts" / "seeds" / f"{args.target}.lean"
        if not seed_path.exists():
            print(f"verify-only: no seed at {seed_path}", flush=True)
            REPORT_FILE.write_text(f"# verify-only\n\nno seed at {seed_path}\n", encoding="utf-8")
            return 1
        body = seed_path.read_text(encoding="utf-8")
        ok, out = tool_run_lean(target, body)
        REPORT_FILE.write_text(
            f"# verify-only: `{target.name}`\n\n**ok={ok}**\n\n```lean\n{body}\n```\n\n"
            f"### kernel output\n```\n{out[-9000:]}\n```\n", encoding="utf-8")
        print(f"\nVERIFY-ONLY ok={ok}\n", flush=True)
        print(out[-5000:], flush=True)
        if ok:
            SUCCESS_FILE.write_text(WORK_FILE.read_text(encoding="utf-8"), encoding="utf-8")
            print("\nSUCCESS: kernel accepts the seed candidate.", flush=True)
        return 0

    key = os.environ.get("KIMI_API_KEY", "").strip()
    if not key:
        print("KIMI_API_KEY is missing — no-op.", flush=True)
        REPORT_FILE.write_text("# Kimi agent-prover\n\nKIMI_API_KEY is missing.\n", encoding="utf-8")
        return 0

    from openai import OpenAI
    client = OpenAI(base_url=os.environ.get("KIMI_BASE_URL") or "https://api.moonshot.ai/v1",
                    api_key=key, timeout=300.0)
    model = os.environ.get("KIMI_MODEL") or "kimi-k3"
    target = TARGETS[args.target]

    REPORT_FILE.write_text(
        f"# Kimi agent-prover\n\nTarget: `{target.name}`\nModel: `{model}`  "
        f"(tools: grep, read_file, run_lean)\n\n{target.description}\n\n", encoding="utf-8")

    system = (
        "You are a Lean 4 + Mathlib proof engineer with TOOLS: `grep` (scope='ecdlp' for this repo; "
        "scope='mathlib' to read the REAL WeierstrassCurve.Ψ₂Sq/ΨSq/Φ/preΨ' definitions in the "
        "installed Mathlib source), `read_file`, and `run_lean` (compiles your proof — the SOLE "
        "judge). Prove the given theorem. Work FAST and EMPIRICALLY: do NOT over-search — after a "
        "few greps, ATTEMPT a proof with run_lean and let the kernel's error drive your next step. "
        "A failed run_lean teaches you more than another grep. Good openers to TRY early: "
        "`simp only [WeierstrassCurve.ΨSq, WeierstrassCurve.Φ, ...]; ring`, or unfold the division "
        "polynomials then `ring`/`ring_nf`. Iterate: attempt → read error → repair. You are DONE "
        "only when run_lean returns ok=true. Never invent lemma names — grep to confirm. If the "
        "theorem is actually false, say so explicitly with counter-evidence.")
    user = (f"Prove this theorem (fill the tactic block after `by`). The file preamble/imports are "
            f"fixed; you only supply the proof body.\n\n```lean\n{target.stem}```\n\nHint: {target.hint}")

    # Resume-seed: if a prior run's near-complete proof body was saved under scripts/seeds/<target>.lean,
    # hand it back to Kimi so it CONTINUES from ~90% instead of re-deriving from scratch. This is Kimi's
    # OWN prior output — the seed only proposes; run_lean/CI remains the sole verifier.
    seed_path = ROOT / "scripts" / "seeds" / f"{args.target}.lean"
    seed = seed_path.read_text(encoding="utf-8") if seed_path.exists() else ""
    if seed.strip():
        user += (
            "\n\nThis proof body is MECHANICALLY COMPLETE and compiles all the way to the final "
            "`ring` — every `have` (hBval=4X³+28, hBne, hSd = R²·Ψ₂Sq², the recurrences, index "
            "normalization, the parity by_cases) is correct and type-checks. The ONE remaining "
            "problem is the final `ring`: it runs but returns a LARGE NON-ZERO RESIDUAL (a polynomial "
            "in `preΨ(t-2..t+3)` and X). Because `ring` is complete, that means the identity is NOT a "
            "free polynomial identity in the `preΨ(t±j)` — it holds only MODULO the elliptic-net / "
            "Somos-4 relation among consecutive `preΨ`.\n"
            "YOUR JOB — close that last gap (this is the real mathematics):\n"
            "  • Option A: the target already imports NormEDSSomos4. grep it (scope='ecdlp') for the "
            "Somos-4 / preΨ four-term relation, then replace the final `ring` with `linear_combination "
            "<coeff> * <that relation>` (or `rw` the relation into the residual, then `ring`).\n"
            "  • Option B: look for a DIRECT Mathlib doubling lemma — grep scope='mathlib' for "
            "`Ψ.*two_mul`, `ΨSq.*two_mul`, `preΨ.*two_mul`, `Ψ_two`, `two_mul` near the division-"
            "polynomial files — and use it to avoid the manual expansion entirely.\n"
            "Keep the mechanically-correct scaffold below; only change how the final per-branch goal "
            f"is closed. run_lean is the sole judge.\n\n```lean\n{seed.strip()}\n```")
        print(f"seed loaded: {seed_path.relative_to(ROOT)} ({seed.count(chr(10))+1} lines)", flush=True)

    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    solved, winning = False, ""
    searches_since_lean = 0   # consecutive turns with no run_lean attempt

    for it in range(1, args.max_iters + 1):
        # kimi-k3 tends to explore forever without ever compiling. After a few search-only turns,
        # FORCE a run_lean so the kernel error can drive it — a failed attempt beats endless grep.
        force_lean = searches_since_lean >= 5
        tc_choice = ({"type": "function", "function": {"name": "run_lean"}}
                     if force_lean else "auto")
        try:
            resp = client.chat.completions.create(
                model=model, messages=messages, tools=TOOLS, tool_choice=tc_choice,
                temperature=1.0, max_tokens=args.max_tokens)
        except Exception as e:  # noqa: BLE001
            if force_lean:
                # Some providers reject a forced function choice; fall back to auto, don't lose the run.
                print(f"::warning::forced run_lean rejected at iter {it}: {e}; retrying auto", flush=True)
                try:
                    resp = client.chat.completions.create(
                        model=model, messages=messages, tools=TOOLS, tool_choice="auto",
                        temperature=1.0, max_tokens=args.max_tokens)
                except Exception as e2:  # noqa: BLE001
                    print(f"::warning::kimi call failed at iter {it}: {e2}", flush=True)
                    report(f"## iter {it}: API failure\n\n```\n{e2}\n```\n\n")
                    break
            else:
                print(f"::warning::kimi call failed at iter {it}: {e}", flush=True)
                report(f"## iter {it}: API failure\n\n```\n{e}\n```\n\n")
                break
        if force_lean:
            print(f"--- iter {it}: FORCED run_lean ({searches_since_lean} search-only turns) ---", flush=True)
            report(f"_iter {it}: forced run_lean after {searches_since_lean} search-only turns_\n\n")

        choice = resp.choices[0]
        msg = choice.message
        finish = choice.finish_reason
        content = (msg.content or "").strip()
        # kimi-k3 is a reasoning model: its visible `content` is often empty while the private
        # chain-of-thought lands in `reasoning_content`. Surface that so the report shows what Kimi
        # is actually thinking (and so an empty `content` isn't mistaken for "said nothing").
        reasoning = (getattr(msg, "reasoning_content", None) or "").strip()
        if content:
            print(f"\n=== iter {it} — Kimi says ===\n{content[:1200]}", flush=True)
            report(f"## iter {it} — Kimi\n\n{content[:1500]}\n\n")
        elif reasoning:
            print(f"\n=== iter {it} — Kimi (reasoning) ===\n{reasoning[:800]}", flush=True)
            report(f"## iter {it} — Kimi (reasoning)\n\n{reasoning[:1200]}\n\n")

        if msg.tool_calls:
            # Assistant turn that carries tool calls. Moonshot 400s on empty-STRING content beside
            # tool_calls, so use None (the OpenAI "tool calls only" form).
            messages.append({
                "role": "assistant", "content": msg.content or None,
                "tool_calls": [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls]})
        else:
            # No tool call this turn. NEVER append an empty assistant message — Moonshot rejects the
            # WHOLE history on the next call ("message ... with role 'assistant' must not be empty").
            # This is the real killer: kimi-k3's reasoning can eat the whole token budget, ending a
            # turn with empty content AND no tool call. Keep the turn only if it has real text; then
            # nudge the model to actually act via a tool.
            if content:
                messages.append({"role": "assistant", "content": content})
            searches_since_lean += 1   # a prose/reasoning-only turn is not a proof attempt
            if finish == "length":
                nudge = ("Your last turn was truncated by the token limit before you emitted a tool "
                         "call. Be terse — no long prose: go STRAIGHT to ONE run_lean with a compact "
                         "proof, or ONE grep for a lemma name.")
            else:
                nudge = ("Not accepted yet. Call run_lean to test a proof, or grep/read_file to find "
                         "the exact lemma names you need. Act via a tool call, not prose.")
            messages.append({"role": "user", "content": nudge})
            continue

        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                a = json.loads(tc.function.arguments or "{}")
            except Exception:
                a = {}
            if name == "grep":
                pat = a.get("pattern", "")
                scope = a.get("scope", "ecdlp")
                res = tool_grep(pat, a.get("glob"), scope)
                print(f"--- iter {it}: grep [{scope}] {pat!r} ---", flush=True)
                report(f"### iter {it}: grep `{pat}` (scope={scope})\n\n```\n{res[:800]}\n```\n\n")
            elif name == "read_file":
                path = a.get("path", "")
                res = tool_read_file(path, int(a.get("start", 1) or 1),
                                     min(400, int(a.get("count", 200) or 200)))
                print(f"--- iter {it}: read_file {path} ---", flush=True)
                report(f"### iter {it}: read_file `{path}` (lines "
                       f"{int(a.get('start', 1) or 1)}+)\n\n")
            elif name == "run_lean":
                body = a.get("proof_body", "")
                ok, out = tool_run_lean(target, body)
                print(f"--- iter {it}: run_lean ok={ok} ---\n{body[:600]}", flush=True)
                report(f"### iter {it}: run_lean ok={ok}\n\n```lean\n{body}\n```\n\n"
                       f"```\n{out[-1500:]}\n```\n\n")
                res = json.dumps({"ok": ok, "lean_output": out[-4000:]})
                if ok:
                    solved, winning = True, body
            else:
                res = f"unknown tool {name}"
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(res)[:MAX_TOOL_OUTPUT]})

        # Reset the stall counter only when this turn actually compiled something.
        did_lean = any(tc.function.name == "run_lean" for tc in msg.tool_calls)
        searches_since_lean = 0 if did_lean else searches_since_lean + 1

        if solved:
            break

    if solved:
        SUCCESS_FILE.write_text(WORK_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        report(f"\n## RESULT: SUCCESS\n\nKernel-accepted proof body:\n\n```lean\n{winning}\n```\n")
        print("\nSUCCESS: Lean accepted a Kimi candidate.", flush=True)
    else:
        report("\n## RESULT: no kernel-accepted proof within the budget.\n")
        print("\nNO PROOF within budget (artifact-only; exit 0).", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
