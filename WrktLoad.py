#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''
'''
Used for loading exercise/workout data between tables
'''

# First party classes
import os, sys
import logging
import logging.config
import re
import datetime

# Third party classes
import configparser

# Custom classes
import dao.ReadLakeExercises as readEx
import dao.ToLakeExercises as toEx
import dao.ToWrkt as toWrkt
import dao.ReadStgExercises as readStgEx
import dao.ToStgExercises as toStgEx
import dao.ToLakeExerciseBrkdn as toLakeExBrkdn
import dao.ReadLakeExerciseBrkdn as readExBrkdn
import dao.ReadCoreWrkt as readWrkt
import util.validate as validate
import util.normalizeLakeData as normData


logging.config.fileConfig('logging.conf')
logger = logging.getLogger()
toWrkt.logger = logger
readEx.logger = logger
toEx.logger = logger
readStgEx.logger = logger
toStgEx.logger = logger
toLakeExBrkdn.logger = logger
readWrkt.logger = logger
readExBrkdn.logger = logger
normData.logger = logger

dbConfig = configparser.ConfigParser()
config = configparser.ConfigParser()

def dictToStgEx(wrktLst):
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))
    config.read(os.path.join(progDir, "config.txt"))

    wrkt = wrktLst
    sntzWrkt = {}

    sntzWrkt['wrkt_dt'] = wrkt['wrkt_dt']
    # if validate.vDecimal(wrkt['wrkt_dt']):
    #     sntzWrkt['wrkt_dt'] = wrkt['wrkt_dt']
    # else:
    #     raise ValueError('Value for wrkt_dt: \'' + str(wrkt['wrkt_dt']) + '\' is not a valid date')

    sntzWrkt['wrkt_typ'] = wrkt['wrkt_typ']
    sntzWrkt['tot_tm'] = wrkt['tot_tm']
    if validate.vDecimal(wrkt['dist']):
        sntzWrkt['dist'] = float(wrkt['dist'])
    else:
        raise ValueError('Value for dist: \'' + str(wrkt['dist']) + '\' is not a valid number')

    sntzWrkt['pace'] = wrkt['pace']
    sntzWrkt['notes'] = wrkt['notes']
    sntzWrkt['category'] = wrkt['category']
    sntzWrkt['gear'] = wrkt['gear']
    sntzWrkt['elevation'] = wrkt['elevation']
    if validate.vInt(wrkt['hr']):
        sntzWrkt['hr'] = int(wrkt['hr'])
    else:
        raise ValueError('Value for hr: ' + str(wrkt['hr']) + ' is not a valid Integer')
    if validate.vInt(wrkt['cal_burn']):
        sntzWrkt['cal_burn'] = wrkt['cal_burn']
    else:
        raise ValueError('Value for cal_burn: ' + str(wrkt['cal_burn']) + ' is not a valid Integer')
    toStgEx.writeExercises(dbConfig['postgresql_write'], [sntzWrkt])
    return sntzWrkt


def dictToLakeEx(wrkt):
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))
    config.read(os.path.join(progDir, "config.txt"))

    sntzWrkt = {}

    sntzWrkt['wrkt_dt'] = wrkt['wrkt_dt']
    # if validate.vDecimal(wrkt['wrkt_dt']):
    #     sntzWrkt['wrkt_dt'] = wrkt['wrkt_dt']
    # else:
    #     raise ValueError('Value for wrkt_dt: \'' + str(wrkt['wrkt_dt']) + '\' is not a valid date')

    sntzWrkt['wrkt_typ'] = wrkt['wrkt_typ']
    sntzWrkt['tot_tm_sec'] = wrkt['tot_tm_sec'] #TODO Validate is an int
    if validate.vDecimal(wrkt['dist_mi']):
        sntzWrkt['dist_mi'] = float(wrkt['dist_mi'])
    else:
        raise ValueError('Value for dist: \'' + str(wrkt['dist']) + '\' is not a valid number')

    sntzWrkt['pace_sec'] = wrkt['pace_sec'] #TODO validate is an int
    # sntzWrkt['notes'] = wrkt['notes'] #TODO Should always be empty
    sntzWrkt['category'] = wrkt['category']
    sntzWrkt['gear'] = wrkt['gear']
    # sntzWrkt['elevation'] = wrkt['elevation']
    sntzWrkt['ele_up'] = wrkt['ele_up'] #TODO validate is an int
    sntzWrkt['ele_down'] = wrkt['ele_down'] #TODO validate is an int
    if validate.vInt(wrkt['hr']):
        sntzWrkt['hr'] = int(wrkt['hr'])
    else:
        raise ValueError('Value for hr: ' + str(wrkt['hr']) + ' is not a valid Integer')
    if validate.vInt(wrkt['cal_burn']):
        sntzWrkt['cal_burn'] = wrkt['cal_burn']
    else:
        raise ValueError('Value for cal_burn: ' + str(wrkt['cal_burn']) + ' is not a valid Integer')

    #TODO setup validation of fields
    sntzWrkt['temp_strt'] = wrkt['wethr_start']['temp']
    sntzWrkt['temp_feels_like_strt'] = wrkt['wethr_start']['temp_feels_like']
    sntzWrkt['wethr_cond_strt'] = wrkt['wethr_start']['cond']
    sntzWrkt['hmdty_strt'] = wrkt['wethr_start']['hmdty']
    sntzWrkt['wind_speed_strt'] = wrkt['wethr_start']['wind_speed']
    sntzWrkt['wind_gust_strt'] = wrkt['wethr_start']['wind_gust']
    sntzWrkt['temp_end'] = wrkt['wethr_end']['temp']
    sntzWrkt['temp_feels_like_end'] = wrkt['wethr_end']['temp_feels_like']
    sntzWrkt['wethr_cond_end'] = wrkt['wethr_end']['cond']
    sntzWrkt['hmdty_end'] = wrkt['wethr_end']['hmdty']
    sntzWrkt['wind_speed_end'] = wrkt['wethr_end']['wind_speed']
    sntzWrkt['wind_gust_end'] = wrkt['wethr_end']['wind_gust']

    toLakeExBrkdn.writeExercises(dbConfig['postgresql_write'], [sntzWrkt])
    return sntzWrkt


