#!/usr/bin/env python3
"""Rebuild app_full if needed, then start."""
from pathlib import Path
import runpy, subprocess, sys

root = Path(__file__).parent
full = root / "app_full.py"

if (root / "_z0.txt").exists() and (root / "_z1.txt").exists():
    if (not full.exists()) or full.stat().st_size < 20000:
        subprocess.check_call([sys.executable, str(root / "rebuild_app.py")])

if not full.exists() or full.stat().st_size < 20000:
    raise SystemExit(
        "app_full.py missing/broken. On your PC run:\n"
        "  git checkout 143c631 -- app_full.py\n"
        "  # or copy your working app_full.py and: git add app_full.py && git push"
    )

runpy.run_path(str(full), run_name="__main__")
