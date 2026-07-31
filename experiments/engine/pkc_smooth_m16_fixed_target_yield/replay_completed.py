#!/usr/bin/env python3
"""Replay the immutable TASK-026 result after its authorization is consumed.

The frozen validator correctly requires the pre-execution authorization shape
that existed at the approved Git commit.  The canonical decision substrate is
now terminal and therefore says ``consumed``.  This adapter verifies that the
current terminal record is exactly the completion of that approved singleton,
then supplies the immutable approved snapshot to the unmodified validator.
"""
from __future__ import annotations

import importlib.util
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VALIDATOR_PATH = HERE / "validate.py"
DECISION_PATH = ROOT / "repo" / "ECDLP_DECISION_SUBSTRATE.json"
AUTHORIZATION_KEY = "bounded_experiment_authorization"
AUTHORIZATION_COMMIT = "ab09b0fc485fca940fd6a5dbacae1e8b117a69ca"
AUTHORIZATION_ID = "AUTH-HYP-M16-FIXED-TARGET-YIELD-001-20260730-01"
EVENT_ID = "REO-2026-07-31-001"
TERMINAL_STATUS = "CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION"
ARTIFACT_SHA256 = (
    "21a95ea4ea71c02d0199c331e549ca2e4ec2fbf7c1d8d70fe6651bea292d6413"
)
TERMINAL_ONLY_FIELDS = {
    "completed_utc",
    "terminal_event_id",
    "terminal_status",
    "normalized_outcome",
    "validated_artifact_sha256",
    "rerun_authorized",
}


def load_validator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "task026_frozen_validator", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def git_json(commit: str, relative: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise RuntimeError("approved authorization commit is not inspectable")
    value = json.loads(completed.stdout)
    if not isinstance(value, dict):
        raise RuntimeError("approved authorization substrate is not an object")
    return value


def terminal_matches_approval(
    approved: dict[str, Any], consumed: dict[str, Any]
) -> None:
    if approved.get("status") != "approved":
        raise RuntimeError("pinned authorization snapshot is not approved")
    if consumed.get("status") != "consumed":
        raise RuntimeError("canonical authorization is not consumed")
    expected_consumed_base = {
        key: value for key, value in consumed.items() if key not in TERMINAL_ONLY_FIELDS
    }
    expected_consumed_base["status"] = "approved"
    if expected_consumed_base != approved:
        raise RuntimeError("consumed authorization base differs from approved snapshot")
    expected_terminal = {
        "authorization_id": AUTHORIZATION_ID,
        "terminal_event_id": EVENT_ID,
        "terminal_status": TERMINAL_STATUS,
        "normalized_outcome": "supported",
        "validated_artifact_sha256": ARTIFACT_SHA256,
        "rerun_authorized": False,
    }
    for field, expected in expected_terminal.items():
        if consumed.get(field) != expected:
            raise RuntimeError(f"terminal authorization field drifted: {field}")


def main() -> int:
    try:
        approved_substrate = git_json(
            AUTHORIZATION_COMMIT, "repo/ECDLP_DECISION_SUBSTRATE.json"
        )
        current_substrate = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        approved = approved_substrate.get(AUTHORIZATION_KEY)
        consumed = current_substrate.get(AUTHORIZATION_KEY)
        if not isinstance(approved, dict) or not isinstance(consumed, dict):
            raise RuntimeError("authorization singleton is absent")
        terminal_matches_approval(approved, consumed)

        validator = load_validator()
        frozen_load_json = validator.load_json

        def load_with_approved_authorization(path: Path) -> Any:
            if path.resolve() == DECISION_PATH.resolve():
                return approved_substrate
            return frozen_load_json(path)

        validator.load_json = load_with_approved_authorization
        with tempfile.TemporaryDirectory() as temporary:
            snapshot_path = Path(temporary) / "approved_substrate.json"
            snapshot_path.write_text(
                json.dumps(
                    {AUTHORIZATION_KEY: approved},
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            frozen_check = validator.check_canonical_authorization

            def check_pinned_authorization(**kwargs: Any) -> None:
                kwargs["substrate_path"] = snapshot_path
                kwargs["check_git_history"] = False
                frozen_check(**kwargs)
                replay = kwargs["replay"]
                source_commit = approved["source_commit"]
                ancestry = subprocess.run(
                    [
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        source_commit,
                        AUTHORIZATION_COMMIT,
                    ],
                    cwd=ROOT,
                    check=False,
                ).returncode
                replay.require(
                    source_commit != AUTHORIZATION_COMMIT,
                    "authorization source is not pre-approval",
                )
                replay.exact("authorization source ancestry", ancestry, 0)
                replay.require(
                    approved_substrate.get(AUTHORIZATION_KEY) == approved,
                    "approved authorization snapshot drifted",
                )
                bound_paths = {
                    "preregistration": HERE / "PREREGISTRATION.md",
                    "curve_table": HERE / "curve_table.json",
                    "experiment_config": HERE / "experiment_config.json",
                    "run_py": HERE / "run.py",
                    "validate_py": VALIDATOR_PATH,
                }
                for relative_path in bound_paths.values():
                    relative = relative_path.relative_to(ROOT).as_posix()
                    source_bytes = subprocess.run(
                        ["git", "show", f"{source_commit}:{relative}"],
                        cwd=ROOT,
                        check=True,
                        stdout=subprocess.PIPE,
                    ).stdout
                    replay.exact(
                        f"authorization source binding {relative}",
                        hashlib.sha256(source_bytes).hexdigest(),
                        validator.file_sha256(relative_path),
                    )
                source_substrate = git_json(
                    source_commit, "repo/ECDLP_DECISION_SUBSTRATE.json"
                )
                replay.require(
                    isinstance(source_substrate, dict),
                    "readiness-source authorization substrate must be an object",
                )
                source_authorization = source_substrate.get(AUTHORIZATION_KEY)
                replay.require(
                    source_authorization is None
                    or isinstance(source_authorization, dict),
                    "readiness-source authorization singleton is malformed",
                )
                replay.require(
                    not (
                        isinstance(source_authorization, dict)
                        and source_authorization.get("status") == "approved"
                    ),
                    "readiness source already contained approved authorization",
                )

            validator.check_canonical_authorization = check_pinned_authorization
            report = validator.validate_paths()
            artifact_document = report["validated_artifact"]
            validator.verify_validated_artifact(
                artifact_document,
                validator.ARTIFACT_PATH,
                validator.SIDECAR_PATH,
                validator.Replay(),
            )
        print(
            "COMPLETED REPLAY: PASS "
            f"({report['checks']} checks; {report['terminal_status']})"
        )
        return 0
    except (
        KeyError,
        OSError,
        RuntimeError,
        subprocess.CalledProcessError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        print(f"COMPLETED REPLAY: FAIL: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
