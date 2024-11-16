from fpdf import FPDF


def generate_pdf_content(booking_info):
    """
    Generates a PDF from booking details and returns the binary PDF content.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    
    
    for key, value in booking_info.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    
    
    pdf_content = pdf.output(dest='S').encode('latin1') 
    return pdf_content

