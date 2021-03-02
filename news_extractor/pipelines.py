# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class NewsExtractorPipeline:
    def process_item(self, item, spider):
        return item

class StaticExtractorPipeline:
    def __init__(self):
        pass

    def process_items(self, item, spiider):
        print(f"Pipeline of Static Extractor Trigger....")
        try:
            file = open("article_static.json", "w")
            file.write(item)
        except Exception as e:
            print(e)
        finally:
            file.close()
        return item

class DynamicExtractorPipeline:
    def __init__(self):
        pass

    def process_items(self, item, spiider):
        print(f"Pipeline of Dyamic Extractor Trigger....")
        try:
            file = open("article_static.json", "w")
            file.write(item)
        except Exception as e:
            print(e)
        finally:
            file.close()
        return item
