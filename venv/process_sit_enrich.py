#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3
import logging

#文件示例： 10.1.71.98	统一监控管理平台（UMP）	CEB-UMP
DB_FILE = "ump_std.db"
filename = 'src/ITM_Situation.lookup'
TABLE_NAME = "itm_sit_enrich"
LOG_FILE = "logs/process_sit_enrich.log"
global counter
global counter_err
counter = 0
counter_err = 0

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
    logger.info('开始导入sit_enrich 数据！')
    clean_db()
    process_sit_enrich()
    logger.info('正常导入%s条记录完成。', counter)

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    sql = "delete from " + TABLE_NAME
    c.execute(sql);
    conn.commit();
    print("Table %s has been cleaned!" % TABLE_NAME);
    logger.info('表%s已被清空！',TABLE_NAME)

def process_sit_enrich():
    global  counter_err
    global  counter
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    with open(filename, 'r',encoding='UTF-8') as file_to_read:
        for lines in file_to_read.readlines():
            #print(lines,end='')
            lines_tmp =  lines.split('\t')

            SITNAME = lines_tmp[0]
            SIT_DESC = lines_tmp[1]
            THRESHOLD_FLAG = lines_tmp[2]
            CUR_VALUE_FLAG = lines_tmp[3]
            DISPLAY_FLAG = lines_tmp[4]
            N_ComponentType = lines_tmp[5]
            N_ComponentTypeId = lines_tmp[6]
            N_Component = lines_tmp[7]
            N_ComponentId = lines_tmp[8]
            N_SubComponent = lines_tmp[9]
            N_SubComponentId = lines_tmp[10]
            try:
                c.execute(
                    "insert into itm_sit_enrich (SITNAME,SIT_DESC,THRESHOLD_FLAG,CUR_VALUE_FLAG,DISPLAY_FLAG,N_ComponentType,N_ComponentTypeId,N_Component,N_ComponentId,N_SubComponent,N_SubComponentId) "
                    "values (?,?,?,?,?,?,?,?,?,?,?)", (SITNAME,SIT_DESC,THRESHOLD_FLAG,CUR_VALUE_FLAG,DISPLAY_FLAG,N_ComponentType,N_ComponentTypeId,N_Component,N_ComponentId,N_SubComponent,N_SubComponentId));
                conn.commit()
                counter += 1
            except:
                    print("有问题的记录:%s" % SITNAME)
                    logger.error('有问题的记录:%s', SITNAME )
                    counter_err += 1

if __name__ == '__main__':
        main()

