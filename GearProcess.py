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
import dao.ToGear as toGear

logging.config.fileConfig('logging.conf')
logger = logging.getLogger()
toGear.logger = logger

def updtRetirement(retired, idLst, nameLst):
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))

    ids = ','.join(['\'' + str(elem) + '\'' for elem in idLst])
    names = ','.join(['\'' + str(elem) + '\'' for elem in nameLst])

    updtStatus = toGear.updtGearRetirement(dbConfig['postgresql_write'], ids, names, retired)

    return updtStatus
