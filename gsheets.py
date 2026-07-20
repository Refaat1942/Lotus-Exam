import json
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


# ======================================================
# GET SHEET (FROM STREAMLIT SECRETS)
# ======================================================
def get_sheet():
    """
    Reads Google Service Account credentials from Streamlit Secrets
    and returns the first worksheet of the Google Sheet.
    """

    service_account_info = json.loads(
        st.secrets["GOOGLE_SERVICE_ACCOUNT"]
    )

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
    service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
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