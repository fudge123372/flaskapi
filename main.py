#1.it has to have a route
#2.it has to have a method(POST/GET/DELETE/PUT)
#3.it has to have a status code(200,201,403)
#4.it has to return data as JSON (key : value pairs)

from flask import Flask,request,jsonify
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from models import Base,Product

app = Flask(__name__)


#create a connection to the database using sqlalchemy engine
engine = create_engine("sqlite:///./flask_duka_api.db", echo=True)

#create tables into the database using sqlalchemy
Base.metadata.create_all(engine)

#create a session to do sql transactions
sessions = Session(engine)

@app.route("/")
def home():
    if request.method == "GET":
        data = {"Flask API" : "Version 1"}
        return jsonify(data),200
    else:
        error = {"error" : "method not allowed"}
        return jsonify(error),405


@app.route ("/products")
def products():
    if request.method=="GET":
        query = select(Product)
        products = Session.scalars(query)

        results = []
        for prod in products:
            p={"id":prod.id,"product_name":prod.product_name,"buying_price":prod.buying_price,"selling_price":prod.selling_price}
            results.append(p)
    elif request.method=="POST":
        data =request.get_json()
        if data["product_name"] =="" or data ["buying_price"] =="" or data["selling_price"] == "":
            error = {"error":"Ensure all fields are set"}
            return jsonify(error),403
        else:
            #store in the database
            pass 
    else:
        error = {"Error" : "method not allowed"}
        return jsonify(error),405
    
app.run(debug=True)