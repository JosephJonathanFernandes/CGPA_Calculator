# tests/test_logic.py
"""
Comprehensive unit tests for CGPA Calculator core logic.
Includes edge cases, boundary testing, and error conditions.
"""
import unittest
from src.logic import (
    DEFAULT_CREDITS,
    DEFAULT_SEM_COUNT,
    cgpa_to_percentage,
    classify_target_feasibility,
    classify_cgpa,
    consistency_score,
    compute_cgpa,
    compute_sgpa,
    grade_letter_to_point,
    padded_default_credits,
    predict_final_cgpa_range,
    required_sgpa_for_target,
    semester_trend_slope,
    sgpa_to_percentage,
    strongest_weakest_semester,
    what_if_simulator,
)

class TestCGPALogic(unittest.TestCase):
    """Test suite for CGPA calculation logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_grades = [8.0, 9.0, 7.5, 8.5]
        self.valid_credits = [20, 22, 18, 20]
        self.expected_cgpa = (8.0*20 + 9.0*22 + 7.5*18 + 8.5*20) / (20+22+18+20)

    def test_compute_cgpa_valid(self):
        """Test valid CGPA calculation with typical inputs."""
        result = compute_cgpa(self.valid_grades, self.valid_credits).get("cgpa")
        self.assertAlmostEqual(result, self.expected_cgpa, places=2)

    def test_compute_cgpa_boundary_values(self):
        """Test boundary values for grades and credits."""
        # Minimum valid grades (0.0)
        result = compute_cgpa([0.0, 0.0], [10, 10]).get("cgpa")
        self.assertEqual(result, 0.0)

        # Maximum valid grades (10.0)
        result = compute_cgpa([10.0, 10.0], [10, 10]).get("cgpa")
        self.assertEqual(result, 10.0)

        # Mixed boundary values
        result = compute_cgpa([0.0, 10.0], [10, 10]).get("cgpa")
        self.assertEqual(result, 5.0)

    def test_compute_cgpa_edge_cases(self):
        """Test edge cases and error conditions."""
        # Empty lists
        self.assertIsNone(compute_cgpa([], []).get("cgpa"))

        # Mismatched lengths
        self.assertIsNone(compute_cgpa([8.0, 9.0], [20]).get("cgpa"))
        self.assertIsNone(compute_cgpa([8.0], [20, 22]).get("cgpa"))

        # Zero total credits
        self.assertIsNone(compute_cgpa([8.0], [0]).get("cgpa"))
        self.assertIsNone(compute_cgpa([8.0, 9.0], [0, 0]).get("cgpa"))

        # Single semester
        result = compute_cgpa([7.5], [20]).get("cgpa")
        self.assertEqual(result, 7.5)

    def test_compute_cgpa_precision(self):
        """Test calculation precision with floating point values."""
        grades = [8.333, 9.666, 7.125]
        credits = [18, 22, 20]
        expected = (8.333*18 + 9.666*22 + 7.125*20) / (18+22+20)
        result = compute_cgpa(grades, credits).get("cgpa")
        self.assertAlmostEqual(result, expected, places=3)

    def test_classify_cgpa_boundaries(self):
        """Test classification boundaries with precise values."""
        # Test exact boundaries
        self.assertEqual(classify_cgpa(9.0), "Outstanding")  # Exact boundary
        self.assertEqual(classify_cgpa(8.999), "Excellent")  # Just below
        self.assertEqual(classify_cgpa(9.001), "Outstanding")  # Just above

        self.assertEqual(classify_cgpa(8.0), "Excellent")
        self.assertEqual(classify_cgpa(7.999), "Good")
        self.assertEqual(classify_cgpa(8.001), "Excellent")

        self.assertEqual(classify_cgpa(7.0), "Good")
        self.assertEqual(classify_cgpa(6.999), "Satisfactory")
        self.assertEqual(classify_cgpa(7.001), "Good")

        self.assertEqual(classify_cgpa(6.0), "Satisfactory")
        self.assertEqual(classify_cgpa(5.999), "Needs improvement")
        self.assertEqual(classify_cgpa(6.001), "Satisfactory")

    def test_classify_cgpa_extreme_values(self):
        """Test classification with extreme values."""
        self.assertEqual(classify_cgpa(0.0), "Needs improvement")
        self.assertEqual(classify_cgpa(10.0), "Outstanding")
        self.assertEqual(classify_cgpa(5.0), "Needs improvement")

    def test_padded_default_credits(self):
        """Test default credits padding functionality."""
        # Test with default semester count
        result = padded_default_credits(DEFAULT_SEM_COUNT)
        self.assertEqual(result, DEFAULT_CREDITS)

        # Test with fewer semesters
        result = padded_default_credits(4)
        self.assertEqual(result, DEFAULT_CREDITS[:4])

        # Test with more semesters (should pad with last value)
        result = padded_default_credits(DEFAULT_SEM_COUNT + 2)
        expected = DEFAULT_CREDITS + [DEFAULT_CREDITS[-1], DEFAULT_CREDITS[-1]]
        self.assertEqual(result, expected)

        # Test with single semester
        result = padded_default_credits(1)
        self.assertEqual(result, [DEFAULT_CREDITS[0]])

    def test_compute_cgpa_with_various_credit_distributions(self):
        """Test CGPA calculation with different credit distributions."""
        # Equal credits
        result = compute_cgpa([7.0, 8.0, 9.0], [20, 20, 20]).get("cgpa")
        self.assertAlmostEqual(result, 8.0, places=2)

        # Unequal credits (weighted average)
        result = compute_cgpa([7.0, 8.0, 9.0], [10, 20, 30]).get("cgpa")
        expected = (7.0*10 + 8.0*20 + 9.0*30) / 60
        self.assertAlmostEqual(result, expected, places=2)

        # Very uneven credits
        result = compute_cgpa([5.0, 9.0], [5, 30]).get("cgpa")
        expected = (5.0*5 + 9.0*30) / 35
        self.assertAlmostEqual(result, expected, places=2)

    def test_compute_cgpa_error_conditions(self):
        """Test various error conditions that should return None."""
        # Negative credits
        self.assertIsNone(compute_cgpa([8.0], [-5]).get("cgpa"))

        # Negative grades (though input validation should prevent this)
        self.assertIsNone(compute_cgpa([-1.0], [20]).get("cgpa"))

        # Extremely large values
        self.assertIsNone(compute_cgpa([8.0], [10000]).get("cgpa"))
        self.assertIsNone(compute_cgpa([100.0], [20]).get("cgpa"))

    def test_classification_consistency(self):
        """Test that classification is consistent across similar values."""
        # Test that values very close to boundaries are classified consistently
        test_cases = [
            (8.99, "Excellent"),
            (9.00, "Outstanding"),
            (9.01, "Outstanding"),
            (7.99, "Good"),
            (8.00, "Excellent"),
            (8.01, "Excellent"),
        ]

        for cgpa, expected in test_cases:
            with self.subTest(cgpa=cgpa):
                self.assertEqual(classify_cgpa(cgpa), expected)

    def test_grade_letter_mapping(self):
        """Test grade-letter to grade-point mapping."""
        self.assertEqual(grade_letter_to_point("O"), 10.0)
        self.assertEqual(grade_letter_to_point("A+"), 9.0)
        self.assertEqual(grade_letter_to_point("A"), 8.0)
        self.assertEqual(grade_letter_to_point("P"), 4.0)
        self.assertEqual(grade_letter_to_point("F"), 0.0)
        self.assertIsNone(grade_letter_to_point("D"))
        self.assertIsNone(grade_letter_to_point("E"))
        self.assertIsNone(grade_letter_to_point("Z"))

    def test_compute_sgpa_fail_rule(self):
        """SGPA must be None if any credit-bearing subject is failed."""
        self.assertIsNone(compute_sgpa([9.0, 0.0, 8.0], [4, 3, 3]).get("sgpa"))

    def test_compute_sgpa_no_fail(self):
        """SGPA should follow weighted average when no subject is failed."""
        expected = (9.0 * 4 + 8.0 * 3 + 7.0 * 3) / 10
        self.assertAlmostEqual(compute_sgpa([9.0, 8.0, 7.0], [4, 3, 3]).get("sgpa"), expected, places=3)

    def test_gpa_percentage_conversion(self):
        """Test CGPA/SGPA percentage conversion using formula (GPA - 0.75) × 10."""
        # (8.0 - 0.75) × 10 = 72.5
        self.assertAlmostEqual(cgpa_to_percentage(8.0), 72.5, places=2)
        # (9.0 - 0.75) × 10 = 82.5
        self.assertAlmostEqual(sgpa_to_percentage(9.0), 82.5, places=2)
        self.assertIsNone(cgpa_to_percentage(11.0))
        self.assertIsNone(sgpa_to_percentage(-1.0))

    def test_required_sgpa_for_target(self):
        """Test planner required-SGPA calculations."""
        result = required_sgpa_for_target(8.0, 80, 8.5, 40)
        self.assertAlmostEqual(result, 9.5, places=2)

        # Already achieved target should yield <= 0 required SGPA
        result = required_sgpa_for_target(9.2, 100, 8.5, 5)
        self.assertLessEqual(result, 0.0)

        # Invalid remaining credits
        self.assertIsNone(required_sgpa_for_target(8.0, 80, 8.5, 0))

    def test_target_feasibility_classification(self):
        """Test planner feasibility labels."""
        self.assertEqual(classify_target_feasibility(-0.2), "Already Achieved")
        self.assertEqual(classify_target_feasibility(8.75), "Feasible")
        self.assertEqual(classify_target_feasibility(10.5), "Not Feasible")

    def test_smarter_analytics_metrics(self):
        """Test trend slope, consistency score, strongest/weakest outputs."""
        grades = [7.0, 7.5, 8.0, 8.5]
        slope = semester_trend_slope(grades)
        self.assertGreater(slope, 0.0)

        consistency = consistency_score(grades)
        self.assertGreaterEqual(consistency, 0.0)
        self.assertLessEqual(consistency, 100.0)

        extremes = strongest_weakest_semester(grades)
        self.assertEqual(extremes["strongest_semester"], 4)
        self.assertEqual(extremes["weakest_semester"], 1)

    def test_prediction_and_what_if_simulator(self):
        """Test final CGPA projections for minimum/realistic/best cases."""
        current_grades = [8.0, 8.2, 8.4]
        current_credits = [20, 20, 20]
        remaining_credits = 40

        prediction = predict_final_cgpa_range(current_grades, current_credits, remaining_credits)
        self.assertIsNotNone(prediction)
        self.assertLessEqual(prediction["minimum"], prediction["realistic"])
        self.assertLessEqual(prediction["realistic"], prediction["best"])

        scenarios = what_if_simulator(current_grades, current_credits, remaining_credits)
        self.assertIsNotNone(scenarios)
        self.assertIn("minimum", scenarios)
        self.assertIn("realistic", scenarios)
        self.assertIn("best", scenarios)


    def test_build_breakdown_logic(self):
        from src.logic import build_breakdown, build_subject_breakdown
        import pandas as pd
        df = build_breakdown(3, [20, 20, 20], [8.0, None, 9.0])
        self.assertTrue(isinstance(df, pd.DataFrame))
        df_sub = build_subject_breakdown(['A', 'B'], [3, 4], [8.0, 9.0])
        self.assertTrue(isinstance(df_sub, pd.DataFrame))
        
    def test_analytics_edge_cases(self):
        from src.logic import semester_trend_slope, consistency_score, strongest_weakest_semester
        self.assertEqual(semester_trend_slope([8.0]), 0.0)
        self.assertEqual(consistency_score([8.0]), 100.0)
        self.assertEqual(consistency_score([8.0, 8.0, 8.0]), 100.0)
        res = strongest_weakest_semester([])
        self.assertEqual(res['strongest_semester'], 0)
        
    def test_predictions_edge_cases(self):
        from src.logic import predict_final_cgpa_range, what_if_simulator
        self.assertIsNone(predict_final_cgpa_range([8.0], [0], 0))
        self.assertIsNone(what_if_simulator([8.0], [0], 0))
        self.assertIsNone(predict_final_cgpa_range([None], [20], 20))
        self.assertIsNone(what_if_simulator([None], [20], 20))
        
    def test_missing_logic_branches(self):
        from src.logic import get_scheme_credits, compute_sgpa, grade_letter_to_point, sgpa_to_percentage, required_sgpa_for_target, consistency_score, predict_final_cgpa_range, what_if_simulator
        self.assertEqual(get_scheme_credits('rc1920', 10), [16, 18, 23, 24, 22, 22, 17, 18, 18, 18])
        self.assertEqual(get_scheme_credits('rc1920', 4), [16, 18, 23, 24])
        self.assertEqual(get_scheme_credits('rc1920', None), [16, 18, 23, 24, 22, 22, 17, 18])
        self.assertEqual(compute_sgpa([], []), {'sgpa': None, 'status': 'error'})
        self.assertEqual(compute_sgpa([8.0], [4, 4]), {'sgpa': None, 'status': 'error'})
        self.assertEqual(compute_sgpa([None, 8.0], [4, 4]), {'sgpa': None, 'status': 'invalid_input'})
        self.assertIsNone(grade_letter_to_point(''))
        self.assertEqual(sgpa_to_percentage(8.0, 'cbse'), 76.0)
        self.assertEqual(sgpa_to_percentage(8.0, 'direct'), 80.0)
        self.assertIsNone(required_sgpa_for_target(8.0, -5, 8.5, 20))
        self.assertIsNone(required_sgpa_for_target(15.0, 20, 8.5, 20))
        self.assertIsNone(required_sgpa_for_target(-1.0, 20, 8.5, 20))
        self.assertIsNone(required_sgpa_for_target(8.0, 20, 11.0, 20))
        self.assertIsNone(required_sgpa_for_target(8.0, 20, -1.0, 20))
        self.assertIsNone(predict_final_cgpa_range([8.0], [20], -1))
        self.assertIsNone(what_if_simulator([8.0], [20], -1))


class TestPerformance(unittest.TestCase):
    """Performance tests for CGPA calculation logic."""

    def test_compute_cgpa_performance(self):
        """Test performance with large number of semesters."""
        import time

        # Generate large input data
        num_semesters = 100
        grades = [7.5 + i * 0.01 for i in range(num_semesters)]
        credits = [20 + i % 5 for i in range(num_semesters)]

        # Measure execution time
        start_time = time.time()
        result = compute_cgpa(grades, credits).get("cgpa")
        end_time = time.time()

        # Should complete in reasonable time (< 100ms)
        self.assertLess(end_time - start_time, 0.1)
        self.assertIsNotNone(result)
        self.assertGreater(result, 7.0)
        self.assertLess(result, 8.0)
def test_update_cgpa_with_new_semester():
    from src.logic import update_cgpa_with_new_semester
    # Normal case
    assert abs(update_cgpa_with_new_semester(8.0, 40, 9.0, 20) - 8.3333333333) < 1e-5
    # Zero credits total
    assert update_cgpa_with_new_semester(8.0, 0, 9.0, 0) is None
