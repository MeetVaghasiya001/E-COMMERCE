import scrapy
import json
from parsel import Selector
from e_commerce.items import BearItem


class BearHouseSpider(scrapy.Spider):
    name = "bear_house"
    allowed_domains = ["thebearhouse.com"]
    
    def start_requests(self):
        url = 'https://thebearhouse.com/collections/tshirts/products/preview-bk'
        payload = url.split('/')[-1]

        query = f"""
            query productDetails($variantsCursor: String) @inContext(country: IN, language: EN) {{
            product(handle: {payload}) {{
                id
                handle
                title
                vendor
                availableForSale
                onlineStoreUrl
                tags
                publishedAt

                priceRange {{
                    maxVariantPrice {{ amount }}
                    minVariantPrice {{ amount }}
                }}

                featuredImage {{ id url }}

                options {{
                    id
                    name
                    values
                    optionValues {{ id name }}
                }}

                images(first: 250) {{
                    nodes {{ id url altText }}
                }}

                variants(first: 250, after: $variantsCursor) {{
                    nodes {{
                        id
                        availableForSale

                        compareAtPrice {{
                            currencyCode
                            amount
                        }}

                        selectedOptions {{
                            name
                            value
                        }}

                        currentlyNotInStock

                        featured_image: image {{
                            id
                            src: url
                            altText
                        }}

                        price {{
                            currencyCode
                            amount
                        }}

                        title
                        sku
                    }}

                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}

                compareAtPriceRange {{
                    maxVariantPrice {{ amount }}
                    minVariantPrice {{ amount }}
                }}
            }}
            }}
        """

        json_data = {
            "query": query,
            "variables": {}
        }

        api = 'https://thebearhouse.com/api/2025-10/graphql.json'

        yield scrapy.Request(
            url=api,
            method="POST",
            body=json.dumps(json_data),
            callback=self.parse_product
        )


    def parse_product(self,response):
        data=response.json()
        with open('responce.json','w',encoding='utf-8') as f:
            json.dump(data,f,indent=4,default=str)
        
        product=(data.get("data") or {}).get("product") or {}
        
        url=product.get("onlineStoreUrl")
        product_title=product.get("title")
        product_id=(product.get("id") or "").split("/")[-1]
        tages=product.get("tags") or []
        vendor=product.get("vendor")
        price_range=product.get("priceRange") or {}
        min_price=float(((price_range.get("minVariantPrice") or {}).get("amount") or 0))
        max_price=float(((price_range.get("maxVariantPrice") or {}).get("amount") or 0))

        images=[i.get("url") for i in (product.get("images") or {}).get("nodes",[]) if i.get("url")]

        varients=[]
        for v in (product.get("variants") or {}).get("nodes",[]):
            selected="".join(str(o.get("value") or "") for o in (v.get("selectedOptions") or []))
            compare=v.get("compareAtPrice") or {}
            varients.append({
                "avalible_for_sale":v.get("availableForSale"),
                "price":float(compare.get("amount") or 0),
                "selected_option":selected,
                "out_of_stock":v.get("currentlyNotInStock"),
                "sku":v.get("sku")
            })

        temp_data={
            "url":url,
            "product_title":product_title,
            "product_id":product_id,
            "tages":tages,
            "vendor":vendor,
            "min_price":min_price,
            "max_price":max_price,
            "images":images,
            "varients":varients
        }

        if not url:
            return

        yield scrapy.Request(
            url=url,
            headers={
                "User-Agent":"Mozilla/5.0",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer":url
            },
            callback=self.full_parser,
            cb_kwargs=temp_data
        )
    
    def full_parser(self, response, **temp_data):
        selector = Selector(response.text)
        with open('data.html','w',encoding='utf-8') as f:
            f.write(response.text)
        main_div = selector.xpath("//div[contains(@class,'product-block--tab')]")
        meta_information = {}
        rating = float(selector.xpath("//div[@data-average-rating]/@data-average-rating").get())
        review_count = float(selector.xpath("//div[@data-number-of-reviews]/@data-number-of-reviews").get())
        
        for i in main_div:
            k = i.xpath(".//button[contains(@class,'collapsible--auto-height')]/text()").get()

            if not k:
                continue
            k = k.replace(":", "").strip()
            if k == 'Description':
                v = {}
                for j in i.xpath(".//div[contains(@class,'collapsible-content__inner')]//p"):
                    key = j.xpath(".//strong//text()").get()
                    if not key:
                        continue
                    key = key.replace(":", "").strip()
                    all_text = j.xpath(".//text()").getall()
                    all_text = [t.strip() for t in all_text if t.strip()]

                    val = " ".join(all_text)
                    val = val.replace(key, "", 1).replace(":", "").strip()
                    v[key] = val

                meta_information[k] = v
            elif k == 'Shipping information':
                v = [
                    " ".join(j.xpath(".//text()").getall()).strip()
                    for j in i.xpath(".//div[contains(@class,'collapsible-content__inner')]//p")
                    if j.xpath(".//text()").get()
                ]
                meta_information[k] = v

            elif k == 'Manufactured & Marketed by':
                v = [
                    " ".join(j.xpath(".//text()").getall()).strip()
                    for j in i.xpath(".//div[contains(@class,'collapsible-content__inner')]//p")
                    if j.xpath(".//text()").get()
                ]
                meta_information[k] = v

        temp_data['meta_info'] = meta_information
        temp_data['rating'] = rating
        temp_data['review_count'] = review_count
        with open('clean.json','w',encoding='utf-8') as f:
            json.dump(temp_data,f,indent=4,default=str)
        item = BearItem()

        item['store'] = 'bear_house'
        item['url'] = temp_data.get('url')
        item['product_title'] = temp_data.get('product_title')
        item['product_id'] = temp_data.get('product_id')
        item['tages'] = temp_data.get('tages')
        item['vendor'] = temp_data.get('vendor')
        item['min_price'] = temp_data.get('min_price')
        item['max_price'] = temp_data.get('max_price')
        item['images'] = temp_data.get('images')
        item['varients'] = temp_data.get('varients')
        item['rating'] = temp_data['rating']
        item['review_count'] = temp_data['review_count']
        item['meta_info'] = temp_data.get('meta_info')

        yield item