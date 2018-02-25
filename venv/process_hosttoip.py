#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('hosttoip.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

FILE = "src/HostToIP"
DB_FILE = "ump_std.db"

def main():
    clean_db();
    with open(FILE, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip("\n")
            record = line.split("&&");
            if len(record) == 2:
                hostname = record[0];
                ipaddress = record[1];
                import_data(hostname,ipaddress);
            #else:
             #   logger.info('hostname=%s,ipddress=%s',hostname,ipaddress)
             #   print("hello")

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("delete from hosttoip");
    conn.commit();
    print("table hosttoip has been cleaned!");

def import_data(hostname,ipaddress):
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("insert into hosttoip (HOSTNAME,IP_ADDRESS) values (?,?)",(hostname,ipaddress));
    print('insert data success');
    conn.commit();

if __name__ == '__main__':
        main()


