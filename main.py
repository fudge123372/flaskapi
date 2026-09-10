#1.it has to have a route
#2.it has to have a method(POST/GET/DELETE/PUT)
#3.it has to have a status code(200,201,403)
#4.it has to return data as JSON (key : value pairs)

from flask import Flask,request,jsonify
from sqlalchemy import create_engine
from models import Base

app = Flask(__name__)


#create a connection to the database using sqlalchemy engine
engine = create_engine("sqlite:///./flask_duka_api.db", echo=True)

#create tables into the database using sqlalchemy
Base.metadata.create_all(engine)


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
        pass
    elif request.method=="POST":
        pass
    else:
        error =
app.run(debug=True)