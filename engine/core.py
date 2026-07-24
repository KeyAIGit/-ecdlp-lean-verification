"""Decision/selection layer for ECDLP research candidates.

This module does NOT discover attack mechanisms. It does three things, and refuses
to do more:

  1. **Admissibility** — boolean gates. A candidate either may be worked on at a
     given tier or it may not. Gates are never blended into a score.
  2. **Value** — for admissible candidates only, expected information gain per unit
     cost, computed from likelihoods the proposer commits to BEFORE running.
  3. **Memory** — a resolution taxonomy in which a negative result is only accepted
     if it says what would reopen it.

Design decisions worth stating, because they are the parts that could reasonably
have gone the other way:

*Gates are boolean, value is continuous, and the two are never multiplied.* A
score of the shape `relevance x plausibility x falsifiability x ... / cost`
conflates "may we do this at all" with "how much is it worth", so a candidate can
pass by being mediocre at everything while a single zero silently annihilates an
otherwise decisive proposal. Here a gate failure makes a candidate inadmissible and
it is never ranked; only survivors get a number.

*Information gain is computed, not asserted.* `expected_information_gain` as a
hand-assigned 0..1 dial is unfalsifiable and rewards optimism. Instead the proposer
must pre-register, for each possible outcome, how likely that outcome is if the
route is live and if it is dead. Mutual information between outcome and liveness
then follows by arithmetic. The point is not numerical precision — the priors are
subjective — it is that the commitment happens before the data and is auditable
afterwards (see `brier_score`).

*A consequence worth accepting deliberately:* for ECDLP every honest prior on
"this route is live" is small. With a small prior, information gain is dominated by
outcomes that would decisively **falsify**. So this layer systematically prefers
cheap, sharply-falsifying probes over expensive confirmatory ones. That is not a
bug to be tuned away; it matches what the project's own experiment history did.

*Threat model is checked first and mechanically.* The dominant failure mode in
ECDLP literature is threat-model drift: leakage, interval promises, many targets,
or reusable precomputation quietly replace the plain single-target problem, and the
result reads as a break. Anything whose declared threat model is not the primary one
is shelved before any other consideration, and shelving is not a judgement about the
work's quality.
"""

from __future__ import annotations

import json
import math
import pathlib
from dataclasses import dataclass, field
from typing import Any

REPO = pathlib.Path(__file__).resolve().parent.parent
SUBSTRATE = REPO / "repo" / "ECDLP_DECISION_SUBSTRATE.json"
HYPOTHESES = REPO / "experiments" / "HYPOTHESES.yaml"
PREREG = REPO / "engine" / "preregistrations.yaml"

#: The one threat model that counts as progress on the stated target. Everything
#: else is shelved by :func:`threat_model_gate` regardless of merit.
PRIMARY_THREAT_MODEL = "classical-single-target-plain"

#: Terminal states a candidate can resolve to. Deliberately finer than
#: pass/fail: `inapplicable` and `resource_exhausted` must not be recorded as
#: evidence against a mechanism, and `bounded_negative` must not be inflated into
#: a general impossibility claim.
RESOLUTIONS = {
    "proved": "Kernel-verified in Lean. The only state that may enter the ledger.",
    "supported": "The pre-registered prediction survived at the scale tested. NOT an "
                 "attack and not a complexity claim: it means the candidate has earned "
                 "the right to be evaluated at the promotion tier.",
    "falsified": "The pre-registered prediction was contradicted by the measurement.",
    "bounded_negative": "No effect within the stated bound. Says nothing outside it.",
    "inapplicable": "Screened out before measurement (e.g. threat model). Not evidence.",
    "inconclusive": "Ran, but the observable did not separate the hypotheses.",
    "resource_exhausted": "Stopped on budget. Not evidence about the mechanism.",
}

#: Resolutions that are claims about the world and therefore must carry an
#: explicit statement of what would reopen them.
_NEEDS_REOPENING = {"falsified", "bounded_negative"}


# --------------------------------------------------------------------------
# Information gain
# --------------------------------------------------------------------------

