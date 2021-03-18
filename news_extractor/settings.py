'''
    IMPORTS
'''
from shutil import which
from decouple import config
import os
'''
    END IMPORTS
'''
BOT_NAME = 'news_extractor'

SPIDER_MODULES = ['news_extractor.spiders']
NEWSPIDER_MODULE = 'news_extractor.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
LOG_ENABLED = False
# LOG_LEVEL = 'ERROR' 

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 10
# CONCURRENT_REQUESTS_PER_IP = 10

# CONCURRENT_ITEMS = 200
# RETRY_TIMES = 3

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

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
    'news_extractor.middlewares.InOutBandwithStats': 990,

    # Retry middleware
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 120,

    # 'news_extractor.middlewares.NewsExtractorDownloaderMiddleware': 543,
    # 'news_extractor.middlewares.CustomProxyMiddleware': 350,
    
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
    # 'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 400,
    # 'scrapy.resolver.CachingThreadedResolver',

    #     # rotating IP proxy
    #    'rotating_proxies.middlewares.RotatingProxyMiddleware': 800,
    #    'rotating_proxies.middlewares.BanDetectionMiddleware': 800,

    # scrapy rotating fake user agents
    #    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    #    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,

    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    # 'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    # 'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,

    # SELENIUM
    # 'scrapy_selenium.SeleniumMiddleware': 800,
}
'''
    ##### ROTATING FAKE USER AGENT ######
'''
# FAKEUSERAGENT_PROVIDERS = [
#     'scrapy_fake_useragent.providers.FakeUserAgentProvider',  # this is the first provider we'll try
#     'scrapy_fake_useragent.providers.FakerProvider',  # if FakeUserAgentProvider fails, we'll use faker to generate a user-agent string for us
#     'scrapy_fake_useragent.providers.FixedUserAgentProvider',  # fall back to USER_AGENT value
#     #'new_extractor.providers.CustomProvider'
# ]
# FAKEUSERAGENT_FALLBACK  = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"


'''
    ###### ROTATING PROXY CONF ######
'''
# ROTATING_PROXY_LIST = [
#     'proxy1.com:8000',
#     'proxy2.com:8031',
#     # etc....
# ]
# ROTATING_PROXY_BAN_POLICY = 'tutorial.policy.MyBanPolicy'
# ROTATING_PROXY_LIST_PATH = 'proxy-list.txt'
# Command
# COMMANDS_MODULE = 'tutorial.bash'

### SELENIUM ###

SELENIUM_DRIVER_NAME = 'firefox'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')
# '--headless' if using chrome instead of firefox
SELENIUM_DRIVER_ARGUMENTS = ['-headless']

### AJAX CRAWLER ###
AJAXCRAWL_ENABLED = True
'''
    ###### END ROTATING CONF ######
'''


# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
   'scrapy.extensions.telnet.TelnetConsole': None,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'news_extractor.pipelines.StaticExtractorPipeline': 300,
    'news_extractor.pipelines.TestStaticPipeline': 300,
    'news_extractor.pipelines.GlobalExtractorPipeline': 300,
    'news_extractor.pipelines.DynamicExtractorPipeline': 300
}


CONCURRENT_ITEMS = 100 # => Maximum number of concurrent items (per response) to process in parallel in item pipelines.
CONCURRENT_REQUESTS = 100
CONCURRENT_REQUESTS_PER_DOMAIN = 100
AUTOTHROTTLE_ENABLED = False
DOWNLOAD_TIMEOUT = 120 # 2 Mins
CONNECTION_TIMEOUT = 60 # 1 min
RETRY_ENABLED = False
# TELNETCONSOLE_ENABLED=False

# REDIRECT_ENABLED = False
# REDIRECT_MAX_TIMES = 4

# LOG_LEVEL = 'ERROR'
# The initial download delay
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_TARGET_CONCURRENCY = 50

#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = True

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
# API_KEY = os.environ.get("API_KEY")
API_KEY = config('API_KEY')
environment = config('PRODUCTION', default=bool)
TOKEN = config('TOKEN')
### EMAIL CONFS
# MAIL_HOST = 

process_name = config("PROCESS_NAME")
### PROXY ###
PROXY = config("USE_PROXY", cast=bool)

### TESTING ###
TESTING = config("TESTING", cast=bool)