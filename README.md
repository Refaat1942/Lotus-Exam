# Lotus Evaluation Platform

An elegant, web-based talent assessment & recruitment exam system for Lotus Pharmacies,
built with [Streamlit](https://streamlit.io/).

Live: http://187.124.15.14:5050/

## Features

- **HR Portal** — generate secure, time-limited, single-use exam links per candidate.
- **Candidate Exam** — validated registration, per-question countdown timer, randomized
  question selection by category, and instant scoring.
- **Admin Panel** — password-protected access to downloadable result files.
- **Automation** — results saved to Google Sheets, emailed to HR, plus a weekly report.
- **Branded UI** — modern, responsive interface with automatic logo detection.

## Project Structure

| File | Purpose |
|------|---------|
| `app.py` | Entry point & routing (home / exam / admin) |
| `branding.py` | Shared theme, CSS, header, and logo handling |
| `home_page.py` | HR link generation page |
| `part1_config_and_helpers.py` | Config, question loading & cleaning helpers |
| `part2_question_selection_and_validation.py` | Exam rules & candidate validation |
| `part3_exam_flow.py` | Token handling, candidate form, exam & results |
| `part4_admin_and_review.py` | Result saving/email + admin panel |
| `gsheets.py` | Google Sheets connection |
| `weekly_report.py` | Weekly results report emailer |

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Add your logo (optional): drop `logo.png` into the `assets/` folder.

3. Configure secrets: copy `.streamlit/secrets.toml.example` to
   `.streamlit/secrets.toml` and paste your Google service-account JSON.

4. Run:

   ```bash
   streamlit run app.py
   ```

## Access

- Home / HR portal: `/`
- Candidate exam: `/?token=XXXXXXXX`
- Admin panel: `/?admin`

## Notes

Per-question time limit and exam composition rules are defined in
`part3_exam_flow.py` and `part2_question_selection_and_validation.py`.
