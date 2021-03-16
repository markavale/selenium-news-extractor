import os
import json
import requests
from dotenv import load_dotenv
from news_extractor.settings import environment, TOKEN
import datetime
# from pprint import pprint
load_dotenv()


_article_url = os.getenv(
    'PRODUCTION_API') if environment else os.getenv('DEVELOPMENT_API')

# TODO: pass => article url
'''
@ Pass params => {
    article_url

}
'''
# MEDIA VALUES FOR PR AND AD VALUES


def media_value(**kwargs):
    headers = {
        'Content-Type': 'application/json'
    }

    _url = os.getenv('PRODUCTION_LAMBDA_API') if environment else os.getenv(
        'DEVELOPMENT_LAMBDA_API')
    _query = {
        'global': kwargs['global_rank'],
        'local': kwargs['local_rank'],
        'website_cost': kwargs['website_cost'],
        'videos': list(kwargs['article_videos']),
        'images': list(kwargs['article_images']),
        'text': kwargs['article_content']
    }
    req = requests.request('POST', '{}article/media_values'.format(_url),
                           data=json.dumps(_query), headers=headers)
    return req

# POST REQ FOR URLS
# REQUEST FOR ARTICLES


def system_articles_data():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        'article_status': 'Queued'
    }
    _fields = {
        'article_url': 1
    }
    req = requests.request('POST', '{}article/custom_query?fields={}&limit={}'.format(
        _article_url, json.dumps(_fields), 3500), data=json.dumps(_query), headers=headers)
    return req.json()  # json(req.json(), indent=4)

### UPDATE ALL SKIP URLS TO QUEUED STATUS ###
def get_all_processing_articles():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        'article_status': 'Processing'
    }
    req = requests.request('POST', '{}article/custom_query'.format(
        _article_url), data=json.dumps(_query), headers=headers)
    return req.json()


def update_process_to_queued(process_article): # review
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    # count_status = requests.request('POST', '{}article/custom_query'.format(
    #     _url), data=json.dumps(_query), headers=headers).json()['data']

    for data in process_article:
        _query = {
            "article_status": {"$in": ["Queued", "Processing", "Done", "Error"]},
            "article_url": data["article_url"]
        }
        count_status = requests.request('POST', '{}article/count_custom_query'.format(
        _url), data=json.dumps(_query), headers=headers).json()['data']

        if count_status > 0:
            req = requests.request('DELETE', '{}article/{}'.format(_url,
                                                                   data['_id']), data=json.dumps(_query), headers=headers).json()['data']
        else:
            req = requests.request('PUT', '{}article/{}'.format(_url,
                                                                data['_id']), data=json.dumps({"article_status": "Queued", "date_updated": datetime.datetime.today().isoformat()}), headers=headers).json()['data']


### GET ARTICELS PER STATUS ###
def get_status_done_articles():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        'article_status': 'Done'
    }
    req = requests.request('POST', '{}article/custom_query'.format(
        _article_url), data=json.dumps(_query), headers=headers)
    return req.json()


def get_status_error_articles():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        'article_status': 'Error'
    }
    req = requests.request('POST', '{}article/custom_query'.format(
        _article_url), data=json.dumps(_query), headers=headers)
    return req.json()


def get_status_queued_articles():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        'article_status': 'Queued'
    }
    req = requests.request('POST', '{}article/custom_query'.format(
        _article_url), data=json.dumps(_query), headers=headers)
    return req.json()

### CRUD OP ARTICLE ###


def __article_process(article_id):
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
    req = requests.request('PUT', '{}article/{}'.format(_url,
                                                        article_id), data=json.dumps(_query), headers=headers)
    return req


def __article_error(article_id, error_status):
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
    req = requests.request('PUT', '{}article/{}'.format(_url,
                                                        article_id), data=json.dumps(_query), headers=headers)
    return req


def __article_success(article):
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
    req = requests.request('PUT', '{}article/{}'.format(_url,
                                                        article['_id']), data=json.dumps(_query), headers=headers)
    return req


# def total_spider_api_call(total_links, workers):
#     print("Total :: {} || {}".format(total_links, workers))


# def spider_log(spiders):
#     # print("")
#     [print(spider) for spider in spiders]
#     print("")
