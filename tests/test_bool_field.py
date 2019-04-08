import unittest

from scrapy.loader.processors import TakeFirst

from crawlit import fields


class TestCase(unittest.TestCase):

    def test_bool_processors_order(self):

        def foo1(s):
            return s

        def foo2(s):
            return s

        field = fields.Boolean('.response:contains("yes")', foo1, foo2,
                               multi_selector=False)

        self.assertIsInstance(field.processors[0], TakeFirst)
        self.assertEqual(field.processors[1], bool)
        self.assertListEqual([foo1, foo2], field.processors[2:])


if __name__ == '__main__':
    unittest.main()
