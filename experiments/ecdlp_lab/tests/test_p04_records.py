from __future__ import annotations

from copy import deepcopy
import shutil
import tempfile
import unittest
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import sha256_json
from experiments.ecdlp_lab.core.catalog_registry import trusted_catalog_sha256s
from experiments.ecdlp_lab.core.contracts import (
    ValidationContext,
    validate_contract,
    validate_cross_record_bundle,
)
from experiments.ecdlp_lab.core.target_registry import load_target_pair
from experiments.ecdlp_lab.orchestration.method_worker import (
    execute_request as execute_method,
    make_method_worker_request,
)
from experiments.ecdlp_lab.orchestration.model import OrchestrationError
from experiments.ecdlp_lab.orchestration.provenance import (
    DEVELOPMENT_DIFF_KIND,
    P04_BASE_SOURCE_COMMIT,
    build_campaign_provenance,
    build_dependency_manifest,
    build_provenance,
    development_diff_sha256,
    method_execution_manifest,
    method_implementation_manifest,
    source_snapshot_manifest,
    validator_execution_manifest,
    validator_implementation_manifest,
)
from experiments.ecdlp_lab.orchestration.records import (
    build_method_request,
    build_method_result,
    build_validation_receipt,
    derive_attempt_id,
    derive_request_id,
    derive_result_id,
    derive_validation_id,
    expand_campaign,
    load_smoke_campaign,
    retry_work_unit,
)
from experiments.ecdlp_lab.orchestration.validator_worker import (
    execute_request as execute_validator,
    make_validator_request,
)
from experiments.ecdlp_lab.methods.python.model import SolverOutcome


REPO_ROOT = Path(__file__).resolve().parents[3]
PRIVATE_KEYS = {
    "expected_scalar",
    "target_derivation_seed",
    "private_payload",
    "generation_receipt_sha256",
}
INITIALIZER_EXPECTATIONS = {
    "experiments/ecdlp_lab/__init__.py": {
        "bsgs",
        "method_execution",
        "rho",
        "validator",
        "validator_execution",
        "snapshot",
    },
    "experiments/ecdlp_lab/core/__init__.py": {
        "bsgs",
        "method_execution",
        "rho",
        "validator",
        "validator_execution",
        "snapshot",
    },
    "experiments/ecdlp_lab/orchestration/__init__.py": {
        "bsgs",
        "method_execution",
        "rho",
        "validator",
        "validator_execution",
        "snapshot",
    },
    "experiments/ecdlp_lab/curves/__init__.py": {
        "bsgs",
        "method_execution",
        "rho",
        "snapshot",
    },
    "experiments/ecdlp_lab/methods/python/__init__.py": {
        "bsgs",
        "method_execution",
        "rho",
        "snapshot",
    },
    "experiments/framework/__init__.py": {
        "validator",
        "validator_execution",
        "snapshot",
    },
    "experiments/ml_structure_probe/p1_toy_scaling/__init__.py": {
        "bsgs",
        "method_execution",
        "rho",
        "snapshot",
    },
}


def walked_keys(value: object) -> set[str]:
    result: set[str] = set()
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            result.update(current)
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return result


def manifest_digests(repo_root: Path) -> dict[str, str]:
    return {
        "bsgs": method_implementation_manifest(
            "bsgs_v1", repo_root=repo_root
        ).sha256,
        "rho": method_implementation_manifest(
            "ordinary_rho_xmod3_v1", repo_root=repo_root
        ).sha256,
        "validator": validator_implementation_manifest(
            repo_root=repo_root
        ).sha256,
        "method_execution": method_execution_manifest(repo_root=repo_root).sha256,
        "validator_execution": validator_execution_manifest(
            repo_root=repo_root
        ).sha256,
        "snapshot": source_snapshot_manifest(repo_root=repo_root).sha256,
    }


