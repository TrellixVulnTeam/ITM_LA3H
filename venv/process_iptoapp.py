#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('iptoapp.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

FILE = "src/ITM_HostToApp.lookup"
DB_FILE = "ump_std.db"

def main():
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
            else:
                print('格式存在问题的记录:'+ line)
                logger.error('格式存在问题的记录: %s',line)
             #   print("hello")
    logger.info('导入完成！')

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("delete from iptoapp");
    conn.commit();
    print("table iptoapp has been cleaned!");
    logger.error('表已被清空！')

def import_data(ipaddress,app_name,app_code):
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    try:
        c.execute("insert into iptoapp (IP_ADDRESS,APP_NAME,APP_CODE) values (?,?,?)",(ipaddress,app_name,app_code));
    except:
        print('重复的记录:'+ ipaddress);
        logger.error('重复的记录: %s', ipaddress)
    conn.commit();

if __name__ == '__main__':
        main()
