"""WSGI entry for Render / gunicorn."""
from pathlib import Path
import subprocess, sys, importlib.util

root = Path(__file__).parent
full = root / "app_full.py"

if (root / "_z0.txt").exists() and (root / "_z1.txt").exists():
    if (not full.exists()) or full.stat().st_size < 20000:
        subprocess.check_call([sys.executable, str(root / "rebuild_app.py")])

if not full.exists() or full.stat().st_size < 20000:
    raise SystemExit("app_full.py missing - push a complete app_full.py to the repo")

spec = importlib.util.spec_from_file_location("app_full", full)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
app = mod.app
