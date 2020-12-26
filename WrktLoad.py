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
import configparser
import logging
import logging.config
import re
import datetime

# Third party classes

# Custom classes
import dao.ReadLakeExercises as readEx
import dao.ToLakeExercises as toEx
import dao.ToWrkt as toWrkt
import dao.ReadStgExercises as readStgEx
import dao.ToStgExercises as toStgEx
import dao.ReadCoreWrkt as readWrkt


logging.config.fileConfig('logging.conf')
logger = logging.getLogger()
toWrkt.logger = logger
readEx.logger = logger
toEx.logger = logger
readStgEx.logger = logger
toStgEx.logger = logger
readWrkt.logger = logger

dbConfig = configparser.ConfigParser()
config = configparser.ConfigParser()

def dictToStgEx(wrktLst):
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))
    config.read(os.path.join(progDir, "config.txt"))

    sntzWrktLst = []
    for wrkt in wrktLst:
        sntzWrkt = {}
        sntzWrkt['wrkt_dt'] = wrkt['wrkt_dt']
        sntzWrkt['wrkt_typ'] = wrkt['wrkt_typ']
        sntzWrkt['tot_tm'] = wrkt['tot_tm_sec']
        sntzWrkt['dist'] = wrkt['dist_mi']
        sntzWrkt['pace'] = wrkt['pace_sec']
        sntzWrkt['notes'] = wrkt['notes']
        sntzWrkt['category'] = 'TEST'
        sntzWrkt['gear'] = wrkt['gear']
        sntzWrkt['elevation'] = 0
        sntzWrkt['hr'] = wrkt['hr']
        sntzWrkt['cal_burn'] = wrkt['cal_burn']
        sntzWrkt['dist_km'] = 0
        sntzWrktLst.append(sntzWrkt)

    toStgEx.writeExercises(dbConfig['postgresql_write'], sntzWrktLst)



def normEx(exLstOrig):
    exLstMod = []
    for ex in exLstOrig:
        # Break up elevation into two fields
        if ex['elevation'] != None:
            ex['ele_up'] = ex['elevation'].split('↑')[0]
            ex['ele_down'] = ex['elevation'].split('↑')[1].split('↓')[0]
        ex.pop('elevation',None)

        # Do not want to process notes for workouts before 2017-05-01
        if ex['wrkt_dt'] >= datetime.datetime(2017, 5, 1):
            notesDict = splitWeatherClothes(ex['notes'])
            if notesDict != None :
                ex.update(splitWeather(notesDict['weatherStart'], keySuffix='_strt'))
                ex.update(splitWeather(notesDict['weatherEnd'], keySuffix='_end'))
                ex['clothes'] = notesDict['clothes']
                ex['notes'] = notesDict['remainingNotes']

        ex['wrkt_tags'] = calcWrktTags(ex)
        ex.pop('category',None)
        logger.debug(ex)

        exLstMod.append(ex)

    return exLstMod


def splitWeatherClothes(rec):
    '''
    Use regular expression patterns to get the start, end, and clothes from passed in record.
    Gets the last position of the sections broken out to get the remainder of the notes.
    Returns dictionary of the pulled values. Any sections not found will have an empty string.
        Return dictionary keys are weatherStart, weatherEnd, clothes, remainingNotes
    '''
    logger.debug('Input Record:' + str(rec))
    d = {}
    if rec == None:
        return None

    oldRecPattern = r'^[\d|:](.*?)[am|pm] '
    weatherPattern = r'^\d(.*?)(\. |\n)'
    weatherStartPattern = r'Start:(.*?)([a-z]\.|\n)'
    weatherEndPattern = r'End:(.*?)([a-z]\.|\n)'
    clothesPattern = r'(Shorts|Tights)(.{0,125}?)(\.|\n)'

    matchWeatherStart = re.search(weatherStartPattern, rec, flags=re.IGNORECASE)
    matchWeather = re.search(weatherPattern, rec, flags=re.IGNORECASE)
    endMatchPos = 0
    if matchWeatherStart:
        d['weatherStart'] = matchWeatherStart.group(0).strip()
        endMatchPos = max(endMatchPos, matchWeatherStart.end(0))
    elif matchWeather:
        d['weatherStart'] = matchWeather.group(0).strip()
        endMatchPos = max(endMatchPos, matchWeather.end(0))
    else:
        d['weatherStart'] = ''
    matchWeatherEnd = re.search(weatherEndPattern, rec, flags=re.IGNORECASE)
    if matchWeatherEnd:
        d['weatherEnd'] = matchWeatherEnd.group(0).strip()
        endMatchPos = max(endMatchPos, matchWeatherEnd.end(0))
    else:
        d['weatherEnd'] = ''
    matchClothes = re.search(clothesPattern,rec, flags=re.IGNORECASE)
    if matchClothes:
        d['clothes'] = matchClothes.group(0).strip()
        endMatchPos = max(endMatchPos, matchClothes.end(0))
    else:
        d['clothes'] = ''

    d['remainingNotes'] = rec[endMatchPos:].strip()
    logger.debug('Weather Start:' + d['weatherStart'])
    logger.debug('Weather End:' + d['weatherEnd'])
    logger.debug('Clothes:' + d['clothes'])
    logger.debug('Notes:' + d['remainingNotes'])
    return d


