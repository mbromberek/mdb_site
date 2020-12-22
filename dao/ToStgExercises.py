#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''
'''
Used for Insert, Update, Delete for STG.EXERCISE table
'''

# First party classes
import os, sys
import logging
import logging.config
import copy

# Third party classes
import psycopg2

# Custom classes
import dao.WrktCmnDAO as cmnDAO

def writeExercises(dbConfig, exLst):
    cur = ''
    conn = ''
    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        writeExerciseAll(cur, copy.deepcopy(exLst))
        conn.commit();
        return True
    finally:
        cmnDAO.closeConnection(cur, conn)

def writeExerciseAll(cur, exLst):
    for ex in exLst:
        columns = ex.keys()
        values = [ex[column] for column in columns]
        isrtStmt = 'insert into stg.exercise (%s) values %s'

        logger.debug(cur.mogrify(isrtStmt, (psycopg2.extensions.AsIs(','.join(columns)), tuple(values))))
        cur.execute(isrtStmt, (psycopg2.extensions.AsIs(','.join(columns)), tuple(values)))

def removeExercises(dbConfig):
    cur = ''
    conn = ''
    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        delCt = removeAll(cur)
        conn.commit();
        return delCt
    finally:
        cmnDAO.closeConnection(cur, conn)

def removeAll(cur):
    delStmt = 'delete from stg.exercise'
    cur.execute(delStmt)
    return cur.rowcount
