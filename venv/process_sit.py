#!/usr/bin/python
# -*- coding: UTF-8 -*-

from xml.etree import ElementTree as et;
import re
import sqlite3
import os
import logging

DB_FILE = "ump_std.db"
FILE_PATH = "src/SITUATION"
TABLE_NAME = "itm_sit_info"
LOG_FILE = "logs/process_sit.log"

global counter
global counter_err
counter = 0
counter_err = 0

#设置log
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create a file handler
handler = logging.FileHandler(LOG_FILE)
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)

#按照agent导入
def import_agent(path, word,agent):
    global counter
    for filename in os.listdir(path):
        fp = os.path.join(path, filename)
        if os.path.isfile(fp) and word in filename:
            proc_sit(fp,agent)
            counter += 1

def main():
    logger.info("开始处理situation xml文件！");
    #清空数据库
    clean_db();

    #根据列出的目录，调用导入函数
    agent_list = ['01','02','GB','HT','LZ','MQ','NT','OQ','RZ','T3','T5','UD','UL','UM','UX','VM','YJ','Others']
    for agent in agent_list:
       path = os.path.join(FILE_PATH,agent)
       word = "CEB_"
       import_agent(path,word,agent);
    logger.info("共处理situation%s个，其中%s个描述字段不符合规范需整改！",counter,counter_err);

#清空数据库
def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    sql = "delete from " + TABLE_NAME
    c.execute(sql);
    conn.commit();
    print("Table %s has been cleaned!" % TABLE_NAME);
    logger.info('表%s已被清空！',TABLE_NAME)

#执行导入SQL
def import_data(sql):
    global counter
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute(sql);
    conn.commit();
    counter += 1

#解析xml文件，并执行导入
def proc_sit(xmlfile,agent):
    global counter_err

    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();

    threshold = 'null'
    period = 'null'
    isstd_sit = 'null'
    severity = 'null'

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

        #SITNAME
        if str(slotName) == "SITNAME":
            sit_name = str(slotValue)

        #TEXT字段举例： [Status!='DEPLOYED';7*24;1]
        if str(slotName) == "TEXT":
            tmpDesc = str(slotValue).split(';');
            if len(tmpDesc) == 3:
                threshold = tmpDesc[0]
                period = tmpDesc[1]
                isstd_sit = tmpDesc[2]
            else:
                print("Situation描述字段不符合规范：%s" % sit_name )
                logger.warn("Situation描述字段不符合规范：%s",sit_name)
                counter_err += 1

        #级别处理。SITINFO 字段举例 ：  COUNT=3;ATOM=K01SERVER.SERVERNAME;TFWD=Y;SEV=Minor;TDST=0;~;
        if str(slotName) == "SITINFO":
            tmpInfo = str(slotValue)
            tmpSeverity = re.findall(r"SEV=(.*);TDST",tmpInfo)
            if len(tmpSeverity) == 0:
                severity = 'NA'
            elif tmpSeverity[0] == 'Critical':
                severity = '1'
            elif tmpSeverity[0] == 'Minor':
                severity = '2'
            elif tmpSeverity[0] == 'Warning':
                severity = '3'
            else:
                severity = '4'

    sql = sql_tmp + "'" + threshold + "','" + period + "','" + isstd_sit + "','" + severity +  "');"
    import_data(sql);
    return sql;

if __name__ == '__main__':
    main()






