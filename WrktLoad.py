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

# Third party classes

# Custom classes
import dao.ReadLakeExercises as readEx
import dao.ToWrkt as toWrkt

logging.config.fileConfig('logging.conf')
logger = logging.getLogger()
toWrkt.logger = logger
readEx.logger = logger

def normEx(exLstOrig):
    exLstMod = []
    for ex in exLstOrig:
        # Break up elevation into two fields
        ex['ele_up'] = ex['elevation'].split('↑')[0]
        ex['ele_down'] = ex['elevation'].split('↑')[1].split('↓')[0]
        ex.pop('elevation',None)

        weatherStart = ex['notes'].split('\n')[0]
        weatherEnd = ex['notes'].split('\n')[1]
        ex['clothes'] = ex['notes'].split('\n')[2]
        remainingNotes = '\n'.join(ex['notes'].split('\n')[3:])

        ex.update(splitWeather(weatherStart, keySuffix='_strt'))
        ex.update(splitWeather(weatherEnd, keySuffix='_end'))

        # print('Weather Start: ' + weatherStart)
        # print('Weather End: ' + weatherEnd)
        # print('Clothes: ' + ex['clothes'])
        # print('RemainingNotes: ' + remainingNotes)
        # print('\nNotes: ' + ex['notes'])

        ex['notes'] = remainingNotes
        ex.pop('category',None)
        logger.info(ex)

        # Break up Notes into Weather Start, Weather End, Clothes, Notes rest
        exLstMod.append(ex)

    return exLstMod

def splitWeather(wethrStr, keySuffix=''):
    '''
    Splits up weather from passed in string.
    Returns a dictionary of weather values.
    Key names can have the keySuffix appended to the end of each name. Default is no suffix
    '''
    wethrDict = {}
    wethrLst = wethrStr.split(',')
    wethrDict['temp' + keySuffix] = wethrLst[0].strip().split(' ')[1]
    wethrDict['wethr_cond' + keySuffix] = wethrLst[0].strip().split(' ')[3]
    wethrDict['hmdty' + keySuffix] = wethrLst[1].strip().split(' ')[0]
    wethrDict['wind_speed' + keySuffix] = wethrLst[2].strip().split(' ')[2]
    wethrDict['wind_gust' + keySuffix] = wethrLst[3].strip().split(' ')[2].split('mph')[0]
    wethrDict['temp_feels_like' + keySuffix] = wethrLst[4].strip().split(' ')[2]

    return wethrDict




def main():
    logger.info('WrktLoad Start')

    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))

    # Read Exercises from LAKE
    exLst = readEx.getExercises(dbConfig['postgresql_read'], strt_dt='2020-12-12')
    # print(exLst)
    # Normalize data in exLst to CORE format
    exNormLst = normEx(exLst)

    # Write Exercises to CORE_FITNESS
    toWrkt.writeExercises(dbConfig['postgresql_write'], exNormLst)
    logger.info('WrktLoad End')


if __name__ == '__main__':
    main()
