import re
import random
from typing import List, Dict
from part1_config_and_helpers import clean_text

# ===========================================================
# VALIDATION
# ===========================================================

def validate_candidate_inputs(name: str, phone: str, year: str, uni: str, exam_type: str):
    if not re.match(r"^[A-Za-z ]+$", name.strip()):
        return False, "Name must contain only letters."
    if not re.match(r"^(010|011|012|015)\d{8}$", phone.strip()):
        return False, "Phone must be 11 digits and start with 010/011/012/015."
    if not re.match(r"^\d{4}$", year.strip()):
        return False, "Graduation Year must be 4 digits."
    if not re.match(r"^[A-Za-z0-9 ]+$", uni.strip()):
        return False, "University must contain only letters and numbers."
    if not exam_type:
        return False, "Please choose an Exam Type."
    return True, ""

# ===========================================================
# NEW EXAM RULES (UPDATED LOGIC)
# ===========================================================

EXAM_RULES = {
    "Pharmacist (New Hire)": {
        "total": 20,
        "categories": {"drug": 15, "cosmetics": 5},
    },
    "Assistant (New Hire)": {
        "total": 20,
        "categories": {"assistant": 20},
    },
    "Beauty Advisor": {
        "total": 25,
        "categories": {"cosmetics": 25},
    },
    "Proficiency Bonus - Pharmacist": {
        "total": 30,
        "categories": {"drug": 15, "cosmetics": 15},
    },
    "Proficiency Bonus - Assistant": {
        "total": 30,
        "categories": {"assistant": 30},
    },
    "Branch Manager Promotion": {
        "total": 30,
        "categories": {"drug": 15, "cosmetics": 15},
    },
    "Shift Manager Promotion": {
        "total": 30,
        "categories": {"drug": 15, "cosmetics": 15},
    },
}

# ===========================================================
# BUILD CATEGORY POOL
# ===========================================================

def build_category_pool(bank: List[Dict], cat_name: str):
    items = {}
    for q in bank:
        cat = str(q.get("category", "")).strip().lower()
        if cat != cat_name:
            continue
        key = q.get("qtext_clean") or clean_text(q.get("question", ""))
        if not key or key in items:
            continue
        q_copy = q.copy()
        items[key] = q_copy
    return list(items.values())

# ===========================================================
# MAIN: SELECT QUESTIONS FOR EXAM
# ===========================================================

def select_questions_for_exam(exam_type: str, bank: List[Dict]):

    if exam_type not in EXAM_RULES:
        return [], f"No rules defined for exam type: {exam_type}"

    rules = EXAM_RULES[exam_type]
    total_required = rules["total"]
    categories_rules = rules["categories"]

    final_questions = []

    for cat_name, count in categories_rules.items():
        pool = build_category_pool(bank, cat_name)
        
        if len(pool) < count:
            return [], f"Not enough questions in category '{cat_name}'. Found {len(pool)}, needed {count}."

        # اختيار عشوائي للأسئلة مما يحقق عشوائية في اختيار درجات الصعوبة
        random.shuffle(pool)
        selected = pool[:count]
        
        final_questions.extend(selected)

    # خلط الأسئلة النهائية عشان متبقاش الأسئلة مترتبة ورا بعض بناءً على القسم
    random.shuffle(final_questions)

    return final_questions[:total_required], ""