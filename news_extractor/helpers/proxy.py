import requests, json
from news_extractor.settings import API_KEY

def get_proxy():
    # try:
    url = f'http://falcon.proxyrotator.com:51337/?apiKey={API_KEY}&get=true&country=PH'
    response = requests.get(url)
    data = json.loads(response.text)
    print(f"---------------------------------------- start request proxy rotator --------------------------------------")
    # ip = data['ip']
    # port = data['port']
    # meta_proxy = f"http://{ip}:{port}"
    # headers = {
    #     "User-Agent": data['randomUserAgent']
    # }
    # meta = {
    #     "proxy": meta_proxy,
    # }
    print(f"---------------------------------------- end proxy rotator -------------------------------------------------")
    return data
    # return meta, headers
    # except Exception as e:
    #     headers = {
    #         "User-Agent": 'Mozilla/5.0 (Windows NT 6.0 rv:21.0) Gecko/20100101 Firefox/21.0'
    #     }
    #     meta = {
    #         "proxy": 'http://103.105.212.106:53281'
    #     }
    #     return meta, headers