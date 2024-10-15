from copy import copy
import operator
from typing import Type
from functools import reduce
from enum import IntFlag, auto
from lsprotocol import types as t
from tools.server import server, serverType
from sapi import _editor_tok
from dataclasses import dataclass
from tools.log import log
from tools.settings import Settings
from tools import error, event
from sqlglot.tokens import Token as GlotToken, TokenType as GlotType


class _TokenModifier(IntFlag):
    definition = auto()

@dataclass
class _EditorRelToken:
    delta_line: int
    delta_offset: int
    text: str
    type_str: str
    modifiers: list[_TokenModifier]

@dataclass
class _EditorAbsToken:
    "Output of tokenizer. Must be converted to _EditorRelToken."
    line: int
    offset: int
    text: str
    type_str: str
    modifiers: list[_TokenModifier]

@dataclass
class _Location:
    "Used in tokenizer and its helper function"
    line_nr: int = 0
    line_start_index: int = 0
    i: int = 0
    def new_line(_): 
        _.line_nr += 1
        _.line_start_index = _.i + 1
        _.i += 1

@server.feature(
    t.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    t.SemanticTokensLegend(token_types=_editor_tok.token_type_names(), 
                           token_modifiers=[m.name for m in _TokenModifier]))
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
    editor_abs_tokens = tokenize(sapi_code)
    editor_rel_tokens = _editor_rel_tokens(editor_abs_tokens)
    return _semantic_tokens(editor_rel_tokens)


def tokenize(sapi_code: str) -> list[_EditorAbsToken]:
    """
    match next_tok start_index: eat to end_index and collect glot_token, seperately for each line
    match single_line_comment_markers: eat to end of line and collect comment_token
    match multi_line_comment_start_markers: eat to end marker and collect comment_token, seperately for each line
    match \n: eat \n and update line_nr, line_start_index
    """
    glot_dialect = Settings.load_database().dialect.sqlglot_dialect()
    glot_tokens = glot_dialect.tokenize(sapi_code)
    comment_markers: list[str | tuple[str, str]] = glot_dialect.tokenizer.COMMENTS
    if len(glot_tokens) == 0: 
        return
    next_glot_tok_idx: int = 0
      
    single_line_1_char_comment_markers = [m for m in comment_markers if isinstance(m, str) and len(m) == 1] # subset of ['--']
    single_line_2_char_comment_markers = [m for m in comment_markers if isinstance(m, str) and len(m) == 2] # subset of ['--', '#!', '//']
    multi_line_comment_end_by_start_markers = {mp[0]: mp[1] for mp in comment_markers if isinstance(mp, tuple)} # = {'/*': '*/'}
    

    loc = _Location(0, 0, 0)
    editor_tokens: list[_EditorAbsToken] = []
    count = len(sapi_code)
    def char(i: int): return sapi_code[i]
    def two_char(i: int): return sapi_code[i] + (sapi_code[i + 1] if i + 1 < count else '')
    
    while loc.i < count:
        next_glot_tok: GlotToken = glot_tokens[next_glot_tok_idx] if next_glot_tok_idx < len(glot_tokens) else None

        if next_glot_tok and loc.i == next_glot_tok.start:
            # eat to end_index and collect glot_token, seperately for each line
            next_glot_tok_idx += 1
            loc_start = copy(loc)
            while loc.i < next_glot_tok.end and loc.i < count: 
                loc.i += 1
                if char(loc.i) == '\n':
                    editor_tokens.append(_make_editor_token(sapi_code, next_glot_tok.token_type, loc_start, loc.i))
                    loc.new_line()
                    loc_start = copy(loc)
            editor_tokens.append(_make_editor_token(sapi_code, next_glot_tok.token_type, loc_start, loc.i))
            loc.i += 1
        elif char(loc.i) in single_line_1_char_comment_markers or two_char(loc.i) in single_line_2_char_comment_markers:
            # eat to end of line and collect comment_token
            loc_start = copy(loc)
            while char(loc.i) != '\n' and loc.i < count: 
                loc.i += 1
            editor_tokens.append(_make_editor_token(sapi_code, None, loc_start, loc.i))
        elif two_char(loc.i) in multi_line_comment_end_by_start_markers.keys():
            # eat to end marker and collect comment_token, seperately for each line
            end_marker = multi_line_comment_end_by_start_markers[two_char(loc.i)]
            loc_start = copy(loc)
            while two_char(loc.i) != end_marker and loc.i < count: 
                loc.i += 1
                if char(loc.i) == '\n':
                    editor_tokens.append(_make_editor_token(sapi_code, None, loc_start, loc.i))
                    loc.new_line()
                    loc_start = copy(loc)
            loc.i += 2 # end_marker is two characters long, so we make a double step
            editor_tokens.append(_make_editor_token(sapi_code, None, loc_start, loc.i))
        elif char(loc.i) == '\n':
            loc.new_line()
        else:
            loc.i += 1
        
    return editor_tokens


def _make_editor_token(sapi_code: str, glot_type: GlotType|None, loc_start: _Location, index_end: int) -> _EditorAbsToken:

    line_start_index = loc_start.line_start_index
    offset = loc_start.i - line_start_index
    error.dev_assert(offset >= 0, f"offset = {offset} = {loc_start.i} - {line_start_index}")

    tok = _EditorAbsToken(
        line = loc_start.line_nr,
        offset = offset,
        text = sapi_code[loc_start.i : index_end + 1].strip('\r\n'), 
        type_str = _editor_tok.get_group_names(glot_type if glot_type else _editor_tok.fake_comment_glot_type()),
        modifiers = [], # no modifiers to begin with
        )
    return tok


def _editor_rel_tokens(editor_abs_tokens: list[_EditorAbsToken]) -> list[_EditorRelToken]:
    editor_rel_tokens: list[_EditorRelToken] = []
    last_line = 0
    last_offset = 0
    for abs_tok in editor_abs_tokens:
        delta_line = abs_tok.line - last_line
        delta_offset = abs_tok.offset - last_offset if delta_line == 0 else abs_tok.offset

        rel_tok = _EditorRelToken(
            delta_line = delta_line,
            delta_offset = delta_offset,
            text = abs_tok.text,
            type_str = abs_tok.type_str,
            modifiers = abs_tok.modifiers,
            )
        editor_rel_tokens.append(rel_tok)

        last_line = abs_tok.line
        last_offset = abs_tok.offset

    return editor_rel_tokens


def _semantic_tokens(editor_tokens: list[_EditorRelToken]) -> t.SemanticTokens:
    data = []
    for tok in editor_tokens:
        data.extend([
            tok.delta_line,
            tok.delta_offset,
            len(tok.text),
            _editor_tok.token_type_names().index(tok.type_str), # returns index into token_type_names
            reduce(operator.or_, tok.modifiers, 0), # returns bitmap into modifier_names
        ])
    return t.SemanticTokens(data=data)




# get tokens
# loop over tokens and color by TokenType
# indications of nullability, triggers, checks and no-access comes later and elsewhere.
# autocompletion is later and elsewhere.
# embddedment is also later and elsewhere.
# hinting autogenerated text is in another file. it can also be toggled on/off in settings

# ----------- colors -------------
# keywords, identifiers, parameter (e.g. var), literals, strings, comments, types, 
# comma, brackets, operators, functions, errors, default for unrecognized
# evt. give separate colors to schema, tree, table, column, view, aliases
# 



