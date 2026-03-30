"""
Streamlit entry point for CGPA Calculator (modular, secure, production-ready).
Enhanced with comprehensive error handling, logging, and user feedback.
"""
import logging
import sys
import json
from typing import Optional, Tuple
from src.config import Theme, Config
from src.layout import inject_styles, render_header, render_inputs, render_planner_inputs, render_planner_results, render_results, render_sgpa_inputs, render_sgpa_results
from src.logic import build_breakdown, build_subject_breakdown, cgpa_to_percentage, classify_cgpa, classify_target_feasibility, compute_cgpa, compute_sgpa, required_sgpa_for_target, sgpa_to_percentage
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

PAGE_OPTIONS = ["CGPA Calculator", "SGPA Calculator", "Planner"]

def resolve_page_from_param(page_param: str) -> str:
    """Map URL page param to internal page label."""
    page = (page_param or "").strip().lower()
    if page == "sgpa":
        return "SGPA Calculator"
    if page == "planner":
        return "Planner"
    return "CGPA Calculator"

def page_to_param(page_name: str) -> str:
    """Map internal page label to URL page param."""
    if page_name == "SGPA Calculator":
        return "sgpa"
    if page_name == "Planner":
        return "planner"
    return "cgpa"

def track_event(event_name: str, payload: dict | None = None) -> None:
    """Record lightweight anonymous telemetry in session and logs."""
    payload = payload or {}
    counters = st.session_state.setdefault("telemetry_counters", {})
    counters[event_name] = counters.get(event_name, 0) + 1
    logger.info("telemetry event=%s payload=%s", event_name, payload)

def _query_get(key: str, default: str = "") -> str:
    value = st.query_params.get(key, default)
    if isinstance(value, list):
        return str(value[0]) if value else default
    return str(value)

def _load_page_state(page_key: str) -> dict:
    raw = _query_get(f"{page_key}_state", "")
    if not raw:
        return {}
    try:
        state = json.loads(raw)
        return state if isinstance(state, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}

def _save_page_state(page_key: str, state: dict) -> None:
    st.query_params[f"{page_key}_state"] = json.dumps(state, separators=(",", ":"))

