import requests, datetime, json
from decouple import config


environment = config("PRODUCTION", cast=bool)
_root_url = config(
    'PRODUCTION_API') if environment else config('DEVELOPMENT_API')
TOKEN = config("TOKEN")

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
        'article_title': article['article_title'],
        'article_section': article['article_section'],
        'article_authors': article['article_authors'],
        'article_publish_date': article['article_publish_date'],
        'article_images': article['article_images'],
        'article_content': article['article_content'],
        'article_videos': article['article_videos'],
        'article_media_type': article['article_media_type'],
        'article_ad_value': article['article_ad_value'],
        'article_pr_value': article['article_pr_value'],
        'article_language': article['article_language'],
        'article_status': article['article_status'],
        'article_error_status': article['article_error_status'],
        'article_source_from': article['article_source_from'],
        'keyword': article['keyword'],
        'article_url': article['article_url'],
        'date_created': article['date_created'],
        'date_updated': article['date_updated'],
        'created_by': article['created_by'],
        'updated_by': article['updated_by']
    }

    if process_name == "article_link":
        req = api(method='PUT', url='{}article/{}'.format(_root_url,
                                               article['article_id']), body=_query, headers=headers)
    else:
        req = api(method='POST', url='{}article'.format(_root_url),
                  body=_query, headers=headers)
        req_update = api(method='PUT', url='{}google-link/{}'.format(_root_url,
                                               article['_id']), body=_query, headers=headers)
    return req.json()
