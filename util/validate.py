#!/usr/bin/env python
# coding: utf-8
'''
BSD 3-Clause License
Copyright (c) 2020, Mike Bromberek
All rights reserved.
'''

# First party classes
import re
import datetime, time
import math

def vDate(dtStr):
    print('dtStr: ' + str(dtStr))
    dtChckReg = r'^(19|20)\d\d([- /.])(0[1-9]|1[012])\2(0[1-9]|[12][0-9]|3[01])$'
    chckRslt = re.search(dtChckReg, str(dtStr), flags=re.IGNORECASE)
    if chckRslt:
        return True
    else:
        return False

def vDecimal(nbrStr):
    # if type(nbrStr) == int or type(nbrStr) == float:
    #     return True
    nbrChckReg = r'^\d+\.(\d)*$'
    nbrChckRslt = re.search(nbrChckReg, str(nbrStr), flags=re.IGNORECASE)
    if nbrChckRslt:
        return True
    else:
        return False


def vInt(nbrStr):
    nbrChckReg = r'^\d+(\.0)*$'
    nbrChckRslt = re.search(nbrChckReg, str(nbrStr), flags=re.IGNORECASE)
    print(nbrChckRslt)
    if nbrChckRslt:
        return True
    else:
        return False


# def vtimeStr(s):
