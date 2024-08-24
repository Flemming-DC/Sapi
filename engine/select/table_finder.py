from textwrap import dedent
from engine.hardcodedTrees import table_by_var, table_tree_names, tree_by_table
from engine.token_tree import Token, TokenTree, TokenType, ParserError, AutoToken
from .join_data import JoinData
from engine.has_passed import has_passed
from engine.dyn_loop import DynLoop

def get_tables(tokens: list[Token|TokenTree], dyn_loop: DynLoop) -> list[JoinData]:
    joinData: list[JoinData] = []
    tables: list[str] = [] # evt. a list of Nodes
    count = len(tokens)
    i = -1 # start at -1 to undo the effect of the initial increment.
    while i < count - 1:
        i += 1
        if isinstance(tokens[i], TokenTree):
            continue
        i = _make_join_data(tokens, i, joinData, count)
        if i >= count or tokens[i].token_type not in [TokenType.IDENTIFIER, TokenType.VAR]:
            continue
        if _table_from_prefix(tokens, i, tables):
            continue
        if _table_from_variable(tokens[i], tables):
            i, count = _insert_table_prefix(tokens, i, count)

    _plug_tables_into_joinData(tables, joinData)
    
    return joinData


def _table_from_prefix(tokens: list[Token], i: int, tables: list[str]) -> bool:
    """
    Returns true if we are handling the prefix and therefore shouldn't try to get table from column.
    Each call to _table_from_prefix will update the prefix and 
    If tree.var is encountered, then the tree is resolved into a variable.
    """
    if i - 1 < 0 or tokens[i - 1].token_type != TokenType.DOT:
        return False
    tab_or_tree: Token = tokens[i - 2] # This includes views and cte's as tables. Is that okay?
    if tab_or_tree.text in table_tree_names:
        _set_prefix_to_table(tokens, i, tab_or_tree) # i is index of variable
    tables.append(tab_or_tree.text) 
    return True
        

def _table_from_variable(token: Token, tables: list[str]) -> bool:
    "returns true if table found. If table is new, then it is inserted."
    if token.text not in table_by_var.keys():
        return False
    tab = table_by_var[token.text] # requires that there is a unique table, which contains var
    if tab not in tables:
        tables.append(tab)
    return True



def _make_join_data(tokens: list[Token], i: int, joinData: list[JoinData], count: int) -> int:
    if tokens[i].token_type not in [TokenType.FROM, TokenType.JOIN]:
        return i
    i += 1 # goto join_obj (or its prefix)
    if tokens[i].token_type not in [TokenType.VAR, TokenType.IDENTIFIER]:
        raise ParserError("expected identifier or variable after from / join.")
    
    # pass through join_obj prefix
    while i + 1 < len(tokens) and tokens[i + 1].token_type == TokenType.DOT:
        i += 2 # for A.B.C, we hit A, see the dot, goto B, see the . and goto C
    if i >= count:
        raise ParserError("Encountered end of query while passing through prefix. Expection join_obj instead.")

    join_obj = tokens[i] # join_obj at end of join_obj prefixes
    if any(j.join_obj == join_obj for j in joinData):
        return i
    is_tree = join_obj.text in table_tree_names

    on_clause_tables: list[str] = []
    for _ in tokens[i:]:
        on_clause_done = i + 1 >= count or tokens[i + 1].token_type in [ # join or clause-after-from
            TokenType.JOIN, TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.OUTER, 
            TokenType.FULL, TokenType.SEMI, TokenType.ANTI, TokenType.LATERAL, TokenType.CROSS, 
            TokenType.CROSS, TokenType.NATURAL,
            TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.WINDOW, TokenType.UNION, 
            TokenType.ORDER_BY, TokenType.LIMIT, TokenType.OFFSET, TokenType.FETCH, TokenType.FOR]
        if on_clause_done: # done at end of on clause, not after passing it.
            break
        i += 1
        
        if tokens[i].text in table_tree_names:
            _set_prefix_to_table(tokens, i + 2, tokens[i]) # i + 2 is index of variable
        if tokens[i].text in tree_by_table.keys(): # is table
            on_clause_tables.append(tokens[i].text)
    

    joinData.append(JoinData(join_obj=join_obj, is_tree=is_tree, on_clause_end_index=i, on_clause_tables=on_clause_tables))
    return i

def _set_prefix_to_table(tokens: list[Token], i: int, prefixed_tree: Token):
    if tokens[i - 2] != prefixed_tree:
        raise ParserError(f"expected table_tree token as in tree.var, but found {tokens[i - 2]}")
    tokens[i - 2] = AutoToken(
        token_type = TokenType.VAR, # TokenType.VAR or TokenType.IDENTIFIER
        text       = table_by_var[tokens[i].text], 
        line       = prefixed_tree.line,
        col        = prefixed_tree.col,
        start      = prefixed_tree.start,
        end        = prefixed_tree.end,
        )

def _insert_table_prefix(tokens: list[Token], i: int, count: int) -> tuple[int, int]:
    if tokens[i - 1].token_type == TokenType.DOT:
        raise ParserError("Trying to insert a table prefix in a variable that already has a prefix")
    token = tokens[i]
    # TokenType.VAR or TokenType.IDENTIFIER
    table = AutoToken(TokenType.VAR, table_by_var[token.text],
                  token.line, token.col, token.start, token.end)
    dot = AutoToken(TokenType.DOT, '.',
                  token.line, token.col, token.start, token.end)
    tokens[i:i] = [table, dot]
    i += 2
    return i, count + 2


def _plug_tables_into_joinData(tables: list[str], joinData: list[JoinData]):
    for tab_name in tables:
        if tab_name not in tree_by_table.keys():
            continue # this happens for cte's and probably views.
        tree_name = tree_by_table[tab_name] # this persumes a table->tree map. Thus you can't have multiple trees containing the same table
        for j in joinData:
            if j.join_obj.text == tree_name:
                j.tables.append(tab_name)
                break
    prior_tables = []
    for j in joinData:
        new_tables = [t for t in j.on_clause_tables if t not in prior_tables]
        if len(new_tables) >= 2:
            raise SyntaxError(dedent(f"""
                Each tree-on-clause may reference at most one new table. 
                The on-clause of {j.join_obj} references {new_tables}.
                """))
        j.first_table = new_tables[0] if new_tables else None

        j.tables += [t for t in j.on_clause_tables if t not in j.tables]
        prior_tables += j.tables
        

