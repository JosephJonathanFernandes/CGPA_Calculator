"""
Streamlit entry point for CGPA Calculator (modular, secure, production-ready).
Enhanced with comprehensive error handling, logging, and user feedback.
"""
import logging
import sys
import json
from typing import Optional, Tuple
from src.config import get_theme, Config
from src.layout import inject_styles, render_header, render_inputs, render_planner_inputs, render_planner_results, render_results, render_sgpa_inputs, render_sgpa_results, render_home_page, render_guide_page, render_compare_page
from src.logic import build_breakdown, build_subject_breakdown, cgpa_to_percentage, classify_cgpa, classify_target_feasibility, compute_cgpa, compute_sgpa, required_sgpa_for_target, sgpa_to_percentage
import streamlit as st
from streamlit_local_storage import LocalStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def track_event(event_name: str, payload: dict | None = None) -> None:
    """Record lightweight anonymous telemetry in session and logs."""
    payload = payload or {}
    counters = st.session_state.setdefault("telemetry_counters", {})
    counters[event_name] = counters.get(event_name, 0) + 1
    logger.info("telemetry event=%s payload=%s", event_name, payload)

def _load_page_state(page_key: str) -> dict:
    if f"{page_key}_state" not in st.session_state:
        return {}
    return st.session_state[f"{page_key}_state"]

def _save_page_state(page_key: str, state: dict) -> None:
    st.session_state[f"{page_key}_state"] = state

def setup_environment() -> None:
    """Setup and validate application environment."""
    try:
        Config.validate()
        st.set_page_config(
            page_title="CGPA Calculator",
            layout="centered",
            initial_sidebar_state="expanded"
        )
    except Exception as e:
        logger.error(f"Environment setup failed: {str(e)}")
        st.error(f"Application initialization failed: {str(e)}")
        st.stop()

def validate_inputs(num_courses: int, completed_semesters: int, credits: list[int], grades: list[float]) -> Tuple[bool, Optional[str]]:
    if num_courses < 1 or num_courses > 12: return False, "Number of semesters must be between 1 and 12."
    if completed_semesters < 1 or completed_semesters > num_courses: return False, "Completed semesters must be between 1 and total semesters."
    if len(credits) != num_courses: return False, f"Expected {num_courses} credit entries."
    for i, credit in enumerate(credits):
        if credit < 0 or credit > 35: return False, f"Semester {i+1} credits must be between 0 and 35."
    if len(grades) != completed_semesters: return False, f"Expected {completed_semesters} SGPA entries."
    for i, grade in enumerate(grades):
        if grade < 0.0 or grade > 10.0: return False, f"Semester {i+1} SGPA must be between 0.0 and 10.0."
    return True, None

def validate_sgpa_inputs(subjects: list[str], credits: list[int], grade_points: list[float]) -> Tuple[bool, Optional[str]]:
    if not subjects or not credits or not grade_points: return False, "Subject details are required to compute SGPA."
    if len(subjects) != len(credits) or len(subjects) != len(grade_points): return False, "Subject lengths mismatch."
    for i, credit in enumerate(credits):
        if credit < 0 or credit > 35: return False, f"Subject {i + 1} credits must be between 0 and 35."
    for i, gp in enumerate(grade_points):
        if gp < 0.0 or gp > 10.0: return False, f"Subject {i + 1} grade point must be between 0.0 and 10.0."
    if sum(credits) <= 0: return False, "Total credits must be greater than 0."
    return True, None

def handle_calculation_error(error: str) -> None:
    logger.error(f"Calculation error: {error}")
    st.error(error)

