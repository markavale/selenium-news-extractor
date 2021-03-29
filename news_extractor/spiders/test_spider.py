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
        log.info(f"Spider started scraping || Total data: {len(self.urls)}")
        log.info("Using Proxy %s" %PROXY)
        urls = [
            "https://www.mixofeverything.net/2021/03/wearable-air-purifier-with-lg-puricare-and-new-air-conditioners.html"
        ]
        for d in self.urls:
            try:
                article = {
                    "test": "hello world",
                    "_id": "123123123123"
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
                    yield scrapy.Request(d, callback=self.parse, errback=self.errback_httpbin, cb_kwargs={'article': article}, dont_filter=True)
            except Exception as e:
                log.exception(e)
                log.error("Skip url: %s", url)

    def parse(self, response, article):
        src = StaticSource(response.url)
        text_format = src.text
        news = News(response.url, text_format)
        if news.title is None or news.content is None:
            log.error(news.title)
            log.error(news.content)
        # data = news.generate_data()
        print("--------------------------------------------------------------------------------")
        log.info(response.request.headers)
        log.debug(response.request.meta)
        articles = self.yeild_article_items(
            article_source_url = article['website']['fqdn'],
            article_title=news.title,
            article_section=[],
            article_authors=news.authors,
            article_publish_date=news.publish_date,
            article_images=news.images,
            article_content=news.content,
            article_videos=news.videos,
            article_media_type='web',
            article_ad_value="",
            article_pr_value="",
            article_language=news.language,
            article_status="Done",
            article_error_status=None,
            keyword=[],
            article_url=news.url,
            date_created=datetime.datetime.today().isoformat(),
            date_updated=datetime.datetime.today().isoformat(),
            created_by="Python Global Scraper",
            updated_by="Python Global Scraper",
            article_id=article['_id'],
            download_latency=response.request.meta['download_latency'],
            http_err=0,
            dns_err=0,
            timeout_err=0,
            base_err=0,
            skip_url=0
        )

        yield articles
        print(
            f"------------------------------------ end parsing ---------------------------")

    def errback_httpbin(self, failure):
        article = failure.request.cb_kwargs['article']

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
            log.error("HTTP Error on %s", response.url)
            articles = self.yeild_article_items(
                article_source_url = article['website']['fqdn'],
                article_title=None,
                article_section=[],
                article_authors=None,
                article_publish_date=None,
                article_images=None,
                article_content=None,
                article_videos=None,
                article_media_type='web',
                article_ad_value=None,
                article_pr_value=None,
                article_language=None,
                article_status="Error",
                article_error_status="HTTP Error",
                keyword=[],
                article_url=response.url,
                date_created=None,
                date_updated=datetime.datetime.today().isoformat(),
                created_by="Python Global Scraper",
                updated_by="Python Global Scraper",
                article_id=article['_id'],
                download_latency=None,
                http_err=1,
                dns_err=0,
                timeout_err=0,
                base_err=0,
                skip_url=0,
            )
            yield articles

        elif failure.check(DNSLookupError):
            request = failure.request
            log.error("DNSLookupError2 on %s", request.url)
            articles = self.yeild_article_items(
                article_source_url = article['website']['fqdn'],
                article_title=None,
                article_section=[],
                article_authors=None,
                article_publish_date=None,
                article_images=None,
                article_content=None,
                article_videos=None,
                article_media_type='web',
                article_ad_value=None,
                article_pr_value=None,
                article_language=None,
                article_status="Error",
                article_error_status="DNS Error",
                keyword=[],
                article_url=request.url,
                date_created=None,
                date_updated=datetime.datetime.today().isoformat(),
                created_by="Python Global Scraper",
                updated_by="Python Global Scraper",
                article_id=article['_id'],
                download_latency=None,
                http_err=0,
                dns_err=1,
                timeout_err=0,
                base_err=0,
                skip_url=0,
            )
            yield articles

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.error("TimeoutError2 on %s", request.url)
            articles = self.yeild_article_items(
                article_source_url = article['website']['fqdn'],
                article_title=None,
                article_section=[],
                article_authors=None,
                article_publish_date=None,
                article_images=None,
                article_content=None,
                article_videos=None,
                article_media_type='web',
                article_ad_value=None,
                article_pr_value=None,
                article_language=None,
                article_status="Error",
                article_error_status="Timeout Error",
                keyword=[],
                article_url=request.url,
                date_created=None,
                date_updated=datetime.datetime.today().isoformat(),
                created_by="Python Global Scraper",
                updated_by="Python Global Scraper",
                article_id=article['_id'],
                download_latency=None,
                http_err=0,
                dns_err=0,
                timeout_err=1,
                base_err=0,
                skip_url=0,
            )
            yield articles
        else:
            request = failure.request
            log.error("BaseError2 on %s", request.url)
            articles = self.yeild_article_items(
                article_source_url = article['website']['fqdn'],
                article_title=None,
                article_section=[],
                article_authors=None,
                article_publish_date=None,
                article_images=None,
                article_content=None,
                article_videos=None,
                article_media_type='web',
                article_ad_value=None,
                article_pr_value=None,
                article_language=None,
                article_status="Error",
                article_error_status="Base Error",
                keyword=[],
                article_url=request.url,
                date_created=None,
                date_updated=datetime.datetime.today().isoformat(),
                created_by="Python Global Scraper",
                updated_by="Python Global Scraper",
                article_id=article['_id'],
                download_latency=None,
                http_err=0,
                dns_err=0,
                timeout_err=0,
                base_err=1,
                skip_url=0,
            )
            yield articles

    def yeild_article_items(self, **kwargs):
        self.article_items['article_source_url'] = kwargs['article_source_url']
        self.article_items['article_title'] = kwargs['article_title'] 
        self.article_items['article_section'] = kwargs['article_section'] 
        self.article_items['article_authors'] = kwargs['article_authors'] 
        self.article_items['article_publish_date'] = kwargs['article_publish_date'] 
        self.article_items['article_images'] = kwargs['article_images'] 
        self.article_items['article_content'] = kwargs['article_content'] 
        self.article_items['article_videos'] = kwargs['article_videos'] 
        self.article_items['article_media_type'] = kwargs['article_media_type'] 
        self.article_items['article_ad_value'] = kwargs['article_ad_value'] 
        self.article_items['article_pr_value'] = kwargs['article_pr_value'] 
        self.article_items['article_language'] = kwargs['article_language'] 
        self.article_items['article_status'] = kwargs['article_status'] 
        self.article_items['article_error_status'] = kwargs['article_error_status'] 
        self.article_items['keyword'] = kwargs['keyword'] 
        self.article_items['article_url'] = kwargs['article_url'] 
        self.article_items['date_created'] = kwargs['date_created'] 
        self.article_items['date_updated'] = kwargs['date_updated'] 
        self.article_items['created_by'] = kwargs['created_by'] 
        self.article_items['updated_by'] = kwargs['updated_by'] 
        self.article_items['article_id'] = kwargs['article_id'] 
        self.article_items['download_latency'] = kwargs['download_latency'] 
        self.article_items['http_err'] = kwargs['http_err'] 
        self.article_items['dns_err'] = kwargs['dns_err'] 
        self.article_items['timeout_err'] = kwargs['timeout_err'] 
        self.article_items['base_err'] = kwargs['base_err'] 
        self.article_items['skip_url'] = kwargs['skip_url'] 

        return self.article_items