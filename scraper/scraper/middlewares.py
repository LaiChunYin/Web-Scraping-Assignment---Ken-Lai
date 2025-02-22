# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, exceptions

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from playwright.async_api import TimeoutError


class ScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class ScraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        if response.status >= 200 and response.status <= 299:
            return response
        else:
            spider.logger.error(f"Request failed with status {response.status}: {response.url}")
            raise exceptions.IgnoreRequest(f"Request failed with status {response.status}")

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        if isinstance(exception, exceptions.IgnoreRequest):
            spider.logger.info(f"Request ignored due to processing failure: {request.url}")
            return None  # This will stop further exception processing

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")

class PlaywrightRetryMiddleware:
    def __init__(self, crawler):
        self.retry_times = crawler.settings.getint('RETRY_TIMES', 3)
        self.retry_http_codes = set(int(x) for x in crawler.settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = crawler.settings.getint('RETRY_PRIORITY_ADJUST', -1)

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_exception(self, request, exception, spider):
        if isinstance(exception, TimeoutError) and request.meta.get("playwright", False):
            retries = request.meta.get('retry_times', 0) + 1

            if retries <= self.retry_times:
                spider.logger.info(f"Retrying {request.url} due to playwright timeout (retry {retries}/{self.retry_times}).")
                retryreq = request.copy()
                retryreq.meta['retry_times'] = retries
                retryreq.dont_filter = True
                retryreq.priority = request.priority + self.priority_adjust
                return retryreq
            else:
                spider.logger.info(f"Gave up retrying {request.url} after {retries} attempts.")

    def spider_opened(self, spider):
        spider.logger.info(f"PlaywrightRetryMiddleware initialized: RETRY_TIMES={self.retry_times}, RETRY_HTTP_CODES={list(self.retry_http_codes)}, RETRY_PRIORITY_ADJUST={self.priority_adjust}")
        spider.logger.info(f"Spider opened: {spider.name}")
