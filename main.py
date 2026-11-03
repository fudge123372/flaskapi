#1.it has to have a route
#2.it has to have a method(POST/GET/DELETE/PUT)
#3.it has to have a status code(200,201,403)
#4.it has to return data as JSON (key : value pairs)


from flask import Flask,request,jsonify
from flask_jwt_extended import JWTManager,jwt_required,create_access_token,get_jwt_identity
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from models import Base,Product,Sale,SaleDetails,Purchase,Payment,User
from datetime import datetime,date
from flask import redirect,url_for
from mpesa import make_stk_push
from generate_receipts import create_pdf
from flask_cors import CORS



app = Flask(__name__)
CORS(app)



app.config["JWT_SECRET_KEY"] = "wqg1q3wc"
jwt = JWTManager(app)

bcrypt = Bcrypt(app)


#create a connection to the database using sqlalchemy engine
engine = create_engine("sqlite:///./flask_duka_api.db", echo=True)

#create tables into the database using sqlalchemy
Base.metadata.create_all(engine)

#create a session to do sql transactions
session = Session(engine)

user = {"id": "1","full_name" : "Larry Mokua","email" : "agustinolarry07@gmailcom","password":"larry1234"}

allowed_methods=['POST', 'GET','PUT', 'PATCH', 'DELETE', 'OPTIONS']



