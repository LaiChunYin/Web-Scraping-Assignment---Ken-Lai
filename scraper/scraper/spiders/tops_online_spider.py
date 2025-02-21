import scrapy
from ..items import ProductItem

from scrapy_playwright.page import PageMethod

class TopsOnlineSpider(scrapy.Spider):
    name = "tops_online"
    allowed_domains = ["www.tops.co.th", "localhost"]
    start_urls = ["https://www.tops.co.th/en"]

    categories_to_be_scrapped = set([
        "OTOP",
        "Only At Tops",
        "Fruits & Vegetables",
        "Meat & Seafood",
        "Fresh Food & Bakery",
        "Pantry & Ingredients",
        "Snacks & Desserts",
        "Beverages",
        "Health & Beauty Care",
        "Mom & Kids",
        "Household & Merit",
        "PetNme",
    ])
    # used to keep track of how many items failed to be extracted in the pipeline
    failed_items = 0 

    # the scripts will keep scrolling to the bottom of the page until no more new products are loaded
    scrolling_infinite_list_script = """
        async () => {
            let currentItems = 0

            while (true) {
                window.scrollBy(0, document.body.scrollHeight)
                await new Promise(r => setTimeout(r, 3000)); // Wait for new content to load
                
                let newItems = document.querySelectorAll(".product-item a").length
        
                if (newItems === currentItems) {
                    break
                }
                currentItems = newItems
            }
        }
    """
    
    def start_requests(self):
        self.logger.debug("start running here")
        for url in self.start_urls:
            self.logger.debug(f"url {url}")

            yield scrapy.Request(url, callback=self.parse, meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", ".pc-sidenavbar a"),
                    PageMethod("wait_for_timeout", 1000)
                ],
            })


    def parse(self, response):
        '''
            Extract categories from the main page
        '''
        try:
            self.logger.debug("start parsing")
            category_selectors = response.css(".pc-sidenavbar a")
            self.logger.debug(f"parsing ${len(category_selectors)}")

            for selector in category_selectors:
                category = selector.css("span::text").get()
                self.logger.debug(f"cat is {category}")
                if category in self.categories_to_be_scrapped:
                    category_url = selector.attrib["href"]
                    self.logger.debug(f"cat url  {category_url}")

                    if not category_url.startswith('http'):
                        category_url = response.urljoin(category_url)
                    self.logger.debug(f"cat url after  {category_url}")

                    yield scrapy.Request(category_url, callback=self.parse_category, meta={
                        "extra_data": {
                            "category": category
                        }, 
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", ".plp-carousel__link"),
                        ],
                    })

        except Exception as e:
            self.logger.error(f'Unexpected error in parse: {e}')

    def parse_category(self, response):
        '''
            Extract subcategories from each category
        '''
        try:
            self.logger.debug("parsing category ")

            subcategory_selectors = response.css(".plp-carousel")

            self.logger.debug(f"sub cats are {len(subcategory_selectors)}")
            for selector in subcategory_selectors:
                subcategory = selector.css(".plp-carousel__title-name::text").get()
                view_all_url = selector.css(".plp-carousel__link").attrib["href"]
                self.logger.debug(f"subcat is {subcategory} {view_all_url}")

                if not view_all_url.startswith('http'):
                    view_all_url = response.urljoin(view_all_url)

                self.logger.debug(f"view all url is {view_all_url}")

                yield scrapy.Request(view_all_url, callback=self.parse_subcategory, meta={
                    "extra_data": {**response.meta["extra_data"], "subcategory": subcategory},
                    "playwright": True,
                    "playwright_page_methods": [
                        # wait for the items to be loaded first
                        PageMethod("wait_for_selector", ".product-item-image"),
                        # scroll to the bottom of the list to load more items
                        PageMethod("evaluate", self.scrolling_infinite_list_script),
                    ],
                })
        except Exception as e:
            self.logger.error(f'Unexpected error in parse_category: {e}')

    def parse_subcategory(self, response):
        '''
            Extract the url to the product details page of each product in the product list
        '''
        try:
            product_selectors = response.css(".product-item a")
                
            for selector in product_selectors:
                product_detail_url = selector.attrib["href"]
                self.logger.debug(f"detail url is {product_detail_url}")

                yield scrapy.Request(product_detail_url, callback=self.parse_details, meta={
                    "extra_data": {
                        **response.meta["extra_data"],
                        "url": product_detail_url,
                    },
                    "playwright": True,
                    "playwright_page_methods": [
                        # wait for the items to be loaded first
                        PageMethod("wait_for_selector", ".product-Details-page-root .add-to-cart"),
                    ],
                })
        except Exception as e:
            self.logger.error(f'Unexpected error in parse_subcategory: {e}')


    def parse_details(self, response):
        '''
            Extract product information from the product detail page
        '''
        try:
            product_item = ProductItem()

            product_item["product_name"] = response.css(".product-tile__name::text").get()
            product_item["product_images"] = [selector.attrib["src"] for selector in response.css(".product-Details-images img")]
            # product_item["quantity"] = response.css("").get()
            product_item["bar_code_number"] = response.css(".product-Details-sku::text").get()
            product_item["product_details"] = response.css('.accordion-property').xpath('.//text()').getall()
            product_item["price"] = response.css(".product-Details-current-price::text").get()
            product_item["labels"] = response.css(".product-Details-seasonal-label::text, .central_container .main-content-wrapper .promo-name").xpath('.//text()').getall()
            product_item["url"] = response.meta["extra_data"]["url"]
            product_item["category"] = response.meta["extra_data"]["category"]
            product_item["subcategory"] = response.meta["extra_data"]["subcategory"]
        
            yield product_item
        except Exception as e:
            self.logger.error(f'Unexpected error in parse_details: {e}')