def setup_environment() -> None:
    """Setup and validate application environment."""
    try:
        # Validate configuration
        Config.validate()
        logger.info("Environment validation successful")

        # Set up Streamlit configuration
        st.set_page_config(
            page_title="CGPA Calculator",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
        logger.info("Streamlit configuration initialized")

    except Exception as e:
        logger.error(f"Environment setup failed: {str(e)}")
        st.error(f"Application initialization failed: {str(e)}")
        st.stop()

def validate_inputs(
    num_courses: int,
    completed_semesters: int,
    credits: list[int],
    grades: list[float]
) -> Tuple[bool, Optional[str]]:
    """
    Validate user inputs with comprehensive error checking.

    Args:
        num_courses: Total number of semesters
        completed_semesters: Number of completed semesters
        credits: List of credits per semester
        grades: List of SGPA scores

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate semester counts
    if num_courses < 1 or num_courses > 12:
        return False, "Number of semesters must be between 1 and 12."

    if completed_semesters < 1 or completed_semesters > num_courses:
        return False, "Completed semesters must be between 1 and total semesters."

    # Validate credits
    if len(credits) != num_courses:
        return False, f"Expected {num_courses} credit entries, got {len(credits)}."

    for i, credit in enumerate(credits):
        if credit < 0 or credit > 35:
            return False, f"Semester {i+1} credits must be between 0 and 35."

    # Validate grades
    if len(grades) != completed_semesters:
        return False, f"Expected {completed_semesters} SGPA entries, got {len(grades)}."

    for i, grade in enumerate(grades):
        if grade < 0.0 or grade > 10.0:
            return False, f"Semester {i+1} SGPA must be between 0.0 and 10.0."

    return True, None

def validate_sgpa_inputs(
    subjects: list[str],
    credits: list[int],
    grade_points: list[float],
) -> Tuple[bool, Optional[str]]:
    """Validate SGPA inputs with comprehensive error checks."""
    if not subjects or not credits or not grade_points:
        return False, "Subject details are required to compute SGPA."

    if len(subjects) != len(credits) or len(subjects) != len(grade_points):
        return False, "Subject names, credits, and grade points must have the same length."

    for i, credit in enumerate(credits):
        if credit < 0 or credit > 35:
            return False, f"Subject {i + 1} credits must be between 0 and 35."

    for i, gp in enumerate(grade_points):
        if gp < 0.0 or gp > 10.0:
            return False, f"Subject {i + 1} grade point must be between 0.0 and 10.0."

    if sum(credits) <= 0:
        return False, "Total credits must be greater than 0."

    return True, None

def handle_calculation_error(error: str) -> None:
    """
    Handle calculation errors with user-friendly messages and logging.

    Args:
        error: Error message to display
    """
    logger.error(f"CGPA calculation error: {error}")

    st.error(error)

    with st.expander("Troubleshooting"):
        st.markdown("""
        - Check SGPA values are between 0.0 and 10.0
        - Make sure completed semesters and grades match
        - Ensure total credits are greater than 0
        """)

def main() -> None:
    """Main application entry point with enhanced error handling."""
    try:
        # Setup environment and configuration
        setup_environment()
        logger.info("Application started successfully")

        # Initialize theme and UI
        theme = Theme()
        inject_styles(theme)
        page_param = _query_get("page", "cgpa")
        default_page = resolve_page_from_param(page_param)

        page = st.sidebar.radio(
            "Navigate",
            PAGE_OPTIONS,
            index=PAGE_OPTIONS.index(default_page),
        )

        st.markdown("### Navigation")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("CGPA", key="top_nav_cgpa", use_container_width=True, type="primary" if page == "CGPA Calculator" else "secondary"):
                st.query_params["page"] = "cgpa"
                st.rerun()
        with col2:
            if st.button("SGPA", key="top_nav_sgpa", use_container_width=True, type="primary" if page == "SGPA Calculator" else "secondary"):
                st.query_params["page"] = "sgpa"
                st.rerun()
        with col3:
            if st.button("Planner", key="top_nav_planner", use_container_width=True, type="primary" if page == "Planner" else "secondary"):
                st.query_params["page"] = "planner"
                st.rerun()

        track_event("page_view", {"page": page})

        selected_page_param = page_to_param(page)
        if _query_get("page", "").lower() != selected_page_param:
            st.query_params["page"] = selected_page_param

        if page == "CGPA Calculator":
            render_header(theme, "CGPA Calculator")

            initial_state = _load_page_state("cgpa")

            # Get user inputs
            submitted, num_courses, completed_semesters, credits, grades = render_inputs(initial_state)

            _save_page_state(
                "cgpa",
                {
                    "num_courses": num_courses,
                    "completed_semesters": completed_semesters,
                    "use_custom": bool(st.session_state.get("cgpa_use_custom", False)),
                    "credits": credits,
                    "grades": grades,
                },
            )

            if submitted:
                logger.info(f"Calculation requested: {completed_semesters} semesters, {num_courses} total")

                # Validate inputs before processing
                is_valid, validation_error = validate_inputs(num_courses, completed_semesters, credits, grades)

                if not is_valid:
                    handle_calculation_error(f"Input validation failed: {validation_error}")
                    return

                try:
                    # Process effective data (only completed semesters)
                    effective_credits = credits[:completed_semesters]
                    effective_grades = grades[:completed_semesters]

                    logger.info(f"Processing {len(effective_grades)} semesters with {sum(effective_credits)} total credits")

                    # Compute CGPA with error handling
                    cgpa = compute_cgpa(effective_grades, effective_credits)

                    if cgpa is None:
                        handle_calculation_error("Unable to compute CGPA. Please check your credits and SGPA entries.")
                        return

                    # Calculate additional metrics
                    total_credits = sum(effective_credits)
                    classification = classify_cgpa(cgpa)
                    percentage = cgpa_to_percentage(cgpa)
                    breakdown = build_breakdown(completed_semesters, effective_credits, effective_grades)

                    logger.info(f"CGPA calculation successful: {cgpa:.2f} ({classification})")

                    # Render results
                    render_results(
                        cgpa,
                        percentage if percentage is not None else 0.0,
                        total_credits,
                        classification,
                        breakdown,
                        completed_semesters,
                        num_courses,
                        credits,
                    )
                    track_event("cgpa_calculated", {"completed_semesters": completed_semesters, "total_semesters": num_courses})

                except Exception as calc_error:
                    handle_calculation_error(f"Calculation failed: {str(calc_error)}")
        else:
            if page == "SGPA Calculator":
                render_header(theme, "SGPA Calculator")

                initial_state = _load_page_state("sgpa")
                submitted, subjects, credits, grade_points = render_sgpa_inputs(initial_state)

                grade_letters = [str(st.session_state.get(f"subject_grade_{i}", "A")) for i in range(len(subjects))]
                _save_page_state(
                    "sgpa",
                    {
                        "num_subjects": len(subjects),
                        "subjects": subjects,
                        "credits": credits,
                        "grades": grade_letters,
                    },
                )

                if submitted:
                    is_valid, validation_error = validate_sgpa_inputs(subjects, credits, grade_points)
                    if not is_valid:
                        handle_calculation_error(f"Input validation failed: {validation_error}")
                        return

                    try:
                        sgpa = compute_sgpa(grade_points, credits)
                        if sgpa is None:
                            handle_calculation_error("Unable to compute SGPA. Please verify your inputs.")
                            return

                        percentage = sgpa_to_percentage(sgpa)
                        breakdown = build_subject_breakdown(subjects, credits, grade_points)
                        render_sgpa_results(sgpa, percentage if percentage is not None else 0.0, sum(credits), breakdown)
                        track_event("sgpa_calculated", {"subjects": len(subjects)})
                    except Exception as sgpa_error:
                        handle_calculation_error(f"Calculation failed: {str(sgpa_error)}")
            else:
                render_header(theme, "Planner")
                initial_state = _load_page_state("planner")
                submitted, current_cgpa, current_credits, target_cgpa, remaining_credits = render_planner_inputs(initial_state)

                _save_page_state(
                    "planner",
                    {
                        "current_cgpa": current_cgpa,
                        "current_credits": current_credits,
                        "target_cgpa": target_cgpa,
                        "remaining_credits": remaining_credits,
                    },
                )

                if submitted:
                    required = required_sgpa_for_target(
                        current_cgpa=current_cgpa,
                        current_credits=current_credits,
                        target_cgpa=target_cgpa,
                        remaining_credits=remaining_credits,
                    )

                    if required is None:
                        handle_calculation_error("Unable to compute planner result. Please verify your inputs.")
                        return

                    feasibility = classify_target_feasibility(required)
                    render_planner_results(
                        required_sgpa=required,
                        feasibility=feasibility,
                        current_cgpa=current_cgpa,
                        current_credits=current_credits,
                        target_cgpa=target_cgpa,
                        remaining_credits=remaining_credits,
                    )
                    track_event("planner_calculated", {"feasibility": feasibility})

        # Footer with resources
        st.markdown("---")
        gdrive_link = "https://drive.google.com/file/d/1JyIgnGSZpeBphGtcoDdaj8eXnVvROFb8/view?usp=drivesdk"
        st.markdown(f"[CGPA Calculation Guide]({gdrive_link})")

        logger.info("Application execution completed")

    except Exception as app_error:
        logger.critical(f"Critical application error: {str(app_error)}", exc_info=True)
        st.error(f"Critical error: {str(app_error)}. Please try refreshing the page.")
        if Config.DEBUG:
            st.exception(app_error)

if __name__ == "__main__":
    main()
