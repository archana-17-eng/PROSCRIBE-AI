from fpdf import FPDF
import io

def export_to_pdf(sections, study_inputs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=f"Clinical Protocol: {study_inputs.get('drug_name', 'N/A')}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Phase: {study_inputs.get('phase', 'N/A')}", ln=True, align='C')
    pdf.ln(10)
    
    # Sections
    for section_name, content in sections.items():
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt=section_name, ln=True, align='L')
        pdf.set_font("Arial", size=12)
        
        # Handle simple markdown bolding removal for PDF demo
        clean_content = content.replace("**", "").replace("## ", "")
        pdf.multi_cell(0, 10, txt=clean_content)
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1')

def export_to_docx(sections, study_inputs):
    # Placeholder for DOCX export logic
    # In a real app, use python-docx to build the document
    return b"Mock DOCX Content"


