from typing import TypeVar, Type
from . import tokenizer
from .select_ import select_parser
from .token_tree import TokenTree, ParserError, TokenType
from sapi.externals.database_py import forest


T = TypeVar('T')
def parse(sapi_str: str, forest_: forest.Forest, return_type: Type[T] = str) -> T:
    forest.set_current(forest_)
    token_trees = tokenizer.tokenize(sapi_str)

    for i, root_tree in enumerate(token_trees):
        token_trees[i] = _parse_token_tree(root_tree) # token_trees goes from sapi to sql

    if return_type == list[TokenTree]:
        return token_trees
    elif return_type == str:
        return '\n;\n'.join(str(t) for t in token_trees) # stringifier.to_sql_str(token_trees, sapi_code)
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
        match tok.token_type:
            case TokenType.SELECT:
                token_tree = select_parser.parse_select(token_tree) # this only changes the leaf tokens
            case TokenType.INSERT | TokenType.UPDATE | TokenType.DELETE | TokenType.CREATE | TokenType.ALTER | TokenType.DROP:
                raise ParserError(f"{tok.token_type} is not yet implemented")
            case _:
                found_stmt_type = False
        if found_stmt_type:
            break

    return token_tree


