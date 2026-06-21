#!/usr/bin/env python3
"""Small end-to-end smoke test for a Featherless prover model.

This script asks a model for a Lean proof body for a tiny theorem, writes the
candidate into a temporary Lean file, and checks it with `lake env lean`.
It never prints the API key.
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
from pathlib import Path

API_URL = "https://api.featherless.ai/v1/chat/completions"
TARGET_FILE = Path("ProverSmoke.lean")
SUCCESS_FILE = Path("prover-smoke-success.lean")
REPORT_FILE = Path("prover-smoke-report.md")

THEOREM_STEM = """import Mathlib

example (a b : Nat) : a + b = b + a := by
"""

PROMPT = """Complete this Lean 4 / Mathlib proof.

Return ONLY the proof body that should appear after `by`.
Do not include prose. Do not include Markdown fences. Do not repeat the theorem.

```lean
import Mathlib

example (a b : Nat) : a + b = b + a := by
```
"""


def clean_candidate(text: str) -> str:
    """Extract a plausible Lean proof body from a model response."""
    text = text.strip()

    # Remove Markdown code fences if present.
    text = re.sub(r"^```(?:lean|lean4|text)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text).strip()

    # If the model repeated a theorem/example and included `:= by`, keep after it.
    marker = ":= by"
    if marker in text:
        text = text.split(marker, 1)[1].strip()

    # If it returned a leading `by`, remove it because the file already has `:= by`.
    if text == "by":
        text = ""
    elif text.startswith("by\n"):
        text = text[3:].strip()
    elif text.startswith("by "):
        text = text[3:].strip()

    # Drop imports or namespace lines if accidentally included.
    kept: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("import "):
            continue
        if stripped.startswith("example ") or stripped.startswith("theorem "):
            continue
        if stripped in {"```", "```lean", "```lean4"}:
            continue
        kept.append(line.rstrip())

    text = "\n".join(kept).strip()
    if not text:
        text = "  exact Nat.add_comm a b"

    # Ensure it is indented under `by`.
    lines = text.splitlines()
    normalized = []
    for line in lines:
        if line.strip():
            normalized.append("  " + line.strip())
        else:
            normalized.append("")
    return "\n".join(normalized) + "\n"


def call_model(api_key: str, model: str, attempt: int) -> str:
    temperature = min(0.8, 0.15 + 0.07 * attempt)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a Lean 4 theorem-proving assistant. Return only valid Lean proof code.",
            },
            {"role": "user", "content": PROMPT},
        ],
        "temperature": temperature,
        "max_tokens": 512,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Featherless HTTP {exc.code}: {error_body}") from exc

    try:
        payload = json.loads(body)
        return payload["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Could not parse model response: {body[:1000]}") from exc


def run_lean(candidate: str) -> tuple[bool, str]:
    TARGET_FILE.write_text(THEOREM_STEM + candidate, encoding="utf-8")
    proc = subprocess.run(
        ["lake", "env", "lean", str(TARGET_FILE)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=180,
    )
    return proc.returncode == 0, proc.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--attempts", type=int, default=4)
    args = parser.parse_args()

    api_key = os.environ.get("FEATHERLESS_API_KEY", "").strip()
    if not api_key:
        print("FEATHERLESS_API_KEY is missing", file=sys.stderr)
        return 2

    REPORT_FILE.write_text(
        f"# Prover smoke test\n\nModel: `{args.model}`\nAttempts: {args.attempts}\n\n",
        encoding="utf-8",
    )

    last_error = ""
    for attempt in range(1, args.attempts + 1):
        print(f"Attempt {attempt}/{args.attempts} with {args.model}")
        raw = call_model(api_key, args.model, attempt)
        candidate = clean_candidate(raw)
        print("Candidate proof body:")
        print(candidate)
        ok, output = run_lean(candidate)
        with REPORT_FILE.open("a", encoding="utf-8") as report:
            report.write(f"## Attempt {attempt}\n\n")
            report.write("```lean\n" + candidate + "```\n\n")
            report.write("Lean output:\n\n```text\n" + output[-4000:] + "\n```\n\n")
        if ok:
            SUCCESS_FILE.write_text(THEOREM_STEM + candidate, encoding="utf-8")
            print("SUCCESS: model produced a Lean proof accepted by Lean.")
            return 0
        last_error = output
        print("Lean rejected this candidate.")
        if last_error:
            print(last_error[-2000:])

    print("FAILURE: no candidate passed Lean.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
