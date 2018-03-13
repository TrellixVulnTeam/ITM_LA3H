#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import re
import logging
from itertools import islice

DB_FILE = "ump_std.db"
FILE = "src/agentlist.txt"
TABLE_NAME = "itm_agent_list"
LOG_FILE = "logs/process_agent_new.log"

global counter
counter = 0
global host_dict
host_dict = {}

# 设置log
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
    logger.info("开始处理agentlist.txt文件！")
    # 清空数据库
    #clean_db()

    # 循环agentlist.txt文件，逐个处理agent
    #process_agent()

    # 补漏，完善ip信息
    post_process()

    logger.info("处理完成！")
    print("处理完成，共%s条记录！" % counter)


# 清空数据库
def clean_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    sql = "delete from " + TABLE_NAME
    c.execute(sql)
    conn.commit()
    conn.close()
    print("Table %s has been cleaned!" % TABLE_NAME)
    logger.info('表%s已被清空！', TABLE_NAME)


def import_data(conn,AGENT_NAME,AGENT_CODE,AGENT_VERSION,HOSTNAME,IP_ADDRESS,INSTANCE,AGENT_HOST,AGENT_TYPE):
    global counter
    sqlStr = "insert into " + TABLE_NAME + " (AGENT_NAME,AGENT_CODE,AGENT_VERSION,HOSTNAME,IP_ADDRESS,INSTANCE,AGENT_HOST,AGENT_TYPE)" \
             "values (?,?,?,?,?,?,?,?) "
    conn.execute(sqlStr,(AGENT_NAME,AGENT_CODE,AGENT_VERSION,HOSTNAME,IP_ADDRESS,INSTANCE,AGENT_HOST,AGENT_TYPE))
    conn.commit()
    counter += 1


def get_host_dict():
    global host_dict
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("select * from hosttoip")
    rows = c.fetchall()
    host_dict = {}
    for row in rows:
        host = str(row[0]).upper()
        ip = row[1]
        host_dict[host] = ip
    conn.close()


def isIP(str): # 判断字符串是否IP地址格式
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(str):
        return True
    else:
        return False


def process_agent():
    get_host_dict()
    global counter
    conn = sqlite3.connect(DB_FILE)
    with open(FILE, 'r',encoding='UTF-8') as file_to_read:
        for line in file_to_read.readlines():
            # print(lines,end='')
            line_tmp = line.split()
            instance = ''
            agent_host = ''
            agent_type = ''
            if len(line_tmp) == 6:  # [93]  ip.pipe:#10.1.8.178[22399]<NM>P74017P1</NM>  iftsdb:P74017P1:RZ  RZ  06.31.02  AIX~6.1
                col2 = line_tmp[1]
                agent_name = line_tmp[2]
                agent_code = line_tmp[3]
                agent_version = line_tmp[4]
                ip_address = re.findall(r"^ip.pipe:#(.*)\[",col2)[0]
                hostname = re.findall(r"<NM>(.*)</NM>",col2)[0]

                if agent_code == '01' or agent_code == '02':  # [7048]  ip.pipe:#10.1.71.107[25141]<NM>UMP-JMX3</NM>  10.1.48.52_RWA:UMP-JMX3:01  01  06.23.00  Linux~
                    instance = agent_name.split(":")[0]
                    ip_address = instance.split("_")[0]

                # print("agent_name:%s  agent_code:%s  agent_version:%s ip_address:%s  hostname:%s" % (agent_name,agent_code,agent_version,ip_address,hostname))
                import_data(conn,agent_name,agent_code,agent_version,hostname,ip_address,instance,agent_host,agent_type)

            elif len(line_tmp) == 5: # [11448]  ip:#10.1.3.7[10000]<NM>ZPMPROXY01</NM>  ZPMProxy01ASFSdp:UAGENT00  UA  06.00.00
                col2 = line_tmp[1]
                agent_name = line_tmp[2]
                agent_code = line_tmp[3]
                agent_version = line_tmp[4]
                ip_address = ''
                hostname = ''

                if agent_code == 'EM':
                    ip_address = re.findall(r"<IP.PIPE>#(.*)\[",col2)[0]
                    hostname = agent_name
                elif isIP(col2):
                    ip_address = col2
                    hostname = agent_name.split(":")[0]
                else:
                    ip_address = re.findall(r"^ip:#(.*)\[", col2)[0]
                    hostname = re.findall(r"<NM>(.*)</NM>", col2)[0]

                import_data(conn, agent_name, agent_code, agent_version, hostname, ip_address, instance, agent_host,agent_type)
                # print("agent_name:%s  agent_code:%s  agent_version:%s ip_address:%s  hostname:%s" % (agent_name, agent_code, agent_version, ip_address, hostname))

            elif len(line_tmp) == 4:
                agent_name = line_tmp[1]
                agent_code = line_tmp[2]
                agent_version = line_tmp[3]
                if agent_code == 'RZ':  # RZ:OIBS1-OIBS1-BL660216:RDB
                    agent_host = agent_name.split(":")[1]
                    hostname = agent_host.split('-', 2)[2]  # 存在多个- 的情况，保留第二个-后面的值
                    try:
                        ip_address = host_dict[hostname.upper()]  # 从hosttoip文件中查询
                    except:
                        ip_address = ''

                # print("agent_name:%s  agent_code:%s  agent_version:%s ip_address:%s  hostname:%s" % (agent_name, agent_code, agent_version, ip_address, hostname))
                import_data(conn, agent_name, agent_code, agent_version, hostname, ip_address, instance, agent_host,agent_type)
            else:
                print("line:" % line)


def post_process():
    # 处理windows RDB Agent
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    sqlStr = "select HOSTNAME from " + TABLE_NAME + " where IP_ADDRESS='' and HOSTNAME like 'WIN%'"
    c.execute(sqlStr)
    rows = c.fetchall()
    for row in rows:
        hostname = row[0]
        sqlStr = "select IP_ADDRESS,AGENT_NAME from " + TABLE_NAME + " where AGENT_CODE='NT' and HOSTNAME like '" + hostname + "%'"
        c.execute(sqlStr)
        rows_ip = c.fetchall()
        if len(rows_ip) > 0:
            ip_address = rows_ip[0][0]
            agent_name = rows_ip[0][1]
            sqlStr = "update " + TABLE_NAME + " set IP_ADDRESS = ? where HOSTNAME = ?"
            conn.execute(sqlStr, (ip_address, hostname))
            conn.commit()
    conn.close()


if __name__ == '__main__':
    main()