from typing import TypeVar, Type
from . import tokenizer, stringifier
from .select import select_parser
from .tokenizer import TokenTree, ParserError, TokenType, Token, AutoToken


def to_sql_str(tok_trees: list[TokenTree], sapi_code: str) -> str:
    sql_str = ""
    for tok_tree in tok_trees:
        sql_str += _tok_tree_to_sql_str(tok_tree, sapi_code)
    return sql_str


def _tok_tree_to_sql_str(tok_tree: TokenTree, sapi_code: str) -> str:
    sql_str = ""
    is_auto = False
    auto_code_length = 0
    
    for tok in tok_tree.flatten():
        was_auto = is_auto
        is_auto = isinstance(tok, AutoToken)
        if is_auto:
            sql_str += TokenTree.add_token_str(sql_str, tok)

        else:
            # ignores comments and evt. semicolon
            sql_str += sapi_code[tok.start + auto_code_length: tok.end + auto_code_length]
        # what about the removed case ? How do you distinguish that from comments ? 


    # split into sections of auto vs not-auto tokens. 
    # grap non-auto sections from sapi_code while match via line number
    # cast auto tokens to str and keep track of ekstra_code_length = length of auto code - length of replaced code
    # use token.start + ekstra_code_length and token.text or token.end + ekstra_code_length to map between tokens and str
    return "not yet implemented"


def _replace_from_with_not_from(sapi_str: str, tokens: list[Token]):
    pieces: list[str] = []
    last_piece_index = 0
    replacement = "not_from"
    for token in tokens:
        if token.token_type == TokenType.FROM:
            pieces.append(sapi_str[last_piece_index: token.start])
            pieces.append(replacement)
            last_piece_index = token.end + 1
    
    sql_str = ''.join(pieces)
    return sql_str

