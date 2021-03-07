import scrapy
from ..items import StaticArticleItem
from logzero import logfile, logger
import requests, datetime, json, os
from news_extractor.settings import API_KEY
from ..article_contents.news import News
from ..article_contents.source.static import StaticSource

# from urllib.parse import urlparse
# from lxml.html import fromstring
# from itertools import cycle
# import traceback

from scrapy.mail import MailSender

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from ..helpers.endpoints import media_value

mailer = MailSender()

class ArticleStaticSpider(scrapy.Spider):
    logfile("server.log", maxBytes=1e6, backupCount=3)
    name = "article_static"

    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.StaticExtractorPipeline': 300},
        "FEEDS": {"articles.json": {"format": "json"}},
    }

    def __init__(self, data=None):
        self.data = data
        self.article_items = StaticArticleItem()

    def start_requests(self):

        for d in self.data['data']:
            # print(d['article_url'])
            proxy = get_proxy()
            ip = proxy['ip']
            port = proxy['port']
            meta_proxy = f"http://{ip}:{port}"
            headers = {
                "User-Agent": proxy['randomUserAgent']
            }
            meta = {
                "proxy": meta_proxy,
            }
            print(f"------------------------------------ start request  -------------------------------")
            yield scrapy.Request(d['article_url'], self.parse, headers=headers, meta=meta, errback=self.errback_httpbin)
            # yield scrapy.Request(d['article_url'], callback=self.parse, errback=self.errback_httpbin, cb_kwargs={'article':d})
            print("------------------------------------ end start requests ---------------------------")
            logger.info(f"{url} scraped...")
            
        logger.info("Static article scraper done...")

    # def start_requests(self):

    #     for d in self.data['data']:
    #         # print(d['article_url'])
    #         proxy = get_proxy()
    #         ip = proxy['ip']
    #         port = proxy['port']
    #         meta_proxy = f"http://{ip}:{port}"
    #         headers = {
    #             "User-Agent": proxy['randomUserAgent']
    #         }
    #         meta = {
    #             "proxy": meta_proxy,
    #         }
    #         print(f"------------------------------------ start request  -------------------------------")
    #         yield scrapy.Request(d['article_url'], self.parse, headers=headers, meta=meta, errback=self.errback_httpbin, cb_kwargs={'article':d})
    #         # yield scrapy.Request(d['article_url'], callback=self.parse, errback=self.errback_httpbin, cb_kwargs={'article':d})
    #         print("------------------------------------ end start requests ---------------------------")
    #         logger.info(f"{url} scraped...")
            
    #     logger.info("Static article scraper done...")

    def parse(self, response):                                                                                              
        src = StaticSource(response.url)
        text_format = src.text
        news = News(response.url, text_format)
        data = news.generate_data()
        print("--------------------------------------------------------------------------------")
        self.article_items['article_title'] = news.title
        self.article_items['article_section'] = []
        self.article_items['article_authors'] = news.authors
        self.article_items['article_publish_date'] = news.publish_date
        self.article_items['article_images'] = news.images
        self.article_items['article_content'] = news.content
        self.article_items['article_videos'] = news.videos
        self.article_items['article_media_type'] = 'web'
        self.article_items['article_ad_value'] = ""#media.json()['data']['advalue']
        self.article_items['article_pr_value'] = ""#media.json()['data']['prvalue']
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

        
        logger.info(response.request.headers)
        logger.debug(response.request.meta)

        
        yield self.article_items
        print(f"------------------------------------ end parsing ---------------------------")

    # def parse(self, response, article):                                                                                              
    #     src = StaticSource(response.url)
    #     text_format = src.text
    #     news = News(response.url, text_format)
    #     data = news.generate_data()
    #     media = media_value(global_rank=article["website"]["alexa_rankings"]['global'],local_rank=article["website"]["alexa_rankings"]['local'], website_cost=article['website']["website_cost"], article_images=news.images, article_videos=news.videos, article_content=news.content )
    #     print("--------------------------------------------------------------------------------")
    #     self.article_items['article_title'] = news.title
    #     self.article_items['article_section'] = []
    #     self.article_items['article_authors'] = news.authors
    #     self.article_items['article_publish_date'] = news.publish_date
    #     self.article_items['article_images'] = news.images
    #     self.article_items['article_content'] = news.content
    #     self.article_items['article_videos'] = news.videos
    #     self.article_items['article_media_type'] = 'web'
    #     self.article_items['article_ad_value'] = media.json()['data']['advalue']
    #     self.article_items['article_pr_value'] = media.json()['data']['prvalue']
    #     self.article_items['article_language'] = news.language
    #     self.article_items['article_status'] = "Done"
    #     self.article_items['article_error_status'] = None
    #     self.article_items['article_source_from'] = None
    #     self.article_items['keyword'] = []
    #     self.article_items['article_url'] = news.url
    #     self.article_items['date_created'] = datetime.datetime.today().isoformat()
    #     self.article_items['date_updated'] = datetime.datetime.today().isoformat()
    #     self.article_items['created_by'] = "Python Global Scraper"
    #     self.article_items['updated_by'] = "Python Global Scraper"

        
    #     logger.info(response.request.headers)
    #     logger.debug(response.request.meta)

        
    #     yield self.article_items
    #     print(f"------------------------------------ end parsing ---------------------------")
        

    def parse_article(self, response):
        # article_authors = []
        article_title = response.css('h1::text').get()
        article_authors = response.xpath(
            '//a[contains(@class, "e1jsehar0")]/text()').extract_first()
        article_content = "".join(response.xpath(
            "//section[contains(@class, 'meteredContent')]/*/*/p/text()").extract())
        article_published_date = response.xpath(
            '//time/@datetime').extract_first()
        article_url = response.xpath(
            '//meta[contains(@property, "og:url")]/@content').extract_first()
        # article source url
        article_source_url = response.xpath(
            '//meta[contains(@property, "og:url")]/@content').extract_first()
        # article_source_url = response.xpath('//meta[contains(@property, "og:site_name")]/@content').extract_first()
        article_images = response.xpath(
            '//meta[contains(@property, "og:image")]/@content').extract_first()
        website = response.xpath(
            '//meta[contains(@property, "og:type")]/@content').extract_first()

        self.article_items['article_title'] = article_title
        self.article_items['article_authors'] = article_authors
        self.article_items['article_publish_date'] = article_published_date
        # [content.strip() for content in article_content if content.strip() != ""]
        self.article_items['article_content'] = article_content
        self.article_items['article_url'] = article_url
        # ""#article_source_url
        self.article_items['article_source_url'] = article_source_url
        self.article_items['article_images'] = article_images
        self.article_items['article_videos'] = None  # article_videos
        self.article_items['article_ad_value'] = 0  # article_ad_value
        self.article_items['article_pr_value'] = 0  # article_pr_value
        self.article_items['article_status'] = "Done"
        self.article_items['created_by'] = 'Python Global Scraper'
        self.article_items['updated_by'] = 'Python Global Scraper'
        self.article_items['website'] = website

        logger.info(response.request.headers)
        logger.debug(response.headers)
        logger.debug(response.request.meta)

        yield self.article_items

    def errback_httpbin(self, failure):
            # log all failures
            self.logger.error(repr(failure))

            # in case you want to do something special for some errors,
            # you may need the failure's type:

            if failure.check(HttpError):
                # these exceptions come from HttpError spider middleware
                # you can get the non-200 response
                logger.error("HttpError ----------------------------------------------------- HttpError")
                logger.error(f"Link: {failure.url}")
                response = failure.value.response
                self.logger.error('HttpError on %s', response.url)

            elif failure.check(DNSLookupError):
                # this is the original request
                logger.error("DNSLookupError ----------------------------------------------------- DNSLookupError")
                logger.error(f"Link: {failure.url}")
                request = failure.request
                self.logger.error('DNSLookupError on %s', request.url)

            elif failure.check(TimeoutError, TCPTimedOutError):
                logger.error("TimeoutError ----------------------------------------------------- TimeoutError")
                logger.error(f"Link: {failure.url}")
                request = failure.request
                self.logger.error('TimeoutError on %s', request.url)

def get_proxy():
    # url = 'http://falcon.proxyrotator.com:51337/'
    # params = dict(
    # apiKey=f'{API_KEY}&get=true'
    # )
    # try:
    url = f'http://falcon.proxyrotator.com:51337/?apiKey={API_KEY}&get=true&country=PH'
    response = requests.get(url)
    data = json.loads(response.text)
    #     print(f"---------------------------------------- start request proxy rotator {counter}--------------------------------------")
    #     print(data)
    #     print(data['proxy'])
    #     print(data['randomUserAgent'])
    #     print(f"---------------------------------------- end proxy rotator {counter}-------------------------------------------------")
    #     return data
    # except:
    #     logger.error("Skipping. Connnection error or Proxy API key expired.")
    #     data = {}
    #     data['proxy'] = "http://159.89.221.73:3128"
    #     data['randomUserAgent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"

    return data
