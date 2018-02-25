#!/usr/bin/python
# -*- coding: UTF-8 -*-

from xml.etree import ElementTree as et;
import json
import re
import sqlite3
import os
import sys

DB_FILE = "ump_std.db"

#按照agent导入
def import_agent(path, word,agent):
    for filename in os.listdir(path):
        fp = os.path.join(path, filename)
        if os.path.isfile(fp) and word in filename:
            print (fp)
            proc_sit(fp,agent)

def main():
   #清空数据库
   clean_db();

   #根据列出的目录，调用导入函数
   agent_list = ['01','02','GB','HT','LZ','MQ','NT','OQ','RZ','T3','T5','UD','UL','UM','UX','VM','YJ','Others']
   for agent in agent_list:
       path = os.path.join("src/SITUATION",agent)
       word = "CEB_"
       import_agent(path,word,agent);

#清空数据库
def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("delete from itm_sit_info");
    conn.commit();
    print("table itm_sit_info has been cleaned!");

#执行导入SQL
def import_data(sql):
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute(sql);
    print('insert data success');
    conn.commit();

#解析xml文件，并执行导入
def proc_sit(xmlfile,agent):
    threshold = 'null'
    period = 'null'
    isstd_sit = 'null'

    #解析xml文件，获取第一个ROW标签下的值
    tree = et.parse(xmlfile);
    root = tree.getroot()
    row = root.getchildren()[0]
    tempDict = row.attrib
    sql_tmp = "insert into itm_sit_info values('" + agent + "',";
    for childNode in row.getchildren():
        slotName = childNode.tag;
        slotValue = childNode.text;
        slotValue = str(slotValue);
        slotValue = slotValue.replace('\'', '"')
        sql_tmp = sql_tmp + "'" + slotValue + "',";
        tempDict[slotName] = slotValue;

        #TEXT字段举例： [Status!='DEPLOYED';7*24;1]
        if str(slotName) == "TEXT":
            tmpDesc = str(slotValue).split(';');
            if len(tmpDesc) == 3:
                threshold = tmpDesc[0]
                period = tmpDesc[1]
                isstd_sit = tmpDesc[2]

    tempJson = json.dumps(tempDict, ensure_ascii=False);
    sql = sql_tmp + "'" + threshold + "','" + period + "','" + isstd_sit + "');"
    print(sql)
    import_data(sql);
    return sql;

if __name__ == '__main__':
    main()






