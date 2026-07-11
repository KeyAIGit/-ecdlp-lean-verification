#!/usr/bin/env python3
"""Experiment-manifest helper — deterministic provenance for every P0 run.

The truth substrate needs a *verifiable chain* (source -> claim -> experiment -> result -> proof),
not just output files. This records, per experiment run, everything needed to reproduce and audit
it: the hypothesis id, a content hash of the experiment code, the seed and parameters, tool
versions, a hash of the recorded results, and a UTC timestamp (passed in, since we never call a
nondeterministic clock inside the experiment itself).

Manifests are written under `experiments/p0_glv_semaev/runs/<run_id>.json`.

Usage (from an experiment script):
    from manifest import Manifest
    m = Manifest(hypothesis="HYP_GLV_SEMAEV_001", variant="glv-base", params={...},
                 code_files=[__file__, "toy_curves.py"])
    ... run ...
    m.record(results={...})
    path = m.write(timestamp_iso)   # caller supplies the timestamp
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_obj(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _tool_versions() -> dict:
    out = {"python": sys.version.split()[0], "platform": platform.platform()}
    for mod in ("sympy", "flint", "galois", "numpy"):
        try:
            m = __import__(mod)
            out[mod] = getattr(m, "__version__", "unknown")
        except Exception:
            out[mod] = "absent"
    return out


@dataclass
class Manifest:
    hypothesis: str
    variant: str
    params: dict
    code_files: list = field(default_factory=list)
    results: dict = field(default_factory=dict)
    code_hashes: dict = field(default_factory=dict)
    tools: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.tools = _tool_versions()
        for f in self.code_files:
            p = Path(f)
            if not p.is_absolute():
                p = HERE / p
            if p.exists():
                self.code_hashes[p.name] = _sha256_file(p)

    def record(self, results: dict) -> None:
        self.results = results

    def to_dict(self, timestamp_iso: str) -> dict:
        body = {
            "hypothesis": self.hypothesis,
            "variant": self.variant,
            "params": self.params,
            "code_hashes": self.code_hashes,
            "tools": self.tools,
            "results": self.results,
            "timestamp": timestamp_iso,
        }
        body["results_hash"] = _sha256_obj(self.results)
        return body

    def run_id(self, timestamp_iso: str) -> str:
        tag = _sha256_obj(
            {"h": self.hypothesis, "v": self.variant, "p": self.params, "t": timestamp_iso}
        )[:12]
        return f"{self.hypothesis}_{self.variant}_{tag}"

    def write(self, timestamp_iso: str) -> Path:
        RUNS.mkdir(exist_ok=True)
        path = RUNS / f"{self.run_id(timestamp_iso)}.json"
        path.write_text(json.dumps(self.to_dict(timestamp_iso), indent=2), encoding="utf-8")
        return path


if __name__ == "__main__":
    # Smoke test: build a manifest with dummy results and print it (no file written).
    m = Manifest(
        hypothesis="HYP_GLV_SEMAEV_001",
        variant="selftest",
        params={"bits": 16, "seed": 1},
        code_files=[__file__, "toy_curves.py"],
    )
    m.record({"relations": 0, "note": "smoke"})
    print(json.dumps(m.to_dict("1970-01-01T00:00:00Z"), indent=2))
