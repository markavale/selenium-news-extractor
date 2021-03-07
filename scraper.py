from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import time
from news_extractor.helpers.endpoints import endpoints

links = [
    # "http://www.nytimes.com/2021/02/28/briefing/myanmar-hongkong-vaccine.html",
    # "http://sailorstarcatcher.net/bpi-celebrates-national-arts-month-with-a-special-treat-for-cardholders-gives-special-offers-at-the-annual-art-in-the-park/",
    # "http://www.gmanetwork.com/news/news/nation/778111/palace-confident-of-uninterrupted-vaccination-vs-covid-19/story/?just_in",
    # "http://www.nytimes.com/2021/02/28/podcasts/the-daily/genetics-dna-tests-ancestry.html",
    # "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
    # "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
    # "http://www.nytimes.com/2021/02/27/nyregion/cuomo-charlotte-bennett-sexual-harassment.html",
    # "http://www.nytimes.com/2021/02/28/nyregion/full-text-of-cuomos-statement-in-response-to-harassment-accusations.html",
    # "http://www.nytimes.com/2021/02/28/health/covid-vaccine-sites.html",
    # "http://www.nytimes.com/2021/02/28/technology/seniors-vaccines-technology.html",
    "http://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html"
    # "http://www.nytimes.com/2021/02/28/us/politics/supreme-court-voting-rights-act.html"
    # "http://www.nytimes.com/2021/02/28/us/politics/trump-cpac-republicans.html",
    # "http://www.nytimes.com/2021/02/28/us/politics/cpac-straw-poll-2024-presidential-race.html",
    # "http://www.nytimes.com/2021/02/28/us/politics/china-india-hacking-electricity.html",
    # "http://www.nytimes.com/2021/02/28/us/ahmaud-arbery-anniversary.html",
    # "http://www.nytimes.com/2021/02/28/business/media/cable-tv-streaming-discovery.html"
    # "http://www.nytimes.com/2021/02/28/opinion/voter-suppression-us.html",
    # "http://www.nytimes.com/2021/02/28/opinion/business-economics/private-equity-reckoning.html",
    # "http://www.nytimes.com/2021/02/28/opinion/brazil-covid-vaccines.html",
    # "http://www.nytimes.com/2021/02/28/opinion/covid-vaccine-global.html",
    # "http://www.nytimes.com/2021/02/23/opinion/humans-animals-philosophy.html",
    # "http://www.nytimes.com/2021/02/27/opinion/sunday/trump-cuomo-media-covid.html",
    # "http://www.nytimes.com/2021/02/27/opinion/sunday/democrats-media-tanden.html",
    # "http://www.nytimes.com/2021/02/23/opinion/woodcock-fda-opioids.html",
    # "http://www.nytimes.com/2021/02/26/opinion/sunday/coronavirus-alive-dead.html",
    # "http://www.nytimes.com/2021/02/26/opinion/sunday/saudi-arabia-biden-khashoggi.html",
    # "http://www.nytimes.com/2021/02/25/opinion/nursing-crisis-coronavirus.html",
    # "http://www.nytimes.com/2021/02/23/magazine/kazuo-ishiguro-klara.html",
    # "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
    # "http://www.nytimes.com/2021/02/25/us/female-con-artists-tori-telfer.html"
]

gma_links = [
    "https://www.gmanetwork.com/news/money/companies/778457/dmci-holdings-net-income-plunges-44-in-2020-as-pandemic-bites/story/?just_in"
]

link2 = [
    "http://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
    "http://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
    "http://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
    "http://www.nytimes.com/2021/02/25/us/female-con-artists-tori-telfer.html"
]

dynamic_links = [
    "http://www.gmanetwork.com/news/news/nation/778102/vp-robredo-says-woman-in-viral-vaccination-photo-not-her/story/",
    "http://www.gmanetwork.com/news/news/world/778076/nigeria-receives-nearly-4-million-free-astrazeneca-vaccines-from-covax/story/"
]

dynamic_links2 = [
    # "http://www.scmp.com/week-asia/politics/article/3123558/china-behind-mystery-kashmir-ceasefire-between-india-and",
    # "http://www.scmp.com/news/hong-kong/politics/article/3123660/hong-kongs-kingmakers-will-citys-tycoons-have-their",
    # "http://www.scmp.com/news/hong-kong/politics/article/3123534/national-security-law-hundreds-supporters-queue-chant-ahead",
    # "http://www.scmp.com/week-asia/politics/article/3123652/myanmars-protesters-and-military-dig-can-asean-us-or-china-help",
    # "http://www.gmanetwork.com/news/news/nation/777941/philippines-detects-south-african-coronavirus-variant/story/",
    "http://www.gmanetwork.com/news/news/nation/778111/palace-confident-of-uninterrupted-vaccination-vs-covid-19/story/?just_in"
]

diff_links = [
    "http://news.abs-cbn.com/sports/03/04/21/g-league-despite-loss-jalen-green-praised-for-improved-playmaking",
    "http://www.gmanetwork.com/news/news/nation/778111/palace-confident-of-uninterrupted-vaccination-vs-covid-19/story/?just_in",
    "http://www.nytimes.com/2021/02/25/us/female-con-artists-tori-telfer.html"

]


def main(data):
    process = CrawlerProcess(get_project_settings())

    # myspd1 Is a crawl name

    process.crawl('article_static', data=data)

    # process.crawl('article_static', urls=links)
    # process.crawl('article_static', urls=links)
    # process.crawl('article_static', urls=links)
    # process.crawl('article_static', urls=links)
    # process.crawl('article_static', urls=links)
    # process.crawl('article_static', urls=links)
    # process.crawl('article_static', urls=links)
    # process.crawl('article_static', urls=links)
    # process.crawl('article_static', urls=links)
    # process.crawl('article_static', urls=links)    


    # process.crawl('article_dynamic', urls=dynamic_links)
    # process.crawl('article_dynamic', urls=dynamic_links2)

    process.start()


if __name__ == "__main__":
    # print(endpoints())
    t1 = time.perf_counter()
    data = endpoints()
    # main(data)
    main(link2)
    t2 = time.perf_counter()
    print(f'Finished in {round(t2-t1, 2)} second(s).....')
