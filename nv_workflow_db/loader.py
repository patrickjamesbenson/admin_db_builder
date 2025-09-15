from __future__ import annotations
import os, re, io, csv, requests
import pandas as pd

from .config import GOOGLE_SA_JSON

_sheet_id_re = re.compile(r"/spreadsheets/d/([A-Za-z0-9-_]+)")

def normalize_sheet_id_or_url(x: str) -> str:
    x = (x or "").strip()
    m = _sheet_id_re.search(x)
    return m.group(1) if m else x

def load_gspread_dataframe(sheet_id: str, worksheet_title: str) -> pd.DataFrame:
    import gspread
    from google.oauth2.service_account import Credentials

    sid = normalize_sheet_id_or_url(sheet_id)
    if not os.path.exists(GOOGLE_SA_JSON):
        raise RuntimeError(f"Service account JSON not found at '{GOOGLE_SA_JSON}'. Set GOOGLE_SA_JSON or place the key there.")
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(GOOGLE_SA_JSON, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(sid)
    try:
        ws = sh.worksheet(worksheet_title)
    except gspread.exceptions.WorksheetNotFound:
        titles = [w.title for w in sh.worksheets()]
        raise RuntimeError(f"Worksheet '{worksheet_title}' not found. Available tabs: {titles}")
    rows = ws.get_all_records()  # uses the first row as headers
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)

def load_csv_dataframe(csv_url: str) -> pd.DataFrame:
    if not csv_url:
        raise RuntimeError("CSV URL is empty. Provide NV_CSV_URL or use a Google Sheet + service account.")
    r = requests.get(csv_url, timeout=30)
    r.raise_for_status()
    data = r.content.decode("utf-8", errors="replace")
    return pd.read_csv(io.StringIO(data))
