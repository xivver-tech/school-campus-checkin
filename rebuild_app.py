#!/usr/bin/env python3
import base64, zlib
from pathlib import Path
root = Path(__file__).parent
parts = [(root / f"_z{i}.txt").read_text().strip() for i in range(2)]
data = zlib.decompress(base64.b64decode("".join(parts)))
(root / "app_full.py").write_bytes(data)
print("OK", len(data))
