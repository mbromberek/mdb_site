#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''
'''
Used for reading from Lake.Exercise table
'''

# First party classes
import os, sys
import logging
import logging.config
import datetime

# Third party classes
import psycopg2

# Custom classes
import dao.WrktCmnDAO as cmnDAO

def getMaxWrktDt(dbConfig, type='None'):
    cur = ''
    conn = ''

    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        return(readMaxDt(cur, type))
    finally:
        cmnDAO.closeConnection(cur, conn)

def readMaxDt(cur, type):
    '''
    Parameter database cursor
    If type is None then reads all records
    Returns max WRKT_DT of passed in type
    '''
    selectQry = """
    select
      max(WRKT_DT) MAX_WRKT_DT
    from core_fitness.wrkt
    ;"""
    cur.execute(selectQry)

    row = cur.fetchone()
    if row[0] is None:
        result = datetime.datetime(1, 1, 1) #default result to 0001-01-01
    else:
        result = row[0]

    return result
