from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import time, os, math, json, time
from news_extractor.helpers.api import endpoints
import concurrent.futures
from pprint import pprint


def main(data):
    print("len of data", len(data))
    divisible_n = math.ceil(len(data) / 3)
    spider_data = [data[i:i + divisible_n] for i in range(0, len(data), divisible_n)]
    print("Spider len ",len(spider_data))
    pprint("")
    for d in spider_data:
        pprint(d)
    pprint("")

    process = CrawlerProcess(get_project_settings())
    # for data in spider_data:
    #     process.crawl('article_static', data)
    [process.crawl('article_static', data) for data in spider_data]    
    process.start()

    # process.crawl('article_static', data=data)

def sub_main(system_data,n_workers):

    divisible_n =  math.ceil(len(system_data) / n_workers)
    data = [system_data[i:i + divisible_n] for i in range(0, len(system_data), divisible_n)]
    with concurrent.futures.ProcessPoolExecutor(max_workers= n_workers) as executor:
        [executor.submit(main, obj) for obj in data]
    
    # if len(system_data) > len(system_data) % WORKERS:
    #     divisible_n =  math.ceil(len(system_data) / WORKERS)
    #     data = [system_data[i:i + divisible_n] for i in range(0, len(system_data), divisible_n)]
    #     with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
    #         [executor.submit(main, obj) for obj in data]
    # else:
    #     divisible_n =  math.ceil(len(system_data) / WORKERS)
    #     data = [system_data[i:i + divisible_n] for i in range(0, len(system_data), divisible_n)]
        
    #     # print(len(data))
    #     # print("")
    #     # pprint(data)
    #     # print("")
    #     MAX_WORKERS = min(len(data), WORKERS)
    #     print(MAX_WORKERS)
    #     with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
    #         [executor.submit(main, obj) for obj in data]
        # print("Nothing yet....")

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

        "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
        "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
        "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
        "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html"
    ]

    # try:
    #     pass
    # except COnnectionError

    data = endpoints()
    system_data = list(filter(lambda x: x['website']['website_category']=='Blog', data['data']))
    # [print(blog['article_url']) for blog in system_data]
    print("total links: ", len(system_data))
    WORKERS = os.cpu_count() - 2
    t1 = time.perf_counter()
    sub_main(system_data, WORKERS)
    t2 = time.perf_counter()
    elapsed_seconds = round(t2-t1, 2)
    time_finish = convert(elapsed_seconds)
    print(f'Finish in {time_finish}')
    
