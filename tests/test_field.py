import unittest

from scrapy.loader.processors import TakeFirst

from crawlit import fields


class TestCase(unittest.TestCase):

    def test_selector_attr(self):
        field = fields.Field('h1')

        self.assertEqual('h1', field.selector)

    def test_default_attr(self):
        field = fields.Field('h1', default='test')

        self.assertEqual('test', field.default)

    def test_regexp_attr(self):
        field = fields.Field('h1', regexp=r'\d+')

        self.assertEqual(r'\d+', field.re)

    def test_default_regexp_attr(self):

        class MyField(fields.Field):
            default_regexp = r'\d+'

        field = MyField('h1')

        self.assertEqual(r'\d+', field.re)

    def test_default_regexp_is_overridable(self):

        class MyField(fields.Field):
            default_regexp = r'\d+'

        field = MyField('h1', regexp=r'\w{3}')

        self.assertEqual(r'\w{3}', field.re)

    def test_processors(self):

        def foo1(s):
            return s

        def foo2(s):
            return s

        field = fields.Field('h2', foo1, foo2, multi_selector=True)

        self.assertListEqual([foo1, foo2], field.processors)

    def test_processors_not_multi_selector(self):

        def foo1(s):
            return s

        def foo2(s):
            return s

        field = fields.Field('h1', foo1, foo2, multi_selector=False)

        self.assertIsInstance(field.processors[0], TakeFirst)
        self.assertListEqual([foo1, foo2], field.processors[1:])


if __name__ == '__main__':
    unittest.main()
