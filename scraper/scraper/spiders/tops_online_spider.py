import scrapy
from scrapy_splash import SplashRequest
from scrapy_selenium import SeleniumRequest
from ..items import ProductItem

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy_playwright.page import PageMethod

class TopsOnlineSpider(scrapy.Spider):
    name = "tops_online"
    allowed_domains = ["www.tops.co.th", "localhost"]
    start_urls = ["https://www.tops.co.th/en"]

    categories_to_be_scrapped = set([
        # "OTOP",
        # "Only At Tops",
        # "Fruits & Vegetables",
        # "Meat & Seafood",
        # "Fresh Food & Bakery",
        "Pantry & Ingredients",
        # "Snacks & Desserts",
        # "Beverages",
        # "Health & Beauty Care",
        # "Mom & Kids",
        # "Household & Merit",
        # "PetNme",
    ])
    # used to keep track of how many items failed to be extracted in the pipeline
    failed_items = 0 

    def generate_script_to_wait_for(self, element):
        return f"""
            function main(splash)
                assert(splash:go(splash.args.url))
                assert(splash:wait(1))

                local function check_element()
                    local element = splash:select('{element}')
                    if element then
                        return splash:html()
                    else
                        splash:wait(0.5)
                        return check_element()
                    end
                end

                return check_element()
            end
        """

    scroll_down_product_infinite_list_script = """
        function main(splash, args)
        splash:go(args.url)
        local scroll = splash:jsfunc([[
            function scrollWithDelay() {
                for (let i = 0; i < 5; i++) {
                    setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * 2000);
                }
            }
        ]])

        scroll()

        local function check_element()
        local element = splash:select('.product-item .mt-product-item a')
        if element then
            return splash:html()
        else
            splash:wait(0.5)
            return check_element()
        end

        return check_element()

        end
    """

    # the scripts will keep scrolling to the bottom of the page until no more new products are loaded
    scrolling_script = """
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

        # const scrollInterval = setInterval(() => {
        #     window.scrollTo(0, document.body.scrollHeight)
        #     setTimeout(() => {
        #         let newItems = document.querySelectorAll(".product-item a").length
            
        #         if (newItems === currentItems) {
        #             clearInterval(scrollInterval)
        #         }
        #         currentItems = newItems
        #     }, 5000) // Wait for new content to load
        # }, 5500)
    
    def start_requests(self):
        self.logger.debug("start running here")
        for url in self.start_urls:
            self.logger.debug(f"url {url}")
            # yield SplashRequest(url, callback=self.parse, endpoint='execute', args={"timeout": 60, "lua_source": self.generate_script_to_wait_for(".pc-sidenavbar a")})
            # yield SeleniumRequest(url=url, callback=self.parse, wait_time=20, wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR, ".pc-sidenavbar a")))
            # yield SeleniumRequest(url=url, callback=self.parse, wait_time=20)
            yield scrapy.Request(url, callback=self.parse, meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", ".pc-sidenavbar a"),
                    PageMethod("wait_for_timeout", 1000)
                ],
            })


    def parse(self, response):
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
                    # yield SplashRequest(category_url, callback=self.parse_category, endpoint='execute', args={"timeout": 60, "lua_source": self.generate_script_to_wait_for(".plp-carousel__link")})
                    # yield SeleniumRequest(url=category_url, callback=self.parse_category, wait_time=20, wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR, ".plp-carousel__link")))
                    # yield SeleniumRequest(url=category_url, callback=self.parse_category, wait_time=20)
                    yield scrapy.Request(category_url, callback=self.parse_category, meta={
                        "extra_data": {
                            "category": category
                        }, 
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", ".plp-carousel__link"),
                        ],
                    })
                    # yield SplashRequest(category_url, callback=self.parse_category, args={"wait": 20, "timeout": 20})
        except Exception as e:
            self.logger.error(f'Unexpected error in parse: {e}')

    def parse_category(self, response):
        try:
            self.logger.debug("parsing category ")
            # self.logger.debug("parsing category ")
            subcategory_selectors = response.css(".plp-carousel")

            self.logger.debug(f"sub cats are {len(subcategory_selectors)}")
            for selector in [subcategory_selectors[0]]:
                subcategory = selector.css(".plp-carousel__title-name::text").get()
                view_all_url = selector.css(".plp-carousel__link").attrib["href"]
                self.logger.debug(f"subcat is {subcategory} {view_all_url}")

                if not view_all_url.startswith('http'):
                    view_all_url = response.urljoin(view_all_url)

                self.logger.debug(f"view all url is {view_all_url}")

                # yield SplashRequest(view_all_url, callback=self.p, endpoint='execute', args={"timeout": 60, "lua_source": self.scroll_down_script})
                # yield SeleniumRequest(url=view_all_url, callback=self.p, wait_time=20)
                yield scrapy.Request(view_all_url, callback=self.parse_subcategory, meta={
                    "extra_data": {**response.meta["extra_data"], "subcategory": subcategory},
                    "playwright": True,
                    "playwright_page_methods": [
                        # wait for the items to be loaded first
                        PageMethod("wait_for_selector", ".product-item-image"),
                        # scroll to the bottom of the list to load more items
                        PageMethod("evaluate", self.scrolling_script),
                    ],
                })
        except Exception as e:
            self.logger.error(f'Unexpected error in parse_category: {e}')

    def parse_subcategory(self, response):
        try:
            product_selectors = response.css(".product-item a")
                
            for selector in product_selectors:
                product_detail_url = selector.attrib["href"]
                self.logger.debug(f"detail url is {product_detail_url}")
                # yield SplashRequest(product_detail_url, self.parse_details, endpoint='execute', args={"timeout": 60}, meta={"url": product_detail_url})
                # yield SeleniumRequest(url=product_detail_url, callback=self.parse_details, wait_time=200, meta={"url": product_detail_url})
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