import cloudinary
import cloudinary.uploader
from send_email import email

Cloud_Name = "bqb3gclm"      # keep your real values
API_key = "869944373719192"
Secret_Key = "feHReqZXhR3jArpkPK0NsvoiIow"

cloudinary.config(
    cloud_name=Cloud_Name,
    api_key=API_key,
    api_secret=Secret_Key
)

def upload_pdf(pdf_file,recipient_email):
    try:
        file_path = f"receipts/{pdf_file}.pdf"
        upload = cloudinary.uploader.upload(file_path, resource_type="raw")
        receipt_url = upload["secure_url"]
        print("successful cloudinary upload")
        print(receipt_url)
        #send email
        email(
            recipient_email,
            "Payment Receipt",
            f"Thank you! We have received your payment.\n\nYour receipt is available here: {receipt_url}"
        )
        return "success"
    except Exception as e:
        print(f"upload failed: {e}")
        return "failed"