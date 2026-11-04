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





#
#        if not payment:
 #3#     if payment.status == "completed" and payment.receipt_url:
    #        return jsonify({"message":"Payment and receipt processed","receipt_url":payment.receipt_url}),200
#
 #       if result_code == 0:
  #          callback_metadata = stkCallback.get('CallbackMetadata',{})
   #         for item in callback_metadata.get('item',[]):
    #            if item.get('Name') == 'MpesaReceiptNumber':
     #               payment.transcation_code = item.get('Value')
      ##3    user = session.get(User,payment.user_id)
#
 #           if user and payment.transaction_code:
  #              text =(f"Trans Code:{payment.transaction_code},"f"amount:{payment.amout},"f"Date:{payment.date_paid}")
###               receipt_url = create_pdf(text,payment.transaction_code)
    #            if receipt_url:
   # #                payment.receipt_url = receipt_url
      #              payment.receipt_status = "available"
       ###       session.commit()
     #       return jsonify({"message":"Payment completed successfully","receipt_url":payment.receipt_url}),200
    #    else:
   #       print("CALLBACK ERROR:",repr(e),flush=True)

#        return jsonify({"error":"Error processing callback"}),500

