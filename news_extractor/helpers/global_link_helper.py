from .api import api
from decouple import config
from .utils import get_host_name
import json
from news_extractor.settings import environment, TOKEN
_root_url = config(
    'PRODUCTION_API') if environment else config('DEVELOPMENT_API')

def global_link_articles(**kwargs):
    a = api(method="POST", url="{}global-link/custom_query?limit={}".format(_root_url,kwargs['limit']),
            body=kwargs['query'], headers=kwargs['headers'])
    return a.json()


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
    req = api(method="POST", url='{}web/'.format(_root_url),
              body=_params, headers=headers)
    return req.json()


def google_link_check_fqdn(**kwargs):
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Authorization': 'Bearer {}'.format(TOKEN)
    # }
    _clean_url = get_host_name(kwargs['article_url'])
    _query = {
        "fqdn": _clean_url
    }
    fields = {
        "alexa_rankings": 1,
        "website_cost": 1,
        "fqdn": 1,
        "website_category": 1
    }
    req = api(method='POST',
              url='{}/web/custom_query?fields={}'.format(
                  _root_url, json.dumps(fields)),
              body=_query, headers=kwargs['headers'])
    domain = req.json()
    if len(domain['data']) != 0:
        clean_data = domain['data'].pop()
        clean_data["article_url"] = kwargs['article_url']
        return clean_data
    return add_new_website(fqdn=_clean_url)
