# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class StaticArticleItem(scrapy.Item):
    # define the fields for your item here like:
    article_title = scrapy.Field()
    article_section = scrapy.Field()
    article_authors = scrapy.Field()
    article_publish_date = scrapy.Field()
    article_images = scrapy.Field()
    article_content = scrapy.Field()
    article_videos = scrapy.Field()
    article_media_type = scrapy.Field()
    # website = scrapy.Field()
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
