from . import select_analyzer, path_finder, join_generator
from sapi._internals.token_tree import TokenTree, StrReplacement
from sapi._internals.select_.analyzer_loop import AnalyzerLoop

def parse_select(token_tree: TokenTree) -> list[StrReplacement]:
    tree_joins, resolvents = select_analyzer.find_tree_joins(AnalyzerLoop(token_tree))

    join_generator.resolve_trees_to_tabs(token_tree, resolvents)
    for tree_join in tree_joins:
        path, eldest = path_finder.join_path(tree_join.referenced_tables, tree_join.first_table, tree_join.tree_tok.text)
        join_generator.make_join_clauses(token_tree, tree_join, path, eldest)


    replacements = token_tree.recursive_str_replacements()
    # sql = make_str(sapi_stmt, replacements)
    return replacements


