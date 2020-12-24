# First party classes
import os, sys

# Third party classes
from flask import Flask
from flask import jsonify
import json
import configparser

# Custom classes
import dao.ReadApiRelease as readApi

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

@app.route("/api/v1/info")
def home_index():
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))

    apiLst = readApi.getApiVersions(dbConfig['postgresql_read'])

    return jsonify({'api_version': apiLst}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
