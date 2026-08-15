import os
import smtplib
from email.message import EmailMessage
import pandas as pd
import streamlit as st
from datetime import datetime
from part1_config_and_helpers import ADMIN_PASSWORD, normalize_phone

from gsheets import get_sheet, get_results_sheet
from branding import page_setup, render_footer

RESULTS_FOLDER = "results"
RESULTS_CSV = "results.csv"

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 # تم تغيير البورت إلى 465
SENDER_EMAIL = "ahmedrefat86@gmail.com"
# ⚠️ يرجى استخدام App Password هنا بدلاً من الباسورد الأساسي لضمان عمل الإرسال
SENDER_PASSWORD = "wbkc fyun luvb tdtl" 
RECEIVER_EMAIL = "rana.hafez@lotuspharmacies.com"


# ========================================================
# 1. EMAIL & SAVE FUNCTIONS
# ========================================================

def send_result_email(excel_path, user_info, score, timed_out_count):
    msg = EmailMessage()
    msg["Subject"] = f"📊 Online Exam Result – {user_info['name']}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    msg.set_content(f"""
Name: {user_info['name']}
Phone: {user_info['phone']}
Exam Type: {user_info['exam_type']}

Score: {score}%
Timed Out Questions: {timed_out_count}
""")

    with open(excel_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(excel_path),
        )

    # تم التعديل إلى SMTP_SSL كحل جذري لمشاكل الإرسال
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)


def save_result_files(user_info, score, correct, incorrect, total, timed_out_count, time_taken, questions, answers, category_breakdown_str):

    os.makedirs(RESULTS_FOLDER, exist_ok=True)

    # Create filename with timestamp
    filename = f"{user_info['name'].replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    filepath = os.path.join(RESULTS_FOLDER, filename)

    phone = normalize_phone(user_info.get("phone", ""))

    # 1. تجهيز الداتا لملف الـ Excel
    summary_df = pd.DataFrame([{
        "Name": user_info["name"],
        "Phone": phone,
        "Graduation Year": user_info.get("year", ""),
        "University": user_info["uni"],
        "Exam Type": user_info["exam_type"],
        "Score %": score,
        "Correct": correct,
        "Incorrect": incorrect,
        "Timed Out": timed_out_count,
        "Total": total,
        "Time Taken": time_taken,
        "Category Breakdown": category_breakdown_str,
        "Exam Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])

    details = []
    for i, q in enumerate(questions):
        ans = answers[i]
        
        correct_ans_str = str(q.get("answer", ""))
        correct_index = ord(correct_ans_str[0].lower()) - 97 if correct_ans_str else 0

        row = {
            "Question": q["question"],
            "Category": q.get("category", ""),
            "Difficulty": q.get("difficulty", ""),
        }

        if ans in (-1, None):
            row.update({
                "Candidate Answer": "No Answer",
                "Correct Answer": q["options"][correct_index] if correct_index < len(q["options"]) else "N/A",
                "Result": "Timed Out",
                "Mark": "⏱",
            })
        else:
            row.update({
                "Candidate Answer": q["options"][ans],
                "Correct Answer": q["options"][correct_index] if correct_index < len(q["options"]) else "N/A",
                "Result": "Correct" if ans == correct_index else "Incorrect",
                "Mark": "✓" if ans == correct_index else "✗",
            })

        details.append(row)

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        pd.DataFrame(details).to_excel(writer, sheet_name="Details", index=False)

    # 2. الحفظ في Google Sheets
    try:
        results_sheet = get_results_sheet()
        row_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_info.get("name", ""),
            f"'{phone}" if phone else "",
            user_info.get("year", ""),
            user_info.get("uni", ""),
            user_info.get("exam_type", ""),
            f"{score}%",
            correct,
            incorrect,
            timed_out_count,
            total,
            time_taken,
            category_breakdown_str
        ]
        results_sheet.append_row(row_data)
    except Exception as e:
        st.error(f"❌ Failed to save to Google Sheets: {e}")

    # 3. إرسال الإيميل
    try:
        send_result_email(filepath, user_info, score, timed_out_count)
    except Exception as e:
        st.error(f"❌ Email failed: {e}")

    return filepath


# ========================================================
# 2. ADMIN PANEL
# ========================================================

def show_admin_panel():
    page_setup("Administration Panel")

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.markdown(
            """
            <div class="lx-card">
                <h3 style="margin-bottom:4px;">🔐 Admin Login</h3>
                <p style="color:#5b6b63; margin-top:0;">Enter your password to access exam results.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("admin_login"):
            password = st.text_input("Admin Password", type="password")
            submit = st.form_submit_button("Login", type="primary")

            if submit:
                if password == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect Password")
        render_footer()
        return

    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.success("✅ Logged in as Admin")
    with top_r:
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

    st.markdown("### 📂 Exam Results")

    if not os.path.exists(RESULTS_FOLDER):
        st.warning("No results found yet.")
        return

    files = [f for f in os.listdir(RESULTS_FOLDER) if f.endswith(".xlsx")]
    files.sort(reverse=True)

    if not files:
        st.info("No exam results found.")
    else:
        st.markdown(f"Found **{len(files)}** result files.")
        
        for f in files:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"📄 {f}")
            with col2:
                file_path = os.path.join(RESULTS_FOLDER, f)
                with open(file_path, "rb") as file_data:
                    st.download_button(
                        label="Download",
                        data=file_data,
                        file_name=f,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f
                    )

        st.divider()

    render_footer()