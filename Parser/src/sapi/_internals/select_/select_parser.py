from . import select_analyzer, path_finder, join_generator
from sapi._internals.token_tree import TokenTree
from sapi._internals.dyn_loop import DynLoop


def parse_select(token_tree: TokenTree) -> TokenTree:

    tree_joins = select_analyzer.find_tree_joins(DynLoop(token_tree))
    for tree_join in tree_joins:
        path, eldest = path_finder.join_path(tree_join.referenced_tables, tree_join.first_table, tree_join.tree_tok.text)
        join_generator.make_join_clauses(token_tree, tree_join, path, eldest)

    return token_tree