def getLakeReadDtRng():
    lakeReadDtRng = {}
    if config['lake_read']['hardcode_read_dt'] == 'Y':
        minYr = int(config['lake_read']['min_dt'].split('-')[0])
        minMo = int(config['lake_read']['min_dt'].split('-')[1])
        minDay = int(config['lake_read']['min_dt'].split('-')[2])
        lakeReadDtRng['minDt'] = datetime.datetime(minYr,minMo,minDay)
        maxYr = int(config['lake_read']['max_dt'].split('-')[0])
        maxMo = int(config['lake_read']['max_dt'].split('-')[1])
        maxDay = int(config['lake_read']['max_dt'].split('-')[2])
        lakeReadDtRng['maxDt'] = datetime.datetime(maxYr,maxMo,maxDay)

    else:
        # lakeReadDtRng['minDt'] = readWrkt.getMaxWrktDt(dbConfig['postgresql_read'])
        lakeReadDtRng['minDt'] = readWrkt.getMaxInsrtTs(dbConfig['postgresql_read'])
        logger.info('Max CORE_FITNESS Insert Timestamp: ' + str(lakeReadDtRng['minDt']) )
        lakeReadDtRng['maxDt'] = datetime.datetime(9999,12,31)
    return lakeReadDtRng


def processNewRecords():
    logger.info('WrktLoad Start')

    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))
    config.read(os.path.join(progDir, "config.txt"))

    lakeReadDtRng = getLakeReadDtRng()

    # Read Exercises from STG
    stgExLst = readStgEx.getExercises(dbConfig['postgresql_read'])
    logger.info('Number of Exercises read from STG: ' + str(len(stgExLst)))

    # Write Exercises to LAKE
    lakeInsrtCt = toEx.writeExercises(dbConfig['postgresql_write'], stgExLst)
    logger.info('Record count loaded to LAKE.EXERCISE: ' + str(lakeInsrtCt))
    # If records were read: Delete Exercises from STG
    if lakeInsrtCt > 0 and config['stg']['delete_stg'] == 'Y':
        stgDelCt = toStgEx.removeExercises(dbConfig['postgresql_write'])
        logger.info('Record count deleted from STG.EXERCISE: ' + str(stgDelCt))

    # Read Exercises from LAKE
    exLst = readEx.getExercises(dbConfig['postgresql_read'], strt_dt=lakeReadDtRng['minDt'], end_dt=lakeReadDtRng['maxDt'])
    logger.info('Number of Exercises read from Lake: ' + str(len(exLst)))

    # Normalize data in exLst to CORE format
    exNormLst = normData.normExSheet(exLst)

    # Write Exercises to CORE_FITNESS
    toWrkt.writeWrkts(dbConfig['postgresql_write'], exNormLst)
    logger.info('WrktLoad End')
    return exNormLst

def processNewBrkdnRecords():
    logger.info('processNewBrkdnRecords Start')

    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))
    config.read(os.path.join(progDir, "config.txt"))

    lakeReadDtRng = getLakeReadDtRng()

    # Read Exercises from LAKE
    exLst = readExBrkdn.getExercises(dbConfig['postgresql_read'], strt_dt=lakeReadDtRng['minDt'], end_dt=lakeReadDtRng['maxDt'])
    logger.info('Number of Exercises read from Lake: ' + str(len(exLst)))

    # Normalize data in exLst to CORE format
    # exNormLst = normEx(exLst)
    exNormLst = []
    for ex in exLst:
        ex['wrkt_tags'] = calcWrktTags(ex)
        ex.pop('category',None)
        exNormLst.append(ex)

    # Write Exercises to CORE_FITNESS
    toWrkt.writeWrkts(dbConfig['postgresql_write'], exNormLst)
    logger.info('processNewBrkdnRecords End')
    return exNormLst


if __name__ == '__main__':
    processNewRecords()
