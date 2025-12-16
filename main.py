from app.config import Theme
from app.layout import inject_styles, render_header, render_inputs, render_results
from app.logic import build_breakdown, classify_cgpa, compute_cgpa

import streamlit as st


st.set_page_config(page_title="CGPA Calculator", layout="centered")

theme = Theme()
inject_styles(theme)
render_header(theme)

submitted, num_courses, completed_semesters, credits, grades = render_inputs()

if submitted:
    effective_credits = credits[:completed_semesters]
    effective_grades = grades[:completed_semesters]
    cgpa = compute_cgpa(effective_grades, effective_credits)

    if cgpa is None:
        st.error("Unable to compute CGPA. Check credits and SGPA entries.")
    else:
        total_credits = sum(effective_credits)
        classification = classify_cgpa(cgpa)
        breakdown = build_breakdown(completed_semesters, effective_credits, effective_grades)
        render_results(
            cgpa,
            total_credits,
            classification,
            breakdown,
            completed_semesters,
            num_courses,
        )

st.markdown("---")
gdrive_link = "https://drive.google.com/file/d/1JyIgnGSZpeBphGtcoDdaj8eXnVvROFb8/view?usp=drivesdk"
st.markdown(f"[View CGPA Calculation Guide]({gdrive_link})")

st.caption("Built for quick academic tracking.")