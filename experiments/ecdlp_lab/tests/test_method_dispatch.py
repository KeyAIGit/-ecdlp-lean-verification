from __future__ import annotations

import copy
import json
import unittest
from dataclasses import replace
from pathlib import Path

from experiments.ecdlp_lab.core.catalog_registry import resolve_curve_fixture
from experiments.ecdlp_lab.core.legacy_solver_replay import (
    load_legacy_replay,
    validate_legacy_replay,
)
from experiments.ecdlp_lab.methods.python.dispatch import (
    dispatch_method_request,
    run_method,
    sanitize_method_request,
)
from experiments.ecdlp_lab.methods.python.model import MethodBudgets, PublicMethodInput
from experiments.ml_structure_probe.p1_toy_scaling.curve_math import Curve

ROOT = Path(__file__).resolve().parents[3]


class SpyCurve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.inner = Curve(p, a, b)
        self.p, self.a, self.b = p, a, b
        self.add_calls = 0

    def is_on_curve(self, point):
        return self.inner.is_on_curve(point)

    def add(self, left, right):
        self.add_calls += 1
        return self.inner.add(left, right)

    def negate(self, point):
        return self.inner.negate(point)


class MethodDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(
            (
                ROOT
                / "experiments/ecdlp_lab/fixtures/contracts/valid/method_request_v1.json"
            ).read_text()
        )
        cls.fixture = resolve_curve_fixture(
            cls.record["curve_catalog_sha256"], cls.record["curve_fixture_id"]
        )

    def test_valid_request_projects_and_dispatches(self) -> None:
        sanitized = sanitize_method_request(
            self.record, resolved_fixture=self.fixture
        )
        self.assertTrue(sanitized.passed)
        self.assertIsInstance(sanitized.public_input, PublicMethodInput)
        outcome = run_method(sanitized.public_input)
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.candidate_scalar, 1)
        self.assertEqual(outcome.counters.legacy_p1_group_operations, 88)

    def test_fixture_or_curve_drift_is_rejected(self) -> None:
        for mutation in (
            ("curve_fixture_id", "not-a-fixture"),
            ("subgroup_order", self.record["subgroup_order"] + 2),
            ("generator", [0, 0]),
            ("target", [0, 0]),
        ):
            changed = copy.deepcopy(self.record)
            changed[mutation[0]] = mutation[1]
            result = sanitize_method_request(changed, resolved_fixture=self.fixture)
            self.assertFalse(result.passed)
            self.assertEqual(result.failure.code, "invalid_public_input")

    def test_unknown_method_and_bool_seed_are_rejected(self) -> None:
        for field, value in (("method_id", "rho_v1"), ("algorithm_seed", True)):
            changed = copy.deepcopy(self.record)
            changed[field] = value
            self.assertFalse(
                sanitize_method_request(
                    changed, resolved_fixture=self.fixture
                ).passed
            )

    def test_backend_curve_mismatch_is_rejected(self) -> None:
        public = sanitize_method_request(
            self.record, resolved_fixture=self.fixture
        ).public_input
        outcome = run_method(public, backend=Curve(6709, 0, 7))
        self.assertEqual(outcome.status, "invalid_request")
        self.assertEqual(outcome.failure.code, "invalid_public_input")

    def test_projection_has_no_metadata_or_precomputation_channels(self) -> None:
        public = sanitize_method_request(
            self.record, resolved_fixture=self.fixture
        ).public_input
        for name, value in (
            ("request_id", "0" * 64),
            ("curve_catalog_sha256", "0" * 64),
            ("public_scalar_interval", {"expected_scalar": 1}),
            ("public_precomputation", {"derivation_seed": 1}),
        ):
            with self.assertRaises(TypeError):
                replace(public, **{name: value})

    def test_dispatch_has_no_external_bsgs_table_channel(self) -> None:
        public = sanitize_method_request(
            self.record, resolved_fixture=self.fixture
        ).public_input
        with self.assertRaises(TypeError):
            run_method(public, bsgs_setup=object())

    def test_public_failure_text_is_fixed_and_does_not_echo_input(self) -> None:
        changed = copy.deepcopy(self.record)
        changed["expected_scalar"] = "DO-NOT-ECHO"
        outcome = dispatch_method_request(changed, resolved_fixture=self.fixture)
        self.assertEqual(outcome.failure.detail, "public method input rejected")
        self.assertNotIn("DO-NOT-ECHO", outcome.failure.detail)

    def test_cooperative_cancellation_is_a_bounded_public_failure(self) -> None:
        public = sanitize_method_request(
            self.record, resolved_fixture=self.fixture
        ).public_input
        outcome = run_method(public, cancelled=lambda: True)
        self.assertEqual(outcome.status, "bounded_failure")
        self.assertEqual(outcome.failure.code, "process_timeout")

    def test_selected_backend_never_performs_uncounted_membership_multiplication(self) -> None:
        public = sanitize_method_request(
            self.record, resolved_fixture=self.fixture
        ).public_input
        limited = replace(
            public,
            method_id="ordinary_rho_xmod3_v1",
            budgets=replace(public.budgets, max_group_law_invocations=1),
        )
        backend = SpyCurve(limited.p, limited.a, limited.b)
        outcome = run_method(limited, backend=backend)
        self.assertEqual(outcome.failure.code, "group_operation_budget_exhausted")
        self.assertEqual(backend.add_calls, 1)

    def test_all_64_authenticated_legacy_rows_match_exactly(self) -> None:
        generous = MethodBudgets(
            max_subgroup_order_bits=32,
            max_field_bits=32,
            max_group_law_invocations=10_000_000,
            max_table_entries=100_000,
            max_steps=10_000_000,
            timeout_ns=1,
            max_memory_bytes=100_000_000,
            workers=1,
        )
        observed = {
            "success": 0,
            "bsgs_legacy": 0,
            "bsgs_offline": 0,
            "bsgs_online": 0,
            "bsgs_entries": 0,
            "bsgs_bytes": 0,
            "rho_legacy": 0,
            "rho_steps": 0,
            "rho_restarts": 0,
            "rho_collisions": 0,
            "rho_noninvertible": 0,
            "rho_invalid": 0,
        }
        for case in load_legacy_replay():
            public = case.to_public_input()
            method_input = PublicMethodInput(
                method_id=public.method_id,
                algorithm_seed=public.seed,
                p=public.p,
                a=public.a,
                b=public.b,
                G=public.G,
                Q=public.Q,
                ell=public.ell,
                budgets=generous,
            )
            outcome = run_method(method_input)
            expected = case.validator_only
            self.assertEqual(outcome.candidate_scalar, expected.expected_scalar)
            self.assertEqual(
                outcome.counters.legacy_p1_group_operations,
                expected.legacy_group_operations,
            )
            observed["success"] += outcome.success
            if public.method_id == "bsgs_v1":
                observed["bsgs_legacy"] += outcome.counters.legacy_p1_group_operations
                observed["bsgs_offline"] += (
                    outcome.counters.offline_setup.group_law_invocations
                )
                observed["bsgs_online"] += (
                    outcome.counters.online_target.group_law_invocations
                )
                observed["bsgs_entries"] += outcome.counters.table_entries
                observed["bsgs_bytes"] += (
                    outcome.counters.estimated_algorithmic_table_bytes
                )
            else:
                observed["rho_legacy"] += outcome.counters.legacy_p1_group_operations
                observed["rho_steps"] += outcome.diagnostics.floyd_iterations
                observed["rho_restarts"] += outcome.counters.restarts
                observed["rho_collisions"] += outcome.counters.collisions
                observed["rho_noninvertible"] += (
                    outcome.counters.noninvertible_collisions
                )
                observed["rho_invalid"] += (
                    outcome.diagnostics.invalid_candidate_collisions
                )
        golden = validate_legacy_replay()
        self.assertEqual(observed["success"], 64)
        self.assertEqual(observed["bsgs_legacy"], golden.bsgs_legacy_group_operations)
        self.assertEqual(
            observed["bsgs_offline"],
            golden.bsgs_offline_setup_group_law_invocations,
        )
        self.assertEqual(
            observed["bsgs_online"], golden.bsgs_online_target_group_law_invocations
        )
        self.assertEqual(observed["bsgs_entries"], golden.bsgs_table_entries)
        self.assertEqual(
            observed["bsgs_bytes"], golden.bsgs_estimated_algorithmic_table_bytes
        )
        self.assertEqual(observed["rho_legacy"], golden.rho_legacy_group_operations)
        self.assertEqual(observed["rho_steps"], golden.expected_rho_floyd_iterations)
        self.assertEqual(observed["rho_restarts"], golden.expected_rho_restarts)
        self.assertEqual(observed["rho_collisions"], golden.expected_rho_collisions)
        self.assertEqual(
            observed["rho_noninvertible"], golden.expected_rho_noninvertible_collisions
        )
        self.assertEqual(
            observed["rho_invalid"], golden.expected_rho_invalid_candidate_collisions
        )


if __name__ == "__main__":
    unittest.main()
