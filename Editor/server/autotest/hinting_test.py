from collections import namedtuple
from textwrap import dedent
from features import hinting
from tools import embedding


_PartialHint = namedtuple('Hint', ['position', 'label'])

def test_inlay_hints():
    _test_1_inlay_hints()
    _test_2_inlay_hints()

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
    sections = embedding.freeform_single_section(lines, True)
    # sapi_code = sections[0].leading_whitespace + sections[0].query # temp
    # lines_2 = sapi_code.split('\n')

    expected_hints = {
        _PartialHint(position='4:3', label=' tab0'),
        _PartialHint(position='4:5', label='JOIN tab00 USING ( tab0_id )'),
        _PartialHint(position='15:12', label=' tab20'),
        _PartialHint(position='18:4', label=' tab'),
        _PartialHint(position='18:12', label=' tab'),
        _PartialHint(position='18:33', label='JOIN tab1 USING ( tab_id )'),
        _PartialHint(position='19:33', label='JOIN tab10 USING ( tab1_id )'),
    }

    actual_hints = hinting.inlay_hints_work(sections)
    actual_hints = { _PartialHint(repr(a.position), a.label) for a in actual_hints }

    assert actual_hints == expected_hints, _error_message(actual_hints, expected_hints)


def _test_2_inlay_hints():
    sapi = dedent('''
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

''')
    lines = sapi.split('\n')
    sections = embedding.sapi_sections(lines, True)
    # sapi_code = sections[0].leading_whitespace + sections[0].query # temp
    # lines_2 = sapi_code.split('\n')

    # expected_hints = {
    #     _PartialHint(position='4:3', label=' tab0'),
    #     _PartialHint(position='4:5', label='JOIN tab00 USING ( tab0_id )'),
    #     _PartialHint(position='15:12', label=' tab20'),
    #     _PartialHint(position='18:4', label=' tab'),
    #     _PartialHint(position='18:12', label=' tab'),
    #     _PartialHint(position='18:33', label='JOIN tab1 USING ( tab_id )'),
    #     _PartialHint(position='19:33', label='JOIN tab10 USING ( tab1_id )'),
    # }

    actual_hints = hinting.inlay_hints_work(sections)
    # actual_hints = { _PartialHint(repr(a.position), a.label) for a in actual_hints }

    # assert actual_hints == expected_hints, _error_message(actual_hints, expected_hints)


def _error_message(actual_hints: set[_PartialHint], expected_hints: set[_PartialHint]) -> str:
    a_not_e = {a for a in actual_hints if a not in expected_hints}
    e_not_a = {e for e in expected_hints if e not in actual_hints}
    
    return f"""
    actual - expected = {a_not_e}
    expected - actual = {e_not_a}
    """
