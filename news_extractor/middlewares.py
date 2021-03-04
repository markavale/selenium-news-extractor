# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import base64
from urllib.parse import unquote, urlunparse
from urllib.request import getproxies, proxy_bypass, _parse_proxy

from scrapy.exceptions import NotConfigured
from scrapy.utils.httpobj import urlparse_cached
from scrapy.utils.python import to_bytes

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import requests, json


from urllib import robotparser
from scrapy.downloadermiddlewares.robotstxt import RobotsTxtMiddleware
from scrapy.utils.python import to_native_str

from news_extractor.settings import API_KEY

class NewsExtractorSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class NewsExtractorDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    
    source = f'http://falcon.proxyrotator.com:51337/?apiKey={API_KEY}&get=true&country=PH'

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        return None
        
        
        # ignore if proxy is already set
        
        # if 'proxy' in request.meta:
        #     if request.meta['proxy'] is None:
        #         return
        #     # extract credentials if present
        #     creds, proxy_url = self._get_proxy(request.meta['proxy'], '')
        #     request.meta['proxy'] = proxy_url
        #     if creds and not request.headers.get('Proxy-Authorization'):
        #         request.headers['Proxy-Authorization'] = b'Basic ' + creds
        #     return
        # elif not self.proxies:
        #     return

        # parsed = urlparse_cached(request)
        # scheme = parsed.scheme

        # # 'no_proxy' is only supported by http schemes
        # if scheme in ('http', 'https') and proxy_bypass(parsed.hostname):
        #     return

        # if scheme in self.proxies:
        #     self._set_proxy(request, scheme)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

# class CustomProxyMiddleware(object):
#     def process_request(self, request, spider):
#         url = f'http://falcon.proxyrotator.com:51337/?apiKey={API_KEY}&get=true&country=PH'
#         response = requests.get(url)
#         data = json.loads(resp.text)
#         request.meta['proxy'] = data['proxy']
#         request.headers['User-Agent'] = data['randomUserAgent']

# class NewRobotsTxtMiddleware(RobotsTxtMiddleware):
#     def _parse_robots(self, response, netloc):
#         self.crawler.stats.inc_value('robotstxt/response_count')
#         self.crawler.stats.inc_value(
#             'robotstxt/response_status_count/{}'.format(response.status))
#         rp = robotparser.RobotFileParser(response.url)
#         body = ''
#         if hasattr(response, 'text'):
#             body = response.text
#         else:  # last effort try
#             try:
#                 body = response.body.decode('utf-8')
#             except UnicodeDecodeError:
#                 # If we found garbage, disregard it:,
#                 # but keep the lookup cached (in self._parsers)
#                 # Running rp.parse() will set rp state from
#                 # 'disallow all' to 'allow any'.
#                 self.crawler.stats.inc_value('robotstxt/unicode_error_count')
#         # stdlib's robotparser expects native 'str' ;
#         # with unicode input, non-ASCII encoded bytes decoding fails in Python2

#         # Start change: Remove the offending items here.
#         lines = to_native_str(body).splitlines()
#         lines.remove('Disallow: /en/')
#         rp.parse(lines)
#         # End of change.

#         rp_dfd = self._parsers[netloc]
#         self._parsers[netloc] = rp
#         rp_dfd.callback(rp)

# def get_proxies():
#     print(f"{API_KEY}")
#     # url = 'http://falcon.proxyrotator.com:51337/'
#     # params = dict(
#     # apiKey=f'{API_KEY}&get=true'
#     # )
#     # try:
#     url = f'http://falcon.proxyrotator.com:51337/?apiKey={API_KEY}&get=true'
#     response = requests.get(url)
#     data = json.loads(response.text)
#     # resp = requests.get(url=url, params=params)
#     # data = json.loads(resp.text)
#     print(data)
#     print(data['proxy'])
#     print(data['randomUserAgent'])
#     # except:
#     #     # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
#     #     # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
#     #     logger.error("Skipping. Connnection error or Proxy API key expired.")
#     #     data = {}
#     #     data['proxy'] = "159.89.221.73:3128"
#     #     data['randomUserAgent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36"

#     return data