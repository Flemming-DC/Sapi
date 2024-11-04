from tools import embedding
from itertools import zip_longest
from textwrap import dedent

def test_sapi_lines():
    _test_1_sapi_lines()
    _test_2_sapi_lines()


def _test_1_sapi_lines():

    py_sapi = '''
class A: ...

pg = ""
class B: ...

pg + """
WITH cte AS (
    SELECT col0_1, col00_2 FROM tree
)
SELECT /* hegr */
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
"""

x = 1
class C: ...
'''
    
    sapi_sections = embedding.sapi_sections(py_sapi.split('\n'))
    actual_sapi_code = ''.join([s.leading_whitespace + s.query for s in sapi_sections]) # '\n'.join(sapi_lines)
    expected_sapi_code = '''






WITH cte AS (
    SELECT col0_1, col00_2 FROM tree
)
SELECT /* hegr */
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




'''

    actual_sapi_code = '\n'.join(line.rstrip() for line in dedent(actual_sapi_code).split('\n'))
    expected_sapi_code = '\n'.join(line.rstrip() for line in dedent(expected_sapi_code).split('\n'))
    actual_sapi_code = actual_sapi_code.rstrip()
    expected_sapi_code = expected_sapi_code.rstrip()
    assert actual_sapi_code == expected_sapi_code, _error_message(actual_sapi_code, expected_sapi_code)

def _test_2_sapi_lines():
    py_sapi = '''
import os
import sqlglot

class Query: ...
Query = str
# todo bvedbre TODO efwew MOO geerge

class A:
    v: int = 1

print('hi')
x = 1

a = "%s $s"

class _sapi:
    pg = str
# pg = _sapi.pg

# pg.read("select 1 from a").rows()
_sapi.read_pg("select 1 from a").rows()

import sapi
# class pg: ...
pg = "select 1 from a"
sapi.read(pg + " select 1 from a ").rows()
# sapi.read(pg + " select 1 from a ").rows()

# class PG: ...
PG = str
query = pg + """
    select 1 
    from a;
"""
query: PG = "select 1 from a"
query = PG("select 1 from a")
query.lower()


with sapi.Transaction() as tr:
    tr.pg.execute("select 1 from a").rows() #pg
    tr.execute_pg("select 1 from a").rows()
    tr.pg("select 1 from a").rows()


_sapi.pg("select 1 from a").read().rows()
_sapi.read_pg("select 1 from a").rows()
_sapi.pg.read("select 1 from a").rows()
_sapi.read.pg("select 1 from a").rows()
_sapi.pg.read("select 1 from a").rows()

# pg (=|\(|\+|,) whitespace string

s: PG = f"""
    WITH cte AS (
        select col0_1, col00_2 FROM tree
    )
    SELECT /* hegr */
        'hejsa',
        $$ multi
        line $$,
        123, true and false,
        cte.col00_2,  
        col10_2,
        (SELECT count(col20_2) FROM tree)
    --FROM tree
    --join cte ON tree.col_1 = cte.col0_1
    FROM cte
    join tree ON tree.col_1 = cte.col0_1
    ;

    alter table xx;
    """

import os

print('hi')

def foo():
    return 5 + 5

'''

    sapi_sections = embedding.sapi_sections(py_sapi.split('\n'))
    actual_sapi_code = ''.join([s.leading_whitespace + s.query for s in sapi_sections]) # '\n'.join(sapi_lines)
    expected_sapi_code = '''




















               select 1 from a



      select 1 from a
                 select 1 from a
                   select 1 from a




    select 1
    from a;

             select 1 from a
            select 1 from a





                   select 1 from a
           select 1 from a


          select 1 from a
               select 1 from a

               select 1 from a





    WITH cte AS (
        select col0_1, col00_2 FROM tree
    )
    SELECT /* hegr */
        'hejsa',
        $$ multi
        line $$,
        123, true and false,
        cte.col00_2,
        col10_2,
        (SELECT count(col20_2) FROM tree)
    --FROM tree
    --join cte ON tree.col_1 = cte.col0_1
    FROM cte
    join tree ON tree.col_1 = cte.col0_1
    ;

    alter table xx;









'''

    a, e = dedent(actual_sapi_code), dedent(expected_sapi_code)
    A = '\n'.join(x.rstrip() for x in  a.split('\n'))
    E = '\n'.join(x.rstrip() for x in  e.split('\n'))
    A = A.rstrip()
    E = E.rstrip()
    assert A == E, _error_message(A, E)



def _error_message(actual_sapi_code: str, expected_sapi_code: str) -> str:
    actual_len, expected_len = len(actual_sapi_code), len(expected_sapi_code)
    zip_ = zip_longest(actual_sapi_code.split('\n'), expected_sapi_code.split('\n'), fillvalue='')
    differing_lines_messages = [
        f"\nactual: '{a}'         expected: '{e}'" for a, e in zip_ if a != e]
    
    return f"""
    len(actual_sapi_code) iff len(expected_sapi_code) = {actual_len} iff {expected_len} = {actual_len == expected_len}
    """ + '\n'.join(differing_lines_messages)
    
