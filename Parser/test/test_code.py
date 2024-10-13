import sys
import psycopg
from textwrap import dedent
from sapi import DataModel, parse
from sapi._test import Token, TokenType, TokenTree, TreeJoin, select_analyzer, DynLoop, data_model
from select_cases import select_cases, select_error_cases
import postgres_model, runtime_model



def _test_get_expected_table_trees(dataModel: DataModel):
    data_model.set_current(dataModel)
    # ------- tokens ---------
    tokens1 = [
        Token(TokenType.SELECT, 'SELECT', 3, 27),
        Token(TokenType.VAR,  'a0',       3, 34),
        Token(TokenType.DOT,  '.',        3, 34),
        Token(TokenType.VAR,  'a0_1',     3, 34),
        Token(TokenType.COMMA,',',        3, 38),
        Token(TokenType.VAR,  'a0',       3, 40),
        Token(TokenType.DOT,  '.',        3, 40),
        Token(TokenType.VAR,  'a0_2',     3, 40),
        Token(TokenType.COMMA,',',        3, 44),
        Token(TokenType.VAR,  'a00',      3, 46),
        Token(TokenType.DOT,  '.',        3, 46),
        Token(TokenType.VAR,  'a00_2',    3, 46),
        Token(TokenType.FROM, 'FROM',     3, 52),
        Token(TokenType.VAR,  'A',        3, 57),
    ]
    
    # ------- tokens ---------
    tokens2 = [
        Token(TokenType.SELECT, 'SELECT', 8, 120),
        Token(TokenType.VAR,    'sum',    8, 127),
        Token(TokenType.L_PAREN,'(',      8, 130),
        Token(TokenType.VAR,    'a20_2',  8, 131),
        Token(TokenType.R_PAREN,')',      8, 136),
        Token(TokenType.FROM,   'FROM',   8, 138),
        Token(TokenType.VAR,    'A',      8, 143),
    ]
    # ------- tokens ---------
    sub_token_tree1 = TokenTree(tokens1, "irrelevant sapi_str",
                        Token(TokenType.R_PAREN, ')', 4, 63))
    sub_token_tree2 = TokenTree(tokens2, "irrelevant sapi_str",
                        Token(TokenType.R_PAREN, ')', 8, 144))

    
    tokens3 = [
        Token(TokenType.WITH,   'WITH', 2, 5),
        Token(TokenType.VAR,    'cte',  2, 10),
        Token(TokenType.ALIAS,  'AS',   2, 14),
        Token(TokenType.L_PAREN,'(',    2, 17),
        sub_token_tree1,
        Token(TokenType.R_PAREN, ')',     4, 63),
        Token(TokenType.SELECT, 'SELECT', 5, 69),
        Token(TokenType.VAR,    'cte',    6, 85),
        Token(TokenType.DOT,    '.',      6, 88),
        Token(TokenType.VAR,    'a00_2',  6, 89),
        Token(TokenType.COMMA,  ',',      6, 94),
        Token(TokenType.VAR,    'a10_2',  7, 104),
        Token(TokenType.COMMA,  ',',      7, 109),
        Token(TokenType.L_PAREN,'(',      8, 119),
        sub_token_tree2,
        Token(TokenType.R_PAREN,')',    8,  144),
        Token(TokenType.FROM,   'FROM', 11, 198),
        Token(TokenType.VAR,    'cte',  11, 203),
        Token(TokenType.JOIN,   'join', 12, 212),
        Token(TokenType.VAR,    'A',    12, 217),
        Token(TokenType.ON,     'ON',   12, 219),
        Token(TokenType.VAR,    'A',    12, 222),
        Token(TokenType.DOT,    '.',    12, 223),
        Token(TokenType.VAR,    'a_1',  12, 224),
        Token(TokenType.EQ,     '=',    12, 228),
        Token(TokenType.VAR,    'cte',  12, 230),
        Token(TokenType.DOT,    '.',    12, 233),
        Token(TokenType.VAR,    'a0_1', 12, 234),
    ]
    root_token_tree3 = TokenTree(tokens3, "irrelevant sapi_str",
                    None)


    expected_1 = TreeJoin(tree_tok = Token(TokenType.VAR, 'A', 3, 57), 
        tree_tok_index=13,
        on_clause_end_index=13, first_table='a0', referenced_tables=['a0', 'a0', 'a00'])
    expected_2 = TreeJoin(tree_tok = Token(TokenType.VAR, 'A', 8, 143),
        tree_tok_index=8, on_clause_end_index=8, 
        first_table='a20', referenced_tables=['a20'])
    expected_3 = TreeJoin(tree_tok = Token(TokenType.VAR, 'A', 12, 217), 
        tree_tok_index=21, on_clause_end_index=29, 
        first_table='a', referenced_tables=['a10', 'a'])
    expected_1 = [expected_1]
    expected_2 = [expected_2]
    expected_3 = [expected_3]

    cases = [
        (tokens1, expected_1, sub_token_tree1),
        (tokens2, expected_2, sub_token_tree2),
        (tokens3, expected_3, root_token_tree3),
        ]

    for _, expected, tok_tree in cases:
        actual: list[TreeJoin] = select_analyzer.find_tree_joins(DynLoop(tok_tree))
        for a, e in zip(actual, expected):
            assert _equal_join_data(a, e), "table_finder.get_tables(tokens1) gave incorrect join_data."