class P04RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pair = load_target_pair(repo_root=REPO_ROOT)
        campaign = load_smoke_campaign(repo_root=REPO_ROOT)
        campaign["provenance"] = build_campaign_provenance(
            config_sha256=campaign["campaign_id"],
            source_commit=P04_BASE_SOURCE_COMMIT,
            source_tree_clean=False,
            diff_sha256=None,
            method_ids=campaign["matrix"]["method_ids"],
            repo_root=REPO_ROOT,
        )
        cls.plan = expand_campaign(
            campaign,
            target_pair=cls.pair,
            repo_root=REPO_ROOT,
        )

    def test_requests_results_and_final_receipts_are_canonical_and_coherent(self) -> None:
        requests: list[dict[str, object]] = []
        results: list[dict[str, object]] = []
        receipts: list[dict[str, object]] = []
        for work in self.plan.work_units:
            request = build_method_request(work, self.pair, repo_root=REPO_ROOT)
            self.assertFalse(PRIVATE_KEYS & walked_keys(request))
            self.assertEqual(
                request["request_id"],
                derive_request_id(work["work_unit_id"], work["attempt_id"]),
            )
            outcome = execute_method(make_method_worker_request(request))
            self.assertEqual((outcome.status, outcome.candidate_scalar), ("success", 1))
            result = build_method_result(work, request, outcome, repo_root=REPO_ROOT)
            request_hash = sha256_json(request)
            self.assertEqual(result["method_request_sha256"], request_hash)
            self.assertEqual(
                result["result_id"],
                derive_result_id(work["work_unit_id"], work["attempt_id"], request_hash),
            )
            validator_request = make_validator_request(request, result["candidate_scalar"])
            validator_output = execute_validator(validator_request)
            receipt = build_validation_receipt(
                work,
                request,
                result,
                validator_request,
                validator_output,
                self.pair,
                repo_root=REPO_ROOT,
            )
            self.assertTrue(receipt["passed"])
            self.assertFalse(receipt["retainable"])
            self.assertEqual(receipt["retention_decision"], "development_only")
            self.assertFalse(PRIVATE_KEYS & walked_keys(receipt))
            self.assertEqual(
                receipt["validation_id"],
                derive_validation_id(
                    receipt["subject_sha256"],
                    receipt["validator_request_sha256"],
                    receipt["validator_output_sha256"],
                ),
            )
            requests.append(request)
            results.append(result)
            receipts.append(receipt)

        context = ValidationContext.from_records(
            (self.pair.public_record, self.pair.private_record),
            repo_root=REPO_ROOT,
            known_catalog_sha256s=trusted_catalog_sha256s(repo_root=REPO_ROOT),
            known_target_vector_sha256s=(self.pair.public_target_vector_sha256,),
            verify_artifacts=False,
        )
        bundle = [
            self.plan.campaign,
            self.pair.public_record,
            self.pair.private_record,
            *self.plan.work_units,
            *requests,
            *results,
            *receipts,
        ]
        self.assertEqual(validate_cross_record_bundle(bundle, context), [])
        for record in (*requests, *results, *receipts):
            self.assertEqual(validate_contract(record, context), [])

    def test_retry_changes_only_attempt_identity_and_request_identity(self) -> None:
        original = self.plan.work_units[0]
        retried = retry_work_unit(original, 1)
        self.assertEqual(retried["work_unit_id"], original["work_unit_id"])
        self.assertEqual(retried["identity"], original["identity"])
        self.assertEqual(retried["retry_ordinal"], 1)
        self.assertEqual(
            retried["attempt_id"], derive_attempt_id(original["work_unit_id"], 1)
        )
        self.assertNotEqual(retried["attempt_id"], original["attempt_id"])
        first = build_method_request(original, self.pair, repo_root=REPO_ROOT)
        retry = build_method_request(retried, self.pair, repo_root=REPO_ROOT)
        self.assertNotEqual(first["request_id"], retry["request_id"])

    def test_receipt_rejects_malformed_validator_protocol_before_finalization(self) -> None:
        work = self.plan.work_units[0]
        request = build_method_request(work, self.pair, repo_root=REPO_ROOT)
        result = build_method_result(
            work,
            request,
            execute_method(make_method_worker_request(request)),
            repo_root=REPO_ROOT,
        )
        validator_request = make_validator_request(request, result["candidate_scalar"])
        validator_output = execute_validator(validator_request)
        poisoned = deepcopy(validator_output)
        poisoned["validator_counters"]["total_group_law_invocations"] += 1
        with self.assertRaisesRegex(OrchestrationError, "counter totals"):
            build_validation_receipt(
                work,
                request,
                result,
                validator_request,
                poisoned,
                self.pair,
                repo_root=REPO_ROOT,
            )

    def test_bounded_failure_is_validated_without_becoming_validator_disagreement(self) -> None:
        work = self.plan.work_units[0]
        request = build_method_request(work, self.pair, repo_root=REPO_ROOT)
        result = build_method_result(
            work,
            request,
            SolverOutcome.failed("step_budget_exhausted"),
            repo_root=REPO_ROOT,
        )
        validator_request = make_validator_request(request, result)
        validator_output = execute_validator(validator_request)
        self.assertTrue(validator_output["passed"])
        self.assertTrue(validator_output["public_input_valid"])
        self.assertTrue(validator_output["status_binding_valid"])
        self.assertTrue(validator_output["counters_binding_valid"])
        self.assertEqual(
            validator_output["validator_counters"]["candidate_relation_check"], 0
        )
        receipt = build_validation_receipt(
            work,
            request,
            result,
            validator_request,
            validator_output,
            self.pair,
            repo_root=REPO_ROOT,
        )
        self.assertTrue(receipt["passed"])
        self.assertEqual(receipt["subject_status"], "bounded_failure")
        self.assertIsNone(receipt["candidate_scalar"])
        self.assertIsNone(receipt["candidate_relation_valid"])
        self.assertEqual(
            {check["check_id"] for check in receipt["checks"]},
            {
                "subject_status_binding_v1",
                "public_input_validation_v1",
                "counters_binding_v1",
                "private_target_binding_v1",
                "provenance_binding_v1",
            },
        )

        poisoned = deepcopy(validator_output)
        poisoned["method_counters_sha256"] = "0" * 64
        with self.assertRaisesRegex(OrchestrationError, "non-success validator"):
            build_validation_receipt(
                work,
                request,
                result,
                validator_request,
                poisoned,
                self.pair,
                repo_root=REPO_ROOT,
            )

    def test_dependency_manifests_are_complete_sorted_content_identities(self) -> None:
        method = method_implementation_manifest("bsgs_v1", repo_root=REPO_ROOT)
        rho = method_implementation_manifest(
            "ordinary_rho_xmod3_v1", repo_root=REPO_ROOT
        )
        validator = validator_implementation_manifest(repo_root=REPO_ROOT)
        snapshot = source_snapshot_manifest(repo_root=REPO_ROOT)
        self.assertEqual(
            [entry.path for entry in method.entries],
            sorted(entry.path for entry in method.entries),
        )
        self.assertNotEqual(method.sha256, validator.sha256)
        self.assertEqual(method.sha256, rho.sha256)
        self.assertEqual(
            method.sha256,
            method_execution_manifest(repo_root=REPO_ROOT).sha256,
        )
        self.assertEqual(
            validator.sha256,
            validator_execution_manifest(repo_root=REPO_ROOT).sha256,
        )
        method_execution_paths = {
            entry.path
            for entry in method_execution_manifest(repo_root=REPO_ROOT).entries
        }
        validator_execution_paths = {
            entry.path
            for entry in validator_execution_manifest(repo_root=REPO_ROOT).entries
        }
        self.assertTrue(
            {
                "experiments/ecdlp_lab/methods/python/bsgs.py",
                "experiments/ecdlp_lab/methods/python/rho.py",
                "experiments/ecdlp_lab/core/contracts.py",
                "experiments/ecdlp_lab/core/schema.py",
            }.issubset(method_execution_paths)
        )
        self.assertTrue(
            {
                "experiments/ecdlp_lab/core/contracts.py",
                "experiments/ecdlp_lab/core/paths.py",
                "experiments/ecdlp_lab/core/safety.py",
                "experiments/ecdlp_lab/core/schema.py",
            }.issubset(validator_execution_paths)
        )
        projection = {
            "manifest_kind": "ecdlp_lab_dependency_manifest_v1",
            "entries": [entry.as_dict() for entry in method.entries],
        }
        self.assertEqual(method.sha256, sha256_json(projection))
        self.assertIn(
            "experiments/ecdlp_lab/orchestration/records.py",
            {entry.path for entry in snapshot.entries},
        )
        with self.assertRaises(OrchestrationError):
            build_dependency_manifest(("../outside.py",), repo_root=REPO_ROOT)

    def test_every_executed_package_initializer_changes_its_manifests(self) -> None:
        manifests = (
            method_implementation_manifest("bsgs_v1", repo_root=REPO_ROOT),
            method_implementation_manifest(
                "ordinary_rho_xmod3_v1", repo_root=REPO_ROOT
            ),
            validator_implementation_manifest(repo_root=REPO_ROOT),
            method_execution_manifest(repo_root=REPO_ROOT),
            validator_execution_manifest(repo_root=REPO_ROOT),
            source_snapshot_manifest(repo_root=REPO_ROOT),
        )
        relative_paths = sorted(
            {entry.path for manifest in manifests for entry in manifest.entries}
        )
        with tempfile.TemporaryDirectory() as directory:
            mirror = Path(directory)
            for relative_path in relative_paths:
                source = REPO_ROOT.joinpath(*relative_path.split("/"))
                destination = mirror.joinpath(*relative_path.split("/"))
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            baseline = manifest_digests(mirror)
            for relative_path, expected_changes in INITIALIZER_EXPECTATIONS.items():
                with self.subTest(relative_path=relative_path):
                    target = mirror.joinpath(*relative_path.split("/"))
                    original = target.read_bytes()
                    target.write_bytes(original + b"\n")
                    mutated = manifest_digests(mirror)
                    target.write_bytes(original)
                    for manifest_name in baseline:
                        self.assertEqual(
                            mutated[manifest_name] != baseline[manifest_name],
                            manifest_name in expected_changes,
                            (relative_path, manifest_name),
                        )

    def test_provenance_builder_enforces_clean_dirty_and_independence_rules(self) -> None:
        method = method_implementation_manifest("bsgs_v1", repo_root=REPO_ROOT)
        validator = validator_implementation_manifest(repo_root=REPO_ROOT)
        snapshot = source_snapshot_manifest(repo_root=REPO_ROOT)
        provenance = build_provenance(
            config_sha256=self.plan.campaign["campaign_id"],
            source_commit="0" * 40,
            source_tree_clean=True,
            diff_sha256=None,
            producer_dependency_sha256s=(method.sha256,),
            validator_dependency_sha256s=(validator.sha256,),
            source_snapshot_sha256=snapshot.sha256,
        )
        self.assertTrue(provenance["source_tree_clean"])
        campaign_provenance = build_campaign_provenance(
            config_sha256=self.plan.campaign["campaign_id"],
            source_commit=P04_BASE_SOURCE_COMMIT,
            source_tree_clean=True,
            diff_sha256=None,
            method_ids=self.plan.campaign["matrix"]["method_ids"],
            repo_root=REPO_ROOT,
        )
        self.assertFalse(campaign_provenance["source_tree_clean"])
        self.assertEqual(campaign_provenance["source_commit"], P04_BASE_SOURCE_COMMIT)
        self.assertEqual(
            campaign_provenance["diff_sha256"],
            development_diff_sha256(
                campaign_provenance["source_snapshot_sha256"]
            ),
        )
        self.assertEqual(
            campaign_provenance["diff_sha256"],
            sha256_json(
                {
                    "base_source_commit": P04_BASE_SOURCE_COMMIT,
                    "diff_kind": DEVELOPMENT_DIFF_KIND,
                    "source_snapshot_sha256": campaign_provenance[
                        "source_snapshot_sha256"
                    ],
                }
            ),
        )
        with self.assertRaises(OrchestrationError):
            build_provenance(
                config_sha256=self.plan.campaign["campaign_id"],
                source_commit="0" * 40,
                source_tree_clean=False,
                diff_sha256=None,
                producer_dependency_sha256s=(method.sha256,),
                validator_dependency_sha256s=(validator.sha256,),
                source_snapshot_sha256=snapshot.sha256,
            )
        with self.assertRaises(OrchestrationError):
            build_campaign_provenance(
                config_sha256=self.plan.campaign["campaign_id"],
                source_commit="0" * 40,
                source_tree_clean=False,
                diff_sha256="1" * 64,
                method_ids=self.plan.campaign["matrix"]["method_ids"],
                repo_root=REPO_ROOT,
            )


if __name__ == "__main__":
    unittest.main()
