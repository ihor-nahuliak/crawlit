import unittest

from scrapy.loader.processors import TakeFirst, MapCompose, Join
from scrapy.exceptions import DropItem

from crawlit import fields


class TestCase(unittest.TestCase):

    def test_float_processors_order(self):

        def foo1(s):
            return s

        def foo2(s):
            return s

        field = fields.Float('.value', foo1, foo2, multi_selector=False)

        self.assertIsInstance(field.processors[0], TakeFirst)
        self.assertIsInstance(field.processors[1], MapCompose)
        self.assertTupleEqual((str.strip,), field.processors[1].functions)
        self.assertIsInstance(field.processors[2], Join)
        self.assertEqual(field.processors[3], field._to_float)
        self.assertListEqual([foo1, foo2], field.processors[4:])

    def test_to_float_default_value(self):
        field = fields.Float('.value', multi_selector=False, default=0.0)
        result = field._to_float('')

        self.assertEqual(0.0, result)

    def test_to_float_value(self):
        field = fields.Float('.value', multi_selector=False, default=0)
        result = field._to_float('3.14')

        self.assertEqual(3.14, result)

    def test_to_float_invalid_value_raises_error(self):
        field = fields.Float('.value', multi_selector=False, default=0)
        field.name = 'float_field'

        with self.assertRaises(DropItem) as err_ctx:
            field._to_float('hello')

        self.assertEqual('"float_field": float expected, not "hello"',
                         err_ctx.exception.args[0])

    def test_to_float_value_custom_delimiter(self):
        field = fields.Float('.value', multi_selector=False, delimiter=',')
        result = field._to_float('3,14')

        self.assertEqual(3.14, result)


if __name__ == '__main__':
    unittest.main()
