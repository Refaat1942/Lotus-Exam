from datetime import datetime
import time
import streamlit as st

from part1_config_and_helpers import load_questions_from_gsheet, QUESTIONS_SHEET_URL
from part2_question_selection_and_validation import (
    validate_candidate_inputs,
    select_questions_for_exam,
)
from gsheets import get_sheet
from branding import page_setup, render_footer

# ✅ تم إزالة الاستدعاء من هنا لتجنب خطأ بدء التشغيل (Startup Error)

QUESTION_TIME_LIMIT = 45  # seconds per question

SHEET_MAP = {
    "Pharmacist (New Hire)": "Pharmacist_New_Hire",
    "Assistant (New Hire)": "Assistant_New_Hire",
    "Proficiency Bonus - Pharmacist": "Proficiency_Bonus_Pharmacist",
    "Proficiency Bonus - Assistant": "Proficiency_Bonus_Assistant",
    "Branch Manager Promotion": "Branch_Manager_Promotion",
    "Shift Manager Promotion": "Shift_Manager_Promotion",
}

# ======================================================
# TOKEN
# ======================================================
def validate_token(token):
    sheet = get_sheet()
    rows = sheet.get_all_records()

    for r in rows:
        if str(r.get("token")).strip() == token:
            
            # التعديل هنا: قراءة الحالة سواء كانت Boolean أو String
            used_status = r.get("used")
            if used_status is True or str(used_status).strip().upper() == "TRUE":
                return False, "❌ This exam link was already used"

            expires_at = datetime.fromisoformat(r.get("expires_at"))
            if datetime.now() > expires_at:
                return False, "❌ This exam link has expired"

            return True, r.get("exam_type")

    return False, "❌ Invalid exam link"


def mark_token_used(token):
    sheet = get_sheet()
    cells = sheet.findall(token)
    if cells:
        sheet.update_cell(cells[0].row, 3, True)


def handle_token_access():
    token = st.query_params.get("token")

    if not token:
        st.error("❌ Access denied.")
        st.stop()

    if st.session_state.get("token_verified"):
        return

    ok, result = validate_token(token)
    if not ok:
        st.error(result)
        st.stop()

    # ❌ تم إزالة mark_token_used من هنا حتى لا يحترق الرابط بمجرد الفتح
    st.session_state.token_verified = True
    st.session_state.exam_type = result
    st.session_state.current_token = token  # حفظ التوكن لحرقه لاحقاً


