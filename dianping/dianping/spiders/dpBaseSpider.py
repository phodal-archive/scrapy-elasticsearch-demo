#!/usr/local/bin/python
# -*-coding:utf8-*-
__author__ = 'youjiezeng'
import sys

from scrapy.spider import Spider
from scrapy.http import Request

sys.path.append('../items')
reload(sys)
try:
    from dianping.items import DianpingItem
except Exception, e:
    print e
import re
from scrapy.exceptions import CloseSpider
from scrapy.selector import Selector

'''
this is a way to run spider in cmdline
scrapy runspider my_spider.py

优化点：
1. 启动爬虫间隔
2. 启动cookie，防止被ban
3. 随机切换user-agent，防止被ban
4. 将编码任务切换到pipeline中
'''


class DpSpider(Spider):
    name = 'dianping'
    allowed_domains = ['dianping.com']
    start_urls = ['http://www.dianping.com/search/category/2/20/g120r1481']
    # rules = [Rule(LxmlParserLinkExtractor(['shop/\d+']), 'parse')]
    # rules = [Rule(SgmlLinkExtractor(allow=('/shop'),restrict_xpaths=('//@href')), callback='parse',follow=True)]

    def parse(self, response):

        shop = DianpingItem()
        status_code = response.status
        if status_code == 403:  #当爬虫被禁时，关闭爬虫
            raise CloseSpider('========   SPIDER WAS FORBIDDEN  =========')

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
        shop_tels = htmlData.xpath('//span[@class="info-name" and text()="' + u"电话：" + '"]/../text()[2]').extract()
        open_times = htmlData.xpath(
            '//p[@class="info info-indent"]/span[text()="' + u"营业时间：" + '"]/../span[2]/text()').extract()
        shop_tags = htmlData.xpath('//span[@class=item]/a[@rel="tag"]/text()').extract()
        scripts = htmlData.xpath('//script/text()').extract()
        urls = htmlData.xpath('//attribute::href').extract()

        #爬取的数据中，有大量的换行符以及“号，在这里清洗掉
        shop['shop_name'] = str(shop_names[0].encode('utf8')).replace("\n", ' ').strip("\"").strip() if len(
            shop_names) > 0 else ''
        shop['street_address'] = str(street_addresses[0].encode('utf8')).replace("\n", ' ').strip("\"").strip() if len(
            street_addresses) > 0 else ''
        shop['shop_tel'] = str(shop_tels[0].encode('utf8')).replace("\n", ' ').strip("\"").strip() if len(
            shop_tels) > 0 else ''
        shop['open_time'] = str(open_times[0].encode('utf8')).replace("\n", ' ').strip("\"").strip() if len(
            open_times) > 0 else ''
        shop['shop_tag'] = str(shop_tags[0].encode('utf8')).replace("\n", ' ').strip("\"").strip() if len(
            shop_tags) > 0 else ''

        pat = re.compile('lng:[0-9.]+,lat:[0-9.]+')
        latAndLngList = [pat.findall(src)[0] for src in scripts if pat.findall(src)]
        latAndLng = latAndLngList[0] if len(latAndLngList) > 0 else ''
        latIdx = latAndLng.find('lat:')
        lat = latAndLng[latIdx + 4:]
        lng = latAndLng[4:latIdx - 1]
        shop['shop_lat'] = lat
        shop['shop_lng'] = lng
        if lat != '' and lng != '':
            yield shop

        currentUrl = response.url
        domainUrl = 'http://www.dianping.com'
        # urls = htmlData.select('//@href').extract()
        urlPattern = re.compile('shop/[0-9]+')

        for url in urls:
            if not urlPattern.findall(url):
                continue
            if str(url.encode('utf8')).startswith('http'):
                pass
            elif str(url.encode('utf8')).startswith('/'):
                url = domainUrl + url
            else:
                url = currentUrl + url
            print '------------url:', url
            yield Request(url, callback=self.parse)

