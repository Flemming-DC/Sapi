from .path_finder import PathInfo
from engine.tokenizer import TokenTree, TokenType, Token, flat_tokenize, TOKENTYPE_AUTO_JOIN
from engine.hardcodedTrees import table_trees

# skip joins that don't mention any trees 
# if joining tree, generate join-clauses for tree.
# at end of loop, replace first join with from


def make_from_clause(token_tree: TokenTree, pathInfo: PathInfo) -> list[str]: # returns tokes or str ?
    # from_index = None
    for i, token in enumerate(token_tree.tokens):

        if token.token_type in [TokenType.VAR, TokenType.IDENTIFIER]:
            if token.text in table_trees:
                _make_join_clause(token, pathInfo)

        # # loop until hitting from clause
        # # if isinstance(token, TokenTree):
        # #     continue
        # if token.token_type == TokenType.FROM:
        #     from_index = i
        #     if len(token_tree.tokens) > 5:
        #         pass
        # if from_index is None:
        #     continue
        
        # skip joins that don't mention any trees 

    return

def _make_join_clause(tokens: list[Token], i: int, pathInfo: PathInfo):
    tables = pathInfo.nodes
    path = pathInfo.path
    table_tree = tokens[i]
    # convert back to str instead of using node?
    assert not tables or len(tables) == len(path) + 1, "Expected table count to be 0 or 1 + path length"
    
    if path == [] and len(tables) == 0:
        return '' # nothing to join

    # can the first table in path be assumed to fit the on clause of the tree as a whole?
    table_at_tree_location = tables[0].name

    # pass through ON clause i.e. until hitting join or end of from
    tree_on_clause = ""
    for tok in tokens:
        on_clause_done = tok.token_type in [ # join or clause-after-from
            TokenType.JOIN, TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.OUTER, 
            TokenType.FULL, TokenType.SEMI, TokenType.ANTI, TokenType.LATERAL, TokenType.CROSS, 
            TokenType.CROSS, TokenType.NATURAL,
            TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.WINDOW, TokenType.UNION, 
            TokenType.ORDER_BY, TokenType.LIMIT, TokenType.OFFSET, TokenType.FETCH, TokenType.FOR]
        if on_clause_done:
            break
        else:
            tree_on_clause += " " + tok.text
            tok.text

    # autogenerate the remaining joins in join_path
    joins = ''
    going_up_the_tree = True
    for tab, next_tab in path:
        if tab == pathInfo.eldest:
            going_up_the_tree = False
        # check for alternative join clauses in the tree
        # this code assumes that foreign key and primary keys follow your naming convention.
        referenced_table = next_tab if going_up_the_tree else tab
        joins += f'join {next_tab.name} using ({referenced_table.name}_id)\n'
    
    # perhaps tree_on_clause should be moved into joins?
    auto_join_str = table_at_tree_location + tree_on_clause + joins
    tokens[i] = Token(
        token_type = TOKENTYPE_AUTO_JOIN,
        text       = auto_join_str, 
        line       = table_tree.line,
        col        = table_tree.col,
        start      = table_tree.start,
        end        = table_tree.end,
        )

    return tokens, i


def _make_join(table_tree: Token, table_name: str):
    def _token(type: TokenType, text: str = None) -> Token:
        text = text if text else type.name
        return Token(type, text, table_tree.line, table_tree.col, table_tree.start, table_tree.end)
    return [
        _token(TokenType.JOIN), 
        _token(TokenType.VAR, table_name), 
        _token(TokenType.USING), 
        _token(TokenType.L_PAREN), 
        _token(TokenType.VAR, table_name + '_id'), 
        _token(TokenType.R_PAREN), 
    ]



def _make_table_token(table_name: str, table_tree: Token) -> Token:
    return Token(
        token_type = TokenType.VAR, # TokenType.VAR or TokenType.IDENTIFIER
        text       = table_name, 
        line       = table_tree.line,
        col        = table_tree.col,
        start      = table_tree.start,
        end        = table_tree.end,
        )



def make_from_clause_old(pathInfo: PathInfo) -> list[str]: # returns tokes or str ?
    tables = pathInfo.nodes
    path = pathInfo.path
    # convert back to str instead of using node?
    assert not tables or len(tables) == len(path) + 1, "Expected table count to be 0 or 1 + path length"
    if path == [] and len(tables) == 0:
        return '' # nothing to join
    if path == [] and len(tables) == 1:
        return f'\nfrom {tables[0].name}\n'

    from_clause = f'\nfrom {tables[0].name}\n' # what if there is already a hard_coded table before the tree?
    going_up_the_tree = True
    for tab, next_tab in path:
        if tab == pathInfo.eldest:
            going_up_the_tree = False
        # check for alternative join clauses in the tree
        # this code assumes that foreign key and primary keys follow your naming convention.
        referenced_table = next_tab if going_up_the_tree else tab
        from_clause += f'join {next_tab.name} using ({referenced_table.name}_id)\n'
        
    return from_clause


# def make_sql_str(select: Select, from_clause: list[str]) -> str:
#     # what if we have to preserve some pre-existing pieces of a from clause?
#     before = select.tokens[0: select.from_clause_start]
#     after = select.tokens[select.from_clause_end: -1]
#     # select.tokens = before + from_clause_tokens + after
#     sql_str = ' '.join(before) + from_clause + ' '.join(after)
#     return sql_str




