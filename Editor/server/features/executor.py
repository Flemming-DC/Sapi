from lsprotocol import types as t
from typing import Sequence
import sapi
from tools.server import server
from tools.command import command
from tools import error, settings, log

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
    if not any(uri.endswith(file_type) for file_type in server.file_types()):
        return []
    document = server.workspace.get_text_document(uri)
    r = params.range # range is the selected range.
    # lines = document.lines #[r.start.line : r.end.line + 1]
    lines = server.sapi_lines(uri) #[r.start.line : r.end.line + 1]
    return code_actions_work(lines, uri)

    
def code_actions_work(lines: list[str], uri: str) -> list[t.CodeAction]:
    if lines == []: return []
    sapi_code = '\n'.join([line.strip('\n\r') for line in lines]) # does this work for multiple queries?
    # if not uri.endswith('.sapi'):
    #     sapi_code = _clear_non_sapi_code(sapi_code)
    dataModel = settings.load_datamodel()
    try:
        sql_query = sapi.parse(sapi_code, dataModel, str) # try-parse
    except Exception as e: # create a user error class for the parser and filter by it
        code_start = sapi_code if len(sapi_code) < 10 else sapi_code[:10] + '...'
        log.log(f"Failed to parse ['''{code_start}''']:\nError: {e}")
        return [] # produce error message in output rather than removing code actions
    


    range_ = t.Range(
        start=t.Position(line=0 + 0, character=0),
        end=t.Position(line=len(lines) - 1, character=len(sapi_code) - 1))
    text_edit = t.TextEdit(range=range_, new_text=sql_query)

    cast_to_sql = t.CodeAction(
        title=f"Cast to SQL",
        kind=t.CodeActionKind.Empty,
        edit=t.WorkspaceEdit(changes={uri: [text_edit]}))
    execute = t.CodeAction(
        title=f"Execute",
        kind=t.CodeActionKind.Empty,
        command=t.Command(title=_execute.__name__, command=_execute.__name__, arguments=[sql_query]))
    log_ = t.CodeAction(
        title=f"Log",
        kind=t.CodeActionKind.Empty,
        command=t.Command(title=_log.__name__, command=_log.__name__, arguments=[sapi_code]))


    return [execute, cast_to_sql, log_]

@command
@error.as_log_and_popup
def _log(msg: str) -> str:
    return msg

@command
@error.as_log_and_popup
def _execute(sql_query: str) -> Sequence[Sequence]:
    database = settings.load_database()
    # error: multiple _execute calls can fit into the same transaction.
    # you need to keep a connection alive between transactions.
    with sapi.Transaction(database) as tr:
        return tr.execute_plain_sql(sql_query).rows()

    # con = database.dialect.connect(**database.connect_kwargs)
    # cur = con.cursor()
    # cur.execute("set search_path to sapi_demo") # temp
    # cur.execute(sql_query)
    # data = cur.fetchall()
    # con.commit()
    # con.close()
    # return data


def _clear_non_sapi_code(sapi_code: str) -> str:
    sections = sapi_code.split('"""')
    if len(sections) >= 2:
        whitespace = ''.join(['\n' if char == '\n' else ' ' for char in sections[0]])
        return whitespace + sections[1]
    else:
        return sections[0]

"""

cast to sql removes the trailing semicolon
-------

"""

