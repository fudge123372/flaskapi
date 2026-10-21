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


app = Flask(__name__)



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

    except Exception:
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

    # Find the logged-in user
    user = session.scalars(
        select(User).where(User.email == email)
    ).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if request.method == "GET":
        query = select(Sale).where(Sale.user_id == user.id)
        sales_list = session.scalars(query).all()

        results = []
        for sale in sales_list:
            results.append({
                "id": sale.id,
                "quantity": sale.quantity,
                "total_amount": sale.total_amount,
                "created_at": (
                    sale.created_at.isoformat()
                    if sale.created_at else None
                )
            })

        return jsonify(results), 200

    elif request.method == "POST":
        data = request.get_json(silent=True) or {}

        quantity = data.get("quantity")
        total_amount = data.get("total_amount")

        if quantity is None or total_amount is None:
            return jsonify({
                "error": "Quantity and total_amount are required"
            }), 400

        try:
            quantity = int(quantity)
            total_amount = float(total_amount)

            if quantity <= 0 or total_amount < 0:
                return jsonify({
                    "error": "Quantity must be positive and total_amount cannot be negative"
                }), 400

            new_sale = Sale(
                user_id=user.id,
                quantity=quantity,
                total_amount=total_amount
            )

            session.add(new_sale)
            session.commit()

            return jsonify({
                "message": "Sale created successfully",
                "sale_id": new_sale.id
            }), 201

        except (ValueError, TypeError):
            session.rollback()
            return jsonify({
                "error": "Quantity must be a whole number and total_amount must be numeric"
            }), 400


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
        query = select(Payment)
        payments_list = session.scalars(query)

        results = []

        for pay in payments_list:
            item = {
                "id": pay.id,
                "user_id": pay.user_id,
                "amount": pay.amount,
                "payment_method": pay.payment_method,
                "date_paid": pay.date_paid.isoformat(),
                "sale_id": pay.sale_id
            }
            results.append(item)

        return jsonify(results), 200

    elif request.method == "POST":
        data = request.get_json(silent=True) or {}

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

        sale = session.get(Sale,int(data["sale_id"]))

        if not sale:
            return jsonify({"Error":"Sale not founf"}),404 

        if sale.user_id !=user.id:
            return jsonify({
                "Error":"cannot pay another user's sale"
            }),403

        if float (data["amount"]) != sale.total_amount:
            return jsonify({
                "Error":"payment amount must be full"
            }),400

        new_payment = Payment(
            user_id=user.id,
            sale_id=data["sale_id"],
            amount=float(data["amount"]),
            payment_method=data["payment_method"]
        )

        session.add(new_payment)
        session.commit()

        return jsonify({
            "Message": "A new payment has been added"
        }), 201

    else:
        return jsonify({
            "Error": "Method Not Allowed"
        }), 405

if __name__== "__main__":
    app.run(debug=True)