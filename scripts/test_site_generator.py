#!/usr/bin/env python3
"""Regression tests for canonical task parsing in generated site views."""
from __future__ import annotations

import re
import unittest

import site_generator


class TaskParserTests(unittest.TestCase):
    def test_metadata_between_required_fields_does_not_merge_tasks(self) -> None:
        text = """\
### TASK-009 - Completed structural task

Status: completed_bounded_structural
Structural lane: completed
Decision: RS-TEST-001
Hypothesis: HYP-009
Foundation: F-TEST
Kind: theorem | research
Why it matters: This result is complete.
Inputs:
- input

### TASK-010 - Active audit

Status: active_remediation_draft
Kind: review | ops
Hypothesis: none
Why it matters: This audit is active.
Inputs:
- input
"""
        tasks = site_generator.parse_task_text(
            text,
            source="tasks/test.md",
            queue_label="test",
            queue_id="test",
        )

        self.assertEqual([task["id"] for task in tasks], ["TASK-009", "TASK-010"])
        self.assertEqual(tasks[0]["status"], "completed_bounded_structural")
        self.assertEqual(tasks[0]["kind"], "theorem | research")
        self.assertEqual(tasks[0]["why"], "This result is complete.")
        self.assertEqual(tasks[1]["status"], "active_remediation_draft")

    def test_multiline_hypothesis_is_bound_to_its_task(self) -> None:
        text = """\
### TASK-014 - Activation cycle

Status: queued
Kind: literature | theorem
Hypothesis: RQ-ONE, while the parallel workstream owns
`RQ-TWO`
Why it matters: The two workstreams share one release gate.
Inputs:
- input
"""
        [task] = site_generator.parse_task_text(
            text,
            source="tasks/test.md",
            queue_label="test",
            queue_id="test",
        )

        self.assertEqual(
            task["hypothesis"],
            "RQ-ONE, while the parallel workstream owns `RQ-TWO`",
        )

    def test_live_queues_parse_every_canonical_heading(self) -> None:
        expected_ids: list[str] = []
        for path in (
            site_generator.RESEARCH_TASKS_PATH,
            site_generator.PRODUCT_TASKS_PATH,
        ):
            expected_ids.extend(
                re.findall(r"^### (TASK-\d+) - ", path.read_text(encoding="utf-8"), re.M)
            )

        self.assertEqual(
            [task["id"] for task in site_generator.parse_tasks()],
            expected_ids,
        )

    def test_missing_required_field_fails_closed(self) -> None:
        text = """\
### TASK-999 - Malformed

Status: active
Hypothesis: none
Why it matters: Missing Kind must not disappear from the site silently.
Inputs:
- input
"""
        with self.assertRaisesRegex(ValueError, "missing required field 'Kind'"):
            site_generator.parse_task_text(
                text,
                source="tasks/test.md",
                queue_label="test",
                queue_id="test",
            )


if __name__ == "__main__":
    unittest.main()
