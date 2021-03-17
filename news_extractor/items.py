# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags


def remove_currency(value):
    return value.replace('£', '').strip()


class TestItem(scrapy.Item):
    # when name field find match it removes tags and take the first none null values
    name = scrapy.Field(input_processor=MapCompose(
        remove_tags), output_processor=TakeFirst())
    #
    price = scrapy.Field(input_processor=MapCompose(
        remove_tags, remove_currency), output_processor=TakeFirst())
    link = scrapy.Field()


class ScrapyCrawlerItem(scrapy.Item):
    url                 = scrapy.Field()
    article_id          = scrapy.Field()
    download_latency    = scrapy.Field()
    http_err            = scrapy.Field()
    timeout_err         = scrapy.Field()
    dns_err             = scrapy.Field()
    base_err            = scrapy.Field()
    skip_url            = scrapy.Field()


class StaticArticleItem(scrapy.Item):
    # define the fields for your item here like:
    article_title           = scrapy.Field()
    article_section         = scrapy.Field()
    article_authors         = scrapy.Field()
    article_publish_date    = scrapy.Field()
    article_images          = scrapy.Field()
    article_content         = scrapy.Field()
    article_videos          = scrapy.Field()
    article_media_type      = scrapy.Field()
    # website = scrapy.Field()
    article_ad_value        = scrapy.Field()
    article_pr_value        = scrapy.Field()
    article_language        = scrapy.Field()
    article_status          = scrapy.Field()
    article_error_status    = scrapy.Field()
    article_source_from     = scrapy.Field()
    keyword                 = scrapy.Field()
    article_url             = scrapy.Field()
    date_created            = scrapy.Field()
    date_updated            = scrapy.Field()
    created_by              = scrapy.Field()
    updated_by              = scrapy.Field()

    article_id              = scrapy.Field()
    download_latency        = scrapy.Field()
    # ip                      = scrapy.Field()
    # user_agent              = scrapy.Field()
    
    # {
    #     "google_date": "2021-03-09T21:55:00.000Z", # article_publish_date
    #     "status": "Queued", # article_status
    #     "date_created": "2021-03-10T10:11:51.000Z",
    #     "date_updated": "2021-03-10T10:11:51.000Z",
    #     "created_by": "System",
    #     "updated_by": "System",
    #     "_id": "60489b6714ffc3252f948577",
    #     "google_link": "https://news.google.com/articles/CBMigAFodHRwczovL3d3dy5tYXJrZXR3YXRjaC5jb20vc3RvcnkvdW5pdGVkLXBhcmNlbC1zZXJ2aWNlLWluYy1jbC1iLXN0b2NrLXJpc2VzLXR1ZXNkYXktb3V0cGVyZm9ybXMtbWFya2V0LTAxNjE1MzI2OTIwLWRjMzA4ZDgyYjQyNtIBhAFodHRwczovL3d3dy5tYXJrZXR3YXRjaC5jb20vYW1wL3N0b3J5L3VuaXRlZC1wYXJjZWwtc2VydmljZS1pbmMtY2wtYi1zdG9jay1yaXNlcy10dWVzZGF5LW91dHBlcmZvcm1zLW1hcmtldC0wMTYxNTMyNjkyMC1kYzMwOGQ4MmI0MjY?hl=en-PH&gl=PH&ceid=PH%3Aen",
    #     "google_title": "United Parcel Service Inc. Cl B stock rises Tuesday, outperforms market",
    #     "google_website_name": "absolute url", # get domain name
    #     "google_image": "https://lh6.googleusercontent.com/proxy/bpMUbH6tdkpxiS7SsMpOKW_u21shFx7qECVKN-4JqPIAi3LTtbiXzKubcuBtPG3083bxwbW1vV5HYmdnZHsLC01J6AH2QSNUwsNksEWJ=-p-df-h100-w100",
    #     # article_images
    # },
    #     # TODO: if exists
    #     {
    #     "google_date": "2021-03-09T12:38:43.000Z", # publish_date
    #     "status": "Queued", # article_status
    #     "google_title": "Korean crypto exchange bithumb toughens up its anti-money laundering measures",
    #     "google_website_name": "FXStreet",
    #     "google_image": "https://lh4.googleusercontent.com/proxy/MYa8zhDW2ss-lQZENBigFVnwVd_SZ3kgeuwhtTa_6xmS0uvwJIsWqosKmNka749YS1llhlpjdcoo_1l5KR0mwrQQj83HIUAP8tFe_IgJa4XF2ODfTxuKxPRRaiG47dbpNscl-crsKDqL2DSbkGjsskGyvhm-=-p-df-h100-w100",
    #     "original_url": "http://www.fxstreet.com/amp/cryptocurrencies/news/korean-crypto-exchange-bithumb-toughens-up-its-anti-money-laundering-measures-202103091238"
    #     }


class GlobalLinkItem(scrapy.Item):
    google_date                 = scrapy.Field()
    status                      = scrapy.Field()
    date_created                = scrapy.Field()
    date_updated                = scrapy.Field()
    created_by                  = scrapy.Field()
    updated_by                  = scrapy.Field()
    google_link                 = scrapy.Field()
    google_title                = scrapy.Field()
    google_website_name         = scrapy.Field()
    google_image                = scrapy.Field()

class GlobalLinkItemExists(scrapy.Item):
    google_date                 = scrapy.Field()
    status                      = scrapy.Field()
    google_title                = scrapy.Field()
    google_website_name         = scrapy.Field()
    google_image                = scrapy.Field()
    original_url                = scrapy.Field()

'''

IP, dl_latency, headers

'''

class GoogleNewsItem(scrapy.Item):
    article_title = scrapy.Field()
    article_section = scrapy.Field()
    article_authors = scrapy.Field()
    article_publish_date = scrapy.Field()
    article_images = scrapy.Field()
    article_content = scrapy.Field()
    article_videos = scrapy.Field()
    article_media_type = scrapy.Field()
    article_ad_value = scrapy.Field()
    article_pr_value = scrapy.Field()
    article_language = scrapy.Field()
    article_status = scrapy.Field()
    article_error_status = scrapy.Field()
    article_source_from = scrapy.Field()
    keyword = scrapy.Field()
    article_url = scrapy.Field()
    date_created = scrapy.Field()
    date_updated = scrapy.Field()
    created_by = scrapy.Field()
    updated_by = scrapy.Field()


class DynamicArticleItem(scrapy.Item):
    # define the fields for your item here like:
    article_source_url = scrapy.Field()
    article_title = scrapy.Field()
    article_authors = scrapy.Field()
    article_publish_date = scrapy.Field()
    article_content = scrapy.Field()
    article_images = scrapy.Field()
    article_videos = scrapy.Field()
    article_ad_value = scrapy.Field()
    article_pr_value = scrapy.Field()
    article_status = scrapy.Field()
    created_by = scrapy.Field()
    updated_by = scrapy.Field()
    website = scrapy.Field()
    article_url = scrapy.Field()
