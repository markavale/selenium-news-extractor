from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy import signals
import os, math, json, time
# from news_extractor.helpers.api import system_articles_data
import concurrent.futures
from pprint import pprint
# from news_extractor.helpers.api import total_spider_api_call, spider_log, get_all_processing_articles, update_process_to_queued, __get_google_links
from logs.main_log import init_log
from news_extractor.pipelines import StaticExtractorPipeline
from news_extractor.helpers.utils import (convert,get_total_spider,__total_data_and_workers,__admin_scraper_post, delete_all_logs,
                save_all_logs)
import random
__articles_items = StaticExtractorPipeline()
from decouple import config
from news_extractor.helpers import article_link_articles, global_link_articles, google_link_check_fqdn

log = init_log("news_extractor")

from decouple import config
TOKEN = config("TOKEN")
##
headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(TOKEN)
    }
info_path = os.path.abspath('/tmp/logs/news_extractor/app.log')
debug_path = os.path.abspath('/tmp/logs/news_extractor/debug.log')
error_path = os.path.abspath('/tmp/logs/news_extractor/errors.log')
json_path = os.path.abspath('/home/markanthonyvale/dev/media_meter/news-extractor/article_spider.json')


def spider(data):
    # INITIALIZATION
    article_items = []
    spiders = []
    crawlers = []
    crawler = {}

    # CHUNK SPIDER
    divisible_n = math.ceil(len(data) / 3)
    spider_data = [data[i:i + divisible_n]
                   for i in range(0, len(data), divisible_n)]

    # SPIDER CRAWLER
    process = CrawlerProcess(get_project_settings())
    for spider in spider_data:
        # process.crawl('test_spider', spider)
        process.crawl('article_static', spider)
        spiders.append({
            'thread_crawlers': {'crawlers': spider}#len(spider)
        })
    log.info("Spider links: {}".format(len(spider_data)))

    # print(__articles_items.items)

    # for item in __articles_items:
    #     print(item)


    # spider_log(spiders)

    process.start()
  
    # print(article_items)
    # for item in article_items:
    #     print(item)
    return spiders


def main(system_data, WORKERS):
    total_links = len(system_data)
    print("MAIN PROCESS")
    divisible_n = math.ceil(len(system_data) / WORKERS)
    data = [system_data[i:i + divisible_n]
            for i in range(0, len(system_data), divisible_n)]
    MAX_WORKERS = min(len(data), WORKERS)
    print("Total links: {} || Total spider/worker: {} ".format(total_links, MAX_WORKERS)) # POST this to system
    log.info("Total links: {} || Total spider/worker: {} ".format(total_links, MAX_WORKERS))
    print("")

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future = [executor.submit(spider, obj) for obj in data]
    spiders =  [obj.result() for obj in future]

    total_data, total_workers = __total_data_and_workers(system_links, MAX_WORKERS)

    return total_data, total_workers, spiders

def update_all_status_processing(data):
    if len(data) != 0:
        log.info("Updating all %s from Processing status to Queued", len(data))
        for obj in data:
            update_process_to_queued(data)   
        print("{} updated".format(len(data)))

    else:
        print("{} articles".format(len(data)))
        log.info("No processing article(s).")

