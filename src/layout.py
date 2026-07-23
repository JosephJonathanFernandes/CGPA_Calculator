# src/layout.py
"""
Streamlit UI layout for CGPA Calculator (modular, clean, secure, HCD-focused).
Enhanced with Human-Centered Design principles for optimal user experience.
"""
import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, List, Tuple, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
from .config import Theme, global_css
from .logic import (
    DEFAULT_CREDITS,
    DEFAULT_SEM_COUNT,
    RC1920_CREDITS,
    NEP2025_CREDITS,
    get_scheme_credits,
    GRADE_POINT_MAP,
    consistency_score,
    grade_letter_to_point,
    predict_final_cgpa_range,
    semester_trend_slope,
    strongest_weakest_semester,
    what_if_simulator,
)
from .export import (
    generate_pdf_report,
    generate_shareable_card
)

def inject_styles(theme: Theme) -> None:
    """Inject global + component CSS."""
    st.markdown(f"<style>{global_css(theme)}{enhanced_css(theme)}</style>", unsafe_allow_html=True)
    
    # Inject JavaScript to allow swipe-to-close for the sidebar on mobile
    components.html(
        """
        <script>
            const doc = window.parent.document;
            if (!doc.swipeGestureAdded) {
                let touchstartX = 0;
                let touchstartY = 0;
                let touchendX = 0;
                let touchendY = 0;

                doc.addEventListener('touchstart', e => {
                    touchstartX = e.changedTouches[0].screenX;
                    touchstartY = e.changedTouches[0].screenY;
                }, { passive: true });

                doc.addEventListener('touchend', e => {
                    touchendX = e.changedTouches[0].screenX;
                    touchendY = e.changedTouches[0].screenY;
                    
                    const xDiff = touchstartX - touchendX;
                    const yDiff = Math.abs(touchstartY - touchendY);
                    
                    // Detect left swipe (at least 50px left, and mostly horizontal)
                    if (xDiff > 50 && yDiff < 50) { 
                        // Dispatch Escape key event to close the Streamlit sidebar
                        const escEvent = new KeyboardEvent('keydown', {
                            key: 'Escape',
                            code: 'Escape',
                            keyCode: 27,
                            which: 27,
                            bubbles: true
                        });
                        doc.dispatchEvent(escEvent);
                    }
                }, { passive: true });
                doc.swipeGestureAdded = true;
            }
        </script>
        """,
        height=0,
        width=0,
    )

