#!/usr/bin/env python3
"""Pure helpers for the ordered TASK-011 -> TASK-012 pilot state machine."""
from __future__ import annotations

from datetime import date

DISCOVERY_DISPOSITIONS = {"build", "change", "stop", "pending"}


def parse_iso_date(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def record_sequence(record: dict) -> int | None:
    value = record.get("sequence")
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        return None
    return value


def is_completed_external(record: object, primary_hypothesis_id: str) -> bool:
    return (
        isinstance(record, dict)
        and record.get("hypothesis_id") == primary_hypothesis_id
        and record.get("external") is True
        and record.get("status") == "completed"
        and parse_iso_date(record.get("performed_on")) is not None
        and record_sequence(record) is not None
        and isinstance(record.get("case_id"), str)
        and bool(record["case_id"])
        and isinstance(record.get("public_summary"), str)
        and bool(record["public_summary"].strip())
        and isinstance(record.get("evidence_files"), list)
        and bool(record["evidence_files"])
    )


def ordered_primary_records(pilot: dict) -> list[dict]:
    primary = pilot.get("primary_hypothesis_id", "")
    records = [
        record
        for record in pilot.get("evidence_log", [])
        if is_completed_external(record, primary)
    ]
    return sorted(records, key=lambda record: record_sequence(record) or 0)


def primary_dispositions(pilot: dict) -> list[dict]:
    return [
        record
        for record in ordered_primary_records(pilot)
        if record.get("stage") == "discovery"
        and record.get("task_id") == "TASK-011"
        and record.get("disposition") in DISCOVERY_DISPOSITIONS
    ]


def latest_primary_disposition(pilot: dict) -> dict | None:
    records = primary_dispositions(pilot)
    return records[-1] if records else None


def task_012_unlocked(pilot: dict) -> bool:
    latest = latest_primary_disposition(pilot)
    return bool(latest and latest.get("disposition") == "build")


def valid_second_projects(pilot: dict) -> list[dict]:
    discovery = latest_primary_disposition(pilot)
    if not discovery or discovery.get("disposition") != "build":
        return []
    discovery_sequence = record_sequence(discovery) or 0
    discovery_date = parse_iso_date(discovery.get("performed_on"))
    return [
        record
        for record in ordered_primary_records(pilot)
        if record.get("stage") == "second_project"
        and record.get("task_id") == "TASK-012"
        and record.get("case_id") == discovery.get("case_id")
        and (record_sequence(record) or 0) > discovery_sequence
        and parse_iso_date(record.get("performed_on")) >= discovery_date
    ]


def valid_returns(pilot: dict) -> list[dict]:
    returns = [
        record
        for record in ordered_primary_records(pilot)
        if record.get("stage") == "return" and record.get("task_id") == "TASK-012"
    ]
    valid: list[dict] = []
    for second_project in valid_second_projects(pilot):
        second_sequence = record_sequence(second_project) or 0
        second_date = parse_iso_date(second_project.get("performed_on"))
        valid.extend(
            record
            for record in returns
            if record.get("case_id") == second_project.get("case_id")
            and (record_sequence(record) or 0) > second_sequence
            and parse_iso_date(record.get("performed_on")) >= second_date
        )
    return sorted(
        {record_sequence(record): record for record in valid}.values(),
        key=lambda record: record_sequence(record) or 0,
    )


def expected_primary_status(pilot: dict) -> str:
    if valid_returns(pilot):
        return "supported"
    latest = latest_primary_disposition(pilot)
    if not latest:
        return "unvalidated"
    disposition = latest.get("disposition")
    if disposition == "stop":
        return "rejected"
    if disposition in {"build", "change"}:
        return "testing"
    prior_testing = any(
        record.get("disposition") in {"build", "change"}
        for record in primary_dispositions(pilot)[:-1]
    )
    return "testing" if prior_testing else "unvalidated"


def expected_pilot_status(pilot: dict) -> str | None:
    if valid_returns(pilot):
        return "mvp_validated"
    latest = latest_primary_disposition(pilot)
    if not latest:
        return None
    disposition = latest.get("disposition")
    if disposition == "stop":
        return "stopped"
    if disposition == "pending":
        return "discovery_active"
    return "discovery_complete"


def latest_completed_external(pilot: dict) -> dict | None:
    records = ordered_primary_records(pilot)
    return records[-1] if records else None
