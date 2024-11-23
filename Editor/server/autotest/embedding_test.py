from itertools import zip_longest
from textwrap import dedent
from lsprotocol import types as t
from tools import embedding

def sapi_sections():
    _test_1_sapi_sections()
    _test_2_sapi_sections()
    _test_3_sapi_sections()
    _test_4_sapi_sections()


def _test_1_sapi_sections():
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

    sapi_sections = embedding.sapi_sections(py_sapi.split('\n'), False)

    actual_sapi_code, expected_sapi_code = _make_comparable(sapi_sections, expected_sapi_code)
    assert actual_sapi_code == expected_sapi_code, _error_message(actual_sapi_code, expected_sapi_code)
    _check_plings_around_sections(sapi_sections, py_sapi.split('\n'))

def _test_2_sapi_sections():
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

    sapi_sections = embedding.sapi_sections(py_sapi.split('\n'), False)

    actual_sapi_code, expected_sapi_code = _make_comparable(sapi_sections, expected_sapi_code)
    assert actual_sapi_code == expected_sapi_code, _error_message(actual_sapi_code, expected_sapi_code)
    _check_plings_around_sections(sapi_sections, py_sapi.split('\n'))

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

def _test_3_sapi_sections():
    py_sapi = '''
class B: ...
PG = str
s1: PG = "select 0 from tab0"
s2: PG = "select 1 from tab1; select 2 from tab2;"
s3: PG = """
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
select 3 from tab3; select 4 from tab4;
"""
x = 1
s3: PG = "select 5 from tab5"
'''
    expected_sapi_code = '''



                              select 2 from tab2;

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
select 3 from tab3;



'''

    range = t.Range(start=t.Position(line=4, character=36), end=t.Position(line=22, character=4))
    sapi_sections = embedding.sapi_sections(py_sapi.split('\n'), False, range)

    actual_sapi_code, expected_sapi_code = _make_comparable(sapi_sections, expected_sapi_code)
    assert actual_sapi_code == expected_sapi_code, _error_message(actual_sapi_code, expected_sapi_code)
    # we omit check_plings_around_sections, when ranges are involved

def _test_4_sapi_sections():
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

    pointlike_range = t.Range(start=t.Position(line=13, character=10), end=t.Position(line=13, character=10))
    print('---')
    sapi_sections = embedding.sapi_sections(py_sapi.split('\n'), False, pointlike_range)

    actual_sapi_code, expected_sapi_code = _make_comparable(sapi_sections, expected_sapi_code)
    assert actual_sapi_code == expected_sapi_code, _error_message(actual_sapi_code, expected_sapi_code)
    _check_plings_around_sections(sapi_sections, py_sapi.split('\n'))




def _error_message(actual_sapi_code: str, expected_sapi_code: str) -> str:
    actual_len, expected_len = len(actual_sapi_code), len(expected_sapi_code)
    zip_ = zip_longest(actual_sapi_code.split('\n'), expected_sapi_code.split('\n'), fillvalue=None)
    differing_lines_messages = [
        f"actual: '{a}'\t\t expected: '{e}'" for a, e in zip_ if a != e]
    diff_char = [(i, a, e) for i, (a, e) in enumerate(zip_longest(actual_sapi_code, expected_sapi_code, fillvalue=None)) if a != e]
    
    return (f"""
    \nlen(actual_sapi_code) iff len(expected_sapi_code) = {actual_len} iff {expected_len} = {actual_len == expected_len}
    \n""" 
    + 'differing_lines:\n\t' + '\n\t'.join(differing_lines_messages) 
    + f'\n\nfirst few differing characters (index, actual, expected):\n\t{diff_char[:5]}')
    

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

def _make_comparable(sapi_sections: list[embedding.Section], expected_sapi_code: str) -> tuple[str, str]:
    # actual_sapi_code, actual_sapi_code = dedent(actual_sapi_code), dedent(expected_sapi_code)
    actual_sapi_code = ''.join([s.leading_whitespace + s.query for s in sapi_sections]) # '\n'.join(sapi_lines)
    actual_sapi_code = '\n'.join(line.rstrip() for line in dedent(actual_sapi_code).split('\n'))
    expected_sapi_code = '\n'.join(line.rstrip() for line in dedent(expected_sapi_code).split('\n'))
    return actual_sapi_code.rstrip(), expected_sapi_code.rstrip()

