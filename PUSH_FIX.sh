#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Building app_full from parts (if present)..."
if [ -f _src_a.py ] && [ -f _src_b.py ] && [ -f _src_c.py ] && [ -f _src_d.py ]; then
  python3 rebuild_app.py
fi
python3 -c "compile(open('app_full.py').read(),'x','exec'); import os; print('OK', os.path.getsize('app_full.py'))"
git add app_full.py _src_*.py rebuild_app.py app.py wsgi.py Procfile requirements.txt i18n.py 2>/dev/null || true
git add app_full.py
git commit -m "Restore complete app_full for Render" || echo "(nothing new to commit)"
git push origin main
echo "DONE — open Render and Redeploy"
