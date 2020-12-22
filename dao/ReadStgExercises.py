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

def getExercises(dbConfig):
    cur = ''
    conn = ''

    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        return(readAll(cur))
    finally:
        cmnDAO.closeConnection(cur, conn)

def readAll(cur):
    '''
    Parameter database cursor
    Reads all records from LAKE.EXERCISE table
    Store results in list of dictionary using names of fields from SQL
    Returns exercises in list of disctionary
    '''
    selectQry = """
    select
      WRKT_DT, WRKT_TYP
      , TOT_TM
      , DIST
      , PACE
      , GEAR
      , elevation
      , category
      , hr
      , cal_burn
      , NOTES
    from stg.exercise
    ;"""
    cur.execute(selectQry)

    exLst = []
    rowLst = cur.fetchall()
    # Get list of column names
    columns = [desc[0] for desc in cur.description]
    # print(columns)

    for row in rowLst:
        exLst.append(dict(zip(columns, row)))
    # print(exLst)

    return exLst
