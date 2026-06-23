#!/usr/bin/env python3
"""Layer 3 target generator.

Reads the read-only claim corpus (`data/KG_CLAIM_FORMALIZATION_v1.csv`) and
*proposes* Lean theorem stems for the Layer 2 prover loop. It NEVER asserts a
proof: every emitted file ends in `sorry`, lives in `Ecdlp/Targets/` (not built,
excluded from the no-`sorry` gate), and is only a conjecture until the Lean
kernel accepts a proof.

Pipeline:
  filter   - drop informal/meta claims and ones with no formal statement
  triage   - classify each remaining claim (cost-model barrier / manual / templated)
  template - for claims matching a known formalizable pattern, emit a stem
             (`Ecdlp/Targets/<id>.lean`) + a registry row (`targets/<id>.json`)
  report   - `generator-report.md`: a formalization-status / barriers registry

The generator is conservative on purpose: it emits a stem only when a template
confidently applies, so the prover is fed real candidates, not noise. Everything
else is recorded as a barrier or a manual-formalization candidate.
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
from pathlib import Path

CSV_PATH = Path("data/KG_CLAIM_FORMALIZATION_v1.csv")
TARGETS_LEAN_DIR = Path("Ecdlp/Targets")
REGISTRY_DIR = Path("targets")
REPORT = Path("generator-report.md")
VERIFIED = Path("VERIFIED.md")

DROP_STATUS = {"informal_only", "scope_meta"}
COST_HINTS = (
    "running time", "expected", "complexity", "o(", "theta(", "sqrt(",
    "cost model", "operations", "subexponential", "exp(", "wall-clock",
)


def area(r: dict) -> str:
    return r.get("mathlib_area") or ""


def stmt(r: dict) -> str:
    return r.get("formal_statement") or ""


def label(r: dict) -> str:
    return " ".join((r.get("label") or r.get("formal_statement") or "").split())


def short(s: str, n: int = 150) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def slug_module(cid: str) -> str:
    return "".join(p.capitalize() for p in re.split(r"[^A-Za-z0-9]+", cid) if p)


def slug_file(cid: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", cid).strip("_").lower()


def slug_thm(cid: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", cid.lower()).strip("_")


# --- Templates ---------------------------------------------------------------
# Each template: a key, a predicate over a claim row, and a function producing
# the Lean proposition line(s) ending in ":= by". Stems are CONJECTURES; their
# Mathlib lemma names need not be correct (the prover/kernel decides truth).

def _t_order_divides(r: dict) -> bool:
    s = stmt(r).lower()
    return "orderofelement" in area(r).lower() and (
        "divides" in s or "pohlig" in s or "lagrange" in s
    )


def _p_order_divides(thm: str) -> str:
    return (
        f"theorem {thm} {{G : Type*}} [Group G] [Fintype G] (g : G) :\n"
        f"    orderOf g ∣ Fintype.card G := by\n"
    )


def _t_prime_order_gen(r: dict) -> bool:
    s = stmt(r).lower()
    return "prime order" in s and "generat" in s


def _p_prime_order_gen(thm: str) -> str:
    return (
        f"theorem {thm} {{G : Type*}} [Group G] [Fintype G]\n"
        f"    (hp : (Fintype.card G).Prime) (g : G) (hg : g ≠ 1) :\n"
        f"    orderOf g = Fintype.card G := by\n"
    )


def _t_cofactor(r: dict) -> bool:
    s = stmt(r).lower()
    return "cofactor" in s or "#e(f_p) = n" in s or re.search(r"=\s*n\s*\*\s*h", s) is not None


def _p_cofactor(thm: str) -> str:
    return (
        f"theorem {thm} {{G : Type*}} [Group G] (H : Subgroup G)\n"
        f"    [Fintype G] [DecidablePred (· ∈ H)] :\n"
        f"    Fintype.card H * H.index = Fintype.card G := by\n"
    )


TEMPLATES = [
    ("order_divides_card", _t_order_divides, _p_order_divides, "high"),
    ("prime_order_generator", _t_prime_order_gen, _p_prime_order_gen, "medium"),
    ("cofactor_card_index", _t_cofactor, _p_cofactor, "medium"),
]


def existing_claim_ids() -> set[str]:
    seen: set[str] = set()
    if VERIFIED.exists():
        text = VERIFIED.read_text(encoding="utf-8")
        seen |= set(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)+-\d+", text))
    for p in REGISTRY_DIR.glob("*.json"):
        try:
            spec = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if spec.get("claim_id"):
            seen.add(spec["claim_id"])
    return seen


def emit(r: dict, key: str, prop_fn, score: str) -> dict:
    cid = r["claim_id"]
    module = "Ecdlp.Targets." + slug_module(cid)
    thm = slug_thm(cid)
    fstem = slug_file(cid)
    lean = (
        "import Mathlib\n\n"
        f"namespace {module}\n\n"
        f"/-- [{cid}] {short(label(r))} -/\n"
        f"{prop_fn(thm)}"
        "  sorry\n\n"
        f"end {module}\n"
    )
    (TARGETS_LEAN_DIR / f"{fstem}.lean").write_text(lean, encoding="utf-8")
    spec = {
        "id": fstem,
        "name": thm,
        "claim_id": cid,
        "status": "todo",
        "difficulty": "unknown",
        "template": key,
        "provability_score": score,
        "why_it_matters": short(label(r)),
        "default_budget": {
            "pythagoras_4b_attempts": 8,
            "goedel_32b_attempts": 4,
            "escalate_if_failed": True,
        },
        "stem_file": f"Ecdlp/Targets/{fstem}.lean",
        "source": {
            "formal_status": r.get("formal_status"),
            "mathlib_area": r.get("mathlib_area"),
            "batch": r.get("batch"),
            "source_id": r.get("source_id"),
        },
    }
    (REGISTRY_DIR / f"{fstem}.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    return spec


def classify(r: dict, already: set[str]) -> tuple[str, str]:
    """Return (category, reason)."""
    if r["claim_id"] in already:
        return "skip_known", "already verified or registered"
    if r.get("formal_status") in DROP_STATUS:
        return "drop", f"formal_status={r.get('formal_status')}"
    if not stmt(r).strip():
        return "drop", "no formal_statement"
    a = area(r).lower()
    s = stmt(r).lower()
    if a.startswith("(complexity") or any(h in s for h in COST_HINTS):
        return "barrier_cost_model", "complexity/cost statement; no Lean cost model"
    if a.startswith("(not in mathlib"):
        return "barrier_not_in_mathlib", area(r)
    for key, pred, _prop, _score in TEMPLATES:
        if pred(r):
            return "templated:" + key, "template matched"
    return "manual", "formalizable but no confident template"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true", help="write stems + registry (default: report only)")
    args = ap.parse_args()

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    already = existing_claim_ids()
    if args.emit:
        TARGETS_LEAN_DIR.mkdir(parents=True, exist_ok=True)
        REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

    cats: dict[str, list[dict]] = collections.defaultdict(list)
    emitted: list[dict] = []
    tpl_lookup = {k: (p, fn, sc) for k, p, fn, sc in TEMPLATES}

    for r in rows:
        cat, reason = classify(r, already)
        cats[cat.split(":")[0]].append(r)
        if cat.startswith("templated:") and args.emit:
            key = cat.split(":", 1)[1]
            _pred, fn, score = tpl_lookup[key]
            emitted.append(emit(r, key, fn, score))

    lines = ["# Generator report (formalization triage)\n"]
    lines.append(f"Corpus: {len(rows)} claims. Emit mode: {args.emit}.\n")
    order = ["templated", "manual", "barrier_cost_model", "barrier_not_in_mathlib", "drop", "skip_known"]
    lines.append("## Category counts\n")
    for c in order:
        lines.append(f"- **{c}**: {len(cats.get(c, []))}")
    lines.append("")
    if emitted:
        lines.append("## Emitted stems (open conjectures)\n")
        for spec in emitted:
            lines.append(f"- `{spec['id']}` <- `{spec['claim_id']}` (template `{spec['template']}`, score {spec['provability_score']})")
        lines.append("")
    lines.append("## Manual-formalization candidates (formalizable, no template)\n")
    for r in cats.get("manual", [])[:40]:
        lines.append(f"- `{r['claim_id']}` [{area(r)}]: {short(label(r), 120)}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Triage: " + ", ".join(f"{c}={len(cats.get(c, []))}" for c in order))
    print(f"Emitted {len(emitted)} stem(s). Report: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
