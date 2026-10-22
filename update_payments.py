from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///./flask_duka_api.db")

new_columns = [
    ("phone_number", "VARCHAR(20)"),
    ("mrid", "VARCHAR(100)"),
    ("crid", "VARCHAR(100)"),
    ("status", "VARCHAR(20) DEFAULT 'pending'"),
    ("transaction_code", "VARCHAR(50)")
]

with engine.begin() as connection:
    existing_columns = connection.execute(
        text("PRAGMA table_info(payments)")
    ).fetchall()

    existing_column_names = {column[1] for column in existing_columns}

    for column_name, column_type in new_columns:
        if column_name not in existing_column_names:
            connection.execute(
                text(
                    f"ALTER TABLE payments ADD COLUMN "
                    f"{column_name} {column_type}"
                )
            )
            print(f"Added column: {column_name}")
        else:
            print(f"Column already exists: {column_name}")

print("Payments table updated successfully!")




#cloudinary_config.config(
 #   cloud_name= Cloud_Name,
  ## api_secret=Secret_Key
#)



#import cloudinary
#import cloudinary.uploader


#Cloud_Name="bqb3gclm"
#API_key="869944373719192"
#Secret_Key="feHReqZXhR3jArpkPK0NsvoiIow"

 #connecting to cloudinary

#def upload_pdf(pdf_file):
 #   try:
  ###    receipt_url = upload["secure_url"]
     #   print("successful cloudinary upload")
      ## return"success"
    #except Exception as e:
     #   print(f"upload failed: {e}")
      #  return "failed"