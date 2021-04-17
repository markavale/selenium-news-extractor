from ..items import StaticArticleItem
from logzero import logfile, logger
import requests, time, os, datetime, scrapy
from scrapy import signals
from ..article_contents.news import News
from ..article_contents.source.static import StaticSource
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from ..helpers.proxy import get_proxy
from news_extractor.settings import PROXY, CREATED_BY, DEFAULT_PROXY, DEFAULT_USER_AGENT
from news_extractor.scrapy_extractor.news import NewsExtract
from newsplease import NewsPlease
from logs.main_log import init_log
log = init_log('test_static_spider')

if CREATED_BY == "System":
    source_created_from = "System Link"
else:
    source_created_from = "Global Link"

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
        return item

    def start_requests(self):
        log.debug(f"Spider started scraping || Total data: {len(self.urls)}")
        for d in self.urls:
            try:
                article = {
                    "test": "hello world",
                    "_id": "123123123123"
                }
                article['article_url'] = d
                if PROXY:
                    print("Using proxy")
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
                        meta['proxy'] = DEFAULT_PROXY
                        headers['User-Agent'] = DEFAULT_USER_AGENT
                    article['proxy'] = meta['proxy']
                    article['user_agent'] = headers['User-Agent']
                    yield scrapy.Request(d, self.parse, headers=headers, meta=meta, errback=self.errback_httpbin, cb_kwargs={'article': article}, dont_filter=True, encoding = 'utf-8')
                else:
                    article['proxy'] = DEFAULT_PROXY
                    article['user_agent'] = DEFAULT_USER_AGENT
                    yield scrapy.Request(d, callback=self.parse, errback=self.errback_httpbin, cb_kwargs={'article': article}, dont_filter=True, encoding = 'utf-8')
            except Exception as e:
                print(f"Skip URL on {d}")
                log.exception(e)
                log.error("Skip url: %s", url)

    def parse(self, response, article):
        try:
            t1_time = time.perf_counter()
            news = NewsExtract(response.url, response.text)
            print(f"Global parser: {round(time.perf_counter() - t1_time, 2)} secs")
            log.info(f"Global parser took {round(time.perf_counter() - t1_time, 2)} secs on {article['article_url']}")
            if news.title is None or news.content is None:
                print(news.title)
                print(news.content)
                print("Content error")
                articles = self.yeild_article_items(
                    article_media_type                  = 'Web',
                    article_status                      = "Error",
                    article_error_status                = "No content",
                    article_url                         = article['article_url'],
                    date_updated                        = datetime.datetime.today().isoformat(),
                    created_by                          = "Python Global Scraper",
                    updated_by                          = "Python Global Scraper",
                    article_id                          = article['_id'],
                    base_err                            = 1,
                    proxy                               = article['proxy'],
                    user_agent                          = article['user_agent'],
                )
                yield articles
            else:
                print("Article have content")
                try:
                    print("--------------------------------------------------------------------------------")
                    log.info(response.request.headers)
                    log.debug(response.request.meta)
                    articles = self.yeild_article_items( 
                        article_source_url              = "test_url",
                        website                         = "website",
                        article_title                   = news.title,
                        article_section                 = [],
                        article_authors                 = news.authors,
                        article_publish_date            = news.publish_date,
                        article_images                  = news.images,
                        article_content                 = news.content,
                        article_videos                  = news.videos,
                        article_media_type              = 'Web',
                        article_ad_value                = "123",
                        article_pr_value                = "123",
                        article_language                = news.language,
                        article_status                  = "Done",
                        keyword                         = [],
                        article_url                     = article['article_url'],
                        date_created                    = datetime.datetime.today().isoformat(),
                        date_updated                    = datetime.datetime.today().isoformat(),
                        created_by                      = "Python Global Scraper",
                        updated_by                      = "Python Global Scraper",
                        article_id                      = article['_id'],
                        download_latency                = response.request.meta['download_latency'],
                        proxy                           = article['proxy'],
                        user_agent                      = article['user_agent']
                    )
                    log.info(response.request.meta)
                    log.info(response.request.headers)
                    yield articles
                    print(
                        f"------------------------------------ end parsing ---------------------------")
                except Exception as e:
                    print("Exception hanlder for main parse")
                    print(e)
        except Exception as e:
            print("Error on Global parser module")
            log.error(f"Global parser error on: {article['article_url']}")
            try:
                articles = self.yeild_article_items(  
                    article_source_url                  = "test_url",
                    article_media_type                  = 'Web',
                    article_status                      = "Error",
                    article_error_status                = "No content",
                    article_url                         = article['article_url'],
                    date_updated                        = datetime.datetime.today().isoformat(),
                    created_by                          = "Python Global Scraper",
                    updated_by                          = "Python Global Scraper",
                    article_id                          = article['_id'],
                    base_err                            = 1,
                    proxy                               = article['proxy'],
                    user_agent                          = article['user_agent'],
                )
                yield articles
            except Exception as e:
                print(":(")
                print(e)
            # TODO: write error catch to yield and save status as error
            print(e)
            
    def errback_httpbin(self, failure):
        article = failure.request.cb_kwargs['article']
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            log.info("HTTP Error Retry to parsing on %s", response.url)
            self.logger.error('HTTP Error Retry parsing on %s', response.url)
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
            self.logger.error(
                'DNS Lookup Error Retry parsing on %s', request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.info("Timeout Error Retry parsing on %s", request.url)
            self.logger.error(
                'Timeout Error Retry parsing on on %s', request.url)
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
        try:
            if failure.check(HttpError):
                response = failure.value.response
                log.error("HTTP Error on %s", response.url)
                self.logger.error('HTTP Error on %s', response.url)
                articles = self.yeild_article_items(
                    article_source_url                      = "test_url",
                    article_media_type                      = 'Web',
                    article_status                          = "Error",
                    article_error_status                    = "HTTP Error",
                    article_url                             = article['article_url'],
                    date_updated                            = datetime.datetime.today().isoformat(),
                    created_by                              = "Python Global Scraper",
                    updated_by                              = "Python Global Scraper",
                    article_id                              = article['_id'],
                    http_err                                = 1,
                    proxy                                   = article['proxy'],
                    user_agent                              = article['user_agent']
                )
                yield articles

            elif failure.check(DNSLookupError):
                print("Network Error")
                request = failure.request
                log.error("DNSLookupError on %s", request.url)
                self.logger.error('DNSLookupError on %s', request.url)
                articles = self.yeild_article_items( 
                    article_source_url                      = "test_url",
                    article_media_type                      = 'Web',
                    article_status                          = "Error",
                    article_error_status                    = "DNS Error",
                    article_url                             = article['article_url'],
                    date_updated                            = datetime.datetime.today().isoformat(),
                    created_by                              = "Python Global Scraper",
                    updated_by                              = "Python Global Scraper",
                    article_id                              = article['_id'],
                    dns_err                                 = 1,
                    proxy                                   = article['proxy'],
                    user_agent                              = article['user_agent']
                )
                yield articles

            elif failure.check(TimeoutError, TCPTimedOutError):
                request = failure.request
                log.error("TimeoutError on %s", request.url)
                self.logger.error('TimeoutError on %s', request.url)
                articles = self.yeild_article_items(
                    article_source_url                      = "test_url",
                    article_media_type                      = 'Web',
                    article_status                          = "Error",
                    article_error_status                    = "Timeout Error",
                    article_url                             = article['article_url'],
                    date_updated                            = datetime.datetime.today().isoformat(),
                    created_by                              = "Python Global Scraper",
                    updated_by                              =" Python Global Scraper",
                    article_id                              = article['_id'],
                    timeout_err                             = 1,
                    proxy                                   = article['proxy'],
                    user_agent                              = article['user_agent']
                )
                yield articles
            else:
                request = failure.request
                log.error("BaseError on %s", request.url)
                articles = self.yeild_article_items(
                    article_source_url                      = "test_url",
                    article_media_type                      = 'Web',
                    article_status                          = "Error",
                    article_error_status                    = "Base Error",
                    article_url                             = article['article_url'],#request.url,
                    date_updated                            = datetime.datetime.today().isoformat(),
                    created_by                              = "Python Global Scraper",
                    updated_by                              = "Python Global Scraper",
                    article_id                              = article['_id'],
                    base_err                                = 1,
                    proxy                                   = article['proxy'],
                    user_agent                              = article['user_agent']
                )
                yield articles
        except Exception as e:
            print(e)
            print("Beyond scrapy error handler")

    def yeild_article_items(self, **kwargs):
        self.article_items['article_source_url']        = kwargs.get('article_source_url', "DEFAULT_V")
        self.article_items['website']                   = kwargs.get('website', "DEFAULT_V")
        self.article_items['article_title']             = kwargs.get("article_title", None)
        self.article_items['article_section']           = kwargs.get("article_section", [])
        self.article_items['article_authors']           = kwargs.get("article_authors", None)
        self.article_items['article_publish_date']      = kwargs.get("article_publish_date", None)
        self.article_items['article_images']            = kwargs.get("article_images", None)
        self.article_items['article_content']           = kwargs.get("article_content", None)
        self.article_items['article_videos']            = kwargs.get("article_videos", None)
        self.article_items['article_media_type']        = kwargs.get("article_media_type", None)
        self.article_items['article_ad_value']          = kwargs.get("article_ad_value", None)
        self.article_items['article_pr_value']          = kwargs.get("article_pr_value", None)
        self.article_items['article_language']          = kwargs.get("article_language", None)
        self.article_items['article_status']            = kwargs.get("article_status", "Processing")
        self.article_items['article_error_status']      = kwargs.get("article_error_status", None)
        self.article_items['keyword']                   = kwargs.get("keyword", None)
        self.article_items['article_url']               = kwargs.get("article_url", None)
        self.article_items['date_created']              = kwargs.get("date_created", None)
        self.article_items['date_updated']              = kwargs.get("date_updated", None)
        self.article_items['created_by']                = kwargs.get("created_by", None)
        self.article_items['updated_by']                = kwargs.get("updated_by", None)
        self.article_items['article_id']                = kwargs.get("article_id", None)
        self.article_items['download_latency']          = kwargs.get("download_latency", None)
        self.article_items['http_err']                  = kwargs.get("http_err", 0)
        self.article_items['dns_err']                   = kwargs.get("dns_err", 0)
        self.article_items['timeout_err']               = kwargs.get("timeout_err", 0)
        self.article_items['base_err']                  = kwargs.get("base_err", 0)
        self.article_items['skip_url']                  = kwargs.get("skip_url", 0)
        self.article_items['proxy']                     = kwargs.get("proxy", None)
        self.article_items['user_agent']                = kwargs.get("user_agent", None)
        self.article_items['source_created_from']       = source_created_from

        return self.article_items