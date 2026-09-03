#1.it has to have a route
#2.it has to have a method(POST/GET/DELETE/PUT)
#3.it has to have a status code(200,201,403)
#4.it has to return data as JSON (key : value pairs)

from flask import Flask,request,jsonify
import json

app = Flask(__name__)

@app.route("/")
def home():
    if request.method == "GET":
        data = {"Flask API" : "Version 1"}
        return jsonify(data),200
    else:
        error = {"error" : "method not allowed"}
        return jsonify(error),403

app.run(debug=True)