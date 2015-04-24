#!/usr/local/bin/python
# -*-coding:utf8-*-
import re

from scrapy.exceptions import CloseSpider
from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request


__author__ = 'youjiezeng'
__createDate__ = '1/17/15'

import sys
sys.path.append('../items')
reload(sys)
try:
    from dianping.items import DianpingItem
except Exception,e:
    print e


'''
# To authenticate the proxy, you must set the Proxy-Authorization header.  You *cannot* use the form http://user:pass@proxy:port in request.meta['proxy']
import base64

proxy_ip_port = "123.456.789.10:8888"
proxy_user_pass = "awesome:dude"

request = Request(url, callback=self.parse)

# Set the location of the proxy
request.meta['proxy'] = "http://%s" % proxy_ip_port

# setup basic authentication for the proxy
encoded_user_pass=base64.encodestring(proxy_user_pass)
request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass


------------------------------------------------------------------------
# Redirect Scrapy log messages to standard Python logger

## Add the following lines to your Scrapy project's settings.py file
## This will redirect *all* Scrapy logs to your standard Python logging facility

from twisted.python import log
observer = log.PythonLoggingObserver()
observer.start()
'''

class dpCrawlSpider(CrawlSpider):
    name = 'dianpingCrawl'
    allowed_domains = ['dianping.com']
    start_urls = ['http://www.dianping.com/search/category/2/20/g120r1481']

    #Each Rule defines a certain behaviour for crawling the site
    # rules = [Rule(LxmlParserLinkExtractor(('category','/shop/')), callback=parse_start_url,follow=True,process_links=,process_request='print_request')]
    # rules = [Rule(SgmlLinkExtractor(allow=('dianping'),restrict_xpaths=('//@href')), callback='parse_start_url',follow=True)]
    def parse_start_url(self, response):
        shop = DianpingItem()
        status_code = response.status
        #handle_httpstatus_list=[403]
        if status_code == 403: #当爬虫被禁时，关闭爬虫
            raise CloseSpider('=====================  SPIDER FORBIDDEN  =====================')
            return
        elif status_code>200:
            return

        # htmlData = HtmlXPathSelector(response)
        # shop_names = htmlData.select('//h1[@class="shop-name"]/text()').extract()
        # street_addresses = htmlData.select('//span[@itemprop="street-address"]/text()').extract()
        # shop_tels = htmlData.select('//span[@class="info-name" and text()="'+u"电话："+'"]/../text()[2]').extract()
        # open_times = htmlData.select('//p[@class="info info-indent"]/span[text()="'+u"营业时间："+'"]/../span[2]/text()').extract()
        # shop_tags = htmlData.select('//span[@class=item]/a[@rel="tag"]/text()').extract()
        # scripts = htmlData.select('//script/text()').extract()
        # urls = htmlData.select('//attribute::href').extract()

        htmlData = Selector(response)

        shop_names = htmlData.xpath('//h1[@class="shop-name"]/text()').extract()
        street_addresses = htmlData.xpath('//span[@itemprop="street-address"]/text()').extract()
        shop_tels = htmlData.xpath('//span[@class="info-name" and text()="'+u"电话："+'"]/../text()[2]').extract()
        open_times = htmlData.xpath('//p[@class="info info-indent"]/span[text()="'+u"营业时间："+'"]/../span[2]/text()').extract()
        shop_tags = htmlData.xpath('//span[@class=item]/a[@rel="tag"]/text()').extract()
        scripts = htmlData.xpath('//script/text()').extract()
        urls = htmlData.xpath('//attribute::href').extract()

        shop['shop_name'] = str(shop_names[0].encode('utf8')).replace("\n",' ').strip("\"").strip() if len(shop_names)>0 else ''
        shop['street_address'] = str(street_addresses[0].encode('utf8')).replace("\n",' ').strip("\"").strip() if len(street_addresses)>0 else ''
        shop['shop_tel'] = str(shop_tels[0].encode('utf8')).replace("\n",' ').strip("\"").strip() if len(shop_tels)>0 else ''
        shop['open_time'] = str(open_times[0].encode('utf8')).replace("\n",' ').strip("\"").strip() if len(open_times)>0 else ''
        shop['shop_tag'] = str(shop_tags[0].encode('utf8')).replace("\n",' ').strip("\"").strip() if len(shop_tags)>0 else ''


        pat = re.compile('lng:[0-9.]+,lat:[0-9.]+')
        latAndLngList = [pat.findall(src)[0] for src in scripts if pat.findall(src)]
        latAndLng = latAndLngList[0] if len(latAndLngList)>0 else ''
        latIdx = latAndLng.find('lat:')
        lat = latAndLng[latIdx+4:]
        lng = latAndLng[4:latIdx-1]
        shop['shop_lat'] = lat
        shop['shop_lng'] = lng
        if lat != '' and lng != '':
            yield shop
        curUrl = response.url
        rootUrl = 'http://www.dianping.com'
        urlPattern = re.compile("category|shop")
        for url in urls:
            if not urlPattern.findall(url):
                continue
            if str(url.encode('utf8')).startswith('http:'):
                url = url.encode('utf8')
            elif str(url.encode('utf8')).startswith('/'):
                url = rootUrl + str(url.encode('utf8'))
            else:
                continue
            yield Request(url,callback=self.parse_start_url)
