from fpdf import FPDF
import os
from typing import Dict, Any
from datetime import datetime

class MaterialPDF(FPDF):
    def header(self):
        # Optional: Add logo or more styling if needed
        self.set_font("Arial", "B", 15)
        # Get page width
        page_w = self.w - 2 * self.l_margin
        self.cell(page_w, 10, "MaterialMind - Material Recommendation Report", border=0, ln=1, align="C") # Use ln=1 and border=0
        self.ln(10) # Add space after header

    def footer(self):
        self.set_y(-15) # Position 1.5 cm from bottom
        self.set_font("Arial", "I", 8)
        self.set_text_color(128) # Grey text color for footer
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_pdf(recommendations: Dict[str, Any], filename: str) -> str:
    output_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(output_dir, filename)
    pdf = MaterialPDF('P', 'mm', 'A4') # Use Portrait, mm units, A4 size
    pdf.set_auto_page_break(auto=True, margin=15) # Bottom margin
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()

    # --- Report Title and General Recommendations ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "General Recommendations:", ln=True, align="L")
    pdf.set_font("Arial", "", 10)
    # Use multi_cell for potentially long recommendations text
    pdf.multi_cell(0, 5, recommendations.get("general_recommendations", "No general recommendations provided."), border=0, align="L")
    pdf.ln(10) # Space after recommendations

    # --- Table Setup ---
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(224, 235, 255)  # Lighter Blue for header
    pdf.set_text_color(0) # Black text
    pdf.set_line_width(0.3) # Thinner borders

    # Define column widths (adjust as needed, total should be close to page width - margins)
    # Page width A4 = 210mm. Margins = 10mm + 10mm = 20mm. Usable width = 190mm
    col_widths = {
        "material": 35,
        "properties": 60,
        "application": 40,
        "rationale": 55 # Adjusted to fit remaining width
    }
    headers = ["Material", "Properties", "Application", "Rationale"]
    header_keys = ["material", "properties", "application", "rationale"] # Keys for width dict

    # --- Draw Table Header ---
    for i, header in enumerate(headers):
        key = header_keys[i]
        pdf.cell(col_widths[key], 10, header, border=1, align="C", fill=True)
    pdf.ln() # Move to next line after header

    # --- Draw Table Rows ---
    pdf.set_font("Arial", "", 9)
    pdf.set_fill_color(255, 255, 255) # White background for rows
    line_height_ratio = 5 # Approx height per line of text in mm for multi_cell

    for material in recommendations.get("materials", []):
        # Prepare cell data
        material_name = str(material.get("name", "N/A"))
        properties_str = "\n".join([f"{key}: {value}" for key, value in material.get("properties", {}).items()])
        application_str = str(material.get("application", "N/A"))
        rationale_str = str(material.get("rationale", "N/A"))

        cell_data = [
            material_name,
            properties_str,
            application_str,
            rationale_str
        ]

        # Store cursor position before drawing the row
        start_x = pdf.get_x()
        start_y = pdf.get_y()
        max_y = start_y # Track the lowest point reached by any cell in this row

        # Draw each cell using multi_cell and manage position manually
        current_x = start_x
        for i, data in enumerate(cell_data):
            key = header_keys[i]
            width = col_widths[key]
            align = 'L' if i > 0 else 'L' # Left-align most, maybe center first col if desired

            pdf.set_xy(current_x, start_y) # Reset Y for each cell, move X
            pdf.multi_cell(width, line_height_ratio, data, border=1, align=align, fill=False) # Draw the cell

            # Update max_y: Check the Y position *after* drawing the multi_cell
            # This tells us how tall this cell was.
            max_y = max(max_y, pdf.get_y())

            # Move the horizontal position for the next cell
            current_x += width

        # After drawing all cells in the row, move the cursor below the tallest cell
        pdf.set_y(max_y)
        # pdf.ln() # Not needed because set_y moves the cursor


    # --- Output PDF ---
    try:
        pdf.output(pdf_path)
        print(f"PDF generated successfully at: {pdf_path}") # Add confirmation
        return pdf_path
    except Exception as e:
        print(f"Error generating PDF: {e}") # Add error handling
        return None

# Example Usage (assuming 'recommendations_data' holds your dictionary)
# generate_pdf(recommendations_data, "MaterialMind_Recommendation_Test.pdf")
