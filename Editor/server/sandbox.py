from tools import settings
from features import highlighter, executor
from autotest.highlighter_test import test_tokenize
from lsprotocol import types as t


if __name__ == '__main__':
    _semanticTokensParams = t.SemanticTokensParams(
        text_document = t.TextDocumentIdentifier(uri="C:\Mine\Python\Sapi\Editor\manual_test\query.sapi"),
        work_done_token = None,
        partial_result_token = None,
    )
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

    out_h = highlighter._highlight_work(sapi)
    # print(out_h)
    out_e = executor.code_actions_work(lines, uri)
    print(out_e)

    print("done")        
