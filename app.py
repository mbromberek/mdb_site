# First party classes
import os, sys
import logging
import logging.config

# Third party classes
from flask import Flask
from flask import request, Response
from flask import jsonify
import simplejson as json
import configparser

# Custom classes
import dao.ReadApiRelease as readApi
import dao.ReadCoreWrkt as readWrkt
import dao.ToStgExercises as toStgEx
import WrktLoad

app = Flask(__name__)

dbConfig = configparser.ConfigParser()
progDir = os.path.dirname(os.path.abspath(__file__))
dbConfig.read(os.path.join(progDir, "database.ini"))

logging.config.fileConfig('logging.conf')
logger = logging.getLogger()
toStgEx.logger = logger
readWrkt.logger = logger

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

@app.route('/api/v1/wrktsLatest', methods=['GET'])
def getLatestWrkts():
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))

    latestWrktDt = readWrkt.getMaxWrktDt(dbConfig['postgresql_read'])
    wrkt = readWrkt.getWrkt(dbConfig['postgresql_read'], latestWrktDt)

    return jsonify({'workout': wrkt}), 200

@app.route('/api/v1/wrkt_sheet', methods=['POST'])
def createWrktSheet():
    logger.debug('createWrktSheet')
    wrkt = request.json['workout']
    try:
        newWrkt = WrktLoad.dictToStgEx(wrkt)
        newCoreWrkt = WrktLoad.processNewRecords()
    except Exception as error:
        logger.error(repr(error))
        return jsonify({'status':repr(error)}), 400
    return jsonify({'new_workout':newCoreWrkt}), 201

@app.route('/api/v1/wrkt_brkdn', methods=['POST'])
def createWrktBrkdn():
    logger.debug('createWrktBrkdn')
    wrkt = request.json['workout']
    logger.debug(wrkt)
    try:
        newWrkt = WrktLoad.dictToLakeEx(wrkt)
        newCoreWrkt = WrktLoad.processNewBrkdnRecords()
    except Exception as error:
        logger.error(repr(error))
        return jsonify({'status':repr(error)}), 400
    return jsonify({'new_workout':newCoreWrkt}), 201

@app.route('/api/v1/wrkt', methods=['PUT'])
def updtWrkt():
    return jsonify({'status':'not setup'}), 418

@app.route('/api/v1/wrktsAll', methods=['GET'])
def getWrktAll():
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))

    wrktLst = readWrkt.getWrktAll(dbConfig['postgresql_read'])

    return jsonify({'workout_list': wrktLst}), 200

@app.route('/api/v1/comparePace', methods=['GET'])
def compareWrktPace():
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))
    wrkt = request.json['workout']

    wrkt_compare = readWrkt.comparePace(dbConfig['postgresql_read'], wrkt)

    return jsonify({'workout_compare': wrkt_compare}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
