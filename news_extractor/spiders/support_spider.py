# import scrapy
# from ..items import StaticArticleItem
# from logzero import logfile, logger
# import requests, datetime, json, os
# from news_extractor.settings import API_KEY
# from ..article_contents.news import News
# from ..article_contents.source.static import StaticSource

# from decouple import config
# # from urllib.parse import urlparse
# # from lxml.html import fromstring
# # from itertools import cycle
# # import traceback


# from scrapy.spidermiddlewares.httperror import HttpError
# from twisted.internet.error import DNSLookupError
# from twisted.internet.error import TimeoutError, TCPTimedOutError
# from ..helpers.api import  __article_process, __article_error# __article_success
# from ..helpers.media_value_helper import media_value
# from ..helpers.proxy import get_proxy
# import csv



# class SupportSpider(scrapy.Spider):
#     name = "support_spider"
#     logfile("server.log", maxBytes=1e6, backupCount=3)
#     custom_settings = {
#         'ITEM_PIPELINES': {'news_extractor.pipelines.StaticExtractorPipeline': 300},
#         "FEEDS": {"edit_article.csv": {"format": "csv"}},
#     }

#     def __init__(self, urls=None):
#         self.urls = urls
#         self.article_items = StaticArticleItem()
#         # with open("NBA__M2comms___Leagues__xlsx.xlsx", "r") as f:
#         #     csv_reader = csv.DictReader(f)
#         #     self.csv_links = (csv_reader)

#     def start_requests(self):
#         urls = [
#             "https://www.rappler.com/sports/nba/lebron-james-lauds-steph-curry-first-stint-teammates-all-star-2021",
#             "http://www.rappler.com/sports/nba/assessing-g-league-ignite-prospects",
#             "http://www.rappler.com/sports/nba/game-updates-team-lebron-durant-all-star-2021",
#             "http://www.rappler.com/sports/nba/jeremy-lin-comes-up-big-santa-cruz-warriors-g-league-victory-march-6-2021",
#             "http://www.rappler.com/sports/nba/best-kicks-2021-all-star-game",
#             "http://www.rappler.com/sports/nba/adam-silver-vaccines-not-mandatory-logo-not-changing",
#             "http://www.rappler.com/sports/nba/adam-silver-no-international-games-next-season-full-arenas-in-plan",
#             "http://www.rappler.com/sports/nba/jeremy-lin-santa-cruz-warriors-g-league-advance-semifinals-march-8-2021",
#             "http://www.rappler.com/sports/nba/zero-positive-covid-19-tests-all-star-weekend-march-2021",
#             "http://www.rappler.com/sports/nba/all-star-slam-dunk-contest-results-winner-march-2021",
#             "http://www.rappler.com/sports/nba/three-point-champion-steph-curry-lot-to-accomplish-nothing-prove",
#             "http://www.rappler.com/sports/nba/brooklyn-nets-sign-blake-griffin",
#             "http://www.rappler.com/sports/nba/g-league-ignite-select-austin-spurs-march-6-2021"
#         ]
#         # proxy = get_proxy()
#         # ip = proxy['ip']
#         # port = proxy['port']
#         # meta_proxy = f"http://{ip}:{port}"
#         # headers = {
#         #     "User-Agent": proxy['randomUserAgent']
#         # }
#         # meta = {
#         #     "proxy": meta_proxy,
#         # }
#         for url in urls:
#             try:
#                 print(f"------------------------------------ start request  -------------------------------")
#                 # yield scrapy.Request(url, callback=self.parse, meta=meta, headers=headers, errback=self.errback_httpbin, dont_filter=True)
#                 yield scrapy.Request(url, callback=self.parse, errback=self.errback_httpbin, dont_filter=True)
#                 logger.debug(f"Link scraped {url}")
#                 print(f"------------------------------------ end start request  -------------------------------")
#             except:
#                 logger.error("SKip url: %s", url)

#     def parse(self, response):                                                                                              
#         src = StaticSource(response.url)
#         text_format = src.text
#         news = News(response.url, text_format)
#         # data = news.generate_data()
#         print("--------------------------------------------------------------------------------")
#         self.article_items['article_title'] = news.title
#         self.article_items['article_section'] = []
#         self.article_items['article_authors'] = news.authors
#         self.article_items['article_publish_date'] = news.publish_date
#         self.article_items['article_images'] = news.images
#         self.article_items['article_content'] = news.content
#         self.article_items['article_videos'] = news.videos
#         self.article_items['article_media_type'] = 'web'
#         self.article_items['article_ad_value'] = ""#
#         self.article_items['article_pr_value'] = ""#
#         self.article_items['article_language'] = news.language
#         self.article_items['article_status'] = "Done"
#         self.article_items['article_error_status'] = None
#         self.article_items['article_source_from'] = None
#         self.article_items['keyword'] = []
#         self.article_items['article_url'] = news.url
#         self.article_items['date_created'] = datetime.datetime.today().isoformat()
#         self.article_items['date_updated'] = datetime.datetime.today().isoformat()
#         self.article_items['created_by'] = "Python Global Scraper"
#         self.article_items['updated_by'] = "Python Global Scraper"

#         logger.info(response.request.headers)
#         logger.debug(response.request.meta)
        
#         yield self.article_items
#         print(f"------------------------------------ end parsing ---------------------------")

#     def errback_httpbin(self, failure):
#         # log all failures
#         self.logger.error(repr(failure))

#         if failure.check(HttpError):
#             # these exceptions come from HttpError spider middleware
#             # you can get the non-200 response
#             response = failure.value.response
#             logger.error("HttpError on %s", request.url)
#             self.logger.error('HttpError on %s', response.url)

#         elif failure.check(DNSLookupError):
#             # this is the original request
#             request = failure.request
#             logger.error("TimeoutError on %s", request.url)
#             self.logger.error('DNSLookupError on %s', request.url)

#         elif failure.check(TimeoutError, TCPTimedOutError):
#             request = failure.request
#             logger.error("TimeoutError on %s", request.url)
#             self.logger.error('TimeoutError on %s', request.url)
#         else:
#             logger.error("Error on %s", request.url)



































