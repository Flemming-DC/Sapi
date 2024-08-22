from . import table_finder, path_finder, join_generator
from engine.tokenizer import TokenTree

def parse_select(token_tree: TokenTree) -> TokenTree:
    print(f'sapi_token_tree: {token_tree}')

    joinData = table_finder.get_tables(token_tree.tokens)
    # print(f'tables: {table_names}')
    
    for i, joinDatum in enumerate(joinData):
        # print('on_clause_end_index: ', ' '.join(
        #     [t.text for t in token_tree.tokens[joinDatum.on_clause_end_index - 1 : joinDatum.on_clause_end_index + 2]]))
        if not joinDatum.is_tree:
            continue
        # table_nodes = [hardcodedTrees.node_by_table[tab] for tab in joinDatum.tables
        #             if tab in hardcodedTrees.node_by_table.keys()]
        previous = joinData[i - 1].join_obj.text if i > 0 else None
        pathInfo = path_finder.join_path(joinDatum.tables, previous)
        print('path:')
        for from_, to_ in pathInfo.path:
            print(f"    {from_.name}, {to_.name}")
        
        token_tree.tokens = join_generator.make_from_clause(token_tree.tokens, pathInfo)
        print(f'sql_token_tree: {token_tree}')


    print('--- done parsing select ---\n')
    return token_tree


