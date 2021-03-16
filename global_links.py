from news_extractor.helpers.global_api import __get_google_links, __google_link_check_fqdn
from news_extractor.helpers.utils import get_host_name
from pprint import pprint
from urllib.parse import urlparse

data = __get_google_links()

data['data'].append({"original_url": "https://www.nytimes.com/"})
print()
articles = list(map(lambda x:__google_link_check_fqdn("https://www.nytimess.com/"), data['data']))

articles_pop = articles.pop()
# print(articles_pop['data'])

# pprint(articles['data'])
print(articles_pop)
print(articles_pop.get('_id'))
_id = dict(articles_pop)
print(_id)