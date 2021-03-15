# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import requests, os
from news_extractor.helpers.api import __article_success
from scrapy.exporters import JsonItemExporter, JsonLinesItemExporter


# class NewsExtractorPipeline:
#     def process_item(self, item, spider):
#         return item

class StaticExtractorPipeline:
    def __init__(self):
        self.file = open("article_spider.json", 'ab')
        self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        print("Pipeline of static extractor---------------------")
        # __article_success(id, article)
        self.exporter.export_item(item)
        __article_success(item)
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
