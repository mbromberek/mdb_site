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

def getWrkt(dbConfig, wrktDt):
    cur = ''
    conn = ''

    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        return(readWrkt(cur, wrktDt))
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

def getWrktAll(dbConfig):
    selectQry = """
    select
      WRKT_DT
      , WRKT_TYP
      , tot_tm_sec
      , dist_mi
      , pace_sec
      , gear
      , temp_strt
      , temp_feels_like_strt
      , wethr_cond_strt
      ,hmdty_strt
      ,wind_speed_strt
      ,wind_gust_strt
      ,temp_end
      ,temp_feels_like_end
      ,wethr_cond_end
      ,hmdty_end
      ,wind_speed_end
      ,wind_gust_end
      ,clothes
      ,ele_up
      ,ele_down
      ,hr
      ,cal_burn
      ,notes
    from core_fitness.wrkt
    ;"""
    cur.execute(selectQry)

    wrktLst = []
    rowLst = cur.fetchall()
    # Get list of column names
    columns = [desc[0] for desc in cur.description]

    for row in rowLst:
        wrktLst.append(dict(zip(columns, row)))

    return wrktLst

def readWrkt(cur, wrktDt):
    '''
    Read in workouts based on passed date and returns it as a list of dictionaries
    '''
    selectQry = """
    select
      WRKT_DT
      , WRKT_TYP
      , tot_tm_sec
      , dist_mi
      , pace_sec
      , gear
      , tot_tm_sec
      , dist_mi
      , pace_sec
      , gear
      , temp_strt
      , temp_feels_like_strt
      , wethr_cond_strt
      ,hmdty_strt
      ,wind_speed_strt
      ,wind_gust_strt
      ,temp_end
      ,temp_feels_like_end
      ,wethr_cond_end
      ,hmdty_end
      ,wind_speed_end
      ,wind_gust_end
      ,clothes
      ,ele_up
      ,ele_down
      ,hr
      ,cal_burn
      ,notes
    from core_fitness.wrkt
    where wrkt_dt = %s
    ;"""

    cur.execute(selectQry, (wrktDt, ))

    wrktLst = []
    rowLst = cur.fetchall()
    # Get list of column names
    columns = [desc[0] for desc in cur.description]

    for row in rowLst:
        wrktLst.append(dict(zip(columns, row)))

    return wrktLst
