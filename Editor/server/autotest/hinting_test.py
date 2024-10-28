from collections import namedtuple
from textwrap import dedent
from features import hinting



def test_inlay_hints():
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
    
    PartialHint = namedtuple('Hint', ['position', 'label'])
    expected = {
        PartialHint(position='4:3', label=' tab0'),
        PartialHint(position='4:5', label='JOIN tab00 USING ( tab0_id )'),
        PartialHint(position='15:12', label=' tab20'),
        PartialHint(position='18:4', label=' tab'),
        PartialHint(position='18:12', label=' tab'),
        PartialHint(position='18:33', label='JOIN tab1 USING ( tab_id )'),
        PartialHint(position='19:33', label='JOIN tab10 USING ( tab1_id )'),
    }

    actual_hints = hinting.inlay_hints_work(lines)
    actual_hints = { PartialHint(repr(a.position), a.label) for a in actual_hints }

    assert actual_hints == expected, "Error in Hinting"

