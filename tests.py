import ast
import tokenize
import unittest
from io import BytesIO

from flake8_tuple_trailing_commas import Plugin


def _results(code):
    ast_tree = ast.parse(code)
    tokens = list(tokenize.tokenize(BytesIO(bytes(code, encoding='utf-8')).readline))
    plugin = Plugin(ast_tree, tokens)
    return set({f'{line},{offset}: {msg}' for line, offset, msg, _ in plugin.run()})


valid_multiline_commas = """
fields = (
    'field1', 'field2',
)
"""

invalid_multiline_commas = """
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
        self.assertSetEqual(_results(valid_multiline_commas), set())

    def test_multiline_invalid(self):
        msg = '4,1: CMA100 trailing comma in tuple is missing'
        self.assertSetEqual(_results(invalid_multiline_commas), set((msg,)))

    def test_unpacking(self):
        self.assertSetEqual(_results("a, *b = c"), set())


not_wrapped_variable = """
error = "Error not wrapped in gettext"
raise ValidationError(error)
"""

wrapped_variable = """
error = _("Error wrapped in gettext")
raise ValidationError(error)
"""


class TestDotInEndOfErrors(unittest.TestCase):
    def test_trivial_case(self):
        self.assertSetEqual(set(), _results(''))

    def test_with_dot(self):
        self.assertSetEqual(
            set(),
            _results('raise ValidationError(_("Error with dot."))')
        )

    def test_without_dot(self):
        self.assertSetEqual(
            {'1,44: CMA200 message of ValidationError should end with dot'},
            _results('raise ValidationError(_("Error without dot"))')
        )

    def test_atribute_with_dot(self):
        self.assertSetEqual(
            set(),
            _results('raise rest_framework.exceptions.ValidationError(_("Error with dot."))')
        )

    def test_attribute_without_dot(self):
        self.assertSetEqual(
            {'1,70: CMA200 message of ValidationError should end with dot'},
            _results('raise rest_framework.exceptions.ValidationError(_("Error without dot"))')
        )

    def test_with_dot_inside_dict(self):
        self.assertSetEqual(
            set(),
            _results('raise ValidationError({"spam": _("With dot.")})')
        )

    def test_without_dot_inside_dict(self):
        self.assertSetEqual(
            {'1,47: CMA200 message of ValidationError should end with dot'},
            _results('raise ValidationError({"spam": _("Without dot")})')
        )

    def test_with_dot_inside_list(self):
        self.assertSetEqual(
            set(),
            _results('raise ValidationError([_("With dot.")])')
        )

    def test_without_dot_inside_list(self):
        self.assertSetEqual(
            {'1,39: CMA200 message of ValidationError should end with dot'},
            _results('raise ValidationError([_("Without dot")])')
        )

    def test_not_wrapped_str(self):
        self.assertSetEqual(
            {'1,22: CMA201 message of ValidationError should be wrapped in `_`'
            },
            _results('raise ValidationError("Not wrapped.")')
        )

    def test_not_wrapped_in_list(self):
        self.assertSetEqual(
            {'1,23: CMA201 message of ValidationError should be wrapped in `_`'
            },
            _results('raise ValidationError(["Not wrapped."])')
        )

    def test_not_wrapped_in_dict(self):
        self.assertSetEqual(
            {'1,32: CMA201 message of ValidationError should be wrapped in `_`'},
            _results('raise ValidationError({"error": "Not wrapped."})')
        )

    @unittest.skip('Functionality not implemented yet')
    def test_not_wrapped_variable(self):
        self.assertEqual(
            {'something bad happened'},
            _results(not_wrapped_variable)
        )

    @unittest.skip('Functionality not implemented yet')
    def test_wrapped_variable(self):
        self.assertEqual(
            {'something bad happened'},
            _results(wrapped_variable)
        )




if __name__ == '__main__':
    unittest.main()
