#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''
'''
Used for Insert, Update, Delete for Core_fitness.WRKT table
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
import dao.ReadCoreWrkt as readWrkt

def writeWrkts(dbConfig, exLst):
    cur = ''
    conn = ''
    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        writeWrktAll(cur, copy.deepcopy(exLst))
        writeWrktTags(cur, exLst)
        conn.commit();
    finally:
        cmnDAO.closeConnection(cur, conn)

def writeWrktAll(cur, exLst):
    for ex in exLst:
        if len(readWrkt.readWrkt(cur, ex['wrkt_dt'], ex['wrkt_dt'])) >0:
            logger.info('Delete existing workout')
            killWrkt(cur, ex['wrkt_dt'])
            killWrktTags(cur, ex['wrkt_dt'])
        wrkt_tags = ex['wrkt_tags']
        ex.pop('wrkt_tags',None)

        columns = ex.keys()
        values = [ex[column] for column in columns]
        isrtStmt = 'insert into core_fitness.wrkt (%s) values %s'

        logger.debug(cur.mogrify(isrtStmt, (psycopg2.extensions.AsIs(','.join(columns)), tuple(values))))
        cur.execute(isrtStmt, (psycopg2.extensions.AsIs(','.join(columns)), tuple(values)))

def writeWrktTags(cur, exLst):
    for ex in exLst:
        wrkt_tags = ex['wrkt_tags']
        for tag in wrkt_tags:
            columns = tag.keys()
            values = [tag[column] for column in columns]
            isrtStmt = 'insert into core_fitness.wrkt_tags (%s) values %s'

            logger.debug(cur.mogrify(isrtStmt, (psycopg2.extensions.AsIs(','.join(columns)), tuple(values))))
            cur.execute(isrtStmt, (psycopg2.extensions.AsIs(','.join(columns)), tuple(values)))

def killWrkt(cur, wrkt_dt):
    '''
    delete passed in workout using wrkt_dt
    '''
    deleteQry = 'delete from core_fitness.wrkt where wrkt_dt = %s'
    cur.execute(deleteQry, (wrkt_dt,))
    rowsDeleted = cur.rowcount
    return rowsDeleted


def killWrktTags(cur, wrkt_dt):
    '''
    delete passed in workout tags using wrkt_dt
    '''
    deleteQry = 'delete from core_fitness.wrkt_tags where wrkt_dt = %s'
    cur.execute(deleteQry, (wrkt_dt,))
    rowsDeleted = cur.rowcount
    return rowsDeleted
