from itertools import zip_longest
from textwrap import dedent
from sapi._test import TestError



def assert_match(sapi: str, actual_sql: str, expected_sql: str, index: int|None = None):
    # remove insignificant differences
    sapi = dedent(sapi)
    actual_sql = _remove_whitespace(actual_sql)
    expected_sql = _remove_whitespace(expected_sql)
    # check
    if _remove_semicolon_lines(actual_sql) != _remove_semicolon_lines(expected_sql): 
        raise TestError(_error_message(sapi, actual_sql, expected_sql, index))
    

def _remove_semicolon_lines(sql: str) -> str:
    sql = '\n'.join(line.lower() for line in sql.split('\n') if line.rstrip(' \n;') != '')
    return sql
 
def _remove_whitespace(sql: str) -> str:
    sql = dedent(sql).lstrip('\n').rstrip(' \n')
    sql = '\n'.join(line.rstrip(' \n') for line in sql.split('\n') if line.rstrip(' \n') != '')
    return sql


def _error_message(sapi: str, actual_sql: str, expected_sql: str, index: int|None) -> str:
    differing_lines = [(a, e) for a, e in 
                        zip_longest(actual_sql.split('\n'), expected_sql.split('\n'), fillvalue='') 
                        if a.lower() != e.lower()]
    differing_lines = '\n' + '\n'.join(f"'{a}'   differs from   '{e}'" for a, e in differing_lines)
    index_str = f'tase case index: {index}' if index != None else ''
    return dedent("""
        -------------------------- ERROR -------------------------- 
        {}
        
        --------- sapi --------- {}
            
        --------- expected_sql --------- \n{}
                            
        --------- actual_sql --------- \n{}
                            
        --------- differing_lines --------- {}
        """).format(index_str, sapi, expected_sql, actual_sql, differing_lines)


