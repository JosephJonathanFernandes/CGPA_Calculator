# tests/test_logic.py
"""
Comprehensive unit tests for CGPA Calculator core logic.
Includes edge cases, boundary testing, and error conditions.
"""
import unittest
from src.logic import compute_cgpa, classify_cgpa, padded_default_credits, DEFAULT_CREDITS, DEFAULT_SEM_COUNT

class TestCGPALogic(unittest.TestCase):
    """Test suite for CGPA calculation logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_grades = [8.0, 9.0, 7.5, 8.5]
        self.valid_credits = [20, 22, 18, 20]
        self.expected_cgpa = (8.0*20 + 9.0*22 + 7.5*18 + 8.5*20) / (20+22+18+20)

    def test_compute_cgpa_valid(self):
        """Test valid CGPA calculation with typical inputs."""
        result = compute_cgpa(self.valid_grades, self.valid_credits)
        self.assertAlmostEqual(result, self.expected_cgpa, places=2)

    def test_compute_cgpa_boundary_values(self):
        """Test boundary values for grades and credits."""
        # Minimum valid grades (0.0)
        result = compute_cgpa([0.0, 0.0], [10, 10])
        self.assertEqual(result, 0.0)

        # Maximum valid grades (10.0)
        result = compute_cgpa([10.0, 10.0], [10, 10])
        self.assertEqual(result, 10.0)

        # Mixed boundary values
        result = compute_cgpa([0.0, 10.0], [10, 10])
        self.assertEqual(result, 5.0)

    def test_compute_cgpa_edge_cases(self):
        """Test edge cases and error conditions."""
        # Empty lists
        self.assertIsNone(compute_cgpa([], []))

        # Mismatched lengths
        self.assertIsNone(compute_cgpa([8.0, 9.0], [20]))
        self.assertIsNone(compute_cgpa([8.0], [20, 22]))

        # Zero total credits
        self.assertIsNone(compute_cgpa([8.0], [0]))
        self.assertIsNone(compute_cgpa([8.0, 9.0], [0, 0]))

        # Single semester
        result = compute_cgpa([7.5], [20])
        self.assertEqual(result, 7.5)

    def test_compute_cgpa_precision(self):
        """Test calculation precision with floating point values."""
        grades = [8.333, 9.666, 7.125]
        credits = [18, 22, 20]
        expected = (8.333*18 + 9.666*22 + 7.125*20) / (18+22+20)
        result = compute_cgpa(grades, credits)
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
        result = compute_cgpa([7.0, 8.0, 9.0], [20, 20, 20])
        self.assertAlmostEqual(result, 8.0, places=2)

        # Unequal credits (weighted average)
        result = compute_cgpa([7.0, 8.0, 9.0], [10, 20, 30])
        expected = (7.0*10 + 8.0*20 + 9.0*30) / 60
        self.assertAlmostEqual(result, expected, places=2)

        # Very uneven credits
        result = compute_cgpa([5.0, 9.0], [5, 30])
        expected = (5.0*5 + 9.0*30) / 35
        self.assertAlmostEqual(result, expected, places=2)

    def test_compute_cgpa_error_conditions(self):
        """Test various error conditions that should return None."""
        # Negative credits
        self.assertIsNone(compute_cgpa([8.0], [-5]))

        # Negative grades (though input validation should prevent this)
        self.assertIsNone(compute_cgpa([-1.0], [20]))

        # Extremely large values
        self.assertIsNone(compute_cgpa([8.0], [10000]))
        self.assertIsNone(compute_cgpa([100.0], [20]))

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
        result = compute_cgpa(grades, credits)
        end_time = time.time()

        # Should complete in reasonable time (< 100ms)
        self.assertLess(end_time - start_time, 0.1)
        self.assertIsNotNone(result)
        self.assertGreater(result, 7.0)
        self.assertLess(result, 8.0)

if __name__ == "__main__":
    unittest.main()
