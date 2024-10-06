from textwrap import dedent
from sapi._internals.externals.database_py import data_model
from sapi._internals.token_tree import Token, TokenTree, TokenType, ParserError
from sapi._internals.dyn_loop import DynLoop
from .tree_join import TreeJoin

def find_tree_joins(loop: DynLoop) -> list[TreeJoin]:
    tree_joins: list[TreeJoin] = []
    tabs_in_on_clauses: list[list[str]] = [] # on_clause_tables_across_joins
    ref_tables: list[str] = []
    while loop.next():
        if isinstance(loop.tok(), TokenTree):
            continue
        tree_join, on_clause_tables_in_join = _make_tree_join(loop, [j.tree_tok for j in tree_joins])
        if tree_join:
            tree_joins.append(tree_join)
            tabs_in_on_clauses.append(on_clause_tables_in_join)
        if not loop.found([TokenType.IDENTIFIER, TokenType.VAR], 0):
            continue
        if _table_from_prefix(ref_tables, loop):
            continue
        _table_from_variable(ref_tables, loop)

    _plug_tables_into_tree_joins(ref_tables, tree_joins, tabs_in_on_clauses)
    return tree_joins



def _make_tree_join(loop: DynLoop, prior_join_objs: list[Token]) -> tuple[TreeJoin, list[str]] | tuple[None, None]:
    if not loop.found([TokenType.FROM, TokenType.JOIN], 0):
        return None, None
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
    join_obj_index = loop.index()
    if join_obj in prior_join_objs:
        return None, None # don't dublicate join_data (is that actually correct behaviour??)
    is_tree = data_model.is_tree(join_obj.text)

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
        # resolve tree prefixes
        if data_model.is_tree(loop.tok().text):
            if not loop.found([TokenType.VAR, TokenType.IDENTIFIER], 2): # peek(2) should be column
                raise ParserError("Expected column after tree, as in tree.column") # why not table?
            
            var = loop.peek(2).text
            tree = loop.tok().text
            tab = _get_table_from_var_and_tree(var, tree)
            if loop.tok().text == 'tree':
                ...
            loop.replace((TokenType.VAR, tab)) # replace tree prefix with table prefix
        # record table prefixes
        if data_model.is_table(loop.tok().text):
            if loop.tok().text == 'tab10':
                ...
            on_clause_tables.append(loop.tok().text) # register table in on clause
            
    if not is_tree:
        return None, None
    tree_join = TreeJoin(tree_tok=join_obj, tree_tok_index=join_obj_index, on_clause_end_index=loop.index())
    return tree_join, on_clause_tables
    

def _table_from_prefix(ref_tables: list[str], loop: DynLoop) -> bool:
    """
    Returns true if we are handling the prefix and therefore shouldn't try to get table from column.
    Each call to _table_from_prefix will update the prefix and 
    If tree.var is encountered, then the tree is resolved into a variable, if table is unique.
    """
    if not loop.found(TokenType.DOT, -1):
        return False
    tab_or_tree: Token = loop.peek(-2) # This includes views and cte's as tables. Is that okay?
    if data_model.is_tree(tab_or_tree.text):
        var = loop.tok().text
        tree = loop.peek(-2).text
        tab = _get_table_from_var_and_tree(var, tree)
        loop.replace((TokenType.VAR, tab), distance = -2) # replace tree prefix with table prefix
    
    if data_model.is_table(tab_or_tree.text) and tab_or_tree.text not in ref_tables:
        ref_tables.append(tab_or_tree.text) 
    return True
        

def _table_from_variable(ref_tables: list[str], loop: DynLoop) -> bool:
    "returns true if table found. If table is new, then it is inserted."
    # we assume unique tab. Is that okay?
    if not data_model.is_var(loop.tok().text):
        return
    var = loop.tok().text
    tabs_of_var = data_model.tables_by_var(var)
    if len(tabs_of_var) > 1:
        raise ParserError(f"There are multiple tables {tabs_of_var} with column {var}.")
    elif len(tabs_of_var) == 0:
        raise ParserError(f"The is no table with column {var}.")
    tab = tabs_of_var[0]

    if loop.found(TokenType.DOT, -1):
        raise ParserError("Trying to insert a table prefix in a variable that already has a prefix")
    if data_model.is_table(tab) and tab not in ref_tables:
        ref_tables.append(tab)
    loop.insert([
        (TokenType.VAR, tab), 
        (TokenType.DOT, '.')])

def _get_table_from_var_and_tree(var: str, tree: str) -> str:
    tabs = data_model.tables_by_var_and_tree(var, tree)
    if len(tabs) > 1:
        raise ParserError(f"The tree {tree} contains multiple tables {tabs} with column {var}.")
    elif len(tabs) == 0:
        raise ParserError(f"The tree {tree} does not contain any table with column {var}.")
    return tabs[0]



def _plug_tables_into_tree_joins(ref_tables: list[str], tree_joins: list[TreeJoin], tabs_in_on_clauses: list[str]):
    for tab_name in ref_tables:
        if data_model.is_table(tab_name): # this filters for cte's and probably views.
            _plug_ref_table_into_tree_join(tab_name, tree_joins)
    
    prior_tables = []
    for j, tabs_in_on_clause in zip(tree_joins, tabs_in_on_clauses):
        
        new_tables = [t for t in tabs_in_on_clause if t not in prior_tables]
        if len(new_tables) >= 2:
            raise SyntaxError(dedent(f"""
                Each tree-on-clause may reference at most one new table. 
                The on-clause of {j.tree_tok} references {new_tables}.
                """))
        # j.first_table can be None in a query like "select 1 from A"
        # min(j.referenced_tables) is the alphabetic minimum
        j.first_table = new_tables[0] if new_tables else min(j.referenced_tables) if j.referenced_tables else None

        prior_tables += j.referenced_tables


def _plug_ref_table_into_tree_join(table_name: str, tree_joins: list[TreeJoin]):
    trees_of_tab = data_model.trees_by_table(table_name)
    already_found = False
    for j in tree_joins:
        if j.tree_tok.text not in trees_of_tab:
            continue
        if already_found:
            raise ParserError(
                "You cannot have multiple trees in the same query, while using columns from a table that belongs to both. "
                f"table {table_name} belongs to {trees_of_tab}.")
        already_found = True
    
        j.referenced_tables.append(table_name)
        if len(trees_of_tab) == 1:
            break # this break is an optimization