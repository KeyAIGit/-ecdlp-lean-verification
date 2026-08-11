from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from experiments.ecdlp_lab.core import validate as offline_validate
from experiments.ecdlp_lab.core.catalog_registry import (
    CI_CATALOG_ID,
    LEGACY_CATALOG_ID,
    CatalogRegistryError,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def run_offline_cli() -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.ecdlp_lab.core.validate",
            "--offline",
            "--json",
        ],
        cwd=REPO_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )


class CatalogOfflineIntegrationTests(unittest.TestCase):
    def test_registered_catalogs_pass_every_offline_curve_gate(self) -> None:
        authorities, registry_issues = offline_validate._catalog_authorities()
        self.assertEqual(registry_issues, [])
        self.assertEqual(
            {authority.catalog_id for authority in authorities},
            {CI_CATALOG_ID, LEGACY_CATALOG_ID},
        )
        self.assertEqual(
            offline_validate._registered_catalog_issues(authorities), []
        )

    def test_offline_cli_is_deterministic_with_catalog_validation(self) -> None:
        first = run_offline_cli()
        second = run_offline_cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        report = json.loads(first.stdout)
        self.assertTrue(report["passed"])
        self.assertEqual(report["issues"], [])
        # P02 strengthens the offline gate without changing the stable P01
        # contract-corpus counters consumed by existing automation.
        self.assertEqual(
            report["summary"],
            {
                "adversarial_cases": 24,
                "issues": 0,
                "schemas": 9,
                "valid_records": 10,
            },
        )

    def test_registry_failure_grants_no_partial_catalog_authority(self) -> None:
        with mock.patch.object(
            offline_validate,
            "load_catalog_registry",
            side_effect=CatalogRegistryError("registry drift"),
        ):
            authorities, issues = offline_validate._catalog_authorities()
        self.assertEqual(authorities, ())
        self.assertEqual(
            {issue.code for issue in issues}, {"offline.catalog_registry"}
        )


if __name__ == "__main__":
    unittest.main()
