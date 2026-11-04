from fpdf import FPDF
from cloudinary_config import upload_pdf

def create_pdf(payment_data, transaction_code):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(200, 10, txt=payment_data, align="C")
    pdf.output(f"receipts/{transaction_code}.pdf")
    print("PDF created. Now uploading to Cloudinary...", flush=True)
    return upload_pdf(transaction_code)