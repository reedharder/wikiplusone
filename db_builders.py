# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 16:20:48 2014

@author: Reed

functions to build SQL databases from wiki dump SQL scripts
"""

import os 
##import MySQLdb
from subprocess import Popen, PIPE
os.chdir("C://Users//Reed//Documents//Github//wikiplus1")
script="simplewiki-20140605-externallinks.sql"
script1="simplewiki-20140605-categorylinks.sql"
script2="simplewiki-20140605-pagelinks.sql"

db='simple1'
user='root'
passwd='reed2[shandy'
filename=script1
args=['mysql', db,'-u', user,'-p'+passwd]

process = Popen(args, stdout=PIPE, stdin=PIPE, shell=True)
sourcecall='source '+filename 
output = process.communicate(input=bytes(sourcecall, 'utf-8'))
