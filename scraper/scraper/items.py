# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    product_name = scrapy.Field()
    product_images = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    quantity = scrapy.Field()
    bar_code_number = scrapy.Field()
    product_details = scrapy.Field()
    price = scrapy.Field()
    labels = scrapy.Field()
    url = scrapy.Field()
