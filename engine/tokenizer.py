from __future__ import annotations
from sqlglot import Dialect
from .token_tree import TokenTree, Token, TokenType, ParserError
from engine.dyn_loop import DynLoop



_dialect = Dialect.get_or_raise("postgres") # dialekt bør gribes fra et config object


def tokenize(sapi_str: str) -> list[TokenTree]:
    tokens: list[Token] = _dialect.tokenize(sapi_str)
    statements: list[str] = sapi_str.split(';')

    i = 0
    count = len(tokens)
    trees: list[TokenTree] = []
    while i < count - 1:
        token_tree, i = _parse_token_tree(tokens, i, statements[i]) # tokens is not modified, only i
        trees.append(token_tree)
        i += 1
    if len(statements) != len(trees):
        raise ParserError("number of statements and number of root level token trees should match.")

    return trees

    


def _parse_token_tree(all_tokens: list[Token], i: int, sapi_str: str) -> tuple[TokenTree, int]:
    if all_tokens[i].token_type == TokenType.L_PAREN:
        ParserError("TokenTree should not start with (") 
    depth = 0 # parenthesis nesting depth
    token_count = len(all_tokens)
    tokens_at_this_level: list[Token] = []

    def _continue(i: int, depth: int): 
        if i >= token_count: 
            return False
        depth_goes_negative = (all_tokens[i].token_type == TokenType.R_PAREN and depth == 0)
        return all_tokens[i].token_type != TokenType.SEMICOLON and not depth_goes_negative
       
    
    while _continue(i, depth):
        token = all_tokens[i]
        match token.token_type:
            case TokenType.L_PAREN: depth += 1 # evt. check if next token if a sub query start
            case TokenType.R_PAREN: depth -= 1
            case TokenType.SELECT | TokenType.INSERT | TokenType.UPDATE | TokenType.DELETE: 
                if depth > 0: # we don't want to recursively parse the outermost select
                    sub_tree, i = _parse_token_tree(all_tokens, i, sapi_str)
                    token = sub_tree
        tokens_at_this_level.append(token) # token can be overridden by a sub_tree
        i += 1
    i -= 1 # dont include finishing parenthesis
    dyn_loop = DynLoop(tokens_at_this_level, sapi_str)
    token_tree = TokenTree(tokens_at_this_level, dyn_loop)
    return token_tree, i


