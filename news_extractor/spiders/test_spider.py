from ..items import StaticArticleItem
from logzero import logfile, logger
import requests
import os
import datetime
import json
import scrapy
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
        # "FEEDS": {"test_articles.json": {"format": "json"}},
    }

    def __init__(self, urls=None):
        self.urls = urls
        self.article_items = StaticArticleItem()
        self.http_error = 0
        self.timeout_error = 0
        self.dns_error = 0
        self.base_error = 0
        self.skip_url = 0
        self.download_latency = 0
        self.crawler_items = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TestSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.item_scraped,
                                signal=signals.item_scraped)
        return spider

    def item_scraped(self, item):
        # Send the scraped item to the server
        # d = treq.post(
        #     'http://example.com/post',
        #     json.dumps(item).encode('ascii'),
        #     headers={b'Content-Type': [b'application/json']}
        # )

        # The next item will be scraped only after
        # deferred (d) is fired
        return item
    

    def start_requests(self):
        print("went here")
        log.debug(f"Spider started scraping || Total data: {len(self.urls)}")
        for d in self.urls:
            try:
                article = {
                    "test": "hello world"
                }
                if PROXY:
                    log.info("USING PROXY")
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
                    yield scrapy.Request(d, callback=self.parse, errback=self.errback_httpbin, cb_kwargs={'article': article}, dont_filter=True)
            except Exception as e:
                log.exception(e)
                log.error("Skip url: %s", url)
                self.crawler_items['skip_url'] = 1

    def parse(self, response, article):
        # print("went here")
        src = StaticSource(response.url)
        text_format = src.text
        news = News(response.url, text_format)
        if news.title is None or news.content is None:
            log.error(news.title)
            log.error(news.content)
        # data = news.generate_data()
        print("--------------------------------------------------------------------------------")
        self.article_items['article_title'] = news.title
        self.article_items['article_section'] = []
        self.article_items['article_authors'] = news.authors
        self.article_items['article_publish_date'] = news.publish_date
        self.article_items['article_images'] = news.images
        self.article_items['article_content'] = news.content
        self.article_items['article_videos'] = news.videos
        self.article_items['article_media_type'] = 'web'
        self.article_items['article_ad_value'] = ""
        self.article_items['article_pr_value'] = ""
        self.article_items['article_language'] = news.language
        self.article_items['article_status'] = "Done"
        self.article_items['article_error_status'] = None
        self.article_items['article_source_from'] = None
        self.article_items['keyword'] = []
        self.article_items['article_url'] = news.url
        self.article_items['date_created'] = datetime.datetime.today(
        ).isoformat()
        self.article_items['date_updated'] = datetime.datetime.today(
        ).isoformat()
        self.article_items['created_by'] = "Python Global Scraper"
        self.article_items['updated_by'] = "Python Global Scraper"

        log.info(response.request.headers)
        log.debug(response.request.meta)
        self.article_items['download_latency'] = response.request.meta['download_latency']
        # try:
        #     log.debug(response.request.headers['User-Agent'])
        #     log.debug(response.meta.get("proxy"))
        # except Exception as e:
        #     log.exception(e)
        # log.debug(response.request.meta['User-Agent'])
        # log.debug(response.request.meta['proxy'])
        # self.article_items['user_agent'] = response.request.headers['User-Agent']
        # self.article_items['ip'] = response.meta.get('proxy')

        

        yield self.article_items
        # log.debug(self.article_items)
        yield self.crawler_items.append(self.article_items)

        print(
            f"------------------------------------ end parsing ---------------------------")

    def errback_httpbin(self, failure):
        article = failure.request.cb_kwargs['article']
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            log.error("HttpError1 on %s", response.url)
            log.info("Retry to parse on %s", response.url)
            self.logger.error('HttpError1 on %s', response.url)
            yield scrapy.Request(response.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            log.error("DNSLookupError1 on %s", request.url)
            log.info("Retry to parse on %s", request.url)
            self.logger.error('DNSLookupError1 on %s', request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.error("TimeoutError1 on %s", request.url)
            log.info("Retry to parse on %s", request.url)
            self.logger.error('TimeoutError1 on %s', request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        else:
            request = failure.request
            log.error("Base Error1 on %s", request.url)
            log.info("Retry to parse on %s", request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )

    def errback_httpbin_final(self, failure):
        log.error("errback_httpbin_final triggered")
        if failure.check(HttpError):
            response = failure.value.response
            log.error("HttpError2 on %s", response.url)
            self.logger.error('HttpError2 on %s', response.url)
            self.http_error = 1

        elif failure.check(DNSLookupError):
            request = failure.request
            log.error("DNSLookupError2 on %s", request.url)
            self.logger.error('DNSLookupError2 on %s', request.url)
            self.dns_error = 1

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.error("TimeoutError2 on %s", request.url)
            self.logger.error('TimeoutError2 on %s', request.url)
            self.timeout_error = 1
        else:
            request = failure.request
            log.error("BaseError2 on %s", request.url)
            self.base_error = 1

    def get_crawler_items():
        return self.crawler_items
