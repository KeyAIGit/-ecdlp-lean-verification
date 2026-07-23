#!/usr/bin/env python3
"""Autonomous discovery: LLM-propose genuinely-closeable next targets -> queue.json.

The deterministic corpus generator (`generator.py`) is exhausted — it emits 0 templated
stems now, and the remaining corpus claims are barrier-blocked (Weil pairing, lattice
reduction, Semaev) or need genuine mathematics. So the autonomous engine discovers new
targets the way the interactive landability audit did: it shows the model the current
verified base + the barrier map, and asks for a ranked list of NEW, closeable-now,
non-barrier-blocked theorems, each as a full prompt (name + NL + Lean signature + imports
+ proof hint) in the exact schema `agent_day.py` consumes.

Output: merges proposals into `targets/queue.json`. Safe by construction — proposals are
only *attempted* downstream; the Lean kernel + CI decide acceptance and a delegated maintainer
decides whether to merge the draft PR. Budget: one model call, hard-capped
(`DISCOVER_BUDGET_USD`, default $1.50).

Usage:
    python3 scripts/autonomous_discover.py            # calls the model, writes queue.json
    python3 scripts/autonomous_discover.py --dry-run  # no API call; prints the prompt + a
                                                       # deterministic fallback queue (for CI
                                                       # smoke / local testing without a key)
    DISCOVER_COUNT=6 python3 scripts/autonomous_discover.py   # ask for N targets
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / os.environ.get("AGENT_QUEUE", "targets/queue.json")
VERIFIED = ROOT / "VERIFIED.md"
BARRIERS = ROOT / "BARRIERS.md"
PROVED_DIR = ROOT / "Ecdlp" / "Proved"

DISCOVER_MODEL = os.environ.get("DISCOVER_MODEL", "claude-sonnet-5")
DISCOVER_BUDGET_USD = float(os.environ.get("DISCOVER_BUDGET_USD", "1.50"))
DISCOVER_COUNT = int(os.environ.get("DISCOVER_COUNT", "6"))


def proved_theorem_names() -> set[str]:
    """Every theorem/def name already in Ecdlp/Proved (so we don't re-propose them)."""
    names: set[str] = set()
    if not PROVED_DIR.is_dir():
        return names
    pat = re.compile(r"^\s*(?:private\s+|noncomputable\s+|protected\s+)*"
                     r"(?:theorem|lemma|def|instance)\s+([A-Za-z_][\w'.]*)")
    for f in PROVED_DIR.glob("*.lean"):
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = pat.match(line)
            if m:
                names.add(m.group(1))
    return names


def read_trimmed(path: Path, limit: int) -> str:
    if not path.exists():
        return "(absent)"
    t = path.read_text(encoding="utf-8", errors="ignore")
    return t if len(t) <= limit else t[:limit] + "\n… (truncated) …"


def build_prompt(done_names: set[str]) -> str:
    canon = "unknown"
    if VERIFIED.exists():
        m = re.search(r"\*\*(\d+ ledger rows / ~\d+ distinct[^*]*)\*\*",
                      VERIFIED.read_text(encoding="utf-8", errors="ignore"))
        if m:
            canon = m.group(1)
    names_list = ", ".join(sorted(done_names)) if done_names else "(none found)"
    barriers = read_trimmed(BARRIERS, 6000)
    return f"""You are the discovery stage of an autonomous Lean 4 / Mathlib v4.31 theorem-proving \
engine for secp256k1 / ECDLP. Propose the next {DISCOVER_COUNT} theorems to prove.

CURRENT VERIFIED BASE: {canon}. Already-proved names (DO NOT re-propose these or trivial \
restatements of them):
{names_list}

BARRIER MAP (DO NOT propose anything that needs these missing foundations — Weil pairing, \
E[n]≅(Z/n)^2 structure theorem, exact point counting #E=n / Schoof, lattice reduction \
LLL/BKZ, Semaev summation polynomials, a cost/probability model):
{barriers}

RULES — each proposed target MUST be:
  1. genuinely NEW (not already proved above, not a trivial named instance of an existing \
uniform bound),
  2. closeable NOW on pinned Mathlib v4.31 with existing Mathlib + repo lemmas (no missing \
foundation from the barrier map),
  3. either a secp256k1-concrete fact, a group/field-algebra identity, an abstract \
DL-crypto protocol identity (Schnorr/ECDSA/threshold/SSS style, no adversary/probability \
model), or a self-gap (something the repo asserts in prose but has not fully proved).

For EACH target output an object with:
  - "name": a CamelCase module name,
  - "model": "claude-sonnet-5" for easy/medium, "claude-opus-4-8" only if genuinely hard,
  - "max_iters": 4-6,
  - "target": a COMPLETE self-contained prompt for a prover model — natural-language goal, \
the EXACT Lean theorem signature, the `import`s it needs (import Mathlib plus any \
`Ecdlp.Proved.*` modules whose lemmas it reuses — cite them by name), and a concrete \
proof sketch. End it with: "Output ONLY the complete Lean file in a ```lean block."
  - OPTIONAL "certify": if the proof rests on a nontrivial ALGEBRAIC identity (a polynomial \
identity, an exact `linear_combination` cofactor, a resultant, an x-coordinate/division-\
polynomial relation), include a precise natural-language statement of that identity to be \
verified by sympy FIRST (exact symbolic computation). Omit for pure group-theory / one-\
Mathlib-lemma targets. When present, add "certify_model": "claude-opus-4-8".

Output STRICT JSON and nothing else:
{{"targets": [ {{"name": "...", "model": "...", "max_iters": 5, "target": "...", "certify": "... (optional)"}} ]}}
Be conservative: a short list of real, closeable targets beats a long list of guesses."""


def extract_json(text: str) -> dict | None:
    # Prefer a fenced ```json block; else the first balanced {...}.
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.S) or \
        re.search(r"```\s*(\{.*?\})\s*```", text, re.S)
    blob = m.group(1) if m else None
    if blob is None:
        start = text.find("{")
        if start < 0:
            return None
        depth = 0
        for i in range(start, len(text)):
            depth += (text[i] == "{") - (text[i] == "}")
            if depth == 0:
                blob = text[start:i + 1]
                break
    if not blob:
        return None
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        return None


