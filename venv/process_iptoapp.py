#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import logging

FILE = "src/ITM_HostToApp.lookup"
DB_FILE = "ump_std.db"
TABLE_NAME = "iptoapp"
LOG_FILE = "logs/process_iptoapp.log"
global counter_dup
global counter_err
global counter
counter_dup = 0
counter_err = 0
counter = 0

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

def main():
    global counter_err
    global counter
    clean_db();
    logger.info('开始导入ip to app 数据！')
    with open(FILE, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip("\n")
            record = line.split();
            if len(record) == 3:
                ipaddress = record[0];
                app_name = record[1];
                app_code = record[2];
                import_data(ipaddress,app_name,app_code);
                counter += 1
            else:
                print('格式存在问题的记录:'+ line)
                logger.error('格式存在问题的记录: %s',line)
                counter_err += 1
             #   print("hello")
    logger.info('正常导入%s条记录完成。另，%s条记录重复，%s条格式异常。',counter,counter_dup,counter_err)

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    sql = "delete from " + TABLE_NAME
    c.execute(sql);
    conn.commit();
    print("Table %s has been cleaned!" % TABLE_NAME);
    logger.info('表%s已被清空！',TABLE_NAME)

def import_data(ipaddress,app_name,app_code):
    global counter_dup
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    try:
        c.execute("insert into iptoapp (IP_ADDRESS,APP_NAME,APP_CODE) values (?,?,?)",(ipaddress,app_name,app_code));
    except:
        print('重复的记录:'+ ipaddress);
        logger.error('重复的记录: %s', ipaddress)
        counter_dup += 1
    conn.commit();

if __name__ == '__main__':
        main()
