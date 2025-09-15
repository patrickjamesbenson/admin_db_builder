# Nervon Workflow Database (Google Sheet → Flat JSON)

A tiny, reusable helper that **loads your Google Sheet**, bundles the bits you need, and writes a **single, flat JSON** database that the rest of your apps can share.

- **Constant filename** for all consumers: `assets/nervon_workflow.json`
- **Version embedded inside** the JSON (and history snapshots kept)
- **Switch Google Sheet later** just by changing config or Streamlit secrets—no code edits
- **Works on Streamlit Cloud or locally** (service account or public CSV export)

---

## Quick start (local)

```bash
# 1) Create a venv and install deps
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) Add your Google service account (private sheet) OR use CSV export (public sheet).
#    Option A: Service account (recommended for private sheets)
#       - Put your Google service account JSON at: service_account.json
#       - Or set environment variable GOOGLE_SA_JSON to the path of your key file.
#
#    Option B: Public CSV export (no auth)
#       - Publish your sheet/tab to the web, grab the CSV export URL and set NV_CSV_URL.

# 3) Configure where the data lives
#    - Easiest: set env vars (see below), OR
#    - Use Streamlit secrets (for Streamlit Cloud), OR
#    - Edit nv_workflow_db/config.py defaults.
#
#    Minimal env example:
#      export NV_SHEET_ID='your-google-sheet-id-here'
#      export NV_WORKSHEET='master_metadata_console'     # your tab name
#      # Optional if you use CSV-export instead of service account:
#      # export NV_CSV_URL='https://docs.google.com/spreadsheets/d/.../export?format=csv&gid=...'
#
# 4) Build once via CLI
python scripts/build_db.py
# → writes assets/nervon_workflow.json (+ versioned history in assets/history/)

# 5) (Optional) Run the demo UI
streamlit run streamlit_app.py
```

> **Note**: If you already have an existing Streamlit app, you can import and read the JSON:
>
> ```python
> from nv_workflow_db.paths import DB_JSON_PATH
> import json
> data = json.loads(open(DB_JSON_PATH, "r", encoding="utf-8").read())
> ```

---

## Changing the Google Sheet later

You **do not** need to change code. Choose any one of these:

1. **Environment variables** (local / server):
   - `NV_SHEET_ID` and `NV_WORKSHEET` for private access with a service account (use `GOOGLE_SA_JSON` to point to your key file)
   - or `NV_CSV_URL` for a published CSV export link

2. **Streamlit secrets** (`.streamlit/secrets.toml` locally, or in Streamlit Cloud UI):
   ```toml
   NV_SHEET_ID = "your-sheet-id"
   NV_WORKSHEET = "master_metadata_console"
   GOOGLE_SA_JSON = "service_account.json"  # or absolute path
   # Alternative:
   # NV_CSV_URL = "https://docs.google.com/spreadsheets/d/.../export?format=csv&gid=..."
   ```

3. **Hard-code defaults** in `nv_workflow_db/config.py` (not recommended).

Rebuild any time from the UI (press **Rebuild DB**) or via CLI (`python scripts/build_db.py`).

---

## What goes into the flat JSON?

By default we include **one worksheet** (your main metadata sheet) and bundle it as a list of rows. We also embed a small **`_meta`** block with version, source, and hash. Example shape:

```json
{
  "_meta": {
    "name": "nervon_workflow",
    "version": 3,
    "built_at_utc": "2025-09-15T01:23:45Z",
    "content_sha256": "…",
    "source": {
      "mode": "gspread",  // or "csv"
      "sheet_id": "...",
      "worksheet": "master_metadata_console"
    }
  },
  "tables": {
    "master_metadata_console": [
      {"FIELD": "IESNA: LM-63-2019", "IES_ORDER": 1, "IES_FUNC": "Derived", "IES_TOOLTIP": "..."},
      ...
    ]
  }
}
```

If you want to add **more tabs** later, you can expand `nv_workflow_db/config.py` (`INCLUDE_SHEETS`) to a list, or pass a list to the builder in code.

---

## Repo layout

```
.
├─ assets/
│  ├─ nervon_workflow.json          # constant filename used by all apps
│  └─ history/                      # auto snapshots per build
├─ nv_workflow_db/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ flatten.py
│  ├─ loader.py
│  ├─ paths.py
│  └─ versioning.py
├─ scripts/
│  └─ build_db.py                   # CLI: python scripts/build_db.py
├─ streamlit_app.py                 # demo UI
├─ .streamlit/secrets.toml          # local example; use Streamlit Cloud UI in prod
├─ requirements.txt
└─ service_account.example.json     # placeholder (do NOT commit real creds)
```

---

## FAQ

**Q: Do I have to make my sheet public?**  
A: No. If your sheet is private, use a **service account key** (Google Cloud → IAM → Service Accounts), share the sheet with the SA email, and place the JSON at `service_account.json` (or set `GOOGLE_SA_JSON`).

**Q: How is the version updated?**  
A: If the content changes, we calculate a new SHA-256 and **increment `version`**. We also keep a dated snapshot in `assets/history/`.

**Q: What if I want semantic versions (1.2.3)?**  
A: You can set `NV_BASE_MAJOR` / `NV_BASE_MINOR` env vars and we’ll emit `"version_label": "1.2.<buildnum>"` alongside the numeric `version` for convenience.

---

## Licence

MIT. Do what you need, no warranty. Enjoy.
