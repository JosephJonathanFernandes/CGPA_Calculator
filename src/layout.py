# src/layout.py
"""
Streamlit UI layout for CGPA Calculator (modular, clean, secure, HCD-focused).
Enhanced with Human-Centered Design principles for optimal user experience.
"""
import streamlit as st
from .config import Theme, global_css
from .logic import DEFAULT_CREDITS, DEFAULT_SEM_COUNT, GRADE_POINT_MAP, grade_letter_to_point

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
        background: #f8fafc !important; /* subtle off-white for contrast */
        color: #0b1221 !important; /* strong dark text for light mode */
        border: 1.5px solid #cbd5e1;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.10);
        transition: all 0.3s ease;
    }}

    .stForm {{
        background: #fff !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb;
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
        font-size: 2rem;
        font-weight: 800;
        color: #0b1221;
        background: linear-gradient(135deg, #e0e7ef 0%, #c7d2fe 100%);
        padding: 0.5rem 1rem;
        border-radius: 12px;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(37,99,235,0.08);
        transition: all 0.3s ease;
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
        .metric-value {{
            font-size: 1.5rem;
            padding: 0.3rem 0.7rem;
        }}
    }}
    """

def render_header(theme: Theme, title: str = "🎓 CGPA Calculator") -> None:
    """Render enhanced header with HCD principles."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(title)
   
    with col2:
        st.metric("📚 Default semesters", DEFAULT_SEM_COUNT, help="Based on GEC Computer curriculum")

def render_inputs() -> tuple[bool, int, int, list[int], list[float]]:
    """Render enhanced input form with HCD principles."""
    st.subheader("🎯 Setup Your Academic Profile")

    # Enhanced tooltip with emoji and better explanation
    with st.expander("ℹ️ Setup Guide", expanded=False):
        st.markdown("""
        **Quick Setup Tips:**
        - Start with your total program semesters
        - Enter only completed semesters with published SGPA
        - Use default credits for standard curriculum
        - Customize credits if you have electives or special courses
        """)

    st.markdown("🔗 [Need semester-wise calculation first? Open SGPA Calculator](?page=sgpa)")

    # Keep dynamic controls outside the form so UI updates immediately.
    num_courses = int(st.number_input(
        "📚 Number of semesters in your program",
        min_value=1,
        max_value=12,
        step=1,
        value=DEFAULT_SEM_COUNT,
        help="Total semesters planned for your academic program (typically 8 for GEC Computer).",
    ))

    completed_semesters = int(st.number_input(
        "🎓 Semesters with published SGPA",
        min_value=1,
        max_value=num_courses,
        step=1,
        value=num_courses,
        help="Number of semesters you've completed with official SGPA results.",
    ))

    # Enhanced checkbox with better visual hierarchy
    st.markdown("---")
    use_custom = st.checkbox(
        "🔧 Use custom credits per semester",
        help="Enable this if your curriculum differs from GEC Computer standards.",
        value=False
    )

    with st.form("cgpa_form", clear_on_submit=False):
        credits: list[int] = []
        grades: list[float] = []
        if use_custom:
            st.markdown("""
            **Custom Credit Setup**
            Enter the total credits for each semester. This helps calculate accurate weighted CGPA.
            """)
            st.markdown("### 📝 Credit Inputs")
            for i in range(num_courses):
                default_value = DEFAULT_CREDITS[i] if i < DEFAULT_SEM_COUNT else DEFAULT_CREDITS[-1]
                credit = st.number_input(
                    f"📝 Semester {i + 1} credits",
                    min_value=0,
                    max_value=35,
                    step=1,
                    value=default_value,
                    key=f"credit_{i}",
                    help=f"Total credits for Semester {i + 1} (default: {default_value})",
                )
                credits.append(int(credit))

            st.markdown("---")
            st.markdown("### 📈 SGPA Inputs")
            for i in range(num_courses):
                grade = st.number_input(
                    f"📈 Semester {i + 1} SGPA",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.01,
                    value=7.0,  # Default to average score for better UX
                    key=f"sgpa_{i}",
                    help=f"Enter your official SGPA for Semester {i + 1}",
                )
                grades.append(float(grade))
        else:
            for i in range(num_courses):
                credits.append(DEFAULT_CREDITS[i] if i < DEFAULT_SEM_COUNT else DEFAULT_CREDITS[-1])
                grade = st.number_input(
                    f"📈 Semester {i + 1} SGPA",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.01,
                    value=7.0,  # Default to average score for better UX
                    key=f"sgpa_{i}",
                    help=f"Enter your official SGPA for Semester {i + 1}",
                )
                grades.append(float(grade))

        # Enhanced submit button with loading state
        submitted = st.form_submit_button(
            "🚀 Calculate My CGPA",
            help="Click to compute your cumulative CGPA with detailed breakdown"
        )

    return submitted, num_courses, completed_semesters, credits, grades

def render_results(
    cgpa: float,
    percentage: float,
    total_credits: int,
    classification: str,
    breakdown,
    completed_semesters: int,
    num_courses: int,
) -> None:
    """Render enhanced results with HCD principles."""
    st.markdown("---")
    st.subheader("🏆 Your Academic Performance Results")


    # Enhanced metrics with visual hierarchy and emojis
    cgpa_emoji = get_performance_emoji(cgpa)
    classification_color = get_classification_color(classification)
    st.markdown(f"""
<div class='glass-card'>
    <table style='width:100%;table-layout:fixed;text-align:center;border-collapse:separate;border-spacing:1rem 0;'>
        <tr>
            <td>
                <div class='metric-label'>🎯 CGPA Score</div>
                <div class='metric-value'>{cgpa_emoji} {cgpa:.2f}</div>
            </td>
            <td>
                <div class='metric-label'>📊 Percentage</div>
                <div class='metric-value'>{percentage:.2f}%</div>
            </td>
            <td>
                <div class='metric-label'>📚 Total Credits</div>
                <div class='metric-value'>{total_credits}</div>
            </td>
            <td>
                <div class='metric-label'>🏅 Academic Standing</div>
                <div class='metric-value' style='background: {classification_color}22; border: 2px solid {classification_color};'>{classification}</div>
            </td>
        </tr>
    </table>
</div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Enhanced breakdown section
    st.subheader("📊 Detailed Semester Breakdown")
    st.dataframe(
        breakdown,
        width="stretch",
        height=300
    )

    # Enhanced info message with better UX
    if completed_semesters < num_courses:
        remaining_semesters = num_courses - completed_semesters
        st.info(
            f"ℹ️ **Calculation Note:** Your CGPA is based on the first {completed_semesters} semester(s). "
            f"You have {remaining_semesters} semester(s) remaining in your plan. "
            f"Update this as you complete more semesters!",
            icon="📅",
        )

    # Enhanced visualization with better UX
    with st.expander("📈 Visualize Your SGPA Trend & Progress"):
        st.markdown("""
        **Performance Trend Analysis**
        Track your academic progress over time to identify patterns and areas for improvement.
        """)
        st.bar_chart(
            breakdown,
            x="Semester",
            y="SGPA",
            width="stretch",
            height=400
        )

        # Add trend analysis
        if len(breakdown) > 1:
            trend = analyze_trend(breakdown['SGPA'].tolist())
            st.markdown(f"**📊 Trend Analysis:** {trend}")

    # Enhanced footnote with actionable advice
    st.markdown("""
    <div class='footnote'>
    💡 **Pro Tip:** Revisit your credit setup when you choose electives or your course load changes.
    This ensures your CGPA calculation remains accurate throughout your academic journey.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def render_sgpa_inputs() -> tuple[bool, list[str], list[int], list[float]]:
    """Render SGPA input form with subject-level details."""
    st.subheader("🧮 Setup Your SGPA Calculation")

    with st.expander("ℹ️ SGPA Guide", expanded=False):
        st.markdown("""
        **How to use this page:**
        - Enter the number of subjects in your current semester
        - Add subject credits and select grade letter for each subject
        - Submit to compute weighted SGPA instantly

        **Supported grades:** O, A+, A, B+, B, C, P, F
        - P is pass (4 points)
        - F is fail (0 points)
        """)
        st.markdown("### 🏷️ Grade Mapping")
        grade_rows = [
            {"Grade": grade, "Grade Point": point, "Status": "Fail" if grade == "F" else "Pass"}
            for grade, point in GRADE_POINT_MAP.items()
        ]
        st.dataframe(grade_rows, width="stretch", height=280)

    num_subjects = int(st.number_input(
        "📘 Number of subjects",
        min_value=1,
        max_value=15,
        step=1,
        value=6,
        help="Total subjects considered for SGPA in this semester.",
    ))

    with st.form("sgpa_form", clear_on_submit=False):
        subjects: list[str] = []
        credits: list[int] = []
        grade_points: list[float] = []

        st.markdown("### 📚 Subject-Wise Entries")
        for i in range(num_subjects):
            col1, col2, col3 = st.columns([2.3, 1, 1])

            with col1:
                subject_name = st.text_input(
                    f"Subject {i + 1} name",
                    value=f"Subject {i + 1}",
                    key=f"subject_name_{i}",
                )
            with col2:
                credit = st.number_input(
                    f"Credits #{i + 1}",
                    min_value=0,
                    max_value=35,
                    step=1,
                    value=3,
                    key=f"subject_credit_{i}",
                )
            with col3:
                grade_letter = st.selectbox(
                    f"Grade #{i + 1}",
                    options=list(GRADE_POINT_MAP.keys()),
                    index=2,
                    key=f"subject_grade_{i}",
                )

            subjects.append(subject_name.strip() or f"Subject {i + 1}")
            credits.append(int(credit))
            grade_points.append(float(grade_letter_to_point(grade_letter) or 0.0))

        submitted = st.form_submit_button(
            "🧾 Calculate My SGPA",
            help="Compute semester GPA from subject-wise credits and grade points",
        )

    return submitted, subjects, credits, grade_points

def render_sgpa_results(sgpa: float, percentage: float, total_credits: int, breakdown) -> None:
    """Render SGPA results and subject-wise breakdown."""
    st.markdown("---")
    st.subheader("🏁 Your SGPA Result")

    st.markdown(f"""
<div class='glass-card'>
    <table style='width:100%;table-layout:fixed;text-align:center;border-collapse:separate;border-spacing:1rem 0;'>
        <tr>
            <td>
                <div class='metric-label'>📘 SGPA Score</div>
                <div class='metric-value'>🧠 {sgpa:.2f}</div>
            </td>
            <td>
                <div class='metric-label'>📊 Percentage</div>
                <div class='metric-value'>{percentage:.2f}%</div>
            </td>
            <td>
                <div class='metric-label'>📚 Total Credits</div>
                <div class='metric-value'>{total_credits}</div>
            </td>
            <td>
                <div class='metric-label'>🧾 Subjects Count</div>
                <div class='metric-value'>{len(breakdown)}</div>
            </td>
        </tr>
    </table>
</div>
    """, unsafe_allow_html=True)

    st.subheader("📊 Subject-Wise Breakdown")
    st.dataframe(
        breakdown,
        width="stretch",
        height=320,
    )

def get_performance_emoji(cgpa: float) -> str:
    """Return emoji based on CGPA performance."""
    if cgpa >= 9.0:
        return "🌟"
    elif cgpa >= 8.0:
        return "⭐"
    elif cgpa >= 7.0:
        return "✨"
    elif cgpa >= 6.0:
        return "👍"
    else:
        return "💪"

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
        return "📈 **Positive Trend:** Your performance is improving! Keep up the good work."
    elif end_avg < start_avg - 0.5:
        return "📉 **Declining Trend:** Your performance has decreased. Consider reviewing your study strategies."
    else:
        return "📊 **Stable Performance:** Your SGPA has remained consistent. Good job maintaining your standards."
