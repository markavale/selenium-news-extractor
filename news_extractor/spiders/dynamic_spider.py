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

class CountriesSpiderSpider(scrapy.Spider):
    # Initializing log file
    logfile("article_dynamic.log", maxBytes=1e6, backupCount=3)
    name = "article_dynamic"
    # allowed_domains = ["toscrape.com"]
    custom_settings = {
        'ITEM_PIPELINES': {'new_extractor.pipelines.DynamicExtractorPipeline': 300},
    }
    def __init__(self, links=None):
        self.driver = webdriver.Chrome(executable_path='C:/dev/web-driver/chromedriver.exe')
        # self.links = [
        #     "https://www.scmp.com/week-asia/politics/article/3123643/scepticism-over-chinas-sinovac-jab-philippines-rolls-out",
        # ]

    # Using a dummy website to start scrapy request
    def start_requests(self):
        # url = "http://quotes.toscrape.com"
        url = "https://www.scmp.com/week-asia/politics/article/3123643/scepticism-over-chinas-sinovac-jab-philippines-rolls-out"
        yield scrapy.Request(url=url, callback=self.parse_article)

    def parse_aticle(self, response):
        driver = webdriver.Chrome(executable_path='C:/dev/web-driver/chromedriver.exe')#webdriver.Chrome()  # To open a new browser window and navigate it
        
        # driver = webdriver.Chrome(ChromeDriverManager().install())
        # Use headless option to not open a new browser window
        # options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        # desired_capabilities = options.to_capabilities()
        # driver = webdriver.Chrome(desired_capabilities=desired_capabilities)

        # Getting list of Countries
        self.driver.get(response.url)
        # fuction for scrollig web driver to the bottom of the page
        use_infinite_scroll_y(self.driver)
        # Implicit wait
        self.driver.implicitly_wait(10)
        
        # Explicit wait
        wait = WebDriverWait(self.driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "info__headline")))
        # print(driver.page_source)
        
        ### Get page source when selenium renders javascript render and use parsing with scrapy
        scrapy_selector = Selector(text = self.driver.page_source)
        
        headline = scrapy_selector.xpath("//h1[contains(@class, 'info__headline ')]/text()").extract()
        countries_count = 0
        # Using Scrapy's yield to store output instead of explicitly writing to a JSON file
        # yield countries

        self.driver.quit()
        logger.info(f"Logger dynamic..")

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