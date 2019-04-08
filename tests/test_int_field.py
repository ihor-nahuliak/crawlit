import unittest

from scrapy.loader.processors import TakeFirst, MapCompose, Join
from scrapy.exceptions import DropItem

from crawlit import fields


class TestCase(unittest.TestCase):

    def test_int_processors_order(self):

        def foo1(s):
            return s

        def foo2(s):
            return s

        field = fields.Integer('.value', foo1, foo2, multi_selector=False)

        self.assertIsInstance(field.processors[0], TakeFirst)
        self.assertIsInstance(field.processors[1], MapCompose)
        self.assertTupleEqual((str.strip,), field.processors[1].functions)
        self.assertIsInstance(field.processors[2], Join)
        self.assertEqual(field.processors[3], field._to_int)
        self.assertListEqual([foo1, foo2], field.processors[4:])

    def test_to_int_default_value(self):
        field = fields.Integer('.value', multi_selector=False, default=0)
        result = field._to_int('')

        self.assertEqual(0, result)

    def test_to_int_value(self):
        field = fields.Integer('.value', multi_selector=False, default=0)
        result = field._to_int('123')

        self.assertEqual(123, result)

    def test_to_int_invalid_value_raises_error(self):
        field = fields.Integer('.value', multi_selector=False, default=0)
        field.name = 'int_field'

        with self.assertRaises(DropItem) as err_ctx:
            field._to_int('hello')

        self.assertEqual('"int_field": int expected, not "hello"',
                         err_ctx.exception.args[0])


if __name__ == '__main__':
    unittest.main()
