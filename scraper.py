from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os, math, json, time, random, scrapy
import concurrent.futures
from pprint import pprint
from news_extractor.helpers.utils import (
    convert, delete_all_logs, save_all_logs, get_system_data)
from news_extractor.helpers import global_link_articles, google_link_check_fqdn, admin_api
from news_extractor.settings import (TESTING, TOKEN, PRODUCTION_ADMIN_API, DEVELOPMENT_ADMIN_API, environment, CREATED_BY, PAGE_OFFSET,
                                     LIMIT)
from logs.main_log import init_log
log = init_log("news_extractor")
# HEADERS
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {}'.format(TOKEN)
}

info_path = os.path.abspath('/tmp/logs/news_extractor/app.log')
debug_path = os.path.abspath('/tmp/logs/news_extractor/debug.log')
error_path = os.path.abspath('/tmp/logs/news_extractor/errors.log')

if TESTING:
    json_path = os.path.abspath('{}/test_article.json'.format(os.getcwd()))
else:
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
            process.crawl('test_spider', spider)
            spiders.append({
                'thread_crawlers': [{"url": data, "article_id": "605abf51d7ca3f780d2163f4"} for data in spider]
            })
    else:
        print("Total thread spider(s): {}".format(len(spider_data)))
        log.info("Total thread spider(s) {}".format(len(spider_data)))
        for spider in spider_data:
            item = process.crawl('article_static', spider)
            spiders.append({
                'thread_crawlers': [{'url': data['article_url'], "article_id": data['_id']} for data in spider]
            })
    log.info("Spider links: {}".format(len(spider_data)))
    process.start()  # Do not stop reactor after spider closes

    return spiders


def main(system_data, WORKERS):
    # Computation for divisible number for chunking URL(s)
    divisible_n = math.ceil(len(system_data) / WORKERS)
    data = [system_data[i:i + divisible_n]
            for i in range(0, len(system_data), divisible_n)]  # Chunking URL(s)
    # Instansiating MAX WORKERS based on the lower number between length of data and defined WORKERS
    MAX_WORKERS = min(len(data), WORKERS)

    # LOGGING ---------------------------
    print("Total URL(s): {}".format(len(system_data)))
    print("Total Spider(s) / Worker(s): {}".format(MAX_WORKERS))
    log.info("Total URL(s): {} ".format(len(system_data)))
    log.info("Total Spider(s) / Worker(s): {} ".format(MAX_WORKERS))

    # MULTI PROCESSING OF SPIDER FUNCTION
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future = [executor.submit(spider, obj) for obj in data]

    # Instansiating the results of multi processing spider function
    spiders = [obj.result() for obj in future]
    return len(system_data), MAX_WORKERS, spiders


def run():
    system_links = list(map(lambda x: x.strip(), open(
            'test-articles.txt').read().split('\n')))
    # Cheking first if for testing or production
    if not TESTING:
        data = get_system_data(limit=LIMIT)
        try:
            print("Getting data from system")
            system_data = data['data']
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
        try:
            crawler_items.append(
                {
                    "article_id": item['article_id'],
                    "article_url": item['article_url'],
                    "fqdn": item['article_source_url'],
                    "download_latency": item['download_latency'],
                    "article_status": item['article_status'],
                    "article_error_status": item['article_error_status'],
                    "http_error": item['http_err'],
                    "dns_error": item['dns_err'],
                    "timeout_error": item['timeout_err'],
                    "base_error": item['base_err'],
                    "skip_url": item['skip_url']
                }
            )
        except Exception as e:
            print(e)

    scraper = {}
    scraper['data'] = total_data
    scraper['workers'] = total_workers
    scraper['spiders'] = spiders
    scraper['info_log'] = info_log
    scraper['error_log'] = error_log
    scraper["time_finished"] = time_finish
    scraper['is_finished'] = True

    crl_items = {}
    crl_items['crawler_items'] = crawler_items

    file = open('scraper_object.json', 'w')
    file.write(str(scraper))

    _url = PRODUCTION_ADMIN_API if environment else DEVELOPMENT_ADMIN_API
    if not TESTING:
        print("SENDING JSON LOG DATA SET TO ADMIN SCRAPER API")
        resp = admin_api(
            method="POST", url="{}crawler-items/".format(_url), body=crl_items["crawler_items"])
        print(resp)
        print("SENDING SCRAPER OBJECT TO ADMIN SCRAPER API")
        resp2 = admin_api(
            method="POST", url="{}process-scraper/".format(_url), body=scraper)
        print(resp2)
    # pprint(scraper)
    # delete_all_logs(info_path, debug_path, error_path, json_path)


if __name__ == "__main__":
    run()
