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
        ex['notes'] = remainingNotes

        ex['wrkt_tags'] = calcWrktTags(ex)
        ex.pop('category',None)
        logger.info(ex)

        # Break up Notes into Weather Start, Weather End, Clothes, Notes rest
        exLstMod.append(ex)

    return exLstMod

def calcWrktTags(wrkt):
    '''
    Get workout tags using provided workout
    Creates a Category tag based on the workouts category field
    Return List of workout tags
    '''
    wrkt_tags = []
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
    exLst = readEx.getExercises(dbConfig['postgresql_read'], strt_dt='2020-12-10')
    # print(exLst)
    # Normalize data in exLst to CORE format
    exNormLst = normEx(exLst)

    # Write Exercises to CORE_FITNESS
    toWrkt.writeWrkts(dbConfig['postgresql_write'], exNormLst)
    logger.info('WrktLoad End')


if __name__ == '__main__':
    main()
