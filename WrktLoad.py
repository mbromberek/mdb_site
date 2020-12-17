#! /Users/mikeyb/Applications/python3
# -*- coding: utf-8 -*-

'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''
'''
Used for loading exercise/workout data between tables
'''

# First party classes
import os, sys
import configparser

# Third party classes

# Custom classes
import dao.ReadLakeExercises as readEx
import dao.ToWrkt as toWrkt

def normEx(exLstOrig):
    exLstMod = []
    for ex in exLstOrig:
        ex.pop('elevation',None)
        ex.pop('category',None)
        exLstMod.append(ex)

    return exLstMod

def main():
    dbConfig = configparser.ConfigParser()
    progDir = os.path.dirname(os.path.abspath(__file__))
    dbConfig.read(os.path.join(progDir, "database.ini"))

    # Read Exercises from LAKE
    exLst = readEx.getExercises(dbConfig['postgresql_read'])
    # print(exLst)
    # Normalize data in exLst to CORE format
    exNormLst = normEx(exLst)

    # Write Exercises to CORE_FITNESS
    toWrkt.writeExercises(dbConfig['postgresql_write'], exNormLst)


if __name__ == '__main__':
    main()