def calcWrktTags(wrkt):
    '''
    Get workout tags using provided workout
    Creates a Category tag based on the workouts category field
    Return List of workout tags
    '''
    wrkt_tags = []

    if wrkt['category'] == None:
        return wrkt_tags

    wrkt_categories = ['race','training', 'hard run', 'easy', 'long run', 'warm up', 'cool down', 'midfoot strike']
    for category_split in wrkt['category'].split(' - '):
        wrkt_tag = {}
        wrkt_tag['wrkt_dt'] = wrkt['wrkt_dt']
        wrkt_tag['wrkt_typ'] = wrkt['wrkt_typ']
        if category_split.lower() in wrkt_categories:
            wrkt_tag['tag_typ'] = 'category'
        else:
            wrkt_tag['tag_typ'] = 'wrkt_typ'
        wrkt_tag['tag_val'] = category_split.lower()
        wrkt_tags.append(wrkt_tag)

    return wrkt_tags


def splitWeather(wethrStr, keySuffix=''):
    '''
    Splits up weather from passed in string.
    Returns a dictionary of weather values.
    Key names can have the keySuffix appended to the end of each name. Default is no suffix
    '''

    wethrDict = {}

    if wethrStr == '':
        return wethrDict

    wethrLst = wethrStr.split(',')
    if len(wethrLst) == 5:
        wethrDict['temp' + keySuffix] = wethrLst[0].strip().split(' ')[1]
        wethrDict['wethr_cond' + keySuffix] = ' '.join(wethrLst[0].strip().split(' ')[3:])
        wethrDict['hmdty' + keySuffix] = wethrLst[1].strip().split(' ')[0]
        wethrDict['wind_speed' + keySuffix] = wethrLst[2].strip().split(' ')[2]
        wethrDict['wind_gust' + keySuffix] = wethrLst[3].strip().split(' ')[2].split('mph')[0]
        wethrDict['temp_feels_like' + keySuffix] = wethrLst[4].strip().split(' ')[2]
    elif len(wethrLst) == 3:
        wethrDict['temp' + keySuffix] = wethrLst[0].strip().split(' ')[1]
        wethrDict['hmdty' + keySuffix] = wethrLst[1].strip().split(' ')[0]
        wethrDict['temp_feels_like' + keySuffix] = wethrLst[2].strip().split(' ')[2]
    elif len(wethrLst) == 1:
        wethrLst = wethrStr.split(' ')
        if wethrLst[0].isdigit() == False:
            wethrDict['temp' + keySuffix] = wethrLst[1].strip()
            if len(wethrLst) > 3:
                wethrDict['hmdty' + keySuffix] = wethrLst[3].strip()
            if len(wethrLst) >= 8:
                wethrDict['temp_feels_like' + keySuffix] = wethrLst[8].strip()
        elif len(wethrLst) == 5:
            wethrDict['temp' + keySuffix] = wethrLst[0].strip()
            if wethrLst[2].isdigit():
                wethrDict['hmdty' + keySuffix] = wethrLst[2].strip()
            else:
                wethrDict['temp_feels_like' + keySuffix] = wethrLst[4].strip()
        elif len(wethrLst) == 2:
            wethrDict['temp' + keySuffix] = wethrLst[0].strip()

    return wethrDict


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
        lakeReadDtRng['minDt'] = readWrkt.getMaxWrktDt(dbConfig['postgresql_read'])
        logger.info('Max CORE_FITNESS Workout date: ' + str(lakeReadDtRng['minDt']) )
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
    exNormLst = normEx(exLst)

    # Write Exercises to CORE_FITNESS
    toWrkt.writeWrkts(dbConfig['postgresql_write'], exNormLst)
    logger.info('WrktLoad End')


if __name__ == '__main__':
    processNewRecords()
