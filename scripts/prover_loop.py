#!/usr/bin/env python3
"""Autonomous prover loop over the `targets/` registry (Layer 2).

For each open target it tries, in order:
  Tier 0  - a zero-cost Lean tactic ladder (no API calls):
            rfl, decide, native_decide, simp, omega, ring, aesop.
  Tier 1  - Featherless Pythagoras-Prover-4B (fast first pass).
  Tier 2  - Featherless Goedel-Prover-V2-32B (heavier repair), each repair
            attempt fed the exact Lean error from the previous try.

This is an **artifact-only** search: it writes a report and Lean-accepted
candidate files under `candidates/`, but it NEVER edits the verified proof base.
Promotion to `Ecdlp/Proved/` happens via a reviewed PR (see prove.yml). The Lean
kernel is the only judge: a candidate counts only if `lake env lean` accepts it.

Shared helpers (model call, candidate cleaning, model ids) are reused from
`prover_target_attempt.py` to avoid duplication.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prover_target_attempt import (  # noqa: E402
    GOEDEL_32B,
    KIMINA_PROVER,
    PYTHAGORAS_4B,
    USER_AGENT,
    Target,
    call_model,
    clean_candidate,
)

REGISTRY_DIR = Path("targets")
REPORT_FILE = Path("prover-loop-report.md")
CANDIDATES_DIR = Path("candidates")
WORK_FILE = Path("ProverLoopAttempt.lean")
API_MODELS_URL = "https://api.featherless.ai/v1/models?available_on_current_plan=true"


def probe_models(api_key: str) -> dict:
    """Report whether the two prover models are available on the current plan.
    Surfaces the common failure mode (models not on plan -> every model call errors)."""
    req = urllib.request.Request(
        API_MODELS_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"[loop] model-availability probe FAILED: {exc}", flush=True)
        return {}
    ids = [m.get("id", "") for m in data.get("data", []) if isinstance(m, dict)]
    print(f"[loop] Featherless: {len(ids)} models available on current plan", flush=True)
    avail = {}
    for m in (PYTHAGORAS_4B, GOEDEL_32B):
        short = m.split("/")[-1].lower()
        avail[m] = any(short in x.lower() for x in ids)
    return avail

# Zero-cost first pass: each tactic is tried as the entire proof body.
TACTIC_LADDER = ["rfl", "decide", "native_decide", "simp", "omega", "ring", "aesop"]

OPEN_STATUSES = {"todo", "searching"}


def stem_namespace(stem: str) -> str | None:
    m = re.search(r"^\s*namespace\s+(\S+)", stem, re.MULTILINE)
    return m.group(1) if m else None


def stem_from_file(path: Path) -> str:
    """Derive a prover stem (everything up to and including `:= by`) from an
    `Ecdlp/Targets/<id>.lean` open-conjecture file (which ends in `sorry`)."""
    text = path.read_text(encoding="utf-8")
    marker = ":= by"
    if marker not in text:
        raise ValueError(f"{path} has no ':= by' marker")
    return text.split(marker, 1)[0] + marker + "\n"


def get_stem(spec: dict) -> str:
    sf = spec.get("stem_file")
    if sf and Path(sf).exists():
        return stem_from_file(Path(sf))
    if spec.get("lean_stem"):
        return spec["lean_stem"]
    raise ValueError(f"target {spec.get('id')} has neither a usable stem_file nor lean_stem")


def build_file(stem: str, body: str) -> str:
    ns = stem_namespace(stem)
    tail = f"\nend {ns}\n" if ns else "\n"
    return stem + body + tail


def run_lean(stem: str, body: str) -> tuple[bool, str]:
    WORK_FILE.write_text(build_file(stem, body), encoding="utf-8")
    proc = subprocess.run(
        ["lake", "env", "lean", str(WORK_FILE)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=300,
    )
    return proc.returncode == 0, proc.stdout


def try_tactic_ladder(stem: str) -> tuple[bool, str | None, str]:
    log: list[str] = []
    for tac in TACTIC_LADDER:
        ok, _ = run_lean(stem, f"  {tac}\n")
        log.append(f"- `{tac}`: {'OK' if ok else 'no'}")
        if ok:
            return True, tac, "\n".join(log)
    return False, None, "\n".join(log)


def load_specs() -> list[dict]:
    specs = []
    for p in sorted(REGISTRY_DIR.glob("*.json")):
        spec = json.loads(p.read_text(encoding="utf-8"))
        # Skip foreign registry files that share targets/ but are not loop targets
        # (e.g. queue.json, agent_day's `{_comment, targets}` schema — no top-level `id`).
        if not isinstance(spec, dict) or "id" not in spec:
            continue
        spec["_path"] = str(p)
        specs.append(spec)
    return specs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="restrict to a single target id")
    ap.add_argument("--tier0-only", action="store_true", help="skip the model tiers")
    args = ap.parse_args()

    api_key = os.environ.get("FEATHERLESS_API_KEY", "").strip()
    print(f"[loop] FEATHERLESS_API_KEY present: {bool(api_key)}", flush=True)
    avail = probe_models(api_key) if api_key else {}
    for _m in (PYTHAGORAS_4B, GOEDEL_32B):
        print(f"[loop] model on plan? {_m}: {avail.get(_m)}", flush=True)
    specs = load_specs()
    open_specs = [s for s in specs if s.get("status", "todo") in OPEN_STATUSES]
    if args.only:
        open_specs = [s for s in open_specs if s.get("id") == args.only]

    CANDIDATES_DIR.mkdir(exist_ok=True)
    report: list[str] = ["# Prover loop report\n"]
    report.append(f"Open targets: {len(open_specs)} (of {len(specs)} registered).\n")
    any_solved = False

    for spec in open_specs:
        tid = spec.get("id", "<no-id>")
        report.append(f"\n## Target `{tid}`\n")
        try:
            stem = get_stem(spec)
        except Exception as exc:  # noqa: BLE001
            report.append(f"SKIP: {exc}\n")
            print(f"SKIP {tid}: {exc}", flush=True)
            continue

        ok, tac, ladder_log = try_tactic_ladder(stem)
        report.append("### Tier 0 - tactic ladder\n" + ladder_log + "\n")
        if ok:
            (CANDIDATES_DIR / f"{tid}.lean").write_text(build_file(stem, f"  {tac}\n"), encoding="utf-8")
            report.append(f"\n**SOLVED by tier 0:** `{tac}`\n")
            print(f"SOLVED {tid} via tier-0 `{tac}`", flush=True)
            any_solved = True
            continue

        if args.tier0_only:
            report.append("tier0-only mode: models skipped.\n")
            continue
        if not api_key:
            report.append("No FEATHERLESS_API_KEY available: model tiers skipped.\n")
            print(f"{tid}: tier-0 failed and no API key; skipping models", flush=True)
            continue

        budget = spec.get("default_budget", {})
        fast_n = int(budget.get("pythagoras_4b_attempts", 4))
        heavy_n = int(budget.get("goedel_32b_attempts", 2))
        kimina_n = int(budget.get("kimina_attempts", 2))
        kimina_model = str(budget.get("kimina_model", KIMINA_PROVER))
        target = Target(
            name=tid,
            description=str(spec.get("why_it_matters", "")),
            stem=stem,
            hint=str(spec.get("hint", "")),
        )
        # Escalation ladder, cheap → strong → structurally-different: Pythagoras-4B, then Goedel-32B,
        # then the Kimina Lean-RL prover as a final different-perspective pass. All free on Featherless.
        sequence = [(PYTHAGORAS_4B, i) for i in range(1, fast_n + 1)]
        sequence += [(GOEDEL_32B, i) for i in range(1, heavy_n + 1)]
        sequence += [(kimina_model, i) for i in range(1, kimina_n + 1)]

        print(f"[loop] {tid}: tier-0 no luck; trying models "
              f"({fast_n}x4B + {heavy_n}x32B + {kimina_n}xKimina)", flush=True)
        prev_cand: str | None = None
        prev_err: str | None = None
        solved = False
        for model, attempt in sequence:
            try:
                raw = call_model(api_key, model, target, attempt, prev_cand, prev_err)
            except Exception as exc:  # noqa: BLE001
                report.append(f"- `{model}` attempt {attempt}: API error: {exc}\n")
                print(f"[loop] {tid}: {model} #{attempt} API ERROR: {str(exc)[:200]}", flush=True)
                continue
            cand = clean_candidate(raw)
            prev_cand = cand
            ok, out = run_lean(stem, cand)
            report.append(f"- `{model}` attempt {attempt}: {'OK' if ok else 'reject'}\n")
            print(f"[loop] {tid}: {model} #{attempt}: {'OK' if ok else 'reject'}", flush=True)
            if ok:
                full = build_file(stem, cand)
                (CANDIDATES_DIR / f"{tid}.lean").write_text(full, encoding="utf-8")
                report.append(f"\n**SOLVED by `{model}`** (attempt {attempt}):\n\n```lean\n{full}```\n")
                print(f"SOLVED {tid} via {model} attempt {attempt}", flush=True)
                any_solved = True
                solved = True
                break
            prev_err = out
        if not solved:
            report.append(
                "No proof within budget. This is not a verified failure of the "
                "theorem; only this search budget found nothing.\n"
            )

    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")
    print(f"Prover loop done. Any solved: {any_solved}. Report: {REPORT_FILE}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
