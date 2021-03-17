from itemadapter import ItemAdapter
import requests
import os
from news_extractor.helpers.api import api
from scrapy.exporters import JsonItemExporter, JsonLinesItemExporter
from decouple import config
from news_extractor.settings import TOKEN, environment
from pprint import pprint
process_name = config("PROCESS_NAME")

_root_url = config(
    'PRODUCTION_API') if environment else config('DEVELOPMENT_API')


class StaticExtractorPipeline:
    def __init__(self):
        self.file = open("article_spider.json", 'ab')
        self.exporter = JsonLinesItemExporter(
            self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
        self.items = []

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(TOKEN)
        }
        # print(dict(item))
        if dict(item)['article_status'] == "Error":
            if dict(item)['collection_name'] == "article_link":
                req = api(method='PUT', url='{}article/{}'.format(_root_url,
                                                                    dict(item)['article_id']), body=dict(item), headers=headers)
            else:
                req = api(method='POST', url='{}article'.format(
                    _root_url), body=dict(item), headers=headers)
        else:

            if dict(item)['collection_name'] == "article_link":
                req = api(method='PUT', url='{}article/{}'.format(_root_url,
                                                                  dict(item)['article_id']), body=dict(item), headers=headers)
            else:
                req = api(method='POST', url='{}article'.format(_root_url),
                          body=dict(item), headers=headers)
                update_query = {
                    "status": "Done",
                    'date_updated': item['date_updated'],
                    'updated_by': "Python Global Scraper"
                }
                req_update = api(method='PUT', url='{}global-link/{}'.format(_root_url,
                                                                             dict(item)['google_link_id']), body=update_query, headers=headers)
        return item


class TestStaticPipeline:
    def __init__(self):
        self.file = open("test_article.json", 'ab')
        self.exporter = JsonLinesItemExporter(
            self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
        self.items = []

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        print("Pipeline Extractor ------------------------------------------------------------------------------------------")
        self.exporter.export_item(item)
        self.items.append(item)
        pprint(item)
        return item


class GlobalExtractorPipeline:
    def __init__(self):
        self.file = open("global_article.json", 'ab')
        self.exporter = JsonLinesItemExporter(
            self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class DynamicExtractorPipeline:
    def __init__(self):
        pass

    def process_item(self, item, spider):
        print(f"Pipeline of Dyamic Extractor Trigger....")
        try:
            file = open("article_dynamic.json", "a")
            file.write(str(item))
        except Exception as e:
            print(e)
        finally:
            file.close()
        return item

# def api_call():
