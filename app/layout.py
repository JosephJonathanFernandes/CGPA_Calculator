from __future__ import annotations

import streamlit as st

from .config import Theme
from .logic import DEFAULT_CREDITS, DEFAULT_SEM_COUNT, padded_default_credits


def inject_styles(theme: Theme) -> None:
    from .config import global_css

    st.markdown(f"<style>{global_css(theme)}</style>", unsafe_allow_html=True)


def render_header(theme: Theme) -> None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("CGPA Calculator")
        st.caption("Human-centered, transparent CGPA tracking with semester-level insights.")
        st.markdown(
            "<div class='pill'>Balanced workload • Clear feedback • Fast edits</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.metric("Default semesters", DEFAULT_SEM_COUNT, help="Based on GEC Computer curriculum")


def render_inputs() -> tuple[bool, int, int, list[int], list[float]]:
    with st.form("cgpa_form"):
        st.subheader("Setup")
        num_courses = st.number_input(
            "Number of semesters",
            min_value=1,
            max_value=12,
            step=1,
            value=DEFAULT_SEM_COUNT,
            help="Plan for the total semesters in your program.",
        )

        completed_semesters = st.number_input(
            "Semesters with published SGPA",
            min_value=1,
            max_value=num_courses,
            step=1,
            value=num_courses,
            help="Trailing semesters without grades are allowed and ignored in CGPA.",
        )

        use_custom = st.checkbox("Use custom credits", help="Override curriculum defaults per semester.")
        credits: list[int] = []

        if use_custom:
            st.markdown(
                "Enter credits for each semester. Defaults align with GEC Computer curriculum."
            )
            for i in range(num_courses):
                default_value = DEFAULT_CREDITS[i] if i < DEFAULT_SEM_COUNT else DEFAULT_CREDITS[-1]
                credit = st.number_input(
                    f"Sem {i + 1} credits",
                    min_value=0,
                    max_value=35,
                    step=1,
                    value=default_value,
                    key=f"credit_{i}",
                )
                credits.append(credit)
        else:
            credits = padded_default_credits(num_courses)
            st.info(
                f"Using default credits: {', '.join(str(c) for c in credits)}.",
                icon="ℹ️",
            )

        st.markdown("---")
        st.subheader("Enter SGPA")
        grades: list[float] = []
        for i in range(completed_semesters):
            grade = st.number_input(
                f"Sem {i + 1} SGPA",
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                key=f"sgpa_{i}",
            )
            grades.append(grade)

        submitted = st.form_submit_button("Calculate CGPA")
    st.markdown("</div>", unsafe_allow_html=True)

    return submitted, num_courses, completed_semesters, credits, grades


def render_results(
    cgpa: float,
    total_credits: int,
    classification: str,
    breakdown,
    completed_semesters: int,
    num_courses: int,
) -> None:
    st.markdown("---")
    st.subheader("Results")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.markdown("<div class='metric-label'>CGPA</div>", unsafe_allow_html=True)
    col1.markdown(f"<div class='metric-value'>{cgpa:.2f}</div>", unsafe_allow_html=True)

    col2.markdown("<div class='metric-label'>Total credits</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-value'>{total_credits}</div>", unsafe_allow_html=True)

    col3.markdown("<div class='metric-label'>Standing</div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='metric-value'>{classification}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Breakdown")
    st.dataframe(breakdown, width="stretch")

    if completed_semesters < num_courses:
        st.info(
            f"CGPA uses the first {completed_semesters} semester(s). {num_courses - completed_semesters} trailing semester(s) without grades were ignored.",
            icon="ℹ️",
        )

    with st.expander("Visualize SGPA trend"):
        st.bar_chart(breakdown, x="Semester", y="SGPA", width="stretch")

    st.markdown("<div class='footnote'>Tip: Revisit credits when electives change to keep CGPA accurate.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
