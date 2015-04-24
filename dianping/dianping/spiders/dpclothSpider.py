# -*- coding: utf-8 -*-
import re
from scrapy import Selector

from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from dianping.items import ShopsItem


class DpshopsSpider(CrawlSpider):
    name = 'dpshops'
    allowed_domains = ['dianping.com']
    website = 'http://www.dianping.com'
    start_urls = [
        'http://www.dianping.com/search/category/17/0'
    ]
    id = 1

    rules = (
        Rule(LinkExtractor(allow=r'/17/0[p0-9]*'), callback='parse_shop_list', follow=True),
        Rule(LinkExtractor(allow=r'/shop/[0-9]+$'), callback='parse_shop', follow=True)
    )

    def parse_start_url(self, response):
        shop_list_pattern = re.compile("/category/17/0[p0-9]*")
        shop_urls = response.xpath("//@href").extract()
        for url in shop_urls:
            if shop_list_pattern.findall(url):
                yield Request(self.website + url.encode('utf8'), cookies={'cye': 'beijing'},
                              callback=self.parse_shop_list)

    def parse_shop_list(self, response):
        shop_urls = response.xpath('//*[@id="shop-all-list"]/ul/li/div[2]/div[1]/a[1]/@href').extract()
        for url in shop_urls:
            yield Request(self.website + url.encode("utf8"), cookies={'cye': 'xian'}, callback=self.parse_shop)

    def parse_shop(self, response):
        shop = ShopsItem()
        shop_url = response.url
        self.id += 1
        shop['id'] = [self.id]

        htmlData = Selector(response)

        shop['shop_dianping_url'] = [shop_url]
        shop['shop_city'] = response.xpath("//div[@class='breadcrumb']/a[1]/text()").extract()
        shop['shop_district'] = response.xpath("//div[@class='breadcrumb']/a[2]/text()").extract()
        shop['shop_region'] = response.xpath("//div[@class='breadcrumb']/a[3]/text()").extract()
        shop['shop_category'] = response.xpath("//div[@class='breadcrumb']/a[4]/text()").extract()

        shop_names = htmlData.xpath('//h1[@class="shop-name"]/text()').extract()
        street_addresses = htmlData.xpath('//span[@itemprop="street-address"]/text()').extract()
        shop_tels = htmlData.xpath('//p[@class="expand-info tel"]/span[text()="' + u"电话：" + '"]/..//text()[position()>1]').extract()
        open_times = htmlData.xpath(('//p[@class="info info-indent"]/span[text()="' + u"营业时间：" + '"]/..//text()[position()>1]')).extract()
        shop_tags = htmlData.xpath('//p[@class="info info-indent"]/span[text()="' + u"分类标签：" + '"]/..//text()[position()>1]').extract()
        scripts = htmlData.xpath('//script/text()').extract()

        shop['shop_name'] = str(shop_names[0].encode('utf8')).replace("\n",' ').strip("\"").strip() if len(shop_names)>0 else ''
        shop['street_address'] = str(street_addresses[0].encode('utf8')).replace("\n",' ').strip("\"").strip() if len(street_addresses)>0 else ''
        shop['shop_tel'] = str(shop_tels[0].encode('utf8')).replace("\n",' ').strip("\"").strip() if len(shop_tels)>0 else ''
        shop['open_time'] = str(open_times[0].encode('utf8')).replace("\n",' ').strip("\"").strip() if len(open_times)>0 else ''
        shop['shop_tag'] = str(shop_tags[0].encode('utf8')).replace("\n",' ').strip("\"").strip() if len(shop_tags)>0 else ''

        pat = re.compile('lng:[0-9.]+,lat:[0-9.]+')
        latAndLngList = [pat.findall(src)[0] for src in scripts if pat.findall(src)]
        latAndLng = latAndLngList[0] if len(latAndLngList) > 0 else ''
        latIdx = latAndLng.find('lat:')
        lat = latAndLng[latIdx + 4:]
        lng = latAndLng[4:latIdx - 1]
        shop['location'] = [lng, lat]
        if lat != '' and lng != '':
            yield shop