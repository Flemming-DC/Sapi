import __sys_path__
from engine import parser
from textwrap import dedent
from collections import namedtuple
from engine.token_tree import Token, TokenType, TokenTree
from engine.select.tree_join import TreeJoin
from engine.select import table_finder #, path_finder, join_generator
from engine.dyn_loop import DynLoop

def test_get_expected_table_trees():
    # ------- tokens ---------
    tokens1 = [
        Token(TokenType.SELECT, 'SELECT', 3, 7, 27, 32),
        Token(TokenType.VAR,  'a0',    3, 12, 34, 37),
        Token(TokenType.DOT,  '.',     3, 12, 34, 37),
        Token(TokenType.VAR,  'a0_1',  3, 12, 34, 37),
        Token(TokenType.COMMA,',',     3, 13, 38, 38),
        Token(TokenType.VAR,  'a0',    3, 18, 40, 43),
        Token(TokenType.DOT,  '.',     3, 18, 40, 43),
        Token(TokenType.VAR,  'a0_2',  3, 18, 40, 43),
        Token(TokenType.COMMA,',',     3, 19, 44, 44),
        Token(TokenType.VAR,  'a00',   3, 25, 46, 50),
        Token(TokenType.DOT,  '.',     3, 25, 46, 50),
        Token(TokenType.VAR,  'a00_2', 3, 25, 46, 50),
        Token(TokenType.FROM, 'FROM',  3, 30, 52, 55),
        Token(TokenType.VAR,  'A',     3, 32, 57, 57),
    ]
    dyn_loop1 = DynLoop(tokens1, "irrelevant sapi_str",
                        previous_token=Token(TokenType.L_PAREN, '(', 2, 14, 17, 17), 
                        next_token=Token(TokenType.R_PAREN, ')', 4, 2, 63, 63)) # we aren't test the updates to sapi_str

    # ------- tokens ---------
    tokens2 = [
        Token(TokenType.SELECT, 'SELECT', 8, 8, 120, 125),
        Token(TokenType.VAR, 'sum', 8, 12, 127, 129),
        Token(TokenType.L_PAREN, '(', 8, 13, 130, 130),
        Token(TokenType.VAR, 'a20_2', 8, 18, 131, 135),
        Token(TokenType.R_PAREN, ')', 8, 19, 136, 136),
        Token(TokenType.FROM, 'FROM', 8, 24, 138, 141),
        Token(TokenType.VAR, 'A', 8, 26, 143, 143),
    ]
    dyn_loop2 = DynLoop(tokens2, "irrelevant sapi_str",
                        previous_token=Token(TokenType.L_PAREN, '(', 8, 2, 119, 119), 
                        next_token=Token(TokenType.R_PAREN, ')', 8, 27, 144, 144)) # we aren't test the updates to sapi_str
    # ------- tokens ---------
    sub_token_tree1 = TokenTree(tokens1, dyn_loop1)
    sub_token_tree2 = TokenTree(tokens2, dyn_loop2)
    
    tokens3 = [
        Token(TokenType.WITH, 'WITH', 2, 5, 5, 8),
        Token(TokenType.VAR, 'cte', 2, 9, 10, 12),
        Token(TokenType.ALIAS, 'AS', 2, 12, 14, 15),
        Token(TokenType.L_PAREN, '(', 2, 14, 17, 17),
        sub_token_tree1,
        Token(TokenType.R_PAREN, ')', 4, 2, 63, 63),
        Token(TokenType.SELECT, 'SELECT', 5, 7, 69, 74),
        Token(TokenType.VAR, 'cte', 6, 4, 85, 87),
        Token(TokenType.DOT, '.', 6, 5, 88, 88),
        Token(TokenType.VAR, 'a00_2', 6, 10, 89, 93),
        Token(TokenType.COMMA, ',', 6, 11, 94, 94),
        Token(TokenType.VAR, 'a10_2', 7, 6, 104, 108),
        Token(TokenType.COMMA, ',', 7, 7, 109, 109),
        Token(TokenType.L_PAREN, '(', 8, 2, 119, 119),
        sub_token_tree2,
        Token(TokenType.R_PAREN, ')', 8, 27, 144, 144),
        Token(TokenType.FROM, 'FROM', 11, 5, 198, 201),
        Token(TokenType.VAR, 'cte', 11, 9, 203, 205),
        Token(TokenType.JOIN, 'join', 12, 5, 212, 215),
        Token(TokenType.VAR, 'A', 12, 7, 217, 217),
        Token(TokenType.ON, 'ON', 12, 10, 219, 220),
        Token(TokenType.VAR, 'A', 12, 12, 222, 222),
        Token(TokenType.DOT, '.', 12, 13, 223, 223),
        Token(TokenType.VAR, 'a_1', 12, 16, 224, 226),
        Token(TokenType.EQ, '=', 12, 18, 228, 228),
        Token(TokenType.VAR, 'cte', 12, 22, 230, 232),
        Token(TokenType.DOT, '.', 12, 23, 233, 233),
        Token(TokenType.VAR, 'a0_1', 12, 27, 234, 237),
    ]
    dyn_loop3 = DynLoop(tokens3, "irrelevant sapi_str", 
                        previous_token=None, 
                        next_token=None) # we aren't test the updates to sapi_str

    expected_1 = TreeJoin(join_obj = Token(TokenType.VAR, 'A', 3, 32, 57, 57,), 
        on_clause_end_index=13, on_clause_tables=[], first_table=None, tables=['a0', 'a0', 'a00'])
    expected_2 = TreeJoin(join_obj = Token(TokenType.VAR, 'A', 8, 26, 143, 143,),
        on_clause_end_index=8, on_clause_tables=[], first_table=None, tables=['a20'])
    # expected_3_1 = TreeJoin(join_obj = Token(TokenType.VAR, 'cte', 11, 9, 203, 205,), 
    #     on_clause_end_index=19, on_clause_tables=[], first_table=None, tables=[], path=[])
    expected_3 = TreeJoin(join_obj = Token(TokenType.VAR, 'A', 12, 7, 217, 217,), 
        on_clause_end_index=29, on_clause_tables=['a'], first_table='a', tables=['a10', 'a'])
    expected_1 = [expected_1]
    expected_2 = [expected_2]
    expected_3 = [expected_3]
    # expected_join_data = [j1, j2, j3, j4]

    cases = [
        (tokens1, expected_1, dyn_loop1),
        (tokens2, expected_2, dyn_loop2),
        (tokens3, expected_3, dyn_loop3),
        ]

    for _, expected, dyn_loop in cases:
        actual: list[TreeJoin] = table_finder.get_tables(dyn_loop)
        for a, e in zip(actual, expected):
            assert _equal_join_data(a, e), "table_finder.get_tables(tokens1) gave incorrect join_data."



