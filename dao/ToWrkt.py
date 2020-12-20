#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''
'''
Used for Insert, Update, Delete for Core.WRKT table
'''

# First party classes
import os, sys
import logging
import logging.config

# Third party classes
import psycopg2

# Custom classes
import dao.WrktCmnDAO as cmnDAO

def writeExercises(dbConfig, exLst):
    cur = ''
    conn = ''
    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        writeAll(cur, exLst)
        conn.commit();
    finally:
        cmnDAO.closeConnection(cur, conn)

def writeAll(cur, exLst):
    for ex in exLst:
        columns = ex.keys()
        values = [ex[column] for column in columns]
        isrtStmt = 'insert into core_fitness.wrkt (%s) values %s'

        logger.debug(cur.mogrify(isrtStmt, (psycopg2.extensions.AsIs(','.join(columns)), tuple(values))))
        cur.execute(isrtStmt, (psycopg2.extensions.AsIs(','.join(columns)), tuple(values)))
