import streamlit as st
import random
import string
from datetime import datetime, timedelta
from gsheets import get_sheet
from branding import page_setup, render_footer, PRIMARY, PRIMARY_DARK

# Ensure this is the correct URL for your server
APP_BASE_URL = "http://187.124.15.14:5050"

EXAM_TYPES = [
    "Pharmacist (New Hire)",
    "Assistant (New Hire)",
    "Beauty Advisor",
    "Proficiency Bonus - Pharmacist",
    "Proficiency Bonus - Assistant",
    "Branch Manager Promotion",
    "Shift Manager Promotion",
]

# ======================================================
# GENERATE TOKEN (SHORT CODE)
# ======================================================
def generate_exam_token(exam_type, minutes_valid, generated_by):
    sheet = get_sheet()
    # Generate a short, unique 8-character token
    token = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    expires_at = datetime.now() + timedelta(minutes=minutes_valid)

    sheet.append_row([
        token,
        exam_type,
        False, # used status
        expires_at.isoformat(),
        generated_by
    ])
    return token


# ======================================================
# HOME PAGE
# ======================================================
def show_home_page():
    page_setup("HR Portal · Generate Candidate Exam Links")

    st.markdown(
        """
        <div class="lx-card">
            <h3 style="margin-bottom:4px;">🔗 Generate Exam Link</h3>
            <p style="color:#5b6b63; margin-top:0;">
                Create a secure, time-limited exam link for a candidate.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hr_name = st.text_input("HR Name", placeholder="Enter your name")
    exam_type = st.selectbox("Exam Type", EXAM_TYPES)
    minutes = st.number_input(
        "Link Validity (Minutes)", min_value=5, max_value=180, value=30
    )

    if st.button("Generate Link Now", type="primary"):
        if not hr_name.strip():
            st.warning("⚠️ Please enter HR name first")
            return

        # Generate token and link
        token = generate_exam_token(
            exam_type=exam_type,
            minutes_valid=minutes,
            generated_by=hr_name.strip()
        )
        exam_link = f"{APP_BASE_URL}?token={token}"

        st.success("✅ Exam link generated successfully!")

        # 1. Direct Open Button (Clickable)
        st.link_button("🚀 Open Exam Directly", exam_link, type="primary")

        st.divider()

        # 2. Professional Copy Button (HTML/JS for HTTP compatibility)
        copy_html = f"""
        <div style="display:flex; align-items:center; gap:10px; font-family:'Inter',sans-serif;
                    background:#ffffff; padding:16px; border-radius:14px;
                    border:1px solid rgba(31,122,77,0.12); box-shadow:0 8px 22px rgba(20,92,57,0.06);">
            <input type="text" id="linkInput" value="{exam_link}" readonly
                   style="padding:11px 12px; flex-grow:1; border:1px solid #e2e8e5; border-radius:10px; font-size:14px; color:#1f2a24;">
            <button onclick="copyLink()"
                    style="padding:11px 20px; background:linear-gradient(135deg,{PRIMARY} 0%,{PRIMARY_DARK} 100%);
                           color:white; border:none; border-radius:10px; cursor:pointer; font-weight:600; white-space:nowrap;
                           box-shadow:0 8px 18px rgba(20,92,57,0.25);">
                📋 Copy Link
            </button>
            <span id="msg" style="color:{PRIMARY_DARK}; display:none; font-size:14px; font-weight:600;">✔ Copied!</span>
        </div>
        <script>
        function copyLink() {{
            var copyText = document.getElementById("linkInput");
            copyText.select();
            copyText.setSelectionRange(0, 99999);
            document.execCommand("copy");
            var msg = document.getElementById("msg");
            msg.style.display = "inline";
            setTimeout(function() {{ msg.style.display = "none"; }}, 2000);
        }}
        </script>
        """
        st.components.v1.html(copy_html, height=90)

        st.info("💡 Use **Open Exam Directly** to launch now, or **Copy Link** to send it to the candidate.")

    render_footer()