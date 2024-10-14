from tools import settings
from features import highlighter
from features.highlighter import _EditorAbsToken

# dataModel = data_model.make_datamodel()
# print(dataModel)

sql_ = """
    WITH cte AS (
        SELECT tab0.col0_1, tab0.col0_2, tab00.col00_2 FROM tab0
        JOIN tab00 USING (tab0_id))
    SELECT 
        cte.col00_2,
        tab10.col10_2,
        (SELECT count(tab20.col20_2) FROM tab20)
    --FROM tree
    --join cte ON tree.col_1 = cte.col0_1
    FROM cte 
    join tab ON tab.col_1 = cte.col0_1
    JOIN tab1 USING (tab_id)
    JOIN tab10 USING (tab1_id)"""

required_token_texts_ = [
    'WITH', 'cte', 'AS', '(',
        'SELECT', 'tab0', '.', 'col0_1', ',', 'tab0', '.', 'col0_2', ',', 'tab00', '.', 'col00_2', 'FROM', 'tab0',
        'JOIN', 'tab00', 'USING', '(', 'tab0_id', ')', ')',
    'SELECT', 
        'cte', '.', 'col00_2', ',',
        'tab10', '.', 'col10_2', ',',
        '(', 'SELECT', 'count', '(', 'tab20', '.', 'col20_2', ')', 'FROM', 'tab20', ')',
    '--FROM tree',
    '--join cte ON tree.col_1 = cte.col0_1',
    'FROM', 'cte', 
    'join', 'tab', 'ON', 'tab', '.', 'col_1', '=', 'cte', '.', 'col0_1',
    'JOIN', 'tab1', 'USING', '(', 'tab_id', ')',
    'JOIN', 'tab10', 'USING', '(', 'tab1_id', ')',
]

sql = """
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

required_token_texts = [
    'WITH', 'cte', 'AS', '(',
        'SELECT', 'col0_1', ',', 'col0_2', ',', 'col00_2', 'FROM', 'tree',
    ')',
    'SELECT', '/* hegr ',
    '*/',
        "'vervre'", ',',
        "$$ multi",
    "    line $$", ',',
        '123', ',',
        'cte', '.', 'col00_2', ',',
        'col10_2', ',',
        '(', 'SELECT', 'count', '(', 'col20_2', ')', 'FROM', 'tree', ')',
    '--FROM tree',
    '--join cte ON tree.col_1 = cte.col0_1',
    'FROM', 'cte', 
    'join', 'tree', 'ON', 'tree', '.', 'col_1', '=', 'cte', '.', 'col0_1',
    ';'
]

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

    # _EditorAbsToken(line=12, offset=50, text='FROM', type_str='keyword', modifiers=[]),
    # _EditorAbsToken(line=12, offset=55, text='cte', type_str='variable', modifiers=[]),
    # _EditorAbsToken(line=13, offset=0, text='join', type_str='keyword', modifiers=[]),
    # _EditorAbsToken(line=13, offset=5, text='tree', type_str='variable', modifiers=[]),
    # _EditorAbsToken(line=13, offset=10, text='ON', type_str='keyword', modifiers=[]),
    # _EditorAbsToken(line=13, offset=13, text='tree', type_str='variable', modifiers=[]),
    # _EditorAbsToken(line=13, offset=17, text='.', type_str='other', modifiers=[]),
    # _EditorAbsToken(line=13, offset=18, text='col_1', type_str='variable', modifiers=[]),
    # _EditorAbsToken(line=13, offset=24, text='=', type_str='other', modifiers=[]),
    # _EditorAbsToken(line=13, offset=26, text='cte', type_str='variable', modifiers=[]),
    # _EditorAbsToken(line=13, offset=29, text='.', type_str='other', modifiers=[]),
    # _EditorAbsToken(line=13, offset=30, text='col0_1', type_str='variable', modifiers=[]),
    # _EditorAbsToken(line=14, offset=0, text=';', type_str='keyword', modifiers=[]),
]
# executor.execute(sql)

if __name__ == '__main__':
    # try:
    #     s = settings._load()
    # except Exception as e:

    editor_abs_tokens = highlighter._tokenize(sql)
    # for tok in editor_abs_tokens:
    #     print(tok)
    print('--------')
    for req, act in zip(required_token_texts, editor_abs_tokens):
        print(req)
        assert act.text == req, f"expected {req}, found {act.text}"
        req = req.strip()
        if req.startswith('--') or req.startswith('/*') or req.startswith('*/'):
            assert act.type_str == 'comment', f"expected comment, found {act.type_str}"
        if req.startswith("'") or req.startswith("$$") or req.endswith("'") or req.endswith("$$"):
            assert act.type_str == 'string', f"expected string, found {act.type_str}"

    print('--------')
    for req, act in zip(required_tokens, editor_abs_tokens):
        print(req.text)
        req.text = req.text.strip()
        act.text = act.text.strip()
        assert act == req, f"expected {req}\nfound {act}"
        
