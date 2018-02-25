#!/usr/bin/python
# -*- coding: UTF-8 -*-

from xml.etree import ElementTree as et;
import json
import re
import sqlite3

tree = et.parse("src/SITUATION/NT/CCEB_OBOAS_CHECK_NSERVER_M.xml");
root = tree.getroot();
row =  root.getchildren();
print(row[0])