#!/usr/bin/env python3
"""Build the machine-readable ECDLP knowledge graph.

Emits `data/knowledge_graph.json`: a navigable, structured index that links every
machine-checked theorem to (a) the knowledge-graph claim it verifies, (b) the Lean
file and import dependencies it rests on, and (c) the formalization barriers that
bound what is provable. The intent (see the project north star) is a verified,
navigable substrate a future automated reasoner can load to understand the *known
and machine-checked* structure of the ECDLP landscape — proofs, dependencies, and
the precise foundations still missing — without re-deriving any of it.

This script READS the human-maintained sources of truth and DERIVES the graph; it
never asserts a proof. The Lean kernel remains the only judge of correctness.

Sources of truth (read-only):
  - VERIFIED.md                      — ledger of proved theorems (the nodes)
  - Ecdlp/*.lean, Ecdlp/Proved/*.lean — Lean sources (import dependency edges)
  - Ecdlp.lean                       — the built import surface (what is gated)
  - BARRIERS.md                      — the no-go / missing-foundation map
  - data/KG_CLAIM_FORMALIZATION_v1.csv — the 486-claim corpus (claim metadata)

Usage:  python3 scripts/build_knowledge_graph.py [--check]
  --check : build in memory and fail (nonzero exit) if it diverges from the
            committed data/knowledge_graph.json (for CI drift detection).
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "knowledge_graph.json"

# --- parse VERIFIED.md: the proved-theorem ledger -------------------------------

_ROW = re.compile(r"^\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|\s*$")


def _strip_md(s: str) -> str:
    """Drop markdown emphasis/backticks/footnote marks, collapse whitespace."""
    s = s.strip()
    s = s.replace("**", "")
    s = s.strip("`")
    s = s.replace("¹", "").replace("²", "")
    return s.strip()


def parse_ledger() -> list[dict]:
    rows: list[dict] = []
    seen_header = False
    for line in (ROOT / "VERIFIED.md").read_text().splitlines():
        m = _ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in m.groups()]
        # skip the header row and the |---|---| separator
        if cells[0].lower() == "claim_id":
            seen_header = True
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if not seen_header:
            continue
        claim, name, file, method, status = cells
        rows.append(
            {
                "claim": _strip_md(claim),
                "name": _strip_md(name),
                "file": _strip_md(file),
                "method": _strip_md(method),
                "status": _strip_md(status),
            }
        )
    return rows


# --- parse Lean imports: file-level dependency edges ----------------------------

_IMPORT = re.compile(r"^\s*import\s+(Ecdlp[\w.]*)")


def lean_path(module: str) -> Path | None:
    rel = module.replace(".", "/") + ".lean"
    p = ROOT / rel
    return p if p.exists() else None


def parse_imports() -> dict[str, list[str]]:
    """module -> list of Ecdlp.* modules it imports (intra-project edges only)."""
    edges: dict[str, list[str]] = {}
    lean_files = list(ROOT.glob("Ecdlp/**/*.lean")) + [ROOT / "Ecdlp.lean"]
    for f in lean_files:
        if not f.exists():
            continue
        module = (
            f.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")
        )
        deps = []
        for line in f.read_text().splitlines():
            m = _IMPORT.match(line)
            if m and m.group(1) != module:
                deps.append(m.group(1))
        edges[module] = deps
    return edges


def file_to_module(file_field: str) -> str:
    return file_field.replace("/", ".").removesuffix(".lean")


# --- the barrier map (curated mirror of BARRIERS.md, machine-readable) ----------
# These are the foundations Mathlib lacks to formalize ECDLP cryptanalysis. Each
# is a first-class node: a precise statement of *what is missing and why*, which is
# itself the research contribution. Counts are indicative (see BARRIERS.md).

BARRIERS = [
    {
        "id": "B1-cost-model",
        "title": "No oracle / group-operation cost model in Lean",
        "missing_foundation": "a general cost / oracle-query model in Mathlib",
        "blocks": "exact Theta running times, index-calculus subexponential bounds, "
        "distinguished-point parallel speedups",
        "affected_claims_estimate": 54,
        "mathlib_area": "(not in Mathlib) complexity/cost model",
        "partial_progress": "generic-group Omega(sqrt p) lower bound and O(sqrt n) "
        "upper bounds are formalized: their information-theoretic core sidesteps a "
        "general cost model (collision count over affine forms a + b*X).",
    },
    {
        "id": "B2-lattice",
        "title": "No lattice-reduction theory in Mathlib",
        "missing_foundation": "LLL/BKZ basis reduction, CVP/SVP",
        "blocks": "hidden-number-problem / biased-nonce ECDSA attacks",
        "affected_claims_estimate": 24,
        "mathlib_area": "(not in Mathlib) lattice reduction",
        "partial_progress": None,
    },
    {
        "id": "B2-quantum",
        "title": "No quantum-circuit cost model in Mathlib",
        "missing_foundation": "quantum circuit resource model",
        "blocks": "Shor-style ECDLP resource estimates",
        "affected_claims_estimate": 38,
        "mathlib_area": "(not in Mathlib) quantum circuits",
        "partial_progress": None,
    },
    {
        "id": "B3-semaev",
        "title": "Summation / Semaev polynomials not in Mathlib",
        "missing_foundation": "elliptic summation polynomials S_n over MvPolynomial",
        "blocks": "index calculus on elliptic curves over extension fields",
        "affected_claims_estimate": 12,
        "mathlib_area": "MvPolynomial (partial)",
        "partial_progress": "Mathlib has multivariate polynomials but not the S_n.",
    },
    {
        "id": "B3-weil-pairing",
        "title": "Weil/Tate pairing and isogeny depth missing",
        "missing_foundation": "Weil pairing on EllipticCurve, isogeny machinery",
        "blocks": "MOV/FR transfer reductions to finite-field DLP",
        "affected_claims_estimate": 15,
        "mathlib_area": "EllipticCurve.Isogeny (partial)",
        "partial_progress": "Mathlib has the curve and isogeny base, not the pairing.",
    },
    {
        "id": "B3-point-counting",
        "title": "Concrete point count #E(F_p) = n not kernel-computable",
        "missing_foundation": "Schoof / efficient point counting in Mathlib",
        "blocks": "deriving #E = n abstractly for the concrete curve",
        "affected_claims_estimate": 6,
        "mathlib_area": "EllipticCurve (partial)",
        "partial_progress": "the concrete order is instead pinned via native_decide / "
        "the published value; primality of n is machine-checked (Pratt).",
    },
]

# Map a ledger row to the barrier(s) it is adjacent to (verified node that lives at
# the frontier of a barrier — either a partial step into it, or its boundary).
FRONTIER = {
    "B1-cost-model": [
        "generic_dlog_query_bound",
        "generic_dlog_sqrt_bound",
        "generic_success_le",
        "bsgs_decomp",
        "pollard_rho_collision",
        "secp256k1_generic_security",
    ],
    "B3-weil-pairing": [
        "secp256k1_j_eq_zero",
        "secp256k1_embedding_degree_gt_100",
        "secp256k1_trace_ordinary_nonanomalous",
        "secp256k1_Ψ₂Sq",
    ],
    "B3-point-counting": ["secp256k1_n_prime", "secp256k1_p_prime"],
}


# --- corpus summary -------------------------------------------------------------

def parse_corpus() -> dict:
    path = ROOT / "data" / "KG_CLAIM_FORMALIZATION_v1.csv"
    with path.open() as f:
        rows = list(csv.DictReader(f))
    status = Counter(r.get("formal_status", "") for r in rows)
    return {
        "total_claims": len(rows),
        "by_formal_status": dict(status.most_common()),
        "columns": list(rows[0].keys()) if rows else [],
        "note": "486 atomic claims. formalizable + formalizable_hard are the "
        "candidate frontier; informal_only / scope_meta are out of scope by nature.",
    }


# --- assemble -------------------------------------------------------------------

def short_name(full: str) -> str:
    """Last dotted component, for frontier matching (e.g. ...secp256k1_n_prime)."""
    return full.split()[0].split(".")[-1] if full else full


# Coarse research areas, matched by keyword against (claim + module). First hit
# wins; order matters (most specific first). Gives a future reasoner a stable
# faceting of the corpus without re-reading every statement.
AREA_RULES = [
    ("primality", ["prime", "pratt", "primality"]),
    ("attack-resistance", ["embedding degree", "anomalous", "trace of frobenius",
                           "supersingular", "mov", "smart"]),
    ("generic-hardness", ["generic", "shoup", "nechaev", "bsgs", "baby-step",
                          "pollard", "query bound", "sqrt", "√"]),
    ("reduction", ["pohlig", "crt", "reconstruct", "projection", "component"]),
    ("protocol-soundness", ["schnorr", "pedersen", "okamoto", "chaum", "dleq",
                            "elgamal", "diffie", "musig", "feldman", "adaptor",
                            "blind", "threshold", "vss", "eddsa"]),
    ("curve-torsion", ["division polynomial", "ψ", "torsion", "j-invariant",
                       "j =", "discriminant", "δ", "c₄", "weierstrass", "b₂",
                       "b₄", "b₆", "b₈", "elliptic", "nonsingular", "generator",
                       "eigenvalue", "cube root", "order exactly 3", "β", "λ",
                       "glv", "cofactor", "lagrange", "secp256k1verified",
                       "lambda", "beta", "lam ", "base point", "on the curve"]),
    ("params", ["p ≡", "special form", "mod four", "3 ∣", "divides"]),
]


def classify_area(claim: str, module: str) -> str:
    hay = (claim + " " + module).lower()
    for area, kws in AREA_RULES:
        if any(k in hay for k in kws):
            return area
    return "other"


def module_depth(module: str, imports: dict[str, list[str]],
                 _cache: dict[str, int] | None = None) -> int:
    """Longest intra-project import chain under `module` (0 = no project deps)."""
    if _cache is None:
        _cache = {}
    if module in _cache:
        return _cache[module]
    _cache[module] = 0  # guard against cycles
    deps = imports.get(module, [])
    depth = 0 if not deps else 1 + max(
        (module_depth(d, imports, _cache) for d in deps), default=0
    )
    _cache[module] = depth
    return depth


def build() -> dict:
    ledger = parse_ledger()
    imports = parse_imports()
    built_modules = set(imports.get("Ecdlp", []))  # what Ecdlp.lean gates
    depth_cache: dict[str, int] = {}

    theorems = []
    for i, r in enumerate(ledger):
        module = file_to_module(r["file"])
        sn = short_name(r["name"])
        theorems.append(
            {
                "id": f"thm-{i:03d}",
                "name": r["name"],
                "short_name": sn,
                "module": module,
                "file": r["file"],
                "claim": r["claim"],
                "method": r["method"],
                "status": r["status"],
                "area": classify_area(r["claim"], module),
                "dependency_depth": module_depth(module, imports, depth_cache),
                "gated": module in built_modules or module
                in {"Ecdlp.Secp256k1Verified", "Ecdlp.Lagrange", "Ecdlp.Statements"},
            }
        )

    name_to_id = {t["short_name"]: t["id"] for t in theorems}

    edges = []
    # file-level import dependency edges between project modules
    for module, deps in imports.items():
        for d in deps:
            edges.append({"from": module, "to": d, "type": "imports"})
    # theorem -> barrier frontier edges
    for bid, names in FRONTIER.items():
        for nm in names:
            if nm in name_to_id:
                edges.append(
                    {"from": name_to_id[nm], "to": bid, "type": "frontier_of"}
                )

    method_hist = Counter(t["method"] for t in theorems)

    return {
        "schema_version": "1.0",
        "name": "ECDLP verified knowledge graph",
        "purpose": "A machine-readable, navigable index of the machine-checked "
        "(Lean 4 + Mathlib, no sorry, no axioms) structure of the ECDLP landscape "
        "for secp256k1: proved theorems, their import dependencies, the corpus "
        "claims they verify, and the formalization barriers that bound them. "
        "Built for a future automated reasoner to load the known-and-verified "
        "frontier without re-deriving it.",
        "invariant": "Every theorem listed is accepted by the Lean kernel with no "
        "sorry and no added axioms. Truth is decided only by the kernel; this graph "
        "is derived from the ledger, it does not assert proofs.",
        "counts": {
            "theorems": len(theorems),
            "barriers": len(BARRIERS),
            "edges": len(edges),
            "by_method": dict(method_hist.most_common()),
            "by_area": dict(Counter(t["area"] for t in theorems).most_common()),
        },
        "theorems": theorems,
        "barriers": BARRIERS,
        "corpus": parse_corpus(),
        "edges": edges,
    }


OUT_MD = ROOT / "data" / "knowledge_graph.md"


def render_markdown(graph: dict) -> str:
    """A human/AI-readable rendering of the graph: the verified frontier grouped by
    research area, then the barriers. Generated — edit the script, not this file."""
    c = graph["counts"]
    lines: list[str] = []
    lines.append("# ECDLP verified knowledge graph (rendered view)")
    lines.append("")
    lines.append(
        "> Auto-generated from `VERIFIED.md` + the Lean import surface by "
        "`scripts/build_knowledge_graph.py`. Machine source of truth: "
        "`data/knowledge_graph.json`. Every theorem below is kernel-checked "
        "(no `sorry`, no axioms)."
    )
    lines.append("")
    lines.append(
        f"**{c['theorems']} theorems** · **{c['barriers']} barriers** · "
        f"**{c['edges']} edges**"
    )
    lines.append("")
    lines.append("By proof method: "
                 + ", ".join(f"{k} ({v})" for k, v in c["by_method"].items()))
    lines.append("")
    lines.append("By research area: "
                 + ", ".join(f"{k} ({v})" for k, v in c["by_area"].items()))
    lines.append("")

    # group theorems by area
    by_area: dict[str, list[dict]] = {}
    for t in graph["theorems"]:
        by_area.setdefault(t["area"], []).append(t)
    lines.append("## Verified theorems by area")
    lines.append("")
    for area in sorted(by_area, key=lambda a: -len(by_area[a])):
        lines.append(f"### {area} ({len(by_area[area])})")
        lines.append("")
        lines.append("| theorem | claim | method | file |")
        lines.append("|---|---|---|---|")
        for t in by_area[area]:
            lines.append(
                f"| `{t['short_name']}` | {t['claim']} | {t['method']} | "
                f"`{t['file'].split('/')[-1]}` |"
            )
        lines.append("")

    # frontier: theorems sitting at a barrier boundary
    frontier = [e for e in graph["edges"] if e["type"] == "frontier_of"]
    id_to_thm = {t["id"]: t for t in graph["theorems"]}
    lines.append("## Barriers and their verified frontier")
    lines.append("")
    lines.append(
        "Each barrier is a foundation Mathlib lacks. The *frontier* lists verified "
        "theorems sitting at that boundary — the realised edge of the missing work."
    )
    lines.append("")
    for b in graph["barriers"]:
        lines.append(f"### {b['id']} — {b['title']}")
        lines.append("")
        lines.append(f"- **Missing:** {b['missing_foundation']}")
        lines.append(f"- **Blocks:** {b['blocks']}")
        if b.get("partial_progress"):
            lines.append(f"- **Partial progress:** {b['partial_progress']}")
        fnodes = [id_to_thm[e["from"]] for e in frontier
                  if e["to"] == b["id"] and e["from"] in id_to_thm]
        if fnodes:
            lines.append("- **Verified frontier:** "
                         + ", ".join(f"`{t['short_name']}`" for t in fnodes))
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    graph = build()
    text = json.dumps(graph, indent=2, ensure_ascii=False) + "\n"
    md = render_markdown(graph)
    if "--check" in sys.argv:
        stale = []
        if not OUT.exists() or OUT.read_text() != text:
            stale.append(str(OUT))
        if not OUT_MD.exists() or OUT_MD.read_text() != md:
            stale.append(str(OUT_MD))
        if stale:
            print(
                "stale; run: python3 scripts/build_knowledge_graph.py -> "
                + ", ".join(stale),
                file=sys.stderr,
            )
            return 1
        print(f"up to date ({graph['counts']['theorems']} theorems).")
        return 0
    OUT.write_text(text)
    OUT_MD.write_text(md)
    print(
        f"wrote {OUT} and {OUT_MD}: {graph['counts']['theorems']} theorems, "
        f"{graph['counts']['barriers']} barriers, {graph['counts']['edges']} edges."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
