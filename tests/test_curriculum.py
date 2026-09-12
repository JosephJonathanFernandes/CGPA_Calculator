"""
Tests for curriculum data integrity and syllabus template definitions.
"""
import json
import os
import unittest


class TestCurriculumData(unittest.TestCase):
    """Ensure curriculum.json is well-formed and valid."""

    @classmethod
    def setUpClass(cls):
        curriculum_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "curriculum.json"
        )
        cls.assertTrue(
            cls, os.path.exists(curriculum_path), "data/curriculum.json not found"
        )
        with open(curriculum_path, "r", encoding="utf-8") as f:
            cls.curriculum = json.load(f)

    def test_curriculum_is_valid_structure(self):
        """Test that curriculum is a dictionary with departments and semesters."""
        self.assertIsInstance(self.curriculum, dict)
        self.assertGreater(len(self.curriculum), 0)

        for dept_name, semesters in self.curriculum.items():
            self.assertIsInstance(dept_name, str)
            self.assertIsInstance(semesters, dict)
            for sem_name, subjects in semesters.items():
                self.assertIsInstance(sem_name, str)
                self.assertIsInstance(subjects, list)
                self.assertGreater(len(subjects), 0)
                for subj in subjects:
                    self.assertIn("name", subj)
                    self.assertIn("credits", subj)
                    self.assertIsInstance(subj["name"], str)
                    self.assertTrue(len(subj["name"].strip()) > 0)
                    self.assertIsInstance(subj["credits"], (int, float))
                    self.assertGreater(subj["credits"], 0)

    def test_vlsi_semester_3_curriculum(self):
        """Test that VLSI Design and Technology Semester 3 matches the syllabus."""
        vlsi_key = "VLSI Design and Technology - RC 2019-20"
        self.assertIn(vlsi_key, self.curriculum)

        vlsi_dept = self.curriculum[vlsi_key]
        self.assertIn("Semester 3", vlsi_dept)

        sem3_subjects = vlsi_dept["Semester 3"]
        self.assertEqual(len(sem3_subjects), 8)

        total_credits = sum(s["credits"] for s in sem3_subjects)
        self.assertEqual(total_credits, 23)

        expected_subjects = [
            ("Applied Mathematics- III", 4),
            ("Semiconductor Physics", 3),
            ("Electronic Devices and Circuits", 4),
            ("Digital Logic Design", 4),
            ("Circuit Analysis and Synthesis", 4),
            ("Electronic Circuits Lab", 1),
            ("Digital Logic Design Lab", 1),
            ("Programming Lab I", 2),
        ]

        actual_tuples = [(s["name"], s["credits"]) for s in sem3_subjects]
        self.assertEqual(actual_tuples, expected_subjects)

    def test_vlsi_semester_4_curriculum(self):
        """Test that VLSI Design and Technology Semester 4 matches the syllabus."""
        vlsi_key = "VLSI Design and Technology - RC 2019-20"
        self.assertIn(vlsi_key, self.curriculum)

        vlsi_dept = self.curriculum[vlsi_key]
        self.assertIn("Semester 4", vlsi_dept)

        sem4_subjects = vlsi_dept["Semester 4"]
        self.assertEqual(len(sem4_subjects), 9)

        total_credits = sum(s["credits"] for s in sem4_subjects)
        self.assertEqual(total_credits, 24)

        expected_subjects = [
            ("Digital Signal Processing", 4),
            ("Electromagnetics", 4),
            ("Microprocessors and Peripherals", 4),
            ("VLSI Technology and IC Fabrication", 3),
            ("Linear Integrated Circuits", 3),
            ("VLSI CAD Lab I", 1),
            ("Linear Integrated Circuits Lab", 1),
            ("Microprocessor Lab", 1),
            ("Engineering Economics and Management", 3),
        ]

        actual_tuples = [(s["name"], s["credits"]) for s in sem4_subjects]
        self.assertEqual(actual_tuples, expected_subjects)

    def test_vlsi_semester_5_curriculum(self):
        """Test that VLSI Design and Technology Semester 5 matches the syllabus."""
        vlsi_key = "VLSI Design and Technology - RC 2019-20"
        self.assertIn(vlsi_key, self.curriculum)

        vlsi_dept = self.curriculum[vlsi_key]
        self.assertIn("Semester 5", vlsi_dept)

        sem5_subjects = vlsi_dept["Semester 5"]
        self.assertEqual(len(sem5_subjects), 9)

        total_credits = sum(s["credits"] for s in sem5_subjects)
        self.assertEqual(total_credits, 24)

        expected_subjects = [
            ("Digital VLSI Design", 4),
            ("Analog VLSI Design", 4),
            ("Professional Elective I (VLSI53X)", 3),
            ("Professional Elective II (VLSI54X)", 3),
            ("Digital VLSI Design Lab", 1),
            ("Analog VLSI Design Lab", 1),
            ("Hardware Description Language Lab", 2),
            ("Open Elective", 3),
            ("Ethics and Entrepreneurship", 3),
        ]

        actual_tuples = [(s["name"], s["credits"]) for s in sem5_subjects]
        self.assertEqual(actual_tuples, expected_subjects)

    def test_vlsi_semester_6_curriculum(self):
        """Test that VLSI Design and Technology Semester 6 matches the syllabus."""
        vlsi_key = "VLSI Design and Technology - RC 2019-20"
        self.assertIn(vlsi_key, self.curriculum)

        vlsi_dept = self.curriculum[vlsi_key]
        self.assertIn("Semester 6", vlsi_dept)

        sem6_subjects = vlsi_dept["Semester 6"]
        self.assertEqual(len(sem6_subjects), 9)

        total_credits = sum(s["credits"] for s in sem6_subjects)
        self.assertEqual(total_credits, 22)

        expected_subjects = [
            ("Embedded Systems with RTOS", 3),
            ("Analog and Digital Communication", 3),
            ("Professional Elective III (VLSI63X)", 3),
            ("Professional Elective IV (VLSI64X)", 3),
            ("Embedded Design Lab", 1),
            ("Programming Lab II", 1),
            ("FPGA Design Lab", 2),
            ("Open Elective", 3),
            ("Cyber Law and IPR", 3),
        ]

        actual_tuples = [(s["name"], s["credits"]) for s in sem6_subjects]
        self.assertEqual(actual_tuples, expected_subjects)

    def test_vlsi_semester_7_curriculum(self):
        """Test that VLSI Design and Technology Semester 7 matches the syllabus."""
        vlsi_key = "VLSI Design and Technology - RC 2019-20"
        self.assertIn(vlsi_key, self.curriculum)

        vlsi_dept = self.curriculum[vlsi_key]
        self.assertIn("Semester 7", vlsi_dept)

        sem7_subjects = vlsi_dept["Semester 7"]
        self.assertEqual(len(sem7_subjects), 5)

        total_credits = sum(s["credits"] for s in sem7_subjects)
        self.assertEqual(total_credits, 15)

        expected_subjects = [
            ("Computer Networks and Protocols", 3),
            ("Professional Elective V (VLSI72X)", 3),
            ("Open Elective", 3),
            ("Internship", 3),
            ("Project Work - Phase I", 3),
        ]

        actual_tuples = [(s["name"], s["credits"]) for s in sem7_subjects]
        self.assertEqual(actual_tuples, expected_subjects)

    def test_vlsi_semester_8_curriculum(self):
        """Test that VLSI Design and Technology Semester 8 matches the syllabus."""
        vlsi_key = "VLSI Design and Technology - RC 2019-20"
        self.assertIn(vlsi_key, self.curriculum)

        vlsi_dept = self.curriculum[vlsi_key]
        self.assertIn("Semester 8", vlsi_dept)

        sem8_subjects = vlsi_dept["Semester 8"]
        self.assertEqual(len(sem8_subjects), 4)

        total_credits = sum(s["credits"] for s in sem8_subjects)
        self.assertEqual(total_credits, 18)

        expected_subjects = [
            ("Design For Testability", 3),
            ("Professional Elective VI (VLSI82X)", 3),
            ("Elective - NPTEL / MOOC / SWAYAM", 3),
            ("Project Work - Phase II", 9),
        ]

        actual_tuples = [(s["name"], s["credits"]) for s in sem8_subjects]
        self.assertEqual(actual_tuples, expected_subjects)


if __name__ == "__main__":
    unittest.main()





