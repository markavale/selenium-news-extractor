from .api import api
from decouple import config
from .utils import get_host_name
import json

environment = config("PRODUCTION", cast=bool)
_root_url = config(
    'PRODUCTION_API') if environment else config('DEVELOPMENT_API')
TOKEN = config("TOKEN")
def article_link_articles(**kwargs):
    # _query = {
    #     'article_status': 'Queued'
    # }
    # _fields = {
    #     'article_url': 1
    # }
    req = api(method='POST', url='{}article/custom_query?fields={}&limit={}'.format(
        _root_url, json.dumps(kwargs['fields']), kwargs['limit']), body=kwargs['query'], headers=kwargs['headers'])
    return req.json()
