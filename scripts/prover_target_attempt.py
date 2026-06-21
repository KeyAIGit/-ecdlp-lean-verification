#!/usr/bin/env python3
"""Try to prove selected Lean targets with Featherless prover models.

This is an artifact-only workflow: it writes reports and candidate Lean files,
but it does not modify the verified proof base or commit model output to main.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

API_URL = "https://api.featherless.ai/v1/chat/completions"
WORK_FILE = Path("ProverTargetAttempt.lean")
REPORT_FILE = Path("prover-target-report.md")
SUCCESS_FILE = Path("prover-target-success.lean")

PYTHAGORAS_4B = "Pythagoras-LM/Pythagoras-Prover-4B"
GOEDEL_32B = "Goedel-LM/Goedel-Prover-V2-32B"


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
        stem=textwrap.dedent(
            """
            import Mathlib

            example (a b : Nat) : a + b = b + a := by
            """
        ).lstrip(),
        hint="This is a very small Nat arithmetic theorem.",
    ),
    "zmod_from_mod_zero": Target(
        name="zmod_from_mod_zero",
        description="Real target pattern used by Ecdlp.Targets.glv_eigenvalue_zmod.",
        stem=textwrap.dedent(
            """
            import Mathlib

            namespace Ecdlp.ProverAttempt

            theorem zmod_from_mod_zero (n lam : Nat) (h : (lam ^ 2 + lam + 1) % n = 0) :
                ((lam : ZMod n) ^ 2 + (lam : ZMod n) + 1) = 0 := by
            """
        ).lstrip(),
        hint=(
            "Useful direction: convert the Nat mod-zero hypothesis to a divisibility fact, "
            "then prove the corresponding natural number casts to zero in ZMod n. "
            "Mathlib tactics like push_cast, ring, rw, exact, simpa, or linear_combination may help."
        ),
    ),
    "lambda_cube_root_shape": Target(
        name="lambda_cube_root_shape",
        description="Small algebraic shape target related to cube-root identities.",
        stem=textwrap.dedent(
            """
            import Mathlib

            namespace Ecdlp.ProverAttempt

            example {R : Type} [CommRing R] (x : R) (h : x ^ 2 + x + 1 = 0) :
                x ^ 3 = 1 := by
            """
        ).lstrip(),
        hint="Use h and ring/linear algebraic manipulation in a commutative ring.",
    ),
}


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
        cleaned = "  simp"

    normalized = []
    for line in cleaned.splitlines():
        if line.strip():
            normalized.append("  " + line.strip())
        else:
            normalized.append("")
    return "\n".join(normalized).rstrip() + "\n"


def make_prompt(target: Target, previous_error: str | None = None) -> str:
    parts = [
        "Complete this Lean 4 / Mathlib proof.",
        "Return ONLY the proof body that should appear after `by`.",
        "Do not include prose. Do not include Markdown fences. Do not repeat the theorem.",
        "",
        f"Target: {target.name}",
        f"Hint: {target.hint}",
        "",
        "```lean",
        target.stem.rstrip(),
        "```",
    ]
    if previous_error:
        parts.extend(
            [
                "",
                "Previous Lean error/output to repair:",
                "```text",
                previous_error[-4000:],
                "```",
            ]
        )
    return "\n".join(parts)


def call_model(api_key: str, model: str, target: Target, attempt: int, previous_error: str | None) -> str:
    prompt = make_prompt(target, previous_error)
    temperature = min(0.9, 0.15 + 0.06 * attempt)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a Lean 4 theorem prover. Return only valid Lean proof code after `by`.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": 900,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=240) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Featherless HTTP {exc.code}: {error_body}") from exc

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
    args = parser.parse_args()

    api_key = os.environ.get("FEATHERLESS_API_KEY", "").strip()
    if not api_key:
        print("FEATHERLESS_API_KEY is missing", file=sys.stderr)
        return 2

    target = TARGETS[args.target]
    REPORT_FILE.write_text(
        f"# Prover target attempt\n\n"
        f"Target: `{target.name}`\n\n"
        f"Description: {target.description}\n\n"
        f"Fast model: `{args.fast_model}` × {args.fast_attempts}\n\n"
        f"Heavy model: `{args.heavy_model}` × {args.heavy_attempts}\n\n",
        encoding="utf-8",
    )

    previous_error: str | None = None
    sequence: list[tuple[str, int, str]] = []
    sequence.extend((args.fast_model, i, "fast") for i in range(1, args.fast_attempts + 1))
    sequence.extend((args.heavy_model, i, "heavy") for i in range(1, args.heavy_attempts + 1))

    infrastructure_error = False
    solved = False

    for model, attempt, phase in sequence:
        print(f"{phase.upper()} attempt {attempt} with {model} on {target.name}")
        try:
            raw = call_model(api_key, model, target, attempt, previous_error)
        except Exception as exc:  # noqa: BLE001
            infrastructure_error = True
            msg = f"Model/API call failed for {model}: {exc}"
            print(msg)
            append_report(f"## {phase} attempt {attempt}: API/model failure\n\n```text\n{msg}\n```\n\n")
            continue

        candidate = clean_candidate(raw)
        print("Candidate proof body:")
        print(candidate)
        ok, output = run_lean(target, candidate)
        append_report(
            f"## {phase} attempt {attempt} — `{model}`\n\n"
            f"Candidate:\n\n```lean\n{candidate}```\n\n"
            f"Lean output:\n\n```text\n{output[-6000:]}\n```\n\n"
        )
        if ok:
            SUCCESS_FILE.write_text(WORK_FILE.read_text(encoding="utf-8"), encoding="utf-8")
            append_report("\n## Result\n\nSUCCESS: Lean accepted this candidate.\n")
            print("SUCCESS: Lean accepted this candidate.")
            solved = True
            break

        previous_error = output or "Lean rejected this candidate without output."
        print("Lean rejected candidate; will pass error to next attempt.")

    if not solved:
        append_report("\n## Result\n\nNo candidate passed Lean in this run. This is not a verified failure of the theorem; it only means this attempt budget did not find a proof.\n")
        print("NO PROOF FOUND within attempt budget. Workflow exits 0 because this is an artifact-only search.")

    if infrastructure_error:
        append_report("\nNote: at least one model/API call failed. Check whether the model is available on the current plan.\n")

    # Exit 0 intentionally: failed proof search is a result, not a broken repository.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
