"""Retrospective validation of the decision layer against decisions already made.

A selector that has never been checked against known outcomes is not a selector;
it is a number generator with a schema. This module replays the gates in
``engine/core.py`` over the project's *existing* route dispositions — which were
reached independently, by hand, before this layer existed — and asks whether the
mechanical gates reproduce them.

Four checks, of decreasing strength:

  R1a **Primary-model anchor (hard).** The layer's ``PRIMARY_THREAT_MODEL`` must
      equal the threat model the substrate itself marks ``primary``. Without this
      independent anchor every other threat-model check is circular — it would use
      the same constant to decide both what must be shelved and what shelving is
      wrong, so a corrupted constant yields a self-consistent, wrong verdict.

  R1  **Threat-model reproduction (hard).** Every route the substrate independently
      classified ``separate_threat_model`` must be shelved by ``threat_model_gate``,
      and no route carrying the primary threat model may be shelved. This is a
      genuine test: the labels were assigned by a human reading the literature, the
      gate reads only the declared ``threat_models`` field, and the two could
      disagree.

  R2  **Non-degeneracy (hard).** A gate that admits everything, or nothing, is not
      a gate. The promotion tier must reject the routes the project itself declined
      to promote (all of them, as of RS-2026-07-22-001), while the exploration tier
      must not be vacuous.

  R3  **Calibration (reported, not gated).** For pre-registrations that have since
      resolved, the mean Brier score of the committed outcome distribution. Gating
      on this would be premature with a handful of resolved items; it is reported so
      that systematic overconfidence becomes visible as the record grows.

R0, R1a, R1 and R2 are wired into CI by ``scripts/check_engine.py``. If a future edit makes
the gates disagree with the recorded dispositions, the build fails and someone has
to say which of the two is wrong — the gate or the disposition. That is the whole
point: it makes drift between the mechanism and the judgement impossible to ignore.
"""

from __future__ import annotations

from typing import Any

from engine.core import (
    PRIMARY_THREAT_MODEL,
    apply_gates,
    brier_score,
    candidates_from_routes,
    load_preregistrations,
    load_substrate,
    predicted_marginal,
    substrate_primary_threat_model,
    threat_model_gate,
    validate_prereg,
)

#: Substrate statuses that mean "this was set aside because it answers a different
#: question", as opposed to "this was examined and found wanting on the target".
SEPARATE_MODEL_STATUS = "separate_threat_model"


def check_primary_anchor() -> dict[str, Any]:
    """R1a — the layer's notion of "primary" must match the substrate's own.

    The independent anchor. Every other threat-model check reads
    ``PRIMARY_THREAT_MODEL``; if that constant drifts from the substrate's
    ``primary: true`` declaration, those checks stay internally consistent while
    being wrong about the world. Editing either side must therefore be a conscious
    act that turns this check red.
    """
    declared = substrate_primary_threat_model()
    return {
        "check": "R1a_primary_threat_model_anchor",
        "engine_constant": PRIMARY_THREAT_MODEL,
        "substrate_declares": declared,
        "passed": declared is not None and declared == PRIMARY_THREAT_MODEL,
    }


def check_threat_model_reproduction() -> dict[str, Any]:
    """R1 — do the mechanical gate and the hand-assigned labels agree?"""
    routes = candidates_from_routes()

    should_shelve = {r["id"] for r in routes
                     if r["substrate_status"] == SEPARATE_MODEL_STATUS}
    did_shelve = {r["id"] for r in routes if threat_model_gate(r) is not None}

    missed = sorted(should_shelve - did_shelve)      # labelled separate, gate let through
    extra = sorted(did_shelve - should_shelve)       # gate shelved, label says otherwise

    # An "extra" is only a real disagreement if the route genuinely lacks the
    # primary threat model; report the reason so a reviewer can judge each one.
    extra_detail = [
        {"id": r["id"], "status": r["substrate_status"],
         "reason": threat_model_gate(r), "declared": r["threat_models"]}
        for r in routes if r["id"] in set(extra)
    ]

    # The other half of the requirement, and the one a "shelving more is always
    # safe" reading gets wrong: a gate that shelves routes which DO carry the
    # primary threat model is not conservative, it is broken — it would quietly
    # remove the project's actual work from consideration. Fault-injecting a wrong
    # PRIMARY_THREAT_MODEL is caught here and nowhere else.
    wrongly_shelved = sorted(
        r["id"] for r in routes
        if PRIMARY_THREAT_MODEL in (r.get("threat_models") or [])
        and threat_model_gate(r) is not None
    )

    return {
        "check": "R1_threat_model_reproduction",
        "routes_total": len(routes),
        "labelled_separate": sorted(should_shelve),
        "gate_shelved": sorted(did_shelve),
        "missed": missed,
        "wrongly_shelved": wrongly_shelved,
        "unexpected": extra_detail,
        # Both directions are hard: never let a different-threat-model route
        # through, and never shelve a primary-threat-model one. Shelving more than
        # the *label* is acceptable (the labels conflate two axes — see the README);
        # shelving more than the *threat model* is not.
        "passed": not missed and not wrongly_shelved,
    }


