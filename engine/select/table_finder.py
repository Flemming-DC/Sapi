from engine.hardcodedTrees import table_by_var, table_tree_names, tree_by_table
from engine.tokenizer import Token, TokenTree, TokenType, ParserError
from .table_tree_data import JoinData

def get_tables(tokens: list[Token|TokenTree]) -> list[JoinData]:
    joinData: list[JoinData] = []
    tables: list[str] = [] # evt. a list of Nodes
    prefix: list[Token] = []
    count = len(tokens)
    i = -1 # start at -1 to undo the effect of the initial increment.
    while i < count - 1:
        i += 1
        if isinstance(tokens[i], TokenTree):
            continue
        i = _make_join_data(tokens, i, joinData)
        if tokens[i].token_type not in [TokenType.IDENTIFIER, TokenType.VAR]:
            continue
        if _table_from_prefix(tokens, i, prefix, tables):
            continue
        if _table_from_variable(tokens[i], tables):
            i = _insert_table_prefix(tokens, i)
        count = len(tokens) # unnesesary work

    _plug_tables_into_joinData(tables, joinData)
        
    return joinData


# missing: tab in table_trees, restrict namespace to resolve ambiguities.
def _table_from_prefix(tokens: list[Token], i: int, prefix: list[Token], tables: list[str]) -> bool:
    """
    Returns true if we are handling the prefix and therefore shouldn't try to get table from column.
    Each call to _table_from_prefix will update the prefix and 
    If tree.var is encountered, then the tree is resolved into a variable.
    """
    # if next token is dot, extend prefix
    if i + 1 < len(tokens) and tokens[i + 1].token_type == TokenType.DOT:
        prefix.append(tokens[i]) 
        return True
    # no prefix is present, so we report that we aren't handling any prefix
    if not prefix:
        return False
    # otherwise finish prefix if present
    tab_or_tree: Token = prefix[-1] 
    prefix.clear()
    if tab_or_tree.text in table_tree_names:
        _set_prefix_to_table(tokens, i, tab_or_tree)
    else:
        # This includes views and cte's as tables. Is that okay?
        tables.append(tab_or_tree.text) 
        return True
        

def _table_from_variable(token: Token, tables: list[str]) -> bool:
    "returns true if table found. If table is new, then it is inserted."
    if token.text not in table_by_var.keys(): # is var
        return False
    tab = table_by_var[token.text] # requires that there is a unique table, which contains var
    if tab not in tables:
        tables.append(tab)
    return True



def _make_join_data(tokens: list[Token], i: int, joinData: list[JoinData]) -> int:
    if tokens[i].token_type not in [TokenType.FROM, TokenType.JOIN]:
        return i
    i += 1 # goto join_obj (or its prefix)
    if tokens[i].token_type not in [TokenType.VAR, TokenType.IDENTIFIER]:
        raise ParserError("expected identifier or variable after from / join.")
    
    # pass through join_obj prefix
    while i + 1 < len(tokens) and tokens[i + 1].token_type == TokenType.DOT:
        i += 2 # for A.B.C, we hit A, see the dot, goto B, see the . and goto C

    join_obj = tokens[i] # join_obj at end of join_obj prefixes
    if any(j.join_obj == join_obj for j in joinData):
        return i
    is_tree = join_obj.text in table_tree_names
    joinData.append(JoinData(join_obj=join_obj, is_tree=is_tree))
    return i

def _set_prefix_to_table(tokens: list[Token], i: int, prefixed_tree: Token):
    if tokens[i - 2] != prefixed_tree:
        raise ParserError(f"expected table_tree token as in tree.var, but found {tokens[i - 2]}")
    tokens[i - 2] = Token(
        token_type = TokenType.VAR, # TokenType.VAR or TokenType.IDENTIFIER
        text       = table_by_var[tokens[i].text], 
        line       = prefixed_tree.line,
        col        = prefixed_tree.col,
        start      = prefixed_tree.start,
        end        = prefixed_tree.end,
        )

def _insert_table_prefix(tokens: list[Token], i: int) -> int:
    token = tokens[i]
    # TokenType.VAR or TokenType.IDENTIFIER
    table = Token(TokenType.VAR, table_by_var[token.text],
                  token.line, token.col, token.start, token.end)
    dot = Token(TokenType.DOT, '.',
                  token.line, token.col, token.start, token.end)
    tokens[i:i] = [table, dot]
    i += 2
    return i

def _plug_tables_into_joinData(tables: list[str], joinData: list[JoinData]):
    for tab_name in tables:
        if tab_name not in tree_by_table.keys():
            continue # this happens for cte's and probably views.
        tree_name = tree_by_table[tab_name] # this persumes a table->tree map. Thus you can't have multiple trees containing the same table
        for j in joinData:
            if j.join_obj.text == tree_name:
                j.tables.append(tab_name)
                break

