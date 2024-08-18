import __sys_path__
from engine import parser
from textwrap import dedent



def test_get_expected_sql():

    cases = [
        (
        "SELECT a2.*", 
        """
SELECT a2.* 
from a2
;

""",
        ),
        (
        """
SELECT 1, a1.*, a2_2
/*
comment
comment
*/
from
where a2_2 != 0 -- comment
;
""", 
        """
select 1 , a1 . * , a2_2 where a2_2 ! = 0
from a1
join a using (a_id)
join a2 using (a_id)
;
""",
        ),
        (
        "SELECT 1",
        "SELECT 1",
        ),
    ]

    for sapi, expected_sql in cases:
        print(f"sapi: \n{dedent(sapi)}")
        produced_sql = parser.parse(sapi)

        produced_sql = dedent(produced_sql).strip('\n').strip(' ')
        expected_sql = dedent(produced_sql).strip('\n').strip(' ')
        assert produced_sql == expected_sql, dedent(f"""
        ERROR: 
        sapi: \n{dedent(sapi)}
        expected_sql: \n{expected_sql}
        produced_sql: \n{produced_sql}
        """)

if __name__ == '__main__':
    test_get_expected_sql()
    print("Passed")



