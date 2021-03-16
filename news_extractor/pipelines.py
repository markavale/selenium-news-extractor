# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import requests, os
from news_extractor.helpers.api import article_success
from scrapy.exporters import JsonItemExporter, JsonLinesItemExporter
from decouple import config

process_name = config("PROCESS_NAME")

# class NewsExtractorPipeline:
#     def process_item(self, item, spider):
#         return item

class StaticExtractorPipeline:
    def __init__(self):
        self.file = open("article_spider.json", 'ab')
        self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
        self.items = []

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
<<<<<<< HEAD
        print("Pipeline of static extractor---------------------")
        # print(f"Pipeline of Static Extrator: {item['article_title']}")
        print(item)
        try:
            file = open("article_static.json", "a")
            file.write(str(item))
        except Exception as e:
            print(e)
        finally:
            file.close()
=======
        self.exporter.export_item(item)
        article_success(item, process_name)
        self.items.append(item)
        return item

class GlobalExtractorPipeline:  
    def __init__(self):
        self.file = open("global_article.json", 'ab')
        self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        # __article_success(item)
>>>>>>> production
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
