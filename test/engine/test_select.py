import __sys_path__
from engine import parser
from textwrap import dedent
from collections import namedtuple



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
        assert actual_sql == expected_sql, dedent(f"""
        ERROR: 
        sapi: \n{dedent(sapi)}
        expected_sql: \n{expected_sql}
        produced_sql: \n{actual_sql}
        """)

if __name__ == '__main__':
    test_get_expected_sql()
    print("Passed")




