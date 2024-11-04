import os
from lsprotocol import types as t
from sapi._editor import editor_tok
from tools.server import server, serverType
from tools import error, log
from tools.embedding import Section
from . import tokenizer, reformatter


@server.feature(
    t.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    t.SemanticTokensLegend(token_types=editor_tok.token_type_names(), 
                           token_modifiers=[m.name for m in tokenizer.TokenModifier]))
@error.as_log_and_popup
def highlight(_: serverType, params: t.SemanticTokensParams) -> t.SemanticTokens | None:
    uri = params.text_document.uri
    # if not uri.endswith('.sapi'): return None
    if not any(uri.endswith(file_type) for file_type in server.file_types()): 
        return None
    sections = server.sapi_sections(uri)
    sapi_code = sections[0].leading_whitespace + sections[0].query # temp
    lines = sapi_code.split('\n')
    # lines = server.sapi_lines(uri)
    sapi_code = os.linesep.join([line.strip('\n\r') for line in lines])
    return _highlight_work(sapi_code)



def _highlight_work(sapi_code: str) -> t.SemanticTokens | None:
    """Return the semantic tokens for the entire document"""
    editor_abs_tokens = tokenizer.tokenize(sapi_code)
    return reformatter.abs_to_semantic_tokens(editor_abs_tokens)



r"""

Traceback (most recent call last):
  File "c:\Mine\Python\Sapi\Editor\local_editor_env\lib\site-packages\sqlglot\tokens.py", line 993, in tokenize
    self._scan()
  File "c:\Mine\Python\Sapi\Editor\local_editor_env\lib\site-packages\sqlglot\tokens.py", line 1026, in _scan
    self._scan_keywords()
  File "c:\Mine\Python\Sapi\Editor\local_editor_env\lib\site-packages\sqlglot\tokens.py", line 1159, in _scan_keywords
    if self._scan_comment(word):
  File "c:\Mine\Python\Sapi\Editor\local_editor_env\lib\site-packages\sqlglot\tokens.py", line 1206, in _scan_comment
    self._advance(comment_end_size - 1)
  File "c:\Mine\Python\Sapi\Editor\local_editor_env\lib\site-packages\sqlglot\tokens.py", line 1054, in _advance
    self._char = self.sql[self._current - 1]
IndexError: string index out of range



"""

# hyp: define semantic token scopes to create a textmate version of our scopes.
#      embed these tokens via an injection gramma

#      alternatively. use source.sql & injection gramma to provide embedded highlighting.
#      Base this of the highlight string extension.

