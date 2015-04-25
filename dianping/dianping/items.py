from scrapy.item import Item, Field

class ShopsItem(Item):
    shop_name = Field()
    street_address = Field()
    shop_tags = Field()
    shop_dianping_url = Field()
    shop_city = Field()
    shop_district = Field()
    shop_region = Field()
    shop_category = Field()
    shop_tel = Field()
    open_time = Field()
    shop_tag = Field()
    location = Field()
