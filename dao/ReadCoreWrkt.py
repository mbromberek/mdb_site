#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''
'''
Used for reading from Core_Fitness.WRKT table
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

def getMaxInsrtTs(dbConfig, type='None'):
    cur = ''
    conn = ''

    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        return(readInsrtTs(cur, type))
    finally:
        cmnDAO.closeConnection(cur, conn)

def getWrkt(dbConfig, wrktDt):
    cur = ''
    conn = ''

    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        return(readWrkt(cur, wrktDt, wrktDt))
    finally:
        cmnDAO.closeConnection(cur, conn)

def getWrktAll(dbConfig):
    cur = ''
    conn = ''

    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        return(readWrkt(cur, strtWrktDt=datetime.datetime(1,1,1), endWrktDt=datetime.datetime(9999,12,31)))
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
def readInsrtTs(cur, type):
    '''
    Parameter database cursor
    If type is None then reads all records
    Returns max WRKT_DT of passed in type
    '''
    selectQry = """
    select
      max(insrt_ts) max_insrt_ts
    from core_fitness.wrkt
    ;"""
    cur.execute(selectQry)

    row = cur.fetchone()
    if row[0] is None:
        result = datetime.datetime(1, 1, 1) #default result to 0001-01-01
    else:
        result = row[0]

    return result

def readWrkt(cur, strtWrktDt, endWrktDt):
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
    where wrkt_dt >= %s and wrkt_dt <= %s
    ;"""

    cur.execute(selectQry, (strtWrktDt, endWrktDt, ))

    wrktLst = []
    rowLst = cur.fetchall()
    # Get list of column names
    columns = [desc[0] for desc in cur.description]

    for row in rowLst:
        wrktLst.append(dict(zip(columns, row)))

    return wrktLst

def comparePace(dbConfig, wrktToCompare):

    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        selectQry = """
        select row_number() over (order by wrkt.pace_sec) pos
          , wrkt.wrkt_dt, wrkt_tags.tag_val
          , cmn.sec_to_tm_str(wrkt.tot_tm_sec, 'hms') tot_tm
          , wrkt.dist_mi
          , cmn.sec_to_tm_str(wrkt.pace_sec, 'hms') pace
          , wrkt.tot_tm_sec
          , wrkt.pace_sec
        from core_fitness.wrkt
        inner join core_fitness.wrkt_tags
          on wrkt.wrkt_dt = wrkt_tags.wrkt_dt
          and wrkt.wrkt_typ = wrkt_tags.wrkt_typ
        where
          wrkt.wrkt_typ = 'Running'
          and wrkt_tags.tag_typ = 'category'
          and wrkt_tags.tag_val in ('race','long run')
          and wrkt.dist_mi between (%s*0.9) and (%s*1.1)
        order by wrkt.pace_sec asc, wrkt.wrkt_dt desc
        ;
        """

        cur.execute(selectQry, (wrktToCompare['dist_mi'], wrktToCompare['dist_mi'], ))

        wrktLst = []
        rowLst = cur.fetchall()
        # Get list of column names
        columns = [desc[0] for desc in cur.description]
        for row in rowLst:
            wrktLst.append(dict(zip(columns, row)))
        workout_compare = {}
        workout_compare['workout_list'] = wrktLst
        workout_compare['compare_dist_mi'] = wrktToCompare['dist_mi']

        compareWrktDt = datetime.datetime.strptime(wrktToCompare['wrkt_dt'],'%m/%d/%Y %H:%M:%S %p')
        logger.info('wrktToCompare[wrkt_dt]' + str(compareWrktDt))
        for wrkt in wrktLst:
            logger.info('wrkt[wrkt_dt]' + str(wrkt['wrkt_dt']))
            if wrkt['wrkt_dt'] == compareWrktDt:
                workout_compare['position'] = wrkt['pos']
                break

        return(workout_compare)
    finally:
        cmnDAO.closeConnection(cur, conn)
