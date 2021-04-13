from ..items import StaticArticleItem
from logzero import logger
import requests,os, datetime, json, scrapy, time
from ..article_contents.news import News
from ..article_contents.source.static import StaticSource
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from ..helpers.api import  article_process, article_error
from ..helpers.media_value_helper import media_value
from ..helpers.proxy import get_proxy
from decouple import config
from pprint import pprint
from logs.main_log import init_log
from news_extractor.settings import TOKEN, PROXY, CREATED_BY, DEFAULT_PROXY, DEFAULT_USER_AGENT
from news_extractor.scrapy_extractor.news import NewsExtract
from news_extractor.helpers.utils import convert
log = init_log('static_spider')
use_proxy = PROXY

if CREATED_BY == "System":
    source_created_from = "System Link"
else:
    source_created_from = "Global Link"

class ArticleStaticSpider(scrapy.Spider):
    name = "article_static"
    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.StaticExtractorPipeline': 300},
    }
    def __init__(self, data=None):
        self.data = data
        self.article_items = StaticArticleItem()

    def start_requests(self):
        log.info("Spider started scraping")
        log.info("Using Proxy %s" %use_proxy)
        start_req_t1 = time.perf_counter()
        for d in self.data:
            try:
                # article_process(d['_id'], "article")  # update status to Process
                is_using_proxy      = d['website']['is_using_proxy']
                needs_https         = d['website']['needs_https']
                if bool(needs_https):
                        http_split = d['article_url'].split('http')
                        d['article_url'] = "https".join(http_split)
                if bool(is_using_proxy) == True:
                    print("Using proxy on ",d['article_url'])
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
                    # add proxy and user agent to dict for cb_kwargs
                    d['proxy'] = meta['proxy']
                    d['user_agent'] = headers['User-Agent']
                    yield scrapy.Request(d['article_url'], self.parse, headers=headers, meta=meta, errback=self.errback_httpbin, cb_kwargs={'article': d}, dont_filter=True)
                else:
                    print("Not using proxy on ", d['article_url'])
                    d['proxy'] = "MACHINE's IP"#DEFAULT_PROXY
                    d['user_agent'] = DEFAULT_USER_AGENT
                    yield scrapy.Request(d['article_url'], callback=self.parse, errback=self.errback_httpbin, cb_kwargs={'article': d}, dont_filter=True)
            except Exception as e:
                log.exception(e)
                log.error("Skip url: %s", d['article_url'])
                articles = self.yeild_article_items(
                    article_source_url                  = d['website']['fqdn'],
                    article_media_type                  = 'Web',
                    article_status                      = "Error",
                    article_error_status                = "Skip URL",
                    article_url                         = d['article_source_url'],
                    date_updated                        = datetime.datetime.today().isoformat(),
                    updated_by                          = "Python Global Scraper",
                    article_id                          = article['_id'],
                    base_url                            = 1,
                    proxy                               = article['proxy'],
                    user_agent                          = article['user_agent']
                )
                yield articles

        start_req_t2 = time.perf_counter()
        log.info("Start Request: {}".format(convert(round(start_req_t2 - start_req_t1, 2))))  

    def parse(self, response, article):
        try:
            # Global Parser
            t1_time = time.perf_counter()
            news = NewsExtract(response.url, response.text)
            print(f"Global parser: took {round(time.perf_counter() - t1_time, 2)} secs on {response.url}")
            log.info(f"Global parser took {round(time.perf_counter() - t1_time, 2)} secs on {article['article_url']}")
            if news.title is None or news.content is None:
                log.error(f"Content error on {article['article_url']}")
                print("Content error")
                articles = self.yeild_article_items(
                    article_source_url                  = article['website']['fqdn'],
                    article_media_type                  = 'Web',
                    article_status                      = "Error",
                    article_error_status                = "No content",
                    article_url                         = article['article_url'],
                    date_updated                        = datetime.datetime.today().isoformat(),
                    updated_by                          = "Python Global Scraper",
                    article_id                          = article['_id'],
                    base_err                            = 1,
                    proxy                               = article['proxy'],
                    user_agent                          = article['user_agent']
                )
                yield articles
            else:
                try:
                    media_t1 = time.perf_counter()
                    media = media_value(global_rank=article["website"]["alexa_rankings"]['global'], local_rank=article["website"]["alexa_rankings"]['local'],
                                        website_cost=article['website']["website_cost"], article_images=news.images, article_videos=news.videos, article_content=news.content)
                    media_t2 = time.perf_counter()
                    log.info('media value: {}'.format(convert(round(media_t2-media_t1, 2))))
                except Exception as e:
                    print(e)
                    log.error("Meida value %s", e)
                    log.error("Media value error %s", response.url)
                try:
                    articles = self.yeild_article_items( 
                        article_source_url              = article['website']['fqdn'],
                        website                         = article['website']['_id'],
                        article_title                   = news.title,
                        article_section                 = [article['website']['website_category']],
                        article_authors                 = news.authors,
                        article_publish_date            = news.publish_date,
                        article_images                  = news.images,
                        article_content                 = news.content,
                        article_videos                  = news.videos,
                        article_media_type              = 'Web',
                        article_ad_value                = media.json()['data']['advalue'],
                        article_pr_value                = media.json()['data']['prvalue'],
                        article_language                = news.language,
                        article_status                  = "Done",
                        keyword                         = [],
                        article_url                     = article['article_url'],#news.url,
                        date_created                    = datetime.datetime.today().isoformat(),
                        date_updated                    = datetime.datetime.today().isoformat(),
                        created_by                      = "Python Global Scraper",
                        updated_by                      = "Python Global Scraper",
                        article_id                      = article['_id'],
                        download_latency                = response.request.meta['download_latency'],
                        proxy                           = article['proxy'],
                        user_agent                      = article['user_agent']
                    )
                    yield articles
                except Exception as e:
                    print("Exception hanlder for main parse")
                    print(e)
        except Exception as e:
            print("Error on Global parser module")
            try:
                articles = self.yeild_article_items(  
                    article_source_url                  = article['website']['fqdn'],
                    article_media_type                  = 'Web',
                    article_status                      = "Error",
                    article_error_status                = "No content",
                    article_url                         = response.url,
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
                log.error(f"Code error: {e}")
                print("Last Exception :( there must be an error when yielding items")
                print(e)
            # TODO: write error catch to yield and save status as error
            print(e)

    def errback_httpbin(self, failure):
        article = failure.request.cb_kwargs['article']
        if failure.check(HttpError):
            response = failure.value.response
            log.info("Retry: HttpError on %s", response.url)
            yield scrapy.Request(response.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(DNSLookupError):
            request = failure.request
            log.info("Retry: DNSLookupError on %s", request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.info("Retry: TimeoutError on %s", request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        else:
            request = failure.request
            log.info("Retry: BaseError to parse on %s", request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )

    def errback_httpbin_final(self, failure):
        article = failure.request.cb_kwargs['article']
        try:
            if failure.check(HttpError):
                response = failure.value.response
                log.error("HTTP Error on %s", response.url)
                self.logger.error('HTTP Error on %s', response.url)
                articles = self.yeild_article_items(
                    article_source_url                      = article['website']['fqdn'],
                    article_media_type                      = 'Web',
                    article_status                          = "Error",
                    article_error_status                    = "HTTP Error",
                    article_url                             = article['article_url'],#response.url,
                    date_updated                            = datetime.datetime.today().isoformat(),
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
                    article_source_url                      = article['website']['fqdn'],
                    article_media_type                      = 'Web',
                    article_status                          = "Error",
                    article_error_status                    = "DNS Error",
                    article_url                             = article['article_url'],#request.url,
                    date_updated                            = datetime.datetime.today().isoformat(),
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
                    article_source_url                      = article['website']['fqdn'],
                    article_status                          = "Error",
                    article_error_status                    = "Timeout Error",
                    article_url                             = article['article_url'],#request.url,
                    date_updated                            = datetime.datetime.today().isoformat(),
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
                    article_source_url                      = article['website']['fqdn'],
                    article_status                          = "Error",
                    article_error_status                    = "Base Error",
                    article_url                             = article['article_url'],#request.url,
                    date_updated                            = datetime.datetime.today().isoformat(),
                    updated_by                              = "Python Global Scraper",
                    article_id                              = article['_id'],
                    base_err                                = 1,
                    proxy                                   = article['proxy'],
                    user_agent                              = article['user_agent']
                )
                yield articles
        except Exception as e:
            log.error(f"Code error {e}")
            print(e)
            print("Beyond scrapy error handler")

    def yeild_article_items(self, **kwargs):
        self.article_items['article_source_url']        = kwargs.get('article_source_url', None)
        self.article_items['website']                   = kwargs.get('website', None)
        self.article_items['article_title']             = kwargs.get("article_title", None)
        self.article_items['article_section']           = kwargs.get("article_section", [])
        self.article_items['article_authors']           = kwargs.get("article_authors", None)
        self.article_items['article_publish_date']      = kwargs.get("article_publish_date", None)
        self.article_items['article_images']            = kwargs.get("article_images", None)
        self.article_items['article_content']           = kwargs.get("article_content", None)
        self.article_items['article_videos']            = kwargs.get("article_videos", None)
        self.article_items['article_media_type']        = kwargs.get("article_media_type", "Web")
        self.article_items['article_ad_value']          = kwargs.get("article_ad_value", None)
        self.article_items['article_pr_value']          = kwargs.get("article_pr_value", None)
        self.article_items['article_language']          = kwargs.get("article_language", None)
        self.article_items['article_status']            = kwargs.get("article_status", "Processing")
        self.article_items['article_error_status']      = kwargs.get("article_error_status", None)
        self.article_items['keyword']                   = kwargs.get("keyword", None)
        self.article_items['article_url']               = kwargs.get("article_url", None)
        self.article_items['date_created']              = kwargs.get("date_created", None)
        self.article_items['date_updated']              = kwargs.get("date_updated", None)
        self.article_items['created_by']                = kwargs.get("created_by", "System")
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
