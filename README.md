# Dianping.com web spider & Save to ElasticSearch


#Setup


##Install
 
1.ElasticSearch

    brew install elasticsearch

2.Python libs

    pip install -r requirements.txt
    
##Run
    
1.Run spider
    
    cd dianping
    scrapy crawl food

``food`` -> dianping/spiders/foodSpider.py -> name='food'
     
2.Save to ElasticSearch
      
    python save_es.py  