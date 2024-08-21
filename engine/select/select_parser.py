from . import table_finder, path_finder, join_generator
from engine import hardcodedTrees
from engine.tokenizer import TokenTree

def parse_select(token_tree: TokenTree) -> TokenTree:
    print(f'sapi_token_tree: {token_tree}')

    joinData = table_finder.get_tables(token_tree.tokens)
    # print(f'tables: {table_names}')
    
    for joinDatum in joinData:
        if not joinDatum.is_tree:
            continue
        table_nodes = [hardcodedTrees.node_by_table[tab] for tab in joinDatum.tables
                    if tab in hardcodedTrees.node_by_table.keys()]
        pathInfo = path_finder.join_path(table_nodes)
        print('path:')
        for from_, to_ in pathInfo.path:
            print(f"    {from_.name}, {to_.name}")
        
        token_tree.tokens = join_generator.make_from_clause(token_tree.tokens, pathInfo)
        print(f'sql_token_tree: {token_tree}')


    print('--- done parsing select ---\n')
    return token_tree


