#!/usr/bin/env python3
"""Honesty gate for the domain registry (Phase-1 platform layer).

The registry (`domains/registry.json`) lets the site show a portfolio of research domains,
of which secp256k1/ECDLP is the only *live* one and the rest are honest placeholders. This
gate makes the placeholders provably honest: a domain may only advertise metrics if it
actually has the artifacts to back them.

Rules enforced (see domains/README.md):
  1. every domain has id / title / status / slots;
  2. a 'live' domain has every non-verifier slot file present, and any named
     metrics_source / frontier_source exists on disk;
  3. a 'planned'/'exploratory' domain claims NO metrics (both sources are null);
  4. at least one 'live' domain exists;
  5. ids are unique and statuses are from the known set.

Exit 0 = honest, 1 = a violation (fails CI). Zero third-party deps.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "domains" / "registry.json"
VALID_STATUS = {"live", "planned", "exploratory"}
# Verifier is a capability name (e.g. "lean-kernel"), not a file path, so it is not
# existence-checked here; the other two slots are repo files.
FILE_SLOTS = ("corpus", "ontology")


def fail(errors: list[str]) -> int:
    print("domain-registry check FAILED:")
    for e in errors:
        print(f"- {e}")
    return 1


def main() -> int:
    if not REGISTRY.exists():
        return fail([f"missing {REGISTRY.relative_to(ROOT)}"])
    try:
        reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return fail([f"registry is not valid JSON: {e}"])

    errors: list[str] = []
    domains = reg.get("domains")
    if not isinstance(domains, list) or not domains:
        return fail(["registry has no 'domains' list"])

    seen_ids: set[str] = set()
    live_count = 0
    for i, d in enumerate(domains):
        tag = d.get("id") or f"#{i}"
        for req in ("id", "title", "status", "slots"):
            if req not in d:
                errors.append(f"{tag}: missing required field '{req}'")
        did = d.get("id")
        if did:
            if did in seen_ids:
                errors.append(f"{tag}: duplicate id")
            seen_ids.add(did)
        status = d.get("status")
        if status not in VALID_STATUS:
            errors.append(f"{tag}: status {status!r} not in {sorted(VALID_STATUS)}")
        slots = d.get("slots") or {}
        m_src = d.get("metrics_source")
        f_src = d.get("frontier_source")

        if status == "live":
            live_count += 1
            for s in FILE_SLOTS:
                path = slots.get(s)
                if not path:
                    errors.append(f"{tag}: live domain must fill slot '{s}'")
                elif not (ROOT / path).exists():
                    errors.append(f"{tag}: live slot '{s}' -> missing file {path}")
            for name, src in (("metrics_source", m_src), ("frontier_source", f_src)):
                if src and not (ROOT / src).exists():
                    errors.append(f"{tag}: {name} -> missing file {src}")
        else:
            # placeholders must not borrow metrics they haven't earned
            if m_src is not None or f_src is not None:
                errors.append(
                    f"{tag}: {status} domain must not claim metrics "
                    f"(metrics_source/frontier_source must be null)")

    if live_count == 0:
        errors.append("registry has no 'live' domain — the platform needs at least one real instance")

    if errors:
        return fail(errors)
    print(f"domain-registry check OK: {len(domains)} domains "
          f"({live_count} live, {len(domains) - live_count} placeholder), all honest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
