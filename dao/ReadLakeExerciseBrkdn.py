#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''
'''
Used for reading from Lake.Exercise_brkdn table
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

def getExercises(dbConfig, strt_dt=datetime.datetime(1,1,1), end_dt=datetime.datetime(9999,12,31)):
    '''
    Get Exercises from LAKE.EXERCISE_brkdn table based on the optional parameters strt_dt and end_dt that are in datetime.datetime format.
        strt_dt default: 0001-01-01
        end_dt default: 9999-12-31
    Returns read in exercises in a list of dictionaries
    '''
    cur = ''
    conn = ''
    # Validate strt_dt is in format of (4{\d}-2{\d}-2{\d})
    logger.info('Read from lake.exercise_brkdn strt_dt: ' + str(strt_dt) + ' ' + 'end_dt: ' + str(end_dt))

    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        return(readAll(cur, strt_dt, end_dt))
    finally:
        cmnDAO.closeConnection(cur, conn)

def readAll(cur, strt_dt, end_dt):
    '''
    Parameter database cursor
    Reads all records from LAKE.EXERCISE_BRKDN table
    Store results in list of dictionary using names of fields from SQL
    Returns exercises in list of disctionary
    '''
    selectQry = """
    select
      WRKT_DT, WRKT_TYP
      , TOT_TM_SEC
      , dist_mi
      , PACE_SEC
      , GEAR
      , ele_up, ele_down
      , category
      , hr
      , cal_burn
      , NOTES
      , temp_strt, temp_feels_like_strt, wethr_cond_strt
      , hmdty_strt, wind_speed_strt, wind_gust_strt
      , temp_end, temp_feels_like_end, wethr_cond_end
      , hmdty_end, wind_speed_end, wind_gust_end
    from lake.exercise_brkdn
    where exercise_brkdn.insrt_ts > %s and exercise_brkdn.insrt_ts < %s
    ;"""
    cur.execute(selectQry, (strt_dt,end_dt,))

    exLst = []
    rowLst = cur.fetchall()
    # Get list of column names
    columns = [desc[0] for desc in cur.description]
    # print(columns)

    for row in rowLst:
        exLst.append(dict(zip(columns, row)))
    # print(exLst)

    return exLst

def exerciseExists(cur, wrkt_dt, wrkt_typ):
    selectQry = 'select count(*) ct from lake.exercise_brkdn where wrkt_dt = %s and wrkt_typ = %s'
    cur.execute(selectQry, (wrkt_dt,wrkt_typ, ))
    result = cur.fetchone()
    if result[0] > 0:
        return True
    else:
        return False
