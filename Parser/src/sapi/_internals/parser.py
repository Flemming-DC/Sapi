import warnings
from collections import namedtuple
from typing import TypeVar, Type
from . import tokenizer
from .insert import insert_parser
from .select_ import select_parser
from .token_tree import TokenTree, TokenType, StrReplacement
from .db_contact import data_model
from .db_contact.data_model import DataModel
from .error import CompilerError
from .generate_sql_str import make_str

# def try_parse(sapi_str: str, model: DataModel, return_type: Type[T] = str) -> T | Exception:
#     try: 
#         return parse(sapi_str, model, return_type)
#     except Exception as e: # create a user error class for the parser and filter by it
#         # code_start = sapi_str if len(sapi_str) < 10 else sapi_str[:10] + '...'
#         message = f"Failed to parse '''{sapi_str}'''\nError: {e}\n"
#         return Exception(message) # cuts off traceback

T = TypeVar('T')
_return_types = (list[list[StrReplacement]], list[str], str)
def parse(sapi_str: str, model: DataModel, return_type: Type[T] = str) -> T:
    # check
    if not (isinstance(sapi_str, str) and isinstance(model, DataModel) and isinstance(return_type, type)):
        expected = str.__name__, DataModel.__name__, type.__name__
        actual = sapi_str.__class__.__name__, model.__class__.__name__, return_type.__class__.__name__
        raise TypeError(f"Excepted input types {expected}, received {actual}")
    if return_type not in _return_types:
        raise TypeError(f"Excepted return_type in {_return_types}, received {return_type}")
    # setup
    data_model.set_current(model)

    # work
    statements: list[str] = [stmt for stmt in sapi_str.split(';') if stmt.strip() != '']

    sql_token_trees_str: list[str] = []
    replacements: list[list] = []
    for stmt in statements:
        sapi_tok_tree = tokenizer.tokenize(stmt)
        if sapi_tok_tree is not None:
            sql, str_replacements = _parse_token_tree(stmt, sapi_tok_tree)
            sql_token_trees_str.append(sql)
            replacements.append(str_replacements)

    # choose return type
    if return_type == list[list[StrReplacement]]:
        return replacements# [t.recursive_str_replacements() for t in sql_token_trees]
    elif return_type == list[str]:
        return [t for t in sql_token_trees_str]
    elif return_type == str:
        return '\n;\n'.join(t for t in sql_token_trees_str)
    else:
        raise CompilerError("Unrecognized return type")


def _parse_token_tree(sapi_stmt: str, token_tree: TokenTree) -> tuple[str, list[StrReplacement]]:
    "Parse sapi TokenTree to sql TokenTree."
    # parse sub_trees
    for tok in token_tree.tokens:
        if isinstance(tok, TokenTree):
            _parse_token_tree(sapi_stmt, tok)

    # parse leaves
    sql: str = sapi_stmt
    replacements = [] # used for hinting
    for tok in token_tree.tokens:
        if isinstance(tok, TokenTree):
            continue
        found_stmt_type = True # to be overridden, if not found
        match tok.type:
            case TokenType.SELECT:
                replacements = select_parser.parse_select(token_tree) # this only changes the leaf tokens
                sql = make_str(sapi_stmt, replacements)
            case TokenType.INSERT:
                sql_ = insert_parser.parse_insert(token_tree.tokens) # this only changes the leaf tokens
                sql = sql_ if sql_ else sapi_stmt
            case TokenType.UPDATE | TokenType.DELETE | TokenType.CREATE | TokenType.ALTER | TokenType.DROP:
                warnings.warn(f"\n{tok.type} is not yet implemented."
                              "Sapi will ignore such inputs and pass them to sql unchanged.")
            case _:
                found_stmt_type = False
        if found_stmt_type:
            break

    return sql, replacements



# def _trailing_semicolon(stmt_str: str) -> str:
#     if not stmt_str.strip().endswith(';'):
#         return ''
#     semicolon_idx = len(stmt_str.strip()) - 1
#     previous_newline_idx = stmt_str.rfind('\n', 0, semicolon_idx)
#     if previous_newline_idx == -1:
#         return ';' # No newline found, so no indentation, only ;
#     indented_semicolon = stmt_str[previous_newline_idx : semicolon_idx + 1]
#     if any(c != ' ' and c != ';' for c in indented_semicolon):
#         raise CompilerError(indented_semicolon)
#     return indented_semicolon
    


