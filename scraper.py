from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os, math, json, time, random, scrapy
# from news_extractor.helpers.api import system_articles_data
import concurrent.futures
from pprint import pprint
# from news_extractor.helpers.api import total_spider_api_call, spider_log, get_all_processing_articles, update_process_to_queued, __get_google_links
from news_extractor.helpers.utils import (convert, __total_data_and_workers, delete_all_logs,
                                          save_all_logs)
from decouple import config
from news_extractor.helpers import article_link_articles, global_link_articles, google_link_check_fqdn, admin_api
from news_extractor.settings import TESTING, TOKEN, PRODUCTION_ADMIN_API, DEVELOPMENT_ADMIN_API, environment
from logs.main_log import init_log
log = init_log("news_extractor")


###
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {}'.format(TOKEN)
}

info_path = os.path.abspath('/tmp//logs/news_extractor/app.log')
debug_path = os.path.abspath('/tmp//logs/news_extractor/debug.log')
error_path = os.path.abspath('/tmp//logs/news_extractor/errors.log')

# info_path = os.path.abspath('{}/logs/info.log'.format(os.getcwd()))
# debug_path = os.path.abspath('{}/logs/debug.log'.format(os.getcwd()))
# error_path = os.path.abspath('{}/logs/error.log'.format(os.getcwd()))
# json_path = os.path.abspath('{}/article_spider.json'.format(os.getcwd()))
if TESTING:
    # json_path = os.path.abspath('/home/markanthonyvale/dev/media_meter/news-extractor/test_article.json')
    json_path = os.path.abspath('{}/test_article.json'.format(os.getcwd()))
else:
    # json_path = os.path.abspath('/home/markanthonyvale/dev/media_meter/news-extractor/article_spider.json')
    json_path = os.path.abspath('{}/article_spider.json'.format(os.getcwd()))


def spider(data):
    # INITIALIZATION
    spiders = []
    # CHUNK SPIDER
    divisible_n = math.ceil(len(data) / 3)
    spider_data = [data[i:i + divisible_n]
                   for i in range(0, len(data), divisible_n)]

    # SPIDER CRAWLER
    process = CrawlerProcess(get_project_settings())
    if TESTING:
        for spider in spider_data:
            #item = process.crawl('test_spider', spider)
            spiders.append({
                'thread_crawlers':[{"url": data, "article_id": "1231231"} for data in spider] # FIX
            })
    else:
        print("Total thread spider(s): {}".format(len(spider_data)))
        log.info("Total thread spider(s) {}".format(len(spider_data)))
        for spider in spider_data:
            item = process.crawl('article_static', spider)
            spiders.append({
                'thread_crawlers': {'crawlers': spider}
            })
    log.info("Spider links: {}".format(len(spider_data)))
    process.start()
    return spiders


def main(system_data, WORKERS):
    total_links = len(system_data)
    divisible_n = math.ceil(len(system_data) / WORKERS)
    data = [system_data[i:i + divisible_n]
            for i in range(0, len(system_data), divisible_n)]
    MAX_WORKERS = min(len(data), WORKERS)
    print("Total links: {} || Total spider/worker: {} ".format(total_links,
                                                               MAX_WORKERS))  # POST this to system
    log.info(
        "Total links: {} || Total spider/worker: {} ".format(total_links, MAX_WORKERS))

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future = [executor.submit(spider, obj) for obj in data]
    spiders = [obj.result() for obj in future]
    total_data, total_workers = __total_data_and_workers(system_data, MAX_WORKERS)
    return total_data, total_workers, spiders


def get_system_data(**kwargs):
    if kwargs['process_name'] == "article_link":
        website_category = config("WEBSITE_CATEGORY")
        _query = {
            'article_status': 'Queued'
        }
        _fields = {
            'article_url': 1
        }

        data = article_link_articles(
            headers=headers, query=_query, fields=_fields, limit=kwargs['limit'])
        print(data)
        # data = list(filter(lambda d:d['website']['website_category'] == website_category, d['data']))
        return data
    else:
        _query = {
            'original_url': {'$ne': None}
        }

        def append_article_url(data):
            data["article_url"] = data['original_url']
            resp = google_link_check_fqdn(
                article_url=data['article_url'], headers=headers)
            data['website'] = resp
            return data
        d = global_link_articles(
            headers=headers, query=_query, limit=kwargs['limit'])
        data = list(map(append_article_url, d['data']))
        return data


if __name__ == "__main__":
    system_links = list(map(lambda x: x.strip(), open(
        'test-articles.txt').read().split('\n'))) * 250
    process_name = config("PROCESS_NAME")
    limit = config("PAGE_LIMIT", cast=int)
    if not TESTING:
        data = get_system_data(process_name=process_name, limit=limit)
        try:
            print("Getting data from system")
            system_data = data
            if len(system_data) == 0:
                print("No Data")
                log.info('No data')
                exit(0)
        except ConnectionError as e:
            print(e)
            log.error(e)
        except TimeoutError as e:
            print(e)
            log.error(e)
        except Exception as e:
            print(e)
            log.error(e)
    else:
        print("Testing MODE")
        system_data = system_links
    WORKERS = os.cpu_count() - 2
    t1 = time.perf_counter()
    total_data, total_workers, spiders = main(system_data, WORKERS)
    t2 = time.perf_counter()
    elapsed_seconds = round(t2-t1, 2)
    time_finish = convert(elapsed_seconds)
    log.info("Finished scraping in %s", time_finish)
    print(f'Finish in {time_finish}')

    # FILE PATH
    # SAVE LOGS IN MEMORY
    info_log, debug_log, error_log, json_log = save_all_logs(
        info_path, debug_path, error_path, json_path)

    crawler_items = []

    for item in json_log:
        crawler_items.append(
            {
                "article_id": item['article_id'],
                "article_url": item['article_url'],
                "download_latency": item['download_latency'],
                "collection_name": item['collection_name'],
                "article_status": item['article_status'],
                "article_error_status": item['article_error_status'],
                "http_error": item['http_err'],
                "dns_error": item['dns_err'],
                "timeout_error": item['timeout_err'],
                "base_error": item['base_err'],
                "skip_url": item['skip_url'],
            }
        )

    scraper = {}
    scraper['data'] = total_data
    scraper['workers'] = total_workers
    scraper['spiders'] = spiders
    scraper['info_log'] = info_log
    scraper['error_log'] = error_log
    scraper['json_log'] = ""#json_log
    scraper['crawler_items'] = ""#""crawler_items # FIX 
    scraper["time_finished"] = time_finish
    scraper['is_finished'] = True

    _url = PRODUCTION_ADMIN_API if environment else DEVELOPMENT_ADMIN_API

    # resp = admin_api(method="POST", url="{}add-crawler-items/".format(_url), body=scraper["crawler_items"])
    # print(resp)
    pprint(scraper)
    with open("test_data.json", 'w') as f:
        f.write(str(scraper))

    # for json in json_log:
    #     print(json['article_title'])

    # delete_all_logs(info_path, debug_path, error_path, json_path)
