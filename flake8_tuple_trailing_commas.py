import ast
import sys

if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.tuple_closing_bracket_positions = []

    def visit_Tuple(self, node):
        self.tuple_closing_bracket_positions.append((node.end_lineno, node.end_col_offset))
        self.generic_visit(node)


_MSG_MISSING_COMMA_TUPLE = 'CMA100 trailing comma in tuple is missing'


class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree, file_tokens):
        self._ast = tree
        self._file_tokens = file_tokens

    def validate_previous_tokens(self, token_idx):
        if token_idx == 0:
            return True
        token_idx -= 1
        token = self._file_tokens[token_idx]
        newline_tokens = [4, 61]
        if token.type in newline_tokens:
            return self.validate_previous_tokens(token_idx)
        return token.type == 54 and token.string == ','

    def run(self):
        visitor = Visitor()
        visitor.visit(self._ast)
        for position in visitor.tuple_closing_bracket_positions:
            idx = self._file_tokens.index(next(x for x in self._file_tokens if x.end == position))
            if not self.validate_previous_tokens(idx):
                yield position[0], position[1], _MSG_MISSING_COMMA_TUPLE, type(self)
