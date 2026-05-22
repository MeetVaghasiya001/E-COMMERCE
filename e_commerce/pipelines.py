# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector
from e_commerce.items import BearItem,SnitchItem,SouldStoreItem
import json
class ECommercePipeline:

    def open_spider(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Actowiz",
            database="E-commerce"
        )

        self.cur = self.conn.cursor()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS bear_product(
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_title varchar(255),
                product_url varchar(500),
                product_id varchar(50),
                vendor varchar(255),
                min_price decimal(10,2),
                max_price decimal(10,2),
                tags json,
                images json,
                variants json,
                rating FLOAT,
                review_count FLOAT,
                meta_info json       
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS snitch_product (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id BIGINT,
                name VARCHAR(255),
                description TEXT,
                sku VARCHAR(255),
                size VARCHAR(255),
                color VARCHAR(255),
                price DECIMAL(10,2),
                high_price DECIMAL(10,2),
                rating FLOAT,
                images JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS sould_store_product (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id VARCHAR(255),
                name TEXT,
                category VARCHAR(255),
                color VARCHAR(255),
                description LONGTEXT,
                product_details LONGTEXT,
                artist_details LONGTEXT,
                price FLOAT,
                images JSON,
                variants JSON
            )
        """)

        self.conn.commit()

        self.bear_products = []
        self.snitch_products = []
        self.sould_store_products = []

    def insert_bear_product_data(self,data):
        query = "INSERT INTO bear_product (product_title, product_url, product_id, vendor, min_price, max_price, tags, images, variants,rating,review_count, meta_info) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.cur.executemany(query,data)
        self.conn.commit()

    def insert_snitch_product_data(self,data):
        query = """INSERT INTO snitch_product (
            product_id,
            name,
            description,
            sku,
            size,
            color,
            price,
            high_price,
            rating,
            images
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

        self.cur.executemany(query,data)
        self.conn.commit()

    def insert_sould_store_products(self,data):
        query = "INSERT INTO sould_store_product (product_id,name,category,color,description,product_details,artist_details,price,images,variants) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.cur.executemany(query,data)
        self.conn.commit()

    def process_item(self, item, spider):
        if isinstance(item,BearItem):
            self.bear_products.append((
                item['product_title'],
                item['url'],
                item['product_id'],
                item['vendor'],
                item['min_price'],
                item['max_price'],
                json.dumps(item['images']),
                json.dumps(item['tages']),
                json.dumps(item['varients']),
                item['rating'],
                item['review_count'],
                json.dumps(item['meta_info']),
            ))

            if len(self.bear_products) >= 100:
                self.insert_bear_product_data(self.bear_products)
                self.bear_products.clear()

        elif isinstance(item,SnitchItem):
            self.snitch_products.append((
                item['productID'],
                item['name'],
                item['description'],
                item['sku'],
                item['size'],
                item['color'],
                item['price'],
                item['highPrice'],
                item['rating'],
                json.dumps(item['image'])
            ))

            if len(self.snitch_products) >= 100:
                self.insert_snitch_product_data(self.snitch_products)
                self.snitch_products.clear()

        elif isinstance(item,SouldStoreItem):
            self.sould_store_products.append((
                item['product_id'],
                item['name'],
                item['category'],
                item['color'],
                item['description'],
                item['product_details'],
                item['artist_details'],
                item['price'],
                json.dumps(item['images']),
                json.dumps(item['variants'])
            ))

            if len(self.sould_store_products) >= 100:
                self.insert_sould_store_products(self.sould_store_products)
                self.sould_store_products.clear()

    def close_spider(self,spider):

        if self.bear_products:
            self.insert_bear_product_data(self.bear_products)
        if self.snitch_products:
            self.insert_snitch_product_data(self.snitch_products)
        if self.sould_store_products:
            self.insert_sould_store_products(self.sould_store_products)
        self.cur.close()
        self.conn.close()



