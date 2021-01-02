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
      coalesce(sheet.wrkt_dt, brkdn.wrkt_dt) wrkt_dt
      , coalesce(sheet.wrkt_typ, brkdn.wrkt_typ) wrkt_typ
      , brkdn.tot_tm_sec, sheet.tot_tm
      , coalesce(sheet.dist, brkdn.dist_mi) dist_mi
      , brkdn.pace_sec, sheet.pace
      , coalesce(sheet.gear, brkdn.gear) gear
      , brkdn.ele_up, brkdn.ele_down, sheet.elevation
      , brkdn.clothes
      , coalesce(sheet.notes, brkdn.notes) notes
      , coalesce(sheet.hr, brkdn.hr) hr
      , coalesce(sheet.cal_burn, brkdn.cal_burn) cal_burn
      , coalesce(sheet.category, brkdn.category) category
      , brkdn.temp_strt, brkdn.temp_feels_like_strt, brkdn.wethr_cond_strt
      , brkdn.hmdty_strt, brkdn.wind_speed_strt, brkdn.wind_gust_strt
      , brkdn.temp_end, brkdn.temp_feels_like_end, brkdn.wethr_cond_end
      , brkdn.hmdty_end, brkdn.wind_speed_end, brkdn.wind_gust_end
    from lake.exercise_sheet sheet
    inner join lake.exercise_brkdn brkdn
      on sheet.wrkt_dt = brkdn.wrkt_dt
      and sheet.wrkt_typ = brkdn.wrkt_typ
    where coalesce(sheet.wrkt_dt, brkdn.wrkt_dt) between %s and %s
    order by sheet.wrkt_dt asc
    ;
    """
    # where coalesce(sheet.wrkt_dt, brkdn.wrkt_dt) between to_date('2020-12-31 00:00:00','YYYY-MM-DD HH24:MI:SS') and to_date('9999-12-31 00:00:00','YYYY-MM-DD HH24:MI:SS')

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
