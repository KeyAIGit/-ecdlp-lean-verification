"""Tests for the decision layer.

Plain unittest, no third-party runner, matching the repo's other test scripts
(`scripts/test_check_axioms.py` etc.) so CI can call it directly.

The interesting tests are the adversarial ones: that a high-prior cheap candidate
with the wrong threat model is still refused, that an experiment which cannot
discriminate scores exactly zero, and that a negative result without reopening
conditions is rejected.
"""

from __future__ import annotations

import math
import unittest

from engine.core import (
    PRIMARY_THREAT_MODEL,
    RESOLUTIONS,
    apply_gates,
    brier_score,
    entropy_bits,
    expected_information_gain,
    predicted_marginal,
    rank,
    threat_model_gate,
    validate_prereg,
)
from engine import retro


def _well_formed(**overrides):
    """A minimal candidate that passes the exploration tier."""
    cand = {
        "id": "T-OK",
        "title": "test",
        "threat_models": [PRIMARY_THREAT_MODEL],
        "prediction": "observable X exceeds threshold T",
        "baseline": "generic",
        "budget": "1 CPU-hour",
        "stop_condition": "one pass",
        "scale": "toy",
        "prior_live": 0.05,
        "cost_units": 1,
        "likelihoods": {
            "supported": {"live": 0.7, "dead": 0.05},
            "bounded_negative": {"live": 0.3, "dead": 0.95},
        },
    }
    cand.update(overrides)
    return cand


class TestEntropyAndGain(unittest.TestCase):
    def test_entropy_endpoints_are_zero(self):
        self.assertEqual(entropy_bits(0.0), 0.0)
        self.assertEqual(entropy_bits(1.0), 0.0)

    def test_entropy_maximal_at_one_half(self):
        self.assertAlmostEqual(entropy_bits(0.5), 1.0)

    def test_uninformative_experiment_scores_exactly_zero(self):
        """If the outcome is independent of liveness, the gain must be 0 bits.

        This is the case a hand-assigned 'expected information gain' dial gets
        wrong most often: the experiment looks interesting and costs little, but
        cannot separate the hypotheses at all.
        """
        likelihoods = {
            "supported": {"live": 0.4, "dead": 0.4},
            "bounded_negative": {"live": 0.6, "dead": 0.6},
        }
        self.assertAlmostEqual(expected_information_gain(0.3, likelihoods), 0.0, places=12)

    def test_perfectly_separating_experiment_recovers_full_prior_entropy(self):
        likelihoods = {
            "supported": {"live": 1.0, "dead": 0.0},
            "bounded_negative": {"live": 0.0, "dead": 1.0},
        }
        for prior in (0.01, 0.1, 0.5, 0.9):
            self.assertAlmostEqual(
                expected_information_gain(prior, likelihoods),
                entropy_bits(prior), places=10)

    def test_gain_never_exceeds_prior_entropy(self):
        likelihoods = {
            "supported": {"live": 0.8, "dead": 0.1},
            "bounded_negative": {"live": 0.2, "dead": 0.9},
        }
        for prior in (0.001, 0.03, 0.25, 0.5, 0.99):
            self.assertLessEqual(
                expected_information_gain(prior, likelihoods),
                entropy_bits(prior) + 1e-12)

    def test_gain_is_never_negative(self):
        likelihoods = {
            "supported": {"live": 0.5000001, "dead": 0.5},
            "bounded_negative": {"live": 0.4999999, "dead": 0.5},
        }
        self.assertGreaterEqual(expected_information_gain(0.02, likelihoods), 0.0)

    def test_marginal_is_a_distribution(self):
        cand = _well_formed()
        marg = predicted_marginal(cand["prior_live"], cand["likelihoods"])
        self.assertAlmostEqual(sum(marg.values()), 1.0, places=12)


