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

class StaticArticleItem(scrapy.Item):
    article_title           = scrapy.Field()
    article_section         = scrapy.Field()
    article_authors         = scrapy.Field()
    article_publish_date    = scrapy.Field()
    article_images          = scrapy.Field()
    article_content         = scrapy.Field()
    article_videos          = scrapy.Field()
    article_media_type      = scrapy.Field()
    article_source_url      = scrapy.Field()
    website                 = scrapy.Field()
    article_ad_value        = scrapy.Field()
    article_pr_value        = scrapy.Field()
    article_language        = scrapy.Field()
    article_status          = scrapy.Field()
    article_error_status    = scrapy.Field()
    keyword                 = scrapy.Field()
    article_url             = scrapy.Field()
    date_created            = scrapy.Field()
    date_updated            = scrapy.Field()
    created_by              = scrapy.Field()
    updated_by              = scrapy.Field()

    article_id              = scrapy.Field()
    download_latency        = scrapy.Field()
    http_err                = scrapy.Field()
    timeout_err             = scrapy.Field()
    dns_err                 = scrapy.Field()
    base_err                = scrapy.Field()
    skip_url                = scrapy.Field()

    proxy                   = scrapy.Field()
    user_agent              = scrapy.Field()
    source_created_from     = scrapy.Field()
    parser                  = scrapy.Field()

class DynamicArticleItem(scrapy.Item):
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