@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or request.form

    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not full_name or not email or not password:
        return jsonify({
            "error": "Full name, email and password are required"
        }), 400

    existing_user = session.scalars(
        select(User).where(User.email == email)
    ).first()

    if existing_user:
        return jsonify({
            "error": "Email already exists"
        }), 409

    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    new_user = User(
        full_name=full_name,
        email=email,
        password=hashed_password
    )

    try:
        session.add(new_user)
        session.commit()

        token = create_access_token(identity=email)

        return jsonify({
            "message": "User created successfully",
            "token": token,
            "user": {
                "id": new_user.id,
                "full_name": new_user.full_name,
                "email": new_user.email
            }
        }), 201

    except Exception as e:
        session.rollback()
        print("REGISTRATION ERROR:",repr(e), flush=True)
        app.logger.exception("Registration failed")

        return jsonify({
            "error": "Registration failed. Check the server terminal."
        }), 500


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    existing_user = session.scalars(
        select(User).where(User.email == email)
    ).first()

    if (
        not existing_user
        or not bcrypt.check_password_hash(
            existing_user.password, password
        )
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    token = create_access_token(identity=email)

    return jsonify({
        "message": "User logged in successfully",
        "token": token,
        "user": {
            "id": existing_user.id,
            "full_name": existing_user.full_name,
            "email": existing_user.email
        }
    }), 200


@app.route("/")
def home():
    if request.method == "GET":
        data = {"Flask API":"Version 1"}
        return jsonify(data),200
    else:
        error = {"Error":"Method Not Allowed"}
        return jsonify (error), 403

@app.route("/products", methods = ["GET","POST"])
@jwt_required()
def products():
    email = get_jwt_identity()
    user = session.scalars(select(User).where(User.email==email)).first()
    if request.method == "GET":
        #fetch data from the database
        query = select (Product).where(Product.user_id == user.id)
        products = session.scalars(query).all()
        results = []
        for prod in products:
            p = {"id":prod.id,
                 "product_name":prod.product_name,
                 "buying_price":prod.buying_price,
                 "selling_price":prod.selling_price}
            results.append(p)
        return jsonify (results), 200
    elif request.method == "POST":
        data = request.get_json(silent=True) or {}
        product_name = data.get("product_name")
        buying_price = data.get("buying_price")
        selling_price = data.get("selling_price")
        if not product_name or not buying_price or not selling_price:
            error = {"error":"Ensure all fields are set"}
            return jsonify (error), 403
        else:
            new_product = Product(
                user_id = user.id,
                product_name = product_name,
                buying_price = float(buying_price),
                selling_price = float(selling_price)
            ) 
            session.add(new_product)
            session.commit()
            return jsonify ({"Message":"A New Product has been added succesfully"}), 201
    else:
        error = {"Error":"Method Not Allowed"}
        return jsonify (error), 405



@app.route("/sales", methods=["GET", "POST"])
@jwt_required()
def sales():
    email = get_jwt_identity()

    user = session.scalars(
        select(User).where(User.email == email)
    ).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # GET: Display the logged-in user's sales
    if request.method == "GET":
        sales_list = session.scalars(
            select(Sale).where(Sale.user_id == user.id).order_by(Sale.id.desc())
        ).all()

        results = []

        for sale in sales_list:
            detail = session.scalars(
                select(SaleDetails).where(
                    SaleDetails.sale_id == sale.id
                )
            ).first()

            product_name = None
            product_id = None

            if detail:
                product = session.get(Product, detail.product_id)

                if product:
                    product_name = product.product_name
                    product_id = product.id

            payment = session.scalars(
                select(Payment)
                .where(
                    Payment.sale_id == sale.id,
                    Payment.user_id == user.id
                )
                .order_by(Payment.id.desc())
            ).first()

            payment_status = payment.status if payment else "unpaid"
            payment_id = payment.id if payment else None
            payment_method = payment.payment_method if payment else None

            results.append({
                "id": sale.id,
                "product_id": product_id,
                "product_name": product_name,
                "quantity": sale.quantity,
                "total_amount": sale.total_amount,
                "status": payment_status,
                "payment_id":payment_id,
                "payment_method":payment_method,
                "created_at": (
                    sale.created_at.isoformat()
                    if sale.created_at else None
                )
            })

        return jsonify(results), 200

    # POST: Create a sale using an existing product
    elif request.method == "POST":
        data = request.get_json(silent=True) or {}

        product_id = data.get("product_id")
        quantity = data.get("quantity")

        if product_id is None or quantity is None:
            return jsonify({
                "error": "Product ID and quantity are required"
            }), 400

        try:
            product_id = int(product_id)
            quantity = int(quantity)

            if product_id <= 0 or quantity <= 0:
                return jsonify({
                    "error": "Product ID and quantity must be positive"
                }), 400

            product = session.scalars(
                select(Product).where(
                    Product.id == product_id,
                    Product.user_id == user.id
                )
            ).first()

            if not product:
                return jsonify({
                    "error": "Product not found"
                }), 404

            # Calculate the amount using the product selling price
            total_amount = product.selling_price * quantity

            new_sale = Sale(
                user_id=user.id,
                quantity=quantity,
                total_amount=total_amount
            )

            session.add(new_sale)
            session.flush()

            new_detail = SaleDetails(
                sale_id=new_sale.id,
                product_id=product.id,
                quantity=quantity,
                amount=total_amount
            )

            session.add(new_detail)
            session.commit()

            return jsonify({
                "message": "Sale created successfully",
                "sale_id": new_sale.id,
                "product_name": product.product_name,
                "quantity": quantity,
                "total_amount": total_amount
            }), 201

        except (ValueError, TypeError):
            session.rollback()
            return jsonify({
                "error": "Product ID and quantity must be valid numbers"
            }), 400

        except Exception as e:
            session.rollback()
            print("SALE CREATION ERROR:", repr(e))
            return jsonify({
                "error": "Could not create sale"
            }), 500


# PUT: Edit an existing sale
@app.route("/sales/<int:sale_id>", methods=["PUT"])
@jwt_required()
def update_sale(sale_id):
    email = get_jwt_identity()

    user = session.scalars(
        select(User).where(User.email == email)
    ).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    sale = session.scalars(
        select(Sale).where(
            Sale.id == sale_id,
            Sale.user_id == user.id
        )
    ).first()

    if not sale:
        return jsonify({"error": "Sale not found"}), 404

    data = request.get_json(silent=True) or {}

    quantity = data.get("quantity")

    if quantity is None:
        return jsonify({
            "error": "Quantity is required"
        }), 400

    try:
        quantity = int(quantity)

        if quantity <= 0:
            return jsonify({
                "error": "Quantity must be greater than zero"
            }), 400

        detail = session.scalars(
            select(SaleDetails).where(
                SaleDetails.sale_id == sale.id
            )
        ).first()

        if not detail:
            return jsonify({
                "error": "Sale product details not found"
            }), 404

        product = session.get(Product, detail.product_id)

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        total_amount = product.selling_price * quantity

        sale.quantity = quantity
        sale.total_amount = total_amount

        detail.quantity = quantity
        detail.amount = total_amount

        session.commit()

        return jsonify({
            "message": "Sale updated successfully",
            "sale_id": sale.id,
            "product_name": product.product_name,
            "quantity": quantity,
            "total_amount": total_amount
        }), 200

    except (ValueError, TypeError):
        session.rollback()
        return jsonify({
            "error": "Quantity must be a valid whole number"
        }), 400

    except Exception as e:
        session.rollback()
        print("SALE UPDATE ERROR:", repr(e))
        return jsonify({
            "error": "Could not update sale"
        }), 500



@app.route("/sale_details", methods=["GET", "POST"])
@jwt_required()
def sale_details():
    email = get_jwt_identity()

    user = session.scalars(
        select(User).where(User.email == email)
    ).first()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    if request.method == "GET":
        query = (
            select(SaleDetails)
            .join(Sale, SaleDetails.sale_id == Sale.id)
            .where(Sale.user_id == user.id)
        )

        details = session.scalars(query).all()
        results = []

        for detail in details:
            item = {
                "id": detail.id,
                "sale_id": detail.sale_id,
                "product_id": detail.product_id,
                "quantity": detail.quantity,
                "amount": detail.amount
            }
            results.append(item)

        return jsonify(results), 200

    elif request.method == "POST":
        data = request.get_json(silent=True) or {}

        sale_id = data.get("sale_id")
        product_id = data.get("product_id")
        quantity = data.get("quantity")
        amount = data.get("amount")

        if (
            sale_id is None
            or product_id is None
            or quantity is None
            or amount is None
        ):
            return jsonify({
                "error": "Please provide sale_id, product_id, quantity and amount"
            }), 400

        try:
            sale_id = int(sale_id)
            product_id = int(product_id)
            quantity = int(quantity)
            amount = float(amount)
        except (ValueError, TypeError):
            return jsonify({"error": "Please provide valid numeric values"}), 400

        if quantity <= 0 or amount < 0:
            return jsonify({
                "error": "Quantity must be greater than zero and amount cannot be negative"
            }), 400

        sale = session.scalars(
            select(Sale).where(
                Sale.id == sale_id,
                Sale.user_id == user.id
            )
        ).first()

        if sale is None:
            return jsonify({"error": "Sale not found"}), 404

        product = session.scalars(
            select(Product).where(
                Product.id == product_id,
                Product.user_id == user.id
            )
        ).first()

        if product is None:
            return jsonify({"error": "Product not found"}), 404

        new_detail = SaleDetails(
            sale_id=sale.id,
            product_id=product.id,
            quantity=quantity,
            amount=amount
        )

        session.add(new_detail)
        session.commit()

        return jsonify({
            "message": "Sale detail added successfully",
            "id": new_detail.id,
            "sale_id": new_detail.sale_id,
            "product_id": new_detail.product_id,
            "quantity": new_detail.quantity,
            "amount": new_detail.amount
        }), 201


@app.route('/purchases', methods=allowed_methods)
@jwt_required()
def purchases():
    if request.method == 'GET':
        query = select(Purchase)
        purchases_list = session.scalars(query)
        result = []

        for i in purchases_list:
            item = {
                'id': i.id,
                'product_id': i.product_id,
                'quantity': i.quantity,
                'date_purchased': i.date_purchased.isoformat(),
                'purchase_price': i.purchase_price
            }
            result.append(item)

        return jsonify(result), 200

    elif request.method == 'POST':
        data = request.get_json(silent=True) or {}

        if (
            not data.get('product_id')
            or not data.get('quantity')
            or not data.get('purchase_price')
        ):
            return jsonify({
                'Message': 'Ensure all fields are set'
            }), 400

        new_purchase = Purchase(
            product_id=data['product_id'],
            quantity=int(data['quantity']),
            purchase_price=float(data['purchase_price'])
        )

        session.add(new_purchase)
        session.commit()

        return jsonify({
            'Message': 'New purchase added'
        }), 201

    else:
        return jsonify({
            'Message': 'Method Not Allowed'
        }), 405


@app.route("/payments", methods=["GET", "POST"])
@jwt_required()
def payments():

    if request.method == "GET":
        email = get_jwt_identity()

        user = session.scalars(select(User).where(user.email == email)).first()

        if not user:
            return jsonify({"error":"User not found"}),404


        query = select(Payment)
        payments_list = session.scalars(query)

        results = []

        for pay in payments_list:
            item = {
                "id": pay.id,
                "amount": pay.amount,
                "payment_method": pay.payment_method,
                "date_paid": (
                    pay.date_paid.isoformat()if pay.date_paid else None
                ),
                "sale_id": pay.sale_id,
                "status":pay.status
            }
            results.append(item)

        return jsonify(results), 200

    elif request.method == "POST":
        data = request.get_json(silent=True) or {}
        sale_id=data.get("sale.id")
        amount = data.get("amount")
        payment_method = data.get("payment_method")
        phone_number = data.get("phone_number")

        if sale_id is None or amount is None or not payment_method:
            return jsonify({
                "error":"Sale ID,amount and payment method is required"
            }),400
        try:
            sale_id = int(sale_id)
            amount = float(amount)

            if sale_id <= 0 or amount <= 0:
                return jsonify ({"error":"Sale ID and amount error"})
        except (ValueError,TypeError):
            return jsonify ({
                "error":"Sale ID and amount must be a valid number"
            }),400
        if payment_method =="M-pesa" and not phone_number:
            return jsonify ({"error":"phone number is required"}),400
        
        if (
            data.get("payment_method") == "M-Pesa"# checks whether mpesa is selected
            and not data.get("phone_number")# checks for phone number
        ):
            return jsonify({
                "Error": "Phone number is required for M-Pesa payments"
            }), 400


        if (
            not data.get("amount")
            or not data.get("payment_method")
        ):
            return jsonify({
                "Error": "Ensure all fields are set"
            }), 400

        email = get_jwt_identity()
        user= session.scalars(
            select(User).where(User.email == email)
        ).first()

        if not user:
            return jsonify({"Error": "User not found"}), 404

        sale = session.get(Sale,sale_id)

        if not sale:
            return jsonify({"Error":"Sale not found"}),404 
        #check whether payment has already started or completed
        payment=session.scalars(select(Payment).where(Payment.sale_id == sale.id,Payment.user_id == user.id,Payment.status.in_(["pending","completed"]))).first()
        
        if payment:
            return jsonify({
                "error":"This sale cannot be edited because payment is pending or completed"
            }),403

        if sale.user_id !=user.id:
            return jsonify({
                "Error":"cannot pay another user's sale"
            }),403
        #prevent duplicate payments
        existing_payment = session.scalars(select(Payment).where(Payment.sale_id == sale.id,Payment.user_id == user.id,Payment.status.in_(["pending","completed"]))).first()
        if existing_payment:
            return jsonify ({
                "error":"A payment already exists","status":existing_payment.status
            }),409

        if float (data["amount"]) != sale.total_amount:
            return jsonify({
                "Error":"payment amount must be full"
            }),400
        
        if data["payment_method"] == "M-Pesa":
            payload = {
                "amount": data["amount"],
                "phone_number": data["phone_number"],
                "sale_id": sale.id
            }
            try:
                response = make_stk_push(payload)
            except Exception as e:
                print("M-Pesa STK Push error:", e)
                return jsonify({
                    "Error": "Could not initiate M-Pesa payment"
                }), 502 # returns an error rather than creating a normal payment record

            return jsonify({
                "Message": "M-Pesa payment request sent to Safaricom",
                "SafaricomResponse": response
            }), 200

        new_payment = Payment(
            user_id=user.id,
            sale_id=sale_id,
            amount=amount,
            payment_method=payment_method,
            status="completed"
        )

        session.add(new_payment)
        session.commit()

        return jsonify({
            "Message": "A new payment has been added",
            "payment_id":new_payment.id,
            "sale_id":sale.id,
            "amount":amount,
            "status":new_payment.status
        }), 201

    else:
        return jsonify({
            "Error": "Method Not Allowed"
        }), 405


@app.route('/stk-push', methods=["POST"])
@jwt_required()
def stk_push():
    email = get_jwt_identity()

    user = session.scalars(
        select(User).where(User.email == email)
    ).first()

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    data = request.get_json(silent=True) or {}

    sale_id = data.get("sale_id")
    amount = data.get("amount")
    phone_number = data.get("phone_number")

    if sale_id is None or amount is None or not phone_number:
        return jsonify({
            "error": "Sale ID, amount and phone number are required"
        }), 400

    try:
        sale_id = int(sale_id)
        amount = float(amount)

        if sale_id <= 0 or amount <= 0:
            return jsonify({
                "error": "Sale ID and amount must be positive"
            }), 400

        # Confirm that this sale belongs to the logged-in user
        sale = session.scalars(
            select(Sale).where(
                Sale.id == sale_id,
                Sale.user_id == user.id
            )
        ).first()

        if not sale:
            return jsonify({
                "error": "Sale not found"
            }), 404

        #prevent another payment request while payment is pending
        existing_payment = session.scalars(select(Payment).where(Payment.sale_id == sale.id,Payment.user_id == user.id,Payment.status.in_(["pending","completed"]))).first()
        
        if existing_payment:
            return jsonify({"error":"A payment request exists for this sale","status":existing_payment.status}),409

        # Confirm that the payment amount matches the sale
        if round(amount, 2) != round(sale.total_amount, 2):
            return jsonify({
                "error": "Payment amount does not match the sale total"
            }), 400

        payload = {
            "amount": amount,
            "phone_number": phone_number,
            "sale_id": sale.id
        }

        response = make_stk_push(payload)
        if not response or response.get("ResponseCode") != "0":
            return jsonify({"error":"payment request denied","details":response}),502

        new_payment = Payment(
            user_id=user.id,
            sale_id=sale.id,
            amount=amount,
            payment_method="M-Pesa",
            phone_number=phone_number,
            mrid=response.get("MerchantRequestID"),
            crid=response.get("CheckoutRequestID"),
            status="pending"
        )

        session.add(new_payment)
        session.commit()

        return jsonify({
            "message": "M-Pesa payment request sent successfully",
            "payment_id": new_payment.id,
            "sale_id": sale.id,
            "amount": amount,
            "status": "pending",
            "safaricom_response": response
        }), 200

    except (ValueError, TypeError):
        return jsonify({
            "error": "Sale ID and amount must be valid numbers"
        }), 400

    except Exception as e:
        session.rollback()
        print("STK PUSH ERROR:", repr(e))

        return jsonify({
            "error": "M-Pesa payment could not be initiated"
        }), 500

@app.route('/saf-callback', methods=["POST"])
def saf_callback():
    try:
        payload = request.get_json()
        body = payload.get('Body', {})
        stkCallback = body.get('stkCallback', {})
        result_code = stkCallback.get('ResultCode')
        mrid = stkCallback.get('MerchantRequestID')
        crid = stkCallback.get('CheckoutRequestID')

        payment = session.scalars(select(Payment).where(Payment.mrid == mrid)).first()

        if payment:
            if payment.status == "completed" and payment.receipt_status == "sent":
                return {"message":"Payment and receipt already processed"}

            if result_code == 0:
                callback_metadata = stkCallback.get('CallbackMetadata', {})
                for item in callback_metadata.get('Item', []):
                    if item.get('Name') == 'MpesaReceiptNumber':
                        payment.transaction_code = item.get('Value')
                payment.status = "completed"
            else:
                payment.status = "failed"

            # Commit payment status FIRST - this is critical
            session.commit()

            # Generate the receipt PDF
            text = f"Trans Code : {payment.transaction_code}, Amount : {payment.amount}, Date : {payment.date_paid}"
            
            if result_code == 0:
                user = session.get(User,payment.user_id)
                if user:
                    result = create_pdf(text,payment.transaction_code,user.email)
                    if result == "success":
                        payment.receipt_status = "sent" 
                    else:
                        payment.receipt_status = "pending"
                    
                    session.commit()

                else:
                    print("Customer not found.Receipt email not sent")

    except Exception as e:
        print({"Message": "Error Processing Callback"})
        print({'stk push error': e})
        session.rollback()

    print("--------------------callback received--------------------------", flush=True)
    return {"message": "callback received"}

if __name__== "__main__":
    app.run(debug=True)