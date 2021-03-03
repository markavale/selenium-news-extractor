import scrapy
from urllib.parse import urlparse
from ..items import StaticArticleItem
from logzero import logfile, logger
from lxml.html import fromstring
import requests
from itertools import cycle
import traceback
import json
import os
from news_extractor.settings import API_KEY
# from scrapy.utils.project import get_project_settings

# settings = get_project_settings()

class ArticleStaticSpider(scrapy.Spider):
    logfile("logs/article.log", maxBytes=1e6, backupCount=3)
    name = "article_static"
    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.StaticExtractorPipeline': 300},
    }

    def __init__(self, urls=None):
        self.urls = urls
        self.article_items = StaticArticleItem()

        # #If you are copy pasting proxy ips, put in the list below
        # #proxies = ['121.129.127.209:80', '124.41.215.238:45169', '185.93.3.123:8080', '194.182.64.67:3128', '106.0.38.174:8080', '163.172.175.210:3128', '13.92.196.150:8080']
        # proxies = get_proxies()
        # proxy_pool = cycle(proxies)

        # url = 'https://httpbin.org/ip'
        # for i in range(1,11):
        #     #Get a proxy from the pool
        #     proxy = next(proxy_pool)
        #     print("Request #%d"%i)
        #     try:
        #         response = requests.get(url,proxies={"http": proxy, "https": proxy})
        #         print(response.json())
        #     except:
        #         #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
        #         #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
        #         print("Skipping. Connnection error")

    def start_requests(self):
        # urls = [
        #     "https://www.nytimes.com/2021/02/28/briefing/myanmar-hongkong-vaccine.html",
        #     "https://www.nytimes.com/2021/02/28/podcasts/the-daily/genetics-dna-tests-ancestry.html"
        # # "https://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        # "https://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
        # "https://www.nytimes.com/2021/02/27/nyregion/cuomo-charlotte-bennett-sexual-harassment.html",
        # "https://www.nytimes.com/2021/02/28/nyregion/full-text-of-cuomos-statement-in-response-to-harassment-accusations.html",
        # "https://www.nytimes.com/2021/02/28/health/covid-vaccine-sites.html",
        # "https://www.nytimes.com/2021/02/28/technology/seniors-vaccines-technology.html",
        # "https://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html",
        # "https://www.nytimes.com/2021/02/28/us/politics/supreme-court-voting-rights-act.html",
        # "https://www.nytimes.com/2021/02/28/us/politics/trump-cpac-republicans.html",
        # "https://www.nytimes.com/2021/02/28/us/politics/cpac-straw-poll-2024-presidential-race.html",
        # "https://www.nytimes.com/2021/02/28/us/politics/china-india-hacking-electricity.html",
        # "https://www.nytimes.com/2021/02/28/us/ahmaud-arbery-anniversary.html",
        # "https://www.nytimes.com/2021/02/28/business/media/cable-tv-streaming-discovery.html",
        # "https://www.nytimes.com/2021/02/28/opinion/voter-suppression-us.html",
        # "https://www.nytimes.com/2021/02/28/opinion/business-economics/private-equity-reckoning.html",
        # "https://www.nytimes.com/2021/02/28/opinion/brazil-covid-vaccines.html",
        # "https://www.nytimes.com/2021/02/28/opinion/covid-vaccine-global.html",
        # "https://www.nytimes.com/2021/02/23/opinion/humans-animals-philosophy.html",
        # "https://www.nytimes.com/2021/02/27/opinion/sunday/trump-cuomo-media-covid.html",
        # "https://www.nytimes.com/2021/02/27/opinion/sunday/democrats-media-tanden.html",
        # "https://www.nytimes.com/2021/02/23/opinion/woodcock-fda-opioids.html",
        # "https://www.nytimes.com/2021/02/26/opinion/sunday/coronavirus-alive-dead.html",
        # "https://www.nytimes.com/2021/02/26/opinion/sunday/saudi-arabia-biden-khashoggi.html",
        # "https://www.nytimes.com/2021/02/25/opinion/nursing-crisis-coronavirus.html",
        # "https://www.nytimes.com/2021/02/23/magazine/kazuo-ishiguro-klara.html",
        # "https://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
        # "https://www.nytimes.com/2021/02/25/us/female-con-artists-tori-telfer.html"
        # ]
        # url =""

        for url in self.urls:
            # proxy = get_proxies(self)
            # print(proxy)
            headers = {
                "User-Agent": proxy['randomUserAgent']
            }
            meta = {
                "proxy": proxy['proxy']
            }
            # logger.info(str(proxy))
            yield scrapy.Request(url, self.parse_article)
            # yield scrapy.Request(url, self.parse_article, headers=headers,meta=meta)

            logger.info(f"Link {url} scraped...")
        logger.info("Static article scraper finished...")

    def parse(self, response):
        pass

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


def get_proxies(self):
    print(f"{API_KEY}")
    # url = 'http://falcon.proxyrotator.com:51337/'
    # params = dict(
    # apiKey=f'{API_KEY}&get=true'
    # )
    url = f'http://falcon.proxyrotator.com:51337/?apiKey={API_KEY}&get=true'
    response = requests.get(url)
    data = json.loads(response.text)
    # resp = requests.get(url=url, params=params)
    # data = json.loads(resp.text)
    print(data)
    print(data['proxy'])
    print(data['randomUserAgent'])

    return data








    return json_data
