#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import sqlite3

#文件示例： NT_TCP_STATUS_HT&&Primary:BL685762:NT Primary:BL685765:NT Primary:HP-BL685-019:NT Primary:HP-BL685-054:NT
DB_FILE = "ump_std.db"
filename = 'src/groupTohost.txt'
groupname = ''
lines_tmp = []
agent_all = []
hostname = []

def main():
    clean_db()
    process_group()

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("delete from grouptoagent");
    conn.commit();
    print("table grouptoagent has been cleaned!");

def import_data(groupname,agentname,host,agent_length):
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("insert into grouptoagent (GROUPNAME,AGENTNAME,HOSTNAME,AGENT_LENGTH) values (?,?,?,?)", (groupname,agentname,host,agent_length));
    #print('insert data success');
    conn.commit();

def process_group():
    with open(filename, 'r') as file_to_read:
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

