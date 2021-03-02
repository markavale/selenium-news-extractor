from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

links = [
    "https://www.nytimes.com/2021/02/28/briefing/myanmar-hongkong-vaccine.html",
    "https://www.nytimes.com/2021/02/28/podcasts/the-daily/genetics-dna-tests-ancestry.html"
    # "https://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
    # "https://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html",
    # "https://www.nytimes.com/2021/02/27/nyregion/cuomo-charlotte-bennett-sexual-harassment.html",
    # "https://www.nytimes.com/2021/02/28/nyregion/full-text-of-cuomos-statement-in-response-to-harassment-accusations.html",
    # "https://www.nytimes.com/2021/02/28/health/covid-vaccine-sites.html",
    # "https://www.nytimes.com/2021/02/28/technology/seniors-vaccines-technology.html",
    # "https://www.nytimes.com/2021/02/28/us/schools-reopening-philadelphia-parents.html",
    # "https://www.nytimes.com/2021/02/28/us/politics/supreme-court-voting-rights-act.html",
    # "https://www.nytimes.com/2021/02/28/us/politics/trump-cpac-republicans.html",
    # "https://www.nytimes.com/2021/02/28/us/politics/cpac-straw-poll-2024-presidential-race.html",
    # "https://www.nytimes.com/2021/02/28/us/politics/china-india-hacking-electricity.html",
    # "https://www.nytimes.com/2021/02/28/us/ahmaud-arbery-anniversary.html",
    # "https://www.nytimes.com/2021/02/28/business/media/cable-tv-streaming-discovery.html",
    # "https://www.nytimes.com/2021/02/28/opinion/voter-suppression-us.html",
    # "https://www.nytimes.com/2021/02/28/opinion/business-economics/private-equity-reckoning.html",
    # "https://www.nytimes.com/2021/02/28/opinion/brazil-covid-vaccines.html",
    # "https://www.nytimes.com/2021/02/28/opinion/covid-vaccine-global.html",
    # "https://www.nytimes.com/2021/02/23/opinion/humans-animals-philosophy.html",
    # "https://www.nytimes.com/2021/02/27/opinion/sunday/trump-cuomo-media-covid.html",
    # "https://www.nytimes.com/2021/02/27/opinion/sunday/democrats-media-tanden.html",
    # "https://www.nytimes.com/2021/02/23/opinion/woodcock-fda-opioids.html",
    # "https://www.nytimes.com/2021/02/26/opinion/sunday/coronavirus-alive-dead.html",
    # "https://www.nytimes.com/2021/02/26/opinion/sunday/saudi-arabia-biden-khashoggi.html",
    # "https://www.nytimes.com/2021/02/25/opinion/nursing-crisis-coronavirus.html",
    # "https://www.nytimes.com/2021/02/23/magazine/kazuo-ishiguro-klara.html",
    # "https://www.nytimes.com/2021/02/28/business/media/pandemic-streaming-tv-shows.html",
    # "https://www.nytimes.com/2021/02/25/us/female-con-artists-tori-telfer.html"
]

link2 = [
    "https://www.nytimes.com/2021/02/25/podcasts/still-processing-best-of-the-archives-whitney-houston.html",
    "https://www.nytimes.com/2021/02/28/nyregion/cuomo-investigation-sex-harassment.html"
]

def main():
    process = CrawlerProcess(get_project_settings())

    # myspd1 Is a crawl name
    
    process.crawl('article_static', urls=links)
    process.crawl('article_static', urls=link2)
    # process.crawl('')
    # process.crawl('posts')

    process.start()

if __name__ == "__main__":
    main()