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
    
    sapi_sections = embedding.sapi_sections(py_sapi.split('\n'), False)
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

    _check_plings_around_sections(sapi_sections, py_sapi.split('\n'))

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
    join tree ON tree.col_1 = cte.col0_1;
    alter table xx;
    """

import os

print('hi')

def foo():
    return 5 + 5

'''

    sapi_sections = embedding.sapi_sections(py_sapi.split('\n'), False)
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
    join tree ON tree.col_1 = cte.col0_1;
    alter table xx;









'''

    a, e = dedent(actual_sapi_code), dedent(expected_sapi_code)
    A = '\n'.join(x.rstrip() for x in a.split('\n'))
    E = '\n'.join(x.rstrip() for x in e.split('\n'))
    A = A.rstrip()
    E = E.rstrip()
    assert A == E, _error_message(A, E)

    actual_ranges = [(s.line_nr_start, s.char_start, s.line_nr_end, s.char_end) for s in sapi_sections]
    expected_ranges = [
        (22-1, 15, 22-1, 30), #              "select 1 from a"
        (26-1, 6,  26-1, 21), #     "select 1 from a"
        (27-1, 16, 27-1, 33), #               " select 1 from a "
        (28-1, 18, 28-1, 35), #                 " select 1 from a "
        (32-1, 16, 35-1, 0 ), #query = pg + """
        # (33-1, 4,  34-1, 11), #    select 1 
        (36-1, 13, 36-1, 28), #          "select 1 from a"
        (37-1, 12, 37-1, 27), #         "select 1 from a"
        (43-1, 19, 43-1, 34), #                  "select 1 from a"
        (44-1, 11, 44-1, 26), #          "select 1 from a"
        (47-1, 10, 47-1, 25), #         "select 1 from a"
        (48-1, 15, 48-1, 30), #              "select 1 from a"
        (50-1, 15, 50-1, 30), #              "select 1 from a"
        (55-1, 12, 72-1, 4 ), #s: PG = f"""
        # (56-1, 4,  71-1, 19), #    WITH cte AS ( 
    ]
    assert actual_ranges == expected_ranges, _error_message_ranges(actual_ranges, expected_ranges)

    _check_plings_around_sections(sapi_sections, py_sapi.split('\n'))

def _error_message(actual_sapi_code: str, expected_sapi_code: str) -> str:
    actual_len, expected_len = len(actual_sapi_code), len(expected_sapi_code)
    zip_ = zip_longest(actual_sapi_code.split('\n'), expected_sapi_code.split('\n'), fillvalue='')
    differing_lines_messages = [
        f"actual: '{a}'         expected: '{e}'" for a, e in zip_ if a != e]
    
    return f"""
    len(actual_sapi_code) iff len(expected_sapi_code) = {actual_len} iff {expected_len} = {actual_len == expected_len}
    \n""" + '\n'.join(differing_lines_messages)
    


def _error_message_ranges(actual_ranges: list[tuple[int]], expected_ranges: list[tuple[int]]) -> str:
    actual_len, expected_len = len(actual_ranges), len(expected_ranges)
    zip_ = zip_longest(actual_ranges, expected_ranges, fillvalue=(None, None, None, None))
    differing_lines_messages = [
        f"actual: {a}   expected: {e}   diff: {(a[0] - e[0], a[1] - e[1], a[2] - e[2], a[3] - e[3])}" for a, e in zip_ if a != e]
    
    return f"""
    len(actual_ranges) iff len(expected_ranges) = {actual_len} iff {expected_len} = {actual_len == expected_len}
    \n""" + '\n'.join(differing_lines_messages)
    



def _check_plings_around_sections(sections: list[embedding.Section], lines: list[str]):
    for section in sections:
        before_start = lines[section.line_nr_start][section.char_start - 3 : section.char_start]
        assert '"' in before_start or "'''" in before_start, (
            f"Expected \", \"\"\" or ''' before section. \nline: {lines[section.line_nr_start]}\nbefore_start: {before_start}"
            f"\n{section.line_nr_start}, {section.char_start}")
        after_end = lines[section.line_nr_end][section.char_end : section.char_end + 3]
        assert '"' in after_end or "'''" in after_end, (
            f"Expected \", \"\"\" or ''' after section. \nline: {lines[section.line_nr_end]}\nafter_end: {after_end}"
            f"\n{section.line_nr_end}, {section.char_end}")

