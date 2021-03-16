from ..items import StaticArticleItem
from logzero import logfile, logger
import requests,os, datetime, json, scrapy
from scrapy import signals
from ..article_contents.news import News
from ..article_contents.source.static import StaticSource

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from ..helpers.proxy import get_proxy

from logs.main_log import init_log
log = init_log('news_extractor')

class TestSpider(scrapy.Spider):
    name = "test_spider"
    logfile("server.log", maxBytes=1e6, backupCount=3)
    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.StaticExtractorPipeline': 300},
        "FEEDS": {"test_articles.json": {"format": "json"}},
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

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TestSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.item_scraped, signal=signals.item_scraped)
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
        log.debug(f"Spider started scraping || Total data: {len(self.urls)}")
        for url in self.urls:
            try:
                # proxy = get_proxy()
                # ip = proxy['ip']
                # port = proxy['port']
                # meta_proxy = f"http://{ip}:{port}"
                # # headers['User-Agent'] = proxy['randomUserAgent']
                # headers = {
                #     "User-Agent": proxy['randomUserAgent']
                # }
                # # meta['proxy'] = meta_proxy
                # meta = {
                #     "proxy": meta_proxy
                # }
                article = {
                    "test": "hello world"
                }
                print(
                    f"------------------------------------ start request  -------------------------------")
                # yield scrapy.Request(url, callback=self.parse, meta=meta, headers=headers, errback=self.errback_httpbin, dont_filter=True)
                # yield scrapy.Request(url, callback=self.parse, meta=meta, headers=headers, errback=self.errback_httpbin, dont_filter=True, cb_kwargs={'article': article})
                yield scrapy.Request(url, callback=self.parse, errback=self.errback_httpbin, dont_filter=True, cb_kwargs={'article': article})

                print(
                    f"------------------------------------ end start request  -------------------------------")
            except Exception as e:
                self.skip_url += 1
                log.error(e)
                log.exception(e)
                log.error("SKip url: %s", url)

    def parse(self, response, article):
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

        yield self.article_items
        print(
            f"------------------------------------ end parsing ---------------------------")

    def errback_httpbin(self, failure):
        article = failure.request.cb_kwargs['article']
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

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
        if failure.check(HttpError):
            self.http_error += 1
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            log.error("HttpError2 on %s", response.url)
            self.logger.error('HttpError2 on %s', response.url)

        elif failure.check(DNSLookupError):
            self.dns_error += 1
            # this is the original request
            request = failure.request
            log.error("DNSLookupError2 on %s", request.url)
            self.logger.error('DNSLookupError2 on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            self.timeout_error += 1
            request = failure.request
            log.error("TimeoutError2 on %s", request.url)
            self.logger.error('TimeoutError2 on %s', request.url)

        else:
            self.base_error += 1
            request = failure.request
            log.error("BaseError2 on %s", request.url)
