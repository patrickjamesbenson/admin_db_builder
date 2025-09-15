from __future__ import annotations
import json, os, re
from typing import Any, Dict, List

from .paths import DB_JSON_PATH

def _geom_key_from_func(func: str) -> str | None:
    f = (func or "").strip().upper()
    if len(f) >= 2 and f.startswith("G") and f[1:].isdigit():
        return f
    return None

def load_master_metadata_schema_from_db(table_name: str = "master_metadata_console") -> List[Dict[str, Any]]:
    """
    Read constant JSON at assets/nervon_workflow.json and convert the chosen table
    into the schema shape your app likely expects (field/order/func/tooltip + helpers).
    """
    if not os.path.exists(DB_JSON_PATH):
        raise FileNotFoundError(f"DB file not found at {DB_JSON_PATH}. Build it first.")
    with open(DB_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    rows = (data.get("tables", {}) or {}).get(table_name, [])
    if not rows:
        raise RuntimeError(f"Table '{table_name}' not found or empty in DB.")

    required = {"FIELD", "IES_ORDER", "IES_FUNC", "IES_TOOLTIP"}
    missing = [c for c in required if any(c not in r for r in rows)]
    if missing:
        raise RuntimeError(f"Required columns missing in DB rows: {missing}")

    schema: List[Dict[str, Any]] = []
    for r in rows:
        row = {
            "field": str(r.get("FIELD", "")).strip(),
            "order": int(r.get("IES_ORDER") or 0),
            "func":  str(r.get("IES_FUNC", "")).strip(),
            "tooltip": str(r.get("IES_TOOLTIP", "")).strip(),
        }
        if "IES_PROPOSED_KEYWORD" in r:
            row["IES_PROPOSED_KEYWORD"] = r.get("IES_PROPOSED_KEYWORD", "")
        if "IES_PROPOSED" in r:
            row["IES_PROPOSED"] = r.get("IES_PROPOSED", "")

        func_l = row["func"].lower()
        row["derived"]  = (func_l == "derived")
        row["editable"] = (func_l == "editable")
        row["geom_key"] = _geom_key_from_func(row["func"])

        schema.append(row)

    # Stable sort by order then field name
    schema.sort(key=lambda x: (x.get("order") if x.get("order") is not None else 10**9, x.get("field", "")))
    return schema
