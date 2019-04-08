import unittest

from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.exceptions import DropItem

from crawlit import fields


class TestCase(unittest.TestCase):

    def test_choices_attr(self):
        field = fields.String('.length', choices={'m': 1, 'km': 1000})

        self.assertDictEqual({'m': 1, 'km': 1000}, field.choices)

    def test_no_filters(self):
        field = fields.String('h2', strip=False, multi_selector=True)

        self.assertListEqual([], field.processors)

    def test_strip_filter(self):
        field = fields.String('h2', strip=True, multi_selector=True)

        self.assertEqual(1, len(field.processors))
        self.assertIsInstance(field.processors[0], MapCompose)
        self.assertTupleEqual((str.strip,), field.processors[0].functions)

    def test_lower_filter(self):
        field = fields.String('h2', multi_selector=True,
                              strip=False, lower=True)

        self.assertEqual(1, len(field.processors))
        self.assertIsInstance(field.processors[0], MapCompose)
        self.assertTupleEqual((str.lower,), field.processors[0].functions)

    def test_upper_filter(self):
        field = fields.String('h2', multi_selector=True,
                              strip=False, upper=True)

        self.assertEqual(1, len(field.processors))
        self.assertIsInstance(field.processors[0], MapCompose)
        self.assertTupleEqual((str.upper,), field.processors[0].functions)

    def test_strip_lower_filter(self):
        field = fields.String('h2', multi_selector=True,
                              strip=True, lower=True)

        self.assertEqual(1, len(field.processors))
        self.assertIsInstance(field.processors[0], MapCompose)
        self.assertTupleEqual(
            (str.strip, str.lower), field.processors[0].functions)

    def test_strip_upper_filter(self):
        field = fields.String('h2', multi_selector=True,
                              strip=True, upper=True)

        self.assertEqual(1, len(field.processors))
        self.assertIsInstance(field.processors[0], MapCompose)
        self.assertTupleEqual(
            (str.strip, str.upper), field.processors[0].functions)

    def test_lower_and_upper_raises_error(self):
        with self.assertRaises(ValueError) as err_ctx:
            fields.String('h2', lower=True, upper=True)

        self.assertEqual('Set lower or upper, not both.',
                         err_ctx.exception.args[0])

    def test_choices_processor(self):
        field = fields.String('.length', multi_selector=True, strip=False,
                              choices={'m': 1, 'km': 1000})

        self.assertEqual(1, len(field.processors))
        self.assertIsInstance(field.processors[0], MapCompose)
        self.assertTupleEqual(
            (field._map_choices,), field.processors[0].functions)

    def test_strip_lower_choices_processor(self):
        field = fields.String('.length', multi_selector=True,
                              strip=True, lower=True,
                              choices={'m': 1, 'km': 1000})

        self.assertEqual(1, len(field.processors))
        self.assertIsInstance(field.processors[0], MapCompose)
        self.assertTupleEqual(
            (str.strip, str.lower, field._map_choices),
            field.processors[0].functions)

    def test_strip_upper_choices_processor(self):
        field = fields.String('.length', strip=True, upper=True,
                              multi_selector=True,
                              choices={'M': 1, 'KM': 1000})

        self.assertEqual(1, len(field.processors))
        self.assertIsInstance(field.processors[0], MapCompose)
        self.assertTupleEqual(
            (str.strip, str.upper, field._map_choices),
            field.processors[0].functions)

    def test_processors_order(self):

        def foo1(s):
            return s

        def foo2(s):
            return s

        field = fields.String('h2', foo1, foo2, multi_selector=False)

        self.assertEqual(4, len(field.processors))
        self.assertIsInstance(field.processors[0], TakeFirst)
        self.assertIsInstance(field.processors[1], MapCompose)
        self.assertListEqual([foo1, foo2], field.processors[2:])

    def test_map_choices_dict(self):
        unit_field = fields.String('.length', choices={'m': 1, 'km': 1000})
        unit = unit_field._map_choices('100 km')

        self.assertEqual(1000, unit)

    def test_map_choices_dict_drops_item(self):
        unit_field = fields.String('.length', choices={'m': 1, 'km': 1000})
        unit_field.name = 'unit_field'

        with self.assertRaises(DropItem) as err_ctx:
            unit_field._map_choices('100 ha')

        self.assertEqual('"unit_field": invalid choice "100 ha"',
                         err_ctx.exception.args[0])

    def test_map_choices_tuple(self):
        unit_field = fields.String('.length', choices=('m', 'km'))
        unit = unit_field._map_choices('100 km')

        self.assertEqual('km', unit)

    def test_map_choices_tuple_drops_item(self):
        unit_field = fields.String('.length', choices=('m', 'km'))
        unit_field.name = 'unit_field'

        with self.assertRaises(DropItem) as err_ctx:
            unit_field._map_choices('100 ha')

        self.assertEqual('"unit_field": invalid choice "100 ha"',
                         err_ctx.exception.args[0])

    def test_map_choices_tuple_default_value(self):
        unit_field = fields.String('.length', choices=('m', 'km'), default='m')
        unit_field.name = 'unit_field'
        unit = unit_field._map_choices('100 ha')

        self.assertEqual('m', unit)

    def test_map_choices_multi_choices_tuple(self):
        unit_field = fields.String('.length', multi_choices=True,
                                   choices=('microwave', 'tv', 'shower'))
        unit = unit_field._map_choices('nice flat with tv and microwave')

        self.assertListEqual(['microwave', 'tv'], unit)

    def test_map_choices_multi_choices_dict(self):
        unit_field = fields.String('.length', multi_choices=True,
                                   choices={
                                       'microwave': ('kitchen', 'microwave'),
                                       'fridge': ('kitchen', 'fridge'),
                                       'shower': ('bathroom', 'shower'),
                                       'tube': ('bathroom', 'tube'),
                                   })
        unit = unit_field._map_choices(
            'nice flat with cable tv, microwave, shower')

        self.assertListEqual(
            ['bathroom', 'kitchen', 'microwave', 'shower'], unit)

    def test_map_choices_split_words(self):
        unit_field = fields.String('.length', multi_choices=True,
                                   choices={
                                       'microwave': ('kitchen', 'microwave'),
                                       'fridge': ('kitchen', 'fridge'),
                                       'shower': ('bathroom', 'shower'),
                                       'tube': ('bathroom', 'tube'),
                                   })
        unit = unit_field._map_choices((
            'nice', 'flat', 'with', 'cable', 'tv', 'microwave', 'shower'))

        self.assertListEqual(
            ['bathroom', 'kitchen', 'microwave', 'shower'], unit)

    def test_map_choices_separator(self):
        field = fields.String('.length', multi_choices=True,
                              choices=('a', 'b', 'c', 'd', 'e', 'f'))
        for separator in ' .,¿?¡!:;-':
            result = field._map_choices('a{0}bc{0}d{0}ef'.format(separator))

            self.assertListEqual(['a', 'd'], result)

    def test_multiple_choices_without_choices_raises_error(self):
        with self.assertRaises(ValueError) as err_ctx:
            fields.String('.length', multi_choices=True)

        self.assertEqual('The "multi_choices" flag can be used '
                         'with "choices" parameter only.',
                         err_ctx.exception.args[0])


if __name__ == '__main__':
    unittest.main()
