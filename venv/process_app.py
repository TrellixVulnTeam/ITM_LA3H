#!/usr/bin/python
# -*- coding: UTF-8 -*-

from xml.etree import ElementTree as et;
import json
import re
import sqlite3

DB_FILE = "ump_std.db"
APP_FILE="src/sysInfo.xml"
JSON_TYPE="EN"

def main():
    clean_db();
    print('read node from xmlfile, transfer them to json, and save into jsonFile:')
    gen_json(APP_FILE,JSON_TYPE);
   # print_json(JSON_TYPE);

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("delete from app_info");
    conn.commit();
    print("database has been cleaned!");

def import_app(sql):
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute(sql);
    print('insert data success');
    conn.commit();

# 从json文件中读取，并打印
def print_json(JSON_TYPE):
    print('read json from jsonfile:')
    if JSON_TYPE=="CN":
        JSON_FILE="json_cn.json"
    elif JSON_TYPE=="EN":
        JSON_FILE="json_en.json"
    else:
        return 1
    for eachJson in open(JSON_FILE, 'r', encoding='utf8'):
        tempStr = json.loads(eachJson);
        print(tempStr)

#生成json文件
def gen_json(APP_FILE,JSON_TYPE):
    if JSON_TYPE=="CN":
        JSON_FILE="json_cn.json"
        FIELED_INFO="fieldChName"
    elif JSON_TYPE=="EN":
        JSON_FILE="json_en.json"
        FIELED_INFO="fieldEnName"
    else:
        return 1
    f = open(JSON_FILE, 'w', encoding="utf8");
    root = et.parse(APP_FILE);

    for recordInfo in root.iter("recordInfo"):
        tempDict = recordInfo.attrib
        sql_tmp = "insert into app_info values(";
        for fieldInfo in recordInfo.findall("fieldInfo"):
            slotName = fieldInfo.find(FIELED_INFO).text;
            slotValue = fieldInfo.find("fieldContent").text;
            sql_tmp = sql_tmp + "'" + str(slotValue) + "',";
            tempDict[slotName] = slotValue;
        tempJson = json.dumps(tempDict, ensure_ascii=False);
        sql = sql_tmp[:-1];
        sql = sql + ");"
        import_app(sql);
        #print(tempJson);
        f.write(tempJson + "\n");
        #print (tmpstr);
    f.close();
    return sql;

if __name__ == '__main__':
    main()
