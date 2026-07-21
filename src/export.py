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
        # Top banner
        self.set_fill_color(79, 70, 229) # Indigo 600
        self.rect(0, 0, 210, 25, 'F')
        
        self.set_font("helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.set_y(8)
        self.cell(0, 10, "Academic Performance Report", align="C")
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Generated on {datetime.date.today()} - Page {self.page_no()}", align="C")


def generate_pdf_report(cgpa: float, percentage: float, standing: str, semesters_data: list, chart_bytes: bytes = None) -> bytes:
    """Generate a premium PDF report using fpdf2."""
    if not _FPDF_AVAILABLE:
        raise RuntimeError("fpdf2 is not installed or could not be imported. Run: pip install --force-reinstall fpdf2")
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Summary Section (Styled Box)
    pdf.set_y(35)
    pdf.set_fill_color(249, 250, 251) # Gray 50
    pdf.set_draw_color(229, 231, 235) # Gray 200
    pdf.rect(10, 35, 190, 45, 'DF')
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(17, 24, 39) # Gray 900
    pdf.set_xy(15, 40)
    pdf.cell(0, 8, "Final Summary")
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(55, 65, 81) # Gray 700
    pdf.set_xy(15, 50)
    pdf.cell(0, 8, f"Cumulative Grade Point Average (CGPA): {cgpa:.2f}")
    pdf.set_xy(15, 58)
    pdf.cell(0, 8, f"Percentage Equivalent: {percentage:.2f}%")
    pdf.set_xy(15, 66)
    pdf.cell(0, 8, f"Standing/Class: {standing}")
    
    pdf.ln(20)

    # Chart
    if chart_bytes:
        try:
            chart_io = io.BytesIO(chart_bytes)
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(17, 24, 39)
            pdf.cell(0, 10, "Performance Trend")
            pdf.ln(10)
            pdf.image(chart_io, w=170, x=20)
            pdf.ln(10)
        except Exception as e:
            pass # Skip chart if PIL/FPDF fails to process it

    # Breakdown Table
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(17, 24, 39)
    pdf.cell(0, 10, "Semester Breakdown")
    pdf.ln(8)

    # Table Header
    pdf.set_font("helvetica", "B", 11)
    pdf.set_fill_color(79, 70, 229) # Indigo 600
    pdf.set_text_color(255, 255, 255)
    pdf.set_draw_color(79, 70, 229)
    
    # Calculate widths
    w_sem, w_cred, w_sgpa = 60, 60, 60
    start_x = (210 - (w_sem + w_cred + w_sgpa)) / 2 # Center table
    pdf.set_x(start_x)
    
    pdf.cell(w_sem, 10, "Semester", border=1, fill=True, align="C")
    pdf.cell(w_cred, 10, "Credits", border=1, fill=True, align="C")
    pdf.cell(w_sgpa, 10, "SGPA", border=1, fill=True, align="C")
    pdf.ln()

    # Table Rows
    pdf.set_font("helvetica", "", 11)
    pdf.set_draw_color(229, 231, 235)
    
    fill = False
    for row in semesters_data:
        pdf.set_x(start_x)
        # Alternate row colors
        if fill:
            pdf.set_fill_color(249, 250, 251)
            pdf.set_text_color(55, 65, 81)
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(17, 24, 39)
            
        sem_val = row.get('Semester', row.get('sem', 'N/A'))
        cred_val = row.get('Credits', row.get('credits', 'N/A'))
        sgpa_val = row.get('SGPA', row.get('sgpa', None))
        
        pdf.cell(w_sem, 10, f"Semester {sem_val}", border=1, align="C", fill=True)
        pdf.cell(w_cred, 10, str(cred_val), border=1, align="C", fill=True)
        
        # Handle nan or None
        import math
        if sgpa_val is None or (isinstance(sgpa_val, float) and math.isnan(sgpa_val)):
            sgpa_str = "N/A"
        else:
            sgpa_str = f"{sgpa_val:.2f}"
            
        pdf.cell(w_sgpa, 10, sgpa_str, border=1, align="C", fill=True)
        pdf.ln()
        fill = not fill

    return pdf.output(dest="S")
