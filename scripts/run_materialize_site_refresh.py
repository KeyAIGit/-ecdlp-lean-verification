#!/usr/bin/env python3
from __future__ import annotations

import lzma
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
source = ROOT / "scripts" / "materialize_site_refresh.py.xz"
target = ROOT / "scripts" / "materialize_site_refresh.py"
target.write_bytes(lzma.decompress(source.read_bytes()))
raise SystemExit(subprocess.run([sys.executable, str(target)], cwd=ROOT).returncode)
