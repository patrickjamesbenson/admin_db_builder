from __future__ import annotations
import os, json
import streamlit as st

from nv_workflow_db import build_and_write
from nv_workflow_db.config import DEFAULT_SHEET_ID, DEFAULT_WORKSHEET, DEFAULT_CSV_URL, BASE_MAJOR, BASE_MINOR
from nv_workflow_db.paths import DB_JSON_PATH

st.set_page_config(page_title="Nervon Workflow DB", layout="wide")
st.title("Nervon Workflow Database — Builder")

with st.expander("Current config & how to change it", expanded=True):
    st.write("**Where are we loading from?**")
    st.code(
        f"NV_SHEET_ID={DEFAULT_SHEET_ID!r}\nNV_WORKSHEET={DEFAULT_WORKSHEET!r}\nNV_CSV_URL={DEFAULT_CSV_URL!r}\nBASE_MAJOR={BASE_MAJOR} BASE_MINOR={BASE_MINOR}",
        language="bash",
    )
    st.write("Change them via environment variables or Streamlit secrets.")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Rebuild DB now", type="primary"):
        try:
            if DEFAULT_CSV_URL:
                path = build_and_write(csv_url=DEFAULT_CSV_URL, csv_alias=(DEFAULT_WORKSHEET or "sheet"), base_major=BASE_MAJOR, base_minor=BASE_MINOR)
            elif DEFAULT_SHEET_ID and DEFAULT_WORKSHEET:
                path = build_and_write(sheet_id=DEFAULT_SHEET_ID, worksheets=[DEFAULT_WORKSHEET], base_major=BASE_MAJOR, base_minor=BASE_MINOR)
            else:
                st.error("Set NV_SHEET_ID & NV_WORKSHEET (service account) or NV_CSV_URL (public CSV).")
                st.stop()
            st.success(f"Wrote {path}")
        except Exception as e:
            st.exception(e)

with col2:
    st.write("**Output file**")
    st.code(DB_JSON_PATH, language="bash")

st.divider()
st.subheader("Preview")
try:
    with open(DB_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    st.json(data.get("_meta", {}))
    tabs = data.get("tables", {})
    if not tabs:
        st.info("No tables found yet. Press **Rebuild DB now**.")
    else:
        for name, rows in tabs.items():
            st.markdown(f"### Table: `{name}`  — {len(rows)} rows")
            st.dataframe(rows)
except FileNotFoundError:
    st.info("No DB file found yet. Press **Rebuild DB now**.")
except Exception as e:
    st.exception(e)
