############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License")           #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http: // www.apache.org/licenses/LICENSE-2.0                         #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################
"""This implements the :lsp:`textDocument/inlayHint` and :lsp:`inlayHint/resolve`
requests.

In editors
`like VSCode <https://code.visualstudio.com/Docs/editor/editingevolved#_inlay-hints>`__
inlay hints are often rendered as inline "ghost text".
They are typically used to show the types of variables and return values from functions.

This server implements ``textDocument/inlayHint`` to scan the given document for integer
values and returns the equivalent representation of that number in binary.
While we could easily compute the inlay hint's tooltip in the same method, this example
uses the ``inlayHint/resolve`` to demonstrate how you can defer expensive computations
to when they are required.
"""

import re
from typing import Optional

from lsprotocol import types
# from pygls.lsp.server import LanguageServer
# from pygls.server import LanguageServer
from tools.server import server, serverType
from tools.log import log
from tools import data_model
import sapi

NUMBER = re.compile(r"\d+")
# server = LanguageServer("inlay-hint-server", "v1")


def parse_int(chars: str) -> Optional[int]:
    try:
        return int(chars)
    except Exception:
        return None


@server.feature(types.TEXT_DOCUMENT_INLAY_HINT)
def inlay_hints(params: types.InlayHintParams):
    items = []
    document_uri = params.text_document.uri
    document = server.workspace.get_text_document(document_uri)

    start_line = params.range.start.line
    end_line = params.range.end.line

    lines = document.lines[start_line : end_line + 1]
    log(start_line, end_line + 1, len(document.lines), len(lines)) # 0 8 7 7
    
    # early placement

    uri = params.text_document.uri
    if not uri.endswith('.sapi'):
        return []
    document = server.workspace.get_text_document(uri)
    sapi_code = document.source


    lines = document.lines
    hint = types.InlayHint(
        label=f":hejsahejsahejsahejsahejsa",
        kind=types.InlayHintKind.Type,
        padding_left=False,
        padding_right=True,
        position=types.Position(line=len(lines)-5, character=1),
    )

    dataModel = data_model.make_datamodel()
    # sql_query = sapi.parse(sapi_code, dataModel, out???)
    sql_query = sapi.parse(sapi_code, dataModel, str)


    items = []
    document_uri = params.text_document.uri
    document = server.workspace.get_text_document(document_uri)

    start_line = params.range.start.line
    end_line = params.range.end.line


    return [hint]


# @server.feature(types.INLAY_HINT_RESOLVE)
# def inlay_hint_resolve(hint: types.InlayHint):
#     try:
#         n = int(hint.label[1:], 2)
#         hint.tooltip = f"Binary representation of the number: {n}"
#     except Exception:
#         pass

#     return hint


# if __name__ == "__main__":
#     server.start_io()
