#!/usr/bin/env python3
"""Try to prove selected Lean targets with Featherless prover models.

Artifact-only workflow: it writes reports and candidate Lean files, but it does
not modify the verified proof base or commit model output to main.

The agent protocol lives in AGENTS.md (§Prover-loop protocol). Prompts live in prompts/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

API_URL = "https://api.featherless.ai/v1/chat/completions"
# Featherless sits behind Cloudflare, which 403s (error 1010) the default
# `Python-urllib` User-Agent. Send a browser-like UA so requests aren't blocked.
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
WORK_FILE = Path("ProverTargetAttempt.lean")
REPORT_FILE = Path("prover-target-report.md")
SUCCESS_FILE = Path("prover-target-success.lean")
PROMPT_DIR = Path("prompts")

PYTHAGORAS_4B = "Pythagoras-LM/Pythagoras-Prover-4B"
GOEDEL_32B = "Goedel-LM/Goedel-Prover-V2-32B"
# A structurally different Lean-RL prover (AIMO). Used as a final escalation tier: it catches goals
# the Goedel model misses, and vice-versa. Free on the Featherless plan. Override via targets/*.json
# budget "kimina_model" if a larger Kimina becomes available on the plan.
KIMINA_PROVER = "AI-MO/Kimina-Prover-Distill-8B"

# Moonshot/Kimi as a general drafter tier: kimi-k3 (the 2.8T flagship) drafts Lean, the kernel
# (`lake env lean`) re-checks every attempt exactly as for the Featherless provers. Drafter only.
# `or` (not a get-default): CI sets these env vars to "" when the secret is undefined, and an
# empty string must fall back to the default rather than becoming a broken URL / model id.
MOONSHOT_URL = os.environ.get("KIMI_CHAT_URL") or "https://api.moonshot.ai/v1/chat/completions"
KIMI_K3 = os.environ.get("KIMI_MODEL") or "kimi-k3"

# provider → (chat-completions URL, api-key env var, User-Agent or None, max_tokens).
# Featherless sits behind Cloudflare (needs a browser UA); Moonshot is plain OpenAI-compatible.
# kimi-k3 is verbose, so it gets a larger token budget to avoid truncated proof bodies.
PROVIDERS: dict[str, tuple[str, str, str | None, int]] = {
    "featherless": (API_URL, "FEATHERLESS_API_KEY", USER_AGENT, 1000),
    "moonshot": (MOONSHOT_URL, "KIMI_API_KEY", None, 4000),
}


@dataclass(frozen=True)
class Target:
    name: str
    description: str
    stem: str
    hint: str


TARGETS: dict[str, Target] = {
    "nat_add_comm": Target(
        name="nat_add_comm",
        description="Tiny sanity target: commutativity of Nat addition.",
        stem="""import Mathlib

example (a b : Nat) : a + b = b + a := by
""",
        hint="This is a very small Nat arithmetic theorem.",
    ),
    "zmod_from_mod_zero": Target(
        name="zmod_from_mod_zero",
        description="Real target pattern used by Ecdlp.Targets.glv_eigenvalue_zmod.",
        stem="""import Mathlib

namespace Ecdlp.ProverAttempt

theorem zmod_from_mod_zero (n lam : Nat) (h : (lam ^ 2 + lam + 1) % n = 0) :
    ((lam : ZMod n) ^ 2 + (lam : ZMod n) + 1) = 0 := by
""",
        hint=(
            "Convert h to divisibility with Nat.dvd_of_mod_eq_zero; then show the corresponding "
            "Nat cast is zero in ZMod n. Useful tools: obtain, rw, push_cast, "
            "ZMod.natCast_self, ring, linear_combination, simpa."
        ),
    ),
    "lambda_cube_root_shape": Target(
        name="lambda_cube_root_shape",
        description="Small algebraic shape target related to cube-root identities.",
        stem="""import Mathlib

namespace Ecdlp.ProverAttempt

example {R : Type} [CommRing R] (x : R) (h : x ^ 2 + x + 1 = 0) :
    x ^ 3 = 1 := by
