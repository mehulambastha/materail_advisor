from fpdf import FPDF
import os
from typing import Dict, Any
from datetime import datetime

class MaterialPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "MaterialMind - Material Recommendation Report", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_pdf(recommendations: Dict[str, Any], filename: str) -> str:
    output_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_path = os.path.join(output_dir, filename)
    pdf = MaterialPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    
    # Add Analysis Text
    pdf.cell(0, 10, "General Recommendations:", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 10, recommendations.get("general_recommendations", "No general recommendations provided."))
    pdf.ln(10)
    
    # Table Header
    pdf.set_fill_color(173, 216, 230)  # Light Blue
    pdf.set_font("Arial", "B", 10)
    col_widths = [40, 70, 35, 45]
    headers = ["Material", "Properties", "Application", "Rationale"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("Arial", "", 9)
    for material in recommendations.get("materials", []):
        properties_str = "\n".join([f"{key}: {value}" for key, value in material.get("properties", {}).items()])
        pdf.cell(col_widths[0], 10, str(material.get("name", "N/A")), border=1)
        pdf.cell(col_widths[1], 10, properties_str, border=1)
        pdf.cell(col_widths[2], 10, str(material.get("application", "N/A")), border=1)
        pdf.cell(col_widths[3], 10, str(material.get("rationale", "N/A")), border=1)
        pdf.ln()
    
    pdf.output(pdf_path)
    return pdf_path
