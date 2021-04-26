from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.options import Options
from scrapy.selector import Selector
from ..items import StaticArticleItem, DynamicArticleItem
# from logzero import logger
import requests,os, datetime, json, scrapy, time
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
from news_extractor.settings import TOKEN, PROXY, CREATED_BY, DEFAULT_PROXY, DEFAULT_USER_AGENT
from news_extractor.scrapy_extractor.news import NewsExtract
from news_extractor.helpers.utils import convert
log = init_log('dynamic_spider')
use_proxy = PROXY

if CREATED_BY == "System":
    source_created_from = "System Link"
else:
    source_created_from = "Global Link"

class ArticleDyamicSpider(scrapy.Spider):
    name = "article_dynamic"
    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.DynamicExtractorPipeline': 300},
    }

    # Init variables that accepts data from main script file
    def __init__(self, data=None):
        self.data = data
        self.article_items = StaticArticleItem()

    # Scrapy Initial Request
    def start_requests(self):
        log.info("Spider started scraping")
        for d in self.data:
            try:
                article_process(d['_id'], "article")  # update status to Process
                is_using_proxy      = d['website']['is_using_proxy']
                needs_https         = d['website']['needs_https']
                needs_endslash      = d['website']['needs_endslash']
                # First: check if needs https or not
                if bool(needs_https):
                    # print("Using https")
                    http_split = d['article_url'].split(':')
                    http_split[0] = "https"
                    d['article_url'] = ":".join(http_split)
                # Second: check if needs endslash
                if bool(needs_endslash):
                    # print("using endslash")
                    d['article_url'] = d['article_url'] + "/"
                # Last: check if url is using proxy
                if bool(is_using_proxy) == True:
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
                        meta['proxy'] = DEFAULT_PROXY
                        headers['User-Agent'] = DEFAULT_USER_AGENT
                    # add proxy and user agent to dict for cb_kwargs
                    d['proxy'] = meta['proxy']
                    d['user_agent'] = headers['User-Agent']
                    
                    yield scrapy.Request(d['article_url'], self.parse, headers=headers, meta=meta, errback=self.errback_httpbin, cb_kwargs={'article': d}, dont_filter=True)
                else:
                    d['proxy'] = "MACHINE's IP"#DEFAULT_PROXY
                    d['user_agent'] = DEFAULT_USER_AGENT
                    yield scrapy.Request(d['article_url'], callback=self.parse, errback=self.errback_httpbin, cb_kwargs={'article': d}, dont_filter=True)

    def parse(self, response):
        print()

    def parse_article(self, response):
        # try:
        # driver = webdriver.Chrome(executable_path='C:/dev/web-driver/chromedriver.exe')#webdriver.Chrome()  # To open a new browser window and navigate it
        # driver = webdriver.Chrome(ChromeDriverManager().install())
        # Use headless option to not open a new browser window
        # options = webdriver.ChromeOptions()
        firefoxOptions = Options()
        firefoxOptions.add_argument("--headless")  # -headless
        firefoxOptions.headless = True
        desired_capabilities = firefoxOptions.to_capabilities()
        driver = webdriver.Firefox(
            executable_path="/home/markanthonyvale/dev/selenium-firefox/drivers/geckodriver", options=firefoxOptions)
        # driver = webdriver.Chrome(executable_path='C:/dev/web-driver/chromedriver.exe', desired_capabilities=desired_capabilities)# chrome_options=options)

        # Getting list of Countries
        # driver.get("https://openaq.org/#/countries")
        driver.get(response.url)
        # fuction for scrollig web driver to the bottom of the page
        use_infinite_scroll_y(driver)
        # Implicit wait
        driver.implicitly_wait(10)

        # Explicit wait
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "story_links")))
        # print(driver.page_source)

        # print(News(response.url, driver.page_source))
        # print("-------------------------------------------")


        scrapy_selector = Selector(text=driver.page_source)

        # Extracting country names
        # countries = scrapy_selector.xpath("//h1[contains(@class, 'card__title')]/a/text()").extract()
        headline = scrapy_selector.xpath(
            "//h1[contains(@class, 'story_links')]/text()").extract()
        # Using Scrapy's yield to store output instead of explicitly writing to a JSON file
        # yield countries
        driver.quit()
        logger.info("Logger dynamic finished......")
        # Using Scrapy's yield to store output instead of explicitly writing to a JSON file
        # yield countries
    # except Exception as e:
        # logger.error(e)
    # finally:
        # logger.info("Logger dynamic finished......")


# class CountriesSpiderSpider(scrapy.Spider):
#     # Initializing log file
#     # logfile("openaq_spider.log", maxBytes=1e6, backupCount=3)
#     name = "countries_spider"
#     allowed_domains = ["toscrape.com"]
#     custom_settings = {
#         'ITEM_PIPELINES': {'news_extractor.pipelines.DynamicExtractorPipeline': 300},
#     }

#     def __init__(self):
#         # self.driver = webdriver.Chrome(executable_path='C:/dev/web-driver/chromedriver.exe')
#         pass

#     # Using a dummy website to start scrapy request
#     def start_requests(self):
#         # url = "http://quotes.toscrape.com"
#         url = "https://www.scmp.com/week-asia/politics/article/3123643/scepticism-over-chinas-sinovac-jab-philippines-rolls-out"
#         yield scrapy.Request(url=url, callback=self.parse_countries)

#     def parse_countries(self, response):
#         # webdriver.Chrome()  # To open a new browser window and navigate it
#         driver = webdriver.Chrome(
#             executable_path='C:/dev/web-driver/chromedriver.exe')
#         # driver = webdriver.Chrome(ChromeDriverManager().install())
#         # Use headless option to not open a new browser window
#         # options = webdriver.ChromeOptions()
#         # options.add_argument("headless")
#         # desired_capabilities = options.to_capabilities()
#         # driver = webdriver.Chrome(desired_capabilities=desired_capabilities)

#         # Getting list of Countries
#         # driver.get("https://openaq.org/#/countries")
#         driver.get(response.url)
#         # fuction for scrollig web driver to the bottom of the page
#         use_infinite_scroll_y(driver)
#         # Implicit wait
#         driver.implicitly_wait(10)

#         # Explicit wait
#         wait = WebDriverWait(driver, 5)
#         wait.until(EC.presence_of_element_located(
#             (By.CLASS_NAME, "info__headline")))
#         # print(driver.page_source)

#         scrapy_selector = Selector(text=driver.page_source)

#         # Extracting country names
#         # countries = scrapy_selector.xpath("//h1[contains(@class, 'card__title')]/a/text()").extract()
#         headline = scrapy_selector.xpath(
#             "//h1[contains(@class, 'info__headline ')]/text()").extract()
#         countries_count = 0
#         # Using Scrapy's yield to store output instead of explicitly writing to a JSON file
#         # yield countries
#         for country in headline:
#             yield {
#                 "headline": country,
#             }
#             countries_count += 1

#         driver.quit()
        # logger.info(f"Total number of Countries in openaq.org: {countries_count}")


def use_infinite_scroll_y(driver):
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
