from .path_finder import PathInfo


def make_from_clause(pathInfo: PathInfo) -> list[str]: # returns tokes or str ?
    tables = pathInfo.nodes
    path = pathInfo.path
    # convert back to str instead of using node?
    assert not tables or len(tables) == len(path) + 1, "Expected table count to be 0 or 1 + path length"
    if path == [] and len(tables) == 0:
        return '' # nothing to join
    if path == [] and len(tables) == 1:
        return f'\nfrom {tables[0].name}\n'

    from_clause = f'\nfrom {tables[0].name}\n' # what if there is already a hard_coded table before the tree?
    going_up_the_tree = True
    for tab, next_tab in path:
        if tab == pathInfo.eldest:
            going_up_the_tree = False
        # check for alternative join clauses in the tree
        # this code assumes that foreign key and primary keys follow your naming convention.
        referenced_table = next_tab if going_up_the_tree else tab
        from_clause += f'join {next_tab.name} using ({referenced_table.name}_id)\n'
        
    return from_clause


# def make_sql_str(select: Select, from_clause: list[str]) -> str:
#     # what if we have to preserve some pre-existing pieces of a from clause?
#     before = select.tokens[0: select.from_clause_start]
#     after = select.tokens[select.from_clause_end: -1]
#     # select.tokens = before + from_clause_tokens + after
#     sql_str = ' '.join(before) + from_clause + ' '.join(after)
#     return sql_str


