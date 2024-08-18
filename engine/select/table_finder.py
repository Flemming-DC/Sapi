from engine.hardcodedTrees import table_by_var, table_trees
from engine.tokenizer import Token, TokenTree, TokenType


def get_tables(tokens: list[Token|TokenTree]) -> list[str]:
    tables: list[str] = [] # evt. a list of Nodes
    prefix: list[str] = []
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
def _table_from_prefix(tokens: list[Token], token: Token, i: int, prefix: list[str], tables: list[str]) -> bool:
    """
    Returns true if we are handling the prefix and therefore shouldn't try to get table from column.
    Each call to _table_from_prefix will update the prefix and 

    """
    # if next token is dot, extend prefix
    if i + 1 < len(tokens) and tokens[i + 1].token_type == TokenType.DOT:
        prefix.append(token.text) 
        return True
    # otherwise finish prefix if present
    if prefix:
        tab = prefix[-1]
        prefix.clear()
        if tab not in table_trees: 
            tables.append(tab)
            return True
        # missing: tab in table_trees, restrict namespace to resolve ambiguities.
    # no prefix is present, so we report that we aren't handling any prefix
    return False 

def _table_from_variable(token: Token, tables: list[str]):
    if token.text in table_by_var.keys(): # is var
        tab = table_by_var[token.text]
        if tab not in tables:
            tables.append(tab)




