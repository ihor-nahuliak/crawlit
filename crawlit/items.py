import copy

import scrapy
from scrapy.item import DictItem
from scrapy.loader import ItemLoader

from .abc import ItemABC
from .utils import is_xpath_selector


class BaseItem(scrapy.Item):
    """Base class that allows access to the field values
    using dot notation, i.e. item.my_field = my_value
    """

    def __getattr__(self, name):
        if name in self.fields:
            if getattr(self.fields[name], 'default', None) is not None:
                default = [self.fields[name].default]
            else:
                default = []
            return self.get(name, default)
        return self.__getattribute__(name)

    def __setattr__(self, name, value):
        if name in self.fields:
            self[name] = value
        else:
            super(BaseItem, self).__setattr__(name, value)


class Item(BaseItem, ItemABC):
    """Base class from which all Items normally inherit.

    :param ItemLoader loader_class:
    """
    loader_class = ItemLoader

    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)

        # scrapy.Item originally has fields as class variable
        # we have to make a copy per class instance
        fields = copy.copy(self.__class__.fields)

        # link field instance to the item instance
        for field_name, field in fields.items():
            field.link_to_item(field_name, self)

        # now set fields attribute for the instance, ignoring class
        super(DictItem, self).__setattr__('fields', fields)

    @classmethod
    def load(cls, selector=None, response=None, parent=None, **context):
        item = cls()
        loader = cls.loader_class(item=item, selector=selector,
                                  response=response, parent=parent, **context)
        for field_name, field in item.fields.items():
            is_xpath = is_xpath_selector(field.selector)
            method = loader.replace_xpath if is_xpath else loader.replace_css
            method(field_name, field.selector, *field.processors, re=field.re)

        item = loader.load_item()
        return item