class TestThreatModelGate(unittest.TestCase):
    def test_primary_model_passes(self):
        self.assertIsNone(threat_model_gate(_well_formed()))

    def test_missing_declaration_is_shelved(self):
        self.assertIsNotNone(threat_model_gate(_well_formed(threat_models=[])))

    def test_high_prior_cheap_wrong_model_is_still_refused(self):
        """The adversarial case the whole ordering exists for.

        A candidate with a high prior and the lowest possible cost would top any
        multiplicative ranking. It must not be ranked at all.
        """
        cand = _well_formed(id="T-CONDITIONED",
                            threat_models=["classical-conditioned"],
                            prior_live=0.9, cost_units=1)
        self.assertFalse(apply_gates(cand, "exploration").admissible)
        self.assertEqual(rank([cand]), [])


class TestGates(unittest.TestCase):
    def test_well_formed_candidate_is_admissible_at_exploration(self):
        self.assertTrue(apply_gates(_well_formed(), "exploration").admissible)

    def test_exploration_does_not_require_a_mechanism(self):
        """The deadlock-breaking property, asserted so it cannot regress.

        Requiring a mechanism at the exploration tier is what made the project
        unable to run the toy experiments that would produce a mechanism.
        """
        cand = _well_formed()
        self.assertNotIn("mechanism", cand)
        self.assertTrue(apply_gates(cand, "exploration").admissible)

    def test_promotion_requires_a_mechanism(self):
        res = apply_gates(_well_formed(), "promotion")
        self.assertFalse(res.admissible)
        self.assertTrue(any("mechanism" in f for f in res.failures))

    def test_promotion_rejects_two_sizes_of_scaling_evidence(self):
        cand = _well_formed(
            mechanism="stated", cost_model="full", no_hidden_precomputation=True,
            independent_reproduction="validator B", scaling_evidence=[8, 16])
        res = apply_gates(cand, "promotion")
        self.assertFalse(res.admissible)
        self.assertTrue(any("three or more" in f for f in res.failures))

    def test_promotion_accepts_three_sizes(self):
        cand = _well_formed(
            mechanism="stated", cost_model="full", no_hidden_precomputation=True,
            independent_reproduction="validator B", scaling_evidence=[8, 16, 32])
        self.assertTrue(apply_gates(cand, "promotion").admissible)

    def test_each_missing_field_blocks_exploration(self):
        for field in ("prediction", "baseline", "budget", "stop_condition", "scale"):
            cand = _well_formed()
            del cand[field]
            self.assertFalse(apply_gates(cand, "exploration").admissible,
                             f"{field} should be required")

    def test_unknown_tier_raises(self):
        with self.assertRaises(ValueError):
            apply_gates(_well_formed(), "whatever")


class TestValidation(unittest.TestCase):
    def test_likelihoods_must_normalise(self):
        cand = _well_formed(likelihoods={
            "supported": {"live": 0.7, "dead": 0.05},
            "bounded_negative": {"live": 0.9, "dead": 0.95},
        })
        self.assertTrue(any("sums to" in e for e in validate_prereg(cand)))

    def test_prior_must_be_strictly_inside_the_unit_interval(self):
        self.assertTrue(validate_prereg(_well_formed(prior_live=0.0)))
        self.assertTrue(validate_prereg(_well_formed(prior_live=1.0)))
        self.assertFalse(validate_prereg(_well_formed(prior_live=0.5)))

    def test_outcome_must_be_in_the_taxonomy(self):
        cand = _well_formed(likelihoods={
            "kind_of_worked": {"live": 1.0, "dead": 1.0},
        })
        self.assertTrue(any("taxonomy" in e for e in validate_prereg(cand)))

    def test_negative_without_reopening_conditions_is_rejected(self):
        """A negative result that cannot be reopened is not reusable knowledge."""
        cand = _well_formed(resolution="bounded_negative")
        self.assertTrue(any("reopening_conditions" in e for e in validate_prereg(cand)))
        cand["reopening_conditions"] = ["a nonredundant formulation"]
        self.assertFalse(validate_prereg(cand))

    def test_supported_is_in_the_taxonomy(self):
        """A positive toy outcome needs somewhere to go, or the layer is biased.

        Without this state an experiment that succeeds has no admissible
        resolution, which would quietly make every pre-registration a bet on
        failure.
        """
        self.assertIn("supported", RESOLUTIONS)

    def test_inapplicable_and_resource_exhausted_are_distinct_from_negative(self):
        for state in ("inapplicable", "resource_exhausted", "inconclusive"):
            self.assertIn(state, RESOLUTIONS)
            self.assertNotIn("evidence against", RESOLUTIONS[state].lower())