def render_cgpa_page(theme, localS: LocalStorage):
    render_header(theme, "CGPA Calculator")

    st.markdown(
        "<p style='font-size:0.83rem;color:var(--muted);margin-top:-0.5rem;'>"
        "<b>Sidebar tip:</b> change your <b>Syllabus Scheme</b> (RC 19-20 / NEP 2025 / Custom), "
        "switch the CGPA formula, pick a percentage conversion, or save your profile."
        "</p>",
        unsafe_allow_html=True
    )
    
    initial_state = _load_page_state("cgpa")
    submitted, num_courses, completed_semesters, credits, grades = render_inputs(initial_state)

    if not st.session_state.get("cgpa_clear_pending", False):
        _save_page_state("cgpa", {
            "num_courses": num_courses,
            "completed_semesters": completed_semesters,
            "syllabus_scheme": st.session_state.get("settings", {}).get("syllabus_scheme", "rc1920"),
            "credits": credits,
            "grades": grades,
        })
        # Sync manually entered CGPA grid grades to localStorage
        if st.session_state.get("storage_consent"):
            cgpa_data = {}
            for i in range(12):
                if f"sgpa_{i}" in st.session_state:
                    cgpa_data[f"sgpa_{i}"] = st.session_state[f"sgpa_{i}"]
            localS.setItem("cgpa_data", json.dumps(cgpa_data))

    if submitted:
        is_valid, validation_error = validate_inputs(num_courses, completed_semesters, credits, grades)
        if not is_valid:
            handle_calculation_error(f"Input validation failed: {validation_error}")
            return
        try:
            with st.status("Rendering analytics...", expanded=False) as status:
                st.write("Validating semester credits...")
                effective_credits = credits[:completed_semesters]
                effective_grades = grades[:completed_semesters]
                cgpa_dict = compute_cgpa(effective_grades, effective_credits, method=st.session_state.get("settings", {}).get("cgpa_method", "weighted"))
                cgpa = cgpa_dict.get("cgpa")
                status_code = cgpa_dict.get("status")
                
                if cgpa is not None:
                    st.session_state["calculated_cgpa"] = cgpa
                    
                if status_code == "error":
                    status.update(label="Calculation failed", state="error")
                    handle_calculation_error("Unable to compute CGPA.")
                    return
                
                st.write("Applying university formulas...")
                total_credits = sum(effective_credits)
                
                if cgpa is not None:
                    classification = classify_cgpa(cgpa)
                    percentage = cgpa_to_percentage(cgpa, formula=st.session_state.get("settings", {}).get("pct_formula", "mu"))
                else:
                    classification = "Withheld"
                    percentage = 0.0
                
                st.write("Building analytics breakdown...")
                breakdown = build_breakdown(completed_semesters, effective_credits, effective_grades)
                status.update(label="Analytics generated!", state="complete")
            
            render_results(cgpa, percentage if percentage is not None else 0.0, total_credits, classification, breakdown, completed_semesters, num_courses, credits, st.session_state.get("settings", {}), status_code=status_code)
            st.toast("CGPA calculation successful!", icon="🎉")
            track_event("cgpa_calculated", {"completed_semesters": completed_semesters})
            
            if cgpa is not None:
                if cgpa >= 10.0:
                    st.balloons()
                elif max(effective_grades) == effective_grades[-1] and len(effective_grades) > 1:
                    st.toast("New Personal Best SGPA! 🏆", icon="🏆")
        except Exception as calc_error:
            handle_calculation_error(f"Calculation failed: {str(calc_error)}")

def render_sgpa_page(theme, localS: LocalStorage):
    render_header(theme, "SGPA Calculator")
    initial_state = _load_page_state("sgpa")
    submitted, subjects, credits, grade_points = render_sgpa_inputs(initial_state)

    grade_letters = [str(st.session_state.get(f"subject_grade_{i}", "A")) for i in range(len(subjects))]
    if not st.session_state.get("sgpa_clear_pending", False):
        _save_page_state("sgpa", {
            "num_subjects": len(subjects),
            "subjects": subjects,
            "credits": credits,
            "grades": grade_letters,
            "grade_map": st.session_state.get("custom_grade_map"),
        })

    if submitted:
        is_valid, validation_error = validate_sgpa_inputs(subjects, credits, grade_points)
        if not is_valid:
            handle_calculation_error(f"Input validation failed: {validation_error}")
            return
        try:
            with st.status("Calculating SGPA...", expanded=False) as status:
                st.write("Mapping grade points...")
                sgpa_dict = compute_sgpa(grade_points, credits)
                sgpa = sgpa_dict.get("sgpa")
                status_code = sgpa_dict.get("status")
                
                if status_code == "error":
                    status.update(label="Calculation failed", state="error")
                    handle_calculation_error("Unable to compute SGPA.")
                    return
                
                st.write("Applying formulas...")
                if sgpa is not None:
                    percentage = sgpa_to_percentage(sgpa, formula=st.session_state.get("settings", {}).get("pct_formula", "mu"))
                else:
                    percentage = 0.0
                
                st.write("Generating breakdown...")
                breakdown = build_subject_breakdown(subjects, credits, grade_points)
                status.update(label="Calculation complete!", state="complete")
                
            render_sgpa_results(sgpa, percentage if percentage is not None else 0.0, sum(credits), breakdown, st.session_state.get("settings", {}), status_code=status_code)
            st.toast("SGPA calculation successful!", icon="🎉")
            
            target_sem_val = st.session_state.get("sgpa_target_sem", "None")
            if target_sem_val != "None" and sgpa is not None and status_code != "error":
                try:
                    sem_idx = int(target_sem_val.split(" ")[1]) - 1
                    st.session_state[f"sgpa_{sem_idx}"] = sgpa
                    st.toast(f"Linked SGPA {sgpa:.2f} to {target_sem_val} in CGPA Calculator!", icon="🔗")
                    
                    if st.session_state.get("storage_consent"):
                        cgpa_data = {}
                        for i in range(12):
                            if f"sgpa_{i}" in st.session_state:
                                cgpa_data[f"sgpa_{i}"] = st.session_state[f"sgpa_{i}"]
                        localS.setItem("cgpa_data", json.dumps(cgpa_data))
                except Exception:
                    pass
            track_event("sgpa_calculated", {"subjects": len(subjects)})
            if sgpa is not None and sgpa >= 10.0:
                st.balloons()
        except Exception as sgpa_error:
            handle_calculation_error(f"Calculation failed: {str(sgpa_error)}")

