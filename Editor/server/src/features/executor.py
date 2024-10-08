import os
import pathlib
from lsprotocol import types as t
# from lsprotocol.types import CodeActionOptions, CodeActionKind, CodeActionParams
from tools.server import server
from tools.log import log
import sapi
# from sandbox import runtime_model
from tools import data_model
from sapi import DataModel
from tools.fallible import err
from tools.settings import Settings
from pygls.server import LanguageServer

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
def code_actions(params: t.CodeActionParams) -> list[t.CodeAction]:
    # log("\n--- code_actions ---\n")
    document_uri = params.text_document.uri
    if not document_uri.endswith('.sapi'):
        return []
    document = server.workspace.get_text_document(document_uri)
    

    # dataModel = runtime_model.make_datamodel() # hardcoded datamodel
    fal_dataModel = data_model.make_datamodel()
    if fal_dataModel.is_err():
        server.show_message(fal_dataModel.err, t.MessageType.Error)
        return []

    sapi_query = '\n'.join([line.strip('\n\r') for line in document.lines]) # assumes the document only contains one query
    sql_query = sapi.parse(sapi_query, fal_dataModel.ok, str) # try-parse


    range_ = t.Range(
        start=t.Position(line=0 + 0, character=0),
        end=t.Position(line=len(document.lines) - 1, character=len(sapi_query) - 1),
        )
    text_edit = t.TextEdit(range=range_, new_text=sql_query)

    Cast_to_SQL = t.CodeAction(
        title=f"Cast to SQL",
        kind=t.CodeActionKind.Empty,
        edit=t.WorkspaceEdit(changes={document_uri: [text_edit]}),
        )
    Execute = t.CodeAction(
        title=f"Execute",
        kind=t.CodeActionKind.Empty,
        command=t.Command(title=_execute.__name__, command=_execute.__name__, arguments=[sql_query]),
        )

    # start_line = params.range.start.line
    # end_line = params.range.end.line

    return [Execute, Cast_to_SQL]



@server.command('_execute')
def _execute(_: LanguageServer, params: list[str]):
# def execute(sql_query: str):
    # WOW! et cirkus. Det må kunne gøres nemmere !
    if len(params) != 1 or not isinstance(params[0], str):
        server.show_message("_execute expects a list[str] containing a single element, namely a query. Received: \n"
            f"{params}", t.MessageType.Error)
        return
    
    sql_query = params[0]
    log(type(sql_query[0]))
    log(sql_query[0])
    fal_settings = Settings.try_load()
    if not fal_settings: 
        return err("Failed to execute query, due to error in settings file:\n" + str(fal_settings.err))

    database_name = fal_settings.ok.current_database
    database = fal_settings.ok.databases[database_name]

    con = database.dialect.connect(**database.connection_info) # can raise
    cur = con.cursor()
    cur.execute("set search_path to sapi_demo")
    cur.execute(sql_query) # can raise
    data = cur.fetchall()
    con.commit()
    con.close()

    server.show_message(str(data), t.MessageType.Info) # how to dumb data properly ?



# t.Command(title='_helloWorld', command='helloWorld', arguments=[param]),
# @server.command('helloWorld')
# def _helloWorld(ls: LanguageServer, param):
#     ls.show_message('Hello, World!', t.MessageType.Info)