import scrapy
from scrapy_splash import SplashRequest
from ..items import ProductItem


class TopsOnlineSpider(scrapy.Spider):
    name = "tops_online"
    allowed_domains = ["www.tops.co.th", "localhost"]
    start_urls = ["https://www.tops.co.th/en"]

    categories_to_be_scrapped = set([
        "OTOP",
        # "Only At Tops",
        # "Fruits & Vegetables",
        # "Meat & Seafood",
        # "Fresh Food & Bakery",
        # "Pantry & Ingredients",
        # "Snacks & Desserts",
        # "Beverages",
        # "Health & Beauty Care",
        # "Mom & Kids",
        # "Household & Merit",
        # "PetNme",
    ])

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


    def start_requests(self):
        print("start running here")
        for url in self.start_urls:
            print("url ", url)
            yield SplashRequest(url, callback=self.parse, endpoint='execute', args={"timeout": 60, "lua_source": self.generate_script_to_wait_for(".pc-sidenavbar a")})


    def parse(self, response):
        print("start parsing")
        category_selectors = response.css(".pc-sidenavbar a")
        print("parsing ", category_selectors)

        for selector in category_selectors:
            category = selector.css("span::text").get()
            print("cat is", category)
            if category in self.categories_to_be_scrapped:
                category_url = selector.attrib["href"]
                print("cat url ", category_url)
                yield SplashRequest(category_url, callback=self.parse_category, endpoint='execute', args={"timeout": 60, "lua_source": self.generate_script_to_wait_for(".plp-carousel__link")})
                # yield SplashRequest(category_url, callback=self.parse_category, args={"wait": 20, "timeout": 20})

    def parse_category(self, response):
        print("parsing category")
        subcategory_selectors = response.css(".plp-carousel__link")

        for selector in subcategory_selectors:
            view_all_url = selector.attrib["href"]
            print("subcat is", view_all_url)
            yield SplashRequest(view_all_url, callback=self.p, endpoint='execute', args={"timeout": 60, "lua_source": self.scroll_down_script})

    def parse_subcategory(self, response):
        product_selectors = response.css(".product-item .mt-product-item a")
            
        for selector in product_selectors:
            product_detail_url = selector.attrib["href"]
            print("detail url is ", product_detail_url)
            yield SplashRequest(product_detail_url, self.parse_details, endpoint='execute', args={"timeout": 60}, meta={"url": product_detail_url})


    def parse_details(self, response):
        product_item = ProductItem()

        product_item["product_name"] = response.css(".product-tile__name").get()
        product_item["product_images"] = [selector.attrib["src"] for selector in response.css(".product-Details-images img")]
        # product_item["quantity"] = response.css("").get()
        product_item["bar_code_number"] = response.css(".product-Details-sku").get()
        product_item["product_details"] = response.xpath('string(.)').extract()
        product_item["price"] = response.css(".product-Details-current-price").get()
        product_item["labels"] = response.css(".promo-name").getall()
        product_item["url"] = response.meta["url"]
    
        print("item is ", product_item)
        yield product_item