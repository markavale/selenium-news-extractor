from scrapy.crawler import CrawlerProcess, CrawlerRunner
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
from news_extractor.settings import TESTING, TOKEN, PRODUCTION_ADMIN_API, DEVELOPMENT_ADMIN_API, environment, CREATED_BY, PAGE_OFFSET
from logs.main_log import init_log
# from apscheduler.schedulers.twisted import TwistedScheduler
# from apscheduler.schedulers.Scheduler import Scheduler
# from apscheduler.schedulers import Scheduler
log = init_log("news_extractor")

# scheduler = TwistedScheduler()

# scheduler = TwistedScheduler()

# HEADERS
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
            # scheduler.add_job(
            #     process.crawl,
            #     "cron",
            #     args=[spider],
            #     minute=1
            # )
            # scheduler.add_job(process.crawl, 'interval', args=['test_spider' ,spider], seconds=10)
            process.crawl('test_spider', spider)
            spiders.append({
                'thread_crawlers': [{"url": data, "article_id": "1231231"} for data in spider]
            })
            # scheduler.start()
    else:
        print("Total thread spider(s): {}".format(len(spider_data)))
        log.info("Total thread spider(s) {}".format(len(spider_data)))
        for spider in spider_data:
            # scheduler.add_job(process.crawl, 'interval', args=['article_static' ,spider], seconds=15)
            item = process.crawl('article_static', spider)
            spiders.append({
                'thread_crawlers': [{'url': data['article_url'], "article_id": data['_id']} for data in spider]
            })
            # scheduler.start()
    log.info("Spider links: {}".format(len(spider_data)))
    process.start() # Do not stop reactor after spider closes

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
    total_data, total_workers = __total_data_and_workers(
        system_data, MAX_WORKERS)
    return total_data, total_workers, spiders


def get_system_data(**kwargs):
    article_website_query = {
        "path": "website",
        "select": "-main_sections -section_filter -article_filter -selectors -sub_sections -embedded_sections -code_snippet"
    }
    body_query = {
        'article_status': 'Queued',
        'created_by': CREATED_BY
    }
    _fields = {
        'article_url': 1,
    }
    data = article_link_articles(
        headers=headers, body=body_query, fields=_fields, limit=kwargs['limit'], website_query=article_website_query, page_offset=PAGE_OFFSET)
    return data

def run():
    system_links = list(map(lambda x: x.strip(), open(
        'test-articles.txt').read().split('\n')))
    limit = config("PAGE_LIMIT", cast=int)
    if not TESTING:
        data = get_system_data(limit=limit)
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
        print(item)
        crawler_items.append(
            {
                "article_id": item['article_id'],
                "article_url": item['article_url'],
                "download_latency": item['download_latency'],
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
    # scraper['crawler_items'] = crawler_items
    scraper["time_finished"] = time_finish
    scraper['is_finished'] = True

    crl_items = {}
    crl_items['crawler_items'] = crawler_items

    _url = PRODUCTION_ADMIN_API if environment else DEVELOPMENT_ADMIN_API

    print("SENDING JSON LOG DATA SET TO ADMIN SCRAPER API")
    resp = admin_api(method="POST", url="{}crawler-items/".format(_url), body=crl_items["crawler_items"])
    print(resp)
    print("SENDING SCRAPER OBJECT TO ADMIN SCRAPER API")
    resp2 = admin_api(method="POST", url="{}process-scraper/".format(_url), body=scraper)
    print(resp2)
    # pprint(scraper)
    # with open("test_data.json", 'w') as f:
    #     f.write(str(scraper))

    # for json in json_log:
    #     print(json['article_title'])

    # delete_all_logs(info_path, debug_path, error_path, json_path)

if __name__ == "__main__":
    run()
    # add_s = scheduler.add_job(run, 'interval', seconds=2)
    # scheduler.start()
    # print(add_s)
    # run()
    # scheduler = Scheduler()
    # print("Started scheduling")
    # scheduler.start()
    # print("Added new job")
    # job = scheduler.add_interval_job(run, seconds=15)
    # print(job)
    
