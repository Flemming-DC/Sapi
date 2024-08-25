from . import table_finder, path_finder, join_generator
from engine.token_tree import TokenTree


def parse_select(token_tree: TokenTree) -> TokenTree:
    print('---')
    # print(f'sapi_token_tree: {token_tree}')
    sapi_joins = table_finder.get_tables(token_tree.tokens, token_tree.dyn_loop)
    tree_joins = [j for j in sapi_joins if j.is_tree]

    # print(f'tables: {table_names}')
    # token_tree.tokens = token_tree.dyn_loop.get_tokens()
    # token_tree.dyn_loop.reset()

    
    for tree_join in tree_joins:
        # print('on_clause_end_index: ', ' '.join(
        #     [t.text for t in token_tree.tokens[joinDatum.on_clause_end_index - 1 : joinDatum.on_clause_end_index + 2]]))
        pathInfo = path_finder.join_path(tree_join.tables, tree_join.first_table)
        # print('path:')
        # for from_, to_ in pathInfo.path:
        #     print(f"    {from_.name}, {to_.name}")
        
        token_tree.tokens = join_generator.make_from_clause(
            token_tree.tokens, pathInfo, token_tree.dyn_loop, tree_join)
        # print(f'sql_token_tree: {token_tree}')


    # print('--- done parsing select ---\n')
    return token_tree


