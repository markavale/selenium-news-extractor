from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os, math, json, time
from news_extractor.helpers.api import endpoints
import concurrent.futures
from pprint import pprint
from news_extractor.helpers.api import total_spider_api_call, spider_log
from logs.main_log import init_log

log = init_log("news_extractor")


# def write_log_spider():
#     with open("spider_spwn.txt", "a") as spider_file:
#         spider_file.write("\n")
#         spider_file.write(f'test')
#         spider_file.write("\n")

#         spider_file.write("\n")


def spider(data):
    spiders = []
    divisible_n = math.ceil(len(data) / 3)
    spider_data = [data[i:i + divisible_n]
                   for i in range(0, len(data), divisible_n)]

    # print("Total spider : {} || Total links per spider: {}".format(len(data), len(spider_data))) # POST this data to system
    # pprint("")
    # for url in spider_data:
    #     print(url)
    # pprint("")

    process = CrawlerProcess(get_project_settings())
    for spider in spider_data:
        process.crawl('test_spider', data)
        spiders.append({
            'Spider data': len(spider)
        })
    log.info("Spider links: {}".format(len(spider_data)))
    spider_log(spiders)

        # process.crawl('test_spider', data)
    # [process.crawl('article_static', data) for data in spider_data]
    # [process.crawl('test_spider', data) for data in spider_data]
    process.start()
    # process.crawl('article_static', data=data)


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
        [executor.submit(spider, obj) for obj in data]

    total_spider_api_call(total_links, MAX_WORKERS)

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


if __name__ == "__main__":
    system_links = [
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
        "http://headtopics.com/my/queen-vows-to-address-harry-and-meghan-racism-claims-new-straits-times-19079486"
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
    ]
    # try:
    #     data = endpoints()
    #     system_data = list(
    #     filter(lambda x: x['website']['website_category'] == 'Blog', data['data']))
    # except ConnectionError as e:
    #     print(e)
    # except TimeoutError as e:
    #     print(e)
    # except Exception as e:
    #     print(e)
    #     print("API BUSY")
    #     time.sleep(1.5)
    #     print("Trying again...")
    
    # print(len(system_data))
    WORKERS = os.cpu_count() - 2
    t1 = time.perf_counter()
    main(system_links, WORKERS)
    t2 = time.perf_counter()
    elapsed_seconds = round(t2-t1, 2)
    time_finish = convert(elapsed_seconds)
    log.info("Finished scraping in %s", time_finish)
    print(f'Finish in {time_finish}')