def check_non_degeneracy() -> dict[str, Any]:
    """R2 — the gates must actually discriminate, and must agree with 'promote none'."""
    routes = candidates_from_routes()

    # Routes carry no pre-registration, so none can satisfy the promotion tier.
    # That is the correct answer here: RS-2026-07-22-001 promoted zero routes.
    promotable = [r["id"] for r in routes if apply_gates(r, "promotion").admissible]

    # Nor may a bare route slip through the exploration tier: exploration is cheap,
    # but it still demands a prediction, a baseline, a budget and a stop condition.
    explorable = [r["id"] for r in routes if apply_gates(r, "exploration").admissible]

    substrate = load_substrate()
    decision = substrate.get("route_selection", {})
    selected = decision.get("selected_route_ids", [])

    return {
        "check": "R2_non_degeneracy",
        "substrate_decision": decision.get("decision"),
        "substrate_selected": selected,
        "gate_promotable": promotable,
        "gate_explorable_without_prereg": explorable,
        # Agreement with the recorded decision, plus the requirement that an
        # unfilled record cannot walk through either tier.
        "passed": not promotable and not explorable and not selected,
    }


def check_calibration() -> dict[str, Any]:
    """R3 — Brier score over resolved pre-registrations (reported, not gated).

    Only candidates that were genuinely pre-registered are scorable. The historical
    records deliberately carry no prior and no likelihoods, because inventing them
    after the fact is exactly the failure this layer exists to prevent — so they are
    counted and excluded rather than silently skipped.
    """
    all_resolved = [c for c in load_preregistrations() if c.get("resolution")]
    scorable = [c for c in all_resolved
                if c.get("preregistered") and c.get("likelihoods") and c.get("prior_live")]

    scores = []
    for cand in scorable:
        predicted = predicted_marginal(cand["prior_live"], cand["likelihoods"])
        scores.append({
            "candidate_id": cand["id"],
            "resolution": cand["resolution"],
            "brier": round(brier_score(predicted, cand["resolution"]), 4),
        })
    mean = round(sum(s["brier"] for s in scores) / len(scores), 4) if scores else None
    return {
        "check": "R3_calibration",
        "resolved_total": len(all_resolved),
        "resolved_but_not_preregistered": len(all_resolved) - len(scorable),
        "scored": scores,
        "mean_brier": mean,
        "note": "Reported, not gated. The pre-existing record is unscorable by "
                "construction: those experiments predate pre-registration, so any "
                "likelihood attached to them now would be written after seeing the "
                "result. Calibration begins with the first pre-registered run.",
        "passed": True,
    }


def check_prereg_wellformed() -> dict[str, Any]:
    """Structural validation of every filed pre-registration."""
    problems = []
    for cand in load_preregistrations():
        errs = validate_prereg(cand)
        if errs:
            problems.append({"candidate_id": cand.get("id", "<no id>"), "errors": errs})
    return {
        "check": "R0_preregistrations_wellformed",
        "checked": len(load_preregistrations()),
        "problems": problems,
        "passed": not problems,
    }


def run_all() -> dict[str, Any]:
    """Run every retrospective check and summarise."""
    checks = [
        check_prereg_wellformed(),
        check_primary_anchor(),
        check_threat_model_reproduction(),
        check_non_degeneracy(),
        check_calibration(),
    ]
    return {
        "primary_threat_model": PRIMARY_THREAT_MODEL,
        "checks": checks,
        "passed": all(c["passed"] for c in checks),
    }


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    report = run_all()
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["passed"] else 1)
