import ast
import sys

if sys.version_info < (3, 8,):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.tuple_closing_bracket_positions = []
        self.exceptions_without_dots = []
        self.exceptions_not_wrapped = []

    def visit_Tuple(self, node):
        empty_tuple = not bool(node.elts)
        last_elem = None if empty_tuple else node.elts[-1]
        if not empty_tuple and not isinstance(last_elem, ast.Starred):
            self.tuple_closing_bracket_positions.append((node.end_lineno, node.end_col_offset,))
        self.generic_visit(node)

    def _check_validation_error_filling(self, payload):
        msg = False

        if isinstance(payload, ast.Dict):
            for value in payload.values:
                self._check_validation_error_filling(value)
            return

        elif isinstance(payload, ast.List):
            for elt in payload.elts:
                self._check_validation_error_filling(elt)
            return

        elif isinstance(payload, ast.Call):
            if payload.func.id not in ['_']:
                self.exceptions_not_wrapped.append((payload.lineno, payload.col_offset,))
            arg1, *_ = payload.args
            if isinstance(arg1, ast.Constant):
                msg = arg1.value
            elif isinstance(arg1, ast.Name):
                pass  # TODO way to check that content of such variable is wrapped

        elif isinstance(payload, ast.Constant):
            self.exceptions_not_wrapped.append((payload.lineno, payload.col_offset,))
            msg = payload.value

        if msg and not msg.endswith('.'):
            self.exceptions_without_dots.append(
                (
                    payload.end_lineno,
                    payload.end_col_offset,
                )
            )

    def visit_Call(self, node):
        target = node.func
        if isinstance(target, ast.Name):
            if target.id == 'ValidationError':
                error_payload, *_ = node.args
                self._check_validation_error_filling(error_payload)

        elif isinstance(target, ast.Attribute):
            if target.attr == 'ValidationError':
                error_payload, *_ = node.args
                self._check_validation_error_filling(error_payload)

        self.generic_visit(node)


_MSG_MISSING_COMMA_TUPLE = 'CMA100 trailing comma in tuple is missing'
_MSG_MISSING_DOT_IN_ERROR = 'CMA200 message of ValidationError should end with dot'
_MSG_NOT_WRAPPED_ERROR = 'CMA201 message of ValidationError should be wrapped in `_`'


class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree, file_tokens):
        self._ast = tree
        self._file_tokens = file_tokens

    def tuple_validate_comma(self, token_idx):
        if token_idx == 0:
            return True
        token_idx -= 1
        token = self._file_tokens[token_idx]
        newline_tokens = [4, 61]
        if token.type in newline_tokens:
            return self.tuple_validate_comma(token_idx)
        return token.type == 54 and token.string == ','
    def run(self):
        visitor = Visitor()
        visitor.visit(self._ast)

        # process_exceptions_without_dots
        for position in visitor.exceptions_without_dots:
            yield (position[0], position[1], _MSG_MISSING_DOT_IN_ERROR, type(self),)

        # process_not_wrapped_exceptions
        for position in visitor.exceptions_not_wrapped:
            yield (position[0], position[1], _MSG_NOT_WRAPPED_ERROR, type(self),)

        # process_tuple_trailing_commas
        for position in visitor.tuple_closing_bracket_positions:
            idx = self._file_tokens.index(next(x for x in self._file_tokens if x.end == position))
            if not self.tuple_validate_comma(idx):
                yield (position[0], position[1], _MSG_MISSING_COMMA_TUPLE, type(self),)