def render_planner_page(theme):
    render_header(theme, "Planner")
    initial_state = _load_page_state("planner")
    submitted, current_cgpa, current_credits, target_cgpa, remaining_credits = render_planner_inputs(initial_state)

    if not st.session_state.get("planner_clear_pending", False):
        _save_page_state("planner", {
            "current_cgpa": current_cgpa,
            "current_credits": current_credits,
            "target_cgpa": target_cgpa,
            "remaining_credits": remaining_credits,
        })

    if submitted:
        if current_cgpa is None:
            handle_calculation_error("Please enter your current CGPA.")
            return
        try:
            required = required_sgpa_for_target(current_cgpa, current_credits, target_cgpa, remaining_credits)
            if required is None:
                handle_calculation_error("Remaining credits must be > 0 to compute target.")
                return
            feasibility = classify_target_feasibility(required)
            render_planner_results(required, feasibility, current_cgpa, current_credits, target_cgpa, remaining_credits)
            st.toast("Planner updated!", icon="✨")
            track_event("planner_calculated", {"feasibility": feasibility})
        except Exception as err:
            handle_calculation_error(f"Calculation failed: {str(err)}")

def render_footer():
    st.markdown("---")
    gdrive_link = "https://drive.google.com/file/d/1JyIgnGSZpeBphGtcoDdaj8eXnVvROFb8/view?usp=drivesdk"
    st.caption(
        f"[Goa University CGPA Calculation Guide]({gdrive_link}) · "
        "Default formulas follow Goa University Engineering. "
        "If you're at a different college, adjust in the Calculation Settings sidebar."
    )

