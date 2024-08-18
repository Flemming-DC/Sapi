from . import table_finder, path_finder, join_generator
from engine import hardcodedTrees
from engine.tokenizer import TokenTree

def parse_select(token_tree: TokenTree) -> TokenTree:
    print(f'sapi_token_tree: {token_tree}')

    table_names = table_finder.get_tables(token_tree.tokens)
    print(f'tables {table_names}')
    
    table_nodes = [hardcodedTrees.node_by_table[tab] for tab in table_names
                   if tab in hardcodedTrees.node_by_table.keys()]
    pathInfo = path_finder.join_path(table_nodes)
    print('path:')
    for from_, to_ in pathInfo.path:
        print(f"    {from_.name}, {to_.name}")
    
    from_clause = join_generator.make_from_clause(pathInfo)
    print(f'from_clause: {from_clause}')

    # overwrite from clause
    # print(f'sql_token_tree: {token_tree}')

    print()

    print('--- done parsing select ---')
    return token_tree


