import os
import pathlib
from lsprotocol import types as t
# from lsprotocol.types import CodeActionOptions, CodeActionKind, CodeActionParams
from tools.server import server
from tools.log import log
import sapi
from sandbox import runtime_model
from tools import data_model

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
    

    sapi_query = '\n'.join([line.strip('\n\r') for line in document.lines]) # assumes the document only contains one query
    # dataModel = runtime_model.make_datamodel() # hardcoded datamodel
    dataModel = data_model.make_datamodel('demo_database').ok
    # show errormessage if it isnt ok. 
    # replace hardcoded 'demo_database' with query to user or a current_database variable in settings

    # log(sapi_query)
    sql_query = sapi.parse(sapi_query, dataModel, str) # try-parse
    # log("\n--- output ---")
    # log(sql_query)


    range_ = t.Range(
        start=t.Position(line=0 + 0, character=0),
        end=t.Position(line=len(document.lines) - 1, character=len(sapi_query) - 1),
    )
    text_edit = t.TextEdit(range=range_, new_text=sql_query)

    action = t.CodeAction(
        title=f"cast to SQL",
        kind=t.CodeActionKind.QuickFix,
        edit=t.WorkspaceEdit(changes={document_uri: [text_edit]}),
    )

    # start_line = params.range.start.line
    # end_line = params.range.end.line

    return [action]