def entropy_bits(p: float) -> float:
    """Binary entropy of a Bernoulli(p), in bits. 0 at p in {0,1}."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def expected_information_gain(prior_live: float,
                              likelihoods: dict[str, dict[str, float]]) -> float:
    """Mutual information (bits) between the experiment outcome and route liveness.

    ``likelihoods`` maps each pre-registered outcome to ``{"live": .., "dead": ..}``,
    i.e. P(outcome | route is live) and P(outcome | route is dead). Each of the two
    conditional distributions must sum to 1 across outcomes; :func:`validate_prereg`
    enforces that, so this function assumes it.

    Returns ``H(prior) - E_outcome[H(posterior)]``, which is 0 exactly when the
    outcome is independent of liveness — the honest score for an experiment that
    cannot distinguish anything, however interesting it looks.
    """
    prior_entropy = entropy_bits(prior_live)
    expected_posterior = 0.0
    for lk in likelihoods.values():
        p_o = prior_live * lk["live"] + (1.0 - prior_live) * lk["dead"]
        if p_o <= 0.0:
            continue
        posterior_live = (prior_live * lk["live"]) / p_o
        expected_posterior += p_o * entropy_bits(posterior_live)
    # Clamp: mutual information is non-negative; tiny negatives are float noise.
    return max(0.0, prior_entropy - expected_posterior)


def predicted_marginal(prior_live: float,
                       likelihoods: dict[str, dict[str, float]]) -> dict[str, float]:
    """The outcome distribution a pre-registration commits to, ``P(outcome)``.

    Derived rather than stored. An earlier draft asked the proposer to write this
    out alongside the likelihoods; keeping two representations of the same
    commitment in sync by hand produced arithmetic errors immediately, and a
    calibration score computed from a stale copy would be silently wrong.
    """
    return {
        outcome: prior_live * lk["live"] + (1.0 - prior_live) * lk["dead"]
        for outcome, lk in likelihoods.items()
    }


def brier_score(predicted: dict[str, float], actual_outcome: str) -> float:
    """Multi-category Brier score for one resolved pre-registration (lower better).

    Scores the *marginal* outcome distribution the proposer committed to against
    what actually happened. This is the term that penalises confidence: predicting
    an outcome at 0.9 and being wrong costs far more than having said 0.5.
    """
    total = 0.0
    for outcome, p in predicted.items():
        target = 1.0 if outcome == actual_outcome else 0.0
        total += (p - target) ** 2
    return total


# --------------------------------------------------------------------------
# Gates
# --------------------------------------------------------------------------

@dataclass
class GateResult:
    """Outcome of applying a tier's gates to one candidate."""

    candidate_id: str
    tier: str
    admissible: bool
    failures: list[str] = field(default_factory=list)
    shelved_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "tier": self.tier,
            "admissible": self.admissible,
            "failures": self.failures,
            "shelved_reason": self.shelved_reason,
        }


def threat_model_gate(candidate: dict[str, Any]) -> str | None:
    """Return a shelving reason, or ``None`` if the candidate targets the primary model.

    Runs before everything else. A candidate that studies a different threat model
    is shelved rather than rejected: the work may be perfectly good, it just cannot
    count as progress on plain single-target secp256k1, and conflating the two is
    the single most common way this field fools itself.
    """
    declared = candidate.get("threat_models") or []
    if not declared:
        return "no threat model declared"
    if PRIMARY_THREAT_MODEL not in declared:
        return f"targets {', '.join(declared)}, not {PRIMARY_THREAT_MODEL}"
    return None


#: Exploration tier: cheap, bounded, falsifiable probing. Deliberately does NOT
#: require a mechanism or a scaling argument — requiring those here is exactly the
#: deadlock this tier exists to break, since a mechanism usually cannot be found
#: without first probing.
EXPLORATION_REQUIREMENTS = {
    "prediction": "a pre-registered observable and threshold",
    "likelihoods": "P(outcome | live) and P(outcome | dead) for every outcome",
    "prior_live": "an explicit prior probability that the route is live",
    "baseline": "the baseline the measurement is compared against",
    "budget": "a bounded compute/time budget",
    "stop_condition": "a condition, fixed in advance, that ends the run",
    "scale": "the toy scale (small field / toy curve) the run is confined to",
}

#: Promotion tier: everything exploration requires, plus the claims that make a
#: result an attack rather than an observation.
PROMOTION_REQUIREMENTS = {
    **EXPLORATION_REQUIREMENTS,
    "mechanism": "an exact non-generic mechanism, stated",
    "cost_model": "a full cost model including relation generation and recovery",
    "scaling_evidence": "measurements at three or more sizes",
    "no_hidden_precomputation": "explicit statement that no precomputation or "
                                "conditioned input is folded into the cost",
    "independent_reproduction": "reproduced by a validator other than the author",
}


def apply_gates(candidate: dict[str, Any], tier: str) -> GateResult:
    """Apply the threat-model gate then the tier's requirements.

    ``tier`` is ``"exploration"`` or ``"promotion"``. Missing/empty fields are
    failures; nothing is inferred or defaulted, because a silently defaulted
    stop condition is worse than none.
    """
    if tier not in ("exploration", "promotion"):
        raise ValueError(f"unknown tier: {tier}")

    shelved = threat_model_gate(candidate)
    if shelved is not None:
        return GateResult(candidate["id"], tier, False, [], shelved)

    required = EXPLORATION_REQUIREMENTS if tier == "exploration" else PROMOTION_REQUIREMENTS
    failures = [f"missing {key}: {desc}"
                for key, desc in required.items()
                if not candidate.get(key)]

    if tier == "promotion":
        ev = candidate.get("scaling_evidence") or []
        if isinstance(ev, list) and 0 < len(ev) < 3:
            failures.append(
                f"scaling_evidence has {len(ev)} size(s); three or more are required "
                "before a trend may be claimed")

    return GateResult(candidate["id"], tier, not failures, failures)


