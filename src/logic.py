# src/logic.py
"""
Core CGPA calculation logic (SOLID, testable, secure).
"""
import pandas as pd
import math
from typing import List, Optional

# RC 19-20 syllabus credit structure (Goa University Engineering)
RC1920_CREDITS = [16, 18, 23, 24, 22, 22, 17, 18]
# NEP 2025 syllabus credit structure (uniform 20 credits per semester)
NEP2025_CREDITS = [20, 20, 20, 20, 20, 20, 20, 20]
# Alias kept for backward compatibility
DEFAULT_CREDITS = RC1920_CREDITS
DEFAULT_SEM_COUNT = len(DEFAULT_CREDITS)

_SCHEME_CREDIT_MAP: dict[str, List[int]] = {
    "rc1920": RC1920_CREDITS,
    "nep2025": NEP2025_CREDITS,
}

def get_scheme_credits(scheme: str, num_semesters: int | None = None) -> List[int]:
    """Return the credit array for the given syllabus scheme key.
    
    Args:
        scheme: One of 'rc1920', 'nep2025', or 'custom'.
                'custom' returns an empty list — caller must supply their own.
        num_semesters: If provided, pads or trims the credit list to match.
    """
    base = list(_SCHEME_CREDIT_MAP.get(scheme, RC1920_CREDITS))
    if num_semesters is not None:
        if num_semesters <= len(base):
            return base[:num_semesters]
        padding = [base[-1]] * (num_semesters - len(base))
        return base + padding
    return base

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

def compute_cgpa(grades: List[Optional[float]], credits: List[int], method: str = "weighted") -> dict:
    """Compute CGPA and return a status dict."""
    if len(grades) != len(credits):
        return {"cgpa": None, "status": "error"}
    if not grades or not credits:
        return {"cgpa": None, "status": "error"}

    # Check for blocked semesters
    if any(grade is None for grade in grades):
        pending = [i + 1 for i, grade in enumerate(grades) if grade is None]
        return {"cgpa": None, "status": "blocked", "blocked_semesters": pending}

    # Keep core validation aligned with UI constraints.
    if any(grade < 0.0 or grade > 10.0 for grade in grades):
        return {"cgpa": None, "status": "error"}
    if any(credit < 0 or credit > 35 for credit in credits):
        return {"cgpa": None, "status": "error"}

    if method == "simple_average":
        return {"cgpa": sum(grades) / len(grades), "status": "cleared"}

    total_credits = sum(credits)
    if total_credits <= 0:
        return {"cgpa": None, "status": "error"}
    weighted_sum = sum(grade * credit for grade, credit in zip(grades, credits))
    return {"cgpa": weighted_sum / total_credits, "status": "cleared"}

def compute_sgpa(grade_points: List[Optional[float]], credits: List[int]) -> dict:
    """Compute SGPA using subject-wise grade points and credits. Returns status dict."""
    if not grade_points or not credits or len(grade_points) != len(credits):
        return {"sgpa": None, "status": "error"}
        
    if any(gp is None for gp in grade_points):
        return {"sgpa": None, "status": "invalid_input"}

    # Academic rule: if any credit-bearing subject is failed (F=0), SGPA is pending backlog.
    if any(point == 0.0 and credit > 0 for point, credit in zip(grade_points, credits)):
        return {"sgpa": None, "status": "backlog_pending"}

    base_sgpa = compute_cgpa(grade_points, credits)
    return {"sgpa": base_sgpa.get("cgpa"), "status": "cleared"}

def grade_letter_to_point(letter: str) -> Optional[float]:
    """Convert grade letter to grade point."""
    if not letter:
        return None
    return GRADE_POINT_MAP.get(letter.strip().upper())

def cgpa_to_percentage(cgpa: float, formula: str = "mu") -> Optional[float]:
    """Convert CGPA to percentage using the specified formula."""
    if cgpa < 0.0 or cgpa > 10.0:
        return None
    if formula == "cbse":
        return cgpa * 9.5
    elif formula == "direct":
        return cgpa * 10.0
    # default to mu: (CGPA - 0.75) * 10
    return (cgpa - 0.75) * 10

def sgpa_to_percentage(sgpa: float, formula: str = "mu") -> Optional[float]:
    """Convert SGPA to percentage using the specified formula."""
    if sgpa < 0.0 or sgpa > 10.0:
        return None
    if formula == "cbse":
        return sgpa * 9.5
    elif formula == "direct":
        return sgpa * 10.0
    # default to mu: (SGPA - 0.75) * 10
    return (sgpa - 0.75) * 10

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

def build_breakdown(completed_semesters: int, credits: List[int], grades: List[Optional[float]]) -> pd.DataFrame:
    weighted = []
    for g, c in zip(grades, credits):
        if g is None:
            weighted.append(None)
        else:
            weighted.append(g * c)
            
    return pd.DataFrame(
        {
            "Semester": [i + 1 for i in range(completed_semesters)],
            "Credits": credits,
            "SGPA": grades,
            "Weighted": weighted,
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

def semester_trend_slope(grades: List[Optional[float]]) -> float:
    """Return linear trend slope for semester grades (ignores None)."""
    valid_grades = [g for g in grades if g is not None]
    n = len(valid_grades)
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

def consistency_score(grades: List[Optional[float]]) -> float:
    """Return a consistency score in [0, 100] from SGPA variability."""
    valid_grades = [g for g in grades if g is not None]
    n = len(valid_grades)
    if n < 2:
        return 100.0

    mean = sum(valid_grades) / n
    variance = sum((g - mean) ** 2 for g in valid_grades) / n
    std_dev = math.sqrt(variance)
    score = 100.0 - (std_dev / 10.0) * 100.0
    return max(0.0, min(100.0, score))

def strongest_weakest_semester(grades: List[Optional[float]]) -> dict:
    """Return strongest and weakest semester metadata."""
    valid_grades = [g for g in grades if g is not None]
    if not valid_grades:
        return {
            "strongest_semester": 0,
            "strongest_sgpa": 0.0,
            "weakest_semester": 0,
            "weakest_sgpa": 0.0,
        }

    # We want original indexes (1-based semester) for the strongest/weakest, so we must iterate over the original list
    valid_indices = [i for i, g in enumerate(grades) if g is not None]
    strongest_idx = max(valid_indices, key=lambda i: grades[i])
    weakest_idx = min(valid_indices, key=lambda i: grades[i])
    return {
        "strongest_semester": strongest_idx + 1,
        "strongest_sgpa": grades[strongest_idx],
        "weakest_semester": weakest_idx + 1,
        "weakest_sgpa": grades[weakest_idx],
    }

def predict_final_cgpa_range(
    current_grades: List[Optional[float]],
    current_credits: List[int],
    remaining_credits: int,
    minimum_future_sgpa: float = 6.0,
    realistic_future_sgpa: float = 8.0,
    best_future_sgpa: float = 9.5,
) -> Optional[dict]:
    """Predict final CGPA range from scenario assumptions."""
    if remaining_credits < 0:
        return None

    cgpa_dict = compute_cgpa(current_grades, current_credits)
    current_cgpa = cgpa_dict.get("cgpa")
    
    # We only compute credits for cleared semesters
    current_total_credits = sum(c for g, c in zip(current_grades, current_credits) if g is not None)
    
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
    current_grades: List[Optional[float]],
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
