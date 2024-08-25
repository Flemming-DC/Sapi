from .path_finder import PathInfo
from engine.token_tree import TokenType, Token, ParserError, AutoToken
from .join_data import JoinData
from engine.dyn_loop import DynLoop


def make_from_clause(tokens: list[Token], pathInfo: PathInfo, loop: DynLoop, tree_join: JoinData) -> list[Token]: 
    print(tree_join)

    join_obj_index = [i for i, tok in enumerate(tokens) if tok == tree_join.join_obj]
    if len(join_obj_index) != 1:
        ParserError("Expected presicely one join_obj_index")
    join_obj_index = join_obj_index[0]

    tokens = _make_join_clause(tokens, join_obj_index, pathInfo, tree_join)

    return tokens


def _make_join_clause(tokens: list[Token], join_obj_index: int, pathInfo: PathInfo, tree_join: JoinData) -> list[Token]:
    tables = pathInfo.nodes
    path = pathInfo.path
    table_tree = tokens[join_obj_index] # this is the table_tree for which we are autogenerating the from clause
    # convert back to str instead of using node?
    assert not tables or len(tables) == len(path) + 1, "Expected table count to be 0 or 1 + path length"
    
    if path == [] and len(tables) == 0:
        return '' # nothing to join

    # can the first table in path be assumed to fit the on clause of the tree as a whole?
    first_table = _make_table_token(tables[0].name, table_tree)
    tokens[join_obj_index] = first_table

    # pass through ON clause i.e. until hitting join or end of from
    i = tree_join.on_clause_end_index + 1

    # autogenerate the remaining joins in join_path
    going_up_the_tree = True
    for tab, next_tab in path:
        if tab == pathInfo.eldest:
            going_up_the_tree = False
        # check for alternative join clauses in the tree
        # this code assumes that foreign key and primary keys follow your naming convention.
        referenced_table = next_tab if going_up_the_tree else tab
        join_tokens = _make_join(next_tab.name, referenced_table.name, table_tree)

        tokens[i:i] = join_tokens
        i += len(join_tokens)
    
    return tokens


def _make_join(next_tab: str, referenced_table: str, table_tree: Token):
    'join {next_tab} using ({referenced_table}_id)\n'
    def _token(type: TokenType, text: str = None) -> Token:
        text = text if text else type.name
        return AutoToken(type, text, table_tree.line, table_tree.col, table_tree.start, table_tree.end)
    return [
        _token(TokenType.JOIN), 
        _token(TokenType.VAR, next_tab), 
        _token(TokenType.USING), 
        _token(TokenType.L_PAREN, '('), 
        _token(TokenType.VAR, referenced_table + '_id'), 
        _token(TokenType.R_PAREN, ')'), 
    ]


def _make_table_token(table_name: str, table_tree: Token) -> Token:
    return AutoToken(
        token_type = TokenType.VAR, # TokenType.VAR or TokenType.IDENTIFIER
        text       = table_name, 
        line       = table_tree.line,
        col        = table_tree.col,
        start      = table_tree.start,
        end        = table_tree.end,
        )





