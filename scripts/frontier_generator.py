#!/usr/bin/env python3
"""Layer-3 *frontier-expander* target generator.

The corpus-reader generator (`scripts/generator.py`) is starved: the 486-claim
corpus is mostly research-level (Weil pairing, Semaev, p-adic) blocked on missing
Mathlib foundations. This generator instead grows targets from the **verified
frontier** itself — mathematics generates its own questions. Each emitted stem is a
well-typed open conjecture (`sorry`, in `Ecdlp/Targets/`, NOT imported → gate stays
green); the Lean kernel (CI) and the server Tier-0 daemon decide truth.

Families (graded, well-typed, tractable):
  - torsion-lattice : boundary + closure facts of `AddSubgroup.torsionBy` (extends
                      the proved `Ecdlp/Proved/Torsion.lean` frontier)
  - group-arith     : order / Lagrange / cofactor arithmetic (omega/decide-closable)

Each family is a list of (id, doc, lean_decl). Run with --emit to write stems +
`targets/<id>.json` registry rows.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

TARGETS = Path("Ecdlp/Targets")
REGISTRY = Path("targets")

# (id, difficulty, tactics-hint, docstring, lean theorem decl ending in ':= by')
STEMS: list[tuple[str, str, list[str], str, str]] = [
    ("frontier_torsionBy_zero_top", "easy", ["simp", "aesop"],
     "Every element is 0-torsion: the 0-torsion subgroup is the whole group.",
     "theorem frontier_torsionBy_zero_top {A : Type*} [AddCommGroup A] :\n"
     "    AddSubgroup.torsionBy A (0 : ℤ) = ⊤ := by"),
    ("frontier_torsionBy_one_bot", "easy", ["simp", "aesop"],
     "Only the identity is 1-torsion: the 1-torsion subgroup is trivial.",
     "theorem frontier_torsionBy_one_bot {A : Type*} [AddCommGroup A] :\n"
     "    AddSubgroup.torsionBy A (1 : ℤ) = ⊥ := by"),
    ("frontier_mem_torsionBy_zero", "easy", ["simp", "intro x; simp"],
     "Membership in the 0-torsion is universal.",
     "theorem frontier_mem_torsionBy_zero {A : Type*} [AddCommGroup A] (x : A) :\n"
     "    x ∈ AddSubgroup.torsionBy A (0 : ℤ) := by"),
    ("frontier_zero_mem_torsionBy", "easy", ["simp", "exact zero_mem _"],
     "The identity is n-torsion for every n.",
     "theorem frontier_zero_mem_torsionBy {A : Type*} [AddCommGroup A] (n : ℤ) :\n"
     "    (0 : A) ∈ AddSubgroup.torsionBy A n := by"),
    ("frontier_orderOf_dvd_card", "medium", ["exact orderOf_dvd_card", "exact?"],
     "Lagrange: every element's order divides the group order (finite group).",
     "theorem frontier_orderOf_dvd_card {G : Type*} [Group G] [Fintype G] (g : G) :\n"
     "    orderOf g ∣ Fintype.card G := by"),
    ("frontier_pow_card_eq_one", "medium", ["exact pow_card_eq_one", "exact?"],
     "Euler/Lagrange: g ^ |G| = 1 in a finite group.",
     "theorem frontier_pow_card_eq_one {G : Type*} [Group G] [Fintype G] (g : G) :\n"
     "    g ^ Fintype.card G = 1 := by"),
]


def emit(stem):
    sid, diff, tacs, doc, decl = stem
    module = "Ecdlp.Targets." + "".join(p.capitalize() for p in sid.split("_"))
    lean = (
        "import Mathlib\n\n"
        f"namespace {module}\n\n"
        f"/-- [frontier:{sid}] {doc} -/\n"
        f"{decl}\n  sorry\n\n"
        f"end {module}\n"
    )
    (TARGETS / f"{sid}.lean").write_text(lean, encoding="utf-8")
    spec = {
        "id": sid, "name": sid, "claim_id": f"frontier-{sid}",
        "status": "todo", "difficulty": diff, "template": "frontier_expander",
        "provability_score": "high" if diff == "easy" else "medium",
        "why_it_matters": doc,
        "default_budget": {"tier0_tactics": tacs, "escalate_if_failed": True},
        "stem_file": f"Ecdlp/Targets/{sid}.lean",
        "source": {"family": "frontier-expander", "from": "verified frontier"},
    }
    (REGISTRY / f"{sid}.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    return sid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args()
    if args.emit:
        TARGETS.mkdir(parents=True, exist_ok=True)
        REGISTRY.mkdir(parents=True, exist_ok=True)
        ids = [emit(s) for s in STEMS]
        print(f"Emitted {len(ids)} frontier stems: {', '.join(ids)}")
    else:
        print(f"{len(STEMS)} frontier stems available (use --emit to write).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
