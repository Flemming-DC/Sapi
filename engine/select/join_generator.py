from engine.token_tree import TokenType, TokenTree
from engine.dialect import blank_from_clause, dialect_str
from .path_finder import pathType, Node
from .tree_join import TreeJoin


def make_join_clauses(token_tree: TokenTree, tree_join: TreeJoin, path: pathType, eldest: Node|None): 
    i = tree_join.tree_tok_index
    if not tree_join.first_table:
        # replace A with a "blank" from clause, such as "from dual" in Oracle or "" in postgres
        # note that replacing from i + 1 to i + 1 is including the lower bound, but excluding the upper bound
        token_tree.replace(i - 1, i + 1, blank_from_clause[dialect_str])
        return

    # replace table_tree with first table in join_path
    token_tree.replace(i, i + 1, [(TokenType.VAR, tree_join.first_table)])

    # autogenerate the remaining joins in join_path
    i = tree_join.on_clause_end_index + 1
    going_up_the_tree = True
    for tab, next_tab in path:
        if tab == eldest: # eldest is only None if there are no referenced tables, and that doesn't happen here.
            going_up_the_tree = False
        referenced_table = next_tab if going_up_the_tree else tab

        # check for alternative join clauses in the tree
        # this code assumes that foreign key and primary keys follow your naming convention.
        # in the general case, then you need tab, next_tab, referenced_table and a join rule to make join_clause_tokens
        join_clause_tokens = [
            (TokenType.JOIN, 'JOIN'), 
            (TokenType.VAR, next_tab.name), 
            (TokenType.USING, 'USING'), 
            (TokenType.L_PAREN, '('), 
            (TokenType.VAR, referenced_table.name + '_id'), 
            (TokenType.R_PAREN, ')'), 
            ]
        token_tree.replace(i, i, join_clause_tokens) # equivalent to insert
        i += len(join_clause_tokens)
    


