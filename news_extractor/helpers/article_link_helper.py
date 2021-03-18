from .api import api
from decouple import config
from .utils import get_host_name
import json
from news_extractor.settings import environment, TOKEN
_root_url = config(
    'PRODUCTION_API') if environment else config('DEVELOPMENT_API')
website_category = config("WEBSITE_CATEGORY")

def article_link_articles(**kwargs):
    # _query = {
    #     'article_status': 'Queued'
    # }
    # _fields = {
    #     'article_url': 1
    # }
    website_query = {
        "path": "website",
        "match": {"website_category": website_category}
    }
    print(website_query)
    # req = api(method='POST', url='{}article/custom_query?fields={}&limit={}'.format(
    #     _root_url, json.dumps(kwargs['fields']), kwargs['limit']), body=kwargs['query'], headers=kwargs['headers'])
    req = api(method='POST', url='{}article/custom_query?website_query={}&fields={}&limit={}'.format(
        _root_url, json.dumps(website_query), json.dumps(kwargs['fields']), kwargs['limit']), body=kwargs['query'], headers=kwargs['headers'])
    return req.json()


# ?website_query = {"path": "website", "select": "website_name website_category", "match": {"website_category": "Blog"}} & limit = 100 & fields = {"article_url": 1}
