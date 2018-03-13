#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import re
import logging

DB_FILE = "ump_std.db"
TABLE_NAME = "itm_policy"
LOG_FILE = "logs/process_all.log"

global counter
counter = 0
global agent_to_ip_dict
agent_to_ip_dict = {}
global agent_to_host_dict
agent_to_host_dict = {}
global group_to_agent_dict
group_to_agent_dict = {}


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
    logger.info('开始处理ITM档案信息分析和入库！')
    clean_db()
    query_sit()
    logger.info("处理完成！共导入%s条档案信息",counter)

def isIP(str): #判断字符串是否IP地址格式
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(str):
        return True
    else:
        return False

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    sql = "delete from " + TABLE_NAME
    c.execute(sql);
    conn.commit();
    print("Table %s has been cleaned!" % TABLE_NAME);
    logger.info('表%s已被清空！',TABLE_NAME)

def query_sit():
    group_to_agent_dict()
    agent_to_ip_dict()
    group_to_agent_dict

    f = open("rs.txt", 'w', encoding="utf8");
    f.write("开始写文件\n")
    f.close()
    conn = sqlite3.connect(DB_FILE);
    sqlStr = "select SITNAME,DISTRIBUTION from itm_sit_info";
    c = conn.execute(sqlStr); #循环所有situation
    rows_sit = c.fetchall()
    f = open("rs.txt", 'a', encoding="utf8");
    if len(rows_sit) > 0:
        for i in range(len(rows_sit)):

            #根据situation名字进行丰富
            sitname = str(rows_sit[i][0])
            sqlStr = "select SIT_DESC,N_ComponentType,N_Component,N_SubComponent from itm_sit_enrich where SITNAME = \'{0}\'".format(
                sitname)
            c = conn.execute(sqlStr)
            rows_enrich = c.fetchall()
            if len(rows_enrich) == 0:
                sit_desc = 'NA'
                n_componenttype = 'NA'
                n_component = 'NA'
                n_subcomponent = 'NA'
            elif len(rows_enrich) > 0:
                sit_desc = rows_enrich[0][0]
                n_componenttype = rows_enrich[0][1]
                n_component = rows_enrich[0][2]
                n_subcomponent = rows_enrich[0][3]

            #根据situation名字查找sit原始信息
            sitname = str(rows_sit[i][0])
            sqlStr = "select ISSTD,PDT,THRESHOLD,SEVERITY from itm_sit_info " \
                     "where SITNAME = \'" + sitname + "\'"
            c = conn.execute(sqlStr)
            rows_enrich = c.fetchall()
            if len(rows_enrich) == 0:
                isstd = 'NA'
                pdt = 'NA'
                threshold = 'NA'
                severity = 'NA'
            elif len(rows_enrich) > 0:
                isstd = rows_enrich[0][0]
                pdt = rows_enrich[0][1]
                threshold = rows_enrich[0][2]
                severity = rows_enrich[0][3]

            #根据下发的组或者agent列表进行处理
            dist = str(rows_sit[i][1]).split(',')
            group_flag = str(rows_sit[i][1]).find(':')  #根据冒号判断是发到组还是Agent。 如果未找到，则值为-1
            if  group_flag != -1 : #situation直接下发到Agent的情况
                for agent in dist:
                    try:
                        ip_address = agent_to_ip_dict[agent]
                    except:
                        ip_address = ''

                    try:
                        host = agent_to_host_dict[agent]
                    except:
                        host = ''

                    appname = iptoapp(ip_address)
                    content = str(sitname) + ":" + host + ":" + ip_address + ":" + appname[0] + ":" + sit_desc + ":" + n_componenttype + ":" + n_component + ":" + n_subcomponent +  ":" + severity + "\n"
                    f.write(content)
                    import_data(conn,sitname,host,ip_address,agent,appname[0],sit_desc,n_componenttype,n_component,n_subcomponent,severity)

                pass

            elif group_flag == -1 : #situation下发到组的情况

                for group in dist:
                    # try:
                    #     agent_list = group_to_agent_dict[group]
                    # except:
                    #     print(group)
                    try:
                        agent_list = group_to_agent_dict[group]
                    except:
                        print(group)
                    for agent in agent_list :
                        try:
                            host = agent_to_host_dict[agent]  # 找到主机名
                        except:
                            host = ''
                        try:
                            ip_address = agent_to_ip_dict[agent]  # 找到IP
                        except:
                            ip_address = ''
                        appname = iptoapp(ip_address)  # 根据IP地址，查找应用系统信息

                        #print(str(sitname) + ":"+ agent[0] + ":" + ip_address[0] + ":" + sit_desc + ":" + n_componenttype + ":" + n_component + ":" + n_subcomponent)
                        content = str(sitname) + ":"+ host + ":" + ip_address + ":" + appname[0] + ":" + sit_desc + ":" + n_componenttype + ":" + n_component + ":" + n_subcomponent +  ":" + severity +  "\n"
                        f.write(content)
                        import_data(conn,sitname, host, ip_address, agent, appname[0], sit_desc, n_componenttype, n_component,n_subcomponent,severity)
                        pass

    conn.close()
    f.close()

def import_data(conn,sitname,host,ip_address,agent,appname,sit_desc,n_componenttype,n_component,n_subcomponent,severity):
    global counter
    sqlStr = "insert into itm_policy  (APP_NAME,IP_ADDRESS,AGENT_NAME,HOSTNAME,SIT_NAME,SIT_DESC,COMPONENT_TYPE,COMPONENT,SUB_COMPONENT,SEVERITY)" \
             "values (?,?,?,?,?,?,?,?,?,?) "
    conn.execute(sqlStr,(appname,ip_address,agent,host,sitname,sit_desc,n_componenttype,n_component,n_subcomponent,severity))
    conn.commit()
    counter += 1

def iptoapp(ip_address):
    appname = ()
    conn = sqlite3.connect(DB_FILE);
    sqlStr = "select APP_NAME from iptoapp where IP_ADDRESS = '" + ip_address + "'"
    c = conn.execute(sqlStr);
    rows_app = c.fetchall()
    if len(rows_app) > 0 : #如果找到了APP，则赋值
        appname = rows_app[0]
    elif len(rows_app) == 0: #如果没找到，则赋默认值
        appname = ('NA',)
    return(appname)


def agent_to_ip_dict():
    global agent_to_ip_dict
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor();
    c.execute("select AGENT_NAME,IP_ADDRESS from itm_agent_list where IP_ADDRESS != ''");
    rows = c.fetchall()
    agent_to_ip_dict = {}
    for row in rows:
        agent_to_ip_dict[row[0]] = row[1]
    conn.close()

def agent_to_host_dict():
    global agent_to_host_dict
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor();
    c.execute("select AGENT_NAME,HOSTNAME from itm_agent_list where HOSTNAME != ''");
    rows = c.fetchall()
    agent_to_host_dict = {}
    for row in rows:
        agent_to_host_dict[row[0]] = row[1]
    conn.close()

def group_to_agent_dict():
    global group_to_agent_dict
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor();
    c.execute("select GROUPNAME,AGENT_NAME from grouptoagent");
    rows = c.fetchall()
    group_to_agent_dict = {}
    for row in rows:
        group_to_agent_dict[row[0]] = row[1]
    conn.close()

if __name__ == '__main__':
        main()