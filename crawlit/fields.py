import re
import logging
from collections import Iterable

import scrapy
from scrapy.loader.processors import TakeFirst, Join, MapCompose
from scrapy.exceptions import DropItem

from .abc import FieldABC


logger = logging.getLogger(__name__)


class Field(scrapy.Field, FieldABC):
    """Base field class.

    :param str selector: css or xpath selector
    :param processors: list of scrapy.loader.processors instances
    :param bool many: it finds all values with that selectors when True
    :param str regexp: regexp string
    :param default: default value used if nothing found
    :param kwargs: rest of parameters
    """
    default_regexp = None

    def __init__(self, selector, *processors, multi_selector=False,
                 regexp=None, default=None, **kwargs):
        super(Field, self).__init__(**kwargs)
        self._regexp = regexp or self.default_regexp
        self.default = default
        self.selector = selector
        self.processors = list(processors)
        self.multi_selector = multi_selector
        if not multi_selector:
            self.processors.insert(0, TakeFirst())

    @property
    def re(self):
        # "re" it's an attribute analyzong by scrapy.ItemLoader
        return self._regexp


class String(Field):
    """String field class.

    :param str selector: css or xpath selector
    :param processors: list of scrapy.loader.processors instances
    :param bool strip: strip string when True
    :param bool lower: to lower case when True
    :param bool upper: to upper case when True
    :param dict, tuple choices: how to map found values to another values
    :param bool multi_choices: it takes all found choice values when True,
                                  otherwise it takes just the first one.
    :param kwargs: rest of parameters
    """
    choice_separators = ' .,¿?¡!:;-'

    def __init__(self, selector, *processors, strip=True,
                 lower=False, upper=False, choices=None,
                 multi_choices=False, **kwargs):
        super(String, self).__init__(selector, *processors, **kwargs)
        self.choices = choices

        filters = []

        if strip:
            filters.append(str.strip)

        if lower and upper:
            raise ValueError('Set lower or upper, not both.')

        if lower:
            filters.append(str.lower)
        elif upper:
            filters.append(str.upper)

        if choices:
            filters.append(self._map_choices)
            self.multi_choices = multi_choices

        elif multi_choices:
            raise ValueError('The "multi_choices" flag can be used '
                             'with "choices" parameter only.')

        if filters:
            idx = len(self.processors) - len(processors)
            self.processors.insert(idx, MapCompose(*filters))

    def _map_choices(self, value):
        # try to find choice pattern in the string value
        matched_values = []
        for choice in self.choices:
            if self._find_pattern(pattern=choice, where=value):
                if isinstance(self.choices, dict):
                    matched_values.append(self.choices[choice])
                else:
                    matched_values.append(choice)
                if not self.multi_choices:
                    break

        if not matched_values:
            logger.debug('"%s": unknown choice "%s"' % (self.name, value))

            if self.default is None:
                raise DropItem('"%s": invalid choice "%s"' % (self.name, value))

        value = matched_values or self.default

        if len(value) == 1 and not isinstance(value[0], (list, tuple)):
            # take first element
            result = value[0]

        elif all(isinstance(v, (list, tuple)) for v in value):
            # merge all multiset items as one set
            result = set()
            for v in value:
                result.update(v)
            result = list(sorted(result))

        else:
            # merge all items as one set
            result = list(sorted(set(value)))

        return result

    @classmethod
    def _find_pattern(cls, pattern, where):
        if isinstance(where, str):
            re_choice = (
                r'^{word}$'
                r'|^{word}[\s{separators}]'
                r'|[\s{separators}]{word}[\s{separators}]'
                r'|[\s{separators}]{word}$'
            ).format(
                word=re.escape(pattern),
                separators=re.escape(cls.choice_separators)
            )
            found = bool(re.findall(re_choice, where))
        else:
            found = isinstance(where, Iterable) and pattern in where
        return found


class Boolean(Field):
    def __init__(self, selector, *processors, **kwargs):
        super(Boolean, self).__init__(selector, *processors, **kwargs)

        idx = len(self.processors) - len(processors)
        self.processors.insert(idx, bool)


class Integer(String):
    """Integer field class.

    :param str selector: css or xpath selector
    :param processors: list of scrapy.loader.processors instances
    :param kwargs: rest of parameters
    """
    default_regexp = '[\-+]?\d+[eE]{1}\+{1}\d+|[\-+]?\d+'

    def __init__(self, selector, *processors, **kwargs):

        super(Integer, self).__init__(selector, *processors, **kwargs)

        idx = len(self.processors) - len(processors)
        self.processors.insert(idx, Join(separator=''))
        self.processors.insert(idx + 1, self._to_int)

    def _to_int(self, value):
        if not value:
            return self.default
        try:
            return int(value)
        except (TypeError, ValueError):
            raise DropItem('"%s": int expected, not "%s"' % (self.name, value))


class Float(String):
    """Float field class.

    :param str selector: css or xpath selector
    :param processors: list of scrapy.loader.processors instances
    :param str delimiter: float delimiter char
    :param kwargs: rest of parameters
    """
    default_regexp = '[\-+]?\d+[eE]{1}[\-+]{1}\d+|[\-+]?\d*\.?\d+'

    def __init__(self, selector, *processors, delimiter='.', **kwargs):
        self.delimiter = delimiter
        if self.delimiter != '.':
            self.default_regexp = self.default_regexp.replace(
                '\.', re.escape(self.delimiter))

        super(Float, self).__init__(selector, *processors, **kwargs)

        idx = len(self.processors) - len(processors)
        self.processors.insert(idx, Join(separator=''))
        self.processors.insert(idx + 1, self._to_float)

    def _to_float(self, value):
        if not value:
            return self.default
        if self.delimiter != '.':
            value = value.replace(self.delimiter, '.')
        try:
            return float(value)
        except (TypeError, ValueError):
            raise DropItem('"%s": float expected, '
                           'not "%s"' % (self.name, value))


class Email(String):
    default_regexp = (
        "(?P<extract>[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
        "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
        "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)")
