"""
Integration-style tests for navigation mapping and calculator flows.
"""
import unittest

from src.logic import (
    build_breakdown,
    build_subject_breakdown,
    classify_target_feasibility,
    compute_cgpa,
    compute_sgpa,
    required_sgpa_for_target,
)


class TestNavigationIntegration(unittest.TestCase):
    """Integration tests for navigation mapping logic."""

    def test_cgpa_flow(self):
        grades = [8.2, 7.9, 8.5, 9.0]
        credits = [20, 22, 18, 20]

        cgpa = compute_cgpa(grades, credits).get("cgpa")
        self.assertIsNotNone(cgpa)

        breakdown = build_breakdown(4, credits, grades)
        self.assertEqual(len(breakdown), 4)
        self.assertIn("Weighted", breakdown.columns)

    def test_sgpa_flow(self):
        subjects = ["Math", "DS", "DBMS"]
        credits = [4, 3, 3]
        grade_points = [9.0, 8.0, 10.0]

        sgpa = compute_sgpa(grade_points, credits).get("sgpa")
        self.assertIsNotNone(sgpa)

        breakdown = build_subject_breakdown(subjects, credits, grade_points)
        self.assertEqual(len(breakdown), 3)
        self.assertIn("Grade Point", breakdown.columns)

    def test_planner_flow(self):
        required = required_sgpa_for_target(
            current_cgpa=8.1,
            current_credits=90,
            target_cgpa=8.5,
            remaining_credits=30,
        )
        self.assertIsNotNone(required)

        feasibility = classify_target_feasibility(required)
        self.assertIn(feasibility, {"Already Achieved", "Feasible", "Not Feasible"})


if __name__ == "__main__":
    unittest.main()
