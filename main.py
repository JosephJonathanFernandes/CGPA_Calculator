"""
Streamlit entry point for CGPA Calculator (modular, secure, production-ready).
Enhanced with comprehensive error handling, logging, and user feedback.
"""
import logging
import sys
from typing import Optional, Tuple
from src.config import Theme, Config
from src.layout import inject_styles, render_header, render_inputs, render_results
from src.logic import build_breakdown, classify_cgpa, compute_cgpa
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
        st.error(f"🚨 Application initialization failed: {str(e)}")
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

def handle_calculation_error(error: str) -> None:
    """
    Handle calculation errors with user-friendly messages and logging.

    Args:
        error: Error message to display
    """
    logger.error(f"CGPA calculation error: {error}")

    # Enhanced error display with troubleshooting tips
    st.error(f"🚨 {error}")

    with st.expander("❓ Troubleshooting Help"):
        st.markdown("""
        **Common Issues and Solutions:**

        - **Invalid Inputs**: Check that all SGPA scores are between 0.0 and 10.0
        - **Missing Data**: Ensure you've entered data for all completed semesters
        - **Credit Mismatch**: Verify credits match your actual course load
        - **Zero Credits**: At least one semester must have credits > 0

        **Need more help?** Contact support or check our documentation.
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
        render_header(theme)

        # Get user inputs
        submitted, num_courses, completed_semesters, credits, grades = render_inputs()

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
                breakdown = build_breakdown(completed_semesters, effective_credits, effective_grades)

                logger.info(f"CGPA calculation successful: {cgpa:.2f} ({classification})")

                # Render results
                render_results(
                    cgpa,
                    total_credits,
                    classification,
                    breakdown,
                    completed_semesters,
                    num_courses,
                )

                # Success feedback
                st.success("✅ CGPA calculation completed successfully!")

            except Exception as calc_error:
                handle_calculation_error(f"Calculation failed: {str(calc_error)}")

        # Footer with resources
        st.markdown("---")
        gdrive_link = "https://drive.google.com/file/d/1JyIgnGSZpeBphGtcoDdaj8eXnVvROFb8/view?usp=drivesdk"
        st.markdown(f"📚 [View CGPA Calculation Guide]({gdrive_link})")
        st.caption("🎓 Built for quick academic tracking with Human-Centered Design principles.")

        logger.info("Application execution completed")

    except Exception as app_error:
        logger.critical(f"Critical application error: {str(app_error)}", exc_info=True)
        st.error(f"🚨 Critical error: {str(app_error)}. Please try refreshing the page.")
        if Config.DEBUG:
            st.exception(app_error)

if __name__ == "__main__":
    main()
