import streamlit as st
from branding import _find_logo

# ======================================================
# PAGE CONFIG
# ======================================================
_logo_path = _find_logo()
st.set_page_config(
    page_title="Lotus Evaluation Platform",
    page_icon=_logo_path if _logo_path else "\U0001F337",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ======================================================
# SESSION INIT
# ======================================================
def init_session():
    defaults = {
        "page": "home",
        "exam_finished": False,
        "questions": [],
        "answers": [],
        "current_q": 0,
        "result_row_dict": {},
        "review_mode": False,
        "start_time": None,
        "token_verified": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ======================================================
# SAFE IMPORTS
# ======================================================
from home_page import show_home_page
from part3_exam_flow import (
    show_candidate_form,
    show_exam,
)

# ❌ لا يوجد show_exam_result في المشروع
# ❌ لا نستورد admin هنا (Lazy فقط)

# ======================================================
# ROUTING
# ======================================================
def main():

    params = st.query_params

    # 🔐 Admin access
    if "admin" in params:
        st.session_state.page = "admin"

    # 🧪 Exam access
    elif "token" in params:
        st.session_state.page = "exam"

    else:
        st.session_state.page = "home"

    # ================= PAGE SWITCH =================
    if st.session_state.page == "home":
        show_home_page()

    elif st.session_state.page == "exam":
        if not st.session_state.questions:
            show_candidate_form()
        else:
            show_exam()

    elif st.session_state.page == "admin":
        from part4_admin_and_review import show_admin_panel
        show_admin_panel()

# ======================================================
# RUN
# ======================================================
if __name__ == "__main__":
    main()
