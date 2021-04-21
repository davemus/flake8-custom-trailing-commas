import ast
import tokenize
import unittest
from io import BytesIO

from flake8_tuple_trailing_commas import Plugin


def _results(code):
    ast_tree = ast.parse(code)
    tokens = list(tokenize.tokenize(BytesIO(bytes(code, encoding='utf-8')).readline))
    plugin = Plugin(ast_tree, tokens)
    return {f'{line},{offset}: {msg}' for line, offset, msg, _ in plugin.run()}


valid_multiline = """
fields = (
    'field1', 'field2',
)
"""

invalid_multiline = """
fields = (
    'field1', 'field2'
)
"""


class TestTrailingCommas(unittest.TestCase):
    def test_trivial_case(self):
        self.assertSetEqual(set(), _results(''))

    def test_with_comma_tuple(self):
        self.assertSetEqual(set(), _results('(1, 2, 3,)'))

    def test_without_comma_tuple(self):
        self.assertSetEqual(
            {'1,9: CMA100 trailing comma in tuple is missing'},
            _results('(1, 2, 3)')
        )

    def test_multiline_valid(self):
        self.assertSetEqual(_results(valid_multiline), set())

    def test_multiline_invalid(self):
        msg = '4,1: CMA100 trailing comma in tuple is missing'
        self.assertSetEqual(_results(invalid_multiline), set((msg,)))


class TestDotInEndOfErrors(unittest.TestCase):
    def test_trivial_case(self):
        self.assertSetEqual(set(), _results(''))

    def test_with_dot(self):
        self.assertSetEqual(
            set(),
            _results('raise ValidationError("Error with dot.")')
        )

    def test_without_dot(self):
        self.assertSetEqual(
            {'1,41: CMA200 message of ValidationError should end with dot'},
            _results('raise ValidationError("Error without dot")')
        )
    
    def test_atribute_with_dot(self):
        self.assertSetEqual(
            set(),
            _results('raise rest_framework.exceptions.ValidationError("Error with dot.")')
        )

    def test_attribute_without_dot(self):
        self.assertSetEqual(
            {'1,67: CMA200 message of ValidationError should end with dot'},
            _results('raise rest_framework.exceptions.ValidationError("Error without dot")')
        )
    
if __name__ == '__main__':
    unittest.main()
