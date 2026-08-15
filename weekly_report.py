import os
import pandas as pd
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

from gsheets import get_results_sheet
from part1_config_and_helpers import normalize_phone

REPORT_VERSION = "2026-08-15-dedup-v2"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "ahmedrefat86@gmail.com"
SENDER_PASSWORD = "wbkc fyun luvb tdtl"
OWNER_EMAIL = "hashem.saad@lotuspharmacies.com"


def send_weekly_report():
    print(f"Starting weekly report... ({REPORT_VERSION})")

    try:
        sheet = get_results_sheet()
        records = sheet.get_all_records()
    except Exception as e:
        print(f"Google Sheets error: {e}")
        return

    if not records:
        print("No data to send.")
        return

    df = pd.DataFrame(records)
    df.columns = df.columns.str.strip()

    df["Exam Date"] = pd.to_datetime(df["Exam Date"])
    last_week = datetime.now() - timedelta(days=7)
    weekly_data = df[df["Exam Date"] >= last_week].copy()

    if weekly_data.empty:
        print("No exams in the last 7 days.")
        return

    rows_before = len(weekly_data)
    if "Phone" in weekly_data.columns:
        weekly_data["_phone_key"] = weekly_data["Phone"].map(normalize_phone)
        weekly_data = (
            weekly_data
            .sort_values("Exam Date")
            .drop_duplicates(subset="_phone_key", keep="last")
            .sort_values("Exam Date", ascending=False)
            .reset_index(drop=True)
        )
        weekly_data["Phone"] = weekly_data["_phone_key"].where(
            weekly_data["_phone_key"] != "",
            weekly_data["Phone"].astype(str).str.strip(),
        )
        weekly_data = weekly_data.drop(columns=["_phone_key"])

    rows_after = len(weekly_data)
    print(f"Rows this week: {rows_before} -> after dedup: {rows_after}")

    total_exams = len(weekly_data)
    weekly_data["Exam Date"] = weekly_data["Exam Date"].dt.strftime("%Y-%m-%d %H:%M")

    report_filename = f"Weekly_Report_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    weekly_data.to_excel(report_filename, index=False, engine="openpyxl")

    msg = EmailMessage()
    msg["Subject"] = f"📊 التقرير الأسبوعي لنتائج الامتحانات - {datetime.now().strftime('%Y-%m-%d')}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = OWNER_EMAIL
    msg.set_content(f"""
أهلاً بك،

مرفق طيه التقرير الأسبوعي لنتائج امتحانات التقييم والتوظيف.

📌 ملخص هذا الأسبوع:
- إجمالي عدد الامتحانات المجراة: {total_exams} امتحان.

برجاء الاطلاع على ملف الإكسيل المرفق لمعرفة أسماء الممتحنين، التقييمات، وتفاصيل النتائج (الإجابات الصحيحة والخاطئة والوقت المستغرق).

تحياتي،
نظام الامتحانات الآلي
""")

    with open(report_filename, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=report_filename,
        )

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("Weekly report sent successfully.")
    except Exception as e:
        print(f"Email send failed: {e}")
    finally:
        if os.path.exists(report_filename):
            os.remove(report_filename)


if __name__ == "__main__":
    send_weekly_report()
