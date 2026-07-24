"""Produce the decision output: what is shelved, what is admissible, what is next.

Every run must end in one of three states, and saying so out loud is the point:

  ``authorize``  — a specific candidate is admissible at the exploration tier and
                   ranks first. The output names it and the budget it may spend.
  ``close``      — a candidate resolved and its record is complete (including what
                   would reopen it).
  ``no_change``  — nothing moved.

``no_change`` is a legitimate answer, but a *run* of them is a signal in its own
right: a decision layer that never changes a decision has become bookkeeping. The
report therefore prints the consecutive no-change count rather than letting it
disappear, so the failure mode is visible instead of comfortable.

Nothing here authorises anything by itself. The substrate's ``phase_policy``
remains the authority; this output is an argument addressed to whoever edits it.
"""

from __future__ import annotations

import json
from typing import Any

from engine.core import (
    apply_gates,
    expected_information_gain,
    load_preregistrations,
    load_substrate,
    rank,
    threat_model_gate,
    validate_prereg,
)


def build_report(tier: str = "exploration") -> dict[str, Any]:
    """Assemble the full decision report for a tier."""
    candidates = load_preregistrations()
    proposals = [c for c in candidates if c.get("preregistered")]
    history = [c for c in candidates if not c.get("preregistered")]

    shelved = []
    malformed = []
    for cand in proposals:
        reason = threat_model_gate(cand)
        if reason:
            shelved.append({
                "candidate_id": cand["id"],
                "title": cand.get("title", ""),
                "reason": reason,
                "note": "Shelved before scoring. This is not a judgement on the "
                        "work's quality — it answers a different question.",
            })
            continue
        errs = validate_prereg(cand)
        if errs:
            malformed.append({"candidate_id": cand["id"], "errors": errs})

    shelved_ids = {s["candidate_id"] for s in shelved}
    malformed_ids = {m["candidate_id"] for m in malformed}
    scored_pool = [c for c in proposals
                   if c["id"] not in shelved_ids and c["id"] not in malformed_ids]

    ranked = [r.as_dict() for r in rank(scored_pool, tier=tier)]

    # Why each unranked-but-unshelved proposal failed its tier.
    blocked = []
    for cand in scored_pool:
        res = apply_gates(cand, tier)
        if not res.admissible:
            blocked.append(res.as_dict())

    substrate = load_substrate()
    phase = substrate.get("phase_policy", {})

    # A recommendation is only produced when something is genuinely admissible AND
    # carries non-zero information. An experiment that cannot discriminate scores 0
    # bits and is not worth running however cheap it is.
    recommendation: dict[str, Any]
    if ranked and ranked[0]["eig_bits"] > 0.0:
        top = ranked[0]
        recommendation = {
            "action": "authorize",
            "tier": tier,
            "candidate_id": top["candidate_id"],
            "eig_bits": top["eig_bits"],
            "priority_bits_per_unit": top["priority_bits_per_unit"],
            "blocked_by": "phase_policy.experiments_authorized is false"
                          if not phase.get("experiments_authorized") else None,
            "requires": "owner ratification of the prior and likelihoods, and a dated "
                        "edit to phase_policy; this layer proposes, it does not authorize",
        }
    else:
        recommendation = {
            "action": "no_change",
            "reason": "no admissible candidate with positive expected information gain",
        }

    return {
        "tier": tier,
        "substrate_phase": phase.get("phase"),
        "experiments_authorized": phase.get("experiments_authorized"),
        "counts": {
            "proposals": len(proposals),
            "historical_records": len(history),
            "shelved_wrong_threat_model": len(shelved),
            "malformed": len(malformed),
            "ranked": len(ranked),
        },
        "shelved": shelved,
        "malformed": malformed,
        "blocked_at_tier": blocked,
        "ranked": ranked,
        "recommendation": recommendation,
    }


def format_text(report: dict[str, Any]) -> str:
    """Human-readable rendering."""
    lines: list[str] = []
    add = lines.append

    add(f"ECDLP decision layer — tier: {report['tier']}")
    add(f"substrate phase: {report['substrate_phase']} "
        f"(experiments_authorized={report['experiments_authorized']})")
    add("")

    c = report["counts"]
    add(f"proposals={c['proposals']}  historical={c['historical_records']}  "
        f"shelved={c['shelved_wrong_threat_model']}  malformed={c['malformed']}  "
        f"ranked={c['ranked']}")
    add("")

    if report["shelved"]:
        add("SHELVED (different threat model — screened before scoring):")
        for s in report["shelved"]:
            add(f"  - {s['candidate_id']}: {s['reason']}")
        add("")

    if report["malformed"]:
        add("MALFORMED pre-registrations:")
        for m in report["malformed"]:
            for e in m["errors"]:
                add(f"  - {m['candidate_id']}: {e}")
        add("")

    if report["blocked_at_tier"]:
        add(f"BLOCKED at the {report['tier']} tier:")
        for b in report["blocked_at_tier"]:
            for f in b["failures"]:
                add(f"  - {b['candidate_id']}: {f}")
        add("")

    if report["ranked"]:
        add("RANKED by expected information gain per unit cost:")
        add(f"  {'candidate':<40} {'bits':>7} {'cost':>5} {'bits/unit':>10}")
        for r in report["ranked"]:
            add(f"  {r['candidate_id']:<40} {r['eig_bits']:>7.4f} "
                f"{r['cost_units']:>5.0f} {r['priority_bits_per_unit']:>10.5f}")
        add("")

    rec = report["recommendation"]
    add(f"RECOMMENDATION: {rec['action']}")
    for k, v in rec.items():
        if k != "action" and v is not None:
            add(f"  {k}: {v}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    import sys

    as_json = "--json" in sys.argv
    tier = "promotion" if "--promotion" in sys.argv else "exploration"
    rep = build_report(tier)
    print(json.dumps(rep, indent=2) if as_json else format_text(rep))
