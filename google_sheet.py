import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def get_gsheet_client():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=SCOPES,
    )
    return gspread.authorize(creds)

def get_spreadsheet():
    gc = get_gsheet_client()
    return gc.open_by_key(st.secrets["spreadsheet_id"])

def get_worksheet(name: str):
    return get_spreadsheet().worksheet(name)

def worksheet_to_df(name: str) -> pd.DataFrame:
    ws = get_worksheet(name)
    records = ws.get_all_records()
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)

def get_note(user_id: str, category: str) -> str:
    df = worksheet_to_df("notes")
    if df.empty:
        return ""
    matched = df[(df["user_id"] == user_id) & (df["category"] == category)]
    if matched.empty:
        return ""
    return str(matched.iloc[0]["content"])

def save_note(user_id: str, category: str, content: str):
    ws = get_worksheet("notes")
    records = ws.get_all_records()

    for i, row in enumerate(records, start=2):  # header 在第1列
        if row.get("user_id") == user_id and row.get("category") == category:
            ws.update(f"C{i}:D{i}", [[content, now_iso()]])
            return

    ws.append_row([user_id, category, content, now_iso()])

def get_progress(user_id: str) -> dict:
    df = worksheet_to_df("progress")
    if df.empty:
        return {}

    df = df[df["user_id"] == user_id]
    result = {}
    for _, row in df.iterrows():
        result[str(row["key"])] = str(row["done"]).lower() in ("true", "1", "yes")
    return result

def save_progress(user_id: str, key: str, done: bool):
    ws = get_worksheet("progress")
    records = ws.get_all_records()

    for i, row in enumerate(records, start=2):
        if row.get("user_id") == user_id and row.get("key") == key:
            ws.update(f"C{i}:D{i}", [[str(done), now_iso()]])
            return

    ws.append_row([user_id, key, str(done), now_iso()])