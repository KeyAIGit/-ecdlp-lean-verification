#!/usr/bin/env python3
"""Compatibility entry point for every generated KeyAI public-site surface."""
from __future__ import annotations

from build_results_portal import main as build_results_portal
from site_generator import main as build_site


def main() -> int:
    result = build_site()
    if result:
        return result
    return build_results_portal([])


if __name__ == "__main__":
    raise SystemExit(main())
