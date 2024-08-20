from engine.hardcodedTrees import table_by_var, table_trees
from engine.tokenizer import Token, TokenTree, TokenType, ParserError


def get_tables(tokens: list[Token|TokenTree]) -> list[str]:
    tables: list[str] = [] # evt. a list of Nodes
    prefix: list[Token] = []
    for i, token in enumerate(tokens):
        if isinstance(token, TokenTree):
            continue
        if token.token_type not in [TokenType.IDENTIFIER, TokenType.VAR]:
            continue

        if _table_from_prefix(tokens, token, i, prefix, tables):
            continue
        _table_from_variable(token, tables)
        
    return tables


# missing: tab in table_trees, restrict namespace to resolve ambiguities.
def _table_from_prefix(tokens: list[Token], token: Token, i: int, prefix: list[Token], tables: list[str]) -> bool:
    """
    Returns true if we are handling the prefix and therefore shouldn't try to get table from column.
    Each call to _table_from_prefix will update the prefix and 
    If tree.var is encountered, then the tree is resolved into a variable.
    """
    # if next token is dot, extend prefix
    if i + 1 < len(tokens) and tokens[i + 1].token_type == TokenType.DOT:
        prefix.append(token) 
        return True
    # otherwise finish prefix if present
    if prefix:
        tab_or_tree = prefix[-1]
        prefix.clear()
        if tab_or_tree.text in table_trees:
            tree = tab_or_tree
            if tokens[i - 2] != tree:
                raise ParserError(f"expected table_tree token as in tree.var, but found {tokens[i - 2]}")
            tokens[i - 2] = Token(
                token_type = TokenType.VAR, # TokenType.VAR or TokenType.IDENTIFIER
                text       = table_by_var[token.text], 
                line       = tree.line,
                col        = tree.col,
                start      = tree.start,
                end        = tree.end,
                )
            # instead of storing trees_dot_vars, then replace tree.var with tab.var
            # missing: tab in table_trees, restrict namespace to resolve ambiguities.
        else: 
            tables.append(tab_or_tree.text)
            return True
        
    # no prefix is present, so we report that we aren't handling any prefix
    return False 

def _table_from_variable(token: Token, tables: list[str]):
    if token.text in table_by_var.keys(): # is var
        tab = table_by_var[token.text]
        if tab not in tables:
            tables.append(tab)




