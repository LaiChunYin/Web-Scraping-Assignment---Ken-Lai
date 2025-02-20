# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import re
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScraperPipeline:
    def split_name_quantity(self, name):
        # Regular expression to find volume patterns such as numbers followed by ml, L, g, etc.
        # Adjust the pattern to capture more cases as needed
        pattern = re.compile(r'\s+((\d+\.?\d*\s*(ml|L|g|kg|oz|pcs|lb|cc|oz|gal|m|cm))\.?)', re.IGNORECASE)
        
        match = pattern.search(name)
        if match:
            # possibly with a trailing dot
            volume = match.group(1)
            name = " ".join(name.split(volume))

            # without a trailing dot
            volume = match.group(2)
            return name, volume
        else:
            return name, None
        
    def extract_bar_code(self, sku):
        pattern = re.compile(r'\s?(\d+)', re.IGNORECASE)
        match = pattern.search(sku)
        return match.group(0).strip() if match else ""
    
    def convert_price_to_float(self, price):
        price = re.sub(r'[^\d\.]', '', price)
        return float(price)


    def process_item(self, item, spider):
        try:
            adapter = ItemAdapter(item)

            field_names = adapter.field_names()
            for field in field_names:
                spider.logger.debug(f"field is {field}")

                if 'product_name' == field:
                    spider.logger.debug(f"name and vol {adapter[field]}")
                    name, quantity = self.split_name_quantity(adapter[field])
                    spider.logger.debug(f"name and vol after {name}, {quantity}")
                    adapter["product_name"] = name.strip()
                    adapter["quantity"] = quantity

                if 'product_details' == field:
                    adapter[field] = "".join(adapter[field]).strip()
                
                if 'price' == field:
                    adapter[field] = self.convert_price_to_float(adapter[field])

                if 'bar_code_number' == field:
                    adapter[field] = self.extract_bar_code(adapter[field])
        except Exception as e:
            spider.logger.error(f"Error processing item {item}: {e}")
            spider.failed_items += 1

        return item
    
    def close_spider(self, spider):
        spider.logger.info(f"Pipeline closed for spider: {spider.name}")
        spider.logger.info(f"Pipeline failed to process: {spider.failed_items} items")
