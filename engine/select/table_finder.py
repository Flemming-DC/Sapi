from textwrap import dedent
from engine.hardcodedTrees import table_by_var, table_tree_names, tree_by_table
from engine.token_tree import Token, TokenTree, TokenType, ParserError, AutoToken
from .tree_join import TreeJoin
from engine.dyn_loop import DynLoop

def get_tables(loop: DynLoop) -> list[TreeJoin]:
    joinData: list[TreeJoin] = []
    tables: list[str] = [] # evt. a list of Nodes
    while loop.next():
        if isinstance(loop.tok(), TokenTree):
            continue
        _make_join_data(joinData, loop)
        if not loop.found([TokenType.IDENTIFIER, TokenType.VAR], 0):
            continue
        if _table_from_prefix(tables, loop):
            continue
        if _table_from_variable(loop.tok(), tables):
            _insert_table_prefix(loop)

    _plug_tables_into_joinData(tables, joinData)
    return joinData



def _make_join_data(joinData: list[TreeJoin], loop: DynLoop):
    if not loop.found([TokenType.FROM, TokenType.JOIN], 0):
        return
    loop.next()
    if not loop.found([TokenType.VAR, TokenType.IDENTIFIER], 0):
        raise ParserError("expected identifier or variable after from / join.")
    
    # pass through join_obj prefix
    while loop.found(TokenType.DOT, 1):
        loop.next()
        loop.next()

    if loop.at_end():
        raise ParserError("Encountered end of query while passing through prefix. Expected join_obj instead.")

    join_obj = loop.tok() # join_obj at end of join_obj prefixes
    if any(j.join_obj == join_obj for j in joinData):
        return # don't dublicate join_data
    is_tree = join_obj.text in table_tree_names

    def _on_clause_done(): 
        return loop.at_end(1) or loop.found([ # join or clause-after-from
            TokenType.JOIN, TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.OUTER, 
            TokenType.FULL, TokenType.SEMI, TokenType.ANTI, TokenType.LATERAL, TokenType.CROSS, 
            TokenType.CROSS, TokenType.NATURAL,
            TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.WINDOW, TokenType.UNION, 
            TokenType.ORDER_BY, TokenType.LIMIT, TokenType.OFFSET, TokenType.FETCH, TokenType.FOR], after_steps=1)

    # resolve tree prefixes and record table prefixes in on clause
    on_clause_tables: list[str] = []
    while not _on_clause_done():
        loop.next()
        
        if loop.tok().text in table_tree_names: # is tree
            if not loop.found([TokenType.VAR, TokenType.IDENTIFIER], 2): # peek(2) should be column
                raise ParserError("Expected column after tree, as in tree.column") # why not table?
            tab_of_var = table_by_var[loop.peek(2).text] 
            loop.replace([(TokenType.VAR, tab_of_var)]) # replace tree prefix with table prefix
        if loop.tok().text in tree_by_table.keys(): # is table
            on_clause_tables.append(loop.tok().text) # register table in on clause

    if is_tree:
        joinData.append(TreeJoin(
            join_obj=join_obj, on_clause_end_index=loop.index(), on_clause_tables=on_clause_tables))
    

def _table_from_prefix(tables: list[str], loop: DynLoop) -> bool:
    """
    Returns true if we are handling the prefix and therefore shouldn't try to get table from column.
    Each call to _table_from_prefix will update the prefix and 
    If tree.var is encountered, then the tree is resolved into a variable.
    """
    if not loop.found(TokenType.DOT, -1):
        return False
    tab_or_tree: Token = loop.peek(-2) # This includes views and cte's as tables. Is that okay?
    if tab_or_tree.text in table_tree_names:
        text = table_by_var[loop.tok().text]
        loop.insert([(TokenType.VAR, text)], distance = -2)
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

def _insert_table_prefix(loop: DynLoop):
    if loop.found(TokenType.DOT, -1):
        raise ParserError("Trying to insert a table prefix in a variable that already has a prefix")
    loop.insert([
        (TokenType.VAR, table_by_var[loop.tok().text]), 
        (TokenType.DOT, '.')])
    


def _plug_tables_into_joinData(tables: list[str], joinData: list[TreeJoin]):
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
        

