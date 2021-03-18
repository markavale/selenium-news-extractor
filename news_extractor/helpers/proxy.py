import requests, json
from news_extractor.settings import API_KEY

def get_proxy():
    # try:
    url = f'http://falcon.proxyrotator.com:51337/?apiKey={API_KEY}&get=true&country=PH'
    response = requests.get(url)
    data = json.loads(response.text)
    return data