def main() -> None:
    try:
        setup_environment()
        
        # Local Storage Initialization
        localS = LocalStorage()
        
        # Auto-load logic
        if not st.session_state.get("storage_loaded", False):
            consent_given = localS.getItem("consent_given")
            if str(consent_given).lower() == "true":
                st.session_state["storage_consent"] = True
                cgpa_data = localS.getItem("cgpa_data")
                if cgpa_data:
                    try:
                        parsed_data = json.loads(cgpa_data) if isinstance(cgpa_data, str) else cgpa_data
                        for k, v in parsed_data.items():
                            st.session_state[k] = v
                    except Exception:
                        pass
            elif str(consent_given).lower() == "false":
                st.session_state["storage_consent"] = False
            st.session_state["storage_loaded"] = True
            
        # Sidebar Settings
        dark_mode = st.sidebar.toggle("Dark Mode", value=st.session_state.get("dark_mode", False), key="dark_mode")
        theme = get_theme(dark_mode)
        inject_styles(theme)
        
        with st.sidebar.expander("⚙️ Calculation Settings", expanded=True):
            st.markdown("<span style='font-size: 0.85rem; color: var(--muted);'>Not sure? Leave these as standard!</span>", unsafe_allow_html=True)
            saved_settings = st.session_state.get("settings", {})
            
            syllabus_scheme = st.selectbox(
                "Syllabus Scheme:",
                options=["rc1920", "nep2025", "custom"],
                format_func=lambda x: "RC 19-20 (Goa Uni Default)" if x == "rc1920" else (
                    "NEP 2025 (20 credits/sem)" if x == "nep2025" else "Custom (Enter manually)"
                ),
                key="sidebar_syllabus_scheme",
                help="RC 19-20 is the standard for DBCE, PCCE, GEC etc. Select NEP 2025 for the new uniform credit scheme, or Custom to enter credits manually."
            )
            calc_method = st.selectbox(
                "How to calculate CGPA?",
                options=["weighted", "simple_average"],
                format_func=lambda x: "Standard (Accounts for credits)" if x == "weighted" else "Simple (Ignores credits)",
                key="sidebar_cgpa_method",
                help="If your university uses credits (like Goa University), pick Standard."
            )
            pct_formula = st.selectbox(
                "Convert to Percentage:",
                options=["mu", "cbse", "direct"],
                format_func=lambda x: "Goa / Mumbai Uni (CGPA - 0.75)×10" if x == "mu" else ("CBSE / AICTE (CGPA × 9.5)" if x == "cbse" else "Direct Multiply (CGPA × 10)"),
                key="sidebar_pct_formula",
                help="Different boards use different math. Pick the one your college follows."
            )
            st.session_state["settings"] = {
                "syllabus_scheme": st.session_state.get("sidebar_syllabus_scheme", "rc1920"),
                "cgpa_method": st.session_state.get("sidebar_cgpa_method", "weighted"),
                "pct_formula": st.session_state.get("sidebar_pct_formula", "mu")
            }

        with st.sidebar.expander("💾 Data Management", expanded=True):
            current_state = {
                "cgpa": _load_page_state("cgpa"),
                "sgpa": _load_page_state("sgpa"),
                "planner": _load_page_state("planner"),
                "settings": st.session_state["settings"]
            }
            json_state = json.dumps(current_state, indent=2)
            st.download_button(
                label="Download Profile",
                data=json_state,
                file_name="cgpa_profile.json",
                mime="application/json",
                width="stretch",
            )
            
            uploaded_file = st.file_uploader("Upload Profile", type=["json"])
            if uploaded_file is not None:
                try:
                    uploaded_state = json.load(uploaded_file)
                    if st.button("Load Data", width="stretch", type="primary"):
                        if "cgpa" in uploaded_state: _save_page_state("cgpa", uploaded_state["cgpa"])
                        if "sgpa" in uploaded_state: _save_page_state("sgpa", uploaded_state["sgpa"])
                        if "planner" in uploaded_state: _save_page_state("planner", uploaded_state["planner"])
                        if "settings" in uploaded_state:
                            st.session_state["settings"] = uploaded_state["settings"]
                            st.session_state["sidebar_syllabus_scheme"] = uploaded_state["settings"].get("syllabus_scheme", "rc1920")
                            st.session_state["sidebar_cgpa_method"] = uploaded_state["settings"].get("cgpa_method", "weighted")
                            st.session_state["sidebar_pct_formula"] = uploaded_state["settings"].get("pct_formula", "mu")
                        st.toast("Profile loaded successfully!", icon="✅")
                        st.rerun()
                except json.JSONDecodeError:
                    st.error("Invalid JSON file.")
            
            st.markdown("---")
            consent_status = localS.getItem("consent_given")
            if str(consent_status).lower() == "true":
                st.session_state["storage_consent"] = True
                st.success("Browser storage active.", icon="✅")
                if st.button("Forget my data", key="forget_data", type="secondary"):
                    localS.deleteAll()
                    st.session_state["storage_consent"] = False
                    st.toast("Browser data erased.", icon="🗑️")
                    st.rerun()
            elif str(consent_status).lower() == "false":
                if st.button("Enable Browser Storage"):
                    localS.setItem("consent_given", "true")
                    st.session_state["storage_consent"] = True
                    st.rerun()
            else:
                st.info("This app can remember your SGPA values in your browser so you don't have to re-enter them next visit. Nothing is sent to a server; it stays on this device.")
                colA, colB = st.columns(2)
                with colA:
                    if st.button("Allow", key="allow_storage"):
                        localS.setItem("consent_given", "true")
                        st.session_state["storage_consent"] = True
                        st.rerun()
                with colB:
                    if st.button("Decline", key="decline_storage"):
                        localS.setItem("consent_given", "false")
                        st.session_state["storage_consent"] = False
                        st.rerun()

        # Navigation
        cgpa_page = st.Page(lambda: render_cgpa_page(theme, localS), title="CGPA", url_path="cgpa", icon="📊")
        guide_page = st.Page(lambda: render_guide_page(), title="How it Works", url_path="guide", icon="📖")
        sgpa_page = st.Page(lambda: render_sgpa_page(theme, localS), title="SGPA", url_path="sgpa", icon="📝")
        planner_page = st.Page(lambda: render_planner_page(theme), title="Goal Planner", url_path="planner", icon="🎯")
        compare_page = st.Page(lambda: render_compare_page(), title="Compare Profiles", url_path="compare", icon="⚖️")
        home_page = st.Page(lambda: render_home_page(cgpa_page, sgpa_page, planner_page, guide_page), title="Home", url_path="home", icon="🏠", default=True)
        
        pg = st.navigation({
            "": [home_page],
            "Calculators": [cgpa_page, sgpa_page, planner_page],
            "Analysis": [compare_page],
            "Help": [guide_page]
        })
        
        pg.run()
        render_footer()
        
    except Exception as app_error:
        logger.critical(f"Critical application error: {str(app_error)}", exc_info=True)
        st.error(f"Critical error: {str(app_error)}. Please try refreshing the page.")
        if Config.DEBUG:
            st.exception(app_error)

if __name__ == "__main__":
    main()
