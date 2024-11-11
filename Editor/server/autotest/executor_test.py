from textwrap import dedent
from itertools import zip_longest
from features import executor
from lsprotocol.types import *
from tools import embedding


def test_code_actions():
    sapi = dedent("""
        WITH cte AS (
            SELECT col0_1, col0_2, col00_2 FROM tree
        )
        SELECT /* hegr 
        */
            'vervre',
            $$ multi
            line $$,
            123,
            cte.col00_2,
            col10_2,
            (SELECT count(col20_2) FROM tree)
        --FROM tree
        --join cte ON tree.col_1 = cte.col0_1
        FROM cte 
        join tree ON tree.col_1 = cte.col0_1
        ;
        """)
    lines = sapi.split('\n')
    uri="C:\Mine\Python\Sapi\Editor\manual_test\query.sapi"
    range = Range(start=Position(line=0, character=0),
                  end=Position(line=len(lines), character=len(lines[-1])))

    expected_sql = """
        WITH cte AS (
            SELECT col0_1, col0_2, col00_2 FROM tab0
            JOIN tab00 USING (tab0_id))
        SELECT /* hegr 
        */
            'vervre',
            $$ multi
            line $$,
            123,
            cte.col00_2,
            col10_2,
            (SELECT count(col20_2) FROM tab20)
        --FROM tree
        --join cte ON tree.col_1 = cte.col0_1
        FROM cte 
        join tab ON tab.col_1 = cte.col0_1
        JOIN tab1 USING (tab_id)
        JOIN tab10 USING (tab1_id)
        """
    # expected_sql_to_execute = "\n\nWITH cte AS (\n    SELECT col0_1, col0_2, col00_2 FROM tab0\n    JOIN tab00 USING (tab0_id))\nSELECT /* hegr \n*/\n    'vervre',\n    $$ multi\n    line $$,\n    123,\n    cte.col00_2,\n    tab10.col10_2,\n    (SELECT count(tab20.col20_2) FROM tab20)\n--FROM tree\n--join cte ON tree.col_1 = cte.col0_1\nFROM cte \njoin tab ON tab.col_1 = cte.col0_1\nJOIN tab1 USING (tab_id)\nJOIN tab10 USING (tab1_id)"
    # expected_sql_to_cast = "\n\nWITH cte AS (\n    SELECT col0_1, col0_2, col00_2 FROM tab0\n    JOIN tab00 USING (tab0_id))\nSELECT /* hegr \n*/\n    'vervre',\n    $$ multi\n    line $$,\n    123,\n    cte.col00_2,\n    tab10.col10_2,\n    (SELECT count(tab20.col20_2) FROM tab20)\n--FROM tree\n--join cte ON tree.col_1 = cte.col0_1\nFROM cte \njoin tab ON tab.col_1 = cte.col0_1\nJOIN tab1 USING (tab_id)\nJOIN tab10 USING (tab1_id)"

    sections = embedding.freeform_single_section(lines, False)
    actions = executor.code_actions_work(sections, uri, range)
    actual_sql_to_execute: str = [act.command.arguments[0] for act in actions if act.command != None][0]
    actual_sql_sql_to_cast: str = [act.edit.changes[uri][0].new_text for act in actions if act.edit != None][0]
    
    actual_sql_to_execute = _remove_space_and_newline(actual_sql_to_execute)
    actual_sql_sql_to_cast = _remove_space_and_newline(actual_sql_sql_to_cast)
    expected_sql = _remove_space_and_newline(expected_sql)

    # assert actual_sql_to_execute == expected_sql, ""
    # assert actual_sql_sql_to_cast == expected_sql, ""
    
    for actual_sql in [(actual_sql_to_execute), (actual_sql_sql_to_cast)]:
        if actual_sql.lower() != expected_sql.lower():
            differing_lines = [(a, e) for a, e in 
                                zip_longest(actual_sql.split('\n'), expected_sql.split('\n'), fillvalue='') 
                                if a.lower() != e.lower()]
            differing_lines = '\n' + '\n'.join(f"'{a}'   differs from   '{e}'" for a, e in differing_lines)
            raise Exception(dedent("""
                -------------------------- ERROR -------------------------- 
                
                --------- sapi --------- {}
                    
                --------- expected_sql --------- {}
                                    
                --------- produced_sql --------- {}
                                    
                --------- differing_lines --------- {}
                """).format(sapi, expected_sql, actual_sql, differing_lines))


def _remove_space_and_newline(sql: str) -> str:
    sql = dedent(sql).lstrip('\n').rstrip(' \n')
    sql = '\n'.join(line.rstrip(' \n') for line in sql.split('\n') if line.rstrip(' \n;') != '')
    return sql
 
