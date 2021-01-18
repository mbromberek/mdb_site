#!/usr/bin/env python
# coding: utf-8
'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''

"""
Functions for converting time in seconds
"""

# First party classes
import re
import datetime, time
import math

def breakTimeFromSeconds(totTimeSec):
    if totTimeSec is None or math.isnan(totTimeSec):
        totTimeSec = 0
    hourTot = math.floor(totTimeSec/60/60)
    minTot = math.floor((totTimeSec/60/60 - hourTot) * 60)
    secTot = math.floor(((totTimeSec/60/60 - hourTot) * 60 - minTot) *60)
    return hourTot, minTot, secTot

def formatNumbersTime(h, m, s, forceHr=False):
    '''
    Format passed in hours, minutes, seconds into format Nh Nm Ns as a string
    Will not include hour if the value is zero unless forceHr is set to True
    '''
    durTotNumbers = ''
    if h != 0 or forceHr == True:
        durTotNumbers = str(h) + 'h '
    durTotNumbers = durTotNumbers + str(m) + 'm ' + str(s) + 's'
    return durTotNumbers
def formatSheetsTime(h, m, s):
    durTotSheets = str(h) + ':' + str(m) + ':' + str(s)
    return durTotSheets