def _equal_join_data(j1: TreeJoin, j2: TreeJoin):
    # evt. put the comparison into the join data class
    jo1 = j1.tree_tok
    jot1 = (jo1.type, jo1.type, jo1.text, jo1.line, jo1.start)
    j1_comparable = (jot1, j1.on_clause_end_index, j1.first_table, j1.referenced_tables)

    jo2 = j2.tree_tok
    jot2 = (jo2.type, jo2.type, jo2.text, jo2.line, jo2.start)
    j2_comparable = (jot2, j2.on_clause_end_index, j2.first_table, j2.referenced_tables)

    return j1_comparable == j2_comparable


def _test_get_expected_sql(dataModel: DataModel):
    for sapi, expected_sql in select_cases:
        actual_sql = parse(sapi, dataModel)
        
        # remove insignificant differences
        sapi = dedent(sapi)
        actual_sql = '\n' + _remove_space_and_newline(actual_sql)
        expected_sql = '\n' + _remove_space_and_newline(expected_sql)

        if actual_sql.lower() != expected_sql.lower():
            differing_lines = [(a, e) for a, e in zip(actual_sql.split('\n'), expected_sql.split('\n')) if a.lower() != e.lower()]
            differing_lines = '\n' + '\n'.join(f"'{a}'   differs from   '{e}'" for a, e in differing_lines)
            raise Exception(dedent("""
                -------------------------- ERROR -------------------------- 
                
                --------- sapi --------- {}
                 
                --------- expected_sql --------- {}
                                   
                --------- produced_sql --------- {}
                                   
                --------- differing_lines --------- {}
                """).format(sapi, expected_sql, actual_sql, differing_lines))


def _test_raise_error(dataModel: DataModel):
    for sapi, error_type in select_error_cases:
        found_error = False
        try:   parse(sapi, dataModel)
        except error_type: found_error = True
        except Exception: ...

        if not found_error:
            sapi = dedent(sapi)
            raise Exception(f"Failed to raise {error_type.__name__} in {sapi}")


def _test_expected_queries_works():
    connection_info = postgres_model.get_connection_info()
    with psycopg.Connection.connect(**connection_info) as con:
        with con.cursor() as cur:
            cur.execute("set search_path to sapi_demo")
            con.commit()
            exc = None
            for _, expected_sql in select_cases:
                if 'some_view' in expected_sql:
                    continue # some_view doesnt actually exist, so we dont demand this query to work
                try:
                    cur.execute(expected_sql)
                except Exception as e:
                    exc = e
                    con.rollback()
                    print("------ failed to execute expected_sql ------")
                    print(expected_sql)
                    print()
                    print(e)
            if exc:
                sys.exit()

def _remove_space_and_newline(sql: str) -> str:
    sql = dedent(sql).lstrip('\n').rstrip(' \n')
    sql = '\n'.join(line.rstrip(' \n') for line in sql.split('\n') if line.rstrip(' \n') != '')
    return sql
 

def _test_forest(dataModel: DataModel):
    _test_get_expected_table_trees(dataModel)
    _test_get_expected_sql(dataModel)
    _test_raise_error(dataModel)


if __name__ == '__main__':
    _test_forest(runtime_model.make_datamodel())
    _test_forest(postgres_model.setup_db_and_make_datamodel())
    _test_expected_queries_works()
    print("All Tests Passed")




