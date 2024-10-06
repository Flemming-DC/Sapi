from pygls.server import LanguageServer
from pygls.workspace.text_document import TextDocument
from lsprotocol import types
from tools.server import server
from tools.log import log

_current_uri = None

class _:

    # Handler for when a document is opened
    @server.feature(types.TEXT_DOCUMENT_DID_OPEN)
    def _on_document_open(server_: LanguageServer, params: types.DidOpenTextDocumentParams):
        uri = params.text_document.uri
        document = server_.workspace.get_document(uri)
        _split_document_into_queries(document)
        # log(f"Document opened: {document.uri}")
        # log(f"Initial content:\n{document.source}")

    
    @server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
    def _on_document_change(server_: LanguageServer, params: types.DidChangeTextDocumentParams):
        uri = params.text_document.uri
        document = server_.workspace.get_document(uri)
        # TODO: for performance, only look at the changes, not the whole file.
        _split_document_into_queries(document)
        
        # for change in params.content_changes:
        #     log(f"Document edited: {document.uri}")
        #     log(f"New content:\n{change.text}")
            
        #     # You can also get the full updated document content
        #     log(f"Updated document content:\n{document.source}")

# document has
    # uri: str,
    # source: Optional[str] = None,
    # language_id: Optional[str] = None,

def _split_document_into_queries(document: TextDocument):
    # hyp, if extension if sql or sapi, then call sapi.parse on the 
    # entire document. Else, find the quri inside and then call sapi.parse
    # nb: probably pick the token-tree output type.
    
    document.source
    ...


def _is_query_start(file_ext: str, word: str) -> bool:
    # eventually read from settings. For now just hardcode
    # hyp start after error and after ;
    
    query_starters = [ # this list is probably to short. Get the real list from sqlglot
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE', 
        'CREATE', 'ALTER', 'DROP', 'SET', 
        'GRANT', 'REVOKE']
    
    if file_ext in ['sql', 'sapi']:
        return word in query_starters
    else:
        raise NotImplementedError("embedded sapi isnt yet supported.")


def _is_query_end(file_ext: str, char: str) -> bool:
    # eventually read from settings. For now just hardcode
    if file_ext in ['sql', 'sapi']:
        return ';' == char
    else:
        raise NotImplementedError("embedded sapi isnt yet supported.")



"""
That list of keywords is too short. It lacks DO and probably a bunch of other obscurities.

"begin": "(?i)\\s*([^']'''|[^']'|[^\"]\"\"\"|[^\"]\")\\s*(SELECT|INSERT|DELETE|UPDATE|DROP|ALTER|CREATE|SET|TRUNCATE|GRANT|REVOKE)\\s",
"end": "('''[^']|'[^']|\"\"\"[^\"]|\"[^\"])",

"begin": "(?i)\\w\\s*:\\s*Query\\s*=\\s*([^']'''|[^']'|[^\"]\"\"\"|[^\"]\")",
"end": "('''[^']|'[^']|\"\"\"[^\"]|\"[^\"])",
"""

