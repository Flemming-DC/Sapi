# from sqlglot import Dialect
from .token_tree import TokenTree, Token, TokenType, ParserError
from sapi._internals.externals.database_py import data_model


# _dialect = Dialect.get_or_raise(dialect.current.dialect_str) # dialekt bør gribes fra et config object


def tokenize(sapi_stmt: str) -> TokenTree:
    tokens: list = data_model.dialect().sqlglot_dialect().tokenize(sapi_stmt) 
    # tokens is a list of builtins.token, which seems to behave like Token, except for type checks.
    # cast to sqlglot.tokens.Token and drop the unreliable token.end. evt. drop all the unused stuff.
    tokens: list[Token] = [Token(t.token_type, t.text, t.line, t.col, t.start, None, t.comments) for t in tokens]

    tree, _ = _make_nested_tok_tree(tokens, 0, sapi_stmt)
    return tree

    


def _make_nested_tok_tree(all_tokens: list[Token], i: int, sapi_str: str) -> tuple[TokenTree, int]:
    if all_tokens[i].token_type == TokenType.L_PAREN:
        ParserError("TokenTree should not start with (") 
    depth = 0 # parenthesis nesting depth
    token_count = len(all_tokens)
    tokens_at_this_level: list[Token] = []

    def _continue(i: int, depth: int): 
        if i >= token_count: 
            return False
        depth_goes_negative = (all_tokens[i].token_type == TokenType.R_PAREN and depth <= 0)
        return all_tokens[i].token_type != TokenType.SEMICOLON and not depth_goes_negative
       
    
    while _continue(i, depth):
        token = all_tokens[i]
        match token.token_type:
            case TokenType.L_PAREN: depth += 1 # evt. check if next token if a sub query start
            case TokenType.R_PAREN: depth -= 1
            # case TokenType.SEMICOLON: depth = -1000 # exit tokentree
            case TokenType.SELECT | TokenType.INSERT | TokenType.UPDATE | TokenType.DELETE: 
                if depth > 0: # we don't want to recursively parse the outermost select
                    sub_tree, i = _make_nested_tok_tree(all_tokens, i, sapi_str)
                    token = sub_tree
        tokens_at_this_level.append(token) # token can be overridden by a sub_tree
        i += 1
    if i < len(all_tokens) and all_tokens[i].token_type == TokenType.R_PAREN:
        i -= 1 # dont include finishing parenthesis
    next_token = all_tokens[i + 1] if i + 1 < len(all_tokens) else None

    # make single layer of token_tree
    token_tree = TokenTree(tokens_at_this_level, sapi_str, next_token)
    return token_tree, i


