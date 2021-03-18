import requests, datetime, json
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

    req = api(method='PUT', url='{}{}/{}'.format(_root_url,collection_name,
                                           article_id), body=_query, headers=headers)
    return req.json()


def article_error(article_id, error_status, process_name):
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

    if process_name == "article_link":
        req = api(method='PUT', url='{}article/{}'.format(_root_url,
                                               article_id), body=_query, headers=headers)
    else:
        req = api(method='POST', url='{}article'.format(_root_url),
                  body=_query, headers=headers)
    return req.json()


def article_success(article, process_name):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        article
    }

    if process_name == "article_link":
        req = api(method='PUT', url='{}article/{}'.format(_root_url,
                                               article['article_id']), body=_query, headers=headers)
    else:
        req = api(method='POST', url='{}article'.format(_root_url),
                  body=_query, headers=headers)
        print(req.json())
        update_query = {
            "status": "Done",
            'date_updated': article['date_updated'],
            'updated_by': "Python Global Scraper"
        }
        print(article)
        log.debug(article)
        print(update_query)
        print(article['_id'])
        log.debug(article['_id'])
        log.debug(update_query)
        # try:
        req_update = api(method='PUT', url='{}global-link/{}'.format(_root_url,
                                            article['_id']), body=update_query, headers=headers)
        # ex
    return req.json()
