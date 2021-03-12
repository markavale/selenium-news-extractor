import scrapy
from news_extractor.items import TestItem
from scrapy.loader import ItemLoader

class WhiskySpider(scrapy.Spider):
    name = 'test_logic'
    custom_settings = {
        # 'ITEM_PIPELINES': {'news_extractor.pipelines.StaticExtractorPipeline': None},
        "FEEDS": {"whisky.json": {"format": "json"}},
    }
    def start_requests(self):
        url = 'https://www.whiskyshop.com/scotch-whisky?item_availability=In+Stock'
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        for products in response.css('div.product-item-info'):
            loader = ItemLoader(item = TestItem(), selector=products)
            loader.add_css('name', 'a.product-item-link')
            loader.add_css('price', 'span.price')
            loader.add_css('link', 'a.product-item-link::attr(href)')

            yield loader.load_item()

            # item['name'] = products.css('a.product-tem-link::text').get()
            # item['price'] = product.css('span.price::text').get().replace('£', '')
            # item['link'] = product.css('a.product-item-link').attrib['href']

            # yield item

        next_page = response.css('a.action.next').attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)