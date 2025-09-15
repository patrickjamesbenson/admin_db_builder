from __future__ import annotations
import os
from nv_workflow_db import build_and_write
from nv_workflow_db.config import DEFAULT_SHEET_ID, DEFAULT_WORKSHEET, DEFAULT_CSV_URL, BASE_MAJOR, BASE_MINOR

def main():
    if DEFAULT_CSV_URL:
        out = build_and_write(csv_url=DEFAULT_CSV_URL, csv_alias=(DEFAULT_WORKSHEET or "sheet"), base_major=BASE_MAJOR, base_minor=BASE_MINOR)
    elif DEFAULT_SHEET_ID and DEFAULT_WORKSHEET:
        out = build_and_write(sheet_id=DEFAULT_SHEET_ID, worksheets=[DEFAULT_WORKSHEET], base_major=BASE_MAJOR, base_minor=BASE_MINOR)
    else:
        raise SystemExit("Set NV_SHEET_ID & NV_WORKSHEET (service account) or NV_CSV_URL (public CSV).")
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
