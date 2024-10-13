from typing import TypeVar, Type
from . import tokenizer
from .select_ import select_parser
from .token_tree import TokenTree, ParserError, TokenType
from sapi._internals.externals.database_py import data_model


T = TypeVar('T')
def parse(sapi_str: str, model: data_model.DataModel, return_type: Type[T] = str) -> T:
    # print(sapi_str)
    data_model.set_current(model)
    statements: list[str] = [stmt for stmt in sapi_str.split(';') if stmt.strip() != '']

    sql_token_trees = [] # sapi tok tree
    for stmt in statements:
        sapi_tok_tree = tokenizer.tokenize(stmt)
        sql_token_trees.append(_parse_token_tree(sapi_tok_tree))

    if return_type == list[TokenTree]:
        return sql_token_trees
    elif return_type == list[str]:
        return [str(t) for t in sql_token_trees]
    elif return_type == str:
        return '\n;\n'.join(str(t) for t in sql_token_trees) 
    else:
        # evt. allow out = abstrakt syntax tree
        raise TypeError("Unrecognized out_type")

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
                raise ParserError(f"{tok.type} is not yet implemented")
            case _:
                found_stmt_type = False
        if found_stmt_type:
            break

    return token_tree


