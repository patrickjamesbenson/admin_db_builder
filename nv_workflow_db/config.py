from __future__ import annotations
import os

# Defaults (can be overridden by env vars or Streamlit secrets)
DEFAULT_SHEET_ID   = os.environ.get("NV_SHEET_ID", "")
DEFAULT_WORKSHEET  = os.environ.get("NV_WORKSHEET", "master_metadata_console")
DEFAULT_CSV_URL    = os.environ.get("NV_CSV_URL", "")  # if using public CSV export instead
GOOGLE_SA_JSON     = os.environ.get("GOOGLE_SA_JSON", "service_account.json")

# Optional "semantic-ish" labels base
BASE_MAJOR = int(os.environ.get("NV_BASE_MAJOR", "1"))
BASE_MINOR = int(os.environ.get("NV_BASE_MINOR", "0"))

# Which sheets to include. By default, just the PRIMARY worksheet.
# You can pass a list when calling build() to include more later.
INCLUDE_SHEETS = [DEFAULT_WORKSHEET] if DEFAULT_WORKSHEET else []
