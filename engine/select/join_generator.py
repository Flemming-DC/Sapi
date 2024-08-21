from .path_finder import PathInfo
from engine.tokenizer import TokenType, Token, ParserError
from engine.hardcodedTrees import table_tree_names, table_by_var
from .join_data import JoinData



def make_from_clause(tokens: list[Token], pathInfo: PathInfo) -> list[Token]: 
    i = 0
    count = len(tokens)
    while i < count:
        if tokens[i].token_type in [TokenType.FROM, TokenType.JOIN]:
            i += 1
            if tokens[i].token_type not in [TokenType.VAR, TokenType.IDENTIFIER]:
                raise ParserError("expected identifier or variable after from / join.")
            if tokens[i].text in table_tree_names:
                tokens, i = _make_join_clause(tokens, i, pathInfo)
                count = len(tokens)
        i += 1
    return tokens


def _make_join_clause(tokens: list[Token], i: int, pathInfo: PathInfo) -> tuple[list[Token], int]:
    tables = pathInfo.nodes
    path = pathInfo.path
    table_tree = tokens[i] # this is the table_tree for wich we are autogenerating the from clause
    # convert back to str instead of using node?
    assert not tables or len(tables) == len(path) + 1, "Expected table count to be 0 or 1 + path length"
    
    if path == [] and len(tables) == 0:
        return '' # nothing to join

    # can the first table in path be assumed to fit the on clause of the tree as a whole?
    first_table = _make_table_token(tables[0].name, table_tree)
    tokens[i] = first_table
    i += 1

    # pass through ON clause i.e. until hitting join or end of from
    # on_clause_start_index = i
    on_clause: list[Token] = []
    for tok in tokens[i:]:
        on_clause_done = tok.token_type in [ # join or clause-after-from
            TokenType.JOIN, TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.OUTER, 
            TokenType.FULL, TokenType.SEMI, TokenType.ANTI, TokenType.LATERAL, TokenType.CROSS, 
            TokenType.CROSS, TokenType.NATURAL,
            TokenType.WHERE, TokenType.GROUP_BY, TokenType.HAVING, TokenType.WINDOW, TokenType.UNION, 
            TokenType.ORDER_BY, TokenType.LIMIT, TokenType.OFFSET, TokenType.FETCH, TokenType.FOR]
        if on_clause_done:
            break
        else:
            if tok.text in table_tree_names:
                next_ = tokens[i + 2] # we skip past the dot
                # we assume that tree in an on clause must be on the form tree.var. 
                # It cannot be a free floating tree, nor tree.table.var, nor tree.meta.colname

                # table_by_var[next_.text] assumes that there is only one table that contains var. 
                # Use tokens[i - 2] or some joinData info instead. 
                tokens[i] = _make_table_token(table_by_var[next_.text], table_tree)  # tree.var is replaced with tab.var
            on_clause.append(tokens[i]) # tok is now invalid, so we use tokens[i]
            i += 1


    # autogenerate the remaining joins in join_path
    going_up_the_tree = True
    for tab, next_tab in path:
        if tab == pathInfo.eldest:
            going_up_the_tree = False
        # check for alternative join clauses in the tree
        # this code assumes that foreign key and primary keys follow your naming convention.
        referenced_table = next_tab if going_up_the_tree else tab
        # tokens = flat_tokenize(f'join {next_tab.name} using ({referenced_table.name}_id)\n')
        join_tokens = _make_join(next_tab.name, referenced_table.name, table_tree)

        if first_table.text == 'a10':
            # print(' '.join([t.text for t in tokens[18:]]))
            ...

        # print(f"inserting {[t.text for t in join_tokens]} at {tokens[i].text if i in range(len(tokens)) else 'end'}")
        tokens[i:i] += join_tokens
        i += len(join_tokens)
        # joins += f'join {next_tab.name} using ({referenced_table.name}_id)\n'
    
    return tokens, i


def _make_join(next_tab: str, referenced_table: str, table_tree: Token):
    'join {next_tab} using ({referenced_table}_id)\n'
    def _token(type: TokenType, text: str = None) -> Token:
        text = text if text else type.name
        return Token(type, text, table_tree.line, table_tree.col, table_tree.start, table_tree.end)
    return [
        _token(TokenType.JOIN), 
        _token(TokenType.VAR, next_tab), 
        _token(TokenType.USING), 
        _token(TokenType.L_PAREN, '('), 
        _token(TokenType.VAR, referenced_table + '_id'), 
        _token(TokenType.R_PAREN, ')'), 
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




