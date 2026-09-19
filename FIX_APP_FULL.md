# Restore app_full.py (required for Render)

The large `app_full.py` must be pushed from your PC (GitHub uploads of the full file were truncated).

## On your computer (where the app already worked)

```bash
cd school-campus-checkin

# Option A: restore from older good commit
git fetch
git checkout 143c631 -- app_full.py

# Option B: if you still have a working local app_full.py, keep it

# Test
python -c "compile(open('app_full.py').read(),'x','exec'); print('OK')"
python app.py
# Ctrl+C after it starts

# Push
git add app_full.py Procfile requirements.txt wsgi.py app.py
git commit -m "Restore complete app_full for Render"
git push origin main
```

Then open Render and deploy / redeploy.

## After push, Render settings

- Build: `pip install -r requirements.txt`
- Start: `gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app`
- Or use the Procfile (same command)
