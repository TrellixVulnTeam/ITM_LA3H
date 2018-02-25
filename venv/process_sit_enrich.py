#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import sqlite3

#文件示例： NT_TCP_STATUS_HT&&Primary:BL685762:NT Primary:BL685765:NT Primary:HP-BL685-019:NT Primary:HP-BL685-054:NT
DB_FILE = "ump_std.db"
filename = 'src/ITM_Situation.lookup'
lines_tmp = []

def main():
    clean_db()
    process_sit_enrich()

def clean_db():
    conn = sqlite3.connect(DB_FILE);
    c = conn.cursor();
    c.execute("delete from itm_sit_enrich");
    conn.commit();
    print("table itm_sit_enrich has been cleaned!");

def process_sit_enrich():
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
            except:
                    print("error:",SITNAME)

if __name__ == '__main__':
        main()

