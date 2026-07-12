#!/usr/bin/env python3
"""Typed result registry — derive the ledger from the Lean source, not a hand number.

Parses every built Lean file under `Ecdlp/` (excluding open `Targets/` stems) for its
declarations (`theorem`/`lemma`/`def`/`instance`/`abbrev`) with fully-qualified names, and
cross-references the theorem names **cited in `VERIFIED.md`**. Emits `data/result_registry.json`
and, in `--check` mode, fails if `VERIFIED.md` cites a fully-qualified `Ecdlp.*` theorem name that
does **not** exist in the source — a mechanical guard against ledger drift (a row referencing a
renamed/removed theorem).

This is the first brick of provenance: the ledger's *content* becomes auditable against the actual
kernel-checked source. (It does not recompute the headline count — that stays the curated
`VERIFIED.md` canonical figure — but it makes every cited name verifiable.)

Usage:
  python3 scripts/gen_result_registry.py            # write data/result_registry.json
  python3 scripts/gen_result_registry.py --check    # fail on cited-but-missing theorem names
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEAN_ROOT = ROOT / "Ecdlp"
VERIFIED = ROOT / "VERIFIED.md"
OUT = ROOT / "data" / "result_registry.json"

DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?"
    r"(?:private\s+|protected\s+|noncomputable\s+|scoped\s+|local\s+)*"
    r"(theorem|lemma|def|instance|abbrev)\s+([A-Za-z_][A-Za-z0-9_'!?]*)",
)
NS_RE = re.compile(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_'.]*)")
END_RE = re.compile(r"^\s*end\s+([A-Za-z_][A-Za-z0-9_'.]*)")
# Fully-qualified Ecdlp.* references cited in VERIFIED.md (the canonical theorem-name column).
CITE_RE = re.compile(r"\bEcdlp\.(?:[A-Za-z0-9_']+\.)*[A-Za-z0-9_']+")


def lean_files() -> list[Path]:
    out = []
    for p in sorted(LEAN_ROOT.rglob("*.lean")):
        if "Targets" in p.parts:
            continue
        out.append(p)
    return out


ANON_INST_RE = re.compile(
    r"^\s*(?:noncomputable\s+|scoped\s+|local\s+)*instance\s*:\s*(.+)")


def parse_declarations() -> tuple[dict[str, list[dict]], set[str], set[str], set[str]]:
    """Return (by_qualified_name, simple_names, namespaces, anon_instance_targets).

    `namespaces` collects every namespace path seen (so a bare namespace cited in prose is not
    mistaken for a missing theorem). `anon_instance_targets` collects the `.`-joined last two
    components of `instance : <Type>` declarations (which have no name of their own), so a cited
    anonymous instance like `secp256k1.IsElliptic` resolves.
    """
    by_qual: dict[str, list[dict]] = {}
    simple: set[str] = set()
    namespaces: set[str] = set()
    anon: set[str] = set()
    for f in lean_files():
        ns_stack: list[str] = []
        rel = str(f.relative_to(ROOT))
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            m = NS_RE.match(line)
            if m:
                ns_stack.append(m.group(1))
                namespaces.add(".".join(ns_stack))
                continue
            if END_RE.match(line):
                if ns_stack:
                    ns_stack.pop()
                continue
            d = DECL_RE.match(line)
            if d:
                kind, name = d.group(1), d.group(2)
                ns = ".".join(ns_stack)
                qual = f"{ns}.{name}" if ns else name
                by_qual.setdefault(qual, []).append(
                    {"name": name, "namespace": ns, "kind": kind, "file": rel, "line": i}
                )
                simple.add(name)
                continue
            ai = ANON_INST_RE.match(line)
            if ai:
                # capture dotted identifiers in the instance type (e.g. `secp256k1.IsElliptic`)
                for ident in re.findall(r"[A-Za-z_][A-Za-z0-9_'.]*", ai.group(1)):
                    if "." in ident:
                        anon.add(".".join(ident.split(".")[-2:]))
                    anon.add(ident)
    return by_qual, simple, namespaces, anon


def cited_names() -> set[str]:
    if not VERIFIED.exists():
        return set()
    text = VERIFIED.read_text(encoding="utf-8")
    cites = set()
    for m in CITE_RE.finditer(text):
        q = m.group(0)
        if q.endswith("."):  # e.g. a bare "Ecdlp.Curve." prefix — not a decl
            continue
        cites.add(q)
    return cites


def resolve(cite: str, by_qual: dict, simple: set, namespaces: set, anon: set) -> bool:
    """Resolve a cited `Ecdlp.*` reference. It counts as resolved if it is a namespace (cited as
    context, not a theorem), a fully-qualified declaration, a known simple decl name, or an
    anonymous-instance target (by its last one/two components)."""
    if cite in namespaces:
        return True
    if cite in by_qual:
        return True
    last = cite.rsplit(".", 1)[-1]
    last2 = ".".join(cite.split(".")[-2:])
    return last in simple or last2 in anon or last in anon


def main() -> int:
    check = "--check" in sys.argv
    by_qual, simple, namespaces, anon = parse_declarations()
    cites = cited_names()

    missing = sorted(c for c in cites if not resolve(c, by_qual, simple, namespaces, anon))
    decls = sum(len(v) for v in by_qual.values())

    registry = {
        "schemaVersion": 1,
        "source": "Ecdlp/**/*.lean minus Targets/",
        "declaration_count": decls,
        "distinct_qualified_names": len(by_qual),
        "verified_md_citations": len(cites),
        "unresolved_citations": missing,
        "note": "Derived from Lean source; the headline ledger figure remains VERIFIED.md canonical.",
        "declarations": {
            q: v[0] | {"occurrences": len(v)} for q, v in sorted(by_qual.items())
        },
    }

    if check:
        if missing:
            print("result-registry check FAILED — VERIFIED.md cites theorem names not found "
                  "in the Lean source (renamed/removed?):")
            for m in missing:
                print(f"  - {m}")
            return 1
        print(f"result-registry check OK: {len(cites)} VERIFIED.md citations all resolve to "
              f"source declarations ({decls} decls, {len(by_qual)} distinct names).")
        return 0

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {decls} declarations, {len(by_qual)} distinct names, "
          f"{len(cites)} VERIFIED.md citations, {len(missing)} unresolved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