""",
        hint="Use h and ring/linear algebraic manipulation in a commutative ring.",
    ),
}


def read_prompt(filename: str, fallback: str) -> str:
    path = PROMPT_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return fallback


def render_template(template: str, values: dict[str, str]) -> str:
    result = template
    for key, value in values.items():
        result = result.replace("{{" + key + "}}", value)
    return result


def close_namespace_if_needed(stem: str) -> str:
    return "\nend Ecdlp.ProverAttempt\n" if "namespace Ecdlp.ProverAttempt" in stem else ""


def clean_candidate(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:lean|lean4|text)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text).strip()

    marker = ":= by"
    if marker in text:
        text = text.split(marker, 1)[1].strip()

    if text.startswith("by\n"):
        text = text[3:].strip()
    elif text.startswith("by "):
        text = text[3:].strip()
    elif text == "by":
        text = ""

    kept: list[str] = []
    skip_prefixes = ("import ", "theorem ", "example ", "namespace ", "end ")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            kept.append("")
            continue
        if stripped in {"```", "```lean", "```lean4"}:
            continue
        if stripped.startswith(skip_prefixes):
            continue
        kept.append(line.rstrip())

    cleaned = "\n".join(kept).strip()
    if not cleaned:
        cleaned = "simp"

    normalized = []
    for line in cleaned.splitlines():
        if line.strip():
            normalized.append("  " + line.strip())
        else:
            normalized.append("")
    return "\n".join(normalized).rstrip() + "\n"


def make_prompt(target: Target, previous_candidate: str | None, previous_error: str | None) -> str:
    if previous_error:
        template = read_prompt(
            "lean_repair_prompt.md",
            "Repair the Lean proof. Return only the proof body after by.\n{{THEOREM_STEM}}\n{{LEAN_ERROR}}",
        )
        return render_template(
            template,
            {
                "THEOREM_STEM": target.stem.rstrip(),
                "TARGET_HINT": target.hint,
                "PREVIOUS_CANDIDATE": previous_candidate or "",
                "LEAN_ERROR": previous_error[-5000:],
            },
        )

    template = read_prompt(
        "lean_prover_prompt.md",
        "Complete this Lean proof. Return only the proof body after by.\n{{THEOREM_STEM}}",
    )
    return render_template(
        template,
        {
            "THEOREM_STEM": target.stem.rstrip(),
            "TARGET_HINT": target.hint,
        },
    )


def call_model(
    provider: str,
    api_key: str,
    model: str,
    target: Target,
    attempt: int,
    previous_candidate: str | None,
    previous_error: str | None,
) -> str:
    url, _, user_agent, max_tokens = PROVIDERS[provider]
    prompt = make_prompt(target, previous_candidate, previous_error)
    temperature = min(0.9, 0.15 + 0.06 * attempt)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a Lean 4 proof engineer. Return only valid Lean code after `by`.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if user_agent:
        headers["User-Agent"] = user_agent
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=240) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{provider} HTTP {exc.code}: {error_body}") from exc

    parsed = json.loads(body)
    return parsed["choices"][0]["message"]["content"]


def write_candidate_file(target: Target, candidate: str) -> None:
    WORK_FILE.write_text(target.stem + candidate + close_namespace_if_needed(target.stem), encoding="utf-8")


def run_lean(target: Target, candidate: str) -> tuple[bool, str]:
    write_candidate_file(target, candidate)
    proc = subprocess.run(
        ["lake", "env", "lean", str(WORK_FILE)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=240,
    )
    return proc.returncode == 0, proc.stdout


def append_report(text: str) -> None:
    with REPORT_FILE.open("a", encoding="utf-8") as f:
        f.write(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=sorted(TARGETS), default="zmod_from_mod_zero")
    parser.add_argument("--fast-attempts", type=int, default=4)
    parser.add_argument("--heavy-attempts", type=int, default=2)
    parser.add_argument("--fast-model", default=PYTHAGORAS_4B)
    parser.add_argument("--heavy-model", default=GOEDEL_32B)
    parser.add_argument("--kimina-model", default=KIMINA_PROVER)
    parser.add_argument("--kimina-attempts", type=int, default=2)
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="featherless",
                        help="drafter provider; 'moonshot' routes all attempts to Kimi")
    parser.add_argument("--kimi-model", default=KIMI_K3)
    parser.add_argument("--kimi-attempts", type=int, default=6,
                        help="draft→verify→repair rounds when --provider moonshot")
    args = parser.parse_args()

    key_env = PROVIDERS[args.provider][1]
    api_key = os.environ.get(key_env, "").strip()
    if not api_key:
        print(f"{key_env} is missing", flush=True)
        REPORT_FILE.write_text(f"# Prover target attempt\n\n{key_env} is missing.\n", encoding="utf-8")
        return 0

    target = TARGETS[args.target]

    previous_error: str | None = None
    previous_candidate: str | None = None
    sequence: list[tuple[str, int, str]] = []
    if args.provider == "moonshot":
        sequence.extend((args.kimi_model, i, "kimi") for i in range(1, args.kimi_attempts + 1))
        models_line = f"Model: `{args.kimi_model}` × {args.kimi_attempts}"
    else:
        sequence.extend((args.fast_model, i, "fast") for i in range(1, args.fast_attempts + 1))
        sequence.extend((args.heavy_model, i, "heavy") for i in range(1, args.heavy_attempts + 1))
        sequence.extend((args.kimina_model, i, "kimina") for i in range(1, args.kimina_attempts + 1))
        models_line = (f"Fast `{args.fast_model}` × {args.fast_attempts}; "
                       f"heavy `{args.heavy_model}` × {args.heavy_attempts}; "
                       f"kimina `{args.kimina_model}` × {args.kimina_attempts}")

    REPORT_FILE.write_text(
        f"# Prover target attempt\n\n"
        f"Target: `{target.name}`\n\n"
        f"Description: {target.description}\n\n"
        f"Provider: `{args.provider}`\n\n"
        f"{models_line}\n\n"
        f"Prompt source: `prompts/lean_prover_prompt.md`, `prompts/lean_repair_prompt.md`\n\n",
        encoding="utf-8",
    )

    infrastructure_error = False
    solved = False

    for model, attempt, phase in sequence:
        print(f"{phase.upper()} attempt {attempt} with {model} on {target.name}", flush=True)
        try:
            raw = call_model(args.provider, api_key, model, target, attempt, previous_candidate, previous_error)
        except Exception as exc:  # noqa: BLE001
            infrastructure_error = True
            msg = f"Model/API call failed for {model}: {exc}"
            print(msg, flush=True)
            append_report(f"## {phase} attempt {attempt}: API/model failure\n\n```text\n{msg}\n```\n\n")
            continue

        candidate = clean_candidate(raw)
        previous_candidate = candidate
        print("Candidate proof body:", flush=True)
        print(candidate, flush=True)
        ok, output = run_lean(target, candidate)
        append_report(
            f"## {phase} attempt {attempt} — `{model}`\n\n"
            f"Candidate:\n\n```lean\n{candidate}```\n\n"
            f"Lean output:\n\n```text\n{output[-6000:]}\n```\n\n"
        )
        if ok:
            SUCCESS_FILE.write_text(WORK_FILE.read_text(encoding="utf-8"), encoding="utf-8")
            append_report("\n## Result\n\nSUCCESS: Lean accepted this candidate.\n")
            print("SUCCESS: Lean accepted this candidate.", flush=True)
            solved = True
            break

        previous_error = output or "Lean rejected this candidate without output."
        print("Lean rejected candidate; will pass error to next repair attempt.", flush=True)

    if not solved:
        append_report(
            "\n## Result\n\nNo candidate passed Lean in this run. "
            "This is not a verified failure of the theorem; it only means this attempt budget did not find a proof.\n"
        )
        print("NO PROOF FOUND within attempt budget. Artifact-only search exits 0.", flush=True)

    if infrastructure_error:
        append_report("\nNote: at least one model/API call failed. Check whether the model is available on the current plan.\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