def validate_prereg(candidate: dict[str, Any]) -> list[str]:
    """Structural errors in a candidate's pre-registration, as human-readable strings.

    Checked separately from :func:`apply_gates` because these are *malformed input*
    rather than an honest failure to meet a bar.
    """
    errors: list[str] = []

    prior = candidate.get("prior_live")
    if prior is not None and not (0.0 < prior < 1.0):
        errors.append(f"prior_live must lie strictly in (0,1), got {prior}")

    likelihoods = candidate.get("likelihoods") or {}
    if likelihoods:
        for state in ("live", "dead"):
            total = sum(lk.get(state, 0.0) for lk in likelihoods.values())
            if abs(total - 1.0) > 1e-6:
                errors.append(
                    f"P(outcome | {state}) sums to {total:.4f}, must be 1.0")
        for outcome, lk in likelihoods.items():
            if outcome not in RESOLUTIONS:
                errors.append(f"outcome {outcome!r} is not in the resolution taxonomy")
            for state in ("live", "dead"):
                if state not in lk:
                    errors.append(f"outcome {outcome!r} is missing P(.|{state})")

    resolution = candidate.get("resolution")
    if resolution is not None:
        if resolution not in RESOLUTIONS:
            errors.append(f"resolution {resolution!r} is not in the taxonomy")
        elif resolution in _NEEDS_REOPENING and not candidate.get("reopening_conditions"):
            errors.append(
                f"resolution {resolution!r} requires reopening_conditions: a negative "
                "result without a statement of what would reopen it is not reusable")

    return errors


# --------------------------------------------------------------------------
# Ranking
# --------------------------------------------------------------------------

@dataclass
class Ranked:
    candidate_id: str
    eig_bits: float
    cost_units: float
    priority: float
    title: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "title": self.title,
            "eig_bits": round(self.eig_bits, 4),
            "cost_units": self.cost_units,
            "priority_bits_per_unit": round(self.priority, 5),
        }


def rank(candidates: list[dict[str, Any]], tier: str = "exploration") -> list[Ranked]:
    """Rank the admissible candidates by information gain per unit cost.

    Inadmissible candidates are absent from the result rather than ranked low —
    the distinction between "not allowed" and "allowed but unpromising" is the
    point of separating gates from scores.
    """
    out: list[Ranked] = []
    for cand in candidates:
        if not apply_gates(cand, tier).admissible:
            continue
        if validate_prereg(cand):
            continue
        eig = expected_information_gain(cand["prior_live"], cand["likelihoods"])
        cost = float(cand.get("cost_units") or 1.0)
        out.append(Ranked(cand["id"], eig, cost, eig / cost, cand.get("title", "")))
    out.sort(key=lambda r: (-r.priority, r.candidate_id))
    return out


# --------------------------------------------------------------------------
# Canonical-source loading
# --------------------------------------------------------------------------

def load_substrate() -> dict[str, Any]:
    """The canonical decision substrate. Never written by this layer."""
    return json.loads(SUBSTRATE.read_text(encoding="utf-8"))


def substrate_primary_threat_model() -> str | None:
    """The threat model the substrate itself marks ``primary``, or ``None``.

    An independent anchor for :data:`PRIMARY_THREAT_MODEL`. Without it the
    threat-model checks are circular: they would use the same constant to decide
    both what must be shelved and what shelving is wrong, so corrupting the
    constant produces a self-consistent — and completely wrong — verdict. That is
    not hypothetical; it survived a first round of fault injection here.
    """
    primaries = [t["id"] for t in load_substrate().get("threat_models", [])
                 if t.get("primary")]
    return primaries[0] if len(primaries) == 1 else None


def load_preregistrations() -> list[dict[str, Any]]:
    """Pre-registered candidates, or ``[]`` when none have been filed yet."""
    if not PREREG.exists():
        return []
    try:
        import yaml
    except ImportError:  # pragma: no cover - yaml ships with the repo's CI
        return []
    data = yaml.safe_load(PREREG.read_text(encoding="utf-8")) or {}
    return data.get("candidates", [])


def candidates_from_routes() -> list[dict[str, Any]]:
    """Project the substrate's routes into candidate records.

    Routes carry a threat model and a status but no pre-registration, so they are
    exactly the population on which the threat-model gate can be checked against a
    decision that was already made independently — which is what
    ``engine/retro.py`` uses them for.
    """
    sub = load_substrate()
    return [
        {
            "id": r["id"],
            "title": r.get("title", ""),
            "threat_models": r.get("threat_models", []),
            "substrate_status": r.get("status"),
            "authorized_experiment": r.get("authorized_experiment", False),
        }
        for r in sub.get("routes", [])
    ]
