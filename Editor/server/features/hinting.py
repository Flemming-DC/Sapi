from lsprotocol import types as t
from tools.server import server, serverType
from tools.log import log
from tools import error
from lsprotocol import types as t
import sapi
from sapi._editor import TokenTree
from tools.server import server
from tools import data_model
from tools.settings import Settings
from tools.command import command
from tools import error



@server.feature(t.TEXT_DOCUMENT_INLAY_HINT)
@error.as_log_and_popup
def inlay_hints(params: t.InlayHintParams) -> list[t.InlayHint]:
    uri = params.text_document.uri
    if not uri.endswith('.sapi'):
        return []
    document = server.workspace.get_text_document(uri)
    sapi_code = document.source
    r = params.range
    lines = document.lines[r.start.line : r.end.line + 1]

    # sapi_code = '\r\n'.join([line.strip('\n\r') for line in lines]) # does this work for multiple queries?
    dataModel = data_model.make_datamodel()
    # sql_query = sapi.parse(sapi_code, dataModel, out???)
    sql_token_trees = sapi.parse(sapi_code, dataModel, list[TokenTree])
    sql_query = '\n;\n'.join(str(t) for t in sql_token_trees)
    sql_lines = sql_query.split('\n')
    hints = []
    for i, line in enumerate(sql_lines):
        hint = t.InlayHint(
            label=line.strip(),
            kind=t.InlayHintKind.Type,
            padding_left=False,
            padding_right=True,
            position=t.Position(line=i, character=0),
        )
        hints.append(hint)

    return hints


@server.feature(t.INLAY_HINT_RESOLVE)
def inlay_hint_resolve(hint: t.InlayHint):
    try:
        n = int(hint.label[1:], 2)
        hint.tooltip = f"Binary representation of the number: {n}"
    except Exception:
        pass

    return hint





