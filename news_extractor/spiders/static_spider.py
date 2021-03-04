import scrapy
from ..items import StaticArticleItem
from logzero import logfile, logger
import requests
import json
import os
from news_extractor.settings import API_KEY
from ..article_contents.news import News
from ..article_contents.source.static import StaticSource

# from urllib.parse import urlparse
# from lxml.html import fromstring
# from itertools import cycle
# import traceback

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


class ArticleStaticSpider(scrapy.Spider):
    logfile("server.log", maxBytes=1e6, backupCount=3)
    name = "article_static"
    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.StaticExtractorPipeline': 300},
    }

    def __init__(self, urls=None):
        self.urls = urls
        self.article_items = StaticArticleItem()

    def start_requests(self):
        counter = 0
        urls = [
            "https://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html"
        ]
        for url in self.urls:
            counter +=1
            proxy = get_proxies(counter)
            ip = proxy['ip']
            port = proxy['port']
            # print(proxy)
            meta_proxy = f"https://{ip}:{port}"
            headers = {
                "User-Agent": proxy['randomUserAgent']
            }
            meta = {
                "proxy": meta_proxy
            }
            # logger.info(str(proxy))
            print(f"------------------------------------ start request {counter} -------------------------------")
            # yield scrapy.Request(url, self.parse, errback=self.errback_httpbin)
            yield scrapy.Request(url, callback=self.parse, headers=headers,meta=meta, errback=self.errback_httpbin)
            print("------------------------------------ end start requests ---------------------------")
            logger.info(f"{url} scraped...")
        print("------------------------------------------------------------- DONE SCRAPING -------------------------------------------------------------")
        logger.info("Static article scraper done...")

    def parse(self, response):            
        print(f"------------------------------------ start parsing ---------------------------")                                                                                              
        src = StaticSource(response.url)
        text_format = src.text
        news = News(response.url, text_format)
        data = news.generate_data()
        

        logger.info(response.request.headers)
        logger.debug(response.request.meta)

        print(json.dumps(data, indent=4))
        print(f"------------------------------------ end parsing ---------------------------")
        # yield data

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
                response = failure.value.response
                self.logger.error('HttpError on %s', response.url)

            elif failure.check(DNSLookupError):
                # this is the original request
                request = failure.request
                self.logger.error('DNSLookupError on %s', request.url)

            elif failure.check(TimeoutError, TCPTimedOutError):
                request = failure.request
                self.logger.error('TimeoutError on %s', request.url)

def get_proxies(counter):
    print(f"{API_KEY}")
    # url = 'http://falcon.proxyrotator.com:51337/'
    # params = dict(
    # apiKey=f'{API_KEY}&get=true'
    # )
    try:
        url = f'http://falcon.proxyrotator.com:51337/?apiKey={API_KEY}&get=true&country=PH'
        response = requests.get(url)
        data = json.loads(response.text)
        # resp = requests.get(url=url, params=params)
        # data = json.loads(resp.text)
        print(f"---------------------------------------- start request proxy rotator {counter}--------------------------------------")
        print(data)
        print(data['proxy'])
        print(data['randomUserAgent'])
        print(f"---------------------------------------- end proxy rotator {counter}-------------------------------------------------")
    except:
        # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
        # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
        logger.error("Skipping. Connnection error or Proxy API key expired.")
        data = {}
        data['proxy'] = "http://159.89.221.73:3128"
        data['randomUserAgent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"

    return data
