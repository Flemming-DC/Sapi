from tools import settings
from features import highlighter, executor, hinting
from autotest.highlighter_test import test_tokenize
from lsprotocol import types as t


if __name__ == '__main__':
    sapi = """

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
    lines = sapi.split('\n')
    uri="C:\Mine\Python\Sapi\Editor\manual_test\query.sapi"

    hints = hinting.inlay_hints_work(lines)
    for hint in hints:
        print(hint.label)

    print("done")        
