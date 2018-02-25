#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import sqlite3
import re

DB_FILE = "ump_std.db"

def main():
    clean_db()
    query_sit()

def isIP(str): #判断字符串是否IP地址格式
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(str):
        return True
    else:
        return False

def clean_db(): #清除数据库
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    #c.execute("delete from ");
    #conn.commit();
    print("table  has been cleaned!");

def query_sit():
    f = open("rs.txt", 'w', encoding="utf8");
    conn = sqlite3.connect(DB_FILE);
    sqlStr = "select SITNAME,DISTRIBUTION from itm_sit_info";
    c = conn.execute(sqlStr); #循环所有situation
    rows_sit = c.fetchall()
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

            #根据下发的组或者agent列表进行处理
            dist = str(rows_sit[i][1]).split(',')
            if len(dist) > 1 : #situation直接下发到Agent的情况
                #print(dist)
                pass
            elif len(dist) == 1: #situation下发到组的情况
                #print(dist)
                sqlStr = "select HOSTNAME from grouptoagent where GROUPNAME = ?"
                c = conn.execute(sqlStr,dist); #根据组名称，查找主机名
                rows_group = c.fetchall()
                for j in range(len(rows_group)) :
                    agent = rows_group[j] #找到主机名
                    if isIP(agent[0]): #如果是IP地址格式的，则直接赋值给ip_address字段
                        ip_address = agent[0]
                    else:    #如果不是IP地址格式，则要继续查询
                        sqlStr = "select IP_ADDRESS from hosttoip where HOSTNAME = ?"
                        c = conn.execute(sqlStr,agent)  #根据主机名，查找IP地址
                        rows_host = c.fetchall()
                        if len(rows_host) > 0:  #如果找到了IP，则赋值
                            ip_address = rows_host[0]
                        elif len(rows_host) == 0 :  #如果没找到，则赋默认值
                            ip_address = 'N'

                        #根据IP地址，查找应用系统信息

                        print(str(sitname) + ":"+ agent[0] + ":" + ip_address[0] + ":" + sit_desc + ":" + n_componenttype + ":" + n_component + ":" + n_subcomponent)
                    pass



if __name__ == '__main__':
        main()