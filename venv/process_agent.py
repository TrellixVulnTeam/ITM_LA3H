#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import re
import logging
from itertools import islice

DB_FILE = "ump_std.db"
FILE = "src/listsystems.txt"
TABLE_NAME = "itm_agent_info"
LOG_FILE = "logs/process_agent.log"

global counter
counter = 0
global host_dict
host_dict = {}

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
    logger.info("开始处理systemlists.txt文件！");
    #清空数据库
    clean_db();
    process_agent();
    logger.info("处理完成！");
    print("处理完成，共%s条记录！" % counter)

def get_host_dict():
    global host_dict
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor();
    c.execute("select * from hosttoip");
    rows = c.fetchall()
    host_dict = {}
    for row in rows:
        host_dict[row[0]] = row[1]
    conn.close()

def isIP(str): #判断字符串是否IP地址格式
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(str):
        return True
    else:
        return False
#清空数据库
def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    sql = "delete from " + TABLE_NAME
    c.execute(sql);
    conn.commit();
    conn.close()
    print("Table %s has been cleaned!" % TABLE_NAME);
    logger.info('表%s已被清空！',TABLE_NAME)

def import_data(conn,AGENT_NAME,AGENT_CODE,AGENT_VERSION,AGENT_STATUS,HOST_NAME,IP_ADDRESS,INSTANCE,AGENT_HOST,AGENT_TYPE):
    global counter
    sqlStr = "insert into itm_agent_info  (AGENT_NAME,AGENT_CODE,AGENT_VERSION,AGENT_STATUS,HOST_NAME,IP_ADDRESS,INSTANCE,AGENT_HOST,AGENT_TYPE)" \
             "values (?,?,?,?,?,?,?,?,?) "
    conn.execute(sqlStr,(AGENT_NAME,AGENT_CODE,AGENT_VERSION,AGENT_STATUS,HOST_NAME,IP_ADDRESS,INSTANCE,AGENT_HOST,AGENT_TYPE))
    conn.commit()
    counter += 1

def process_agent():
    get_host_dict();
    conn = sqlite3.connect(DB_FILE);
    line_num = 0
    with open(FILE, 'r',encoding='UTF-8') as file_to_read:
        #for lines in file_to_read.readlines():
        for lines in islice(file_to_read, 1, None):
            #print(lines,end='')
            ip_address = '';
            lines_tmp =  lines.split()
            agent_name = lines_tmp[0]
            agent_code = lines_tmp[1]
            agent_version = lines_tmp[2]
            agent_status = lines_tmp[3]
            #print(groupname)

            agent_all = agent_name.split(":")
            if  len(agent_all) == 2:  #agent 格式，只有2个域的。示例 ： P55010P1:KUX
                instance = ''
                agent_host = agent_all[0]
                agent_type = agent_all[1]
                hostname = agent_host

                if agent_type == 'UAGENT00':  #处理UA相关代理
                    if len(re.findall(r"(.*)ASFSdp", agent_host)) > 0:
                        hostname = re.findall(r"(.*)ASFSdp", agent_host)[0]
                    elif len(re.findall(r"(.*)SNMPdp", agent_host)) > 0:
                        hostname = re.findall(r"(.*)SNMPdp", agent_host)[0]

                if len(re.findall(r"^N[0-9][0-9]|^P[0-9][0-9]|^R[0-9][0-9]|UAGENT00",agent_type)) > 0: #处理小用户启动的UA实例
                    try:
                        ip_address = host_dict[agent_host]
                    except:
                        if len(hostname.split("_")) > 1:
                            #try:
                            hostname = hostname.split("_")[1]
                            #except:
                            #print(hostname.split("_"))

                if isIP(hostname):
                    ip_address = hostname
                    hostname = ''

            elif len(agent_all) == 3:
                instance = agent_all[0]
                agent_host = agent_all[1]
                agent_type = agent_all[2]
                hostname = agent_host  #默认主机名就是中间这个域的值，下面会进行特殊处理

                if agent_type == '01' or agent_type == '02':  # 处理JMX 相关Agent ,示例 10.1.88.81_ORM:UMP-JMX2:01
                    ip_address = instance.split("_")[0]
                    hostname = ''
                elif agent_type == 'RDB' or agent_type == 'ASM' or agent_type == 'DG':  # 处理 RDB代理 ，示例 RZ:OIBS1-OIBS1-BL660216:RDB
                    hostname = agent_host.split('-', 2)[2]  # 存在多个- 的情况，如RZ:REPDB-REPDB-ALM-DB-P01:RDB
                    pass

            if  not isIP(ip_address):
                try:
                        ip_address = host_dict[hostname]
                except:
                    ip_address = ''
            import_data(conn,agent_name,agent_code,agent_version,agent_status,hostname,ip_address,instance,agent_host,agent_type)
    file_to_read.close()

if __name__ == '__main__':
    main()