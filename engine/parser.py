from . import tokenizer
from .select import select_parser
from .tokenizer import TokenTree, ParserError, TokenType

def parse(sapi_code: str) -> list[TokenTree]: # output str or tokenTrees or Tokens? 
    token_trees = tokenizer.tokenize(sapi_code)
    
    for i, root_tree in enumerate(token_trees):
        token_trees[i] = _parse_token_tree(root_tree)

    return token_trees

def _parse_token_tree(token_tree: TokenTree) -> TokenTree:
    "Parse sapi TokenTree to sql TokenTree."
    # parse sub_trees
    for i, tok in enumerate(token_tree.tokens):
        if isinstance(tok, TokenTree):
            token_tree.tokens[i] = _parse_token_tree(tok)

    # parse leaves
    # stmt_type = token_tree.first_leaf().token_type # first leaf or first statement-starter?
    for tok in token_tree.tokens:
        if isinstance(tok, TokenTree):
            continue
        found_stmt_type = True # to be overridden, if not found
        match tok.token_type:
            case TokenType.SELECT:
                token_tree = select_parser.parse_select(token_tree) # this only changes the leaf tokens
            case TokenType.INSERT | TokenType.UPDATE | TokenType.DELETE | TokenType.CREATE | TokenType.ALTER | TokenType.DROP:
                raise ParserError(f"{tok.token_type} is not yet implemented")
            case _:
                found_stmt_type = False
        if found_stmt_type:
            break

    return token_tree




if __name__ == '__main__':
    q = """
    WITH cte AS (
        SELECT a0_1, a0_2, a00_2 FROM A
    )
    SELECT 
        cte.a00_2,
        a10_2,
        (SELECT sum(a20_2) FROM A)
    FROM cte 
    join A ON A.a_1 = cte.a0_1
    """
    # tab_in_cte: a00, a0
    # outer_tab: a, a1, a10
    # sub: a20
    res = """
    WITH cte AS (
        SELECT a0_1, a0_2, a00_2 
        FROM a00
        JOIN a0 ON a0.a0_1 = a00.a0_1
    )
    SELECT 
        cte.a00_2,
        a10_2,
        (SELECT sum(a20_2) FROM a20)
    FROM cte 
    JOIN a   ON a.a_1 = cte.a0_1
    JOIN a1  ON a1.a_1 = a.a_1
    JOIN a10 ON a10.a1_1 = a1.a1_1
    """
    # evt. bug: graps a0_2 from a0 instead of cte
    # should we auto_join the missing tables or all the tables?
    # suggested answer: all, unless prefix says otherwise
    trees = parse(q)

    for tr in trees:
        print("--- tree ---")
        print(tr)


