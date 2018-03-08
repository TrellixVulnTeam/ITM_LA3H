#!/usr/bin/python
# -*- coding: UTF-8 -*-

from xml.etree import ElementTree as et;
import re
import sqlite3

DB_FILE = "ump_std.db"
APP_FILE = "src/sysInfo.xml"
TABLE_NAME = "app_info"
global counter

def main():
    counter = 0
    clean_db();
    process(APP_FILE);
    print("Total %s application have been imported !" % counter)


def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    sql = "delete from " + TABLE_NAME
    c.execute(sql);
    conn.commit();
    print("Table %s has been cleaned!" % TABLE_NAME);

def import_app(c,sql):
    c.execute(sql);
    #print('insert data success');
    counter += 1



#生成json文件
def process(APP_FILE):
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    root = et.parse(APP_FILE);
    for recordInfo in root.iter("recordInfo"):
        tempDict = recordInfo.attrib
        sql_tmp = "insert into app_info values(";
        for fieldInfo in recordInfo.findall("fieldInfo"):
            slotName = fieldInfo.find('fieldChName').text;
            slotValue = fieldInfo.find("fieldContent").text;
            sql_tmp = sql_tmp + "'" + str(slotValue) + "',";
            tempDict[slotName] = slotValue;
        sql = sql_tmp[:-1];
        sql = sql + ");"
        import_app(c,sql);
    conn.commit();
    c.close()

if __name__ == '__main__':
    main()
