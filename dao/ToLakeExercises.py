#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''
'''
Used for Insert, Update, Delete for LAKE.EXERCISE_SHEET table
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
import dao.ReadLakeExercises as readEx

def writeExercises(dbConfig, exLst):
    cur = ''
    conn = ''
    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        insrtCt, updtCt = writeExerciseAll(cur, copy.deepcopy(exLst))
        conn.commit();
        return insrtCt
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return -1
    finally:
        cmnDAO.closeConnection(cur, conn)

def writeExerciseAll(cur, exLst):
    insrtCt = 0
    updtCt = 0
    for ex in exLst:
        columns = ex.keys()
        values = [ex[column] for column in columns]
        recordExist = readEx.exerciseExists(cur, ex['wrkt_dt'], ex['wrkt_typ'])
        if recordExist:
            killExercise(cur, ex['wrkt_dt'], ex['wrkt_typ'])

        isrtStmt = 'insert into lake.exercise_sheet (%s) values %s'
        logger.debug(cur.mogrify(isrtStmt, (psycopg2.extensions.AsIs(','.join(columns)), tuple(values))))
        cur.execute(isrtStmt, (psycopg2.extensions.AsIs(','.join(columns)), tuple(values)))
        if recordExist:
            insrtCt = insrtCt +1
        else:
            updtCt = updtCt +1
    return insrtCt, updtCt

def killExercise(cur, wrkt_dt, wrkt_typ):
    deleteQry = 'delete from lake.exercise_sheet where wrkt_dt = %s and wrkt_typ = %s'
    cur.execute(deleteQry, (wrkt_dt,wrkt_typ,))
    rowsDeleted = cur.rowcount
    return rowsDeleted
