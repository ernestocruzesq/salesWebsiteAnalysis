import logging

from fpdf import FPDF
import os

def create_pdf_from_llm_output(llm_output, output_filename='sales_prospect_report.pdf'):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_title("Sales Prospect Research Report")

    # Add your custom font
    path_font = os.path.join(os.getcwd(), 'app', 'misecellaneous', 'DejaVuSans.ttf' )
    pdf.add_font('DejaVu', '', path_font, uni=True)


    # Add title page
    pdf.add_page()
    pdf.set_font("DejaVu", '', 16)
    pdf.cell(0, 10, "Sales Prospect Research Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("DejaVu", '', 12)
    pdf.cell(0, 10, "Generated Report for Sales Team", ln=True, align='C')
    pdf.ln(20)

    pdf.set_font("DejaVu", '', 12)

    # Process the LLM output to structure it within the PDF
    lines = llm_output.split('\n')
    for line in lines:
        line = line.strip()
        if line == "":
            pdf.ln(5)
        else:
            if line.lower().startswith(("introduction", "products/services", "success stories", "value proposition")):
                pdf.set_font("DejaVu", '', 14)
                pdf.cell(0, 10, line, ln=True)
                pdf.set_font("DejaVu", '', 12)
                pdf.ln(5)
            else:
                pdf.multi_cell(0, 10, line)

    pdf.output(output_filename)