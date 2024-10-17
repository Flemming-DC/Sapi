from lsprotocol import types as t
from sapi._editor import editor_tok
from tools.server import server, serverType
from tools import error
from . import tokenizer, reformatter


@server.feature(
    t.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    t.SemanticTokensLegend(token_types=editor_tok.token_type_names(), 
                           token_modifiers=[m.name for m in tokenizer.TokenModifier]))
@error.as_log_and_popup
def highlight(_: serverType, params: t.SemanticTokensParams) -> t.SemanticTokens | None:
    uri = params.text_document.uri
    if not uri.endswith('.sapi'):
        return None
    document = server.workspace.get_text_document(uri)
    sapi_code = document.source
    return _highlight_work(sapi_code)


def _highlight_work(sapi_code) -> t.SemanticTokens | None:
    """Return the semantic tokens for the entire document"""
    editor_abs_tokens = tokenizer.tokenize(sapi_code)
    return reformatter.abs_to_semantic_tokens(editor_abs_tokens)






"""

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



