#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import logging
DB_FILE = "ump_std.db"
# 连接数据库
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# 查询数据库，获得最近一小时的记录
cur.execute('''select * from hosttoip''')

rows = cur.fetchall()
dict = {}

for row in rows:
    dict[row[0]] = row[1]

print(dict['CCS-RED-APP-P01'])