if __name__ == "__main__":
    delete_all_logs(info_path, debug_path, error_path, json_path)
    process_name = config("PROCESS_NAME")
    limit = config("PAGE_LIMIT", cast=int)
    website_category = config("WEBSITE_CATEGORY")
    if process_name == "article_link":
        _query = {
        'article_status': 'Queued'
        }
        _fields = {
            'article_url': 1
        }
        
        d = article_link_articles(headers=headers, query=_query, fields=_fields, limit=limit)
        # data = list(map(lambda x:x, d['data']))
        data = list(filter(lambda d:d['website']['website_category'] == website_category, d['data']))
    else:
        _query = {
        'original_url': {'$ne':None}
        }
        def append_article_url(data):
            data["article_url"] = data['original_url']
            resp = google_link_check_fqdn(article_url=data['article_url'], headers=headers)
            data['website'] = resp
            return data
        d = global_link_articles(headers=headers, query=_query, limit=limit)
        data = list(map(append_article_url, d['data']))

    system_links = [
        "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        # 'https://newsinfo.inquirer.net/1407028/manila-to-place-6-barangays-under-4-day-lockdown',
        "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
        # "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
        "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html"

        # "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        # "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
        # "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
        # "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html",

        # "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        # "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
        # "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
        # "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html",

        # "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        # "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
        # "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
        # "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html",

        # "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        # "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
        # "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
        # "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html",

        # "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        # "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
        # "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
        # "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html",

        # "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        # "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
        # "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
        # "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html",

        # "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        # "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
        # "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
        # "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html"

        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-covid-19-misinformation-vaccines-conspiracy-theories-antisemitism/",
        # "https://thenextweb.com/plugged/2021/03/10/nothings-first-product-concept-1-design-bullshit-analysis/",
        # "https://thenextweb.com/plugged/2021/03/09/chrome-os-10th-birthday-phone-hub/",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-covid-19-misinformation-vaccines-conspiracy-theories-antisemitism/",

        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-covid-19-misinformation-vaccines-conspiracy-theories-antisemitism/",
        # "https://thenextweb.com/plugged/2021/03/10/nothings-first-product-concept-1-design-bullshit-analysis/",
        # "https://thenextweb.com/plugged/2021/03/09/chrome-os-10th-bi/"
        # "http://headtopics.com/my/queen-vows-to-address-harry-and-meghan-racism-claims-new-straits-times-19079486",
        # "http://markanthonyvale.herokuapp.com/"
        # "covid-19-misinformation-vaccines-conspiracy-theories-antisemitism/",

        # "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html",
        # "https://thenextweb.com/plugged/2021/03/09/chrome-os-10th-birthday-phone-hub/",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-",
        # "https://thenextweb.com/neural/2021/03/09/instagram-algorithm-recommends-"
        # "https://www.gmanetwork.com/news/lifestyle/familyandrelationships/779216/marjorie-barretto-says-daughter-julia-is-at-her-happiest-on-24th-birthday/story/"
    ] * 1
    try:
        while True:
            print("Getting data from system")
            system_data = data
            if len(system_data) == 0:
                log.info("{} data available. Sleeping....".format(len(system_data)))
                time.sleep(random.randint(3,10))
            else:
                break        
    except ConnectionError as e:
        print(e)
        log.error(e)
    except TimeoutError as e:
        print(e)
        log.error(e)
    except Exception as e:
        print(e)
        log.error(e)
    # print(len(system_links))
    WORKERS = os.cpu_count() - 2
    t1 = time.perf_counter()
    total_data, total_workers, spiders = main(system_data, WORKERS)
    t2 = time.perf_counter()
    elapsed_seconds = round(t2-t1, 2)
    time_finish = convert(elapsed_seconds)
    log.info("Finished scraping in %s", time_finish)
    print(f'Finish in {time_finish}')

    # print("-------------------------------")
    # print(total_data, total_workers)
    # print("-------------------------------")
    # print("spiders")
    # print("-------------------------------")

    # FILE PATH
    

    # SAVE LOGS IN MEMORY
    info_log, debug_log, error_log, json_log = save_all_logs(info_path, debug_path, error_path, json_path)

    # process_articles = get_all_processing_articles()
    # if len(process_articles) > 0:
    #     update_all_status_processing(process_articles['data'])
        

    # pprint(info_log)
    # for article_item in json_log:
    #     print(article_item.get('download_latency'))


    # scraper = {}
    # scraper['data'] = total_data
    # scraper['workers'] = total_workers
    # scraper['spiders'] = spiders
    # scraper['info_log'] = info_log
    # scraper['debug_log'] = debug_log
    # scraper['error_log'] = error_log
    # scraper['json_log'] = json_log
    # scraper['is_finished'] = True

    # pprint(scraper)
    # for spider in scraper['spiders']:
    #     print("")
    #     pprint(spider)
    #     print("")

    # time.sleep(1.5)

    # delete_all_logs(info_path, debug_path, error_path, json_path)
    
    
    