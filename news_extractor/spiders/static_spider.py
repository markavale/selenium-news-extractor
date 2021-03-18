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
from pprint import pprint
from logs.main_log import init_log
from news_extractor.settings import TOKEN, process_name, PROXY
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
                log.exception(e)
                log.error("Skip url: %s", url)
                self.crawler_items['skip_url'] = 1

                yield self.crawler_items
                
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
        self.article_items['article_source_from'] = None
        self.article_items['keyword'] = []
        self.article_items['article_url'] = news.url
        self.article_items['date_created'] = datetime.datetime.today().isoformat()
        self.article_items['date_updated'] = datetime.datetime.today().isoformat()
        self.article_items['created_by'] = "Python Global Scraper"
        self.article_items['updated_by'] = "Python Global Scraper"
        
        self.article_items['collection_name'] = process_name
        if process_name == "article_link":
            self.article_items['article_id'] = article['_id']
            
        else:
            self.article_items['google_link_id'] = article['_id']
            self.article_items['website'] = article['website']['_id']

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
        # article_id = article['_id']

        if failure.check(HttpError):
            response = failure.value.response
            log.error("HttpError on %s", response.url)
            if process_name == "article_link":
                self.article_items['article_id'] = article['_id']
            else:
                self.article_items['google_link_id'] = article['_id']
            self.logger.error('HttpError on %s', response.url)
            self.crawler_items['http_err'] = 1
            self.article_items['article_status'] = "Error"
            self.article_items['article_error_status'] = "HTTP Error"
            self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            self.article_items['article_url'] = response.url
            self.article_items['collection_name'] = process_name
            yield self.article_items

        elif failure.check(DNSLookupError):
            request = failure.request
            log.error("DNSLookupError on %s", request.url)
            self.logger.error('DNSLookupError on %s', request.url)
            self.crawler_items['dns_err'] = 1
            if process_name == "article_link":
                self.article_items['article_id'] = article['_id']
            else:
                self.article_items['google_link_id'] = article['_id']
            self.article_items['article_status'] = "Error"
            self.article_items['article_error_status'] = "DNS Lookup Error"
            self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            self.article_items['article_url'] = request.url
            self.article_items['collection_name'] = process_name
            yield self.article_items

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            log.error("TimeoutError2 on %s", request.url)
            self.logger.error('TimeoutError on %s', request.url)
            # self.crawler_items['timeout_err'] = 1
            if process_name == "article_link":
                self.article_items['article_id'] = article['_id']
            else:
                self.article_items['google_link_id'] = article['_id']
            self.article_items['article_status'] = "Error"
            self.article_items['article_error_status'] = "Timeout Error"
            self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            self.article_items['article_url'] = request.url
            self.article_items['collection_name'] = process_name
            yield self.article_items
        else:
            request = failure.request
            log.error("BaseError on %s", request.url)
            # self.crawler_items['base_err'] = 1
            if process_name == "article_link":
                self.article_items['article_id'] = article['_id']
            else:
                self.article_items['google_link_id'] = article['_id']
            self.article_items['article_status'] = "Error"
            self.article_items['article_error_status'] = "Error"
            self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            self.article_items['article_url'] = request.url
            self.article_items['collection_name'] = process_name
            yield self.article_items

