from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def main():
    process = CrawlerProcess(get_project_settings())

    # myspd1 Is a crawl name
    process.crawl('')
    process.crawl('')
    # process.crawl('posts')

    process.start()

if __name__ == "__main__":
    main()