class TestRanking(unittest.TestCase):
    def test_cheaper_wins_when_information_is_equal(self):
        a = _well_formed(id="A", cost_units=1)
        b = _well_formed(id="B", cost_units=4)
        order = [r.candidate_id for r in rank([b, a])]
        self.assertEqual(order, ["A", "B"])

    def test_more_informative_wins_when_cost_is_equal(self):
        sharp = _well_formed(id="SHARP", likelihoods={
            "supported": {"live": 0.95, "dead": 0.02},
            "bounded_negative": {"live": 0.05, "dead": 0.98},
        })
        blunt = _well_formed(id="BLUNT", likelihoods={
            "supported": {"live": 0.5, "dead": 0.45},
            "bounded_negative": {"live": 0.5, "dead": 0.55},
        })
        order = [r.candidate_id for r in rank([blunt, sharp])]
        self.assertEqual(order, ["SHARP", "BLUNT"])

    def test_malformed_candidates_are_excluded_not_ranked_low(self):
        bad = _well_formed(id="BAD", prior_live=1.0)
        self.assertEqual([r.candidate_id for r in rank([bad])], [])

    def test_ranking_is_deterministic_under_ties(self):
        a = _well_formed(id="Z-TIE")
        b = _well_formed(id="A-TIE")
        self.assertEqual([r.candidate_id for r in rank([a, b])], ["A-TIE", "Z-TIE"])


class TestBrier(unittest.TestCase):
    def test_confident_and_wrong_costs_more_than_uncertain(self):
        confident_wrong = brier_score({"supported": 0.9, "bounded_negative": 0.1},
                                      "bounded_negative")
        uncertain = brier_score({"supported": 0.5, "bounded_negative": 0.5},
                                "bounded_negative")
        self.assertGreater(confident_wrong, uncertain)

    def test_perfect_prediction_scores_zero(self):
        self.assertAlmostEqual(
            brier_score({"supported": 1.0, "bounded_negative": 0.0}, "supported"), 0.0)


class TestRetrospective(unittest.TestCase):
    """The retrospective checks must pass against the repo's real substrate."""

    def test_threat_model_reproduction_passes(self):
        res = retro.check_threat_model_reproduction()
        self.assertTrue(res["passed"], res)
        self.assertEqual(res["missed"], [], "a different-threat-model route slipped through")

    def test_primary_anchor_matches_substrate(self):
        """R1a: the constant must equal the substrate's own primary declaration."""
        self.assertTrue(retro.check_primary_anchor()["passed"],
                        retro.check_primary_anchor())

    def test_primary_threat_model_routes_are_never_shelved(self):
        """Caught by fault injection: shelving *more* is not automatically safe.

        An earlier version passed R1 whenever no labelled-separate route slipped
        through, so corrupting PRIMARY_THREAT_MODEL shelved 15 of 17 routes and the
        gate still reported OK.
        """
        res = retro.check_threat_model_reproduction()
        self.assertEqual(res["wrongly_shelved"], [], res)

    def test_non_degeneracy_passes(self):
        self.assertTrue(retro.check_non_degeneracy()["passed"])

    def test_preregistrations_are_wellformed(self):
        res = retro.check_prereg_wellformed()
        self.assertTrue(res["passed"], res["problems"])

    def test_run_all_passes(self):
        self.assertTrue(retro.run_all()["passed"])

    def test_historical_records_are_not_used_for_calibration(self):
        """Records written before pre-registration must never be scored.

        Scoring them would mean inventing a prior after seeing the outcome, which
        is the exact failure this layer exists to prevent.
        """
        res = retro.check_calibration()
        self.assertGreater(res["resolved_but_not_preregistered"], 0)
        self.assertEqual(res["scored"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
