from shutil import which
from decouple import config
import os

BOT_NAME = 'news_extractor'

SPIDER_MODULES = ['news_extractor.spiders']
NEWSPIDER_MODULE = 'news_extractor.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
LOG_ENABLED = config("DEBUG", cast=bool)
# LOG_LEVEL = 'ERROR' 

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 10
# CONCURRENT_REQUESTS_PER_IP = 10

# CONCURRENT_ITEMS = 200
# RETRY_TIMES = 2

# Disable cookies (enabled by default)
COOKIES_ENABLED = False
COOKIES_DEBUG = False
### custom conf ###
# LOG_ENABLED = True
# LOG_LEVEL = 'ERROR'  # to only display errors
# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "DNT": "1",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    #    "x-requested-with": "XMLHttpRequest",
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'news_extractor.middlewares.NewsExtractorSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {

    # Robots.txt logic
    # 'news_extractor.middlewares.NewRobotsTxtMiddleware': 100,
    # 'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None,

    # Bandwidth tracker
    'news_extractor.middlewares.InOutBandwithStats': None,#990,

    # Retry middleware
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 120,

    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware':120,

    # 'news_extractor.middlewares.NewsExtractorDownloaderMiddleware': 543,
    # 'news_extractor.middlewares.CustomProxyMiddleware': 350,
    
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
    # 'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 400,
    # 'scrapy.resolver.CachingThreadedResolver': 400, # testing

    # SELENIUM
    # 'scrapy_selenium.SeleniumMiddleware',
}

### SELENIUM ###

SELENIUM_DRIVER_NAME = 'firefox'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')
# '--headless' if using chrome instead of firefox
SELENIUM_DRIVER_ARGUMENTS = ['-headless']

### AJAX CRAWLER ###
AJAXCRAWL_ENABLED = True


# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'news_extractor.pipelines.StaticExtractorPipeline': 300,
    'news_extractor.pipelines.TestStaticPipeline': 300,
    'news_extractor.pipelines.GlobalExtractorPipeline': 300,
    'news_extractor.pipelines.DynamicExtractorPipeline': 300
}

CONCURRENT_ITEMS = 200 # 100 # => Maximum number of concurrent items (per response) to process in parallel in item pipelines.
CONCURRENT_REQUESTS = 200
CONCURRENT_REQUESTS_PER_DOMAIN = 200 #100
AUTOTHROTTLE_ENABLED = True # it should be false to scrape
DOWNLOAD_TIMEOUT = 60 #120 # 2 Mins
CONNECTION_TIMEOUT = 60 # 1 min
RETRY_ENABLED = False
# TELNETCONSOLE_ENABLED=False

# Redirect must enabled to parse all google links
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 1 # It must always be set to 1 to avoid redirecting in paywall page.

# LOG_LEVEL = 'ERROR'
# The initial download delay
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_TARGET_CONCURRENCY = 50
    
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 30
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 150
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = config("DEBUG", cast=bool)

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


'''
        ENV VARIABLES
'''

API_KEY = config('API_KEY')
environment = config('PRODUCTION', cast=bool)
TOKEN = config('TOKEN')

# EMAIL CONFS

# [ ARTICLES - REQUEST VARIABLES ]
CREATED_BY = config("CREATED_BY")
PAGE_OFFSET = config("PAGE_OFFSET")
LIMIT = config("PAGE_LIMIT", cast=int)

# [ HEADERS ]
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {}'.format(config("TOKEN"))
}

# [ PROXY ]
PROXY = config("USE_PROXY", cast=bool)

# [ TESTING ]
TESTING                     = config("TESTING", cast=bool)

# [ ADMIN TOKEN ]
ADMIN_TOKEN                 = config("ADMIN_TOKEN")
PRODUCTION_ADMIN_API        = config("PRODUCTION_ADMIN_API")
DEVELOPMENT_ADMIN_API       = config("DEVELOPMENT_ADMIN_API")
USE_ADMIN_API               = config("USE_ADMIN_API", cast=bool)


# [ DEFAULT PROXY AND HEADERS ]
DEFAULT_PROXY               = 'http://103.105.212.106:53281'
DEFAULT_USER_AGENT          = 'Mozilla/5.0 (Windows NT 6.0 rv:21.0) Gecko/20100101 Firefox/21.0'