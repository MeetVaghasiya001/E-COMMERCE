# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BearItem(scrapy.Item):
    store = scrapy.Field()
    url = scrapy.Field()
    product_title = scrapy.Field()
    product_id = scrapy.Field()
    tages = scrapy.Field()
    vendor = scrapy.Field()
    min_price = scrapy.Field()
    max_price = scrapy.Field()
    images = scrapy.Field()
    varients = scrapy.Field()
    rating = scrapy.Field()
    review_count = scrapy.Field()
    meta_info = scrapy.Field()



class SnitchItem(scrapy.Item):
    productID = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    sku = scrapy.Field()
    size = scrapy.Field()
    color = scrapy.Field()
    price = scrapy.Field()
    highPrice = scrapy.Field()
    rating = scrapy.Field()
    image = scrapy.Field()



class SouldStoreItem(scrapy.Item):
    product_id = scrapy.Field()
    name = scrapy.Field()
    category = scrapy.Field()
    color = scrapy.Field()
    description = scrapy.Field()
    product_details = scrapy.Field()
    artist_details = scrapy.Field()
    images = scrapy.Field()
    price = scrapy.Field()
    variants = scrapy.Field()
    