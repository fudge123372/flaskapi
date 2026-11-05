from fpdf import FPDF
from cloudinary_config import upload_pdf

def create_pdf(payment_data, transaction_code):
    pdf = FPDF()
    pdf.add_page()
    # BUSINESS HEADING
    pdf.set_font("Arial", "B", 20)
    pdf.cell(190, 15, "DUKA BUSINESS", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, "OFFICIAL PAYMENT RECEIPT", ln=True, align="C")
    pdf.ln(10)
    # RECEIPT DETAILS
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, "Payment Information", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(190, 10, txt=payment_data)
    pdf.ln(10)
    # TRANSACTION CODE
    pdf.set_font("Arial", "B", 12)#change text appearance
    pdf.cell(190, 10, "M-Pesa Transaction Code:", ln=True)#place headings and details
    pdf.set_font("Arial", size=12)
    pdf.cell(190, 10, transaction_code, ln=True)
    pdf.ln(10)#move to the next line
    # PAYMENT CONFIRMATION
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 12, "PAYMENT SUCCESSFUL", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(190, 10, "Thank you for shopping with Duka!", ln=True, align="C")

    #SAVE PDf
    pdf.output(f"receipts/{transaction_code}.pdf")
    print("PDF created. Now uploading to Cloudinary...", flush=True)
    return upload_pdf(transaction_code)