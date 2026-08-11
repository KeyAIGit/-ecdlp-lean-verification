"""Small structured diagnostics shared by the lab contract modules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Issue:
    """A stable machine-testable validation diagnostic."""

    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"
