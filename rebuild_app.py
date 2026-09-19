#!/usr/bin/env python3
from pathlib import Path
root = Path(__file__).parent
text = "".join((root / f"_src_{x}.py").read_text() for x in ("a", "b", "c", "d"))
(root / "app_full.py").write_text(text)
print("OK", len(text))
