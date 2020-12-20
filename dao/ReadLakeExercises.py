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

# Third party classes
import psycopg2

# Custom classes
import dao.WrktCmnDAO as cmnDAO

def getExercises(dbConfig, strt_dt='0001-01-01'):
    cur = ''
    conn = ''
    # Validate strt_dt is in format of (4{\d}-2{\d}-2{\d})
    logger.debug('strt_dt: ' + strt_dt)

    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        return(readAll(cur, strt_dt))
    finally:
        cmnDAO.closeConnection(cur, conn)

def readAll(cur, strt_dt):
    '''
    Parameter database cursor
    Reads all records from LAKE.EXERCISE table
    Store results in list of dictionary using names of fields from SQL
    Returns exercises in list of disctionary
    '''
    selectQry = """
    select
      WRKT_DT, WRKT_TYP
      , LAKE.TM_STR_to_SEC(TOT_TM,'hms') TOT_TM_SEC
      , DIST dist_mi
      , LAKE.TM_STR_to_SEC(PACE,'hms') PACE_SEC
      , GEAR
      , elevation
      , category
      , hr
      , cal_burn
      , NOTES
    from lake.exercise
    where wrkt_dt >= to_date(%s,'YYYY-MM-DD')
    ;"""
    cur.execute(selectQry, (strt_dt,))

    exLst = []
    rowLst = cur.fetchall()
    # Get list of column names
    columns = [desc[0] for desc in cur.description]
    # print(columns)

    for row in rowLst:
        exLst.append(dict(zip(columns, row)))
    # print(exLst)

    return exLst
