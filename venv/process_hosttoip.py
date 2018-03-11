#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import logging

FILE = "src/HostToIP"
DB_FILE = "ump_std.db"
TABLE_NAME = "hosttoip"
LOG_FILE = "logs/process_hosttoip.log"
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

def main():
    logger.info('开始导入host to ip 数据！')
    global counter_err
    clean_db();
    with open(FILE, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip("\n")
            record = line.split("&&");
            if len(record) == 2:
                hostname = record[0];
                ipaddress = record[1];
                import_data(hostname,ipaddress);
            else:
                logger.error('有问题的记录:%s',line)
                print("有问题的记录:%s" % line)
                counter_err += 1
    logger.info('正常导入%s条记录完成。另，%s条记录异常。', counter,counter_err)

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    sql = "delete from " + TABLE_NAME
    c.execute(sql);
    conn.commit();
    print("Table %s has been cleaned!" % TABLE_NAME);
    logger.info('表%s已被清空！',TABLE_NAME)

def import_data(hostname,ipaddress):
    global counter
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("insert into hosttoip (HOSTNAME,IP_ADDRESS) values (?,?)",(hostname,ipaddress));
    conn.commit();
    counter += 1

if __name__ == '__main__':
        main()


