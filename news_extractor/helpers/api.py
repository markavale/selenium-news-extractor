import requests
import datetime
import json
from decouple import config
from logs.main_log import init_log
from news_extractor.settings import environment, TOKEN
log = init_log("api")

_root_url = config(
    'PRODUCTION_API') if environment else config('DEVELOPMENT_API')


def api(**kwargs):
    r = requests.request(
        method=kwargs['method'],
        url=kwargs['url'],
        headers=kwargs['headers'],
        data=json.dumps(kwargs['body'])
    )
    return r


def article_process(article_id, collection_name):
    '''
    @ Required params
    article id => unique
    article_status => Process (Default)
    '''
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        'article_status': 'Processing',
        'date_updated': datetime.datetime.today().isoformat()
    }

    req = api(method='PUT', url='{}{}/{}'.format(_root_url, collection_name,
                                                 article_id), body=_query, headers=headers)
    return req.json()


def article_error(article_id, error_status):
    '''
    @ Required params
    article id => unique
    article_response => Error message
    article_status => Error (Default)
    '''
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        'article_status': 'Error',
        'article_error_status': error_status,
        'date_updated': datetime.datetime.today().isoformat()
    }
    req = api(method='PUT', url='{}article/{}'.format(_root_url,
                                                      article_id), body=_query, headers=headers)
    return req.json()


def article_success(article):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        article
    }

    req = api(method='PUT', url='{}article/{}'.format(_root_url,
                                                      article['article_id']), body=_query, headers=headers)
    return req.json()
