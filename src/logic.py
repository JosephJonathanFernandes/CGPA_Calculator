# src/logic.py
"""
Core CGPA calculation logic (SOLID, testable, secure).
"""
import pandas as pd
from typing import List, Optional

DEFAULT_CREDITS = [16, 18, 23, 24, 22, 22, 17, 18]
DEFAULT_SEM_COUNT = len(DEFAULT_CREDITS)
GRADE_POINT_MAP = {
    "O": 10.0,
    "A+": 9.0,
    "A": 8.0,
    "B+": 7.0,
    "B": 6.0,
    "C": 5.0,
    "P": 4.0,
    "F": 0.0,
}

def padded_default_credits(num_semesters: int) -> List[int]:
    """Ensure default credits match the selected semester count."""
    if num_semesters <= DEFAULT_SEM_COUNT:
        return DEFAULT_CREDITS[:num_semesters]
    padding = [DEFAULT_CREDITS[-1]] * (num_semesters - DEFAULT_SEM_COUNT)
    return DEFAULT_CREDITS + padding

def compute_cgpa(grades: List[float], credits: List[int]) -> Optional[float]:
    if len(grades) != len(credits):
        return None
    if not grades or not credits:
        return None

    # Keep core validation aligned with UI constraints.
    if any(grade < 0.0 or grade > 10.0 for grade in grades):
        return None
    if any(credit < 0 or credit > 35 for credit in credits):
        return None

    total_credits = sum(credits)
    if total_credits <= 0:
        return None
    weighted_sum = sum(grade * credit for grade, credit in zip(grades, credits))
    return weighted_sum / total_credits

def compute_sgpa(grade_points: List[float], credits: List[int]) -> Optional[float]:
    """Compute SGPA using subject-wise grade points and credits."""
    return compute_cgpa(grade_points, credits)

def grade_letter_to_point(letter: str) -> Optional[float]:
    """Convert grade letter to grade point."""
    if not letter:
        return None
    return GRADE_POINT_MAP.get(letter.strip().upper())

def gpa_to_percentage(gpa: float) -> Optional[float]:
    """Convert GPA value to percentage using 9.5 multiplier."""
    if gpa < 0.0 or gpa > 10.0:
        return None
    return gpa * 9.5

def cgpa_to_percentage(cgpa: float) -> Optional[float]:
    """Convert CGPA to percentage."""
    return gpa_to_percentage(cgpa)

def sgpa_to_percentage(sgpa: float) -> Optional[float]:
    """Convert SGPA to percentage."""
    return gpa_to_percentage(sgpa)

def classify_cgpa(cgpa: float) -> str:
    if cgpa >= 9:
        return "Outstanding"
    if cgpa >= 8:
        return "Excellent"
    if cgpa >= 7:
        return "Good"
    if cgpa >= 6:
        return "Satisfactory"
    return "Needs improvement"

def build_breakdown(completed_semesters: int, credits: List[int], grades: List[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Semester": [i + 1 for i in range(completed_semesters)],
            "Credits": credits,
            "SGPA": grades,
            "Weighted": [g * c for g, c in zip(grades, credits)],
        }
    )

def build_subject_breakdown(subjects: List[str], credits: List[int], grade_points: List[float]) -> pd.DataFrame:
    """Build SGPA table from subject-level inputs."""
    return pd.DataFrame(
        {
            "Subject": subjects,
            "Credits": credits,
            "Grade Point": grade_points,
            "Weighted": [g * c for g, c in zip(grade_points, credits)],
        }
    )
