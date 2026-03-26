# src/logic.py
"""
Core CGPA calculation logic (SOLID, testable, secure).
"""
import pandas as pd
import math
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
    base_sgpa = compute_cgpa(grade_points, credits)
    if base_sgpa is None:
        return None

    # Academic rule: if any credit-bearing subject is failed (F=0), SGPA is 0.
    if any(point == 0.0 and credit > 0 for point, credit in zip(grade_points, credits)):
        return 0.0

    return base_sgpa

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

def required_sgpa_for_target(
    current_cgpa: float,
    current_credits: int,
    target_cgpa: float,
    remaining_credits: int,
) -> Optional[float]:
    """Compute required SGPA over remaining credits to reach target CGPA."""
    if remaining_credits <= 0:
        return None
    if current_credits < 0:
        return None
    if not (0.0 <= current_cgpa <= 10.0 and 0.0 <= target_cgpa <= 10.0):
        return None

    total_credits = current_credits + remaining_credits
    if total_credits <= 0:
        return None

    target_total_points = target_cgpa * total_credits
    current_points = current_cgpa * current_credits
    return (target_total_points - current_points) / remaining_credits

def classify_target_feasibility(required_sgpa: float) -> str:
    """Classify feasibility status from required SGPA."""
    if required_sgpa <= 0:
        return "Already Achieved"
    if required_sgpa <= 10:
        return "Feasible"
    return "Not Feasible"

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

def semester_trend_slope(grades: List[float]) -> float:
    """Return linear trend slope for semester grades."""
    n = len(grades)
    if n < 2:
        return 0.0

    x_vals = [i + 1 for i in range(n)]
    x_mean = sum(x_vals) / n
    y_mean = sum(grades) / n

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, grades))
    denominator = sum((x - x_mean) ** 2 for x in x_vals)
    if denominator == 0:
        return 0.0
    return numerator / denominator

def consistency_score(grades: List[float]) -> float:
    """Return a consistency score in [0, 100] from SGPA variability."""
    n = len(grades)
    if n < 2:
        return 100.0

    mean = sum(grades) / n
    variance = sum((g - mean) ** 2 for g in grades) / n
    std_dev = math.sqrt(variance)
    score = 100.0 - (std_dev / 10.0) * 100.0
    return max(0.0, min(100.0, score))

def strongest_weakest_semester(grades: List[float]) -> dict:
    """Return strongest and weakest semester metadata."""
    if not grades:
        return {
            "strongest_semester": 0,
            "strongest_sgpa": 0.0,
            "weakest_semester": 0,
            "weakest_sgpa": 0.0,
        }

    strongest_idx = max(range(len(grades)), key=lambda i: grades[i])
    weakest_idx = min(range(len(grades)), key=lambda i: grades[i])
    return {
        "strongest_semester": strongest_idx + 1,
        "strongest_sgpa": grades[strongest_idx],
        "weakest_semester": weakest_idx + 1,
        "weakest_sgpa": grades[weakest_idx],
    }

def predict_final_cgpa_range(
    current_grades: List[float],
    current_credits: List[int],
    remaining_credits: int,
    minimum_future_sgpa: float = 6.0,
    realistic_future_sgpa: float = 8.0,
    best_future_sgpa: float = 9.5,
) -> Optional[dict]:
    """Predict final CGPA range from scenario assumptions."""
    if remaining_credits < 0:
        return None

    current_cgpa = compute_cgpa(current_grades, current_credits)
    current_total_credits = sum(current_credits)
    if current_cgpa is None or current_total_credits <= 0:
        return None

    total_credits = current_total_credits + remaining_credits
    if total_credits <= 0:
        return None

    current_points = current_cgpa * current_total_credits

    minimum_final = (current_points + minimum_future_sgpa * remaining_credits) / total_credits
    realistic_final = (current_points + realistic_future_sgpa * remaining_credits) / total_credits
    best_final = (current_points + best_future_sgpa * remaining_credits) / total_credits

    return {
        "minimum": minimum_final,
        "realistic": realistic_final,
        "best": best_final,
    }

def what_if_simulator(
    current_grades: List[float],
    current_credits: List[int],
    remaining_credits: int,
) -> Optional[dict]:
    """Return minimum/realistic/best case projection bundle."""
    return predict_final_cgpa_range(
        current_grades=current_grades,
        current_credits=current_credits,
        remaining_credits=remaining_credits,
        minimum_future_sgpa=6.0,
        realistic_future_sgpa=8.0,
        best_future_sgpa=9.5,
    )
