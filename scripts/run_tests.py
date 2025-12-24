# scripts/run_tests.py
"""
Script to run all tests for CGPA Calculator.
"""
import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
