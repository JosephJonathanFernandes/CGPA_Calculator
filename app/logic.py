from __future__ import annotations

import pandas as pd

DEFAULT_CREDITS = [16, 18, 23, 24, 22, 22, 17, 18]
DEFAULT_SEM_COUNT = len(DEFAULT_CREDITS)


def padded_default_credits(num_semesters: int) -> list[int]:
    """Ensure default credits match the selected semester count."""
    if num_semesters <= DEFAULT_SEM_COUNT:
        return DEFAULT_CREDITS[:num_semesters]
    padding = [DEFAULT_CREDITS[-1]] * (num_semesters - DEFAULT_SEM_COUNT)
    return DEFAULT_CREDITS + padding


def compute_cgpa(grades: list[float], credits: list[int]) -> float | None:
    if len(grades) != len(credits):
        return None
    total_credits = sum(credits)
    if total_credits <= 0:
        return None
    weighted_sum = sum(grade * credit for grade, credit in zip(grades, credits))
    return weighted_sum / total_credits


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


def build_breakdown(completed_semesters: int, credits: list[int], grades: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Semester": [i + 1 for i in range(completed_semesters)],
            "Credits": credits,
            "SGPA": grades,
            "Weighted": [g * c for g, c in zip(grades, credits)],
        }
    )
