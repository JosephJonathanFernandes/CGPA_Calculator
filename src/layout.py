# src/layout.py
"""
Streamlit UI layout for CGPA Calculator (modular, clean, secure, HCD-focused).
Enhanced with Human-Centered Design principles for optimal user experience.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
from .config import Theme, global_css
from .logic import (
    DEFAULT_CREDITS,
    DEFAULT_SEM_COUNT,
    GRADE_POINT_MAP,
    consistency_score,
    grade_letter_to_point,
    predict_final_cgpa_range,
    semester_trend_slope,
    strongest_weakest_semester,
    what_if_simulator,
)

def inject_styles(theme: Theme) -> None:
    """Inject enhanced CSS styling with HCD principles."""
    st.markdown(f"<style>{global_css(theme)}{enhanced_css(theme)}</style>", unsafe_allow_html=True)

def enhanced_css(theme: Theme) -> str:
    """Return enhanced CSS with HCD principles: accessibility, visual hierarchy, and micro-interactions."""
    return f"""
    /* Enhanced typography and spacing */
    .stTextInput, .stNumberInput, .stCheckbox {{
        margin-bottom: 1.2rem !important;
    }}

    /* Pill styling with smooth transitions */
    .pill {{
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1.2rem;
        background: linear-gradient(90deg, #e0f2fe 0%, #bae6fd 100%);
        border: 2px solid {theme.primary};
        border-radius: 2rem;
        font-size: 1.08rem;
        font-weight: 700;
        color: #0b1221;
        text-shadow: none;
        letter-spacing: 0.01em;
        box-shadow: 0 2px 12px 0 rgba(37,99,235,0.10);
        backdrop-filter: blur(2px);
        transition: all 0.3s ease;
        margin-top: 0.5rem;
    }}

    .pill:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px {theme.primary}33;
    }}

    /* Enhanced glass card effect */
    .glass-card {{
        background: var(--card) !important;
        color: var(--text) !important;
        border: 1.5px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.10);
        transition: all 0.3s ease;
    }}

    .stForm {{
        background: var(--card) !important;
        color: var(--text) !important;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
    }}

    .glass-card:hover {{
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
    }}

    /* Metric styling with visual hierarchy */
    .metric-label {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {theme.muted};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }}

    .metric-value {{
        font-size: clamp(1.1rem, 2.2vw, 2rem);
        font-weight: 800;
        color: var(--text);
        background: var(--surface);
        padding: 0.5rem 1rem;
        border-radius: 12px;
        display: block;
        max-width: 100%;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: break-word;
        box-shadow: 0 2px 8px rgba(37,99,235,0.08);
        transition: all 0.3s ease;
    }}

    .glass-card td {{
        overflow-wrap: anywhere;
        word-break: break-word;
        vertical-align: top;
    }}

    .metric-value:hover {{
        transform: scale(1.05);
        box-shadow: 0 4px 12px {theme.primary}33;
    }}

    /* Footnote styling */
    .footnote {{
        font-size: 0.75rem;
        color: {theme.muted};
        font-style: italic;
        margin-top: 1.5rem;
        padding: 0.75rem;
        background: {theme.card};
        border-left: 3px solid {theme.primary};
        border-radius: 0 8px 8px 0;
    }}

    /* Enhanced button styling */
    .stButton>button {{
        background: linear-gradient(135deg, {theme.primary} 0%, {theme.primary_dark} 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px {theme.primary}33;
    }}

    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 15px {theme.primary}44;
    }}

    .stButton>button:active {{
        transform: translateY(0);
    }}

    /* Accessibility enhancements */
    input:focus, textarea:focus, select:focus {{
        outline: 2px solid {theme.primary} !important;
        outline-offset: 2px;
    }}

    /* Responsive design */
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 1rem !important;
        }}
        .metric-value {{
            font-size: 1.5rem;
            padding: 0.3rem 0.7rem;
        }}
        .glass-card table,
        .glass-card tbody,
        .glass-card tr,
        .glass-card td {{
            display: block;
            width: 100% !important;
        }}
        .glass-card tr {{
            margin-bottom: 0.5rem;
        }}
        .glass-card td {{
            text-align: left !important;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.8rem;
            margin-bottom: 0.6rem;
            background: var(--card);
        }}
    }}

    @media (max-width: 480px) {{
        .block-container {{
            padding-left: 0.55rem !important;
            padding-right: 0.55rem !important;
            padding-top: 0.75rem !important;
        }}
        h1 {{
            font-size: 1.6rem !important;
            line-height: 1.2 !important;
        }}
        h2 {{
            font-size: 1.25rem !important;
            line-height: 1.25 !important;
        }}
        h3 {{
            font-size: 1.05rem !important;
        }}
        .stButton > button {{
            padding: 0.6rem 0.85rem !important;
            font-size: 0.9rem !important;
            border-radius: 10px !important;
        }}
        .stTextInput, .stNumberInput, .stCheckbox {{
            margin-bottom: 0.75rem !important;
        }}
        .glass-card {{
            padding: 1rem !important;
            border-radius: 12px !important;
        }}
        .stForm {{
            padding: 1rem !important;
            border-radius: 12px !important;
        }}
        .metric-label {{
            font-size: 0.75rem !important;
        }}
        .metric-value {{
            font-size: 1.2rem !important;
            padding: 0.3rem 0.55rem !important;
        }}
    }}
    """

def render_header(theme: Theme, title: str = "CGPA Calculator") -> None:
    """Render enhanced header with HCD principles."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(title)
   
    with col2:
        st.metric("Default semesters", DEFAULT_SEM_COUNT)

