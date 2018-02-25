#!/usr/bin/python
# -*- coding: UTF-8 -*-

from xml.etree import ElementTree as et;
import json
import re
import sqlite3
import os
import sys

def main():
   # search(para1, para2)
   # clean_db();
   proc_sit("src/SITUATION/01/CEB_Wls_AppStatus_ALL_ALL_M.xml")

def proc_sit(xmlfile):
    root = et.parse(xmlfile);
    for row in root.iter("ROW"):
        tempDict = row.attrib
        sql_tmp = "create table TABLE_NAME (";
        for childNode in row.getchildren():
            slotName = childNode.tag;
            sql_tmp = sql_tmp + " " + str(slotName) + " TEXT" + ",\n";

        sql = sql_tmp[:-2];
        sql = sql + ");"
        #import_app(sql);

        print(sql)
if __name__ == '__main__':
    main()