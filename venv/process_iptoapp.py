#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3

FILE = "src/ITM_HostToApp.lookup"
DB_FILE = "ump_std.db"

def main():
    clean_db();
    with open(FILE, 'r', encoding="utf-8") as f:
        for line in f:
            line = line.strip("\n")
            record = line.split();
            if len(record) == 3:
                ipaddress = record[0];
                app_name = record[1];
                app_code = record[2];
                import_data(ipaddress,app_name,app_code);
            #else:
             #   logger.info('hostname=%s,ipddress=%s',hostname,ipaddress)
             #   print("hello")

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("delete from iptoapp");
    conn.commit();
    print("table iptoapp has been cleaned!");

def import_data(ipaddress,app_name,app_code):
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("insert into iptoapp (IP_ADDRESS,APP_NAME,APP_CODE) values (?,?,?)",(ipaddress,app_name,app_code));
    print('insert data success');
    conn.commit();

if __name__ == '__main__':
        main()
