from itertools import zip_longest
from textwrap import dedent



def assert_match(sapi: str, actual_sql: str, expected_sql: str):
    # remove insignificant differences
    sapi = dedent(sapi)
    actual_sql = '\n' + _remove_space_and_newline(actual_sql)
    expected_sql = '\n' + _remove_space_and_newline(expected_sql)
    # check
    assert actual_sql.lower() == expected_sql.lower(), _error_message(sapi, actual_sql, expected_sql)
    

def _remove_space_and_newline(sql: str) -> str:
    sql = dedent(sql).lstrip('\n').rstrip(' \n')
    sql = '\n'.join(line.rstrip(' \n') for line in sql.split('\n') if line.rstrip(' \n;') != '')
    return sql
 


def _error_message(sapi: str, actual_sql: str, expected_sql: str) -> str:
    differing_lines = [(a, e) for a, e in 
                        zip_longest(actual_sql.split('\n'), expected_sql.split('\n'), fillvalue='') 
                        if a.lower() != e.lower()]
    differing_lines = '\n' + '\n'.join(f"'{a}'   differs from   '{e}'" for a, e in differing_lines)
    return dedent("""
        -------------------------- ERROR -------------------------- 
        
        --------- sapi --------- {}
            
        --------- expected_sql --------- {}
                            
        --------- actual_sql --------- {}
                            
        --------- differing_lines --------- {}
        """).format(sapi, expected_sql, actual_sql, differing_lines)


