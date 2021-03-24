from ..items import StaticArticleItem
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
from news_extractor.settings import TOKEN, PROXY
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
        for d in self.data:
            try:
                # print("Article status: ".format(d['article_status']))
                article_process(d['_id'], "article")  # update status to Process
                # print("Article status: ".format(d['article_status']))
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
                # self.yield_artilce(etc....)
                # yield articles
                
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
            print(e)
            log.error("Meida value %s", e)
            log.error("Media value error %s", response.url)
        # self.article_items['article_source_url'] = article['website']['fqdn']
        # self.article_items['article_title'] = news.title
        # self.article_items['article_section'] = [article['website']['website_category']]
        # self.article_items['article_authors'] = news.authors
        # self.article_items['article_publish_date'] = news.publish_date
        # self.article_items['article_images'] = news.images
        # self.article_items['article_content'] = news.content
        # self.article_items['article_videos'] = news.videos
        # self.article_items['article_media_type'] = 'Web'
        # self.article_items['article_ad_value'] = media.json()['data']['advalue']
        # self.article_items['article_pr_value'] = media.json()['data']['prvalue']
        # self.article_items['article_language'] = news.language
        # self.article_items['article_status'] = "Done"
        # self.article_items['keyword'] = []
        # self.article_items['article_url'] = news.url
        # self.article_items['date_created'] = datetime.datetime.today().isoformat()
        # self.article_items['date_updated'] = datetime.datetime.today().isoformat()
        # self.article_items['created_by'] = "Python Global Scraper"
        # self.article_items['updated_by'] = "Python Global Scraper"
        # self.article_items['website'] = article['website']['_id']
        # self.article_items['article_id'] = article['_id']
        # self.article_items['download_latency'] = response.request.meta['download_latency']        
        # self.article_items['article_error_status'] = None
        # self.article_items['http_err'] = 0
        # self.article_items['timeout_err'] = 0
        # self.article_items['dns_err'] = 0
        # self.article_items['base_err'] = 0
        # self.article_items['skip_url'] = 0
        print("Article parsed: {}".format(news.url))
        articles = self.yeild_article_items(
            article_source_url              = article['website']['fqdn'],
            article_title                   = news.title,
            article_section                 = [],
            article_authors                 = news.authors,
            article_publish_date            = news.publish_date,
            article_images                  = news.images,
            article_content                 = news.content,
            article_videos                  = news.videos,
            article_media_type              ='Web',
            article_ad_value                = media.json()['data']['advalue'],
            article_pr_value                = media.json()['data']['prvalue'],
            article_language                = news.language,
            article_status                  = "Done",
            keyword                         = [],
            article_url                     = news.url,
            date_created                    = datetime.datetime.today().isoformat(),
            date_updated                    = datetime.datetime.today().isoformat(),
            created_by                      = "Python Global Scraper",
            updated_by                      = "Python Global Scraper",
            article_id                      = article['_id'],
            website                         = article['website']['_id'],
            download_latency                = response.request.meta['download_latency'],
            # http_err=0,
            # dns_err=0,
            # timeout_err=0,
            # base_err=0,
            # skip_url=0
        )
        print("Article status: Done")
        log.info(response.request.headers)
        log.debug(response.request.meta)

        yield articles

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
        print("Article status: Error" )
        # article_id = article['_id']

        if failure.check(HttpError):
            response = failure.value.response
            log.error("HttpError on %s", response.url)
            # self.article_items['article_id'] = article['_id']
            # self.logger.error('HttpError on %s', response.url)
            # self.article_items['article_status'] = "Error"
            # self.article_items['article_error_status'] = "HTTP Error"
            # self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            # self.article_items['article_url'] = response.url
            # yield self.article_items

            articles = self.yeild_article_items(
                article_status="Error",
                article_error_status="HTTP Error",
                article_source_from=None,
                article_url=response.url,
                date_updated=datetime.datetime.today().isoformat(),
                created_by="Python Global Scraper",
                updated_by="Python Global Scraper",
                article_id=article['_id'],
                http_err=1,
                dns_err=0,
                timeout_err=0,
                base_err=0,
                skip_url=0,
            )
            yield articles

        elif failure.check(DNSLookupError):
            request = failure.request
            log.error("DNSLookupError on %s", request.url)
            self.logger.error('DNSLookupError on %s', request.url)
            # self.article_items['article_id'] = article['_id']
            # self.article_items['article_status'] = "Error"
            # self.article_items['article_error_status'] = "DNS Lookup Error"
            # self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            # self.article_items['article_url'] = request.url
            # yield self.article_items

            articles = self.yeild_article_items(
                article_status="Error",
                article_error_status="DNS Lookup Error",
                article_source_from=None,
                article_url=response.url,
                date_updated=datetime.datetime.today().isoformat(),
                created_by="Python Global Scraper",
                updated_by="Python Global Scraper",
                article_id=article['_id'],
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
            self.logger.error('TimeoutError on %s', request.url)
            # self.article_items['article_id'] = article['_id']
            # self.article_items['article_status'] = "Error"
            # self.article_items['article_error_status'] = "Timeout Error"
            # self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            # self.article_items['article_url'] = request.url
            # yield self.article_items
            articles = self.yeild_article_items(
                article_status="Error",
                article_error_status="Timeout Error",
                article_source_from=None,
                article_url=response.url,
                date_updated=datetime.datetime.today().isoformat(),
                created_by="Python Global Scraper",
                updated_by="Python Global Scraper",
                article_id=article['_id'],
                http_err=0,
                dns_err=0,
                timeout_err=1,
                base_err=0,
                skip_url=0,
            )
            yield articles
            
        else:
            request = failure.request
            log.error("BaseError on %s", request.url)
            # self.article_items['article_id'] = article['_id']
            # self.article_items['article_status'] = "Error"
            # self.article_items['article_error_status'] = "Error"
            # self.article_items['date_updated'] = datetime.datetime.today().isoformat()
            # self.article_items['article_url'] = request.url
            # yield self.article_items

            articles = self.yeild_article_items(
                article_status="Error",
                article_error_status="Base Error",
                article_source_from=None,
                article_url=response.url,
                date_updated=datetime.datetime.today().isoformat(),
                created_by="Python Global Scraper",
                updated_by="Python Global Scraper",
                article_id=article['_id'],
                http_err=0,
                dns_err=0,
                timeout_err=0,
                base_err=1,
                skip_url=0,
            )
            yield articles

    def yeild_article_items(self, **kwargs):
        self.article_items['article_source_url'] = kwargs['article_source_url'] or None
        self.article_items['article_title'] = kwargs['article_title'] or None
        self.article_items['article_section'] = kwargs['article_section'] or None
        self.article_items['article_authors'] = kwargs['article_authors'] or ['No - Author']
        self.article_items['article_publish_date'] = kwargs['article_publish_date'] or None 
        self.article_items['article_images'] = kwargs['article_images'] or []
        self.article_items['article_content'] = kwargs['article_content'] or None
        self.article_items['article_videos'] = kwargs['article_videos'] or []
        self.article_items['article_media_type'] = kwargs['article_media_type'] or 'Web'
        self.article_items['article_ad_value'] = kwargs['article_ad_value'] or None
        self.article_items['article_pr_value'] = kwargs['article_pr_value'] or None
        self.article_items['article_language'] = kwargs['article_language'] or 'en'
        self.article_items['article_status'] = kwargs['article_status'] or "Error"
        self.article_items['article_error_status'] = kwargs['article_error_status'] 
        self.article_items['keyword'] = kwargs['keyword'] or []
        self.article_items['article_url'] = kwargs['article_url'] or None
        self.article_items['date_created'] = kwargs['date_created'] or datetime.datetime.today().isoformat()
        self.article_items['date_updated'] = kwargs['date_updated'] or datetime.datetime.today().isoformat()
        self.article_items['created_by'] = kwargs['created_by'] or "Python Global Scraper"
        self.article_items['updated_by'] = kwargs['updated_by'] or "Python Global Scraper"
        self.article_items['article_id'] = kwargs['article_id'] or None
        self.article_items['website'] = kwargs['website'] or None
        self.article_items['download_latency'] = kwargs['download_latency'] or None
        self.article_items['http_err'] = kwargs['http_err'] or 0
        self.article_items['dns_err'] = kwargs['dns_err'] or 0
        self.article_items['timeout_err'] = kwargs['timeout_err'] or 0 
        self.article_items['base_err'] = kwargs['base_err'] or 0
        self.article_items['skip_url'] = kwargs['skip_url'] or 0

        return self.article_items