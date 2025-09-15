from __future__ import annotations
import os, json, time
from typing import Sequence, Dict
from .paths import DB_JSON_PATH, HISTORY_DIR, ensure_dirs
from .versioning import sha256_of, utc_now_iso
from . import flatten as F
from . import loader as L

def _read_existing_version() -> tuple[int, str] | tuple[int, None]:
    try:
        with open(DB_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        ver = int(data.get("_meta", {}).get("version", 0) or 0)
        content_sha = str(data.get("_meta", {}).get("content_sha256", "")) or ""
        return ver, content_sha
    except Exception:
        return 0, None

def _write_outputs(payload: dict) -> str:
    ensure_dirs()
    # constant file
    with open(DB_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    # snapshot history
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    hist_path = os.path.join(HISTORY_DIR, f"nervon_workflow_{payload['_meta']['version']}_{stamp}.json")
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return DB_JSON_PATH

def build_from_gspread(sheet_id: str, worksheets: Sequence[str]) -> dict:
    tables: Dict[str, list] = {}
    for tab in worksheets:
        df = L.load_gspread_dataframe(sheet_id, tab)
        df = F.clean_table(df)
        tables[tab] = F.df_to_rows(df)
    return {"tables": tables, "_source": {"mode": "gspread", "sheet_id": sheet_id, "worksheets": list(worksheets)}}

def build_from_csv(csv_url: str, alias: str) -> dict:
    df = L.load_csv_dataframe(csv_url)
    df = F.clean_table(df)
    return {"tables": {alias: F.df_to_rows(df)}, "_source": {"mode": "csv", "csv_url": csv_url, "alias": alias}}

def build_payload(core: dict, base_major: int = 1, base_minor: int = 0) -> dict:
    # Versioning: compare SHA of the "tables" block with previous
    new_sha = sha256_of(core["tables"])
    prev_ver, prev_sha = _read_existing_version()
    version = prev_ver + 1 if prev_sha != new_sha else prev_ver or 1

    payload = {
        "_meta": {
            "name": "nervon_workflow",
            "version": version,
            "built_at_utc": utc_now_iso(),
            "content_sha256": new_sha,
            "version_label": f"{base_major}.{base_minor}.{version}",
            "source": core.get("_source", {}),
        },
        "tables": core["tables"],
    }
    return payload

def build_and_write(*, sheet_id: str | None = None, worksheets: Sequence[str] | None = None, csv_url: str | None = None, csv_alias: str | None = None, base_major: int = 1, base_minor: int = 0) -> str:
    if csv_url:
        core = build_from_csv(csv_url, csv_alias or "sheet")
    elif sheet_id:
        core = build_from_gspread(sheet_id, worksheets or [])
    else:
        raise RuntimeError("Provide either sheet_id(+worksheets) or csv_url.")
    payload = build_payload(core, base_major=base_major, base_minor=base_minor)
    return _write_outputs(payload)
