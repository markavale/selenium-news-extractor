import os, json, requests, datetime
from dotenv import load_dotenv
from news_extractor.settings import environment, TOKEN
from news_extractor.helpers.utils import get_host_name
# from pprint import pprint

load_dotenv()

_root_url = os.getenv(
    'PRODUCTION_API') if environment else os.getenv('DEVELOPMENT_API')


def add_new_website(**kwargs):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _clean_url = kwargs['fqdn']
    _params = {
        "fqdn": _clean_url,
        "website_name": _clean_url.split(".")[0].title(),
        "website_cost": 300,
        "website_category": "News",
        "country": "Unknown",
        "country_code": "NoC",
        "website_url": "http://"+_clean_url,
        "alexa_rankings": {
            "global": 0,
            "local": 0
        }
    }
    # return _params
    req = requests.request('POST', '{}web/'.format(_root_url),
                           data=json.dumps(_params), headers=headers)
    return req.json()

def __google_link_check_fqdn(article_url):
    _clean_url = get_host_name(article_url)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        "fqdn": _clean_url
    }
    fields = {
        "alexa_rankings": 1,
        "website_cost": 1
    }
    req = requests.request('POST', '{}/web/custom_query?fields={}'.format(_root_url, json.dumps(fields)),
                           data=json.dumps(_query), headers=headers)
    domain = req.json()
    if len(domain['data']) != 0:
        clean_data = domain['data'].pop()
        clean_data["article_url"] = article_url
        return clean_data
    return add_new_website(fqdn=_clean_url)

def __get_google_links():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
        "original_url": {
            "$ne": None
        }
    }
    fields = {"original_url": 1, "_id": 0}
    req = requests.request('POST', '{}/global-link/custom_query?fields={}'.format(
        _root_url, json.dumps(fields)), data=json.dumps(_query), headers=headers)

    return req.json()

def __google_links_process():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
    }
    req = requests.request('POST', '{}/global-link/count_custiom_query'.format(
        _root_url), data=json.dumps(_query), headers=headers)
    return req

def __google_links_error():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
    }
    req = requests.request('POST', '{}/global-link/count_custiom_query'.format(
        _root_url), data=json.dumps(_query), headers=headers)
    return req

def __google_links_success():
    _url = os.getenv('PRODUCTION_LAMBDA_API') if environment else os.getenv(
        'DEVELOPMENT_LAMBDA_API')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
    }
    req = requests.request('POST', '{}/global-link/count_custiom_query'.format(
        _url), data=json.dumps(_query), headers=headers)
    return req

def __google_():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
    _query = {
    }
    req = requests.request('POST', '{}/global-link/count_custiom_query'.format(
        _root_url), data=json.dumps(_query), headers=headers)
