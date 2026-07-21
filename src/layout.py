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
    .stTextInput, .stNumberInput, .stCheckbox {{
        margin-bottom: 1.2rem !important;
    }}

    /* Pill styling with smooth transitions */
    .pill {{
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1.2rem;
        background: linear-gradient(135deg, var(--surface) 0%, var(--card) 100%);
        border: 1px solid var(--border);
        border-radius: 2rem;
        font-size: 1.08rem;
        font-weight: 700;
        color: var(--text);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
        margin-top: 0.5rem;
    }}

    .pill:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: var(--primary);
    }}

    /* Enhanced glass card effect using flexbox */
    .glass-card {{
        background: var(--glass-bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .sticky-summary {{
        position: sticky;
        top: 2rem;
        z-index: 999;
    }}

    .stForm {{
        background: transparent !important;
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }}

    .glass-card:hover {{
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.15);
        transform: translateY(-4px);
    }}

    /* Flexbox metrics container */
    .metrics-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        justify-content: space-between;
        align-items: flex-start;
    }}

    .metric-item {{
        flex: 1;
        min-width: 120px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }}

    /* Metric styling with visual hierarchy */
    .metric-label {{
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .metric-value {{
        font-size: clamp(1.5rem, 3vw, 2.5rem);
        font-weight: 800;
        color: var(--text);
        line-height: 1.2;
        letter-spacing: -0.02em;
    }}

    .hero {{
        text-align: center;
        padding: 3rem 1.5rem;
        margin-bottom: 2rem;
    }}
    .hero-tag {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        background-color: rgba(2, 132, 199, 0.1);
        color: var(--primary);
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }}
    .hero h1 {{
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: var(--text);
    }}
    .hero p {{
        font-size: 1.1rem;
        color: var(--muted);
        max-width: 600px;
        margin: 0 auto;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        padding-top: 1rem;
    }}
    /* Aggressive native theme overrides */
    [data-testid="stHeader"] {{
        background: var(--surface) !important;
        color: var(--text) !important;
    }}
    
    [data-testid="stSidebar"] [data-testid="stExpander"],
    [data-testid="stSidebar"] [data-testid="stExpander"] details,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary,
    [data-testid="stSidebar"] [data-testid="stExpander"] div {{
        background-color: var(--surface) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
    }}
    
    [data-testid="stSidebar"] [data-testid="stExpander"] {{
        border-radius: 12px !important;
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        overflow: hidden !important;
    }}

    [data-testid="stSidebarNav"] span, 
    [data-testid="stSidebarNav"] a, 
    [data-testid="stSidebarNav"] div,
    [data-testid="stSidebarNav"] svg {{
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        color: var(--text) !important;
        fill: var(--text) !important;
    }}
    [data-testid="stSidebar"] .stToggle {{
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }}
    
    .large-guide-btn [data-testid="stPageLink-NavLink"] {{
        background-color: var(--primary) !important;
        color: white !important;
        padding: 1.25rem !important;
        border-radius: 12px !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }}
    
    .large-guide-btn [data-testid="stPageLink-NavLink"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.15) !important;
    }}
    
    .feature-card {{
        padding: 1.5rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }}
    .feature-icon {{
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }}
    
    .card-btn {{
        margin-top: auto;
        display: inline-block;
        padding: 0.75rem 1rem;
        background-color: var(--primary);
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
        text-align: center;
    }}
    .card-btn:hover {{
        background-color: var(--primary-dark);
        transform: translateY(-2px);
    }}
    
    .large-guide-link {{
        display: block;
        width: 100%;
        padding: 1.25rem;
        background-color: var(--surface);
        border: 2px solid var(--primary);
        color: var(--text) !important;
        text-align: center;
        border-radius: 12px;
        font-size: 1.2rem;
        font-weight: 700;
        text-decoration: none;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }}
    .large-guide-link:hover {{
        background-color: var(--primary);
        color: white !important;
        transform: translateY(-2px);
    }}
    .feature-card h3 {{
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.25rem;
    }}
    .feature-card p {{
        color: var(--muted);
        font-size: 0.95rem;
        margin: 0;
    }}

    /* Badge styling */
    .status-badge {{
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 12px;
        font-size: 0.95rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}

    /* Enhanced button styling */
    .stButton>button {{
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(37,99,235,0.2);
    }}

    .stButton>button:hover {{
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 20px rgba(37,99,235,0.3);
    }}

    .stButton>button:active {{
        transform: translateY(0) scale(0.98);
    }}
    
    /* Secondary button styling */
    button[kind="secondary"] {{
        background: transparent !important;
        border: 2px solid var(--border) !important;
        color: var(--text) !important;
        box-shadow: none !important;
    }}
    
    button[kind="secondary"]:hover {{
        border-color: var(--primary) !important;
        color: var(--primary) !important;
        background: rgba(37,99,235,0.05) !important;
    }}

    /* Accessibility enhancements */
    input:focus, textarea:focus, select:focus {{
        outline: 2px solid var(--primary) !important;
        outline-offset: 2px;
    }}

    /* Responsive design */
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }}
        .metrics-container {{
            flex-direction: column;
            gap: 1.5rem;
        }}
        .metric-item {{
            width: 100%;
            background: var(--surface);
            padding: 1rem;
            border-radius: 16px;
            border: 1px solid var(--border);
        }}
        .metric-value {{
            font-size: 2rem;
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

def render_home_page(cgpa_page=None, sgpa_page=None, planner_page=None, guide_page=None):
    st.markdown("""
    <div class="hero glass-card">
        <span class="hero-tag">Goa University (DBCE, PCCE, GEC, RIT, AITD) & Beyond</span>
        <h1>Plan Your Academic Future</h1>
        <p>Track your CGPA, simulate what-if scenarios, and know exactly
           what you need to hit your target. Pre-configured for Goa University colleges, 
           but fully customizable for any other university's curriculum!</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    features = [
        ("📊", "CGPA Calculator", "See your cumulative standing, trend analysis, and a predictive range for your final CGPA.", "cgpa"),
        ("📘", "SGPA Calculator", "Auto-filled subjects for your branch and semester — just enter grades.", "sgpa"),
        ("🎯", "Target Planner", "Tell us your goal CGPA; we'll tell you the SGPA you need each remaining semester.", "planner"),
    ]
    for col, (icon, title, desc, url) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class="feature-card glass-card" style="margin-bottom: 1rem;">
                <div class="feature-icon">{icon}</div>
                <h3>{title}</h3>
                <p style="margin-bottom: 1.5rem;">{desc}</p>
                <a href="{url}" target="_self" class="card-btn">🚀 Get Started →</a>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if guide_page:
            st.markdown(f'<a href="guide" target="_self" class="large-guide-link">📖 New here? Read our simple Guide & FAQs</a>', unsafe_allow_html=True)

def render_guide_page():
    st.title("📖 How it Works (Guide & FAQs)")
    
    st.markdown("### The Basics (Explained Simply)")
    st.info("""
    **What is an SGPA?**  
    Think of SGPA like your batting average for a *single tournament* (one semester). It only looks at your performance in those specific matches.
    
    **What is a CGPA?**  
    Your CGPA is your *career* batting average. It combines the scores from every tournament you've ever played (all your semesters) into one master score.
    
    **Why do 'Credits' matter?**  
    Imagine you're playing a video game. A 4-credit subject (like Engineering Math) is a **Boss Fight**. A 1-credit subject (like a Lab) is a **Side Quest**.  
    If you do poorly on a Side Quest, it barely affects your score. But if you fail a Boss Fight, your overall score drops massively. That's why the 'Standard (Accounts for credits)' setting is so important!
    """)
    
    st.markdown("### Frequently Asked Questions")
    
    with st.expander("I'm from a Goa University Engineering College. What should I do?"):
        st.write("Nothing! The app is already pre-loaded with the exact formulas and credit structures for DBCE, PCCE, GEC, RIT, and AITD. Just click on 'CGPA Calculator' and start entering your grades.")
        
    with st.expander("I'm from another University or Board. Can I still use this?"):
        st.write("Yes! Open the **⚙️ Calculation Settings** in the left sidebar. You can switch the percentage conversion to CBSE or Mumbai University, and change the CGPA formula to ignore credits if your college calculates it differently.")
        
    with st.expander("What is the Target Planner?"):
        st.write("If you currently have a 6.5 CGPA and want to graduate with a 7.0, the Target Planner does the reverse-math for you. It tells you *exactly* what SGPA you need to score in your remaining semesters to hit your dream target.")
        
    with st.expander("Will I lose my grades when I close the app?"):
        st.write("Normally, yes. But if you open the **💾 Data Management** tab in the sidebar, you can click 'Download Profile'. This saves all your grades to a tiny file on your computer. Next time you visit, just upload that file and all your grades will instantly reappear!")

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
                    if int(credit) == 0 and i < completed_semesters:
                        st.error("⚠️ Missing credit", icon="🚨")
                with col2:
                    if i < completed_semesters:
                        grade = st.number_input(
                            f"Semester {i + 1} SGPA",
                            min_value=0.0,
                            step=0.01,
                            key=f"sgpa_{i}",
                        )
                        grades.append(float(grade))
                        if float(grade) > 10.0:
                            st.error("⚠️ SGPA > 10.0", icon="🚨")
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
                                step=0.01,
                                key=f"sgpa_{i+j}",
                            )
                            grades.append(float(grade))
                            if float(grade) > 10.0:
                                st.error("⚠️ SGPA > 10.0", icon="🚨")

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
<div class='glass-card sticky-summary'>
    <div class='metrics-container'>
        <div class='metric-item'>
            <div class='metric-label'>CGPA</div>
            <div class='metric-value' style='color: var(--primary)'>{cgpa:.2f}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>US GPA</div>
            <div class='metric-value'>{us_gpa:.2f}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Percentage</div>
            <div class='metric-value'>{percentage:.2f}%</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Credits</div>
            <div class='metric-value'>{total_credits}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Standing</div>
            <div class='status-badge' style='background: {classification_color}22; border: 1.5px solid {classification_color}; color: {classification_color}'>{classification}</div>
        </div>
    </div>
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
            width="stretch",
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
                "<br>"
                "<b>Electronics and Telecommunication:</b> "
                "<a href='https://pccegoa.edu.in/wp-content/uploads/2022/02/RC_19-20_Scheme_of_Instructions_sem3-sem8.pdf' target='_blank'>Sem 3 to 8 Syllabus</a>"
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
<div class='glass-card sticky-summary'>
    <div class='metrics-container'>
        <div class='metric-item'>
            <div class='metric-label'>SGPA</div>
            <div class='metric-value' style='color: var(--primary)'>{sgpa:.2f}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>US GPA</div>
            <div class='metric-value'>{us_gpa:.2f}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Percentage</div>
            <div class='metric-value'>{percentage:.2f}%</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Credits</div>
            <div class='metric-value'>{total_credits}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Subjects</div>
            <div class='metric-value'>{len(breakdown)}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Status</div>
            <div class='status-badge' style='background: {result_color}22; border: 1.5px solid {result_color}; color: {result_color}'>{result_status}</div>
        </div>
    </div>
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
<div class='glass-card sticky-summary'>
    <div class='metrics-container'>
        <div class='metric-item'>
            <div class='metric-label'>Required SGPA</div>
            <div class='metric-value' style='color: var(--primary)'>{required_sgpa:.2f}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Target CGPA</div>
            <div class='metric-value'>{target_cgpa:.2f}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Remaining Credits</div>
            <div class='metric-value'>{remaining_credits}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Feasibility</div>
            <div class='status-badge' style='background: {status_color}22; border: 1.5px solid {status_color}; color: {status_color}'>{feasibility}</div>
        </div>
    </div>
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
