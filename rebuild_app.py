#!/usr/bin/env python3
"""Rebuild app_full.py from base64 chunks (GitHub size-safe deploy)."""
import base64
from pathlib import Path
root = Path(__file__).parent
parts = []
for i in range(5):
    parts.append((root / f"_b64_{i}.txt").read_text().strip())
data = base64.b64decode("".join(parts))
(root / "app_full.py").write_bytes(data)
print("Rebuilt app_full.py", len(data), "bytes")
