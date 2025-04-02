from fpdf import FPDF
import os
from typing import Dict, Any
from datetime import datetime

class MaterialPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'MaterialMind - Material Recommendation Report', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')



def get_string_height(pdf, width: float, text: str) -> float:
    """Estimate the height of a multi-cell text."""
    if not text:
        return 5  # Minimum row height if text is empty
    
    temp_pdf = FPDF()
    temp_pdf.add_page()  # Ensure a page is added before using multi_cell
    temp_pdf.set_font('Arial', '', 10)
    
    # Convert width to float if needed
    width = float(width)

    # Use multi_cell to estimate height
    lines = temp_pdf.multi_cell(width, 5, text, split_only=True)  
    return len(lines) * 5  # Multiply by line height



def generate_pdf(recommendations: Dict[str, Any], filename: str) -> str:
    output_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_path = os.path.join(output_dir, filename)
    pdf = MaterialPDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Material Recommendation Report', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'General Recommendations:', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, recommendations.get("general_recommendations", "No general recommendations provided."))
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Recommended Materials:', 0, 1)
    
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font('Arial', 'B', 10)
    
    col_widths = [40, 70, 35, 45]
    pdf.cell(col_widths[0], 10, 'Material', 1, 0, 'C', True)
    pdf.cell(col_widths[1], 10, 'Properties', 1, 0, 'C', True)
    pdf.cell(col_widths[2], 10, 'Application', 1, 0, 'C', True)
    pdf.cell(col_widths[3], 10, 'Rationale', 1, 1, 'C', True)
    
    pdf.set_font('Arial', '', 9)
    
    for material in recommendations.get("materials", []):
        properties_str = "\n".join([f"{key}: {value}" for key, value in material.get("properties", {}).items()])
        
        required_height = max(
            get_string_height(pdf, col_widths[0], material.get("name", "")),
            get_string_height(pdf, col_widths[1], properties_str),
            get_string_height(pdf, col_widths[2], material.get("application", "")),
            get_string_height(pdf, col_widths[3], material.get("rationale", ""))
        )
        
        x_pos = pdf.get_x()
        y_pos = pdf.get_y()
        
        pdf.multi_cell(col_widths[0], required_height / 4, material.get("name", ""), 1, 'L')
        pdf.set_xy(x_pos + col_widths[0], y_pos)
        pdf.multi_cell(col_widths[1], required_height / 4, properties_str, 1, 'L')
        pdf.set_xy(x_pos + col_widths[0] + col_widths[1], y_pos)
        pdf.multi_cell(col_widths[2], required_height / 4, material.get("application", ""), 1, 'L')
        pdf.set_xy(x_pos + col_widths[0] + col_widths[1] + col_widths[2], y_pos)
        pdf.multi_cell(col_widths[3], required_height / 4, material.get("rationale", ""), 1, 'L')
        
        pdf.ln()
    
    pdf.output(pdf_path)
    
    return pdf_path
