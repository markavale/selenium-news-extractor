from ..items import StaticArticleItem
import requests, os, datetime, json, scrapy
from scrapy import signals
from ..article_contents.news import News
from ..article_contents.source.static import StaticSource
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from ..helpers.proxy import get_proxy
from news_extractor.settings import PROXY
from logs.main_log import init_log

log = init_log('test_static_spider')


class TestSpider(scrapy.Spider):
    name = "test_spider"
    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.TestStaticPipeline': 300},
    }

    def __init__(self, urls=None):
        self.urls = urls
        self.article_items = StaticArticleItem()

    def start_requests(self):
        # log.info(f"Spider started scraping || Total data: {len(self.urls)}")
        log.info("Using Proxy %s" %PROXY)
        urls = [
            "https://www.mixofeverything.net/2021/03/wearable-air-purifier-with-lg-puricare-and-new-air-conditioners.html"
        ]
        for d in self.urls:
            try:
                article = {
                    "test": "hello world",
                    "_id": "awef1231231231"
                }
                if PROXY:
                    meta = {}
                    headers = {}
                    try:
                        proxy = get_proxy()
                        ip = proxy['ip']
                        port = proxy['port']
                        meta_proxy = f"http://{ip}:{port}"
                        headers['User-Agent'] = proxy['randomUserAgent']
                        meta['proxy'] = meta_proxy
                    except Exception as e:
                        meta['proxy'] = 'http://103.105.212.106:53281'
                        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.0 rv:21.0) Gecko/20100101 Firefox/21.0'
                    yield scrapy.Request(d, self.parse, headers=headers, meta=meta, errback=self.errback_httpbin, cb_kwargs={'article': article}, dont_filter=True)
                else:
                    print(d)
                    yield scrapy.Request(d, callback=self.parse, errback=self.errback_httpbin, cb_kwargs={'article': article}, dont_filter=True)
            except Exception as e:
                log.exception(e)
                log.error("Skip url: %s", url)

    def parse(self, response, article):
        src = StaticSource(response.url)
        text_format = src.text
        news = News(response.url, text_format)
        pprint(news)
        if news.title is None or news.content is None:
            log.error(news.title)
            log.error(news.content)
        # data = news.generate_data()
        print("--------------------------------------------------------------------------------")
        log.info(response.request.headers)
        log.debug(response.request.meta)
        self.article_items['article_source_url'] = ""
        self.article_items['article_title'] = news.title
        self.article_items['article_section'] = []
        self.article_items['article_authors'] = news.authors
        self.article_items['article_publish_date'] = news.publish_date
        self.article_items['article_images'] = news.images
        self.article_items['article_content'] = news.content
        self.article_items['article_videos'] = news.videos
        self.article_items['article_media_type'] = 'Web'
        self.article_items['article_ad_value'] = ""
        self.article_items['article_pr_value'] = ""
        self.article_items['article_language'] = news.language
        self.article_items['article_status'] = "Done"
        self.article_items['article_error_status'] = None
        self.article_items['keyword'] = []
        self.article_items['article_url'] = news.url
        self.article_items['date_created'] = datetime.datetime.today().isoformat()
        self.article_items['date_updated'] = datetime.datetime.today().isoformat()
        self.article_items['created_by'] = "Python Global Scraper"
        self.article_items['updated_by'] = "Python Global Scraper"
        self.article_items['website'] = ""
        self.article_items['article_id'] = article['_id']
        self.article_items['download_latency'] = response.request.meta['download_latency']        
        self.article_items['http_err'] = 0
        self.article_items['timeout_err'] = 0
        self.article_items['dns_err'] = 0
        self.article_items['base_err'] = 0
        self.article_items['skip_url'] = 0

        yield self.article_items
        print(
            f"------------------------------------ end parsing ---------------------------")

    def errback_httpbin(self, failure):
        article = failure.request.cb_kwargs['article']
        print("error")
        log.error("error")
        log.error(failure)

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            log.info("HTTP Error Retry to parsing on %s", response.url)
            yield scrapy.Request(response.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            log.info("DNSLookup Error Retry to parsing on %s", request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.info("Timeout Error Retry parsing on %s", request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        else:
            request = failure.request
            log.info("Base Error Retry parsing on %s", request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )

    def errback_httpbin_final(self, failure):
        article = failure.request.cb_kwargs['article']
        log.exception("errback_httpbin_final triggered")
        print("errror")
        if failure.check(HttpError):
            response = failure.value.response
            log.error("HttpError on %s", response.url)
            self.article_items['article_id'] = article['_id']
            self.article_items['article_source_url'] = ""
            self.article_items['http_err'] = 1
            self.article_items['dns_err'] = 0
            self.article_items['timeout_err'] = 0
            self.article_items['base_err'] = 0
            self.article_items['skip_url'] = 0
            self.article_items['download_latency'] = None
            self.article_items['article_status'] = "Error"
            self.article_items['article_error_status'] = "HTTP Error"
            self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            self.article_items['article_url'] = response.url
            yield self.article_items

        elif failure.check(DNSLookupError):
            request = failure.request
            log.error("DNSLookupError on %s", request.url)
            self.article_items['article_source_url'] = ""
            self.article_items['http_err'] = 0
            self.article_items['dns_err'] = 1
            self.article_items['timeout_err'] = 0
            self.article_items['base_err'] = 0
            self.article_items['skip_url'] = 0
            self.article_items['article_id'] = article['_id']
            self.article_items['download_latency'] = None
            self.article_items['article_status'] = "Error"
            self.article_items['article_error_status'] = "DNS Lookup Error"
            self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            self.article_items['article_url'] = request.url
            yield self.article_items

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.error("TimeoutError2 on %s", request.url)
            self.article_items['article_source_url'] = ""
            self.article_items['http_err'] = 0
            self.article_items['dns_err'] = 0
            self.article_items['timeout_err'] = 1
            self.article_items['base_err'] = 0
            self.article_items['skip_url'] = 0
            self.article_items['article_id'] = article['_id']
            self.article_items['download_latency'] = None
            self.article_items['article_status'] = "Error"
            self.article_items['article_error_status'] = "Timeout Error"
            self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            self.article_items['article_url'] = request.url
            yield self.article_items
        else:
            request = failure.request
            log.error("BaseError on %s", request.url)
            self.article_items['article_source_url'] = ""
            self.article_items['http_err'] = 0
            self.article_items['dns_err'] = 0
            self.article_items['timeout_err'] = 0
            self.article_items['base_err'] = 1
            self.article_items['skip_url'] = 0
            self.article_items['article_id'] = article['_id']
            self.article_items['article_status'] = "Error"
            self.article_items['download_latency'] = None
            self.article_items['article_error_status'] = "Error"
            self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            self.article_items['article_url'] = request.url
            yield self.article_items