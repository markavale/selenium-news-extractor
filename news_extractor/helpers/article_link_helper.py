from .api import api
from decouple import config
# from news_extractor.helpers.utils import get_host_name
# from . utils import get_host_name
# from news_extractor.helpers.utils import get_host_name
import json, requests
from pprint import pprint
from news_extractor.settings import environment, TOKEN, HEADERS

_root_url = config(
    'PRODUCTION_API') if environment else config('DEVELOPMENT_API')

def article_link_articles(**kwargs):
    # _query = {
    #     'article_status': 'Queued'
    # }
    # _fields = {
    #     'article_url': 1
    # }
    req = api(method='POST', url='{}article/custom_query?website_query={}&fields={}&limit={}&offset={}&sort=date_created&sortBy=1'.format(
        _root_url, json.dumps(kwargs['website_query']), json.dumps(kwargs['fields']), kwargs['limit'], kwargs['page_offset']), body=kwargs['body'], headers=kwargs['headers'])
    
    # pprint(req.json())

    # data = list(filter(lambda d:d, req.json()['data']))[0]
    # print(data['_id'])
    # r = requests.get('{}/article/{}'.format(_root_url,data['_id']), headers=HEADERS)
    # pprint(r.json())

    # exit(1)
    return req.json()




# ?website_query = {"path": "website", "select": "website_name website_category", "match": {"website_category": "Blog"}} & limit = 100 & fields = {"article_url": 1}
