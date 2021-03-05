import os, json, requests
from dotenv import load_dotenv
# from pprint import pprint
load_dotenv()

environment = bool(os.getenv('PRODUCTION'))

# POST REQ FOR URLS
def endpoints():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(os.getenv('TOKEN'))
    }
    
    _url = os.getenv('PRODUCTION_API') if environment else os.getenv('DEVELOPMENT_API') 
    _query = {
        #'status': 'Queued'
        'article_status': 'Queued'
    }
    _fields = {
        'article_url': 1
    }
    req = requests.request('POST','{}article/custom_query?fields={}&limit={}'.format(_url,json.dumps(_fields),1), data=json.dumps(_query), headers=headers)
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
    return req#json.dumps(req.json(), indent=4)
    
    


