import warnings
from typing import TypeVar, Type
from . import tokenizer
from .select_ import select_parser
from .token_tree import TokenTree, ParserError, TokenType
from .db_contact import data_model
from .db_contact.data_model import DataModel
from .execution import dependencies

# class dependencies:
#     default_data_model = None

T = TypeVar('T')
def parse(sapi_str: str, model: DataModel = None, return_type: Type[T] = str) -> T:
    # setup
    if model is None:
        model = dependencies.default_data_model
    if not (isinstance(sapi_str, str) and isinstance(model, DataModel) and isinstance(return_type, type)):
        expected = str.__name__, DataModel.__name__, type.__name__
        actual = sapi_str.__class__.__name__, model.__class__.__name__, return_type.__class__.__name__
        raise TypeError(f"Excepted input types {expected}, received {actual}")
    data_model.set_current(model)

    # work
    statements: list[str] = [stmt for stmt in sapi_str.split(';') if stmt.strip() != '']

    sql_token_trees = [] # sapi tok tree
    for stmt in statements:
        sapi_tok_tree = tokenizer.tokenize(stmt)
        sql_token_trees.append(_parse_token_tree(sapi_tok_tree))

    # choose return type
    if return_type == list[TokenTree]:
        return sql_token_trees
    elif return_type == list[str]:
        return [str(t) for t in sql_token_trees]
    elif return_type == str:
        return '\n;\n'.join(str(t) for t in sql_token_trees)
    else:
        # evt. allow out = abstrakt syntax tree
        raise TypeError("Unrecognized return type")


def _parse_token_tree(token_tree: TokenTree) -> TokenTree:
    "Parse sapi TokenTree to sql TokenTree."
    # parse sub_trees
    for i, tok in enumerate(token_tree.tokens):
        if isinstance(tok, TokenTree):
            token_tree.tokens[i] = _parse_token_tree(tok)

    # parse leaves
    # stmt_type = token_tree.first_leaf().token_type # first leaf or first statement-starter?
    for tok in token_tree.tokens:
        if isinstance(tok, TokenTree):
            continue
        found_stmt_type = True # to be overridden, if not found
        match tok.type:
            case TokenType.SELECT:
                token_tree = select_parser.parse_select(token_tree) # this only changes the leaf tokens
            case TokenType.INSERT | TokenType.UPDATE | TokenType.DELETE | TokenType.CREATE | TokenType.ALTER | TokenType.DROP:
                warnings.warn(f"\n{tok.type} is not yet implemented."
                              "Sapi will ignore such inputs and pass them to sql unchanged.")
            case _:
                found_stmt_type = False
        if found_stmt_type:
            break

    return token_tree



def _trailing_semicolon(stmt_str: str) -> str:
    if not stmt_str.strip().endswith(';'):
        return ''
    semicolon_idx = len(stmt_str.strip()) - 1
    previous_newline_idx = stmt_str.rfind('\n', 0, semicolon_idx)
    if previous_newline_idx == -1:
        return ';' # No newline found, so no indentation, only ;
    indented_semicolon = stmt_str[previous_newline_idx : semicolon_idx + 1]
    if any(c != ' ' and c != ';' for c in indented_semicolon):
        raise Exception(indented_semicolon)
    return indented_semicolon
    


