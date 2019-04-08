# crawlit
Crawl it!

#### About
It's an extension for [scrapy](https://scrapy.org/) library written with the goal of making scrappers code more descriptively.

```python
from scrapy import Spider
from crawlit import Item, fields


class ProfileItem(Item):
    first_name = fields.String('.first-name::text')
    last_name = fields.String('.last-name::text')
    phones_list = fields.String('.phone::attr(href)', multi_selector=True)
    emails_list = fields.Email('.email::attr(href)', multi_selector=True)
    gender = fields.String('.gender::text', choices=('m', 'f', 'u'))
    age = fields.Integer('.age::text')


class ProfileSpider(Spider):
    name = 'profile_item'
    start_urls = ['https://example.com/']

    @classmethod
    def parse(cls, response):
        item = ProfileItem.load(response)
        yield item

```

#### Testing
```
make install
make test
```

(C) Ihor Nahuliak