def enhanced_css(theme: Theme) -> str:
    """
    Full component CSS.
    Design system: Inter body, JetBrains Mono for numbers,
    Indigo primary, Amber accent, Saffron backlog state.
    """
    return f"""
    /* ── Premium Streamlit Inputs ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    [data-baseweb="input"] {{
        border-radius: 12px !important;
        border: 1.5px solid var(--border) !important;
        background-color: var(--surface) !important;
        color: var(--text) !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 1px 2px rgba(79, 70, 229, 0.03) inset !important;
    }}

    .stSelectbox > div[data-baseweb="select"] > div {{
        border-radius: 12px !important;
        border: 1.5px solid var(--border) !important;
        background-color: var(--surface) !important;
        color: var(--text) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 1px 2px rgba(79, 70, 229, 0.03) inset !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div[data-baseweb="select"] > div:focus-within,
    [data-baseweb="input"]:focus-within {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
        background-color: var(--glass-bg) !important;
    }}

    .stTextInput, .stNumberInput, .stCheckbox, .stSelectbox {{
        margin-bottom: 1.1rem !important;
    }}

    /* Checkbox & radio labels */
    .stCheckbox label span, .stRadio label span {{
        font-weight: 500 !important;
        color: var(--text) !important;
    }}

    /* ── Micro-Animations ── */
    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .glass-card, .feat-card, .stForm, .backlog-banner, .result-hero {{
        animation: fadeUp 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }}
    @media (prefers-reduced-motion: reduce) {{
        .glass-card, .feat-card, .stForm, .backlog-banner, .result-hero {{
            animation: none !important;
        }}
    }}

    /* ── Glass card ── */
    .glass-card {{
        background: var(--glass-bg) !important;
        color: var(--text) !important;
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.25rem 0;
        box-shadow: 0 4px 24px -8px rgba(79,70,229,0.08);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        transition: transform 0.25s cubic-bezier(0.4,0,0.2,1),
                    box-shadow 0.25s cubic-bezier(0.4,0,0.2,1);
    }}
    .glass-card:hover {{
        box-shadow: 0 12px 32px -8px rgba(79,70,229,0.13);
        transform: translateY(-2px);
    }}
    @media (prefers-reduced-motion: reduce) {{
        .glass-card, .glass-card:hover {{
            transition: none !important; transform: none !important;
        }}
    }}

    .sticky-summary {{
        position: sticky;
        top: 2rem;
        z-index: 999;
    }}

    /* ── Result hero — the big CGPA number ── */
    .result-hero {{
        text-align: center;
        padding: 2.25rem 1rem 1.75rem;
    }}
    .result-hero .cgpa-number {{
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: clamp(3.5rem, 10vw, 6rem);
        font-weight: 600;
        color: var(--primary);
        line-height: 1;
        letter-spacing: -0.03em;
        margin: 0;
        display: block;
    }}
    .result-hero .cgpa-label {{
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 2.5px;
        margin-top: 0.5rem;
        display: block;
    }}

    /* ── BACKLOG / WITHHELD STATE — signature moment ── */
    /*
     * Contrast rationale: saffron (#EA580C) on tinted bg gives ~3.1:1,
     * which fails WCAG AA for text at <18.67px. Fix: saffron is structural
     * (border + background tint + bullet prefix only). All readable text uses
     * var(--text) (near-black on light, near-white on dark) for full contrast.
     */
    .backlog-banner {{
        border-left: 4px solid var(--warning);
        background: rgba(234,88,12,0.07);
        border-radius: 0 16px 16px 0;
        padding: 1.4rem 1.75rem;
        margin: 1.25rem 0;
    }}
    .backlog-banner h4 {{
        font-size: 0.95rem;
        font-weight: 800;
        color: var(--text) !important;  /* near-black/white — passes AA */
        margin: 0 0 0.5rem;
        letter-spacing: 0.2px;
    }}
    .backlog-banner h4 .backlog-dot {{
        color: var(--warning);
        margin-right: 0.4rem;
        font-size: 0.6rem;
        vertical-align: middle;
        position: relative;
        top: -1px;
    }}
    .backlog-banner p {{
        font-size: 0.9rem;
        color: var(--text) !important;
        margin: 0;
        line-height: 1.65;
    }}
    .backlog-banner .backlog-step {{
        display: inline-block;
        margin-top: 0.9rem;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--text) !important;  /* near-black — passes AA */
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.7;
    }}
    .sem-backlog-row {{
        border-left: 3px solid var(--warning);
        background: rgba(234,88,12,0.06);
        border-radius: 0 10px 10px 0;
        padding: 0.4rem 0.75rem;
        margin-bottom: 0.35rem;
        font-size: 0.82rem;
        color: var(--text);
        font-weight: 700;
        letter-spacing: 0.3px;
    }}

    /* ── Form ── */
    .stForm {{
        background: var(--glass-bg) !important;
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2.25rem 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px -8px rgba(79,70,229,0.06);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }}
    
    /* Enhance Streamlit buttons */
    .stButton > button, .stFormSubmitButton > button {{
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        padding: 0.6rem 1.25rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid var(--primary) !important;
    }}
    
    /* Primary buttons */
    .stFormSubmitButton > button:first-child {{
        background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
        color: var(--btn-text) !important;
        border: none !important;
        box-shadow: 0 4px 12px -2px rgba(79,70,229,0.3) !important;
    }}
    .stFormSubmitButton > button:first-child:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px -2px rgba(79,70,229,0.4) !important;
    }}

    /* ── Flexbox metrics strip ── */
    .metrics-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        justify-content: space-between;
        align-items: flex-start;
    }}
    .metric-item {{
        flex: 1;
        min-width: 110px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.3rem;
    }}
    .metric-label {{
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 1.4px;
    }}
    .metric-value {{
        font-family: 'JetBrains Mono', monospace;
        font-size: clamp(1.3rem, 2.2vw, 2rem);
        font-weight: 600;
        color: var(--text);
        line-height: 1.15;
        letter-spacing: -0.02em;
    }}

    /* ── Landing hero ── */
    .hero {{
        text-align: center;
        padding: 2.5rem 1.5rem 1.25rem;
    }}
    .hero-eyebrow {{
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        background: rgba(79,70,229,0.09);
        border: 1px solid rgba(79,70,229,0.18);
        color: var(--primary);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }}
    .hero h1 {{
        font-size: clamp(1.75rem, 4vw, 2.6rem);
        font-weight: 800;
        margin-bottom: 0.75rem;
        color: var(--text) !important;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }}
    .hero p {{
        font-size: 0.97rem;
        color: var(--muted);
        max-width: 520px;
        margin: 0 auto;
        line-height: 1.65;
    }}

    /* ── Score track — animated landing bar ── */
    .score-track-wrap {{
        margin: 1.75rem auto 0.25rem;
        max-width: 440px;
    }}
    .score-track-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.4rem;
    }}
    .score-track-labels {{
        display: flex;
        justify-content: space-between;
        font-size: 0.7rem;
        color: var(--muted);
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }}
    /* Inline "EXAMPLE" chip — prevents first-time users from reading the
       demo bar as their own result */
    .score-track-example-chip {{
        display: inline-block;
        font-size: 0.6rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--muted);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 0.1rem 0.5rem;
    }}
    .score-track-outer {{
        height: 10px;
        background: var(--border);
        border-radius: 999px;
        overflow: hidden;
    }}
    .score-track-fill {{
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        animation: trackFill 1.5s cubic-bezier(0.22,1,0.36,1) both;
    }}
    @keyframes trackFill {{
        from {{ width: 0 !important; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
        .score-track-fill {{ animation: none !important; }}
    }}
    .score-track-caption {{
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--muted);
        margin-top: 0.5rem;
        font-style: italic;
    }}

    /* ── Feature cards (landing) ── */
    .feat-card {{
        border-radius: 18px;
        background: var(--glass-bg);
        border: 1px solid var(--border);
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 12px -4px rgba(79,70,229,0.07);
        transition: transform 0.22s cubic-bezier(0.4,0,0.2,1),
                    box-shadow 0.22s cubic-bezier(0.4,0,0.2,1);
        backdrop-filter: blur(12px);
    }}
    .feat-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 28px -6px rgba(79,70,229,0.14);
    }}
    @media (prefers-reduced-motion: reduce) {{
        .feat-card, .feat-card:hover {{
            transition: none !important; transform: none !important;
        }}
    }}
    .feat-stripe {{
        height: 4px;
        width: 100%;
        flex-shrink: 0;
    }}
    .feat-body {{
        padding: 1.4rem 1.5rem 1.5rem;
        flex: 1;
        display: flex;
        flex-direction: column;
    }}
    .feat-body h3 {{
        font-size: 1rem;
        font-weight: 700;
        margin: 0 0 0.45rem;
        color: var(--text) !important;
    }}
    .feat-body p {{
        font-size: 0.85rem;
        color: var(--muted);
        margin: 0 0 1.25rem;
        line-height: 1.55;
        flex: 1;
    }}
    .feat-btn {{
        display: inline-block;
        padding: 0.55rem 1rem;
        border-radius: 10px;
        font-size: 0.83rem;
        font-weight: 700;
        text-decoration: none !important;
        text-align: center;
        color: var(--btn-text) !important;
        transition: opacity 0.18s ease, transform 0.18s ease;
        border: none;
    }}
    .feat-btn:hover {{
        opacity: 0.85;
        transform: translateY(-1px);
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        padding-top: 1rem;
        background: var(--glass-bg) !important;
        border-right: 1px solid var(--border) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background: transparent !important;
    }}
    [data-testid="stHeader"] {{
        background: var(--surface) !important;
        border-bottom: 1px solid var(--border) !important;
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
        margin-top: 0.75rem !important;
        margin-bottom: 0.75rem !important;
        overflow: hidden !important;
    }}
    [data-testid="stSidebarNav"] span,
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNav"] div,
    [data-testid="stSidebarNav"] svg {{
        font-size: 0.93rem !important;
        font-weight: 500 !important;
        color: var(--text) !important;
        fill: var(--text) !important;
    }}

    /* ── Status badge ── */
    .status-badge {{
        display: inline-block;
        padding: 0.28rem 0.8rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.9px;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: var(--btn-text);
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.75rem;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 0.88rem;
        letter-spacing: 0.2px;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        box-shadow: 0 3px 10px rgba(79,70,229,0.22);
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(79,70,229,0.3);
    }}
    .stButton > button:active {{
        transform: translateY(0) scale(0.98);
    }}
    button[kind="secondary"] {{
        background: transparent !important;
        border: 1.5px solid var(--border) !important;
        color: var(--text) !important;
        box-shadow: none !important;
    }}
    button[kind="secondary"]:hover {{
        border-color: var(--primary) !important;
        color: var(--primary) !important;
        background: rgba(79,70,229,0.05) !important;
    }}
    input:focus, textarea:focus, select:focus, button:focus-visible {{
        outline: 2px solid var(--primary) !important;
        outline-offset: 2px !important;
    }}

    /* ── Guide link ── */
    .large-guide-link {{
        display: block;
        width: 100%;
        padding: 0.9rem;
        background-color: transparent;
        border: 1.5px solid var(--border);
        color: var(--text) !important;
        text-align: center;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 600;
        text-decoration: none !important;
        transition: all 0.2s ease;
    }}
    .large-guide-link:hover {{
        border-color: var(--primary);
        background: rgba(79,70,229,0.05);
        color: var(--primary) !important;
    }}

    /* ── Responsive ── */
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }}
        .metrics-container {{ gap: 0.75rem; }}
        .metric-item {{
            min-width: 88px;
            background: var(--surface);
            padding: 0.7rem 0.9rem;
            border-radius: 12px;
            border: 1px solid var(--border);
            width: calc(50% - 0.375rem);
            flex: none;
        }}
        .metric-value {{ font-size: 1.4rem; }}
        .result-hero .cgpa-number {{ font-size: 3.5rem; }}
        .hero h1 {{ font-size: 1.55rem; }}
    }}
    /* ── Mobile: stack all st.columns vertically ── */
    /* st.columns renders as flex children; below 640px we override to full width
       so the 2-1-1 landing layout and all other column groups stack vertically. */
    @media (max-width: 640px) {{
        [data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }}
        .score-track-wrap {{
            max-width: 100%;
            padding: 0 0.5rem;
        }}
        .feat-body p {{ display: none; }}  /* hide desc on tiny screens to save space */
        .backlog-banner {{
            border-radius: 0 10px 10px 0;
            padding: 1rem 1.1rem;
        }}
    }}
    @media (max-width: 480px) {{
        .metric-item {{ width: 100%; }}
    }}

    /* ── Print Optimization ── */
    @media print {{
        [data-testid="stSidebar"],
        header,
        .stForm,
        .stButton,
        .feat-btn,
        .stApp > header {{
            display: none !important;
        }}
        .glass-card, .backlog-banner, .feat-card {{
            box-shadow: none !important;
            border: 1px solid #ddd !important;
            background: #fff !important;
            color: #000 !important;
            page-break-inside: avoid;
            animation: none !important;
        }}
        .metric-value, .metric-label, .result-hero .cgpa-number, .result-hero .cgpa-label {{
            color: #000 !important;
        }}
        body, .stApp {{
            background: #fff !important;
        }}
    }}
    """

