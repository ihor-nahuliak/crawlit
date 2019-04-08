"""Abstract base classes.

These are necessary to avoid circular imports between items.py and fields.py.
"""


class FieldABC:
    """Abstract base class from which all Field classes inherit.

    :param str name: class variable name in terms of ItemABC
    :param ItemABC parent: an instance which class has the field declared
    :param str selector: css or xpath selector
    """
    name = None
    parent = None
    selector = None

    def link_to_item(self, field_name, item):
        """
        :param str field_name: class variable name in terms of ItemABC
        :param ItemABC item: an instance which class has the field declared
        :return: None
        """
        self.name = field_name
        self.parent = item


class ItemABC:
    """Abstract base class from which all Items inherit."""
    fields = NotImplemented

    def load(self, selector=None, response=None, parent=None, **context):
        """Abstract method that must load fields from the response.

        :param scrapy.Selector selector:
        :param scrapy.Response response:
        :param scrapy.ItemLoader parent:
        :param dict context:
        :return ItemABC: filled instance
        """
        raise NotImplementedError
