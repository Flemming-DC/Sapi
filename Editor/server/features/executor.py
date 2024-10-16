from lsprotocol import types as t
from typing import Sequence
import sapi
from tools.server import server
from tools import data_model
from tools.settings import Settings
from tools.command import command
from tools import error
from pygls.workspace.text_document import TextDocument

# register code action ideally by ctrl-enter-enter. 
# first connect, then execute or parse (you choose)
# if connect: how to get connection?
# store connection info in sapi_settings.json in .vscode (evt. use some builtin lsp settings feature)
# store dialect (by name) in sapi_settings.
# rely on the builtin dialect class to provide the dialect instance given the name. 
#   The issue of whether and how to expose the dialect class is saved for later

@server.feature(
    t.TEXT_DOCUMENT_CODE_ACTION,
    t.CodeActionOptions(code_action_kinds=[t.CodeActionKind.QuickFix]))
@error.as_log_and_popup
def code_actions(params: t.CodeActionParams) -> list[t.CodeAction]:
    uri = params.text_document.uri
    if not uri.endswith('.sapi'):
        return []
    document = server.workspace.get_text_document(uri)
    r = params.range # range is selected range.
    lines = document.lines #[r.start.line : r.end.line + 1]
    return code_actions_work(lines, uri)

    
def code_actions_work(lines: list[str], uri: str) -> list[t.CodeAction]:
    dataModel = data_model.make_datamodel()
    sapi_query = '\n'.join([line.strip('\n\r') for line in lines]) # does this work for multiple queries?
    sql_query = sapi.parse(sapi_query, dataModel, str) # try-parse


    range_ = t.Range(
        start=t.Position(line=0 + 0, character=0),
        end=t.Position(line=len(lines) - 1, character=len(sapi_query) - 1))
    text_edit = t.TextEdit(range=range_, new_text=sql_query)

    cast_to_sql = t.CodeAction(
        title=f"Cast to SQL",
        kind=t.CodeActionKind.Empty,
        edit=t.WorkspaceEdit(changes={uri: [text_edit]}))
    execute = t.CodeAction(
        title=f"Execute",
        kind=t.CodeActionKind.Empty,
        command=t.Command(title=_execute.__name__, command=_execute.__name__, arguments=[sql_query]))


    return [execute, cast_to_sql]


@command
@error.as_log_and_popup
def _execute(sql_query: str) -> Sequence[Sequence]:
    fal_database = Settings.load_database()
    
    con = fal_database.dialect.connect(**fal_database.connection_info)
    cur = con.cursor()
    cur.execute("set search_path to sapi_demo") # temp
    cur.execute(sql_query)
    data = cur.fetchall()
    con.commit()
    con.close()
    return data



