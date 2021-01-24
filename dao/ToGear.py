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

def updtGearRetirement(dbConfig, ids, names, retired):
    '''
    Takes list of IDs and Names of Gear to mark with the boolean retired status
    Returns Success or Fail
    '''
    cur = ''
    conn = ''
    updtQry = """
update core_fitness.gear
set retired = %s
where id in (~gear_id~)
  or name in (~gear_name~)
    """.replace('~gear_id~',ids).replace('~gear_name~',names)
    logger.info(updtQry)
    try:
        conn, cur = cmnDAO.getConnection(dbConfig)
        cur.execute(updtQry, (retired, ))
        conn.commit();
    finally:
        cmnDAO.closeConnection(cur, conn)

    return True
