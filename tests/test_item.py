import unittest
import logging

import scrapy
from scrapy.exceptions import DropItem
from scrapy.crawler import CrawlerProcess
from crawlit import Item, fields


class ScrupinghubContactItem(Item):
    phone_number = fields.String(
        'section.contact-ctas h3 a:contains("+1")::attr(href)')
    callable_weekdays = fields.String(
        'section.contact-ctas h3::text',
        choices=('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'),
        multi_choices=True)


class ContactItemValidatorPipeline:
    required_fields = ('phone_number',)

    @classmethod
    def process_item(cls, item, spider):
        for field_name in cls.required_fields:

            # assertion just to test
            assert item.get(field_name), '"%s" is required field' % field_name

            if not item.get(field_name):
                raise DropItem('"%s" is required field' % field_name)
        return item


class ScrupinghubContactSpider(scrapy.Spider):
    name = 'scrupinghub_contact_item'
    item_class = ScrupinghubContactItem
    start_urls = ['https://scrapinghub.com/contact']
    custom_settings = {
        'ITEM_PIPELINES': {
            'tests.test_item.ContactItemValidatorPipeline': 101,
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    @classmethod
    def parse(cls, response):
        item = cls.item_class.load(response)
        yield item


class TestCase(unittest.TestCase):

    def test_run_spider(self):
        crawler = CrawlerProcess(settings={'LOG_LEVEL': logging.INFO})
        crawler.crawl(ScrupinghubContactSpider)
        crawler.start()


if __name__ == '__main__':
    unittest.main()
