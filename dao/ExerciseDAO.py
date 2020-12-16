#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''
# First party classes
import os, sys
import configparser

# Third party classes
import psycopg2


def testDbConn(cur):
    # Get and print DB versions
    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    print(db_version)

    # Read from Lake doing a Group By of week for the year to print out total mileage for the year
    # Get and print DB versions
    cur.execute("select to_char(wrkt_dt,'YYYY-MM') RUN_MONTH, count(*) TOT_RUNS, sum(dist) TOT_DIST from lake.exercise where wrkt_typ in ('Running','Indoor Running') AND wrkt_dt >= to_date('2020-01-01','YYYY-MM-DD') group by to_char(wrkt_dt,'YYYY-MM') order by to_char(wrkt_dt,'YYYY-MM');")

    rowLst = cur.fetchall()
    for row in rowLst:
        print('Month ' + row[0] + ': ran ' + str(row[1]) + ' times for total mileage ' + str(row[2]))

def getConnection(dbConn):
    conn = psycopg2.connect(host=dbConn['host'], database=dbConn['database'], user=dbConn['user'], password=dbConn['password'])
    cur = conn.cursor()
    return conn,cur

def closeConnection(cur, conn):
    if (conn):
        cur.close()
        conn.close()


def main():
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(progDir + "/../database.ini")

    try:
        conn, cur = getConnection(dbConfig['postgresql'])
        testDbConn(cur)
    finally:
        closeConnection(cur, conn)


if __name__ == '__main__':
    main()
