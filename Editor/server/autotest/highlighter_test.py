from textwrap import dedent
from features import highlighter
from features.highlighter import _EditorAbsToken
from lsprotocol import types as t



def test_tokenize():
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

    required_tokens = [
        _EditorAbsToken(line=1, offset=0, text='WITH', type_str='keyword', modifiers=[]),
        _EditorAbsToken(line=1, offset=5, text='cte', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=1, offset=9, text='AS', type_str='keyword', modifiers=[]),
        _EditorAbsToken(line=1, offset=12, text='(', type_str='other', modifiers=[]),
        _EditorAbsToken(line=2, offset=4, text='SELECT', type_str='keyword', modifiers=[]),
        _EditorAbsToken(line=2, offset=11, text='col0_1', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=2, offset=17, text=',', type_str='other', modifiers=[]),
        _EditorAbsToken(line=2, offset=19, text='col0_2', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=2, offset=25, text=',', type_str='other', modifiers=[]),
        _EditorAbsToken(line=2, offset=27, text='col00_2', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=2, offset=35, text='FROM', type_str='keyword', modifiers=[]),
        _EditorAbsToken(line=2, offset=40, text='tree', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=3, offset=0, text=')', type_str='other', modifiers=[]),
        _EditorAbsToken(line=4, offset=0, text='SELECT', type_str='keyword', modifiers=[]),
        _EditorAbsToken(line=4, offset=7, text='/* hegr', type_str='comment', modifiers=[]),
        _EditorAbsToken(line=4+1, offset=0, text='*/', type_str='comment', modifiers=[]),
        _EditorAbsToken(line=5+1, offset=4, text="'vervre'", type_str='string', modifiers=[]),
        _EditorAbsToken(line=5+1, offset=12, text=',', type_str='other', modifiers=[]),
        _EditorAbsToken(line=6+1, offset=4, text='$$ multi', type_str='string', modifiers=[]),
        _EditorAbsToken(line=7+1, offset=0, text='    line $$', type_str='string', modifiers=[]),
        
        _EditorAbsToken(line=7+1, offset=11, text=',', type_str='other', modifiers=[]),
        _EditorAbsToken(line=8+1, offset=4, text='123', type_str='number', modifiers=[]),
        _EditorAbsToken(line=8+1, offset=7, text=',', type_str='other', modifiers=[]),
        _EditorAbsToken(line=9+1, offset=4, text='cte', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=9+1, offset=7, text='.', type_str='other', modifiers=[]),
        _EditorAbsToken(line=9+1, offset=8, text='col00_2', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=9+1, offset=15, text=',', type_str='other', modifiers=[]),
        _EditorAbsToken(line=10+1, offset=4, text='col10_2', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=10+1, offset=11, text=',', type_str='other', modifiers=[]),
        _EditorAbsToken(line=11+1, offset=4, text='(', type_str='other', modifiers=[]),
        _EditorAbsToken(line=11+1, offset=5, text='SELECT', type_str='keyword', modifiers=[]),
        _EditorAbsToken(line=11+1, offset=12, text='count', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=11+1, offset=17, text='(', type_str='other', modifiers=[]),
        _EditorAbsToken(line=11+1, offset=18, text='col20_2', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=11+1, offset=25, text=')', type_str='other', modifiers=[]),
        _EditorAbsToken(line=11+1, offset=27, text='FROM', type_str='keyword', modifiers=[]),
        _EditorAbsToken(line=11+1, offset=32, text='tree', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=11+1, offset=36, text=')', type_str='other', modifiers=[]),
        _EditorAbsToken(line=12+1, offset=0, text='--FROM tree', type_str='comment', modifiers=[]),
        _EditorAbsToken(line=13+1, offset=0, text='--join cte ON tree.col_1 = cte.col0_1', type_str='comment', modifiers=[]),
        _EditorAbsToken(line=15, offset=0, text='FROM', type_str='keyword', modifiers=[]),
        _EditorAbsToken(line=15, offset=5, text='cte', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=16, offset=0, text='join', type_str='keyword', modifiers=[]),
        _EditorAbsToken(line=16, offset=5, text='tree', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=16, offset=10, text='ON', type_str='keyword', modifiers=[]),
        _EditorAbsToken(line=16, offset=13, text='tree', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=16, offset=17, text='.', type_str='other', modifiers=[]),
        _EditorAbsToken(line=16, offset=18, text='col_1', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=16, offset=24, text='=', type_str='other', modifiers=[]),
        _EditorAbsToken(line=16, offset=26, text='cte', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=16, offset=29, text='.', type_str='other', modifiers=[]),
        _EditorAbsToken(line=16, offset=30, text='col0_1', type_str='variable', modifiers=[]),
        _EditorAbsToken(line=17, offset=0, text=';', type_str='keyword', modifiers=[]),

    ]

    editor_abs_tokens = highlighter.tokenize(sapi)

    for req, act in zip(required_tokens, editor_abs_tokens):
        req.text = req.text.strip()
        act.text = act.text.strip()
        assert act == req, f"expected {req}\nfound {act}"
        