# ======================================================
# CANDIDATE FORM
# ======================================================
def show_candidate_form():

    handle_token_access()

    page_setup("Candidate Registration")

    st.markdown(
        f"""
        <div class="lx-card">
            <h3 style="margin-bottom:4px;">📝 Candidate Information</h3>
            <p style="color:#5b6b63; margin-top:0;">
                Please fill in your details to begin the
                <b>{st.session_state.get('exam_type', 'assessment')}</b> exam.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("candidate_form"):
        name = st.text_input("Name", placeholder="Full name (letters only)")
        phone = st.text_input("Phone", placeholder="01xxxxxxxxx")
        year = st.text_input("Graduation Year", placeholder="e.g. 2022")
        uni = st.text_input("University", placeholder="Your university")

        submitted = st.form_submit_button("Start Exam", type="primary")

        if submitted:
            ok, msg = validate_candidate_inputs(
                name, phone, year, uni, st.session_state.exam_type
            )
            if not ok:
                st.error(msg)
                return

            # ✅ حرق اللينك يحدث هنا فقط: بعد إدخال البيانات بشكل صحيح وبدء الامتحان
            mark_token_used(st.session_state.current_token)

            st.session_state.user_info = {
                "name": name,
                "phone": phone,
                "year": year,
                "uni": uni,
                "exam_type": st.session_state.exam_type,
            }

            bank = load_questions_from_gsheet(
                QUESTIONS_SHEET_URL,
                SHEET_MAP[st.session_state.exam_type]
            )

            questions, err = select_questions_for_exam(
                st.session_state.exam_type, bank
            )
            if err:
                st.error(err)
                return

            st.session_state.questions = questions
            st.session_state.answers = [None] * len(questions)
            st.session_state.current_q = 0
            st.session_state.start_time = datetime.now()
            st.session_state.question_start_time = datetime.now()
            st.session_state.page = "exam"
            st.rerun()

    render_footer()


# ======================================================
# EXAM
# ======================================================
def show_exam():

    handle_token_access()

    page_setup(f"{st.session_state.get('exam_type', 'Exam')} · In Progress")

    questions = st.session_state.questions
    answers = st.session_state.answers
    q_index = st.session_state.current_q

    if q_index >= len(questions):
        finish_exam()
        return

    q = questions[q_index]
    total = len(questions)

    elapsed = (datetime.now() - st.session_state.question_start_time).seconds
    remaining = QUESTION_TIME_LIMIT - elapsed

    # TIME OUT
    if remaining <= 0:
        if answers[q_index] is None:
            answers[q_index] = -1
        st.session_state.current_q += 1
        st.session_state.question_start_time = datetime.now()
        st.rerun()

    remaining = max(0, remaining)

    # Progress + timer row
    if remaining > 20:
        timer_class = "ok"
    elif remaining > 10:
        timer_class = "warn"
    else:
        timer_class = "danger"

    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown(
            f"<div style='font-family:Poppins;font-weight:600;color:#5b6b63;'>"
            f"Question {q_index + 1} of {total}</div>",
            unsafe_allow_html=True,
        )
    with top_r:
        st.markdown(
            f"<div style='text-align:right;'>"
            f"<span class='lx-timer {timer_class}'>⏱ {remaining}s</span></div>",
            unsafe_allow_html=True,
        )

    st.progress((q_index) / total)

    st.markdown(
        f"""
        <div class="lx-card" style="margin-top:6px;">
            <div style="font-family:'Poppins';font-size:1.15rem;font-weight:600;color:#1f2a24;">
                {q["question"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if answers[q_index] in (None, -1):
        choice = st.radio("Select your answer", q["options"], index=None)
    else:
        choice = st.radio("Select your answer", q["options"], index=answers[q_index])

    if choice is not None:
        answers[q_index] = q["options"].index(choice)

    is_last = (q_index + 1) >= total
    btn_label = "Finish Exam" if is_last else "Next Question →"
    if st.button(btn_label, disabled=answers[q_index] is None, type="primary"):
        st.session_state.current_q += 1
        st.session_state.question_start_time = datetime.now()
        st.rerun()

    time.sleep(1)
    st.rerun()


# ======================================================
# FINISH + RESULT UI
# ======================================================
def finish_exam():
    # ✅ الاستدعاء الآمن جداً لتجنب أي مشاكل
    import part4_admin_and_review

    questions = st.session_state.questions
    answers = st.session_state.answers
    user = st.session_state.user_info

    correct = 0
    category_stats = {} 

    for i, q in enumerate(questions):
        cat = str(q.get("category", "other")).strip().capitalize()
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "correct": 0}
        
        category_stats[cat]["total"] += 1

        if answers[i] in (-1, None):
            continue
        
        correct_ans = str(q.get("answer", ""))
        if not correct_ans:
            continue
            
        if chr(97 + int(answers[i])) == correct_ans[0].lower():
            correct += 1
            category_stats[cat]["correct"] += 1

    breakdown_list = [f"{c}: {s['correct']}/{s['total']}" for c, s in category_stats.items()]
    category_breakdown_str = " | ".join(breakdown_list)

    total = len(questions)
    timed_out = answers.count(-1) + answers.count(None)
    incorrect = total - correct - timed_out
    score = round((correct / total) * 100, 2)
    time_taken = str(datetime.now() - st.session_state.start_time).split('.')[0]

    if not st.session_state.get("exam_finished", False):
        # ✅ استخدام الدالة من الملف المستدعى
        part4_admin_and_review.save_result_files(
            user,
            score,
            correct,
            incorrect, 
            total,
            timed_out, 
            time_taken,
            questions,
            answers,
            category_breakdown_str 
        )
        st.session_state.exam_finished = True

    page_setup("Assessment Complete", show_header=True)

    st.markdown(
        f"""
        <div class="lx-card" style="text-align:center;">
            <div style="font-size:2.6rem;">🎉</div>
            <h2 style="margin:6px 0;">Exam Completed</h2>
            <p style="color:#5b6b63; margin-top:0;">
                Thank you, <b>{user.get('name','')}</b>. Your responses have been recorded.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("🎯 Score %", score)
    c2.metric("✅ Correct", correct)
    c3.metric("⏱ Timed Out", timed_out)

    c4, c5 = st.columns(2)
    c4.metric("❌ Incorrect", incorrect)
    c5.metric("⏳ Time Taken", time_taken)

    st.success("📩 Your result has been saved and sent to HR.")

    render_footer()

    st.stop()