from .api import api
from decouple import config
from .utils import get_host_name
import json

environment = config("PRODUCTION", bool)
_root_url = config(
    'PRODUCTION_LAMBDA_API') if environment else config('DEVELOPMENT_LAMBDA_API')
TOKEN = config("TOKEN")

def media_value(**kwargs):
    headers = {
        'Content-Type': 'application/json'
    }

    _query = {
        'global': kwargs['global_rank'],
        'local': kwargs['local_rank'],
        'website_cost': kwargs['website_cost'],
        'videos': list(kwargs['article_videos']),
        'images': list(kwargs['article_images']),
        'text': kwargs['article_content']
    }
    req = api(method="POST", url='{}article/media_values'.format(_root_url),
                           body=_query, headers=headers)
    return req
