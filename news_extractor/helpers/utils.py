import time, os, datetime, json
from news_extractor.settings import HEADERS, CREATED_BY, PAGE_OFFSET
# from news_extractor.helpers import article_link_articles
# from news_extractor.helpers import article_link_articles
# from . import article_link_articles
from news_extractor.helpers.article_link_helper import article_link_articles
from urllib.parse import urlparse

def time_in_range(start, end, x):
    """Return False if x is in the range [start, end]"""

    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def get_host_name(url):
    parsed_uri = urlparse(str(url))
    host_name = '{uri.netloc}'.format(uri=parsed_uri)
    clear_url = host_name.replace(r'www.', '').strip()
    return clear_url


### MAIN SCRAPER FUNCTION ###
def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)

def delete_all_logs(info_path, debug_path, error_path, json_path):
    with open(str(info_path), 'w') as info_file, open(str(debug_path), 'w') as debug_file, open(str(error_path), 'w') as erorr_file, open(str(json_path), 'w') as json_file:
        info_file.write("")
        debug_file.write("")
        erorr_file.write("")
        json_file.write("")

def save_all_logs(info_path, debug_path, error_path, json_path):
    info_log    = []
    debug_log   = []
    error_log   = []
    json_log    = []
    # try:
    with open(str(info_path), 'r') as info_file, open(str(debug_path), 'r') as debug_file, open(str(error_path), 'r') as erorr_file, open(str(json_path)) as json_file:
        [info_log.append(line) for line in info_file]
        [debug_log.append(line) for line in debug_file]
        [error_log.append(line) for line in erorr_file]
        [json_log.append(json.loads(line)) for line in json_file]
    # except FileNotFoundError:
    #     with open(str(info_path), 'r') as info_file, open(str(debug_path), 'r') as debug_file, open(str(error_path), 'r') as erorr_file, open(str(json_path)) as json_file:
    #         [info_log.append(line) for line in info_file]
    #         [debug_log.append(line) for line in debug_file]
    #         [error_log.append(line) for line in erorr_file]
    #         [json_log.append(json.loads(line)) for line in json_file]
    return info_log, debug_log, error_log, json_log


'''
    HELPER FUNCTIONS FOR scraper.py
'''
def get_system_data(**kwargs):
    article_website_query = {
        "path": "website",
        "select": "-main_sections -section_filter -article_filter -selectors -sub_sections -embedded_sections -code_snippet"
    }
    body_query = {
        # "article_source_url": "manilanews.net"
        'article_status': 'Queued',
        'created_by': CREATED_BY    
        }
    _fields = {
        'article_url': 1
    }
    data = article_link_articles(
        headers=HEADERS, body=body_query, fields=_fields, limit=kwargs['limit'], website_query=article_website_query, page_offset=PAGE_OFFSET)
    return data