from fpdf import FPDF
import os
from typing import Dict, Any
from datetime import datetime

class MaterialPDF(FPDF):
    def header(self):
        # Set font for the main title
        self.set_font("Arial", "B", 16)
        # Calculate width available for the title
        page_w = self.w - 2 * self.l_margin
        self.cell(page_w, 10, "MaterialMind - Material Recommendation Report", border=0, ln=1, align="C") # Centered Title

        # Add a subtitle or report generation time
        self.set_font("Arial", "I", 9)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.set_text_color(128) # Grey color for timestamp
        self.cell(page_w, 8, f"Report Generated: {timestamp}", border=0, ln=1, align="C")
        self.set_text_color(0) # Reset text color to black

        # Add a line separator below the header
        # self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y()) # Draw line
        # self.ln(5) # Add a bit more space after the line/header info

        # Or just add spacing
        self.ln(8) # Add space after header section before content starts

    def footer(self):
        self.set_y(-15) # Position 1.5 cm from bottom
        self.set_font("Arial", "I", 8)
        self.set_text_color(128) # Grey text color for footer
        # Add page number
        page_num_text = f"Page {self.page_no()} / {{nb}}" # {nb} is alias for total pages
        self.cell(0, 10, page_num_text, align="C")
        self.set_text_color(0) # Reset text color


def generate_pdf(recommendations: Dict[str, Any], filename: str) -> str:
    output_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    pdf_path = os.path.join(output_dir, filename)
    pdf = MaterialPDF('P', 'mm', 'A4') # Use Portrait, mm units, A4 size
    pdf.alias_nb_pages() # Enable total page count alias '{nb}'
    pdf.set_auto_page_break(auto=True, margin=15) # Bottom margin
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()

    # --- Report Title and General Recommendations ---
    # Report title is now handled in the header
    pdf.set_font("Arial", "B", 12) # Section heading font
    pdf.cell(0, 10, "General Recommendations:", ln=True, align="L")
    pdf.set_font("Arial", "", 10) # Body text font
    # Use multi_cell for potentially long recommendations text
    pdf.multi_cell(0, 5, recommendations.get("general_recommendations", "No general recommendations provided."), border=0, align="L")
    pdf.ln(10) # Space after recommendations

    # --- Table Setup ---
    pdf.set_font("Arial", "B", 10) # Table header font
    pdf.set_fill_color(224, 235, 255)  # Lighter Blue for header
    pdf.set_text_color(0) # Black text
    pdf.set_line_width(0.3) # Thinner borders

    # Define column widths (adjust as needed, total should be close to page width - margins)
    # Page width A4 = 210mm. Margins = 10mm + 10mm = 20mm. Usable width = 190mm
    col_widths = {
        "material": 40,  # Adjusted slightly
        "properties": 55, # Adjusted slightly
        "application": 40,
        "rationale": 55
    }
    # Ensure total width is manageable
    total_width = sum(col_widths.values())
    # Optional: print(f"Total table width: {total_width}mm / Usable: {pdf.w - pdf.l_margin - pdf.r_margin}mm")

    headers = ["Material", "Properties", "Application", "Rationale"]
    header_keys = ["material", "properties", "application", "rationale"] # Keys for width dict

    # --- Draw Table Header ---
    for i, header in enumerate(headers):
        key = header_keys[i]
        pdf.cell(col_widths[key], 10, header, border=1, align="C", fill=True)
    pdf.ln() # Move to next line after header

    # --- Draw Table Rows ---
    pdf.set_font("Arial", "", 9) # Table body font
    pdf.set_fill_color(255, 255, 255) # White background for rows
    line_height_ratio = 5 # Approx height per line of text in mm for multi_cell
    cell_padding_horiz = 2  # Horizontal padding (left/right) in mm
    cell_padding_vert = 2   # Vertical padding (top) in mm

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
        max_y = start_y # Track the lowest point reached by any cell's *content* in this row

        # --- Calculate content height and draw text first (without borders) ---
        content_end_y_per_cell = {}
        current_x = start_x
        for i, data in enumerate(cell_data):
            key = header_keys[i]
            col_width = col_widths[key]
            text_area_width = col_width - (2 * cell_padding_horiz)
            align = 'L'

            # Set position for text content with padding
            pdf.set_xy(current_x + cell_padding_horiz, start_y + cell_padding_vert)
            pdf.multi_cell(text_area_width, line_height_ratio, data, border=0, align=align, fill=False)

            # Record where the content ended for this cell
            content_end_y_per_cell[i] = pdf.get_y()
            # Update the maximum Y position based on content bottom + padding
            max_y = max(max_y, content_end_y_per_cell[i] + cell_padding_vert)

            # Update X for the next cell calculation (though we reset XY each time)
            current_x += col_width

        # --- Draw the Borders for the entire row ---
        # Now that we know the maximum height needed (max_y - start_y)
        actual_row_height = max_y - start_y
        current_x = start_x # Reset X to start of row
        for i, data in enumerate(cell_data):
             key = header_keys[i]
             col_width = col_widths[key]
             pdf.rect(current_x, start_y, col_width, actual_row_height) # Draw border rectangle
             current_x += col_width


        # After drawing all cells & borders, move the cursor below the row
        pdf.set_y(max_y)

    # --- END OF TABLE ---
    pdf.ln(10) # Add space after the table

    # --- Additional Sections ---
    section_data = {
        "Alternative Materials": recommendations.get("alt_materials"),
        "Manufacturing Considerations": recommendations.get("manufacturing_considerations"),
        "Cost Considerations": recommendations.get("cost_considerations")
    }

    for heading, text in section_data.items():
        if text: # Only add section if text exists
            pdf.set_font("Arial", "B", 11) # Section heading font size
            pdf.cell(0, 10, heading + ":", ln=True, align="L")
            pdf.set_font("Arial", "", 10) # Body text font size
            pdf.multi_cell(0, 5, str(text), border=0, align="L")
            pdf.ln(5) # Add space after each section's content

    # --- Output PDF ---
    try:
        pdf.output(pdf_path)
        print(f"PDF generated successfully at: {pdf_path}") # Add confirmation
        return pdf_path
    except Exception as e:
        print(f"Error generating PDF: {e}") # Add error handling
        return None

# Example Usage (how you'd call it):
# Assuming 'recommendations_data' holds your full dictionary including the new keys
# generate_pdf(recommendations_data, "MaterialMind_Ship_Report.pdf")
