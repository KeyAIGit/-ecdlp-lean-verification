"""Stable command-line entry point for the fixed P04 smoke campaign.

The command intentionally accepts neither worker modules nor raw commands.  Its
configuration locator is a frozen repository-relative authority and its output
is confined to one explicit directory below the host temporary directory.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import canonical_json_bytes

from .model import OrchestrationError
from .records import SMOKE_CAMPAIGN_PATH, load_smoke_campaign
from .runner import RunnerError, run_campaign


REPO_ROOT = Path(__file__).resolve().parents[3]


def _artifact_root(raw: str) -> Path:
    if (
        type(raw) is not str
        or not raw
        or raw != raw.strip()
        or "\x00" in raw
        or "\\" in raw
        or "://" in raw
    ):
        raise RunnerError(
            "orchestration.output_path", "output must be an absolute local path"
        )
    candidate = Path(raw)
    if not candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise RunnerError(
            "orchestration.output_path",
            "output must be a canonical absolute path without dot components",
        )

    temporary_root = Path(tempfile.gettempdir()).resolve(strict=True)
    parent = candidate.parent
    try:
        if parent.is_symlink():
            raise RunnerError(
                "orchestration.output_path", "output parent cannot be a symlink"
            )
        resolved_parent = parent.resolve(strict=True)
        if resolved_parent != parent.absolute():
            raise RunnerError(
                "orchestration.output_path", "output cannot traverse a symlink"
            )
        resolved_parent.relative_to(temporary_root)
    except RunnerError:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        raise RunnerError(
            "orchestration.output_path",
            "output parent must exist beneath the host temporary directory",
        ) from error
    if candidate == temporary_root or candidate.is_symlink():
        raise RunnerError(
            "orchestration.output_path",
            "output must be a nonsymlink child of the temporary directory",
        )
    if candidate.exists() and not candidate.is_dir():
        raise RunnerError(
            "orchestration.output_path", "existing output must be a directory"
        )
    resolved = resolved_parent / candidate.name
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        return resolved
    raise RunnerError(
        "orchestration.output_path", "output must be outside the repository"
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run or resume the fixed ECDLP engineering smoke campaign."
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.config != SMOKE_CAMPAIGN_PATH:
        print(
            "orchestration.config_path: only the committed smoke campaign is allowed",
            file=sys.stderr,
        )
        return 2
    try:
        output = _artifact_root(args.output)
        campaign = load_smoke_campaign(repo_root=REPO_ROOT)
        summary = run_campaign(
            campaign,
            output,
            repo_root=REPO_ROOT,
            max_parallel=1,
        )
    except (OrchestrationError, RunnerError) as error:
        print(f"{error.code}: {error.message}", file=sys.stderr)
        return 1
    except Exception:
        print("orchestration.internal: smoke failed closed", file=sys.stderr)
        return 1
    try:
        os.write(sys.stdout.fileno(), canonical_json_bytes(summary.as_dict()) + b"\n")
    except OSError:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
