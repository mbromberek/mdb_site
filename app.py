# First party classes
import os, sys
# import json

# Third party classes
from flask import Flask
from flask import jsonify
import simplejson as json
import configparser

# Custom classes
import dao.ReadApiRelease as readApi
import dao.ReadCoreWrkt as readWrkt

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

@app.route('/api/v1/wrkts', methods=['GET'])
def getLatestWrkts():
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))

    latestWrktDt = readWrkt.getMaxWrktDt(dbConfig['postgresql_read'])
    wrkt = readWrkt.getWrkt(dbConfig['postgresql_read'], latestWrktDt)

    return jsonify({'workout': wrkt}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
