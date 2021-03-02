import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logzero import logfile, logger
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.selector import Selector
from ..items import DynamicArticleItem
import time

class ArticleDyamicSpider(scrapy.Spider):
    # Initializing log file
    logfile("logs/article_dynamic.log", maxBytes=1e6, backupCount=3)
    name = "article_dynamic"
    # allowed_domains = ["toscrape.com"]
    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.DynamicExtractorPipeline': 300},
    }
    def __init__(self, urls=None):
        
        # self.driver = webdriver.Chrome(executable_path='C:/dev/web-driver/chromedriver.exe')
        # self.items = DynamicArticleItem()
        self.urls = urls
        # self.links = [
        #     "https://www.scmp.com/week-asia/politics/article/3123643/scepticism-over-chinas-sinovac-jab-philippines-rolls-out",
        # ]

    # Using a dummy website to start scrapy request
    def start_requests(self):
        # url = "http://quotes.toscrape.com"
        url = "https://www.scmp.com/week-asia/politics/article/3123643/scepticism-over-chinas-sinovac-jab-philippines-rolls-out"
        for url in self.urls: 
            yield scrapy.Request(url=url, callback=self.parse_article)

    def parse_article(self, response):
    # try:
        # driver = webdriver.Chrome(executable_path='C:/dev/web-driver/chromedriver.exe')#webdriver.Chrome()  # To open a new browser window and navigate it
        # driver = webdriver.Chrome(ChromeDriverManager().install())
        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.headless = True
        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(executable_path='C:/dev/web-driver/chromedriver.exe', desired_capabilities=desired_capabilities)# chrome_options=options)

        # Getting list of Countries
        # driver.get("https://openaq.org/#/countries")
        driver.get(response.url)
        # fuction for scrollig web driver to the bottom of the page
        use_infinite_scroll_y(driver)
        # Implicit wait
        driver.implicitly_wait(10)
        
        # Explicit wait
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "story_links")))
        # print(driver.page_source)
        
        scrapy_selector = Selector(text = driver.page_source)
        
        # Extracting country names
        # countries = scrapy_selector.xpath("//h1[contains(@class, 'card__title')]/a/text()").extract()
        headline = scrapy_selector.xpath("//h1[contains(@class, 'story_links ')]/text()").extract()
        countries_count = 0
        # Using Scrapy's yield to store output instead of explicitly writing to a JSON file
        # yield countries
        for country in headline:
            yield {
                "headline": country,
            }
            countries_count += 1
        logger.info(response.request.headers)
        logger.debug(response.headers)
        logger.debug(response.request.meta)
        driver.quit()
        logger.info("Logger dynamic finished......")
        # countries_count = 0
        # Using Scrapy's yield to store output instead of explicitly writing to a JSON file
        # yield countries
    # except Exception as e:
        # logger.error(e)
    # finally:
        # logger.info("Logger dynamic finished......")

class CountriesSpiderSpider(scrapy.Spider):
    # Initializing log file
    logfile("openaq_spider.log", maxBytes=1e6, backupCount=3)
    name = "countries_spider"
    allowed_domains = ["toscrape.com"]
    custom_settings = {
        'ITEM_PIPELINES': {'news_extractor.pipelines.DynamicExtractorPipeline': 300},
    }
    def __init__(self):
        # self.driver = webdriver.Chrome(executable_path='C:/dev/web-driver/chromedriver.exe')
        pass

    # Using a dummy website to start scrapy request
    def start_requests(self):
        # url = "http://quotes.toscrape.com"
        url = "https://www.scmp.com/week-asia/politics/article/3123643/scepticism-over-chinas-sinovac-jab-philippines-rolls-out"
        yield scrapy.Request(url=url, callback=self.parse_countries)

    def parse_countries(self, response):
        driver = webdriver.Chrome(executable_path='C:/dev/web-driver/chromedriver.exe')#webdriver.Chrome()  # To open a new browser window and navigate it
        # driver = webdriver.Chrome(ChromeDriverManager().install())
        # Use headless option to not open a new browser window
        # options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        # desired_capabilities = options.to_capabilities()
        # driver = webdriver.Chrome(desired_capabilities=desired_capabilities)

        # Getting list of Countries
        # driver.get("https://openaq.org/#/countries")
        driver.get(response.url)
        # fuction for scrollig web driver to the bottom of the page
        use_infinite_scroll_y(driver)
        # Implicit wait
        driver.implicitly_wait(10)
        
        # Explicit wait
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "info__headline")))
        # print(driver.page_source)
        
        scrapy_selector = Selector(text = driver.page_source)
        
        # Extracting country names
        # countries = scrapy_selector.xpath("//h1[contains(@class, 'card__title')]/a/text()").extract()
        headline = scrapy_selector.xpath("//h1[contains(@class, 'info__headline ')]/text()").extract()
        countries_count = 0
        # Using Scrapy's yield to store output instead of explicitly writing to a JSON file
        # yield countries
        for country in headline:
            yield {
                "headline": country,
            }
            countries_count += 1

        driver.quit()
        # logger.info(f"Total number of Countries in openaq.org: {countries_count}")

def use_infinite_scroll_y(driver):
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height