def render_header(theme: Theme, title: str = "CGPA Calculator") -> None:
    """Page header — clean, no distracting widgets."""
    st.markdown(
        f"<h1 style='margin-bottom:0.15rem;font-size:1.55rem;font-weight:800;letter-spacing:-0.03em;'>{title}</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='font-size:0.8rem;color:var(--muted);margin-top:0;margin-bottom:1.5rem;'>Goa University · Engineering</p>",
        unsafe_allow_html=True
    )

def render_home_page(cgpa_page=None, sgpa_page=None, planner_page=None, guide_page=None):
    # ── Hero block with animated score track ──
    st.markdown("""
    <div class="hero">
        <span class="hero-eyebrow">Goa University &nbsp;·&nbsp; Engineering</span>
        <h1>Know your standing.<br>Plan your next move.</h1>
        <p>Track your CGPA, compute semester scores, and figure out exactly what it takes to hit your target — all in one place. Formulas are pre-set for Goa University, tweakable for any college.</p>
        <div class="score-track-wrap">
            <div class="score-track-header">
                <div class="score-track-labels"><span>0</span><span>5</span><span>10</span></div>
                <span class="score-track-example-chip">Example</span>
            </div>
            <div class="score-track-outer">
                <div class="score-track-fill" style="width: 85%;"></div>
            </div>
            <div class="score-track-caption">8.5 out of 10 &mdash; not your score, just an illustration</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature cards: 2-1-1 column ratio (CGPA dominant) ──
    col_cgpa, col_sgpa, col_plan = st.columns([2, 1, 1])

    with col_cgpa:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-stripe" style="background:var(--primary);"></div>
            <div class="feat-body">
                <h3>CGPA Calculator</h3>
                <p>Enter your semester SGPAs and credits. Get your overall CGPA, your US-GPA equivalent, percentage, trend analysis, and a projection for your final score.</p>
                <a href="cgpa" target="_self" class="feat-btn" style="background:var(--primary);">Open CGPA Calculator &rarr;</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_sgpa:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-stripe" style="background:var(--accent);"></div>
            <div class="feat-body">
                <h3>SGPA</h3>
                <p>Calculate a single semester from subject grades. Auto-fill subjects for your branch and year.</p>
                <a href="sgpa" target="_self" class="feat-btn" style="background:var(--accent);">Open &rarr;</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_plan:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-stripe" style="background:var(--success);"></div>
            <div class="feat-body">
                <h3>Goal Planner</h3>
                <p>Have a target CGPA? Find the SGPA you need to hit in your remaining semesters to get there.</p>
                <a href="planner" target="_self" class="feat-btn" style="background:var(--success);">Plan &rarr;</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if guide_page:
            st.markdown('<a href="guide" target="_self" class="large-guide-link">New here? Read the Guide &amp; FAQs</a>', unsafe_allow_html=True)

    # ── Sidebar discovery strip ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div style='border:1px solid var(--border);border-radius:14px;padding:1rem 1.25rem;background:var(--surface);'>
    <div style='font-size:0.78rem;font-weight:600;color:var(--muted);letter-spacing:0.06em;margin-bottom:0.65rem;text-transform:uppercase;'>
        <span>☰</span> &nbsp;Click the top-left icon to open the sidebar for:
    </div>
    <div style='display:flex;flex-wrap:wrap;gap:0.5rem;'>
        <span style='background:var(--primary)18;border:1px solid var(--primary)44;color:var(--primary);border-radius:20px;padding:0.25rem 0.75rem;font-size:0.8rem;'>🌙 Dark Mode toggle</span>
        <span style='background:var(--primary)18;border:1px solid var(--primary)44;color:var(--primary);border-radius:20px;padding:0.25rem 0.75rem;font-size:0.8rem;'>📚 Syllabus Scheme (RC 19-20 / NEP 2025 / Custom)</span>
        <span style='background:var(--primary)18;border:1px solid var(--primary)44;color:var(--primary);border-radius:20px;padding:0.25rem 0.75rem;font-size:0.8rem;'>🧮 CGPA Formula (Standard / Simple)</span>
        <span style='background:var(--primary)18;border:1px solid var(--primary)44;color:var(--primary);border-radius:20px;padding:0.25rem 0.75rem;font-size:0.8rem;'>% Percentage conversion (Goa / CBSE / Direct)</span>
        <span style='background:var(--primary)18;border:1px solid var(--primary)44;color:var(--primary);border-radius:20px;padding:0.25rem 0.75rem;font-size:0.8rem;'>Save & load your profile (JSON)</span>
    </div>
</div>
    """, unsafe_allow_html=True)

