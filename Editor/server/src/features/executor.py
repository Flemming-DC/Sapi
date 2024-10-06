import os
import pathlib
from lsprotocol import types
from tools.server import server
from tools.log import log

# register code action ideally by ctrl-enter-enter. 
# first connect, then execute or parse (you choose)
# if connect: how to get connection?
# store connection info in sapi_settings.json in .vscode (evt. use some builtin lsp settings feature)
# store dialect (by name) in sapi_settings.
# rely on the builtin dialect class to provide the dialect instance given the name. 
#   The issue of whether and how to expose the dialect class is saved for later

@server.feature(
    types.TEXT_DOCUMENT_CODE_ACTION,
    types.CodeActionOptions(code_action_kinds=[types.CodeActionKind.QuickFix]))
def code_actions(params: types.CodeActionParams):
    items = []
    document_uri = params.text_document.uri
    document = server.workspace.get_text_document(document_uri)

    start_line = params.range.start.line
    end_line = params.range.end.line

    lines = document.lines[start_line : end_line + 1]
    # log(document.lines)
    # log("----")
    # log(lines)
    # for idx, line in enumerate(lines):
    #     match = ADDITION.match(line)
    #     if match is not None:
    #         range_ = types.Range(
    #             start=types.Position(line=start_line + idx, character=0),
    #             end=types.Position(line=start_line + idx, character=len(line) - 1),
    #         )

    #         left = int(match.group(1))
    #         right = int(match.group(2))
    #         answer = left + right

    #         text_edit = types.TextEdit(
    #             range=range_, new_text=f"{line.strip()} {answer}!"
    #         )

    #         action = types.CodeAction(
    #             title=f"Evaluate '{match.group(0)}'",
    #             kind=types.CodeActionKind.QuickFix,
    #             edit=types.WorkspaceEdit(changes={document_uri: [text_edit]}),
    #         )
    #         items.append(action)

    return items


"""
['1 + 1 =\n', '\n', '\n', '2 + 3 = \n', '\n', 'select 1\n', 'from hi\n', ';\n', '\n', '6 + 6 =\n']
----
['from hi\n']
['1 + 1 =\n', '\n', '\n', '2 + 3 = \n', '\n', 'select 1\n', 'from hi\n', ';\n', '\n', '6 + 6 =\n']
----
['from hi\n']
["['1 + 1 =\\n', '\\n', '\\n', '2 + 3 = \\n', '\\n', 'select 1\\n', 'from hi\\n', ';\\n', '\\n', '6 + 6 =\\n']\r\n", '----\r\n', "['from hi\\n']\r\n", "['1 + 1 =\\n', '\\n', '\\n', '2 + 3 = \\n', '\\n', 'select 1\\n', 'from hi\\n', ';\\n', '\\n', '6 + 6 =\\n']\r\n", '----\r\n', "['from hi\\n']\r\n"]
----
["['1 + 1 =\\n', '\\n', '\\n', '2 + 3 = \\n', '\\n', 'select 1\\n', 'from hi\\n', ';\\n', '\\n', '6 + 6 =\\n']\r\n"]
"""

