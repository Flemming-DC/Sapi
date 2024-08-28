from . import table_finder, path_finder, join_generator
from engine.token_tree import TokenTree
from engine.dyn_loop import DynLoop


def parse_select(token_tree: TokenTree) -> TokenTree:
    print('---')

    tree_joins = table_finder.get_tables(DynLoop(token_tree))
    for tree_join in tree_joins:
        path, eldest = path_finder.join_path(tree_join.referenced_tables, tree_join.first_table)
        join_generator.make_join_clauses(token_tree, tree_join, path, eldest)

    return token_tree


