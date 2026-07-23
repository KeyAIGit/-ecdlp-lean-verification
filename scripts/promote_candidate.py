#!/usr/bin/env python3
"""Promote Lean-accepted candidate proofs from `candidates/` into the verified base.

The autonomous prover loop (`scripts/prover_loop.py`) writes each Lean-accepted proof to
`candidates/<id>.lean` (verified by `lake env lean` in that run). This script performs the
*mechanical* promotion so `prove.yml` can open a PR that already carries the finished change
instead of a raw candidate for a human to wire by hand:

  * move `candidates/<id>.lean` -> `Ecdlp/Proved/<Module>.lean`;
  * add `import Ecdlp.Proved.<Module>` to `Ecdlp.lean` (idempotent);
  * set `targets/<id>.json` `status` -> `verified`, record `verified_in`, and consume the
    open stem: remove it from `Ecdlp/Targets/` and null the `stem_file` pointer, so
    `Ecdlp/Targets/` holds only open stems and the registry never carries dead pointers
    (`scripts/check_targets.py` gates this);
  * append a row to a dedicated, script-managed table in `VERIFIED.md` (created on first use)
    so the coverage entry exists without touching the hand-written prose sections.

HARD RULES (this script only MOVES kernel-accepted proofs; it never proves or weakens anything):
  * `main` is never touched — only the working tree is edited; `prove.yml` commits the result
    onto the `prover/candidates` PR branch. A delegated maintainer reviews it; nothing auto-merges.
  * A candidate is promoted ONLY if it declares a NAMED `theorem`/`lemma`/`def`/`instance`
    and contains no `sorry`/`admit`. An anonymous `example` is verification-only and SKIPPED
    (e.g. the smoke target), as is anything with a leaked obligation.
  * An `import Ecdlp.Proved.*` is added ONLY for a file placed under `Ecdlp/Proved/`.
  * Idempotent: a target already `verified`, an existing Proved file, an already-present import,
    or an existing ledger row are each left as-is (no duplicates, no clobber).

Usage:
  python3 scripts/promote_candidate.py            # promote everything in candidates/
  python3 scripts/promote_candidate.py --dry-run  # print planned actions, write nothing
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = ROOT / "candidates"
PROVED = ROOT / "Ecdlp" / "Proved"
REGISTRY = ROOT / "targets"
ECDLP_ROOT = ROOT / "Ecdlp.lean"
VERIFIED = ROOT / "VERIFIED.md"

# Marker delimiting the script-managed ledger table (created on first promotion).
LEDGER_HEADER = "### Auto-promoted by the prover loop (tier-0 / model — coverage, NOT headline)"
LEDGER_INTRO = (
    "Kernel-accepted candidate proofs promoted mechanically by `scripts/promote_candidate.py` "
    "from open `Ecdlp/Targets/` stems the autonomous loop closed. Each was verified by "
    "`lake env lean`; these are **coverage** entries, tracked separately and **excluded from the "
    "headline count**. A human reviewed and merged the promoting PR."
)
LEDGER_TABLE_HEAD = "| Result | Lean name | File | Method | Status |\n|---|---|---|---|---|"

DECL_RE = re.compile(r"^\s*(?:noncomputable\s+|private\s+|protected\s+|scoped\s+)*"
                     r"(theorem|lemma|def|instance)\s+([A-Za-z_][A-Za-z0-9_'ₐ-ₜ₀-₉]*)",
                     re.MULTILINE)
NS_RE = re.compile(r"^\s*namespace\s+(\S+)", re.MULTILINE)


def module_name(tid: str) -> str:
    """PascalCase module name from a target id (e.g. `frontier_orderOf_one` -> `FrontierOrderOfOne`)."""
    parts = re.split(r"[^A-Za-z0-9]+", tid)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def declared_name(text: str) -> str | None:
    """Return the first named decl (theorem/lemma/def/instance), or None for an anonymous
    `example` / no named decl."""
    m = DECL_RE.search(text)
    return m.group(2) if m else None


def qualified_name(text: str, name: str) -> str:
    ns = NS_RE.search(text)
    return f"{ns.group(1)}.{name}" if ns else name


def add_import(module: str, dry: bool) -> bool:
    """Add `import Ecdlp.Proved.<module>` to Ecdlp.lean if absent. Returns True if it (would) change."""
    line = f"import Ecdlp.Proved.{module}"
    text = ECDLP_ROOT.read_text(encoding="utf-8")
    if line in text.splitlines():
        return False
    if not dry:
        body = text.rstrip("\n") + "\n" + line + "\n"
        ECDLP_ROOT.write_text(body, encoding="utf-8")
    return True


def ensure_ledger_section(text: str) -> str:
    if LEDGER_HEADER in text:
        return text
    block = f"\n{LEDGER_HEADER}\n{LEDGER_INTRO}\n\n{LEDGER_TABLE_HEAD}\n"
    return text.rstrip("\n") + "\n" + block


def append_ledger_row(qname: str, module: str, method: str, dry: bool) -> bool:
    """Append one row under the managed ledger table if that Lean name is not already cited."""
    text = VERIFIED.read_text(encoding="utf-8")
    if f"`{qname}`" in text:
        return False
    text = ensure_ledger_section(text)
    row = (f"| Auto-promoted candidate `{qname}` (loop-closed target) | `{qname}` | "
           f"Ecdlp/Proved/{module}.lean | {method} | proved |")
    lines = text.splitlines()
    # insert right after the managed table header row (the `|---|` separator following LEDGER_TABLE_HEAD)
    out, inserted = [], False
    for i, ln in enumerate(lines):
        out.append(ln)
        if not inserted and ln.startswith("|---|---|---|---|---|") and i >= 1 \
                and lines[i - 1].startswith("| Result | Lean name |"):
            out.append(row)
            inserted = True
    if not inserted:  # section existed but table head not found — append at end defensively
        out.append(row)
    if not dry:
        VERIFIED.write_text("\n".join(out) + "\n", encoding="utf-8")
    return True


def promote_one(cand: Path, dry: bool) -> tuple[str, str]:
    """Returns (outcome, detail). outcome in {promoted, skipped}."""
    tid = cand.stem
    text = cand.read_text(encoding="utf-8")
    if "sorry" in text or "admit" in text:
        return "skipped", f"{tid}: candidate contains sorry/admit — never promote"
    name = declared_name(text)
    if name is None:
        return "skipped", f"{tid}: anonymous example / no named decl — verification-only, not promotable"
    spec_path = REGISTRY / f"{tid}.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.exists() else {"id": tid}
    if spec.get("status") == "verified":
        return "skipped", f"{tid}: already verified — idempotent no-op"
    module = module_name(tid)
    proved_path = PROVED / f"{module}.lean"
    if proved_path.exists():
        # Never clobber an existing verified module (a name collision the human must resolve).
        return "skipped", f"{tid}: Ecdlp/Proved/{module}.lean already exists — refusing to overwrite"
    qname = qualified_name(text, name)
    method = "native_decide" if "native_decide" in text else "Mathlib / tier-0 tactic"
    stem_rel = spec.get("stem_file")
    stem_path = (ROOT / stem_rel) if stem_rel else None

    if dry:
        actions = [f"write {proved_path.relative_to(ROOT)}",
                   f"import Ecdlp.Proved.{module}",
                   f"targets/{tid}.json status -> verified",
                   f"VERIFIED.md ledger row for `{qname}`"]
        if stem_rel:
            actions.append(f"consume stem: null stem_file"
                           + (f" and remove {stem_rel}" if stem_path.exists() else ""))
        return "promoted", f"{tid}: [dry-run] " + "; ".join(actions)

    proved_path.write_text(text, encoding="utf-8")
    add_import(module, dry=False)
    spec["status"] = "verified"
    spec["verified_in"] = f"Ecdlp/Proved/{module}.lean"
    # The stem is consumed by promotion: Ecdlp/Targets/ holds only OPEN stems, and a
    # verified target must not keep a pointer at a deleted file (check_targets.py gates it).
    if stem_path is not None and stem_path.exists():
        stem_path.unlink()
    spec["stem_file"] = None
    spec_path.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    append_ledger_row(qname, module, method, dry=False)
    cand.unlink()  # consumed
    return "promoted", f"{tid}: promoted `{qname}` -> Ecdlp/Proved/{module}.lean"


def main() -> int:
    ap = argparse.ArgumentParser(description="Promote Lean-accepted candidates into Ecdlp/Proved/.")
    ap.add_argument("--dry-run", action="store_true", help="print planned actions, write nothing")
    args = ap.parse_args()

    if not CANDIDATES.exists():
        print("no candidates/ directory — nothing to promote")
        return 0
    cands = sorted(CANDIDATES.glob("*.lean"))
    if not cands:
        print("candidates/ is empty — nothing to promote")
        return 0

    promoted, skipped = 0, 0
    for cand in cands:
        outcome, detail = promote_one(cand, dry=args.dry_run)
        print(f"[{outcome}] {detail}")
        promoted += outcome == "promoted"
        skipped += outcome == "skipped"
    print(f"\npromoted {promoted}, skipped {skipped}"
          + (" (dry-run — no files written)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
