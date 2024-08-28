from .path_finder import PathInfo
from engine.token_tree import TokenType, Token, ParserError
from .tree_join import TreeJoin
from engine.dyn_loop import DynLoop


def make_from_clause(tokens: list[Token], pathInfo: PathInfo, loop: DynLoop, tree_join: TreeJoin) -> list[Token]: 
    print(tree_join)

    join_obj_index = [i for i, tok in enumerate(tokens) if tok == tree_join.join_obj]
    if len(join_obj_index) != 1:
        ParserError("Expected presicely one join_obj_index")
    join_obj_index = join_obj_index[0]
    on_clause_end_index = tree_join.on_clause_end_index

    tokens = _make_join_clause(tokens, join_obj_index, pathInfo, on_clause_end_index, loop)

    return tokens

c = [0]
def _make_join_clause(tokens: list[Token], join_obj_index: int, pathInfo: PathInfo, on_clause_end_index: int, loop: DynLoop) -> list[Token]:
    path_tables = pathInfo.nodes
    path = pathInfo.path
    # table_tree = tokens[join_obj_index] # this is the table_tree for which we are autogenerating the from clause
    # convert back to str instead of using node?
    assert not path_tables or len(path_tables) == len(path) + 1, "Expected table count to be 0 or 1 + path length"
    if path == [] and len(path_tables) == 0:
        return '' # nothing to join

    c[0] += 1
    print(c[0])
    loop.set_index(join_obj_index) # dirty
    loop.replace((TokenType.VAR, path_tables[0].name))

    i = on_clause_end_index + 1
    loop.set_index(i) # dirty

    # autogenerate the remaining joins in join_path
    going_up_the_tree = True
    for tab, next_tab in path:
        if tab == pathInfo.eldest:
            going_up_the_tree = False
        # check for alternative join clauses in the tree
        # this code assumes that foreign key and primary keys follow your naming convention.
        referenced_table = next_tab if going_up_the_tree else tab
        
        # this assumes a very specific sort of join clause
        loop.insert([
            (TokenType.JOIN, 'JOIN'), 
            (TokenType.VAR, next_tab.name), 
            (TokenType.USING, 'USING'), 
            (TokenType.L_PAREN, '('), 
            (TokenType.VAR, referenced_table.name + '_id'), 
            (TokenType.R_PAREN, ')'), 
            ])
    
    return tokens




