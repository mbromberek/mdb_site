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
from dateutil.relativedelta import relativedelta

# Third party classes
import configparser

# Custom classes
import dao.ReadCoreWrkt as readWrkt
import util.timeConv as tc

logging.config.fileConfig('logging.conf')
logger = logging.getLogger()
readWrkt.logger = logger

wkDayNbr = {"Monday":0,"Tuesday":1,"Wednesday":2,"Thursday":3,"Friday":4, "Saturday":5,"Sunday":6}
wrktTypDict = {"running":"'Running', 'Indoor Running'", "cycling":"'Cycling','Indoor Cycling'", "swimming":"Swimming"}

def comparePeriods(periodTyp, wrktTyp, prdEndDt):
    '''
    Compare workout summaries of two time periods that are both for the same length of time from start of the period.
    Example comparing run workouts between current week and previous week only using data up to Wednesday of the two weeks.
    prdEndDt is used for getting the end date in the two periods being compared
    '''
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))

    logger.info('Period Type: ' + periodTyp)
    logger.info('Workout Type: ' + wrktTyp)
    wrktTypVal = wrktTypDict[wrktTyp]

    if periodTyp.lower() == 'month':
        prd1EndDt = prdEndDt
        prdEndDay = int(prd1EndDt.strftime("%-d"))-1
        logger.info('Date %s is day %s of month', prd1EndDt, str( prdEndDay ))

        prd1StartDt = prd1EndDt - datetime.timedelta(days=prdEndDay)
        prd2StartDt = prd1StartDt + relativedelta(months=-1)
        prd2EndDt = prd1EndDt + relativedelta(months=-1)
    elif periodTyp.lower() == 'year':
        prd1EndDt = prdEndDt
        prdEndDay = int(prd1EndDt.strftime("%-j"))-1
        logger.info('Date %s is day %s of year', prd1EndDt, str( prdEndDay ))

        prd1StartDt = prd1EndDt - datetime.timedelta(days=prdEndDay)
        prd2StartDt = prd1StartDt + relativedelta(years=-1)
        prd2EndDt = prd1EndDt + relativedelta(years=-1)

    else:
        # if periodTyp.lower() == 'week':
        prd1EndDt = prdEndDt
        prdEndDay = wkDayNbr[prd1EndDt.strftime("%A")]
        logger.info('Date %s is day %s of week', prd1EndDt, str( prdEndDay ))

        prd1StartDt = prd1EndDt - datetime.timedelta(days=prdEndDay)
        prd2StartDt = prd1StartDt - datetime.timedelta(days=7)
        prd2EndDt = prd1EndDt - datetime.timedelta(days=7)

    logger.info('Summarize %s between %s and %s:', wrktTypVal, prd1StartDt, prd1EndDt)
    logger.info('Summarize %s between %s and %s:', wrktTypVal, prd2StartDt, prd2EndDt)

    prd1Sum = readWrkt.wrktSummary(dbConfig['postgresql_read'], wrktTypVal, prd1StartDt, prd1EndDt)
    prd1Sum['start_dt'] = prd1StartDt
    prd1Sum['end_dt'] = prd1EndDt
    prd1Sum['tot_tm'] =  tc.formatNumbersTime(*tc.breakTimeFromSeconds(prd1Sum['tot_tm_sec']))

    prd2Sum = readWrkt.wrktSummary(dbConfig['postgresql_read'], wrktTypVal, prd2StartDt, prd2EndDt)
    prd2Sum['start_dt'] = prd2StartDt
    prd2Sum['end_dt'] = prd2EndDt
    prd2Sum['tot_tm'] =  tc.formatNumbersTime(*tc.breakTimeFromSeconds(prd2Sum['tot_tm_sec']))

    prdComp = {}
    prdComp['dist_delta'] = prd1Sum['tot_dist'] - prd2Sum['tot_dist']
    if prd1Sum['tot_dist'] == 0:
        prdComp['dist_delta_pct'] = 0
    elif prd2Sum['tot_dist'] == 0:
        prdComp['dist_delta_pct'] = 100
    else:
        prdComp['dist_delta_pct'] = round(((prd1Sum['tot_dist'] / prd2Sum['tot_dist']) -1) *100,2)
    prdComp['tot_tm_delta_sec'] = prd1Sum['tot_tm_sec'] - prd2Sum['tot_tm_sec']
    if prd1Sum['tot_tm_sec'] == 0:
        prdComp['tot_tm_delta_pct'] = 0
    elif prd2Sum['tot_tm_sec'] == 0:
        prdComp['tot_tm_delta_pct'] = 100
    else:
        prdComp['tot_tm_delta_pct'] = round(((prd1Sum['tot_tm_sec'] / prd2Sum['tot_tm_sec']) -1) *100,2)
    prdComp['tot_tm_delta'] =  tc.formatNumbersTime(*tc.breakTimeFromSeconds(prdComp['tot_tm_delta_sec']))
    prdComp['nbr_delta'] = prd1Sum['nbr'] - prd2Sum['nbr']
    prdComp['day_of_nbr'] = prdEndDay
    prdComp['day_of_week'] = prd1EndDt.strftime("%A")

    return {"period_compare":prdComp,"period_1":prd1Sum,"period_2":prd2Sum}

def compareWeather(temp, wrktTyp, tempDelta, tempCompare):
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))

    similarWeatherWrkts = {}
    similarWeatherWrkts['temp'] = temp

    # determine range for weather compare
    if tempCompare == 'less':
        minTemp = -9999
        maxTemp = temp + tempDelta
    elif tempCompare == 'greater':
        minTemp = temp - tempDelta
        maxTemp = 9999
    else: #between
        minTemp = temp - tempDelta
        maxTemp = temp + tempDelta
    wrktTypVal = wrktTypDict[wrktTyp]
    similarWeatherWrkts['min_temp'] = minTemp
    similarWeatherWrkts['max_temp'] = maxTemp

    wrktLst = readWrkt.getWrktByWethr(dbConfig['postgresql_read'], minTemp, maxTemp, wrktTypVal)

    similarWeatherWrkts['workouts'] = wrktLst

    return similarWeatherWrkts


def getWrktsForDate(wrktDt, wrktTyp):
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))
    strtWrktDt = wrktDt
    endWrktDt = wrktDt + datetime.timedelta(hours=23, minutes=59, seconds=59)
    logger.info('strtWrktDt: ' + str(strtWrktDt))
    logger.info('endWrktDt: ' + str(endWrktDt))

    wrktLst = readWrkt.getWrkt(dbConfig['postgresql_read'], strtWrktDt, endWrktDt)

    return wrktLst
