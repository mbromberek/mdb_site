# First party classes
import os, sys
import logging
import logging.config
import datetime

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
import WrktData as wrktData

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
    wrktLst = request.json['workouts']
    try:
        newWrktLst = WrktLoad.dictToStgEx(wrktLst)
        newCoreWrktLst = WrktLoad.processNewBrkdnRecords()
    except Exception as error:
        logger.error(repr(error))
        return jsonify({'status':repr(error)}), 400
    return jsonify({'new_workouts':newCoreWrktLst}), 201

@app.route('/api/v1/wrkt_brkdn', methods=['POST'])
def createWrktBrkdn():
    logger.debug('createWrktBrkdn')
    wrktLst = request.json['workouts']
    logger.debug(wrktLst)
    try:
        newWrktLst = WrktLoad.dictToLakeEx(wrktLst)
        newCoreWrktLst = WrktLoad.processNewBrkdnRecords()
    except Exception as error:
        logger.error(repr(error))
        return jsonify({'status':repr(error)}), 400
    return jsonify({'new_workouts':newCoreWrktLst}), 201

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
    if 'prcnt_delta' in request.json:
        prcntDelta = request.json['prcnt_delta']
    else:
        prcntDelta = 0.1

    wrkt_compare = readWrkt.comparePace(dbConfig['postgresql_read'], wrkt, prcntDelta=prcntDelta)

    return jsonify({'workout_compare': wrkt_compare}), 200

@app.route('/api/v1/comparePeriods', methods=['GET'])
def compareTimePeriods():
    '''
    Gets summary of current workouts of type wrkt_typ for passed in period_typ for start of period until current date or the period_end_dt passed

    period_typ - week|month|year (optional default week)
        Currently only works with week
    wrkt_typ - running|cycling|swimming
    period_end_dt - end date to use for period (optional default current date)
    previous_date - y|n (optional default n)
        Only used when period_end_dt is not passed

    returns
        period_compare - comparison of distance, time, number of workouts, between the two periods
        period_1 - summary of first period for period_end_dt until first day of period typ
        period_2 - summary of second period for period_end_dt -number of days in period until first day of period typ
    '''
    req = request.json
    if 'period_typ' in req:
        periodTyp = req['period_typ']
    else:
        periodTyp = 'week'

    if 'wrkt_typ' in req:
        wrktTyp = req['wrkt_typ']
    else:
        return jsonify({"error_msg":"Missing Workout Type"}), 400

    if 'period_end_dt' in req:
        #TODO validate the date is a valid format
        prdEndDt = datetime.datetime.strptime(req['period_end_dt'], '%Y-%m-%d')
    else:
        prdEndDt = datetime.datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)
        if 'previous_date' in req and req['previous_date'].lower() == 'y':
            prdEndDt = prdEndDt - datetime.timedelta(days=1)
    period_compare = wrktData.comparePeriods(periodTyp, wrktTyp, prdEndDt)
    return jsonify(period_compare), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