def _equal_join_data(j1: TreeJoin, j2: TreeJoin):
    # evt. put the comparison into the join data class
    jo1 = j1.join_obj
    jot1 = (jo1.token_type, jo1.token_type, jo1.text, jo1.line, jo1.col, jo1.start, jo1.end, jo1.comments)
    j1_comparable = (jot1, j1.on_clause_end_index, j1.on_clause_tables, j1.first_table, j1.tables)

    jo2 = j2.join_obj
    jot2 = (jo2.token_type, jo2.token_type, jo2.text, jo2.line, jo2.col, jo2.start, jo2.end, jo2.comments)
    j2_comparable = (jot2, j2.on_clause_end_index, j2.on_clause_tables, j2.first_table, j2.tables)
    if j1_comparable != j2_comparable:
        ...
    return j1_comparable == j2_comparable


def test_get_expected_sql():

    Case = namedtuple('Case', ['sapi', 'expected_sql'])

    case1 = Case(sapi = """
    WITH cte AS (
        SELECT a0_1, a0_2, a00_2 FROM A
    )
    SELECT 
        cte.a00_2,
        a10_2,
        (SELECT sum(a20_2) FROM A)
    --FROM A
    --join cte ON A.a_1 = cte.a0_1
    FROM cte 
    join A ON A.a_1 = cte.a0_1
    """,
    expected_sql = """[WITH cte AS ([
    SELECT a0.a0_1, a0.a0_2, a00.a00_2 
    FROM a0 
    JOIN a00 USING (a0_id)]) 
SELECT cte.a00_2, a10.a10_2, ([
    SELECT sum (a20.a20_2) 
    FROM a20]) 
FROM cte 
join a ON a.a_1 = cte.a0_1 
JOIN a1 USING (a_id) 
JOIN a10 USING (a1_id)]""")

    cases = [case1]

    for sapi, expected_sql in cases:
        actual_sql = parser.parse(sapi)

        actual_sql = dedent(actual_sql).strip('\n').strip(' ')
        expected_sql = dedent(expected_sql).strip('\n').strip(' ')
        print('--- test ---')
        print(actual_sql)
        assert actual_sql == expected_sql, dedent("")
        # f"""
        # ERROR: 
        # sapi: \n{dedent(sapi)}
        # expected_sql: \n{expected_sql}
        # produced_sql: \n{actual_sql}
        # """)

if __name__ == '__main__':
    # test_get_expected_table_trees()
    test_get_expected_sql()
    print("Passed")




