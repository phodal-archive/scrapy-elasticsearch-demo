import codecs
import json
from pyelasticsearch import ElasticSearch

es = ElasticSearch('http://localhost:9200/')

file = codecs.open('shop_data.json', mode='r', encoding='utf-8')

index = 0

for line in file.readlines():
    data = json.loads(line)
    data["location"] = [data["shop_lng"], data["shop_lat"]]
    index += 1
    es.index('dianping', 'food', data, id=index)