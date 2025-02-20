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
        pattern = re.compile(r'\s+((\d+\.?\d*\s*(ml|L|g|kg|oz|pcs))\.?)', re.IGNORECASE)
        
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

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        field_names = adapter.field_names()
        for field in field_names:
            print("field is ", field)

            if 'product_name' in adapter:
                print("name and vol ", name)
                name, quantity = self.split_name_quantity(adapter[field])
                print("name and vol after ", name, quantity)
                adapter["product_name"] = name
                adapter["quantity"] = quantity

            if 'product_details' in adapter:
                adapter[field] = adapter[field].strip()
            
            if 'price' in adapter:
                adapter[field] = float(adapter[field])

        return item
