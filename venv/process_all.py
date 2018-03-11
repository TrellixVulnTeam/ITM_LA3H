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
            sqlStr = "select SIT_DESC,N_ComponentType,N_Component,N_SubComponent from itm_sit_enrich " \
                     "where SITNAME = \'" + sitname + "\'"
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
            if len(dist) > 1 and group_flag != -1 : #situation直接下发到Agent的情况
                for agent in dist:
                    agent = agent.split(':')
                    if len(agent) == 2:
                        host = agent[0]
                    elif len(agent) == 3:
                        if agent[2] == '01':  # 处理JMX 01类型 ,示例 10.1.88.81_ORM:UMP-JMX2:01
                            # host_tmp = []
                            agent_tmp = agent[0].split('_')
                            host = agent_tmp[0]
                        elif agent[2] == 'RDB':  # 处理 RDB代理 ，示例 RZ:OIBS1-OIBS1-BL660216:RDB
                            # host_tmp = []
                            agent_tmp = agent[1].split('-', 2)  # 存在多个- 的情况，如RZ:REPDB-REPDB-ALM-DB-P01:RDB
                            host = agent_tmp[2]
                        else:
                            host = agent[1]
                    ip_address = hosttoip(host)
                    appname = iptoapp(ip_address)
                    content = str(sitname) + ":" + host + ":" + ip_address[0] + ":" + appname[0] + ":" + sit_desc + ":" + n_componenttype + ":" + n_component + ":" + n_subcomponent +  ":" + severity + "\n"
                    f.write(content)
                    import_data(conn,sitname,host,ip_address[0],appname[0],sit_desc,n_componenttype,n_component,n_subcomponent,severity)

                pass

            elif len(dist) > 1 and group_flag == -1 : #situation下发到多个组的情况
                for group in dist:
                    sqlStr = "select HOSTNAME from grouptoagent where GROUPNAME = \'" + group + "'"
                    c = conn.execute(sqlStr); #根据组名称，查找主机名
                    rows_group = c.fetchall()
                    for j in range(len(rows_group)) :
                        agent = rows_group[j] #找到主机名
                        host = agent[0]
                        ip_address = hosttoip(host)
                        appname = iptoapp(ip_address)
                        #根据IP地址，查找应用系统信息

                        #print(str(sitname) + ":"+ agent[0] + ":" + ip_address[0] + ":" + sit_desc + ":" + n_componenttype + ":" + n_component + ":" + n_subcomponent)
                        content = str(sitname) + ":"+ host + ":" + ip_address[0] + ":" + appname[0] + ":" + sit_desc + ":" + n_componenttype + ":" + n_component + ":" + n_subcomponent +  ":" + severity +  "\n"
                        f.write(content)
                        import_data(conn,sitname, host, ip_address[0], appname[0], sit_desc, n_componenttype, n_component,n_subcomponent,severity)
                        pass

            elif len(dist) == 1 or group_flag == -1 : #situation下发到单个组的情况
                #print(dist)
                sqlStr = "select HOSTNAME from grouptoagent where GROUPNAME = ?"
                c = conn.execute(sqlStr,dist); #根据组名称，查找主机名
                rows_group = c.fetchall()
                for j in range(len(rows_group)) :
                    agent = rows_group[j] #找到主机名
                    host = agent[0]
                    ip_address = hosttoip(host)
                    appname = iptoapp(ip_address)

                    #print(str(sitname) + ":"+ agent[0] + ":" + ip_address[0] + ":" + sit_desc + ":" + n_componenttype + ":" + n_component + ":" + n_subcomponent)
                    content = str(sitname) + ":" + host + ":" + ip_address[0] + ":" + appname[0] + ":" + sit_desc + ":" + n_componenttype + ":" + n_component + ":" + n_subcomponent + ":" + severity + "\n"
                    f.write(content)
                    import_data(conn,sitname, host, ip_address[0], appname[0], sit_desc, n_componenttype, n_component,n_subcomponent,severity)
                    pass
    conn.close()
    f.close()

def import_data(conn,sitname,host,ip_address,appname,sit_desc,n_componenttype,n_component,n_subcomponent,severity):
    global counter
    sqlStr = "insert into itm_policy  (APP_NAME,IP_ADDRESS,HOSTNAME,SIT_NAME,SIT_DESC,COMPONENT_TYPE,COMPONENT,SUB_COMPONENT,SEVERITY)" \
             "values (?,?,?,?,?,?,?,?,?) "
    conn.execute(sqlStr,(appname,ip_address,host,sitname,sit_desc,n_componenttype,n_component,n_subcomponent,severity))
    conn.commit()
    counter += 1

def hosttoip(hostname):
    ip_address = ()
    conn = sqlite3.connect(DB_FILE);
    if isIP(hostname):  # 如果是IP地址格式的，则直接赋值给ip_address字段
        ip_address = (hostname,)
    else:  # 如果不是IP地址格式，则要继续查询
        sqlStr = "select IP_ADDRESS from hosttoip where HOSTNAME = '" + hostname + "'"
        c = conn.execute(sqlStr)  # 根据主机名，查找IP地址
        rows_host = c.fetchall()
        if len(rows_host) > 0:  # 如果找到了IP，则赋值
            ip_address = rows_host[0]
        elif len(rows_host) == 0:  # 如果没找到，则赋默认值
            ip_address = ('NA',)
    return(ip_address)

def iptoapp(ip_address):
    appname = ()
    conn = sqlite3.connect(DB_FILE);
    sqlStr = "select APP_NAME from iptoapp where IP_ADDRESS = '" + ip_address[0] + "'"
    c = conn.execute(sqlStr);
    rows_app = c.fetchall()
    if len(rows_app) > 0 : #如果找到了APP，则赋值
        appname = rows_app[0]
    elif len(rows_app) == 0: #如果没找到，则赋默认值
        appname = ('NA',)
    return(appname)

if __name__ == '__main__':
        main()