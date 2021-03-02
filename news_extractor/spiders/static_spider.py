import scrapy
from urllib.parse import urlparse
from ..items import StaticArticleItem
from logzero import logfile, logger

class ArticleStaticSpiider(scrapy.Spider):
    logfile("article_static.log", maxBytes=1e6, backupCount=3)
    name = "article_static"
    custom_settings = {
        'ITEM_PIPELINES': {'news_extactor.pipelines.StaticExtractorPipeline': 300},
    }
    
    def __init__(self):
        pass

    def start_requests(self):
        url =""
        yield scrapy.Request(url, self.parse_article)

    def parse_article(self, response):
        pass