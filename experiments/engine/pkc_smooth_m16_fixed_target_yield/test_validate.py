#!/usr/bin/env python3
"""Independent readiness and semantic-fault tests for the M16 validator."""

from __future__ import annotations

import copy
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
VALIDATOR_PATH = HERE / "validate.py"
SPEC = importlib.util.spec_from_file_location("m16_fixed_target_validator", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load validator")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def load_producer():
    path = HERE / "run.py"
    spec = importlib.util.spec_from_file_location(
        "m16_fixed_target_producer_test", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    resource_missing = importlib.util.find_spec("resource") is None
    if resource_missing:
        sys.modules["resource"] = mock.Mock(name="posix_resource_import_stub")
    try:
        spec.loader.exec_module(module)
    finally:
        if resource_missing:
            sys.modules.pop("resource", None)
    return module


ZERO_OPERATIONS = {
    "curve_additions": 0,
    "curve_doublings": 0,
    "identity_shortcuts": 0,
    "field_inversions": 0,
    "scalar_multiplication_bits": 0,
}


def build_cell_fixture(attempts: int = 500) -> dict:
    curve = copy.deepcopy(validator.EXPECTED_CURVES[0])
    arm = "PLAIN_MATCHED"
    # Deliberately outside the five preregistered experiment seeds.  Unit
    # tests must never consume a future authorized primary stream.
    seed = 9001
    peer_seed = 9002
    points, build_counts = validator.reconstruct_factor_base(
        curve=curve,
        arm=arm,
        seed=seed,
        prefix=validator.PRNG_PREFIX,
        size=384,
    )
    current_cell = f"{curve['curve_id']}--{arm}--S{seed}"
    peer_cell = f"{curve['curve_id']}--{arm}--S{peer_seed}"
    commitment = validator.base_commitment(
        curve["curve_id"], arm, seed, points
    )
    target = validator.reconstruct_target_point(
        curve=curve, seed=seed, prefix=validator.PRNG_PREFIX
    )
    peer_target = validator.reconstruct_target_point(
        curve=curve, seed=peer_seed, prefix=validator.PRNG_PREFIX
    )
    target_entry = {
        "cell_id": current_cell,
        "curve_id": curve["curve_id"],
        "arm": arm,
        "seed": seed,
        "base_commitment": commitment,
        "point": validator.point_json(target),
        "statement": "target-frozen-before-leaf-stream-v1",
        "shuffled_target_cell_id": peer_cell,
        "frozen_sequence": 2,
    }
    target_entry["commitment"] = validator.target_commitment(target_entry)
    peer_entry = {
        "cell_id": peer_cell,
        "curve_id": curve["curve_id"],
        "arm": arm,
        "seed": peer_seed,
        "base_commitment": "unused-in-cell-fixture",
        "point": validator.point_json(peer_target),
        "statement": "target-frozen-before-leaf-stream-v1",
        "commitment": "unused-in-cell-fixture",
        "shuffled_target_cell_id": "",
        "frozen_sequence": 2,
    }
    base_entry = {
        "cell_id": current_cell,
        "curve_id": curve["curve_id"],
        "arm": arm,
        "seed": seed,
        "ordered_base_sha256": commitment,
        "frozen_sequence": 1,
    }
    selection = {
        key: value
        for key, value in build_counts.items()
        if key not in {
            "prng_words",
            "prng_rejected_blocks",
            "operation_counts",
        }
    }
    base_event = {
        "event": "base",
        "cell_id": current_cell,
        "curve_id": curve["curve_id"],
        "arm": arm,
        "seed": seed,
        "points": [validator.point_json(point) for point in points],
        "commitment": commitment,
        "selection_counts": selection,
        "prng_blocks": build_counts["prng_words"],
        "prng_rejected_blocks": build_counts["prng_rejected_blocks"],
        "operation_counts": copy.deepcopy(build_counts["operation_counts"]),
        "frozen_sequence": 1,
    }
    target_event = {
        "event": "target",
        **target_entry,
        "target_base_x_collision": target[0] in {
            point[0] for point in points
        },
    }
    leaf = validator.CounterPrng(
        validator.PRNG_PREFIX,
        validator.prng_domain(curve["curve_id"], arm, seed, "leaves"),
    )
    random_labels = validator.CounterPrng(
        validator.PRNG_PREFIX,
        validator.prng_domain(curve["curve_id"], arm, seed, "random-label"),
    )
    x_to_index = {point[0]: index for index, point in enumerate(points)}
    accepted: dict[int, dict] = {}
    shuffled: dict[int, dict] = {}
    counts = {
        "attempts": 0,
        "accepted": 0,
        "affine_regular": 0,
        "balanced_regular": 0,
        "residual_identity": 0,
        "residual_not_in_base": 0,
        "shuffled_accepted": 0,
        "shuffled_affine_regular": 0,
        "random_label_true": 0,
        "repeated_index_total": 0,
        "repeated_coordinate_total": 0,
        "target_coordinate_collision_total": 0,
    }
    endpoint_failures = {"base": 0, "final": 0}
    prefix_failures = [0] * 6
    suffix_failures = [0] * 6
    for trial in range(attempts):
        indices15, signs15, residual = validator.replay_leaf_trial(
            leaf, points, target, curve["p"]
        )
        counts["attempts"] += 1
        if residual is None:
            counts["residual_identity"] += 1
        elif residual[0] not in x_to_index:
            counts["residual_not_in_base"] += 1
        else:
            final_index = x_to_index[residual[0]]
            final_sign = 1 if residual == points[final_index] else -1
            indices = indices15 + [final_index]
            signs = signs15 + [final_sign]
            coordinates = [points[index] for index in indices]
            labels = validator.regularity_labels(coordinates, target, curve["p"])
            controls = []
            for control_index in range(16):
                order = validator.deterministic_permutation(
                    curve_id=curve["curve_id"],
                    arm=arm,
                    seed=seed,
                    trial_index=trial,
                    permutation_index=control_index,
                    prefix=validator.PRNG_PREFIX,
                )
                controls.append(
                    {
                        "control_index": control_index,
                        "permutation": order,
                        "labels": validator.regularity_labels(
                            [coordinates[index] for index in order],
                            target,
                            curve["p"],
                        ),
                    }
                )
            random_label = random_labels.randbelow(2) == 1
            repeated_index = 16 - len(set(indices))
            repeated_coordinate = 16 - len(
                {points[index][0] for index in indices}
            )
            target_collision = sum(
                points[index][0] == target[0] for index in indices
            )
            accepted[trial] = {
                "event": "accepted",
                "cell_id": current_cell,
                "trial_index": trial,
                "indices": indices,
                "signs": signs,
                "points": [
                    validator.point_json(point) for point in coordinates
                ],
                "target": validator.point_json(target),
                "labels": labels,
                "permutations": controls,
                "random_label": random_label,
                "repeated_index_count": repeated_index,
                "repeated_coordinate_count": repeated_coordinate,
                "target_coordinate_collision_count": target_collision,
                "operation_counts": dict(ZERO_OPERATIONS),
            }
            counts["accepted"] += 1
            counts["affine_regular"] += int(labels["affine_regular"])
            counts["balanced_regular"] += int(labels["balanced_regular"])
            counts["random_label_true"] += int(random_label)
            counts["repeated_index_total"] += repeated_index
            counts["repeated_coordinate_total"] += repeated_coordinate
            counts["target_coordinate_collision_total"] += target_collision
            endpoint_failures["base"] += int(
                not labels["base_endpoint_nonzero"]
            )
            endpoint_failures["final"] += int(
                not labels["final_endpoint_nonzero"]
            )
            for index in range(6):
                prefix_failures[index] += int(not labels["prefix_nonzero"][index])
                suffix_failures[index] += int(not labels["suffix_nonzero"][index])

        signed15 = [
            points[index] if sign == 1
            else validator.ec_neg(points[index], curve["p"])
            for index, sign in zip(indices15, signs15)
        ]
        control_residual = validator.ec_sub(
            peer_target,
            validator.ec_sum(signed15, curve["p"]),
            curve["p"],
        )
        if control_residual is not None and control_residual[0] in x_to_index:
            final_index = x_to_index[control_residual[0]]
            final_sign = (
                1 if control_residual == points[final_index] else -1
            )
            indices = indices15 + [final_index]
            signs = signs15 + [final_sign]
            coordinates = [points[index] for index in indices]
            labels = validator.regularity_labels(
                coordinates, peer_target, curve["p"]
            )
            shuffled[trial] = {
                "event": "shuffled_accepted",
                "cell_id": current_cell,
                "source_target_cell_id": peer_cell,
                "trial_index": trial,
                "indices": indices,
                "signs": signs,
                "points": [
                    validator.point_json(point) for point in coordinates
                ],
                "target": validator.point_json(peer_target),
                "labels": labels,
            }
            counts["shuffled_accepted"] += 1
            counts["shuffled_affine_regular"] += int(labels["affine_regular"])
    summary = {
        "event": "cell_summary",
        "cell_id": current_cell,
        "curve_id": curve["curve_id"],
        "m": curve["m"],
        "arm": arm,
        "seed": seed,
        "planned_attempts": attempts,
        "cell_complete": True,
        "counts": counts,
        "endpoint_failures": endpoint_failures,
        "prefix_failures": prefix_failures,
        "suffix_failures": suffix_failures,
        "leaf_prng_blocks": leaf.counter,
        "leaf_prng_rejected_blocks": leaf.rejected_blocks,
        "operation_counts": dict(ZERO_OPERATIONS),
    }
    bundle = {
        "base": base_event,
        "target": target_event,
        "constructed": validator.reconstruct_constructed_control(
            curve=curve, arm=arm, seed=seed, factor_base=points
        ),
        "accepted": accepted,
        "shuffled": shuffled,
        "summary": summary,
    }
    config = {
        "factor_base_size": 384,
        "trials_per_seed": {curve["curve_id"]: attempts},
    }
    return {
        "bundle": bundle,
        "target_entry": target_entry,
        "shuffled_entry": peer_entry,
        "base_entry": base_entry,
        "factor_base": points,
        "curve": curve,
        "config": config,
    }


def build_decision_fixture() -> list[dict]:
    """Synthetic summaries only; no frozen primary stream is consumed."""

    cells: list[dict] = []
    seeds = validator.CONFIG_CONTRACT["seeds"]
    for curve in validator.EXPECTED_CURVES:
        curve_id = curve["curve_id"]
        accepted_per_seed = 20 if curve["m"] == 19 else 1000
        for arm in validator.ARMS:
            for seed in seeds:
                if arm == "GLV_ORBIT_CLOSED":
                    affine = (
                        accepted_per_seed
                        if curve["m"] == 19
                        else 990
                    )
                    shuffled_affine = round(0.8 * accepted_per_seed)
                    permutation_mean = 0.8
                else:
                    affine = (
                        round(0.8 * accepted_per_seed)
                        if curve["m"] in (19, 21)
                        else 990
                    )
                    shuffled_affine = round(0.7 * accepted_per_seed)
                    permutation_mean = 0.7
                cells.append(
                    {
                        "curve_id": curve_id,
                        "arm": arm,
                        "seed": seed,
                        "counts": {
                            "attempts": accepted_per_seed * 2,
                            "accepted": accepted_per_seed,
                            "affine_regular": affine,
                            "shuffled_accepted": accepted_per_seed,
                            "shuffled_affine_regular": shuffled_affine,
                            "random_label_true": accepted_per_seed // 2,
                        },
                        "_validator_metrics": {
                            "permutation_relation_mean_sum":
                                permutation_mean * accepted_per_seed,
                            "permutation_relation_count": accepted_per_seed,
                        },
                    }
                )
    return cells


def decision_rows(
    cells: list[dict], curve_id: str, arm: str
) -> list[dict]:
    return [
        cell
        for cell in cells
        if cell["curve_id"] == curve_id and cell["arm"] == arm
    ]


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.curve = copy.deepcopy(validator.EXPECTED_CURVES[0])
        cls.curve["trials_per_seed"] = 10000
        cls.p = cls.curve["p"]
        generator_raw = cls.curve["generator"]
        cls.generator = (generator_raw["x"], generator_raw["y"])
        cls.factor_base = [
            validator.ec_mul(scalar, cls.generator, cls.p)
            for scalar in range(1, 33)
        ]
        cls.indices = list(range(16))
        cls.signs = [1] * 16
        cls.points = cls.factor_base[:16]
        cls.target = validator.ec_sum(cls.points, cls.p)
        assert cls.target is not None
        labels = validator.regularity_labels(cls.points, cls.target, cls.p)
        permutations = []
        for control_index in range(16):
            order = validator.deterministic_permutation(
                curve_id=cls.curve["curve_id"],
                arm="PLAIN_MATCHED",
                seed=0,
                trial_index=0,
                permutation_index=control_index,
                prefix=validator.PRNG_PREFIX,
            )
            permuted = [cls.points[index] for index in order]
            permutations.append(
                {
                    "control_index": control_index,
                    "permutation": order,
                    "labels": validator.regularity_labels(
                        permuted, cls.target, cls.p
                    ),
                }
            )
        cls.record = {
            "trial_index": 0,
            "indices": cls.indices,
            "signs": cls.signs,
            "points": [validator.point_json(point) for point in cls.points],
            "target": validator.point_json(cls.target),
            "labels": labels,
            "permutations": permutations,
        }
        cls.cell = {
            "cell_id": "READINESS-CELL",
            "curve_id": cls.curve["curve_id"],
            "arm": "PLAIN_MATCHED",
            "seed": 0,
        }
        cls.transcript_fixture = build_cell_fixture()
        assert cls.transcript_fixture["bundle"]["accepted"]
        assert cls.transcript_fixture["bundle"]["shuffled"]

    def replay(self, record=None, *, curve=None, base=None, target=None) -> None:
        replay = validator.Replay()
        validator.replay_accepted(
            copy.deepcopy(self.record if record is None else record),
            cell=self.cell,
            curve=self.curve if curve is None else curve,
            factor_base=self.factor_base if base is None else base,
            target=self.target if target is None else target,
            replay=replay,
            expected_indices=self.indices,
            expected_signs=self.signs,
        )

    def assert_rejected(self, function) -> None:
        with self.assertRaises(validator.ValidationFailure):
            function()

    def validate_transcript_fixture(self, fixture=None) -> None:
        selected = copy.deepcopy(
            self.transcript_fixture if fixture is None else fixture
        )
        validator.validate_cell_transcript(
            replay=validator.Replay(),
            **selected,
        )

    def test_curve_table_replays(self) -> None:
        replay = validator.Replay()
        curves = validator.check_curve_table(
            validator.load_json(validator.CURVE_TABLE_PATH), replay
        )
        self.assertEqual(len(curves), 3)
        self.assertGreater(replay.checks, 60)

    def test_validator_imports_no_producer(self) -> None:
        tree = ast.parse(VALIDATOR_PATH.read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertNotIn("run", imported)
        self.assertFalse(any(name.endswith(".run") for name in imported))

    def test_curve_fault_rejected(self) -> None:
        document = validator.load_json(validator.CURVE_TABLE_PATH)
        document["curves"][0]["p"] += 2
        self.assert_rejected(
            lambda: validator.check_curve_table(document, validator.Replay())
        )

    def test_exact_relation_and_all_labels_replay(self) -> None:
        self.replay()

    def test_target_fault_rejected(self) -> None:
        wrong = validator.ec_add(self.target, self.generator, self.p)
        self.assert_rejected(lambda: self.replay(target=wrong))

    def test_sign_fault_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["signs"][3] = -1
        self.assert_rejected(lambda: self.replay(record))

    def test_order_fault_rejected_by_deterministic_stream(self) -> None:
        record = copy.deepcopy(self.record)
        record["indices"][0], record["indices"][15] = (
            record["indices"][15],
            record["indices"][0],
        )
        self.assert_rejected(lambda: self.replay(record))

    def test_base_fault_rejected(self) -> None:
        base = list(self.factor_base)
        base[4] = validator.ec_add(base[4], self.generator, self.p)
        self.assert_rejected(lambda: self.replay(base=base))

    def test_obstruction_fault_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["labels"]["prefix_nonzero"][2] = not record["labels"][
            "prefix_nonzero"
        ][2]
        self.assert_rejected(lambda: self.replay(record))

    def test_endpoint_fault_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["labels"]["final_endpoint_nonzero"] = not record["labels"][
            "final_endpoint_nonzero"
        ]
        self.assert_rejected(lambda: self.replay(record))

    def test_permutation_label_fault_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        record["permutations"][7]["labels"]["suffix_nonzero"][4] = not record[
            "permutations"
        ][7]["labels"]["suffix_nonzero"][4]
        self.assert_rejected(lambda: self.replay(record))

    def test_permutation_order_fault_rejected(self) -> None:
        record = copy.deepcopy(self.record)
        order = record["permutations"][3]["permutation"]
        order[0], order[1] = order[1], order[0]
        self.assert_rejected(lambda: self.replay(record))

    def test_bounded_cell_transcript_replays(self) -> None:
        self.validate_transcript_fixture()

    def test_omitted_acceptance_rejected(self) -> None:
        fixture = copy.deepcopy(self.transcript_fixture)
        fixture["bundle"]["accepted"].pop(
            next(iter(fixture["bundle"]["accepted"]))
        )
        self.assert_rejected(lambda: self.validate_transcript_fixture(fixture))

    def test_omitted_shuffled_acceptance_rejected(self) -> None:
        fixture = copy.deepcopy(self.transcript_fixture)
        fixture["bundle"]["shuffled"].pop(
            next(iter(fixture["bundle"]["shuffled"]))
        )
        self.assert_rejected(lambda: self.validate_transcript_fixture(fixture))

    def test_cell_summary_mutation_rejected(self) -> None:
        fixture = copy.deepcopy(self.transcript_fixture)
        fixture["bundle"]["summary"]["counts"]["accepted"] += 1
        self.assert_rejected(lambda: self.validate_transcript_fixture(fixture))

    def test_random_label_mutation_rejected(self) -> None:
        fixture = copy.deepcopy(self.transcript_fixture)
        first = next(iter(fixture["bundle"]["accepted"].values()))
        first["random_label"] = not first["random_label"]
        self.assert_rejected(lambda: self.validate_transcript_fixture(fixture))

    def test_constructed_control_role_mutation_rejected(self) -> None:
        fixture = copy.deepcopy(self.transcript_fixture)
        fixture["bundle"]["constructed"]["role"] = "constructed-control/99"
        self.assert_rejected(lambda: self.validate_transcript_fixture(fixture))

    def check_config_document(self, document) -> None:
        replay = validator.Replay()
        curves = validator.check_curve_table(
            validator.load_json(validator.CURVE_TABLE_PATH), replay
        )
        validator.check_config(
            document,
            curves,
            replay,
            curve_table_path=validator.CURVE_TABLE_PATH,
            preregistration_path=validator.HERE / "PREREGISTRATION.md",
        )

    def test_target_stream_mutation_rejected_even_with_new_commitment(self) -> None:
        document = validator.load_json(validator.CONFIG_PATH)
        target = document["targets"][0]
        target["point"] = copy.deepcopy(document["targets"][1]["point"])
        target["commitment"] = validator.target_commitment(target)
        self.assert_rejected(lambda: self.check_config_document(document))

    def test_paired_public_target_mismatch_rejected(self) -> None:
        document = validator.load_json(validator.CONFIG_PATH)
        orbit = next(
            target
            for target in document["targets"]
            if target["arm"] == "GLV_ORBIT_CLOSED"
        )
        plain = next(
            target
            for target in document["targets"]
            if target["arm"] == "PLAIN_MATCHED"
            and target["curve_id"] == orbit["curve_id"]
            and target["seed"] == orbit["seed"]
        )
        replacement = next(
            target
            for target in document["targets"]
            if target["curve_id"] == orbit["curve_id"]
            and target["seed"] != orbit["seed"]
        )
        plain["point"] = copy.deepcopy(replacement["point"])
        plain["commitment"] = validator.target_commitment(plain)
        self.assertNotEqual(plain["point"], orbit["point"])
        self.assert_rejected(lambda: self.check_config_document(document))

    def test_base_commitment_mutation_rejected(self) -> None:
        document = validator.load_json(validator.CONFIG_PATH)
        document["base_manifest"][0]["ordered_base_sha256"] = "0" * 64
        self.assert_rejected(lambda: self.check_config_document(document))

    def test_target_commitment_mutation_rejected(self) -> None:
        document = validator.load_json(validator.CONFIG_PATH)
        document["targets"][0]["commitment"] = "1" * 64
        self.assert_rejected(lambda: self.check_config_document(document))

    def test_noncyclic_shuffled_peer_rejected(self) -> None:
        document = validator.load_json(validator.CONFIG_PATH)
        target = document["targets"][0]
        target["shuffled_target_cell_id"] = document["targets"][2]["cell_id"]
        target["commitment"] = validator.target_commitment(target)
        self.assert_rejected(lambda: self.check_config_document(document))

    def test_hash_fault_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact = root / "artifact.json"
            sidecar = root / "artifact.sha256"
            artifact.write_text('{"a":1}\n', encoding="utf-8")
            sidecar.write_text(
                hashlib.sha256(artifact.read_bytes()).hexdigest()
                + "  artifact.json\n",
                encoding="utf-8",
            )
            validator.verify_sidecar(artifact, sidecar, validator.Replay())
            artifact.write_text('{"a":2}\n', encoding="utf-8")
            self.assert_rejected(
                lambda: validator.verify_sidecar(
                    artifact, sidecar, validator.Replay()
                )
            )

    def test_validated_artifact_write_verify_and_refuse_overwrite(self) -> None:
        document = {
            "schema_version": validator.ARTIFACT_SCHEMA_VERSION,
            "terminal_status": "PROMOTE_TO_SOLVER_SLOPE_TEST",
            "decision_metrics": {
                "h_new_signal": False,
                "ordered": [3, 2, 1],
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact = root / "artifact.json"
            sidecar = root / "artifact.sha256"
            validator.emit_validated_artifact(document, artifact, sidecar)
            self.assertEqual(
                artifact.read_bytes(),
                validator.canonical_utf8_line(document),
            )
            validator.verify_validated_artifact(
                document, artifact, sidecar, validator.Replay()
            )
            self.assert_rejected(
                lambda: validator.emit_validated_artifact(
                    document, artifact, sidecar
                )
            )
            sidecar.write_text("0" * 64 + "  artifact.json\n", encoding="ascii")
            self.assert_rejected(
                lambda: validator.verify_validated_artifact(
                    document, artifact, sidecar, validator.Replay()
                )
            )

    def fixture_raw_events(self) -> tuple[list[dict], list[dict]]:
        fixture = self.transcript_fixture
        bundle = fixture["bundle"]
        trial_events = list(bundle["accepted"].values()) + list(
            bundle["shuffled"].values()
        )
        trial_events.sort(
            key=lambda item: (
                item["trial_index"],
                0 if item["event"] == "accepted" else 1,
            )
        )
        events = [
            {"event": "run_header"},
            bundle["base"],
            bundle["target"],
            bundle["constructed"],
            *trial_events,
            bundle["summary"],
            {"event": "run_summary"},
        ]
        return copy.deepcopy(events), [fixture["target_entry"]]

    def test_raw_event_order_and_duplicate_faults(self) -> None:
        events, targets = self.fixture_raw_events()
        validator.split_raw_events(events, targets, validator.Replay())
        reordered = copy.deepcopy(events)
        reordered[1], reordered[2] = reordered[2], reordered[1]
        self.assert_rejected(
            lambda: validator.split_raw_events(
                reordered, targets, validator.Replay()
            )
        )
        duplicated = copy.deepcopy(events)
        accepted_index = next(
            index
            for index, event in enumerate(duplicated)
            if event.get("event") == "accepted"
        )
        duplicated.insert(accepted_index + 1, copy.deepcopy(duplicated[accepted_index]))
        self.assert_rejected(
            lambda: validator.split_raw_events(
                duplicated, targets, validator.Replay()
            )
        )

    def test_raw_file_binding_mutation_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            raw = Path(temporary) / "transcript.jsonl"
            raw.write_bytes(b'{"event":"run_summary"}\n')
            binding = [
                {
                    "path": "raw/transcript.jsonl",
                    "sha256": validator.file_sha256(raw),
                    "bytes": raw.stat().st_size,
                }
            ]
            validator.check_raw_file_binding(
                raw, binding, "raw/transcript.jsonl", validator.Replay()
            )
            raw.write_bytes(b'{"event":"mutated"}\n')
            self.assert_rejected(
                lambda: validator.check_raw_file_binding(
                    raw, binding, "raw/transcript.jsonl", validator.Replay()
                )
            )

    def valid_manifest(self) -> dict:
        return {
            "schema_version": "keyai-m16-fixed-target-producer-v1",
            "run_id": "AUTH-TEST",
            "hypothesis_id": validator.HYPOTHESIS_ID,
            "authorization_id": "AUTH-TEST",
            "authorization_source_commit": "a" * 40,
            "bindings": {
                "preregistration_sha256": validator.file_sha256(
                    validator.HERE / "PREREGISTRATION.md"
                ),
                "curve_table_sha256": validator.file_sha256(
                    validator.CURVE_TABLE_PATH
                ),
                "experiment_config_sha256": validator.file_sha256(
                    validator.CONFIG_PATH
                ),
                "run_py_sha256": validator.file_sha256(
                    validator.HERE / "run.py"
                ),
                "validate_py_sha256": validator.file_sha256(
                    validator.VALIDATOR_PATH
                    if hasattr(validator, "VALIDATOR_PATH")
                    else validator.Path(validator.__file__).resolve()
                ),
            },
            "chronology": {
                "base_manifest_frozen_sequence": 1,
                "targets_committed_sequence": 2,
                "leaves_started_sequence": 3,
                "run_started_utc": "2026-07-30T12:00:00Z",
            },
        }

    def test_manifest_binding_and_chronology_faults(self) -> None:
        manifest = self.valid_manifest()
        validator.check_manifest(
            manifest,
            curve_table_path=validator.CURVE_TABLE_PATH,
            config_path=validator.CONFIG_PATH,
            replay=validator.Replay(),
        )
        bad_binding = copy.deepcopy(manifest)
        bad_binding["bindings"]["run_py_sha256"] = "0" * 64
        self.assert_rejected(
            lambda: validator.check_manifest(
                bad_binding,
                curve_table_path=validator.CURVE_TABLE_PATH,
                config_path=validator.CONFIG_PATH,
                replay=validator.Replay(),
            )
        )
        bad_time = copy.deepcopy(manifest)
        bad_time["chronology"]["run_started_utc"] = "not-a-time"
        self.assert_rejected(
            lambda: validator.check_manifest(
                bad_time,
                curve_table_path=validator.CURVE_TABLE_PATH,
                config_path=validator.CONFIG_PATH,
                replay=validator.Replay(),
            )
        )

    def test_post_run_authorization_and_missing_auth(self) -> None:
        manifest = self.valid_manifest()
        config = validator.load_json(validator.CONFIG_PATH)
        authorization = {
            "status": "approved",
            "hypothesis_id": validator.HYPOTHESIS_ID,
            "task_id": validator.TASK_ID,
            "route_id": validator.ROUTE_ID,
            "cell_id": validator.RESEARCH_CELL_ID,
            "promotion_authorized": False,
            "authorization_id": manifest["authorization_id"],
            "source_commit": manifest["authorization_source_commit"],
            "authorized_utc": "2026-07-30T11:00:00Z",
            "sha256_bindings": {
                "preregistration": manifest["bindings"][
                    "preregistration_sha256"
                ],
                "curve_table": manifest["bindings"]["curve_table_sha256"],
                "experiment_config": manifest["bindings"][
                    "experiment_config_sha256"
                ],
                "run_py": manifest["bindings"]["run_py_sha256"],
                "validate_py": manifest["bindings"]["validate_py_sha256"],
            },
            "resource_budget": config["resource_budget"],
            "scope": {
                "kind": "synthetic_toy_only",
                "curve_family": "E_7",
                "curve_ids": config["curve_ids"],
                "max_field_bits": 25,
                "real_world_targets_forbidden": True,
                "secp256k1_targets_forbidden": True,
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            substrate = Path(temporary) / "substrate.json"
            substrate.write_text(
                json.dumps(
                    {"bounded_experiment_authorization": authorization}
                ),
                encoding="utf-8",
            )
            validator.check_canonical_authorization(
                manifest=manifest,
                config=config,
                config_path=validator.CONFIG_PATH,
                curve_table_path=validator.CURVE_TABLE_PATH,
                replay=validator.Replay(),
                substrate_path=substrate,
                check_git_history=False,
            )
            checked = validator.check_approved_authorization(
                config=config,
                config_path=validator.CONFIG_PATH,
                curve_table_path=validator.CURVE_TABLE_PATH,
                replay=validator.Replay(),
                substrate_path=substrate,
                check_git_history=False,
            )
            self.assertEqual(
                checked["authorization_id"], manifest["authorization_id"]
            )
            future = copy.deepcopy(authorization)
            future["authorized_utc"] = "2099-01-01T00:00:00Z"
            substrate.write_text(
                json.dumps({"bounded_experiment_authorization": future}),
                encoding="utf-8",
            )
            self.assert_rejected(
                lambda: validator.check_approved_authorization(
                    config=config,
                    config_path=validator.CONFIG_PATH,
                    curve_table_path=validator.CURVE_TABLE_PATH,
                    replay=validator.Replay(),
                    substrate_path=substrate,
                    check_git_history=False,
                    authorization_not_after=datetime.now(timezone.utc),
                )
            )
            unexpected = copy.deepcopy(authorization)
            unexpected["notes"] = "must not broaden the exact singleton"
            substrate.write_text(
                json.dumps(
                    {"bounded_experiment_authorization": unexpected}
                ),
                encoding="utf-8",
            )
            self.assert_rejected(
                lambda: validator.check_approved_authorization(
                    config=config,
                    config_path=validator.CONFIG_PATH,
                    curve_table_path=validator.CURVE_TABLE_PATH,
                    replay=validator.Replay(),
                    substrate_path=substrate,
                    check_git_history=False,
                )
            )
            malformed_source = copy.deepcopy(authorization)
            malformed_source["source_commit"] = "A" * 40
            substrate.write_text(
                json.dumps(
                    {"bounded_experiment_authorization": malformed_source}
                ),
                encoding="utf-8",
            )
            self.assert_rejected(
                lambda: validator.check_approved_authorization(
                    config=config,
                    config_path=validator.CONFIG_PATH,
                    curve_table_path=validator.CURVE_TABLE_PATH,
                    replay=validator.Replay(),
                    substrate_path=substrate,
                    check_git_history=False,
                )
            )
            malformed_bindings = copy.deepcopy(authorization)
            malformed_bindings["sha256_bindings"] = []
            substrate.write_text(
                json.dumps(
                    {"bounded_experiment_authorization": malformed_bindings}
                ),
                encoding="utf-8",
            )
            self.assert_rejected(
                lambda: validator.check_approved_authorization(
                    config=config,
                    config_path=validator.CONFIG_PATH,
                    curve_table_path=validator.CURVE_TABLE_PATH,
                    replay=validator.Replay(),
                    substrate_path=substrate,
                    check_git_history=False,
                )
            )
            substrate.write_text("{}\n", encoding="utf-8")
            self.assert_rejected(
                lambda: validator.check_canonical_authorization(
                    manifest=manifest,
                    config=config,
                    config_path=validator.CONFIG_PATH,
                    curve_table_path=validator.CURVE_TABLE_PATH,
                    replay=validator.Replay(),
                    substrate_path=substrate,
                    check_git_history=False,
                )
            )

    def test_pre_execution_gate_rejects_present_outcome(self) -> None:
        config = validator.load_json(validator.CONFIG_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            isolated_here = Path(temporary)
            artifact = isolated_here / "artifact.json"
            with (
                mock.patch.object(validator, "HERE", isolated_here),
                mock.patch.object(
                    validator, "ARTIFACT_PATH", artifact
                ),
                mock.patch.object(
                    validator,
                    "SIDECAR_PATH",
                    isolated_here / "artifact.sha256",
                ),
            ):
                validator.check_no_outcomes(config, validator.Replay())
                artifact.write_text("{}\n", encoding="utf-8")
                self.assert_rejected(
                    lambda: validator.check_no_outcomes(
                        config, validator.Replay()
                    )
                )

    def test_execute_writes_nothing_before_full_preflight(self) -> None:
        producer = load_producer()
        with (
            mock.patch.object(
                producer,
                "authorized_preflight",
                side_effect=producer.AuthorizationError("preflight fault"),
            ),
            mock.patch.object(producer, "write_json") as write_json,
            self.assertRaises(producer.AuthorizationError),
        ):
            producer.execute_authorized(
                producer.DEFAULT_CONFIG,
                producer.DEFAULT_CURVE_TABLE,
                producer.HERE,
            )
        write_json.assert_not_called()

    def test_uncommitted_authorization_bytes_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "substrate.json"
            path.write_bytes(b'{"bounded_experiment_authorization":{}}\n')
            validator.check_committed_bytes(
                path,
                path.read_bytes(),
                "committed substrate",
                validator.Replay(),
            )
            self.assert_rejected(
                lambda: validator.check_committed_bytes(
                    path,
                    b"{}\n",
                    "committed substrate",
                    validator.Replay(),
                )
            )
    def test_float_resource_usage_and_nan_rejection(self) -> None:
        budget = {
            "max_cpu_hours": 4,
            "max_wall_hours": 24,
            "max_peak_rss_gib": 4,
        }
        usage = {"cpu_hours": 1.25, "wall_hours": 2.5, "peak_rss_gib": 0.5}
        validator.check_resource_usage(
            usage, budget=budget, resource_reason=None, replay=validator.Replay()
        )
        bad = dict(usage)
        bad["cpu_hours"] = float("nan")
        self.assert_rejected(
            lambda: validator.check_resource_usage(
                bad,
                budget=budget,
                resource_reason=None,
                replay=validator.Replay(),
            )
        )

    def test_resource_terminal_is_validated_pause(self) -> None:
        report = validator.terminal_report(
            producer_terminal="PRODUCER_RESOURCE_EXHAUSTED_UNVALIDATED",
            resource_reason="maximum CPU-hour budget reached",
            cell_summaries=[],
            checks=17,
        )
        self.assertEqual(report["validation_status"], "PASS")
        self.assertEqual(report["terminal_status"], "PAUSE_INCONCLUSIVE")
        self.assertFalse(report["opens_solver_slope_proposal"])
        self.assertFalse(report["h_new_retained"])

    def test_resource_completed_or_final_partial_prefix_accepted(self) -> None:
        validator.check_resource_cell_prefix(
            [{"cell_complete": True}], validator.Replay()
        )
        validator.check_resource_cell_prefix(
            [{"cell_complete": True}, {"cell_complete": False}],
            validator.Replay(),
        )
        self.assert_rejected(
            lambda: validator.check_resource_cell_prefix(
                [{"cell_complete": False}, {"cell_complete": True}],
                validator.Replay(),
            )
        )
        self.assert_rejected(
            lambda: validator.check_resource_cell_prefix(
                [], validator.Replay()
            )
        )

    def test_h_new_all_precommitted_gates_pass(self) -> None:
        cells = build_decision_fixture()
        metrics = validator.decision_metrics(cells)
        self.assertTrue(metrics["primary_promotion_gates_pass"])
        self.assertTrue(metrics["h_new_signal"])
        self.assertEqual(
            metrics["h_new_qualifying_sizes"],
            [
                "E7-P262153-N262567",
                "E7-P1048783-N1050337",
            ],
        )
        self.assertEqual(
            validator.classify_terminal(cells),
            "PROMOTE_TO_SOLVER_SLOPE_TEST",
        )
        # The reader-facing metrics must be deterministic JSON data, not
        # internal tuple-key maps.
        json.dumps(metrics, sort_keys=True)

    def test_each_h_new_gate_blocks_only_h_new(self) -> None:
        m19 = "E7-P262153-N262567"
        baseline_terminal = validator.classify_terminal(
            build_decision_fixture()
        )
        self.assertEqual(
            baseline_terminal, "PROMOTE_TO_SOLVER_SLOPE_TEST"
        )

        cases = {}

        cells = build_decision_fixture()
        for row in decision_rows(cells, m19, "PLAIN_MATCHED"):
            row["counts"]["affine_regular"] = 19
        cases["primary_delta"] = cells

        cells = build_decision_fixture()
        for row in decision_rows(cells, m19, "GLV_ORBIT_CLOSED"):
            row["counts"]["affine_regular"] = 19
        for row in decision_rows(cells, m19, "PLAIN_MATCHED"):
            row["counts"]["affine_regular"] = 17
        cases["primary_interval_nonoverlap"] = cells

        cells = build_decision_fixture()
        orbit_rows = decision_rows(cells, m19, "GLV_ORBIT_CLOSED")
        plain_rows = decision_rows(cells, m19, "PLAIN_MATCHED")
        for row in plain_rows:
            row["counts"]["affine_regular"] = 12
        for index, row in enumerate(orbit_rows):
            row["counts"]["affine_regular"] = 20 if index < 3 else 12
        cases["primary_four_of_five"] = cells

        cells = build_decision_fixture()
        for arm in validator.ARMS:
            for row in decision_rows(cells, m19, arm):
                row["counts"]["shuffled_accepted"] = 19
                row["counts"]["shuffled_affine_regular"] = (
                    15 if arm == "GLV_ORBIT_CLOSED" else 13
                )
        cases["shuffled_minimum_count"] = cells

        cells = build_decision_fixture()
        for arm in validator.ARMS:
            for row in decision_rows(cells, m19, arm):
                row["counts"]["shuffled_affine_regular"] = 14
        cases["shuffled_delta"] = cells

        cells = build_decision_fixture()
        for arm in validator.ARMS:
            for row in decision_rows(cells, m19, arm):
                row["_validator_metrics"][
                    "permutation_relation_mean_sum"
                ] = 14.0
        cases["permutation_delta"] = cells

        cells = build_decision_fixture()
        orbit_rows = decision_rows(cells, m19, "GLV_ORBIT_CLOSED")
        plain_rows = decision_rows(cells, m19, "PLAIN_MATCHED")
        for row in plain_rows:
            row["_validator_metrics"][
                "permutation_relation_mean_sum"
            ] = 10.0
        for index, row in enumerate(orbit_rows):
            row["_validator_metrics"][
                "permutation_relation_mean_sum"
            ] = 20.0 if index < 3 else 10.0
        cases["permutation_four_of_five"] = cells

        cells = build_decision_fixture()
        for arm in validator.ARMS:
            for row in decision_rows(cells, m19, arm):
                row["counts"]["random_label_true"] = 14
        cases["random_label_rate"] = cells

        cells = build_decision_fixture()
        for row in decision_rows(cells, m19, "GLV_ORBIT_CLOSED"):
            row["counts"]["random_label_true"] = 13
        for row in decision_rows(cells, m19, "PLAIN_MATCHED"):
            row["counts"]["random_label_true"] = 10
        cases["random_label_arm_delta"] = cells

        for name, selected in cases.items():
            with self.subTest(gate=name):
                metrics = validator.decision_metrics(selected)
                self.assertFalse(metrics["h_new_signal"])
                self.assertEqual(
                    validator.classify_terminal(selected),
                    baseline_terminal,
                )

    def test_known_and_promote_both_open_one_slope_proposal(self) -> None:
        promote_cells = build_decision_fixture()
        promote = validator.terminal_report(
            producer_terminal="PRODUCER_COMPLETE_UNVALIDATED",
            resource_reason=None,
            cell_summaries=promote_cells,
            checks=1,
        )
        self.assertEqual(
            promote["terminal_status"], "PROMOTE_TO_SOLVER_SLOPE_TEST"
        )
        self.assertTrue(promote["opens_solver_slope_proposal"])
        self.assertTrue(promote["h_new_retained"])

        known_cells = build_decision_fixture()
        m21 = "E7-P1048783-N1050337"
        for row in decision_rows(known_cells, m21, "PLAIN_MATCHED"):
            row["counts"]["affine_regular"] = 990
        known = validator.terminal_report(
            producer_terminal="PRODUCER_COMPLETE_UNVALIDATED",
            resource_reason=None,
            cell_summaries=known_cells,
            checks=1,
        )
        self.assertEqual(
            known["terminal_status"],
            "CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION",
        )
        self.assertTrue(known["opens_solver_slope_proposal"])
        self.assertFalse(known["h_new_retained"])

    def test_wilson_reference_values(self) -> None:
        low, high = validator.wilson_interval(95, 100)
        self.assertAlmostEqual(low, 0.8882495307680808)
        self.assertAlmostEqual(high, 0.9784563208456319)
        self.assertEqual(validator.wilson_interval(0, 0), (0.0, 1.0))

    def test_missing_outcomes_are_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(validator.ValidationInconclusive):
                validator.validate_paths(
                    curve_table_path=root / "curve_table.json",
                    config_path=root / "experiment_config.json",
                    manifest_path=root / "run_manifest.json",
                    raw_path=root / "raw" / "transcript.jsonl",
                    summary_path=root / "summary.json",
                )


if __name__ == "__main__":
    unittest.main()
