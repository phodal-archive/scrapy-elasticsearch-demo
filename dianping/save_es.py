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
    data["shop_tel"] = data["shop_tel"].split(",")
    data["location"] = [data["shop_lng"], data["shop_lat"]]
    data["shop_tags"] = re.sub("\(\d+\)", "", data["shop_tags"])
    data["shop_tags"] = data["shop_tags"].encode("utf8").replace("分类标签：,", "").split(",")
    data.pop('shop_lng')
    data.pop('shop_lat')
    index += 1
    es.index('dianping', 'food', data, id=index)