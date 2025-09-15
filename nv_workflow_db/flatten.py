from __future__ import annotations
import pandas as pd

# Simple default cleaning rules:
# - Drop completely empty rows
# - Drop columns that are entirely NA
# - Preserve all other columns as-is
def clean_table(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    df2 = df.copy()
    # Drop columns that are entirely NA
    df2 = df2.dropna(axis=1, how="all")
    # Drop rows that are entirely NA
    df2 = df2.dropna(axis=0, how="all")
    return df2

def df_to_rows(df: pd.DataFrame) -> list[dict]:
    if df is None or df.empty:
        return []
    # Convert NaN → None for JSON cleanliness
    return [{k: (None if pd.isna(v) else v) for k, v in row.items()} for row in df.to_dict(orient="records")]
