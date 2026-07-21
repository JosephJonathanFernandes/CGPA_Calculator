import io
import datetime
from PIL import Image, ImageDraw, ImageFont

try:
    from fpdf import FPDF
    _FPDF_AVAILABLE = True
except ImportError:
    _FPDF_AVAILABLE = False
    FPDF = object  # dummy base so class definition below doesn't error

def generate_shareable_card(cgpa: float, percentage: float, standing: str) -> bytes:
    """Generate a shareable PNG card with the user's CGPA and standing."""
    width, height = 800, 450
    bg_color = (79, 70, 229)  # Indigo 600
    card = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(card)

    try:
        font_title = ImageFont.load_default(size=40)
        font_cgpa = ImageFont.load_default(size=120)
        font_sub = ImageFont.load_default(size=30)
        font_footer = ImageFont.load_default(size=20)
    except TypeError:
        font_title = font_cgpa = font_sub = font_footer = ImageFont.load_default()

    # Draw Text
    draw.text((width//2, 80), "My CGPA Result", fill=(255,255,255), anchor="ms", font=font_title)
    
    # Highlighted CGPA Box
    draw.rounded_rectangle([(width//2 - 150, 120), (width//2 + 150, 260)], radius=20, fill=(255,255,255))
    draw.text((width//2, 220), f"{cgpa:.2f}", fill=bg_color, anchor="ms", font=font_cgpa)

    # Subtext (Standing & Percentage)
    draw.text((width//2, 320), f"Class: {standing}  •  {percentage:.2f}%", fill=(255,255,255), anchor="ms", font=font_sub)
    
    # Footer
    draw.text((width//2, 400), "Calculated via CGPA & SGPA Calculator", fill=(200,220,255), anchor="ms", font=font_footer)

    img_byte_arr = io.BytesIO()
    card.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


class PDFReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 20)
        self.set_text_color(37, 99, 235)
        self.cell(0, 10, "Academic Performance Report", align="C")
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Generated on {datetime.date.today()} - Page {self.page_no()}", align="C")


def generate_pdf_report(cgpa: float, percentage: float, standing: str, semesters_data: list, chart_bytes: bytes = None) -> bytes:
    """Generate a PDF report using fpdf2."""
    if not _FPDF_AVAILABLE:
        raise RuntimeError("fpdf2 is not installed or could not be imported. Run: pip install --force-reinstall fpdf2")
    pdf = PDFReport()
    pdf.add_page()

    # Summary Section
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Final Summary")
    pdf.ln(10)
    
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, f"Cumulative Grade Point Average (CGPA): {cgpa:.2f}")
    pdf.ln(8)
    pdf.cell(0, 8, f"Percentage Equivalent: {percentage:.2f}%")
    pdf.ln(8)
    pdf.cell(0, 8, f"Standing/Class: {standing}")
    pdf.ln(15)

    # Chart
    if chart_bytes:
        # Save bytes to a temp file because FPDF requires a filepath or a BytesIO
        chart_io = io.BytesIO(chart_bytes)
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "Performance Trend")
        pdf.ln(10)
        # Assuming the image is wide, fit to width 180mm
        pdf.image(chart_io, w=180)
        pdf.ln(10)

    # Breakdown Table
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Semester Breakdown")
    pdf.ln(10)

    # Table Header
    pdf.set_font("helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(40, 10, "Semester", border=1, fill=True, align="C")
    pdf.cell(40, 10, "Credits", border=1, fill=True, align="C")
    pdf.cell(40, 10, "SGPA", border=1, fill=True, align="C")
    pdf.ln()

    # Table Rows
    pdf.set_font("helvetica", "", 12)
    for row in semesters_data:
        pdf.cell(40, 10, f"Sem {row['sem']}", border=1, align="C")
        pdf.cell(40, 10, str(row['credits']), border=1, align="C")
        pdf.cell(40, 10, f"{row['sgpa']:.2f}", border=1, align="C")
        pdf.ln()

    return pdf.output(dest="S")
