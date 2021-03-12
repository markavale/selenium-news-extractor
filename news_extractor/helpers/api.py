import os, json, requests
from dotenv import load_dotenv

# from pprint import pprint
load_dotenv()

environment = bool(os.getenv('PRODUCTION'))

_article_url = os.getenv('PRODUCTION_API') if environment else os.getenv('DEVELOPMENT_API') 

# POST REQ FOR URLS
def endpoints():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(os.getenv('TOKEN'))
    }
    
    # _url = os.getenv('PRODUCTION_API') if environment else os.getenv('DEVELOPMENT_API') 
    _query = {
        #'status': 'Queued'
        'article_status': 'Queued'
    }
    _fields = {
        'article_url': 1
    }
    req = requests.request('POST','{}article/custom_query?fields={}&limit={}'.format(_article_url,json.dumps(_fields),5000), data=json.dumps(_query), headers=headers)
    return req.json()#json(req.json(), indent=4)

    # return headers, _url, _query 


# TODO: pass => article url
'''
@ Pass params => {
    article_url

}
'''
def media_value(**kwargs):
    headers = {
        'Content-Type': 'application/json'
    }
    
    _url = os.getenv('PRODUCTION_LAMBDA_API') if environment else os.getenv('DEVELOPMENT_LAMBDA_API') 
    _query = {
        'global': kwargs['global_rank'],
        'local': kwargs['local_rank'],
        'website_cost': kwargs['website_cost'],
        'videos': list(kwargs['article_videos']),
        'images': list(kwargs['article_images']),
        'text': kwargs['article_content']
    }
    print(_query, _url)
    req = requests.request('POST','{}article/media_values'.format(_url), data=json.dumps(_query), headers=headers)
    return req#json.dumps(req.json(), indent=4)-----------------------------------------------MEDIA VALUE")

def __google_link_check_fqdn(domain_name):
    _url = os.getenv('PRODUCTION_LAMBDA_API') if environment else os.getenv('DEVELOPMENT_LAMBDA_API')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(os.getenv('TOKEN'))
    }
    _query = {
        'fqdn': domain_name
    }
    req = requests.request('POST', '{}/web/count_custiom_query'.format(_url), data=json.dumps(_query), headers=headers)

def __article_process(article_id):
    print(article_id)
    '''
    @ Required params
    article id => unique
    article_status => Process (Default)
    '''
    print(article_response)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(os.getenv('TOKEN'))
    }
    _query = {
        'article_status': 'Process'#,
        # ''
    }
    req = requests.request('PUT','{}article/{}'.format(_url, article_id), data=json.dumps(_query), headers=headers)
    return req

def __article_error(article_id, error_status):
    '''
    @ Required params
    article id => unique
    article_response => Error message
    article_status => Error (Default)
    '''
    print(article_response)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(os.getenv('TOKEN'))
    }
    _query = {
        'article_status': 'Error',
        'article_error_status': error_status
    }
    req = requests.request('PUT','{}article/{}'.format(_url, article_id), data=json.dumps(_query), headers=headers)
    return req

def __article_success(article_id, article):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(os.getenv('TOKEN'))
    }
    _query = {
        article
    }
    req = requests.request('PUT','{}article/{}'.format(_url, article_id), data=json.dumps(_query), headers=headers)
    return req

def api_call(article):
    pass


def total_spider_api_call(total_links, workers):
    print("Total :: {} || {}".format(total_links, workers))

def spider_log(spiders):
    [print(spider) for spider in spiders]
    print("")