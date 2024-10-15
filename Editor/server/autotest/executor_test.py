from textwrap import dedent
from features import executor
from lsprotocol.types import *


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
    
    expected_sql_to_execute = "\n\nWITH cte AS (\n    SELECT tab0.col0_1, tab0.col0_2, tab00.col00_2 FROM tab0\n    JOIN tab00 USING (tab0_id))\nSELECT /* hegr \n*/\n    'vervre',\n    $$ multi\n    line $$,\n    123,\n    cte.col00_2,\n    tab10.col10_2,\n    (SELECT count(tab20.col20_2) FROM tab20)\n--FROM tree\n--join cte ON tree.col_1 = cte.col0_1\nFROM cte \njoin tab ON tab.col_1 = cte.col0_1\nJOIN tab1 USING (tab_id)\nJOIN tab10 USING (tab1_id)"
    expected_sql_to_cast = "\n\nWITH cte AS (\n    SELECT tab0.col0_1, tab0.col0_2, tab00.col00_2 FROM tab0\n    JOIN tab00 USING (tab0_id))\nSELECT /* hegr \n*/\n    'vervre',\n    $$ multi\n    line $$,\n    123,\n    cte.col00_2,\n    tab10.col10_2,\n    (SELECT count(tab20.col20_2) FROM tab20)\n--FROM tree\n--join cte ON tree.col_1 = cte.col0_1\nFROM cte \njoin tab ON tab.col_1 = cte.col0_1\nJOIN tab1 USING (tab_id)\nJOIN tab10 USING (tab1_id)"

    actions = executor.code_actions_work(lines, uri)
    actual_sql_to_execute: str = [act.command.arguments[0] for act in actions if act.command != None][0]
    actual_sql_sql_to_cast: str = [act.edit.changes[uri][0].new_text for act in actions if act.edit != None][0]
    
    assert actual_sql_to_execute.strip() == expected_sql_to_execute.strip(), "code_actions_work"
    assert actual_sql_sql_to_cast.strip() == expected_sql_to_cast.strip(), "code_actions_work"

