#!/usr/bin/env python3
"""Campus check-in entry point - Rowad Nahda Private Tiznit."""
from pathlib import Path
import runpy

p = Path(__file__).parent / "app_full.py"
if not p.exists():
    raise SystemExit("Missing app_full.py - pull the full repo")
runpy.run_path(str(p), run_name="__main__")
