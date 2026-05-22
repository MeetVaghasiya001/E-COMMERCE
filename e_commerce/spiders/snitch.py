import scrapy
import json
from ..items import SnitchItem

class ProductSpider(scrapy.Spider):
    name = "snitch"
    allowed_domains = ["snitch.com"]
    start_urls = ["https://www.snitch.com/men-shirts/100-viscose-box-fit-graphic-shirt-4shs148-01/9214319984802/buy"]

    def parse(self, response):
        scripts = response.xpath('//script[@type="application/ld+json"]/text()').getall()

        for script in scripts:
            try:
                data = json.loads(script)
            except:
                continue

            if isinstance(data, list):
                for d in data:
                    if d.get("@type") == "Product":
                        yield self.build_item(d)
            else:
                if data.get("@type") == "Product":
                    yield self.build_item(data)


    def build_item(self, json_data):
        item = SnitchItem()

        offers = json_data.get("offers", {})
        rating = json_data.get("aggregateRating", {})

        item["productID"] = json_data.get("productID")
        item["name"] = json_data.get("name")
        item["description"] = json_data.get("description")
        item["sku"] = json_data.get("sku")
        item["size"] = json_data.get("size")
        item["color"] = json_data.get("color")
        item["price"] = offers.get("price")
        item["highPrice"] = offers.get("highPrice")
        item["rating"] = rating.get("ratingValue")
        item["image"] = json_data.get("image")

        return item
            
        
