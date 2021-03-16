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
log = init_log('news_extractor')

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
<<<<<<< HEAD
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
=======
        log.info("Spider started scraping")
        log.info("Using Proxy %s" %use_proxy)
        for d in self.data:
            try:
                if process_name == "article_link":
                    article_process(d['_id'], "article")  # update status to Process
                else:
                    article_process(d['_id'], "global-link")  # update status to Process
                if use_proxy == True:
                    print("IM HERE -----------------------------------------------")
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
>>>>>>> production
        src = StaticSource(response.url)
        text_format = src.text
        news = News(response.url, text_format)
        if news.content is None:
            log.error("Content Error on %s", response.url)
        data = news.generate_data()
<<<<<<< HEAD
        

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
=======
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
        self.article_items['download_latency'] = response.request.headers['download_latency']
        
        log.info(response.request.headers)
        log.debug(response.request.meta)
>>>>>>> production

        yield self.article_items

    def errback_httpbin(self, failure):
<<<<<<< HEAD
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
=======
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
>>>>>>> production