def sanitize(targets: list[dict], done_names: set[str]) -> list[dict]:
    out, seen = [], set()
    for t in targets:
        if not isinstance(t, dict):
            continue
        name = str(t.get("name", "")).strip()
        target = str(t.get("target", "")).strip()
        if not name or not target or name in seen:
            continue
        # Drop if the proposed name is already proved, or clearly forbidden.
        if name in done_names:
            continue
        if re.search(r"\b(sorry|admit|axiom)\b", target):
            continue
        seen.add(name)
        entry = {
            "name": re.sub(r"[^A-Za-z0-9_]", "", name)[:48] or "Discovered",
            "model": t.get("model", DISCOVER_MODEL),
            "max_iters": int(t.get("max_iters", 5)),
            "target": target,
        }
        cert = str(t.get("certify", "")).strip()
        if cert and not re.search(r"\b(sorry|admit|axiom)\b", cert):
            entry["certify"] = cert
            entry["certify_model"] = t.get("certify_model", "claude-opus-4-8")
            entry["certify_iters"] = int(t.get("certify_iters", 4))
        out.append(entry)
    return out


def write_queue(targets: list[dict]) -> None:
    payload = {
        "_comment": "Auto-populated by scripts/autonomous_discover.py (LLM discovery). "
                    "Consumed by scripts/agent_day.py. Regenerated each engine run.",
        "targets": targets,
    }
    QUEUE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")


def fallback_targets() -> list[dict]:
    """Deterministic, no-API queue for --dry-run / no-key CI smoke. These are genuinely
    closeable (odd-torsion degree rungs) so the loop has something real to chew even if the
    discovery call is unavailable — they exercise the full pipeline end to end."""
    return [{
        "name": "ElevenTorsionDegree",
        "model": "claude-sonnet-5",
        "max_iters": 4,
        "target": ("In `namespace Ecdlp.Curve` with `open Polynomial`, prove "
                   "`theorem secp256k1_preΨ₁₁_natDegree : "
                   "(secp256k1.preΨ' 11).natDegree = 60`. Imports: `import Mathlib`, "
                   "`import Ecdlp.Proved.DivisionPolynomial`, "
                   "`import Ecdlp.Proved.DivisionPolynomialDegree`. Proof: "
                   "`have h : ((11:ℕ):ZMod Secp256k1.p) ≠ 0 := by rw [Ne, "
                   "ZMod.natCast_eq_zero_iff]; native_decide` then "
                   "`rw [secp256k1.natDegree_preΨ' h]; decide`. "
                   "Output ONLY the complete Lean file in a ```lean block."),
    }]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="no API call; write the deterministic fallback queue")
    args = ap.parse_args(argv)

    done = proved_theorem_names()

    if args.dry_run or not os.environ.get("ANTHROPIC_API_KEY"):
        reason = "dry-run" if args.dry_run else "no ANTHROPIC_API_KEY"
        print(f"discover: {reason} -> writing deterministic fallback queue")
        targets = fallback_targets()
        write_queue(targets)
        print(f"discover: wrote {len(targets)} fallback target(s) to "
              f"{os.path.relpath(QUEUE_PATH, ROOT)}")
        return 0

    # Lazy imports so --dry-run needs neither the SDK nor the repo agent modules.
    sys.path.insert(0, str(ROOT / "scripts"))
    import anthropic  # noqa: E402
    from agent_day import call_model, usd_for  # noqa: E402
    from agent_prove import build_system  # noqa: E402

    client = anthropic.Anthropic()
    system = build_system()
    prompt = build_prompt(done)
    resp = call_model(client, DISCOVER_MODEL, system,
                      [{"role": "user", "content": prompt}])
    spend = usd_for(DISCOVER_MODEL, resp.usage)
    reply = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    print(f"discover: model call ~${spend:.3f} (cap ${DISCOVER_BUDGET_USD:.2f})")

    data = extract_json(reply)
    raw = (data or {}).get("targets", []) if isinstance(data, dict) else []
    targets = sanitize(raw, done)
    if not targets:
        print("discover: model returned no usable targets; using fallback")
        targets = fallback_targets()
    write_queue(targets)
    print(f"discover: wrote {len(targets)} target(s) to {os.path.relpath(QUEUE_PATH, ROOT)}")
    for t in targets:
        print(f"  - {t['name']} (model {t['model']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
