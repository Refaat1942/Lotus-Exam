import json
import os
import tomllib
import streamlit as st
import gspread
import gspread.exceptions
from google.oauth2.service_account import Credentials

# ======================================================
# GOOGLE SHEETS CONFIG
# ======================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_NAME = "lotus_exam_tokens"  # اسم Google Sheet بالظبط


def _load_service_account_info():
    """Load Google credentials from Streamlit secrets or secrets.toml (cron/CLI)."""
    try:
        if "GOOGLE_SERVICE_ACCOUNT" in st.secrets:
            return json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    except Exception:
        pass

    secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        with open(secrets_path, "rb") as f:
            secrets = tomllib.load(f)
        if "GOOGLE_SERVICE_ACCOUNT" in secrets:
            return json.loads(secrets["GOOGLE_SERVICE_ACCOUNT"])

    raise RuntimeError(
        "Google credentials not found. Set GOOGLE_SERVICE_ACCOUNT in .streamlit/secrets.toml"
    )


# ======================================================
# GET SHEET (FROM STREAMLIT SECRETS)
# ======================================================
def get_sheet():
    """
    Reads Google Service Account credentials from Streamlit Secrets
    and returns the first worksheet of the Google Sheet.
    """

    service_account_info = _load_service_account_info()

    creds = Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

# ======================================================
# GET RESULTS SHEET (NEW)
# ======================================================
def get_results_sheet():
    """
    Returns the 'Results' worksheet. Creates it with headers if it doesn't exist.
    """
    service_account_info = _load_service_account_info()
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    client = gspread.authorize(creds)
    doc = client.open(SHEET_NAME)
    
    try:
        # بيحاول يفتح التاب لو موجود
        return doc.worksheet("Results")
    except gspread.exceptions.WorksheetNotFound:
        # لو مش موجود، بيكريته ويحط العناوين الأساسية
        sheet = doc.add_worksheet(title="Results", rows="1000", cols="20")
        headers = [
            "Exam Date", "Name", "Phone", "Graduation Year", "University", 
            "Exam Type", "Score %", "Correct", "Incorrect", "Timed Out", 
            "Total", "Time Taken", "Category Breakdown"
        ]
        sheet.append_row(headers)
        return sheet