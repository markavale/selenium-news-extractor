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
from news_extractor.settings import TOKEN, PROXY
from news_extractor.helpers.utils import convert
log = init_log('static_spider')
use_proxy = PROXY

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
                article_process(d['_id'], "article")  # update status to Process
                is_using_proxy = d['website']['is_using_proxy']
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
                        print(headers ,meta)
                    except Exception as e:
                        meta['proxy'] = 'http://103.105.212.106:53281'
                        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.0 rv:21.0) Gecko/20100101 Firefox/21.0'
                    yield scrapy.Request(d['article_url'], self.parse, headers=headers, meta=meta, errback=self.errback_httpbin, cb_kwargs={'article': d}, dont_filter=True)
                else:
                    print("Not using proxy on ", d['article_url'])
                    yield scrapy.Request(d['article_url'], callback=self.parse, errback=self.errback_httpbin, cb_kwargs={'article': d}, dont_filter=True)
            except Exception as e:
                log.exception(e)
                log.error("Skip url: %s", d['article_url'])
                self.article_items['article_id'] = article['_id']
                self.article_items['article_status'] = "Error"
                self.article_items['download_latency'] = None
                self.article_items['article_error_status'] = "Skip URL"
                self.article_items['date_updated'] = datetime.datetime.today().isoformat()
                self.article_items['article_url'] = d['article_url']
                self.article_items['http_err'] = 1
                self.article_items['dns_err'] = 0
                self.article_items['timeout_err'] = 0
                self.article_items['base_err'] = 0
                self.article_items['skip_url'] = 0

                yield self.article_items
        start_req_t2 = time.perf_counter()
        log.info("Start Request: {}".format(convert(round(start_req_t2 - start_req_t1, 2))))        
    def parse(self, response, article):
        global_parser_t1 = time.perf_counter()
        src = StaticSource(response.url)
        text_format = src.text
        news = News(response.url, text_format)
        global_parser_t2 = time.perf_counter()
        log.info("Global Parser: {}".format(convert(round(global_parser_t2 - global_parser_t1, 2))))
        if news.content is None:
            log.error("Content Error on %s", response.url)
        data = news.generate_data()
        
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
            # exit(0)
        parse_t1 = time.perf_counter()
        self.article_items['article_source_url'] = article['website']['fqdn']
        self.article_items['article_title'] = news.title
        self.article_items['article_section'] = [article['website']['website_category']]
        self.article_items['article_authors'] = news.authors
        self.article_items['article_publish_date'] = news.publish_date
        self.article_items['article_images'] = news.images
        self.article_items['article_content'] = news.content
        self.article_items['article_videos'] = news.videos
        self.article_items['article_media_type'] = 'Web'
        self.article_items['article_ad_value'] = media.json()[
            'data']['advalue']
        self.article_items['article_pr_value'] = media.json()[
            'data']['prvalue']
        self.article_items['article_language'] = news.language
        self.article_items['article_status'] = "Done"
        self.article_items['article_error_status'] = None
        self.article_items['keyword'] = []
        self.article_items['article_url'] = news.url
        self.article_items['date_created'] = datetime.datetime.today().isoformat()
        self.article_items['date_updated'] = datetime.datetime.today().isoformat()
        self.article_items['created_by'] = "Python Global Scraper"
        self.article_items['updated_by'] = "Python Global Scraper"
        self.article_items['website'] = article['website']['_id']
        self.article_items['article_id'] = article['_id']
        self.article_items['download_latency'] = response.request.meta['download_latency']        
        self.article_items['http_err'] = 0
        self.article_items['timeout_err'] = 0
        self.article_items['dns_err'] = 0
        self.article_items['base_err'] = 0
        self.article_items['skip_url'] = 0

        yield self.article_items
        parse_t2 = time.perf_counter()
        log.info("Parsing: {}".format(convert(round(parse_t2 - parse_t1, 2))))
    def errback_httpbin(self, failure):
        article = failure.request.cb_kwargs['article']

        if failure.check(HttpError):
            response = failure.value.response
            log.error("Retry: HttpError on %s", response.url)
            yield scrapy.Request(response.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(DNSLookupError):
            request = failure.request
            log.error("Retry: DNSLookupError on %s", request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.error("Retry: TimeoutError on %s", request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        else:
            request = failure.request
            log.error("Retry: Base Error on %s", request.url)
            log.info("Retry to parse on %s", request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )

    def errback_httpbin_final(self, failure):
        article = failure.request.cb_kwargs['article']
        # article_id = article['_id']

        if failure.check(HttpError):
            response = failure.value.response
            log.error("HttpError on %s", response.url)
            self.article_items['article_id'] = article['_id']
            self.article_items['article_source_url'] = article['website']['fqdn']
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
            self.article_items['article_source_url'] = article['website']['fqdn']
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
            self.article_items['article_source_url'] = article['website']['fqdn']
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
            self.article_items['article_source_url'] = article['website']['fqdn']
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
