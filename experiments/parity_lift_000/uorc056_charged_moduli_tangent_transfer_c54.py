#!/usr/bin/env python3
"""Machine-readable decision package for UORC-056 C54."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from uorc056_c54_transfer_analysis import build_payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = build_payload()
    if args.out:
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("UORC056_CHARGED_MODULI_TANGENT_TRANSFER_C54_OK")
    print(json.dumps(payload["aggregate"], indent=2, sort_keys=True))
    print("digest=" + payload["digest"])


if __name__ == "__main__":
    main()
