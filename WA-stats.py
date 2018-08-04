#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ===== Initialisation =====
import pandas as pd
import re
from dateutil.parser import parse
import os
import sys
import numpy as np

TXT_FILE = ""
for root, dirs, files in os.walk(os.getcwd()):
    for f in files:
        if "whatsapp" in f.lower():
            TXT_FILE = f
            break
    break
if TXT_FILE == "":
    print("No WhatsApp file found, exiting...")
    sys.exit()
else:
    print("Using file: {0}".format(TXT_FILE))
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

# Number of messages by name
name_set = list(set(data["name"]))
name_set.remove(None)
msg_count = data.groupby("name").size()
print("\nmsg_count:\n{}".format(msg_count))

# Cumulated number of messages by name
msg_cum_count = {}
for name in name_set:
    data_name = data[data.name == name]
    msg_cum_count[name] = {}
    msg_cum_count[name]["t"] = data_name.datetime
    msg_cum_count[name]["y"] = np.ones(len(data_name))
    msg_cum_count[name]["y"] = np.cumsum(msg_cum_count[name]["y"])

# Histogram of messages by hour
hours = data.index.floor('1H').map(lambda x: x.time().hour)
bins = range(0, 24)
cats = pd.cut(hours, bins)
histo = pd.value_counts(cats).sort_index()

# Words frequencies
all_words = []
for item in data['message']:
    all_words.extend(item.split(' '))
all_words = pd.DataFrame(all_words)  # To be able to count easily
words_set = pd.DataFrame(list(set(all_words[0])), columns=["words"])
words_set["count"] = 0
for word in words_set["words"]:
    count = all_words[all_words[0] == word].size
    words_set.loc[words_set[words_set.words == word].index, "count"] = count
print("\nWord frequencies:\n{}".format(words_set.sort(columns="count", ascending=False).head()))
