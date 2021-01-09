#!/usr/bin/env python
# coding: utf-8
'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''

'''
Normalize data read from Lake table(s) for loading to CORE_FITNESS tables
'''
# First party classes
import os, sys
import logging
import logging.config
import datetime, time
import re
import copy

# Third party classes
# Custom classes

def normLakeExMerge(exLstOrig):
    exLstMod = []
    for ex in exLstOrig:
        exNorm = {}
        exNorm['wrkt_dt'] = ex['wrkt_dt']
        exNorm['wrkt_typ'] = ex['wrkt_typ']

        exNorm['tot_tm_sec'] = ex['tot_tm_sec']
        exNorm['dist_mi'] = ex['dist_mi']
        exNorm['pace_sec'] = ex['pace_sec']
        exNorm['gear'] = ex['gear']
        exNorm['hr'] = ex['hr']
        exNorm['cal_burn'] = ex['cal_burn']

        if ex['wrkt_dt'] >= datetime.datetime(2017, 5, 1):
            notesDict = splitWeatherClothes(ex['notes'])
        else:
            notesDict = None

        # Determine source for weather
        if ex['temp_strt'] is not None:
            logger.debug('temp from API')
            exNorm['temp_strt'] = ex['temp_strt']
            exNorm['temp_feels_like_strt'] = ex['temp_feels_like_strt']
            exNorm['wethr_cond_strt'] = ex['wethr_cond_strt']
            exNorm['hmdty_strt'] = ex['hmdty_strt']
            exNorm['wind_speed_strt'] = ex['wind_speed_strt']
            exNorm['wind_gust_strt'] = ex['wind_gust_strt']
            exNorm['temp_end'] = ex['temp_end']
            exNorm['temp_feels_like_end'] = ex['temp_feels_like_end']
            exNorm['wethr_cond_end'] = ex['wethr_cond_end']
            exNorm['hmdty_end'] = ex['hmdty_end']
            exNorm['wind_speed_end'] = ex['wind_speed_end']
            exNorm['wind_gust_end'] = ex['wind_gust_end']
        elif notesDict != None:
            logger.debug('temp from SHEET')
            exNorm.update(splitWeather(notesDict['weatherStart'], keySuffix='_strt'))
            exNorm.update(splitWeather(notesDict['weatherEnd'], keySuffix='_end'))

        # Deterine source for clothes
        if ex['clothes'] is not None:
            logger.debug('clothes from API:' + str(ex['clothes']))
            exNorm['clothes'] = ex['clothes']
        elif notesDict != None:
            logger.debug('clothes from SHEET')
            exNorm['clothes'] = notesDict['clothes']
        else:
            logger.info('clothes is null')
            exNorm['clothes'] = None

        # Determine source for elevation
        if ex['ele_up'] is None:
            if ex['elevation'] != None:
                exNorm['ele_up'] = ex['elevation'].split('↑')[0]
                exNorm['ele_down'] = ex['elevation'].split('↑')[1].split('↓')[0]
        else:
            exNorm['ele_up'] = ex['ele_up']
            exNorm['ele_down'] = ex['ele_down']

        # Breakup notes if needed
        if notesDict != None:
            exNorm['notes'] = notesDict['remainingNotes']
        else:
            exNorm['notes'] = ex['notes']

        exNorm['wrkt_tags'] = calcWrktTags(ex)
        logger.info(exNorm)

        exLstMod.append(exNorm)

    return exLstMod

def normExSheet(exLstOrig):
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

def calcWrktTags(wrkt):
    '''
    Get workout tags using provided workout
    Creates a Category tag based on the workouts category field
    Return List of workout tags
    '''
    wrkt_tags = []

    if wrkt['category'] == None:
        return wrkt_tags

    wrkt_categories = ['race','training', 'hard run', 'easy', 'long run', 'warm up', 'cool down', 'midfoot strike', 'virtual race']
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
