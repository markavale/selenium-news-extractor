import json, datetime, json, requests
from news_extractor.settings import environment, ADMIN_TOKEN, PRODUCTION_ADMIN_API, DEVELOPMENT_ADMIN_API

_url = PRODUCTION_ADMIN_API if environment else DEVELOPMENT_ADMIN_API

def admin_api(**kwargs):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token "+ADMIN_TOKEN
    }
    r = requests.request(
        method=kwargs['method'],
        url=kwargs['url'],
        headers=headers,
        data=json.dumps(kwargs['body'])
    )
    return r

