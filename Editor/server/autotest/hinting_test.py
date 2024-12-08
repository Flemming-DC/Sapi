from collections import namedtuple
from textwrap import dedent
from lsprotocol import types as t
from features import hinting
from tools import embedding


_PartialHint = namedtuple('Hint', ['position', 'label'])

def test_inlay_hints():
    _test_1_inlay_hints()
    _test_2_inlay_hints()
    _test_3_inlay_hints()

def _test_1_inlay_hints():
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
    sections = embedding.freeform_single_section(lines, True, None)
    # sapi_code = sections[0].leading_whitespace + sections[0].query # temp
    # lines_2 = sapi_code.split('\n')


    expected_hints = {
        _PartialHint(position=f'2:44', label=' tab0'),
        _PartialHint(position=f'3:{0 + 0}', label='JOIN tab00 USING (tab0_id)'),
        _PartialHint(position=f'12:36', label=' tab20'),
        _PartialHint(position=f'16:9', label=' tab'),
        _PartialHint(position=f'16:17', label=' tab'),
        _PartialHint(position=f'17:{0 + 0}', label='JOIN tab1 USING (tab_id)'),
        _PartialHint(position=f'18:{0 + 0}', label='JOIN tab10 USING (tab1_id)'),
    }

    actual_hints = hinting.inlay_hints_work(sections)
    actual_hints = { _PartialHint(repr(a.position), a.label) for a in actual_hints }

    assert actual_hints == expected_hints, _error_message(actual_hints, expected_hints)


def _test_2_inlay_hints():
    python_with_sapi = dedent('''
class A: ...

pg = ""
class B: ...

pg + """
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
    """

x = 1
class C: ...

''')
    lines = python_with_sapi.split('\n')
    sections = embedding.sapi_sections(lines, True)

    expected_hints_1 = set() # first section is empty
    line_nr_offset = sections[1].line_nr_start
    expected_hints_2 = {
        _PartialHint(position=f'{2  + line_nr_offset}:{44 + 4}', label=' tab0'),
        _PartialHint(position=f'{3  + line_nr_offset}:{0  + 4}', label='JOIN tab00 USING (tab0_id)'),
        _PartialHint(position=f'{12 + line_nr_offset}:{36 + 4}', label=' tab20'),
        _PartialHint(position=f'{16 + line_nr_offset}:{9  + 4}', label=' tab'),
        _PartialHint(position=f'{16 + line_nr_offset}:{17 + 4}', label=' tab'),
        _PartialHint(position=f'{17 + line_nr_offset}:{0  + 4}', label='JOIN tab1 USING (tab_id)'),
        _PartialHint(position=f'{18 + line_nr_offset}:{0  + 4}', label='JOIN tab10 USING (tab1_id)'),
    }
    expected_hints = expected_hints_1.union(expected_hints_2)

    actual_hints = hinting.inlay_hints_work(sections)
    actual_hints = { _PartialHint(repr(a.position), a.label) for a in actual_hints }

    assert actual_hints == expected_hints, _error_message(actual_hints, expected_hints)


def _test_3_inlay_hints():
    python_with_sapi = dedent('''
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
    select 1 table tab0;
    """

import os

print('hi')

def foo():
    return 5 + 5

''')
    lines = python_with_sapi.split('\n')
    full_range = t.Range(start = t.Position(line=0, character=0), 
                         end   = t.Position(line=len(lines), character=len(lines[-1])))
    sections = embedding.sapi_sections(lines, True, full_range)

    expected_hints = {
        _PartialHint(position='56:40', label=' tab0'),
        _PartialHint(position='57:4', label='JOIN tab00 USING (tab0_id)'),
        _PartialHint(position='65:40', label=' tab20'),
        _PartialHint(position='69:13', label=' tab'),
        _PartialHint(position='69:21', label=' tab'),
        _PartialHint(position='70:4', label='JOIN tab1 USING (tab_id)'),
        _PartialHint(position='71:4', label='JOIN tab10 USING (tab1_id)'),
    }

    actual_hints = hinting.inlay_hints_work(sections)
    actual_hints = { _PartialHint(repr(a.position), a.label) for a in actual_hints }

    assert actual_hints == expected_hints, _error_message(actual_hints, expected_hints)







def _error_message(actual_hints: set[_PartialHint], expected_hints: set[_PartialHint]) -> str:

    def difference_as_str(hints1: set[_PartialHint], hints2: set[_PartialHint]):
        diff = [h for h in hints1 if h not in hints2]
        diff.sort(key = lambda h: int(h.position.split(':')[0]) * 100 + int(h.position.split(':')[1]))
        diff = '\n\t'.join([str(h) for h in diff])
        return diff

    a_not_e = difference_as_str(actual_hints, expected_hints)
    e_not_a = difference_as_str(expected_hints, actual_hints)
    
    return f"""
    actual - expected: 
        {a_not_e}

    expected - actual: 
        {e_not_a}
    """





"""
hints for multiple queries in one sapi file are incorrect

probably due to rep.str_to in ```line_nr, char = _line_nr_and_char(rep.str_to, lines, line_start_indices)``` 
not accounting for ;
"""



