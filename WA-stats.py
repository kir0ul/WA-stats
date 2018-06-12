#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ===== Initialisation =====
import pandas as pd
import re
from dateutil.parser import parse

# TXT_FILE = "WhatsApp Chat with Brunoy foot  Club.txt"
TXT_FILE = "test.txt"
HEADER = 0

# ===== File parsing =====
with open(TXT_FILE, "r") as f:
    raw_data = f.readlines()

INIT_LINE_REG = re.compile(r"^\d{1,2}\/\d{1,2}\/\d{2}, \d{2}:\d{2} - ")
DATE_REG = re.compile(r"^\d{1,2}\/\d{1,2}\/\d{2},")
TIME_REG = re.compile(r", \d{2}:\d{2} - ")
NAME_MSG_REG = re.compile(r"-.*?: ")

data = pd.DataFrame(columns=["date", "time", "name", "message"])
datetime = []
name = []
msg = []
for i, l in enumerate(raw_data[HEADER:-1]):
    if INIT_LINE_REG.match(l) == None:
        msg[-1] += l
        continue
    date = DATE_REG.findall(l)[0][0:-1]
    time = TIME_REG.findall(l)[0][2:-3]
    datetime.append(parse(date + " " + time))
    if len(NAME_MSG_REG.findall(l)) > 0:
        name.append(NAME_MSG_REG.findall(l)[0][2:-2])
        msg.append(NAME_MSG_REG.split(l)[1])
    else:
        name.append(None)
        msg.append(INIT_LINE_REG.split(l)[1])
data = pd.DataFrame({"datetime": datetime, "name": name, "message": msg}, index=datetime)

print(data.tail())


# ===== Compute some stats =====
name_set = set(data["name"])
name_set.remove(None)
