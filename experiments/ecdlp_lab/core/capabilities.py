"""Deterministic, dependency-free capability discovery for the ECDLP lab.

Finding an executable is deliberately separate from verifying the backend it
belongs to.  This module never executes optional tools: it only resolves them
with :func:`shutil.which`.  Consequently, an installed optional backend is
reported as available but untested, while a missing backend is explicitly
skipped rather than credited with a pass.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Sequence


class CapabilityState(str, Enum):
    """Discovery state for a tool or backend."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    UNTESTED = "untested"


class VerificationState(str, Enum):
    """Independent verification state for a discovered capability."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED_MISSING_CAPABILITY = "skipped_missing_capability"
    UNTESTED = "untested"


@dataclass(frozen=True)
class Capability:
    """One stable capability-report row."""

    name: str
    command: str
    resolved_path: str | None
    capability_state: str
    verification_state: str


_OPTIONAL_COMMANDS: tuple[tuple[str, str], ...] = (
    ("sage", "sage"),
    ("cargo", "cargo"),
    ("rustc", "rustc"),
    ("nvcc", "nvcc"),
    ("nvidia-smi", "nvidia-smi"),
    ("docker", "docker"),
)


def _resolve(
    name: str,
    command: str,
    *,
    verified_when_available: bool = False,
) -> Capability:
    """Resolve *command* without executing it and report failures honestly."""

    try:
        resolved_path = shutil.which(command)
    except (OSError, TypeError, ValueError):
        return Capability(
            name=name,
            command=command,
            resolved_path=None,
            capability_state=CapabilityState.ERROR.value,
            verification_state=VerificationState.FAILED.value,
        )

    if resolved_path is None:
        return Capability(
            name=name,
            command=command,
            resolved_path=None,
            capability_state=CapabilityState.UNAVAILABLE.value,
            verification_state=VerificationState.SKIPPED_MISSING_CAPABILITY.value,
        )

    verification_state = (
        VerificationState.PASSED
        if verified_when_available
        else VerificationState.UNTESTED
    )
    return Capability(
        name=name,
        command=command,
        resolved_path=resolved_path,
        capability_state=CapabilityState.AVAILABLE.value,
        verification_state=verification_state.value,
    )


def collect_capabilities() -> tuple[Capability, ...]:
    """Collect capabilities in a fixed order with no subprocesses or network."""

    # This module is already running under sys.executable, so successful
    # resolution of that exact interpreter is the one capability we can mark
    # verified without invoking a separate backend test.
    python_command = sys.executable or "python3"
    rows = [
        _resolve(
            "python",
            python_command,
            verified_when_available=True,
        )
    ]
    rows.extend(_resolve(name, command) for name, command in _OPTIONAL_COMMANDS)
    return tuple(rows)


def build_report() -> dict[str, object]:
    """Return the stable JSON-compatible capability report."""

    capabilities = collect_capabilities()
    _assert_valid_states(capabilities)
    return {
        "schema_version": 1,
        "report_kind": "ecdlp_lab_capability_report",
        "capabilities": [asdict(capability) for capability in capabilities],
    }


def _assert_valid_states(capabilities: Sequence[Capability]) -> None:
    capability_states = {state.value for state in CapabilityState}
    verification_states = {state.value for state in VerificationState}
    for capability in capabilities:
        if capability.capability_state not in capability_states:
            raise RuntimeError(f"invalid capability state for {capability.name}")
        if capability.verification_state not in verification_states:
            raise RuntimeError(f"invalid verification state for {capability.name}")
        if (
            capability.capability_state == CapabilityState.UNAVAILABLE.value
            and capability.verification_state == VerificationState.PASSED.value
        ):
            raise RuntimeError(
                f"unavailable capability cannot pass: {capability.name}"
            )


def _render_text(report: dict[str, object]) -> str:
    capabilities = report["capabilities"]
    if not isinstance(capabilities, list):  # Defensive guard for internal use.
        raise RuntimeError("capabilities report is malformed")
    return "\n".join(
        f"{row['name']}: {row['capability_state']} / "
        f"{row['verification_state']}"
        for row in capabilities
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report local ECDLP lab capabilities without executing backends."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit deterministic compact JSON",
    )
    args = parser.parse_args(argv)

    report = build_report()
    if args.json:
        output = json.dumps(
            report,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    else:
        output = _render_text(report)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
