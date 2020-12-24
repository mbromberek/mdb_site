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

def getApiVersions(dbConfig):
    cur = ''
    conn = ''
    # logger.info('Read from Lake.Exercise strt_dt: ' + str(strt_dt) + ' ' + 'end_dt: ' + str(end_dt))

    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        return(readAll(cur))
    finally:
        cmnDAO.closeConnection(cur, conn)


def readAll(cur):
    '''

    '''
    api_list=[]
    cur.execute("""
        select
            buildtime, vers, methods, links
        from cmn.apirelease
        """)
    rowLst = cur.fetchall()
    for row in rowLst:
        a_dict = {}
        a_dict['version'] = row[0]
        a_dict['buildtime'] = row[1]
        a_dict['methods'] = row[2]
        a_dict['links'] = row[3]
        api_list.append(a_dict)
    return api_list
