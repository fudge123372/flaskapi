import sqlite3

connection = sqlite3.connect("flask_duka_api.db")
cursor = connection.cursor()

cursor.execute("""
    ALTER TABLE payments
    ADD COLUMN receipt_status VARCHAR(20) DEFAULT 'pending'
""")

connection.commit()
connection.close()

print("Receipt status column added successfully!")