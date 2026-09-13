import unittest
from src.export import generate_pdf_report, generate_shareable_card, _FPDF_AVAILABLE


class TestExport(unittest.TestCase):
    def test_export_pdf_generation(self):
        """Verify that PDF generation produces valid PDF bytes."""
        if not _FPDF_AVAILABLE:
            self.skipTest("fpdf2 is not installed in this environment.")

        sem_data = [
            {'Semester': 1, 'Credits': 20, 'SGPA': 8.5},
            {'Semester': 2, 'Credits': 22, 'SGPA': 8.7},
        ]
        pdf_bytes = generate_pdf_report(8.6, 78.5, 'First Class with Distinction', sem_data, chart_bytes=None)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 0)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'), "PDF output should start with %PDF magic header")

    def test_export_pdf_with_chart(self):
        """Verify that PDF report correctly embeds chart image bytes."""
        if not _FPDF_AVAILABLE:
            self.skipTest("fpdf2 is not installed in this environment.")

        card_png = generate_shareable_card(8.5, 77.5, 'First Class')
        sem_data = [{'Semester': 1, 'Credits': 20, 'SGPA': 8.5}]
        pdf_bytes_no_chart = generate_pdf_report(8.5, 77.5, 'First Class', sem_data, chart_bytes=None)
        pdf_bytes = generate_pdf_report(8.5, 77.5, 'First Class', sem_data, chart_bytes=card_png)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), len(pdf_bytes_no_chart))
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_export_pdf_handles_nan_and_none_sgpa(self):
        """Verify that PDF report handles missing or NaN SGPA gracefully."""
        if not _FPDF_AVAILABLE:
            self.skipTest("fpdf2 is not installed in this environment.")

        sem_data = [
            {'Semester': 1, 'Credits': 20, 'SGPA': None},
            {'Semester': 2, 'Credits': 20, 'SGPA': float('nan')},
        ]
        pdf_bytes = generate_pdf_report(0.0, 0.0, 'Pass Class', sem_data, chart_bytes=None)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_export_shareable_card_png(self):
        """Verify that shareable card generation produces valid PNG bytes."""
        png_bytes = generate_shareable_card(9.2, 84.5, 'Distinction')
        self.assertIsInstance(png_bytes, bytes)
        self.assertGreater(len(png_bytes), 0)
        self.assertTrue(png_bytes.startswith(b'\x89PNG\r\n\x1a\n'), "PNG output should start with PNG magic header")


if __name__ == '__main__':
    unittest.main()
