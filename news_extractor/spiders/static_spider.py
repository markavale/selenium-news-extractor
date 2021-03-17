from ..items import StaticArticleItem, ScrapyCrawlerItem
from logzero import logfile, logger
import requests,os, datetime, json, scrapy
from ..article_contents.news import News
from ..article_contents.source.static import StaticSource
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from ..helpers.api import  article_process, article_error
from ..helpers.media_value_helper import media_value
from ..helpers.proxy import get_proxy
from decouple import config

from logs.main_log import init_log
log = init_log('static_spider')

use_proxy = config('USE_PROXY', cast=bool)

process_name = config('PROCESS_NAME')

TOKEN = config("TOKEN")

class ArticleStaticSpider(scrapy.Spider):
    name = "article_static"
    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.StaticExtractorPipeline': 300},
    }
    def __init__(self, data=None):
        self.data = data
        self.article_items = StaticArticleItem()
        self.crawler_items = ScrapyCrawlerItem()
        self.crawler_items['http_err'] = 0
        self.crawler_items['timeout_err'] = 0
        self.crawler_items['dns_err'] = 0
        self.crawler_items['base_err'] = 0
        self.crawler_items['skip_url'] = 0

    def start_requests(self):
        log.info("Spider started scraping")
        log.info("Using Proxy %s" %use_proxy)
        for d in self.data:
            try:
                if process_name == "article_link":
                    article_process(d['_id'], "article")  # update status to Process
                else:
                    article_process(d['_id'], "global-link")  # update status to Process
                if use_proxy == True:
                    # print("IM HERE -----------------------------------------------")
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
                    yield scrapy.Request(d['article_url'], self.parse, headers=headers, meta=meta, errback=self.errback_httpbin, cb_kwargs={'article': d}, dont_filter=True)
                else:
                    yield scrapy.Request(d['article_url'], callback=self.parse, errback=self.errback_httpbin, cb_kwargs={'article': d}, dont_filter=True)
            except Exception as e:
                log.error(e)
                log.error("Skip url: %s", url)
                self.crawler_items['skip_url'] = 1
                
    def parse(self, response, article):
        src = StaticSource(response.url)
        text_format = src.text
        news = News(response.url, text_format)
        if news.content is None:
            log.error("Content Error on %s", response.url)
        data = news.generate_data()
        try:
            media = media_value(global_rank=article["website"]["alexa_rankings"]['global'], local_rank=article["website"]["alexa_rankings"]['local'],
                                website_cost=article['website']["website_cost"], article_images=news.images, article_videos=news.videos, article_content=news.content)
        except Exception as e:
            log.error("Meida value %s", e)
            log.error("Media value error %s", response.url)
        self.article_items['article_title'] = news.title
        self.article_items['article_section'] = []
        self.article_items['article_authors'] = news.authors
        self.article_items['article_publish_date'] = news.publish_date
        self.article_items['article_images'] = news.images
        self.article_items['article_content'] = news.content
        self.article_items['article_videos'] = news.videos
        self.article_items['article_media_type'] = 'web'
        self.article_items['article_ad_value'] = media.json()[
            'data']['advalue']
        self.article_items['article_pr_value'] = media.json()[
            'data']['prvalue']
        self.article_items['article_language'] = news.language
        self.article_items['article_status'] = "Done"
        self.article_items['article_error_status'] = None
        self.article_items['article_source_from'] = None
        self.article_items['keyword'] = []
        self.article_items['article_url'] = news.url
        self.article_items['date_created'] = datetime.datetime.today().isoformat()
        self.article_items['date_updated'] = datetime.datetime.today().isoformat()
        self.article_items['created_by'] = "Python Global Scraper"
        self.article_items['updated_by'] = "Python Global Scraper"
        self.article_items['article_id'] = article['_id']
        self.article_items['artice_source_url'] = article['fqdn']
        
        # self.article_items['download_latency'] = response.request.headers['download_latency']
        
        log.info(response.request.headers)
        log.debug(response.request.meta)

        yield self.article_items

    def errback_httpbin(self, failure):
        article = failure.request.cb_kwargs['article']
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            log.error("Retry: HttpError on %s", response.url)
            self.logger.error('HttpError on %s', response.url)
            yield scrapy.Request(response.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(DNSLookupError):
            request = failure.request
            log.error("Retry: DNSLookupError on %s", request.url)
            self.logger.error('DNSLookupError on %s', request.url)
            yield scrapy.Request(request.url,
                                 callback=self.parse,
                                 errback=self.errback_httpbin_final,
                                 dont_filter=True,
                                 cb_kwargs={'article': article}
                                 )
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.error("Retry: TimeoutError on %s", request.url)
            self.logger.error('TimeoutError on %s', request.url)
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
        article_id = article['_id']

        if failure.check(HttpError):
            response = failure.value.response
            log.error("HttpError on %s", response.url)
            article_error(article_id, "HTTP Error", process_name)
            self.logger.error('HttpError on %s', response.url)
            self.crawler_items['http_err'] = 1


        elif failure.check(DNSLookupError):
            request = failure.request
            log.error("DNSLookupError on %s", request.url)
            article_error(article_id, "DNS Lookup Error", process_name)
            self.logger.error('DNSLookupError on %s', request.url)
            self.crawler_items['dns_err'] = 1

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.error("TimeoutError2 on %s", request.url)
            article_error(article_id, "Timeout Error", process_name)
            self.logger.error('TimeoutError on %s', request.url)
            self.crawler_items['timeout_err'] = 1

        else:
            request = failure.request
            log.error("BaseError on %s", request.url)
            article_error(article_id, "Error", process_name)
            self.crawler_items['base_err'] = 1