def render_inputs(initial_state: dict | None = None) -> tuple[bool, int, int, list[int], list[float]]:
    """Render enhanced input form with HCD principles."""
    initial_state = initial_state or {}

    # Apply reset before creating widgets to avoid Streamlit session-state mutation errors.
    if st.session_state.get("cgpa_reset_requested", False):
        st.session_state["cgpa_num_courses"] = DEFAULT_SEM_COUNT
        st.session_state["cgpa_completed_semesters"] = DEFAULT_SEM_COUNT
        st.session_state["cgpa_use_custom"] = False
        for i in range(12):
            default_credit = DEFAULT_CREDITS[i] if i < DEFAULT_SEM_COUNT else DEFAULT_CREDITS[-1]
            st.session_state[f"credit_{i}"] = int(default_credit)
            st.session_state[f"sgpa_{i}"] = 8.0
        st.session_state["cgpa_reset_requested"] = False

    if "cgpa_num_courses" not in st.session_state:
        st.session_state["cgpa_num_courses"] = int(initial_state.get("num_courses", DEFAULT_SEM_COUNT))
    if "cgpa_completed_semesters" not in st.session_state:
        st.session_state["cgpa_completed_semesters"] = int(initial_state.get("completed_semesters", st.session_state["cgpa_num_courses"]))
    if "cgpa_use_custom" not in st.session_state:
        st.session_state["cgpa_use_custom"] = bool(initial_state.get("use_custom", False))

    initial_credits = initial_state.get("credits", [])
    initial_grades = initial_state.get("grades", [])
    for i in range(12):
        c_key = f"credit_{i}"
        if c_key not in st.session_state:
            if i < len(initial_credits):
                st.session_state[c_key] = int(initial_credits[i])
            else:
                st.session_state[c_key] = int(DEFAULT_CREDITS[i] if i < DEFAULT_SEM_COUNT else DEFAULT_CREDITS[-1])
        
        g_key = f"sgpa_{i}"
        if g_key not in st.session_state:
            if i < len(initial_grades):
                st.session_state[g_key] = float(initial_grades[i])
            else:
                st.session_state[g_key] = 7.0 if st.session_state["cgpa_use_custom"] else 8.0

    st.subheader("Academic Profile")
    st.caption("Need subject-wise calculation first? Open SGPA Calculator.")

    # Keep dynamic controls outside the form so UI updates immediately.
    num_courses = int(st.number_input(
        "Number of semesters",
        min_value=1,
        max_value=12,
        step=1,
        key="cgpa_num_courses",
        help="Total semesters in your program.",
    ))

    completed_semesters = int(st.number_input(
        "Completed semesters",
        min_value=1,
        max_value=num_courses,
        step=1,
        key="cgpa_completed_semesters",
        help="Semesters with final SGPA available.",
    ))

    if completed_semesters > num_courses:
        completed_semesters = num_courses
        st.session_state["cgpa_completed_semesters"] = num_courses

    st.markdown("---")
    use_custom = st.checkbox(
        "Use custom credits",
        help="Enable if your semesters have non-standard credits.",
        key="cgpa_use_custom",
    )

    with st.form("cgpa_form", clear_on_submit=False):
        credits: list[int] = []
        grades: list[float] = []
        if use_custom:
            st.markdown("### Semester Details")
            for i in range(num_courses):
                col1, col2 = st.columns(2)
                with col1:
                    credit = st.number_input(
                        f"Semester {i + 1} Credits",
                        min_value=0,
                        max_value=35,
                        step=1,
                        key=f"credit_{i}",
                    )
                    credits.append(int(credit))
                with col2:
                    if i < completed_semesters:
                        grade = st.number_input(
                            f"Semester {i + 1} SGPA",
                            min_value=0.0,
                            max_value=10.0,
                            step=0.01,
                            key=f"sgpa_{i}",
                        )
                        grades.append(float(grade))
                    else:
                        st.markdown("<div style='margin-top: 2.8rem; color: var(--muted); text-align: center; font-size: 0.9rem;'>Not completed</div>", unsafe_allow_html=True)
        else:
            for i in range(num_courses):
                credits.append(st.session_state[f"credit_{i}"])
            
            st.markdown("### SGPA")
            for i in range(0, completed_semesters, 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < completed_semesters:
                        with cols[j]:
                            grade = st.number_input(
                                f"Semester {i + j + 1} SGPA",
                                min_value=0.0,
                                max_value=10.0,
                                step=0.01,
                                key=f"sgpa_{i+j}",
                            )
                            grades.append(float(grade))

        submitted = st.form_submit_button(
            "Calculate CGPA",
        )
        clear_clicked = st.form_submit_button(
            "Clear",
            type="secondary",
        )

    if clear_clicked:
        st.session_state["cgpa_clear_pending"] = True

    if st.session_state.get("cgpa_clear_pending", False):
        st.warning("Clear all CGPA inputs? This action will reset your current entries.")
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("Confirm", key="cgpa_confirm_clear", use_container_width=True):
                st.session_state["cgpa_reset_requested"] = True
                if "cgpa_state" in st.query_params:
                    del st.query_params["cgpa_state"]
                st.session_state["cgpa_clear_pending"] = False
                st.toast("CGPA inputs cleared.", icon="🗑️")
                st.rerun()
        with col_cancel:
            if st.button("Cancel", key="cgpa_cancel_clear", use_container_width=True):
                st.session_state["cgpa_clear_pending"] = False
                st.rerun()

    return submitted, num_courses, completed_semesters, credits, grades

def render_results(
    cgpa: float,
    percentage: float,
    total_credits: int,
    classification: str,
    breakdown,
    completed_semesters: int,
    num_courses: int,
    all_credits: list[int],
    settings: dict | None = None,
) -> None:
    """Render enhanced results with HCD principles."""
    st.markdown("---")
    st.subheader("Results")


    classification_color = get_classification_color(classification)
    us_gpa = (cgpa / 10.0) * 4.0
    st.markdown(f"""
<div class='glass-card'>
    <table style='width:100%;table-layout:fixed;text-align:center;border-collapse:separate;border-spacing:0.5rem 0;'>
        <tr>
            <td>
                <div class='metric-label'>CGPA</div>
                <div class='metric-value'>{cgpa:.2f}</div>
            </td>
            <td>
                <div class='metric-label'>US GPA</div>
                <div class='metric-value'>{us_gpa:.2f}</div>
            </td>
            <td>
                <div class='metric-label'>Percentage</div>
                <div class='metric-value'>{percentage:.2f}%</div>
            </td>
            <td>
                <div class='metric-label'>Credits</div>
                <div class='metric-value'>{total_credits}</div>
            </td>
            <td>
                <div class='metric-label'>Standing</div>
                <div class='metric-value' style='background: {classification_color}22; border: 2px solid {classification_color}; font-size: 0.9rem;'>{classification}</div>
            </td>
        </tr>
    </table>
</div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    weighted_sum = float(breakdown["Weighted"].sum()) if not breakdown.empty else 0.0
    
    settings = settings or {}
    cgpa_method = settings.get("cgpa_method", "weighted")
    pct_formula = settings.get("pct_formula", "mu")

    cgpa_formula_str = r"$CGPA = \frac{\sum(SGPA_i \times Credits_i)}{\sum(Credits_i)}$" if cgpa_method == "weighted" else r"$CGPA = \frac{\sum(SGPA_i)}{n_{semesters}}$"
    pct_formula_str = r"$(CGPA - 0.75) \times 10$" if pct_formula == "mu" else (r"$CGPA \times 9.5$" if pct_formula == "cbse" else r"$CGPA \times 10$")

    with st.expander("How it's calculated"):
        st.markdown(f"""
        **CGPA Formula**

        {cgpa_formula_str}

        **Your values**

        - Total weighted score: {weighted_sum:.2f}
        - Total credits: {total_credits}
        - Final CGPA: {cgpa:.2f}
        - Percentage: {percentage:.2f}% (using {pct_formula_str})
        - US GPA Equivalent: {us_gpa:.2f} (using $(CGPA \\div 10) \\times 4.0$)
        """)

    st.subheader("Semester Breakdown")
    st.dataframe(
        breakdown,
        width="stretch",
        height=300
    )

    if not breakdown.empty:
        csv_data = breakdown.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Breakdown (CSV)",
            data=csv_data,
            file_name='semester_breakdown.csv',
            mime='text/csv',
        )

    if completed_semesters < num_courses:
        remaining_semesters = num_courses - completed_semesters
        st.info(
            f"Based on first {completed_semesters} semester(s). {remaining_semesters} semester(s) remaining.",
        )

    with st.expander("Trend"):
        if not breakdown.empty:
            fig = px.bar(
                breakdown,
                x="Semester",
                y="SGPA",
                text="SGPA",
                color="SGPA",
                color_continuous_scale="Blues",
                labels={"SGPA": "SGPA Score"},
                height=400
            )
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(
                xaxis_title="Semester",
                yaxis_title="SGPA",
                showlegend=False,
                margin=dict(l=0, r=0, t=30, b=0),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if len(breakdown) > 1:
                slope = semester_trend_slope(breakdown['SGPA'].tolist())
                trend_text = "Improving" if slope > 0.05 else ("Declining" if slope < -0.05 else "Stable")
                st.caption(f"Trend: **{trend_text}**")

    sgpa_series = breakdown["SGPA"].tolist() if not breakdown.empty else []
    slope = semester_trend_slope(sgpa_series)
    consistency = consistency_score(sgpa_series)
    extreme_meta = strongest_weakest_semester(sgpa_series)

    st.subheader("Analytics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Trend slope", f"{slope:+.3f}")
    with col2:
        st.metric("Consistency score", f"{consistency:.1f}/100")
    with col3:
        st.metric(
            "Strongest / Weakest",
            f"S{extreme_meta['strongest_semester']} / S{extreme_meta['weakest_semester']}",
            help=f"Best SGPA: {extreme_meta['strongest_sgpa']:.2f}, Worst SGPA: {extreme_meta['weakest_sgpa']:.2f}",
        )

    if completed_semesters < num_courses:
        remaining_credits = sum(all_credits[completed_semesters:])
        projection = predict_final_cgpa_range(
            current_grades=sgpa_series,
            current_credits=all_credits[:completed_semesters],
            remaining_credits=remaining_credits,
        )
        what_if = what_if_simulator(
            current_grades=sgpa_series,
            current_credits=all_credits[:completed_semesters],
            remaining_credits=remaining_credits,
        )

        if projection and what_if:
            st.subheader("Expected Final CGPA")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Minimum case", f"{projection['minimum']:.2f}")
            with c2:
                st.metric("Realistic case", f"{projection['realistic']:.2f}")
            with c3:
                st.metric("Best case", f"{projection['best']:.2f}")

            with st.expander("What-if"):
                st.markdown(
                    f"""
                    Assuming your remaining {remaining_credits} credits:
                    - Minimum-case SGPA ($6.0$): Final CGPA ≈ **{what_if['minimum']:.2f}**
                    - Realistic SGPA ($8.0$): Final CGPA ≈ **{what_if['realistic']:.2f}**
                    - Best-case SGPA ($9.5$): Final CGPA ≈ **{what_if['best']:.2f}**
                    """
                )

    st.caption("Tip: Update credits if your semester load changes.")

def render_sgpa_inputs(initial_state: dict | None = None) -> tuple[bool, list[str], list[int], list[float]]:
    """Render SGPA input form with subject-level details."""
    initial_state = initial_state or {}

    # Apply reset before creating widgets to avoid Streamlit session-state mutation errors.
    if st.session_state.get("sgpa_reset_requested", False):
        st.session_state["sgpa_num_subjects"] = 6
        for i in range(15):
            st.session_state[f"subject_name_{i}"] = f"Subject {i + 1}"
            st.session_state[f"subject_credit_{i}"] = 3
            st.session_state[f"subject_grade_{i}"] = "A"
        st.session_state["sgpa_reset_requested"] = False

    if "sgpa_num_subjects" not in st.session_state:
        st.session_state["sgpa_num_subjects"] = int(initial_state.get("num_subjects", 6))

    initial_subjects = initial_state.get("subjects", [])
    initial_credits = initial_state.get("credits", [])
    initial_grades = initial_state.get("grades", [])

    if "custom_grade_map" not in st.session_state:
        st.session_state["custom_grade_map"] = initial_state.get("grade_map", dict(GRADE_POINT_MAP))
    custom_map = st.session_state["custom_grade_map"]

    for i in range(15):
        n_key = f"subject_name_{i}"
        if n_key not in st.session_state:
            st.session_state[n_key] = str(initial_subjects[i]) if i < len(initial_subjects) else f"Subject {i + 1}"
        c_key = f"subject_credit_{i}"
        if c_key not in st.session_state:
            st.session_state[c_key] = int(initial_credits[i]) if i < len(initial_credits) else 3
        g_key = f"subject_grade_{i}"
        if g_key not in st.session_state:
            st.session_state[g_key] = initial_grades[i] if i < len(initial_grades) and initial_grades[i] in custom_map else list(custom_map.keys())[0] if custom_map else "A"

    st.subheader("SGPA Setup")

    with st.expander("Grade mapping", expanded=False):
        st.markdown("Edit your grading scale below. You can add or remove rows as needed.")
        grade_rows = [
            {"Grade": grade, "Grade Point": point}
            for grade, point in custom_map.items()
        ]
        df = pd.DataFrame(grade_rows)
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="grade_map_editor"
        )
        
        # Rebuild custom_map from edited_df
        new_custom_map = {}
        for _, row in edited_df.iterrows():
            g = str(row.get("Grade", "")).strip()
            p = row.get("Grade Point")
            if g and pd.notna(p):
                try:
                    new_custom_map[g] = float(p)
                except ValueError:
                    pass
        
        # Save back to session state if changed
        if new_custom_map != custom_map and new_custom_map:
            st.session_state["custom_grade_map"] = new_custom_map
            st.rerun()

    @st.cache_data
    def load_curriculum():
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "curriculum.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    curriculum_data = load_curriculum()
    if curriculum_data:
        with st.expander("✨ Auto-fill from Template", expanded=False):
            st.markdown("Select your syllabus and semester to automatically fill in the subjects and credits.")
            col_b, col_s = st.columns(2)
            with col_b:
                branch = st.selectbox("Syllabus", options=list(curriculum_data.keys()), key="template_branch")
            with col_s:
                if branch:
                    sem = st.selectbox("Semester", options=list(curriculum_data[branch].keys()), key="template_sem")
            
            if st.button("Load Subjects", type="primary", use_container_width=True):
                if branch and sem:
                    subjects_list = curriculum_data[branch][sem]
                    st.session_state["sgpa_num_subjects"] = len(subjects_list)
                    for i, subj in enumerate(subjects_list):
                        st.session_state[f"subject_name_{i}"] = subj["name"]
                        st.session_state[f"subject_credit_{i}"] = subj["credits"]
                        # Also default to grade 'A' to make it faster
                        st.session_state[f"subject_grade_{i}"] = "A"
                    st.rerun()

            st.markdown("---")
            st.markdown("**Verify Curriculum Sources:**")
            st.markdown(
                "<small>"
                "<b>Computer Engineering:</b> "
                "<a href='https://pccegoa.edu.in/wp-content/uploads/2022/02/RC2019_20-FirstYear_schema1.pdf' target='_blank'>First Year</a> | "
                "<a href='https://pccegoa.edu.in/wp-content/uploads/2022/04/RC2019-20_compscheme_syllabus_sem_III_IV.pdf' target='_blank'>Sem 3 & 4</a> | "
                "<a href='https://pccegoa.edu.in/wp-content/uploads/2022/11/RC2019-20_compscheme_syllabus_sem_V_VI.pdf' target='_blank'>Sem 5 & 6</a> | "
                "<a href='https://pccegoa.edu.in/wp-content/uploads/2022/11/Approved-Scheme-RC19-20-Sem-VII-and-VIII.pdf' target='_blank'>Sem 7 & 8</a>"
                "<br>"
                "<b>Information Technology:</b> "
                "<a href='https://pccegoa.edu.in/wp-content/uploads/2022/02/RC2019_20_IT_Scheme.pdf' target='_blank'>Full RC 2019-20 Syllabus</a>"
                "<br>"
                "<b>Mechanical Engineering:</b> "
                "<a href='https://pccegoa.edu.in/wp-content/uploads/2022/02/Second-Year-Sem-III-Sem-IV-RC-19.pdf' target='_blank'>Sem 3 & 4</a> | "
                "<a href='https://pccegoa.edu.in/wp-content/uploads/2022/02/Third-Year-Sem-V-Sem-VI-RC-19.pdf' target='_blank'>Sem 5 & 6</a> | "
                "<a href='https://pccegoa.edu.in/wp-content/uploads/2022/02/Fourth-Year-Sem-VII-Sem-VIII-RC-19.pdf' target='_blank'>Sem 7 & 8</a>"
                "</small>", 
                unsafe_allow_html=True
            )

    num_subjects = int(st.number_input(
        "Number of subjects",
        min_value=1,
        max_value=15,
        step=1,
        key="sgpa_num_subjects",
    ))

    with st.form("sgpa_form", clear_on_submit=False):
        subjects: list[str] = []
        credits: list[int] = []
        grade_points: list[float] = []

        st.markdown("### Subjects")
        for i in range(num_subjects):
            col1, col2, col3 = st.columns([2.3, 1, 1])

            with col1:
                subject_name = st.text_input(
                    f"Subject {i + 1} name",
                    key=f"subject_name_{i}",
                )
            with col2:
                credit = st.number_input(
                    f"Credits #{i + 1}",
                    min_value=0,
                    max_value=35,
                    step=1,
                    key=f"subject_credit_{i}",
                )
            with col3:
                grade_letter = st.selectbox(
                    f"Grade #{i + 1}",
                    options=list(st.session_state["custom_grade_map"].keys()),
                    key=f"subject_grade_{i}",
                )
                st.caption("Pass" if grade_letter != "F" else "Fail")

            subjects.append(subject_name.strip() or f"Subject {i + 1}")
            credits.append(int(credit))
            grade_points.append(float(st.session_state["custom_grade_map"].get(grade_letter, 0.0)))

        submitted = st.form_submit_button(
            "Calculate SGPA",
        )
        clear_clicked = st.form_submit_button(
            "Clear",
            type="secondary",
        )

    if clear_clicked:
        st.session_state["sgpa_clear_pending"] = True

    if st.session_state.get("sgpa_clear_pending", False):
        st.warning("Clear all SGPA inputs? This action will reset your current entries.")
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("Confirm", key="sgpa_confirm_clear", use_container_width=True):
                st.session_state["sgpa_reset_requested"] = True
                if "sgpa_state" in st.query_params:
                    del st.query_params["sgpa_state"]
                st.session_state["sgpa_clear_pending"] = False
                st.toast("SGPA inputs cleared.", icon="🗑️")
                st.rerun()
        with col_cancel:
            if st.button("Cancel", key="sgpa_cancel_clear", use_container_width=True):
                st.session_state["sgpa_clear_pending"] = False
                st.rerun()

    return submitted, subjects, credits, grade_points

def render_sgpa_results(sgpa: float, percentage: float, total_credits: int, breakdown) -> None:
    """Render SGPA results and subject-wise breakdown."""
    st.markdown("---")
    st.subheader("SGPA Result")

    is_failed = bool((breakdown["Grade Point"] == 0.0).any()) if not breakdown.empty else False
    result_status = "FAILED" if is_failed else "PASSED"
    result_color = "#EF4444" if is_failed else "#10B981"
    us_gpa = (sgpa / 10.0) * 4.0

    st.markdown(f"""
<div class='glass-card'>
    <table style='width:100%;table-layout:fixed;text-align:center;border-collapse:separate;border-spacing:1rem 0;'>
        <tr>
            <td>
                <div class='metric-label'>SGPA</div>
                <div class='metric-value'>{sgpa:.2f}</div>
            </td>
            <td>
                <div class='metric-label'>US GPA</div>
                <div class='metric-value'>{us_gpa:.2f}</div>
            </td>
            <td>
                <div class='metric-label'>Percentage</div>
                <div class='metric-value'>{percentage:.2f}%</div>
            </td>
            <td>
                <div class='metric-label'>Credits</div>
                <div class='metric-value'>{total_credits}</div>
            </td>
            <td>
                <div class='metric-label'>Subjects</div>
                <div class='metric-value'>{len(breakdown)}</div>
            </td>
            <td>
                <div class='metric-label'>Status</div>
                <div class='metric-value' style='background: {result_color}22; border: 2px solid {result_color};'>{result_status}</div>
            </td>
        </tr>
    </table>
</div>
    """, unsafe_allow_html=True)

    if is_failed:
        st.error("One or more subjects are F, so SGPA is 0.00.")

    st.subheader("Subject Breakdown")
    st.dataframe(
        breakdown,
        width="stretch",
        height=320,
    )

    if not breakdown.empty:
        csv_data = breakdown.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Breakdown (CSV)",
            data=csv_data,
            file_name='subject_breakdown.csv',
            mime='text/csv',
        )

    settings = settings or {}
    pct_formula = settings.get("pct_formula", "mu")
    pct_formula_str = r"$(SGPA - 0.75) \times 10$" if pct_formula == "mu" else (r"$SGPA \times 9.5$" if pct_formula == "cbse" else r"$SGPA \times 10$")

    weighted_sum = float(breakdown["Weighted"].sum()) if not breakdown.empty else 0.0
    with st.expander("How it's calculated"):
        st.markdown(f"""
        **SGPA Formula**

        $SGPA = \\frac{{\\sum(GradePoint_i \\times Credits_i)}}{{\\sum(Credits_i)}}$

        **Your values**

        - Total weighted score: {weighted_sum:.2f}
        - Total credits: {total_credits}
        - Final SGPA: {sgpa:.2f}
        - Percentage: {percentage:.2f}% (using {pct_formula_str})
        - US GPA Equivalent: {us_gpa:.2f} (using $(SGPA \\div 10) \\times 4.0$)

        **Rule applied**

        - If any subject has grade **F** (grade point $0$), final SGPA is shown as **0.00 (Failed)**.
        """)

def render_planner_inputs(initial_state: dict | None = None) -> tuple[bool, float, int, float, int]:
    """Render target planner input form."""
    initial_state = initial_state or {}

    # Apply reset before creating widgets to avoid Streamlit session-state mutation errors.
    if st.session_state.get("planner_reset_requested", False):
        st.session_state["planner_current_cgpa"] = 8.0
        st.session_state["planner_current_credits"] = 80
        st.session_state["planner_target_cgpa"] = 8.5
        st.session_state["planner_remaining_credits"] = 40
        st.session_state["planner_reset_requested"] = False

    if "planner_current_cgpa" not in st.session_state:
        st.session_state["planner_current_cgpa"] = float(initial_state.get("current_cgpa", 8.0))
    if "planner_current_credits" not in st.session_state:
        st.session_state["planner_current_credits"] = int(initial_state.get("current_credits", 80))
    if "planner_target_cgpa" not in st.session_state:
        st.session_state["planner_target_cgpa"] = float(initial_state.get("target_cgpa", 8.5))
    if "planner_remaining_credits" not in st.session_state:
        st.session_state["planner_remaining_credits"] = int(initial_state.get("remaining_credits", 40))

    st.subheader("Target Planner")

    with st.form("planner_form", clear_on_submit=False):
        current_cgpa = float(st.number_input(
            "Current CGPA",
            min_value=0.0,
            max_value=10.0,
            step=0.01,
            key="planner_current_cgpa",
        ))
        current_credits = int(st.number_input(
            "Completed credits",
            min_value=0,
            max_value=250,
            step=1,
            key="planner_current_credits",
        ))
        target_cgpa = float(st.number_input(
            "Target CGPA",
            min_value=0.0,
            max_value=10.0,
            step=0.01,
            key="planner_target_cgpa",
        ))
        remaining_credits = int(st.number_input(
            "Remaining credits",
            min_value=1,
            max_value=250,
            step=1,
            key="planner_remaining_credits",
        ))

        submitted = st.form_submit_button("Calculate Required SGPA")
        clear_clicked = st.form_submit_button(
            "Clear",
            type="secondary",
        )

    if clear_clicked:
        st.session_state["planner_clear_pending"] = True

    if st.session_state.get("planner_clear_pending", False):
        st.warning("Clear all Planner inputs? This will reset target-planning values.")
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("Confirm", key="planner_confirm_clear", use_container_width=True):
                st.session_state["planner_reset_requested"] = True
                if "planner_state" in st.query_params:
                    del st.query_params["planner_state"]
                st.session_state["planner_clear_pending"] = False
                st.toast("Planner inputs cleared.", icon="🗑️")
                st.rerun()
        with col_cancel:
            if st.button("Cancel", key="planner_cancel_clear", use_container_width=True):
                st.session_state["planner_clear_pending"] = False
                st.rerun()

    return submitted, current_cgpa, current_credits, target_cgpa, remaining_credits

def render_planner_results(
    required_sgpa: float,
    feasibility: str,
    current_cgpa: float,
    current_credits: int,
    target_cgpa: float,
    remaining_credits: int,
) -> None:
    """Render target planner result cards and explanation."""
    st.markdown("---")
    st.subheader("Planner Result")

    status_color = {
        "Already Achieved": "#10B981",
        "Feasible": "#3B82F6",
        "Not Feasible": "#EF4444",
    }.get(feasibility, "#6B7280")

    st.markdown(f"""
<div class='glass-card'>
    <table style='width:100%;table-layout:fixed;text-align:center;border-collapse:separate;border-spacing:1rem 0;'>
        <tr>
            <td>
                <div class='metric-label'>Required SGPA</div>
                <div class='metric-value'>{required_sgpa:.2f}</div>
            </td>
            <td>
                <div class='metric-label'>Target CGPA</div>
                <div class='metric-value'>{target_cgpa:.2f}</div>
            </td>
            <td>
                <div class='metric-label'>Remaining Credits</div>
                <div class='metric-value'>{remaining_credits}</div>
            </td>
            <td>
                <div class='metric-label'>Feasibility</div>
                <div class='metric-value' style='background: {status_color}22; border: 2px solid {status_color};'>{feasibility}</div>
            </td>
        </tr>
    </table>
</div>
    """, unsafe_allow_html=True)

    if feasibility == "Not Feasible":
        st.error("Target is not feasible with current constraints because required SGPA is above 10.")
    elif feasibility == "Already Achieved":
        st.success("Your current performance already satisfies this target CGPA.")
    else:
        if required_sgpa >= 9.5:
            st.info(f"Target is feasible, but you will need nearly perfect scores (O grades) across all your remaining {remaining_credits} credits.")
        elif required_sgpa >= 8.5:
            st.info(f"Target is feasible. You will need to average mostly A+ (9.0) and O (10.0) grades over your remaining {remaining_credits} credits.")
        elif required_sgpa >= 7.5:
            st.info(f"Target is feasible. You will need to maintain a solid A (8.0) average over your remaining {remaining_credits} credits.")
        else:
            st.info(f"Target is feasible. Maintaining an average above {required_sgpa:.2f} will get you there.")

    with st.expander("How it's calculated"):
        st.markdown(f"""
        **Required SGPA Formula**

        $RequiredSGPA = \\frac{{TargetCGPA \\times (CurrentCredits + RemainingCredits) - CurrentCGPA \\times CurrentCredits}}{{RemainingCredits}}$

        **Your values**

        - Current CGPA: {current_cgpa:.2f}
        - Current credits: {current_credits}
        - Target CGPA: {target_cgpa:.2f}
        - Remaining credits: {remaining_credits}
        - Required SGPA: {required_sgpa:.2f}
        """)

def get_classification_color(classification: str) -> str:
    """Return color based on classification for visual feedback."""
    colors = {
        "Outstanding": "#10B981",  # Green
        "Excellent": "#3B82F6",   # Blue
        "Good": "#8B5CF6",        # Purple
        "Satisfactory": "#F59E0B", # Orange
        "Needs improvement": "#EF4444" # Red
    }
    return colors.get(classification, "#6B7280")  # Default gray

def analyze_trend(sgpa_list: list[float]) -> str:
    """Analyze SGPA trend and return human-readable analysis."""
    if len(sgpa_list) < 2:
        return "Not enough data to analyze trend."

    # Calculate simple trend
    start_avg = sum(sgpa_list[:2]) / 2
    end_avg = sum(sgpa_list[-2:]) / 2

    if end_avg > start_avg + 0.5:
        return "Positive trend"
    elif end_avg < start_avg - 0.5:
        return "Declining trend"
    else:
        return "Stable trend"
