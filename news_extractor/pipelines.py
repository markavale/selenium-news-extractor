from itemadapter import ItemAdapter
import requests
import os
from news_extractor.helpers.api import api
from scrapy.exporters import JsonItemExporter, JsonLinesItemExporter
from decouple import config
from news_extractor.settings import TOKEN, environment
from pprint import pprint

_root_url = config(
    'PRODUCTION_API') if environment else config('DEVELOPMENT_API')


class StaticExtractorPipeline:
    def __init__(self):
        self.file = open("article_spider.json", 'ab')
        self.exporter = JsonLinesItemExporter(
            self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(TOKEN)
        }
        # print("Download latency: ",item['download_latency'])
        # pprint(item)
        try:
            if dict(item)['article_status'] == "Error":
                req = api(method='PUT', url='{}article/{}'.format(_root_url,
                                                                  dict(item)['article_id']), body=dict(item), headers=headers)
            else:
                req = api(method='PUT', url='{}article/{}'.format(_root_url,
                                                                  dict(item)['article_id']), body=dict(item), headers=headers)
            # print("went here")
            # pprint(req.json())
        except Exception as e: 
            print(e)
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
        try:
            print("Pipeline Extractor ------------------------------------------------------------------------------------------")
            self.exporter.export_item(item)
            pprint(item)
            return item
        except:
            print("error on pipeline")


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
