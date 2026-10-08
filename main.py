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
from datetime import datetime

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


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        error = {"Error":  "Method Not Allowed"}
        return jsonify(error), 405
    elif request.method == "POST":
        data = request.get_json()

        email = data["email"]
        password = data["password"]
        
        if data["email"] == "" or data["password"] == "":
            error = {"Error":"Ensure email and password are set"}
            return jsonify(error),403

            query = select(User).filter_by(email=data["email"])
            existing_user = session.scalars(query).first()

            if not existing_user:
                error = {"Error":"Invalid Email"}
                return jsonify (error), 403

            if not bcrypt.check_password_hash(existing_user.password,password):
                error = {"Error":"Invalid password"}
                return jsonify(error), 403

            token = create_access_token(identity=email)
            return jsonify({"Message": "User logged in successfully","token":token}), 200
            
    else:
        error = {"error":"Method Not Allowed"}
        return jsonify(error), 405

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        error = {"Error":"Method Not Allowed"}
        return jsonify(error),405
    elif request.method == "POST":
        data = request.get_json()
        if data["full_name"] == "" or data["email"] == "" or data["password"] == "":
            error = {"Error": "Ensure all fields are set"}
            return jsonify(error), 403
        existing_user = session.query(User).filter_by(email = data["email"]).first()
        if existing_user :
            error = {"Error": "Email already exists"}
            return jsonify(error), 403
        else :
            hashed_password = bcrypt.generate_password_hash(
                data["password"]
            ).decode("utf-8")
            new_user = User(
                full_name=data["full_name"],
                email=data["email"],
                password=hashed_password,
                created_at = datetime.utcnow()
            )
            session.add(new_user)
            session.commit()

            token = create_access_token(identity =data["email"])

            return jsonify ({"message":"User created successfully","token":token}), 201
    else:
            error = {"Error": "Method Not Allowed"}
            return jsonify(error), 405


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
        query = select (Product)
        products = session.scalars(query)

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

@app.route("/sales",methods = ["GET", "POST"])
@jwt_required()
def sales():
    id = get_jwt_identity()

    product = session.scalars(select(product).where(product.id==id)).first()

    if request.method == "GET":
        query = select(Sale)
        sales = session.scalars(query)

        results = []
        for sale in sales:
            s ={"id":sale.id,
                "quantity":sale.quantity}
            results.append(s)
        return jsonify(results), 200
    elif request.method == "POST":
        data = request.get_json()
        if data ["quantity"] == "":
            error = {"error":"Ensure all fields are set"}
            return jsonify(error), 403
        else:
            new_sale = Sale(
                productID = product.id,
                quantity = float(data["quantity"])
            )
            session.add(new_sale)
            session.commit()
            return jsonify({"Message":"A new sale has been done successfully"}), 201
    else:
        error = {"Error":"Method Not Allowed"}
        return jsonify(error), 405

@app.route("/sale_details", methods = ["GET","POST"])
def sale_details():
    if request.method == "GET":
        query = select(sale_details)
        sale_details = session.scalars(query)

        results = []
        for sale_details in sale_details:
            sd = {"id":sale_details.quantity,
                  "quantity":sale_details.quantity,
                  "selling_price":sale_details.quantity,
                  "created_at":sale_details.created_at}
            results.append(sd)
        return jsonify(results),200
    elif request.method == "POST":
        data = request.get_json()
        if data["quantity"] == "" or data ["selling_price"] == "" or data["created_at"] == "":
            error = {"error":"Ensure all fields are set"}
            return jsonify(error), 403
        else:
            new_sale_detail = Sale_details(
                sale_id = data.get("sale_id"),
                product_id =float(data["product_id"]),
                created_at =data["created_at"]
            )
            session.add(new_sale_detail)
            session.commit()
            return jsonify({"Message":"A new sale detail has been added successfully"}), 201
    else:
        error = {"Error":"Method Not Allowed"}
        return jsonify(error), 405


@app.route("/purchases", methods = ["GET", "POST"])
def purchases():
    if request.method == "GET":
        query = select (Purchase)
        purchases = session.scalars(query)
        results = []
        for pur in purchases:
            p= {"id": pur.id,
                "quantity": pur.quantity,
                "buying_price": pur.buying_price,
                "created_at": pur.created_at}
            results.append(p)
        return jsonify(results), 200
    elif request.method == "POST":
        data = request.json()
        if data["quantity"] == "" or data["buying_price"] == "" or data["created_at"] == "":
            error = {"Error": "Ensure all fields are set"}
            return jsonify(error) ,403
        else:
            new_purchase = Purchase(
                product_id = data.get("product_id"),
                quantity = float(data["quantity"]),
                buying_price = float(data["buying_price"]),
                created_at = data["created_at"]
            )
            session.add(new_purchase)
            session.commit()
            return jsonify({"Message":"A new purchase has been made"}), 201
    else:
            error = {"Error": "Method Not Allowed"}
            return jsonify(error),405

@app.route("/payments", methods = ["GET", "POST"])
def payments():
    if request.method == "GET":
        query = select(Payment)
        payments = session.scalars(query)
        results = []
        for pay in payments:
            pa = {"id":pay.id,
                  "amount":pay.amount,
                  "payment_method":pay.payment_method,
                  "created_at":pay.created_at}
            results.append(pa)
        return jsonify(results), 200
    elif request.method == "POST":
        data = request.get_json()
        if data["amount"] == "" or data["payment_method"] == "" or data["created_at"] == "":
            error = {"Error":"Ensure all fields are set"}
            return jsonify(error), 403
        else:
            new_payment = Payment(
                sale_id = data.get("sale_id"),
                amount = float(data["amount"]),
                payment_methods = data["payment_method"],
                created_at = data["created_at"]
            )
            session.add(new_payment)
            session.commit()
            return jsonify ({"A new payment has been made"}), 201
    else:
        error = {"Error":"Method Not Allowed"}
        return jsonify(error), 405

if __name__== "__main__":
    app.run(debug=True)