import scrapy
from urllib.parse import urlparse
from ..items import StaticArticleItem
from logzero import logfile, logger


class ArticleStaticSpider(scrapy.Spider):
    logfile("article_static.log", maxBytes=1e6, backupCount=3)
    name = "article_static"
    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.StaticExtractorPipeline': 300},
    }

    def __init__(self, urls=None):
        self.urls = urls
        self.article_items = StaticArticleItem()

    def start_requests(self):
        urls = [
            "https://www.nytimes.com/2021/02/28/briefing/myanmar-hongkong-vaccine.html",
            "https://www.nytimes.com/2021/02/28/podcasts/the-daily/genetics-dna-tests-ancestry.html"
            # "https://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
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
        ]
        # url =""
        
        for url in urls:
            yield scrapy.Request(url, self.parse_article)
        logger.info("Static article scraper finished...")

    def parse_article(self, response):
        # article_authors = []
        article_title = response.css('h1::text').get()
        article_authors = response.xpath(
            '//a[contains(@class, "e1jsehar0")]/text()').extract_first()
        # article_content = response.xpath(
        #     response.xpath("//section[contains(@class, 'meteredContent')]/*/*/p/text()").extract()
        #     )
        # '//section[contains(@class, "Content")]/*').css("::text").extract_first()
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

        # split_link = article_url.split("/")
        # article_source_url = split_link[2]

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

        yield self.article_items
