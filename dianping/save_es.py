#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import codecs
import json
import re
from pyelasticsearch import ElasticSearch

es = ElasticSearch('http://localhost:9200/')

file = codecs.open('shop_data.json', mode='r', encoding='utf-8')

index = 0

for line in file.readlines():
    data = json.loads(line)
    data.pop("id")
    data["shop_tel"] = re.sub(" +", ",", data["shop_tel"])
    data["shop_tel"] = data["shop_tel"].encode("utf8").replace("电话：", "").split(",")[1:]

    data["location"] = re.sub(" +", ",", data["location"]).split(",")
    data["location"] = data["location"][1] + "," + data["location"][0]

    data["shop_tags"] = re.sub("\(\d+\)", "", data["shop_tags"])
    data["shop_tags"] = re.sub(" +", ",", data["shop_tags"])
    data["shop_tags"] = data["shop_tags"].encode("utf8").replace("分类标签：,", "").split(",")[:-1]

    data["open_time"] = re.sub(" +", "", data["open_time"])
    data["open_time"] = data["open_time"].encode("utf8").replace("营业时间：", "").replace("添加", "").replace("修改", "").replace("：",":")
    index += 1
    es.index('dianping', 'food', data, id=index)