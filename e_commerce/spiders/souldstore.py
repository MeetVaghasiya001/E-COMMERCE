import scrapy
import json
from parsel import Selector
from e_commerce.items import SouldStoreItem


class SouldstoreSpider(scrapy.Spider):

    name = "souldstore"
    allowed_domains = ["thesouledstore.com"]

    def start_requests(self):
        url = "https://www.thesouledstore.com/product/statement-shirt-aqua-women?gte=1"

        main_url = url.split("/product/")[-1]
        main_url = main_url.split("?gte=")[0]

        print("MAIN URL =", main_url)

        product_api = f"https://api.thesouledstore.com/api/v2/static/product/{main_url}"

        price_api = f"https://api.thesouledstore.com/api/v2/product/{main_url}/pricing"

        inventory_api = f"https://api.thesouledstore.com/api/v2/product/{main_url}/inventory"

        yield scrapy.Request(
            url=product_api,
            callback=self.parse_product,
            meta={
                "price_api": price_api,
                "inventory_api": inventory_api
            }
        )

    def parse_product(self, response):

        base_url = "https://prod-img.thesouledstore.com/public/theSoul/uploads/catalog/product/"

        data = json.loads(response.text)

        product_id = data.get("id")
        name = data.get("product")
        category = data.get("category")
        description = data.get("short_desc")

        color_data = data.get("colors", [])
        # colors=[]
        for c in color_data:
            color_name = c.get("colorName")
            if color_name:
                color_name = color_name
            else:
                color_name = c.get("color_name")
            # colors.append(color_name)

        product_details = data.get("add_desc", "")
        selector = Selector(text=product_details)
        details_text = selector.xpath("//text()").getall()
        details_text = " ".join(details_text).strip()

        artist_details = data.get("user_description", "")
        artist_selector = Selector(text=artist_details)
        artist_text = artist_selector.xpath("//text()").getall()
        artist_text = " ".join(artist_text).strip()
        images = data.get("images", [])

        full_images = []

        for img in images:
            full_url = base_url + img
            full_images.append(full_url)

        item = SouldStoreItem()
        item["product_id"] = product_id
        item["name"] = name
        item["category"] = category
        item["color"] = color_name
        item["description"] = description
        item["product_details"] = details_text
        item["artist_details"] = artist_text
        item["images"] = full_images

        yield scrapy.Request(
            url=response.meta["price_api"],
            callback=self.parse_price,
            meta={
                "product_data": item,
                "inventory_api": response.meta["inventory_api"]
            }
        )

    def parse_price(self, response):

        data = json.loads(response.text)
        price = data.get("price")
        item = response.meta["product_data"]
        item["price"] = price

        yield scrapy.Request(
            url=response.meta["inventory_api"],
            callback=self.parse_inventory,
            headers=None,
            meta={
                "product_data": item
            }
        )

    def parse_inventory(self, response):

        data = json.loads(response.text)
        variants = []
        variant_data = data.get("variant", [])

        for v in variant_data:

            stock = {
                "size": v.get("name"),
                "stock": v.get("stock")
            }

            variants.append(stock)

        item = response.meta["product_data"]
        item["variants"] = variants

        yield item