def render_compare_page():
    render_header(None, "Compare Profiles")
    st.markdown(
        "<p style='color:var(--muted);margin-top:-0.5rem;'>Compare your current performance vs your target goals, or see how you stack up against a friend's profile. Upload two saved JSON profiles below.</p>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='glass-card' style='padding: 1.5rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        use_active = st.checkbox("Use my current active profile", value=True, key="comp1_use_active", help="Uses the data you have currently entered in the CGPA/SGPA calculators.")
        if use_active:
            name1 = st.text_input("Name (Profile A)", value="My Current Profile", key="name1_input")
            file1, path1 = None, None
        else:
            name1 = st.text_input("Name (Profile A)", placeholder="e.g. My Freshman Year", key="name1_input")
            file1 = st.file_uploader("Upload Profile A", type=["json"], key="comp1",
                                      help="Upload a JSON profile downloaded from the Data Management sidebar.")
            path1 = st.text_input("Or paste local path:", placeholder=r"C:\path\to\p1.json", key="path1_input")
    with col2:
        name2 = st.text_input("Name (Profile B)", placeholder="e.g. Target Goals", key="name2_input")
        file2 = st.file_uploader("Upload Profile B", type=["json"], key="comp2")
        path2 = st.text_input("Or paste local path:", placeholder=r"C:\path\to\p2.json", key="path2_input")
    st.markdown("</div>", unsafe_allow_html=True)

    try:
        data1 = None
        data2 = None
        
        if use_active:
            # Reconstruct live CGPA state
            cgpa_state_live = st.session_state.get("cgpa_state", {}).copy()
            live_grades = []
            num_courses = st.session_state.get("cgpa_num_courses", cgpa_state_live.get("num_courses", 8))
            for i in range(num_courses):
                val = st.session_state.get(f"sgpa_{i}")
                if val is not None:
                    live_grades.append(float(val))
                elif len(cgpa_state_live.get("grades", [])) > i:
                    live_grades.append(cgpa_state_live["grades"][i])
                else:
                    live_grades.append(None)
            cgpa_state_live["grades"] = live_grades

            data1 = {
                "cgpa": cgpa_state_live,
                "sgpa": st.session_state.get("sgpa_state", {}),
                "planner": st.session_state.get("planner_state", {}),
                "settings": st.session_state.get("settings", {})
            }
        elif file1:
            data1 = json.loads(file1.getvalue().decode("utf-8"))
        elif path1 and os.path.exists(path1):
            with open(path1, "r", encoding="utf-8") as f:
                data1 = json.load(f)
                
        if file2:
            data2 = json.loads(file2.getvalue().decode("utf-8"))
        elif path2 and os.path.exists(path2):
            with open(path2, "r", encoding="utf-8") as f:
                data2 = json.load(f)

        if not data1 or not data2:
            st.markdown("""
            <div class='glass-card' style='text-align:center;padding:2.5rem 1.5rem;'>
                <span style='font-size:2rem;'>&#128194;</span>
                <p style='margin-top:0.75rem;color:var(--muted);font-size:0.9rem;'>Upload two profiles from the fields above, or paste their exact local file paths.</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Extract SGPA lists (fix bug: key is "cgpa", not "cgpa_state")
        cgpa1_state = data1.get("cgpa", {})
        cgpa2_state = data2.get("cgpa", {})
        
        grades1 = [g for g in cgpa1_state.get("grades", []) if g is not None]
        grades2 = [g for g in cgpa2_state.get("grades", []) if g is not None]
        
        # Determine labels
        def get_label(name, file_obj, path_str):
            if name.strip(): return name.strip()
            if file_obj: return file_obj.name.replace(".json", "")
            if path_str: return os.path.basename(path_str).replace(".json", "")
            return "Profile"
            
        label1 = get_label(name1, file1, path1)
        label2 = get_label(name2, file2, path2)
        
        df1 = pd.DataFrame({"Semester": range(1, len(grades1) + 1), "SGPA": grades1, "Profile": label1})
        df2 = pd.DataFrame({"Semester": range(1, len(grades2) + 1), "SGPA": grades2, "Profile": label2})
        
        df_combined = pd.concat([df1, df2])
        
        if not df_combined.empty:
            st.markdown(f"### {label1} vs {label2}")
            
            # Premium Plotly Chart
            fig = px.line(
                df_combined, 
                x="Semester", 
                y="SGPA", 
                color="Profile",
                markers=True,
                color_discrete_sequence=["#4F46E5", "#F59E0B"] # Indigo & Amber
            )
            fig.update_layout(
                yaxis=dict(range=[0, 10.5], title="SGPA"),
                xaxis=dict(title="Semester", tickmode="linear"),
                hovermode="x unified",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=40, l=40, r=40, b=40)
            )
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            st.plotly_chart(fig, width="stretch")
            
            # Summary Metrics
            st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
            
            def get_stats(grades):
                if not grades: return 0.0, 0.0, 0.0
                return sum(grades)/len(grades), max(grades), min(grades)
                
            avg1, max1, min1 = get_stats(grades1)
            avg2, max2, min2 = get_stats(grades2)
            
            st.markdown(f"""
            <div class='metrics-container'>
                <div class='metric-item' style='border-top: 3px solid #4F46E5;'>
                    <div class='metric-label'>{label1} - Average SGPA</div>
                    <div class='metric-value'>{avg1:.2f}</div>
                    <div style='font-size: 0.8rem; color: var(--muted); margin-top: 0.25rem;'>High: {max1:.2f} &bull; Low: {min1:.2f}</div>
                </div>
                <div class='metric-item' style='border-top: 3px solid #F59E0B;'>
                    <div class='metric-label'>{label2} - Average SGPA</div>
                    <div class='metric-value'>{avg2:.2f}</div>
                    <div style='font-size: 0.8rem; color: var(--muted); margin-top: 0.25rem;'>High: {max2:.2f} &bull; Low: {min2:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No grades found in the uploaded profiles.")
    except Exception as e:
        st.error(f"Error reading profiles: {e}")

def render_guide_page():
    st.title("📖 How it Works (Guide & FAQs)")
    
    st.markdown("### 1. The Basics (Explained Simply)")
    st.info("""
    **What is an SGPA?**  
    SGPA (Semester Grade Point Average) is your performance score for a *single semester*. It only calculates the grades from those specific subjects.
    
    **What is a CGPA?**  
    CGPA (Cumulative Grade Point Average) is your *overall* performance score. It combines all your SGPAs into one master score that represents your entire degree.
    
    **Why do 'Credits' matter?**  
    Credits represent the "weight" or importance of a subject. A 4-credit subject (like Engineering Math) heavily impacts your CGPA. A 1-credit subject (like a Lab) has a very minor impact. Scoring poorly in a high-credit subject will drop your overall score significantly, which is why the 'Standard (Accounts for credits)' setting is crucial.
    """)
    
    st.markdown("### 2. How we do the math")
    st.markdown("""
    Here are the formulas powering the calculators, just so you know exactly how your scores are computed:
    
    *   **Grade Scale:** When calculating SGPA, we use the standard UGC scale: `O = 10`, `A+ = 9`, `A = 8`, `B+ = 7`, `B = 6`, `C = 5`, `P = 4`, `F = 0`.
    *   **Standard CGPA:** This is the default. It's a weighted average based on your credits: `Sum of (Semester Credits × SGPA) ÷ Total Credits Completed`.
    *   **Simple CGPA:** Used by colleges like Mumbai University. You can toggle this in the settings. It ignores credits completely and just averages your SGPAs: `Sum of all SGPAs ÷ Number of Semesters`.
    *   **Percentage Formula:** By default, we use the Goa University conversion formula: `Percentage = (CGPA - 0.75) × 10`. 
    """)

    st.markdown("### 3. Making sense of the charts")
    st.info("""
    When you check your CGPA, the app runs some extra math to give you a better picture of how you're doing:
    *   **Trend Analysis:** We plot a line through your past SGPAs. If it points up, you're improving every semester.
    *   **Consistency Score:** This checks how much your grades jump around. A high score (90%+) means you're super consistent. A lower score means you have a mix of really good and really bad semesters.
    *   **Predictive Range:** We look at how much your past grades have fluctuated to guess what your final CGPA will probably look like by the time you graduate.
    """)

    st.markdown("### 4. Privacy (no servers used)")
    st.success("""
    **Your data stays on your device.**  
    When you enter your grades, they never leave your computer. There is no backend database and we aren't tracking you. Everything runs locally in your browser, and when you close the tab, your grades are gone.
    
    If you want to save them for next time, use the **Data Management** tab in the sidebar to download a tiny JSON file. You can just upload it next time you visit.
    """)
    
    st.markdown("### Frequently Asked Questions")
    
    with st.expander("I'm from a Goa University Engineering College. What should I do?"):
        st.write("Nothing! The app is pre-configured with the exact formulas and credit structures for DBCE, PCCE, GEC, RIT, and AITD. Just open a Calculator and start entering grades.")
        
    with st.expander("I'm from another University or Board. Can I still use this?"):
        st.write("Yes. Open **Calculation Settings** in the sidebar. You can switch the percentage conversion to CBSE or Mumbai University, and change the CGPA formula to ignore credits if needed.")
        
    with st.expander("Can I adjust the credits for a specific semester?"):
        st.write("Yes. Open **\u2699\ufe0f Calculation Settings** in the sidebar and set the *Syllabus Scheme* to **Custom (Enter manually)**. This will reveal credit input fields alongside the SGPA fields for every semester.")

    with st.expander("Are the default credits for RC 19-20 or RC 24-25?"):
        st.write(
            "The default credit structure follows the **RC 19-20** syllabus. "
            "If you are on the **NEP 2025** scheme, open **\u2699\ufe0f Calculation Settings** in the sidebar "
            "and switch the *Syllabus Scheme* to **NEP 2025 (20 credits/sem)**. "
            "If your college uses something else entirely, pick **Custom** to enter credits manually for each semester."
        )

    with st.expander("Why does my CGPA here slightly differ from my college portal?"):
        st.write("Your college might calculate CGPA differently. Check the **Calculation Settings** to ensure you are using the correct formula ('Standard' vs 'Simple') for your specific university.")

    with st.expander("What is a 'Good' Consistency Score?"):
        st.write("A score above 85% means your grades are highly stable. A lower score indicates high fluctuations (e.g., scoring an 9.0 one semester and a 6.0 the next).")

    with st.expander("How accurate is the Predictive Range?"):
        st.write("It is a statistical projection based on your historical variance. It assumes your future semesters will fluctuate by the same average amount as your past semesters. It is an estimate, not a guarantee.")

    with st.expander("Will I lose my grades when I close the app?"):
        st.write("Yes, unless you save them. Open the **Data Management** tab in the sidebar and click 'Download Profile'. This saves your grades to a tiny file on your computer. Upload it next time to restore your data.")

    with st.expander("📊 How are grades assigned from marks? (Subjectwise Range Table)"):
        st.write(
            "The table below shows how your raw marks are converted into letter grades "
            "based on the maximum marks for each subject (out of 150, 125, 100, 75, 50, or 25). "
            "Use this as a quick reference to figure out which letter grade a particular mark falls into."
        )
        _img_path = os.path.join(os.path.dirname(__file__), "grades_for_marks.jpg")
        if os.path.exists(_img_path):
            st.image(
                _img_path,
                caption="Subjectwise Range: Marks → Letter Grade → Grade Points",
                use_container_width=True,
            )
        else:
            st.warning("Grade reference image not found. Please ensure `src/grades_for_marks.jpg` exists.")

def render_inputs(initial_state: dict | None = None) -> tuple[bool, int, int, list[int], list[Optional[float]]]:
    """Render enhanced input form with HCD principles."""
    initial_state = initial_state or {}

    # Derive the current scheme from global settings (set in sidebar)
    scheme = st.session_state.get("settings", {}).get("syllabus_scheme", "rc1920")
    use_custom = (scheme == "custom")

    # Reset handler: seed credits from the active scheme
    if st.session_state.get("cgpa_reset_requested", False):
        st.session_state["cgpa_num_courses"] = DEFAULT_SEM_COUNT
        st.session_state["cgpa_completed_semesters"] = DEFAULT_SEM_COUNT
        scheme_credits = get_scheme_credits(scheme, DEFAULT_SEM_COUNT)
        for i in range(12):
            st.session_state[f"credit_{i}"] = int(scheme_credits[i] if i < len(scheme_credits) else scheme_credits[-1])
            st.session_state[f"sgpa_{i}"] = 8.0
        st.session_state["cgpa_reset_requested"] = False

    if "cgpa_num_courses" not in st.session_state:
        st.session_state["cgpa_num_courses"] = int(initial_state.get("num_courses", DEFAULT_SEM_COUNT))
    if "cgpa_completed_semesters" not in st.session_state:
        st.session_state["cgpa_completed_semesters"] = int(
            initial_state.get("completed_semesters", st.session_state["cgpa_num_courses"])
        )

    initial_credits = initial_state.get("credits", [])
    initial_grades = initial_state.get("grades", [])
    scheme_defaults = get_scheme_credits(scheme, 12)
    for i in range(12):
        c_key = f"credit_{i}"
        if c_key not in st.session_state:
            if i < len(initial_credits):
                st.session_state[c_key] = int(initial_credits[i])
            else:
                st.session_state[c_key] = int(scheme_defaults[i] if i < len(scheme_defaults) else scheme_defaults[-1])

        g_key = f"sgpa_{i}"
        if g_key not in st.session_state:
            if i < len(initial_grades):
                st.session_state[g_key] = float(initial_grades[i])
            else:
                st.session_state[g_key] = 0.0

    col_title, col_demo = st.columns([2, 1])
    with col_title:
        st.subheader("Academic Profile")
    with col_demo:
        if st.button("Load Demo Data", help="Test the calculator with a sample profile", use_container_width=True):
            st.session_state["cgpa_num_courses"] = 8
            st.session_state["cgpa_completed_semesters"] = 5
            demo_grades = [8.1, 7.8, 8.4, 8.2, 8.9]
            for i in range(12):
                st.session_state[f"sgpa_{i}"] = demo_grades[i] if i < len(demo_grades) else 0.0
            st.rerun()

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

    # Scheme info banner — no checkbox needed anymore
    st.markdown("---")
    if scheme == "rc1920":
        st.info(
            "\U0001f4da **RC 19-20** credits loaded automatically. "
            "Change scheme in **\u2699\ufe0f Calculation Settings** if needed.",
        )
    elif scheme == "nep2025":
        st.info(
            "\U0001f4da **NEP 2025** \u2014 20 credits per semester loaded automatically. "
            "Change scheme in **\u2699\ufe0f Calculation Settings** if needed.",
        )
    else:
        st.caption("\u270f\ufe0f **Custom** mode \u2014 enter your credits and SGPAs below.")

    with st.form("cgpa_form", clear_on_submit=False):
        credits: list[int] = []
        grades: list[Optional[float]] = []
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
                        is_backlog = st.checkbox(f"Backlog Pending", key=f"backlog_{i}")
                        current_sgpa = st.session_state.get(f"sgpa_{i}", 0.0)
                        label_prefix = "✅ " if current_sgpa > 0.0 else ""
                        grade = st.number_input(
                            f"{label_prefix}Semester {i + 1} SGPA",
                            min_value=0.0,
                            step=0.01,
                            key=f"sgpa_{i}",
                            disabled=is_backlog
                        )
                        grades.append(None if is_backlog else float(grade))
                        if not is_backlog and float(grade) > 10.0:
                            st.error("⚠️ SGPA > 10.0", icon="🚨")
                    else:
                        st.markdown("<div style='margin-top: 2.8rem; color: var(--muted); text-align: center; font-size: 0.9rem;'>Not completed</div>", unsafe_allow_html=True)
        else:
            # Auto-load credits from the active scheme — user only provides SGPAs
            active_credits = get_scheme_credits(scheme, num_courses)
            for i in range(num_courses):
                credits.append(active_credits[i])
                st.session_state[f"credit_{i}"] = active_credits[i]

            st.markdown("### SGPA")
            for i in range(0, completed_semesters, 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < completed_semesters:
                        with cols[j]:
                            is_backlog = st.checkbox(f"Backlog (Sem {i + j + 1})", key=f"backlog_{i+j}")
                            current_sgpa = st.session_state.get(f"sgpa_{i+j}", 0.0)
                            label_prefix = "✅ " if current_sgpa > 0.0 else ""
                            grade = st.number_input(
                                f"{label_prefix}Semester {i + j + 1} SGPA",
                                min_value=0.0,
                                step=0.01,
                                key=f"sgpa_{i+j}",
                                disabled=is_backlog
                            )
                            grades.append(None if is_backlog else float(grade))
                            if not is_backlog and float(grade) > 10.0:
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
            if st.button("Confirm", key="cgpa_confirm_clear", width="stretch"):
                st.session_state["cgpa_reset_requested"] = True
                if "cgpa_state" in st.query_params:
                    del st.query_params["cgpa_state"]
                st.session_state["cgpa_clear_pending"] = False
                st.toast("CGPA inputs cleared.", icon="🗑️")
                st.rerun()
        with col_cancel:
            if st.button("Cancel", key="cgpa_cancel_clear", width="stretch"):
                st.session_state["cgpa_clear_pending"] = False
                st.rerun()

    return submitted, num_courses, completed_semesters, credits, grades

def render_results(
    cgpa: Optional[float],
    percentage: float,
    total_credits: int,
    classification: str,
    breakdown,
    completed_semesters: int,
    num_courses: int,
    all_credits: list[int],
    settings: dict | None = None,
    status_code: str = "cleared"
) -> None:
    """Render CGPA results. Handles withheld state with explicit backlog banner."""
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    if status_code != "cleared" or cgpa is None:
        # Determine which semesters are blocked
        blocked_sems = []
        if isinstance(breakdown, pd.DataFrame) and not breakdown.empty:
            blocked_sems = breakdown[breakdown["SGPA"].isna()]["Semester"].tolist()
        sem_list = ", ".join(f"Semester {s}" for s in blocked_sems) if blocked_sems else "one or more semesters"
        st.markdown(f"""
<div class='backlog-banner'>
    <h4><span class='backlog-dot'>&#9679;</span>Your CGPA is on hold.</h4>
    <p>{sem_list} {'has' if len(blocked_sems) == 1 else 'have'} a backlog that needs to be cleared before we can calculate your overall score.
    Once your result is out, uncheck the Backlog box for that semester and enter the SGPA — your CGPA will compute immediately.</p>
    <span class='backlog-step'>What to do &rarr; Update the semester SGPA once results are declared</span>
</div>
        """, unsafe_allow_html=True)
    else:
        classification_color = get_classification_color(classification)
        us_gpa = (cgpa / 10.0) * 4.0
        # Big hero number, then secondary strip
        st.markdown(f"""
<div class='glass-card sticky-summary'>
    <div class='result-hero'>
        <span class='cgpa-number'>{cgpa:.2f}</span>
        <span class='cgpa-label'>Cumulative GPA &nbsp;&mdash;&nbsp; {completed_semesters} semester{'s' if completed_semesters != 1 else ''}</span>
        <div class='cgpa-standing'>
            <span class='status-badge' style='background:{classification_color}22;border:1.5px solid {classification_color};color:{classification_color};'>{classification}</span>
        </div>
    </div>
    <div class='metrics-container' style='margin-top:1.5rem;padding-top:1.25rem;border-top:1px solid var(--border);'>
        <div class='metric-item'>
            <div class='metric-label'>US GPA</div>
            <div class='metric-value'>{us_gpa:.2f}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Percentage</div>
            <div class='metric-value'>{percentage:.1f}%</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Credits</div>
            <div class='metric-value'>{total_credits}</div>
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
        if cgpa is not None:
            st.markdown(f"""
            **CGPA Formula**

            {cgpa_formula_str}

            **Your values**

            - Total weighted score: {weighted_sum:.2f}
            - Total credits: {total_credits}
            - Final CGPA: {cgpa:.2f}
            - Percentage: {percentage:.2f}% (using {pct_formula_str})
            - US GPA Equivalent: {(cgpa / 10.0) * 4.0:.2f} (using $(CGPA \\div 10) \\times 4.0$)
            """)
        else:
            st.markdown(f"**CGPA Formula**: {cgpa_formula_str}")

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
        
        if status_code == "cleared":
            st.markdown("---")
            st.subheader("Exports")
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                if st.button("Generate PDF Report"):
                    with st.spinner("Generating PDF..."):
                        # Generate a basic chart for the PDF (styled to match white PDF background)
                        fig_static = px.line(breakdown, x="Semester", y="SGPA", title="SGPA Trend")
                        fig_static.update_traces(line_color="#4F46E5", line_width=3)
                        fig_static.update_layout(
                            paper_bgcolor="white", 
                            plot_bgcolor="white", 
                            font_color="#111827",
                            title_font_color="#111827",
                            width=800,
                            height=400
                        )
                        try:
                            chart_bytes = fig_static.to_image(format="png")
                        except Exception:
                            chart_bytes = None
                        
                        pdf_data = generate_pdf_report(cgpa, percentage, classification, breakdown.to_dict('records'), chart_bytes)
                        st.session_state['pdf_export_data'] = pdf_data
                
                if 'pdf_export_data' in st.session_state:
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=st.session_state['pdf_export_data'],
                        file_name="academic_report.pdf",
                        mime="application/pdf",
                        type="primary"
                    )

            with col_export2:
                if st.button("Generate Shareable Card"):
                    with st.spinner("Generating PNG..."):
                        png_data = generate_shareable_card(cgpa, percentage, classification)
                        st.session_state['png_export_data'] = png_data
                        
                if 'png_export_data' in st.session_state:
                    st.download_button(
                        label="⬇️ Download PNG",
                        data=st.session_state['png_export_data'],
                        file_name="cgpa_card.png",
                        mime="image/png",
                        type="primary"
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
                st.plotly_chart(fig, width="stretch")
                
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

    scheme = st.session_state.get("settings", {}).get("syllabus_scheme", "rc1920")
    curriculum_data = load_curriculum()
    
    if curriculum_data:
        has_templates = scheme in ["rc1920", "nep2025"]
        with st.expander("Auto-fill from Template", expanded=has_templates):
            st.markdown("Select your syllabus and semester to automatically fill in the subjects and credits.")
            
            # Filter templates based on active scheme
            if scheme == "rc1920":
                valid_templates = [k for k in curriculum_data.keys() if "RC 2019-20" in k]
            elif scheme == "nep2025":
                valid_templates = [k for k in curriculum_data.keys() if "NEP 2025" in k]
            else:
                valid_templates = []
                
            if not valid_templates:
                scheme_label = "NEP 2025" if scheme == "nep2025" else "Custom"
                st.info(f"Auto-fill templates for **{scheme_label}** are not yet available. Please enter subjects manually below.", icon="ℹ️")
            else:
                col_b, col_s = st.columns(2)
                with col_b:
                    saved_branch = st.session_state.get("settings", {}).get("template_branch")
                    default_idx = 0
                    if saved_branch in valid_templates:
                        default_idx = valid_templates.index(saved_branch)
                    branch = st.selectbox("Syllabus", options=valid_templates, index=default_idx, key="template_branch")
                with col_s:
                    if branch:
                        sem = st.selectbox("Semester", options=list(curriculum_data[branch].keys()), key="template_sem")
            
            if st.button("Load Subjects", type="primary", width="stretch"):
                if branch and sem:
                    subjects_list = curriculum_data[branch][sem]
                    st.session_state["sgpa_num_subjects"] = len(subjects_list)
                    for i, subj in enumerate(subjects_list):
                        st.session_state[f"subject_name_{i}"] = subj["name"]
                        st.session_state[f"subject_credit_{i}"] = subj["credits"]
                        # Also default to grade 'A' to make it faster
                        st.session_state[f"subject_grade_{i}"] = "A"
                    st.session_state["sgpa_target_sem"] = sem
                    
                    # Persist selected branch
                    settings = st.session_state.get("settings", {})
                    settings["template_branch"] = branch
                    st.session_state["settings"] = settings
                    
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
                "<br>"
                "<b>Civil & Electrical & Electronics:</b> Sourced from official syllabus copies (not linked online)."
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

        st.markdown("---")
        st.selectbox(
            "Link result to CGPA calculator:",
            options=["None"] + [f"Semester {i}" for i in range(1, 13)],
            key="sgpa_target_sem",
            help="Automatically write this calculated SGPA into the CGPA form for the selected semester."
        )

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
            if st.button("Confirm", key="sgpa_confirm_clear", width="stretch"):
                st.session_state["sgpa_reset_requested"] = True
                if "sgpa_state" in st.query_params:
                    del st.query_params["sgpa_state"]
                st.session_state["sgpa_clear_pending"] = False
                st.toast("SGPA inputs cleared.", icon="🗑️")
                st.rerun()
        with col_cancel:
            if st.button("Cancel", key="sgpa_cancel_clear", width="stretch"):
                st.session_state["sgpa_clear_pending"] = False
                st.rerun()

    return submitted, subjects, credits, grade_points

def render_sgpa_results(sgpa: Optional[float], percentage: float, total_credits: int, breakdown, settings: dict | None = None, status_code: str = "cleared") -> None:
    """Render SGPA results with withheld-state handling."""
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    is_failed = bool((breakdown["Grade Point"] == 0.0).any()) if not breakdown.empty else False
    result_status = "FAILED" if is_failed else "PASSED"
    result_color = "#EF4444" if is_failed else "#10B981"
    failed_subjects = []
    if not breakdown.empty:
        failed_subjects = breakdown[breakdown["Grade Point"] == 0.0]["Subject"].tolist() if "Subject" in breakdown.columns else []
    
    if status_code != "cleared" or sgpa is None:
        subj_list = ", ".join(failed_subjects[:3]) if failed_subjects else "one or more subjects"
        suffix = " (and others)" if len(failed_subjects) > 3 else ""
        st.markdown(f"""
<div class='backlog-banner'>
    <h4><span class='backlog-dot'>&#9679;</span>SGPA is on hold.</h4>
    <p>{subj_list}{suffix} {'was' if len(failed_subjects) == 1 else 'were'} marked F.
    SGPA can only be computed once the backlog is cleared. Select a different grade once your result is out.</p>
    <span class='backlog-step'>What to do &rarr; Update the grade when the result is declared</span>
</div>
        """, unsafe_allow_html=True)
        
        # Render a "Pending" card instead of completely skipping it
        st.markdown(f"""
<div class='glass-card sticky-summary'>
    <div class='result-hero'>
        <span class='cgpa-number' style='font-size:2rem;'>Pending</span>
        <span class='cgpa-label'>Semester GPA</span>
        <div class='cgpa-standing'>
            <span class='status-badge' style='background:#F59E0B22;border:1.5px solid #F59E0B;color:#F59E0B;'>BACKLOG</span>
        </div>
    </div>
</div>""", unsafe_allow_html=True)
    else:
        us_gpa = (sgpa / 10.0) * 4.0
        st.markdown(f"""
<div class='glass-card sticky-summary'>
    <div class='result-hero'>
        <span class='cgpa-number'>{sgpa:.2f}</span>
        <span class='cgpa-label'>Semester GPA</span>
        <div class='cgpa-standing'>
            <span class='status-badge' style='background:{result_color}22;border:1.5px solid {result_color};color:{result_color};'>{result_status}</span>
        </div>
    </div>
    <div class='metrics-container' style='margin-top:1.5rem;padding-top:1.25rem;border-top:1px solid var(--border);'>
        <div class='metric-item'>
            <div class='metric-label'>US GPA</div>
            <div class='metric-value'>{us_gpa:.2f}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Percentage</div>
            <div class='metric-value'>{percentage:.1f}%</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Credits</div>
            <div class='metric-value'>{total_credits}</div>
        </div>
        <div class='metric-item'>
            <div class='metric-label'>Subjects</div>
            <div class='metric-value'>{len(breakdown)}</div>
        </div>
    </div>
</div>
        """, unsafe_allow_html=True)

    if is_failed and sgpa is not None:
        st.warning("One or more subjects received an F grade. Re-check the grades if this looks wrong.")

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
    if sgpa is not None:
        us_gpa = (sgpa / 10.0) * 4.0
        st.expander("How it's calculated").markdown(f"""
        **SGPA Formula**

        $SGPA = \\frac{{\\sum(GradePoint_i \\times Credits_i)}}{{\\sum(Credits_i)}}$

        **Your values**

        - Total weighted score: {float(breakdown["Weighted"].sum()):.2f}
        - Total credits: {total_credits}
        - Final SGPA: {sgpa:.2f}
        - Percentage: {percentage:.2f}% (using {pct_formula_str})
        - US GPA Equivalent: {us_gpa:.2f} (using $(SGPA \\div 10) \\times 4.0$)

        **Rule applied**

        - If any subject has grade **F** (grade point $0$), final SGPA is shown as **0.00 (Failed)**.
        """)

def render_planner_inputs(initial_state: dict | None = None) -> tuple[bool, float | None, int, float, int]:
    """Render target planner input form."""
    initial_state = initial_state or {}
    scheme = st.session_state.get("settings", {}).get("syllabus_scheme", "rc1920")
    is_custom = (scheme == "custom")

    # Apply reset before creating widgets to avoid Streamlit session-state mutation errors.
    if st.session_state.get("planner_reset_requested", False):
        st.session_state["planner_current_cgpa"] = 8.0
        st.session_state["planner_target_cgpa"] = 8.5
        if is_custom:
            st.session_state["planner_current_credits"] = 80
            st.session_state["planner_remaining_credits"] = 40
        else:
            st.session_state["planner_total_sems"] = 8
            st.session_state["planner_completed_sems"] = 4
        st.session_state["planner_reset_requested"] = False

    if "planner_current_cgpa" not in st.session_state:
        # Default to their actual calculated CGPA if they just ran the calculator, else None (blank)
        last_calc = st.session_state.get("calculated_cgpa")
        cgpa_val = initial_state.get("current_cgpa", last_calc)
        st.session_state["planner_current_cgpa"] = float(cgpa_val) if cgpa_val is not None else None
    if "planner_target_cgpa" not in st.session_state:
        st.session_state["planner_target_cgpa"] = float(initial_state.get("target_cgpa", 8.5))
        
    if is_custom:
        if "planner_current_credits" not in st.session_state:
            st.session_state["planner_current_credits"] = int(initial_state.get("current_credits", 80))
        if "planner_remaining_credits" not in st.session_state:
            st.session_state["planner_remaining_credits"] = int(initial_state.get("remaining_credits", 40))
    else:
        # Sync with CGPA inputs dynamically unless explicitly decoupled in this session
        cgpa_total = st.session_state.get("cgpa_num_courses", 8)
        cgpa_completed = st.session_state.get("cgpa_completed_semesters", 4)
        
        if "last_seen_cgpa_total" not in st.session_state or st.session_state["last_seen_cgpa_total"] != cgpa_total:
            st.session_state["planner_total_sems"] = max(2, cgpa_total)
            st.session_state["last_seen_cgpa_total"] = cgpa_total
            
        if "last_seen_cgpa_completed" not in st.session_state or st.session_state["last_seen_cgpa_completed"] != cgpa_completed:
            st.session_state["planner_completed_sems"] = max(1, min(cgpa_completed, st.session_state["planner_total_sems"] - 1))
            st.session_state["last_seen_cgpa_completed"] = cgpa_completed

        # Ensure they still exist as fallbacks
        if "planner_total_sems" not in st.session_state:
            st.session_state["planner_total_sems"] = max(2, cgpa_total)
        if "planner_completed_sems" not in st.session_state:
            st.session_state["planner_completed_sems"] = max(1, min(cgpa_completed, st.session_state["planner_total_sems"] - 1))

    col_title, col_demo = st.columns([2, 1])
    with col_title:
        st.subheader("Target Planner")
    with col_demo:
        if st.button("Load Demo Data", help="Test the planner with realistic sample stats", use_container_width=True):
            st.session_state["planner_current_cgpa"] = 8.12
            st.session_state["planner_target_cgpa"] = 8.5
            if is_custom:
                st.session_state["planner_current_credits"] = 100
                st.session_state["planner_remaining_credits"] = 60
            else:
                st.session_state["planner_total_sems"] = 8
                st.session_state["planner_completed_sems"] = 5
            st.rerun()

    with st.form("planner_form", clear_on_submit=False):
        current_cgpa = st.number_input(
            "Current CGPA",
            min_value=0.0,
            max_value=10.0,
            step=0.01,
            key="planner_current_cgpa",
        )
        if current_cgpa is not None:
            current_cgpa = float(current_cgpa)
        
        if is_custom:
            current_credits = int(st.number_input(
                "Completed credits",
                min_value=0,
                max_value=250,
                step=1,
                key="planner_current_credits",
            ))
        else:
            col1, col2 = st.columns(2)
            with col1:
                total_sems = int(st.number_input(
                    "Total Program Semesters",
                    min_value=2,
                    max_value=12,
                    step=1,
                    key="planner_total_sems"
                ))
            with col2:
                completed_sems = int(st.number_input(
                    "Completed Semesters",
                    min_value=1,
                    max_value=total_sems - 1,
                    step=1,
                    key="planner_completed_sems"
                ))
            
            scheme_credits = get_scheme_credits(scheme, total_sems)
            current_credits = sum(scheme_credits[:completed_sems])
            remaining_credits = sum(scheme_credits[completed_sems:])

        target_cgpa = float(st.number_input(
            "Target CGPA",
            min_value=0.0,
            max_value=10.0,
            step=0.01,
            key="planner_target_cgpa",
        ))
        
        if is_custom:
            remaining_credits = int(st.number_input(
                "Remaining credits",
                min_value=1,
                max_value=250,
                step=1,
                key="planner_remaining_credits",
            ))
        else:
            st.caption(f"Auto-derived from {scheme.upper()} scheme: **{current_credits} credits completed**, **{remaining_credits} credits remaining**.")

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
            if st.button("Confirm", key="planner_confirm_clear", width="stretch"):
                st.session_state["planner_reset_requested"] = True
                if "planner_state" in st.query_params:
                    del st.query_params["planner_state"]
                st.session_state["planner_clear_pending"] = False
                st.toast("Planner inputs cleared.", icon="🗑️")
                st.rerun()
        with col_cancel:
            if st.button("Cancel", key="planner_cancel_clear", width="stretch"):
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

    display_req = "> 10.00" if required_sgpa > 10.0 else ("< 0.00" if required_sgpa < 0.0 else f"{required_sgpa:.2f}")

    st.markdown(f"""
<div class='glass-card sticky-summary'>
    <div class='metrics-container'>
        <div class='metric-item'>
            <div class='metric-label'>Required SGPA</div>
            <div class='metric-value' style='color: var(--primary)'>{display_req}</div>
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

def render_update_cgpa_page(theme):
    render_header(theme, "Update CGPA")
    st.markdown(
        "<p style='color:var(--muted);margin-top:-0.5rem;'>Fast-forward your cumulative CGPA by rolling in new semesters without re-entering all past data.</p>",
        unsafe_allow_html=True
    )
    
    with st.container():
        st.markdown("### Base Profile")
        col1, col2, col3 = st.columns(3)
        with col1:
            old_cgpa = st.number_input("Last known CGPA", min_value=0.0, max_value=10.0, step=0.01, value=8.0, key="update_cgpa_old_cgpa")
        with col2:
            completed_sems = int(st.number_input("Completed through Sem", min_value=1, max_value=11, step=1, value=4, key="update_cgpa_completed_sems"))
        with col3:
            scheme = st.selectbox("Syllabus Scheme", options=["rc1920", "nep2025", "custom"], format_func=lambda x: "RC 19-20" if x == "rc1920" else ("NEP 2025" if x == "nep2025" else "Custom"), key="update_cgpa_scheme")
            
        old_credits = 0
        if scheme == 'custom':
            old_credits = int(st.number_input("Total Credits Earned (Base)", min_value=1, max_value=250, value=80, key="update_cgpa_old_credits"))
        else:
            from src.logic import get_scheme_credits
            scheme_credits = get_scheme_credits(scheme, completed_sems)
            old_credits = sum(scheme_credits[:completed_sems])
            st.caption(f"Auto-derived base credits: **{old_credits}**")
            
    st.markdown("---")
    st.markdown("### New Semesters to Add")
    
    num_new_sems = int(st.number_input("How many new semesters?", min_value=1, max_value=8, value=1, step=1, key="update_cgpa_num_new"))
    
    new_sgpas = []
    new_credits = []
    
    for i in range(num_new_sems):
        c1, c2 = st.columns(2)
        sem_idx = completed_sems + i + 1
        with c1:
            sgpa = st.number_input(f"Sem {sem_idx} SGPA", min_value=0.0, max_value=10.0, step=0.01, value=8.0, key=f"update_cgpa_new_sgpa_{i}")
            new_sgpas.append(float(sgpa))
        with c2:
            if scheme == 'custom':
                cred = st.number_input(f"Sem {sem_idx} Credits", min_value=1, max_value=35, value=20, key=f"update_cgpa_new_cred_{i}")
            else:
                from src.logic import get_scheme_credits
                # Pad to cover up to 12 sems safely
                full_credits = get_scheme_credits(scheme, 12)
                cred = full_credits[sem_idx - 1] if sem_idx <= len(full_credits) else 20
                st.markdown(f"<div style='margin-top: 2.8rem; color: var(--muted);'>Auto Credits: {cred}</div>", unsafe_allow_html=True)
            new_credits.append(int(cred))
            
    if st.button("Update CGPA", type="primary", use_container_width=True):
        from src.logic import update_cgpa_with_new_semester
        import pandas as pd
        
        current_cgpa = old_cgpa
        current_creds = old_credits
        
        rows = []
        rows.append({
            "Phase": "Base (Through Sem " + str(completed_sems) + ")",
            "SGPA/CGPA Added": f"{old_cgpa:.2f}",
            "Credits Added": old_credits,
            "Cumulative CGPA": f"{current_cgpa:.2f}"
        })
        
        for i in range(num_new_sems):
            sgpa = new_sgpas[i]
            cred = new_credits[i]
            sem_idx = completed_sems + i + 1
            
            new_cgpa = update_cgpa_with_new_semester(current_cgpa, current_creds, sgpa, cred)
            if new_cgpa is not None:
                current_cgpa = new_cgpa
                current_creds += cred
                
                rows.append({
                    "Phase": f"Add Sem {sem_idx}",
                    "SGPA/CGPA Added": f"{sgpa:.2f}",
                    "Credits Added": cred,
                    "Cumulative CGPA": f"{current_cgpa:.2f}"
                })
                
        st.success(f"### Final Updated CGPA: **{current_cgpa:.2f}**")
        st.table(pd.DataFrame(rows))
