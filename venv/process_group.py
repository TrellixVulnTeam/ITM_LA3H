#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import logging

#文件示例： NT_TCP_STATUS_HT&&Primary:BL685762:NT Primary:BL685765:NT Primary:HP-BL685-019:NT Primary:HP-BL685-054:NT
DB_FILE = "ump_std.db"
filename = 'src/groupTohost.txt'
TABLE_NAME = "grouptoagent"
LOG_FILE = "logs/process_group.log"
global counter
counter = 0

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
    logger.info('开始导入group to host 数据！')
    clean_db()
    process_group()
    logger.info('正常导入%s条记录完成。', counter)

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    sql = "delete from " + TABLE_NAME
    c.execute(sql);
    conn.commit();
    print("Table %s has been cleaned!" % TABLE_NAME);
    logger.info('表%s已被清空！',TABLE_NAME)

def import_data(groupname,agentname,host,agent_length):
    global counter
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("insert into grouptoagent (GROUPNAME,AGENT_NAME,HOSTNAME,AGENT_LENGTH) values (?,?,?,?)", (groupname,agentname,host,agent_length));
    print('insert data success');
    conn.commit();
    counter += 1

def process_group():
    with open(filename, 'r',encoding='UTF-8') as file_to_read:
        for lines in file_to_read.readlines():
            #print(lines,end='')
            lines_tmp =  lines.split('&&')
            groupname = lines_tmp[0]
            #print(groupname)
            agent_all = lines_tmp[1].split()

            i = 0
            hostname = []
            while i <  len(agent_all):
                hostname = agent_all[i].split(':')
                agent_length = len(agent_all[i])
                if len(hostname) == 2:
                    host = hostname[0]
                elif len(hostname) == 3:
                    if hostname[2] == '01': #处理JMX 01类型 ,示例 10.1.88.81_ORM:UMP-JMX2:01
                        #host_tmp = []
                        host_tmp = hostname[0].split('_')
                        host = host_tmp[0]
                    elif hostname[2] == 'RDB': # 处理 RDB代理 ，示例 RZ:OIBS1-OIBS1-BL660216:RDB
                        #host_tmp = []
                        host_tmp = hostname[1].split('-',2)  #存在多个- 的情况，如RZ:REPDB-REPDB-ALM-DB-P01:RDB
                        host = host_tmp[2]
                    else:
                        host = hostname[1]
                import_data(groupname, agent_all[i], host,agent_length)
                i = i + 1

if __name__ == '__main__':
        main()

